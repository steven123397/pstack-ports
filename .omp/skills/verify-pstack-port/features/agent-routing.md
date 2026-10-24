# Agents and model roles

The plugin's four agents are the routing layer: `pstack-worker` and `pstack-reader` pin `@pstack-fast`, `pstack-judge` pins `@pstack-judge`, `pstack-panel` pins `@pstack-panel`. A user sees the effect as an agent that spawns at all and a resolved model badge (or `resolvedModel` in the JSON stream) that matches `modelRoles`. A role key missing from `config.yml` makes the agent inherit the parent session model instead.

## Sub-features

- `agent-register` spawns a pstack agent by name without an unknown-agent error.
- `agent-role-resolve` reports the agent's `modelRole` and `resolvedModel` and compares it with the configured value.
- `agent-tool-scope` keeps `pstack-reader` read-only through its frontmatter `tools:` list.

## How to get to it (user POV)

- Spawn an agent from a session with the `task` tool, naming it in `agent`.
- In an interactive session, read the resolved-model badge the task tool shows for each spawned agent.
- As a maintainer, run the routing probe from the repo root.

## Driving it with probe_routing.py

Preconditions:

- `omp config get modelRoles` resolves `pstack-fast`, `pstack-judge`, and `pstack-panel`.
- The agents are installed with the plugin (`omp plugin list --json` shows `pstack-omp` enabled).
- Working directory is the repo root; a session model is available for the child run.

- **Prove one agent.** Run `python .omp/skills/verify-pstack-port/scripts/probe_routing.py pstack-reader`. The summary prints `agent: pstack-reader`, `model role: pstack-fast`, the `resolved` model, the `configured` value, `status: completed`, and `match: yes`; exit code `0`.
- **Prove all four.** Run `python .omp/skills/verify-pstack-port/scripts/probe_routing.py --all`. The table covers `pstack-worker`, `pstack-reader`, `pstack-judge`, `pstack-panel`; every row must report `match: yes`. Any mismatch exits 1 and names the agent.
- **Inspect a mismatch.** Re-run with `--json-out artifacts/agent-routing/<agent>.jsonl` and read the raw stream: each `tool_execution_update` carries the progress entry with `modelRole` and `resolvedModel`, and the final entries carry the agent's output.
- **Proof.** Save the summary text and the raw JSONL per agent under `artifacts/agent-routing/`.

## Gotchas

- The parent session's own model proves nothing. Only `resolvedModel` on the spawned agent's progress entry does.
- `@pstack-fast` is a role, not a model. If the role key is absent from `modelRoles`, the agent inherits the parent model and `resolvedModel` mirrors whoever launched the run; that is a valid configuration but not evidence the role is pinned.
- Role edits apply to subagent launches after the edit; an already-running agent keeps its model, so re-run the probe instead of watching a live one.
- `pstack-panel` is intentionally a different model family from `pstack-fast`; if both resolve to the same family the panel seat has no point, and that is a finding, not a pass.
- `agent: "pstack-reader"` failing with an unknown-agent error means the plugin is not linked or its `agents/` directory did not load; check `omp plugin doctor` before blaming the role.
- The probe spends real tokens on a real model call: the parent turn plus one short subagent turn. `--max-time` bounds it.
- `pstack-reader`'s tool scope comes from the `tools: read, grep, glob, web_search` line in `pstack-omp/agents/pstack-reader.md`; a spawn that edits files means someone widened that line.