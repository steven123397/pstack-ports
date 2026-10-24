# Resolve and invoke skills

Every pstack workflow is a skill: omp resolves it by bare name, lists the registry when a name is unknown, and expands `/skill:<name>` into that skill's instructions inside a session. If resolution breaks, every playbook in the plugin is silently unavailable.

## Sub-features

- `skill-resolve` resolves `skill://<name>/SKILL.md` to the installed plugin file.
- `skill-registry` reports the skills omp actually sees, through the error for an unknown name.
- `skill-invoke` expands `/skill:<name>` in a real session and reads the skill body.
- `skill-project-register` loads a project-local skill from `.omp/skills/<name>/SKILL.md` in a session.

## How to get to it (user POV)

- Ask omp for a skill file by URI: `omp read "skill://<name>/SKILL.md"`.
- Type `/skill:<name>` at the composer prompt, or pass it as the prompt of a non-interactive run.
- Ask for a nonexistent skill to see what is registered.
- Run `/skill:verify-pstack-port` to exercise a project-local skill from `.omp/skills/`.

## Driving it with omp CLI

Preconditions:

- The checkout is linked (`✔ Linked pstack-omp from ./pstack-omp`).
- `python .omp/skills/verify-pstack-port/scripts/doctor.py` exits 0.
- Working directory is the repo root.

- **Resolve a skill.** Run `omp read "skill://swarm/SKILL.md:1-8"`. Stdout starts with a path under `~/.omp/plugins/node_modules/pstack-omp/skills/swarm/SKILL.md` and includes the frontmatter line `name: swarm`; exit code `0`.
- **Read the registry.** Run `omp read "skill://not-a-pstack-skill/SKILL.md"`; the command is expected to fail. Exit code is `126`, stderr carries `error: cannot resolve skill://not-a-pstack-skill/SKILL.md for an external command: ENOENT: Unknown skill: not-a-pstack-skill`, and the next line is `Available: ...` listing pstack names including `poteto-help`, `poteto-mode`, `swarm`, `setup-pstack`. Redirect stderr to a file before reading it; the list is long.
- **Invoke a skill in a session.** Run `omp -p --max-time 180 --model bailian/qwen3.8-flash:low "/skill:poteto-help"`. Stdout is the poteto-help map: a line says the command loaded with no question attached and asks which of the numbered options to pick, and the answer quotes the current `modelRoles` pstack entries. That text can only come from the skill body, so its presence is the proof of expansion.
- **Prove a project-local skill registers.** Run `omp -p --max-time 150 --model bailian/qwen3.8-flash:low "/skill:verify-pstack-port Reply with only the H1 title line of the skill you just loaded, nothing else."` Stdout contains `# Verify pstack-port`. This is the only entry point that proves a `.omp/skills/` skill loaded, because `omp read` does not see project or user skills (see Gotchas).
- **Proof.** Save the resolve output, the registry stderr, the invocation stdout, and the project-skill title under `artifacts/skills/`.

## Gotchas

- `omp read` resolves only skills that come from plugins. A native project skill (`.omp/skills/`) or user skill (`~/.omp/agent/skills/`) answers `Unknown skill` there even though a session sees it in its system prompt and `/skill:<name>` loads it. Prove those through a session; do not conclude the skill is broken from `omp read`.
- Skills resolve by bare name only. `skill://pstack-omp/poteto-mode/SKILL.md` fails with `Unknown skill: pstack-omp`; the plugin name is not a namespace segment.
- The path `omp read` prints is the install directory, which is a junction to this checkout. To prove the bytes came from the working tree, reopen the same relative path inside `pstack-omp/` or check the junction target.
- The registry is global. `pstack-zh` ships the same skill names, so an `Available:` entry proves a skill with that name is installed, not that this checkout is the one installed.
- Print mode has no `ask` tool. Skills that interview the user (`setup-pstack` is one) cannot complete non-interactively; use a read-only skill such as `poteto-help` or `poteto-mode` for the invocation proof and never fake an interview's answers.
- `--model` on the child session only affects that session; leaving it off spends the default model's tokens on a help request.
- `--max-time` is in seconds. A slow provider can trip the cap, which shows up as a truncated run rather than an error in the skill.