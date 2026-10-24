---
name: verify-pstack-port
description: "Drive the pstack-omp plugin the way a user does: link the checkout, resolve and invoke its skills through omp, spawn its agents, and check each agent's resolved model against its role. Use when verifying a change to pstack-omp skills, agents, model roles, or the marketplace catalog."
---

# Verify pstack-port

pstack-ports ships an omp plugin, not a UI app. The user surface is a real `omp` process: the plugin gets installed, omp resolves its skills by name, a `/skill:<name>` command runs one, a pstack agent spawns under a model role, and the agent reports which model it actually landed on. Verification means driving those four things and keeping the output.

Everything below runs from the repo root. `omp` commands spawn a short-lived child process, so they are safe to repeat and leave nothing running.

## Launch

```bash
omp plugin link ./pstack-omp
```

Expect `✔ Linked pstack-omp from ./pstack-omp`. This points `~/.omp/plugins/node_modules/pstack-omp` (a Windows junction on this machine) at `./pstack-omp`, so the checkout's skills and agents are what omp loads. There is no build step and no server to keep alive.

Ready means all four:

- `omp plugin list --json` lists `pstack-omp` with `"enabled": true` and a path inside this checkout.
- `omp plugin doctor` ends with `Summary: ... 0 errors`.
- `omp read "skill://poteto-mode/SKILL.md:2-3"` prints `name: poteto-mode` from `~/.omp/plugins/node_modules/pstack-omp/skills/`.
- `omp config get modelRoles` prints a JSON record containing `pstack-fast`, `pstack-judge`, `pstack-panel`.

A marketplace install (`omp plugin marketplace add ./` then `omp plugin install pstack-omp@pstack-ports`) is the consumer path; its catalog is covered in [features/install.md](features/install.md). It writes the same install directory, so do not run a full install while a session is using the plugin.

## Doctor

```bash
python .omp/skills/verify-pstack-port/scripts/doctor.py
```

One read-only pass over the four readiness facts above. It prints `ok`/`FAIL` per check and exits 1 on any failure. Run it first whenever something looks off; it touches no state and needs no model call.

## Drive

Recipes are per feature in [features/](features/):

- [install.md](features/install.md) — link the checkout, resolve the marketplace catalog, and read the marketplace registry.
- [skills.md](features/skills.md) — resolve a skill URI, read the skill registry, and invoke `/skill:<name>` in a real session.
- [agent-routing.md](features/agent-routing.md) — spawn each pstack agent and read its resolved model against the configured role.

Driving conventions:

- Run every command literally from the repo root; do not rewrite flags or paths.
- Treat `omp -p` child sessions as disposable: they get their own session id, they exit on their own, and a `--max-time` cap bounds the run.
- A failed `omp read` exits 126 with the reason on stderr; check the exit code, not just the text.
- `omp read` resolves plugin skills only; native `.omp/skills/` and `~/.omp/agent/skills/` skills load inside a session, never through `omp read`. Prove them with `/skill:<name>`.
- Start each recipe from the state its `Preconditions:` block names.

## Evidence

- Put proof under `.omp/skills/verify-pstack-port/artifacts/<feature>/`. The skill directory's `.gitignore` keeps those files out of git; cleanup never removes them.
- Capture the command, its exit code, and its stdout for every step. For `omp -p --mode json` runs, keep the raw stream (`--json-out`) and the parsed summary together.
- The standards that make a step proof:
  - Skill invocation must show assistant text that could only come from reading the skill body (for `/skill:poteto-help`, the numbered help map), not a generic greeting.
  - Registry proof is the `Available:` list from an unresolvable `skill://` URI, not a directory listing of `skills/`.
  - A project-local skill counts as registered only when `/skill:<name>` in a session returns text from its body; `omp read` cannot show it.
  - Routing proof is `resolvedModel` for the spawned agent compared against that agent's `modelRole` entry in `omp config get modelRoles`. The parent session's own model proves nothing about the role.
  - A run that only checks `omp models` proves which models exist, not that any agent reaches one.
- Report an unreachable step with its command and the unmet precondition. Do not substitute one entry point for another and call it verified.

## Cleanup

- Marketplace registration is additive state: if this run added one, remove it with `omp plugin marketplace remove pstack-ports` (`✔ Removed marketplace: pstack-ports`).
- The link install is shared with the maintainer's working environment. Record whether it existed before the run (`powershell -NoProfile -Command "Get-Item \"$env:USERPROFILE\.omp\plugins\node_modules\pstack-omp\" | Select-Object LinkType"` reports `Junction` when it did) and uninstall with `omp plugin uninstall pstack-omp` only if this run created it.
- `omp -p` leaves no process or port behind; never kill by process name.
- Failed iterations get the same cleanup as passing ones, then the evidence stays where the run put it.