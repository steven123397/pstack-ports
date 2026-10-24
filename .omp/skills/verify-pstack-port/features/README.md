# pstack-port verification map

This directory is the maintained source for verifying the user-facing behavior of the pstack-omp plugin. Read the index before driving anything, then use the matching feature file as the recipe.

## Baseline preconditions

- Run every command from the repo root (`D:/codex_project/pstack-ports` on this machine).
- The checkout is linked into omp: `omp plugin link ./pstack-omp` printed `✔ Linked pstack-omp from ./pstack-omp`.
- `omp plugin doctor` reports `0 errors`.
- `omp config get modelRoles` resolves the three pstack keys; without them the pstack agents inherit the parent session model and routing cannot be proven.
- `python .omp/skills/verify-pstack-port/scripts/doctor.py` exits 0.
- No omp session is mid-write on `~/.omp/plugins`; a full marketplace install would rewrite the live plugin directory.

## Driving conventions

- Start every recipe from the baseline state unless its preconditions say otherwise.
- Commands are literal. Keep quoted names, `:line-range` selectors, and flags unchanged.
- Use `omp read` for anything omp resolves itself; do not read plugin files straight off disk when the point is resolution.
- Use `omp -p` in a child process for anything that needs a session; never drive the session you are working in.
- Check exit codes: a failed `omp read` exits 126, and a routing mismatch makes `probe_routing.py` exit 1.

## Proof and skip reporting

- Capture the user action and the resulting observable state, not only the final screen.
- Plugin proof includes the command, stdout, and exit code.
- Skill proof includes assistant text that could only come from the skill body.
- Routing proof includes `modelRole`, `resolvedModel`, and the configured value side by side.
- Record the feature ID and entry point used with every artifact.
- Report an unreachable path with the attempted command and the unmet precondition. Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with <harness>` starts with `Preconditions:` and uses labeled bullets that pair each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, stable handles, required state, commands, and observable proof.

## Features

- [Install and link](./install.md) covers linking the checkout, marketplace catalog resolution, and the marketplace registry.
- [Resolve and invoke skills](./skills.md) covers skill URI resolution, registry truth, and `/skill:<name>` invocation.
- [Agents and model roles](./agent-routing.md) covers agent registration, per-agent resolved model, and read-only tool scope.