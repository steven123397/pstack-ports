# pstack in omp

Every skill in this plugin that names a tool, a path, or a model applies this file's mapping. When a skill and this file disagree, this file wins.
## Tools

| Cursor | omp |
| --- | --- |
| `Task` | `task`. One subagent per `tasks[]` item in a single call when spawning a batch; parallel `task` calls also work. |
| `AskQuestion` | `ask`. In `-p` / non-interactive mode `ask` is absent, so ask in plain text. |
| Open a todolist | `todo` (`init` beside the first action, then `start`/`done`). |
| Run another pstack skill | Slash references `` `/name` `` become `/skill:<name>` (omp's registered command). Natural-language references like "the **name** skill" stay as written — the agent reads `skill://<name>/SKILL.md` when it follows them, which omp resolves to this plugin's copy. |
| `Grep`, `Glob` | omp has native `grep` and `glob`. Use them. |
| `Read` | `read` (supports `skill://` URLs). |
| Edit files | `edit` for surgical changes, `write` for new files. |
| Run shell commands | `bash`. |
| Web search | `web_search`. |

## Subagent fields

omp's `task` schema is `{ context, tasks: [{ name?, agent?, task, solutionSpace, effort?, ... }] }`. There is no `subagent_type`, no `model`, no `readonly`, no `environment`, no `run_in_background`, no `resume`, and no `file_attachments` field. Map Cursor's fields like this:

| Cursor | omp |
| --- | --- |
| `subagent_type: generalPurpose` | omit `agent` (defaults to the `task` agent), or `agent: "task"`. |
| `subagent_type: poteto-agent` | `agent: "pstack-worker"` (defined in this plugin's `agents/`). |
| `subagent_type: comment-sicko` | `agent: "comment-sicko"` (defined in this plugin's `agents/`). |
| A model slug in `model` (e.g. `claude-opus-5-5-xhigh`, `grok-4.7-xhigh-fast`) | Omit it. omp routes models per *agent type* and per *role*, not per task item. See Models below. |
| `readonly: true` | Use a read-only agent: bundled `scout` (read-only by tool set) or this plugin's `pstack-reader`/`pstack-judge` agents whose frontmatter restricts tools to read-only ones. Do not strip `bash` if the brief needs real commands; then keep the agent read-only *by instruction* ("do not edit files") and check `git status` afterwards. |
| `readonly: false`, agent mode with MCP | omit `agent`. The default `task` agent keeps the session's MCP tools. |
| `environment: "cloud"` | `isolated: true` in the task item — requires the omp setting `task.isolation.enabled: true`; when off, run in the shared checkout instead and note it. The isolation workspace is a copy of the repo, so worker output that must persist goes in the brief: have the worker write its artifact under a path you merge, or report it in its result. |
| `environment: "local"` | Omit. Workers share the parent checkout by default. |
| `cloud_base_branch: <b>` | Name `<b>` in the brief; the worker checks it out first (only meaningful with `isolated: true`). |
| `run_in_background: true` | Omit. With `async.enabled` (default true) every task spawn runs in the background and delivers results automatically. |
| `run_in_background: false` | Not expressible per item. Accept background delivery; `wait` blocks until a job you started settles. |
| `resume` | `write agent://<id>` messages the live or parked agent; `--restore` resumes an interrupted session. Prefer a fresh subagent with consolidated scope per poteto-mode's Subagents section, and use messaging only when state truly lives in that agent. |
| `file_attachments` | List the paths in the brief. |
| (none) | `solutionSpace` is required: describe how open-ended the child's problem is, one line. |

## Models

omp has no per-item `model` field and no Cursor slugs. Model choice lives in three omp places, in precedence order: `task.agentModelOverrides[agentName]` settings, the agent frontmatter `model` list, then the parent's active model. All accept role aliases like `@pstack-fast` that expand through `modelRoles`.

This plugin's skills never name a raw model. They name *roles*, and each role is dispatched through a named agent in this plugin's `agents/` directory whose frontmatter pins `model: "@<role>"`. The roles:

| pstack role | agents/ file | Frontmatter model | Skill default duty |
| --- | --- | --- | --- |
| fast worker (was `grok-4.7-xhigh-fast`) | `pstack-worker.md` | `@pstack-fast` | code delegates, explorers, investigators, swarm workers |
| judge (was `claude-opus-5-5-xhigh`) | `pstack-judge.md` | `@pstack-judge` | explainers, synthesizers, reviewers, prose and judgment |
| extra panel seat | `pstack-worker-2.md` | `@pstack-panel` | second model family for arena runners / interrogate reviewers when configured |

`/skill:setup-pstack` configures what these roles resolve to by writing `modelRoles.pstack-fast` / `pstack-judge` / `pstack-panel` in `~/.omp/agent/config.yml`. Defaults if unconfigured: the roles resolve to the parent session's active model (all three unset), which matches `inherit-parent`. Panel diversity then comes only from what the user configured.

Rules for every spawn:

- An alias entry (`inherit-parent`, `auto`, unset role) means: spawn that seat on an agent with no `model` frontmatter, or on the default `task` agent, so it runs on the parent model.
- Never write a raw provider/model id into a skill. Skills name the role; setup-pstack owns the resolution.
- omp thinking suffixes (`:low`/`:medium`/`:high`/`:xhigh`/`:max`) ride the `modelRoles` value, e.g. `anthropic/claude-opus-5-5:max`. The effort ladder maps Cursor's `medium`/`high`/`xhigh`/`max` tokens onto these suffixes.
- If a role resolves to nothing available, omp falls back to the parent model; say so in the reply rather than failing the spawn.
- `task.enableEffort` (default off) gates the per-item `effort: lo|med|hi` field. When a skill wants a reasoning tier for one spawn, prefer the role's `modelRoles` value over relying on `effort`.

## setup-pstack

Follow the skill's steps with these changes:

- Detect. Run `omp models` to enumerate available models with their supported thinking levels. That is the dependable source.
- Budget. omp budget is the thinking suffix on each role's `modelRoles` value: `max` > `xhigh` > `high` > `medium` > `low`. Map the skill's `unlimited`/`large`/`medium`/`small` labels to `max`/`xhigh`/`high`/`medium`.
- Write. Write `modelRoles` entries into `~/.omp/agent/config.yml` (user scope, applies to every omp session) — see the skill's adapted shape. Overwrite the three `pstack-*` entries as a set; leave other `modelRoles` keys alone. Never write model choices into `AGENTS.md` or `.omp/AGENTS.md`.
- Confirm. Tell the user the roles resolve at the next subagent launch (model-role routing applies to subsequent launches without restarting omp).

## Paths

| Cursor | omp |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | this plugin is installed via `omp plugin link <pstack>` or marketplace; skills live under its `skills/`. For project-local skills: `.omp/skills/<name>/SKILL.md`; user: `~/.omp/agent/skills/<name>/SKILL.md`. |
| `~/.cursor/rules/pstack-models.mdc` | `modelRoles` in `~/.omp/agent/config.yml` (see Models). |
| `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | `~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<sessionId>.jsonl`. `<encoded-cwd>` is derived from the canonical cwd: `-<relative>` under the home directory, `-tmp-<relative>` under the temp root, `--<encoded-absolute>--` otherwise, path separators as `-`. `D:/codex_project/upstreams/pstack` becomes `--D--codex_project-upstreams-pstack--`. Every line is one session entry; the newest `.jsonl` directly in that folder is the most recent session. Subagent transcripts are `<id>.jsonl` files in the session's artifacts tree, read via `history://<id>`. Read only the current workspace's bucket. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<pstack>/<path>` in this plugin. Read the local copy, never fetch it. Give the user the URL when they need a link. |
| `/tmp/arena-<slug>/candidate-<n>/` | `$TMPDIR` or `%TEMP%` path with the same shape; or a git worktree when one is available. |
| `.cursor/worktrees/` | `task` isolation workspaces (branch mode `omp/task/<id>`) or plain `git worktree` commands. |

## Cursor-only features

omp has no Cursor Automations, no Bugbot, no Cursor cloud agents, and no `/loop`. When a step needs one, put one line in your reply, `Skipped in omp: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | omp |
| --- | --- |
| Cursor Automations: routines, webhooks, routine wakes, `SendToUser` secret requests | Skip with the line. |
| Bugbot | GitHub PR review comments are ordinary review threads; triage them with `gh` or the `issue://`/`pr://` internal URLs. Skip a step that starts, waits for, or configures Bugbot when the PR has no such check or comment. |
| Cursor cloud agents | `environment: "cloud"` maps to `isolated: true` as in Subagent fields. Skip a step that needs the cloud agent itself. |
| A built-in PR tool | `gh pr create`, or `pr://` internal URLs for reading. Not a skip. |
| `/loop` | omp equivalent is an autonomous-run prompt ("run until done", goal mode) inside one session; say so and continue. |
| Cursor's built-in `create-skill` | This plugin's own authoring flow: `poteto-mode`'s authoring-a-skill playbook plus omp's `manage_skill` tool / `xd://manage_skill`. Not a skip. |
| `cursor-team-kit` `deslop`, `control-cli`, `control-ui` | `deslop` → the **unslop** skill. CLI/TUI verification → omp `bash` (launch the program, observe). Browser/web UI verification → omp `browser` (`browser.open` tab, `tab.run` JS, visual proof). Not a skip. |

## Transcript reading

omp session files are JSONL with one entry per line. A user turn's text is in entries with `role: "user"`; the file's first user entry holds the conversation's opening prompt. `history://<id>` renders a subagent's `<id>.jsonl` as a concise transcript. Prefer `history://` over parsing JSONL by hand.

