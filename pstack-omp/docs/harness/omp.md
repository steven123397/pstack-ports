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
| `environment: "cloud"` | A Jules cloud session dispatched through `poteto-mode/scripts/jules-cloud.mjs` (see Cloud workers). It works on a connected GitHub repository and opens its own PR, so it survives this machine. For work that must stay local, `isolated: true` copies the repo in a local workspace instead and dies with the machine. |
| `environment: "local"` | Omit. Workers share the parent checkout by default. |
| `cloud_base_branch: <b>` | Dispatch with `jules-cloud.mjs dispatch --branch <b>`; a local `isolated: true` worker checks out `<b>` first. |
| `run_in_background: true` | Omit. With `async.enabled` (default true) every task spawn runs in the background and delivers results automatically. |
| `run_in_background: false` | Not expressible per item. Accept background delivery; `wait` blocks until a job you started settles. |
| `resume` | `write agent://<id>` messages the live or parked agent; `--restore` resumes an interrupted session. Prefer a fresh subagent with consolidated scope per poteto-mode's Subagents section, and use messaging only when state truly lives in that agent. |
| `file_attachments` | List the paths in the brief. |
| (none) | `solutionSpace` is required: describe how open-ended the child's problem is, one line. |

## Cloud workers

omp's `task` is local. A worker that must outlive this machine is a **Jules cloud session**, dispatched through `poteto-mode/scripts/jules-cloud.mjs`. The script is the only place pstack names the provider; skills call it.

- **Prerequisites.** `JULES_API_KEY` in the environment, and the repository must be connected to Jules. Verify with `jules-cloud.mjs sources`; connect a missing repo in the Jules web app first. Set it in the environment, not as a script argument, and never write it into the repo.
- **Dispatch.** `node jules-cloud.mjs dispatch --repo <owner/name> --brief <file> [--branch main] [--title <text>] [--no-pr]`. Put the brief in a file or stdin. Do not pass a long prompt through the Jules CLI's `--session`: it truncates at `#`.
- **Observe.** `status --session <id>` or `wait --session <id> [--timeout 3600] [--require-pr]`. Poll `state` and `outputs[].pullRequest` together: the PR can appear while the session is still `IN_PROGRESS`. Terminal states are `COMPLETED` and `FAILED`; `AWAITING_PLAN_APPROVAL` and `AWAITING_USER_FEEDBACK` need a human and exit non-zero. A timeout is not success. A read-only session can stay `IN_PROGRESS` after it has answered: read `activities --session <id>` for the `agentMessaged` text and stop waiting.
- **Follow up.** `send --session <id> --brief <file>` posts another turn to the same cloud session, for a fix round, a merge order, or an answer to `AWAITING_USER_FEEDBACK`. The session keeps its branch and context.
- **Deliverable.** The PR URL and its head branch. The cloud worker is the only writer on that branch. Use `activities --session <id>` to read the plan and progress. Read-only cloud workers produce no PR: dispatch with `--no-pr`, read the answer with `result --session <id>`, and do not wait for `COMPLETED`.
- **No cancel.** The API documents no cancel endpoint. Abandon a session by ignoring it and deleting any branch or PR it produced.
- **Qoder Cloud Agents MCP is not the default.** It is a generic cloud sandbox: a repository is cloned by an Environment setup script and no PR is produced. Use it only for work that needs custom tools, environments, or scheduled deployments, not for pstack's owner/verifier PR workflow.

## Models

omp has no per-item `model` field and no Cursor slugs. Model choice lives in three omp places, in precedence order: `task.agentModelOverrides[agentName]` settings, the agent frontmatter `model` list, then the parent's active model. All accept role aliases like `@pstack-fast` that expand through `modelRoles`.

This plugin's skills never name a raw model. They name *roles*, and each role is dispatched through a named agent in this plugin's `agents/` directory whose frontmatter pins `model: "@<role>"`. The roles:

| pstack role | agents/ file | Frontmatter model | Skill default duty |
| --- | --- | --- | --- |
| fast worker (was `grok-4.7-xhigh-fast`) | `pstack-worker.md` | `@pstack-fast` | code delegates, explorers, investigators, swarm workers |
| judge (was `claude-opus-5-5-xhigh`) | `pstack-judge.md` | `@pstack-judge` | explainers, synthesizers, reviewers, prose and judgment |
| extra panel seat | `pstack-panel.md` | `@pstack-panel` | second model family for arena runners / interrogate reviewers when configured |

`/skill:setup-pstack` configures what these roles resolve to by writing `modelRoles.pstack-fast` / `pstack-judge` / `pstack-panel` in `~/.omp/agent/config.yml`. Defaults if unconfigured: the roles resolve to the parent session's active model (all three unset), which matches `inherit-parent`. Panel diversity then comes only from what the user configured.

Rules for every spawn:

- An alias entry (`inherit-parent`, `auto`, unset role) means: spawn that seat on an agent with no `model` frontmatter, or on the default `task` agent, so it runs on the parent model.
- Never write a raw provider/model id into a skill. Skills name the role; setup-pstack owns the resolution.
- omp thinking suffixes (`:low`/`:medium`/`:high`/`:xhigh`/`:max`) ride the `modelRoles` value, e.g. `anthropic/claude-opus-5-5:max`. The effort ladder maps Cursor's `medium`/`high`/`xhigh`/`max` tokens onto these suffixes.
- If a role resolves to nothing available, omp falls back to the parent model; say so in the reply rather than failing the spawn.
- `task.enableEffort` (default off) gates the per-item `effort: lo|med|hi` field. When a skill wants a reasoning tier for one spawn, prefer the role's `modelRoles` value over relying on `effort`.
- A `modelRoles` value may itself alias a built-in chat role, e.g. `pstack-judge: "@slow"`. Skills still name only the `pstack-*` roles; pointing them at `@smol`/`@default`/`@slow` is a config-time shortcut setup-pstack may offer, never a skill-side hardcode.

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
| `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | `~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<sessionId>.jsonl`. `<encoded-cwd>` is derived from the canonical cwd: `-<relative>` under the home directory, `-tmp-<relative>` under the temp root, `--<encoded-absolute>--` otherwise, path separators as `-`. `D:/codex_project/upstreams/pstack` becomes `--D--codex_project-upstreams-pstack--`. Every line is one session entry; the newest `.jsonl` directly in that folder is the most recent session. Subagent transcripts are `<AgentName>.jsonl` files in the session's artifacts tree, read via `history://<id>`. Read only the current workspace's bucket. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<pstack>/<path>` in this plugin. Read the local copy, never fetch it. Give the user the URL when they need a link. |
| `/tmp/arena-<slug>/candidate-<n>/` | `$TMPDIR` or `%TEMP%` path with the same shape; or a git worktree when one is available. |
| `.cursor/worktrees/` | `task` isolation workspaces (branch mode `omp/task/<id>`) or plain `git worktree` commands. |

## Cursor-only features

omp has no native Cursor Automations or Bugbot. Cursor cloud agents are replaced by the Jules adapter above. When a step needs a feature with no replacement, put one line in your reply, `Skipped in omp: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | omp |
| --- | --- |
| Cursor Automations: routines, webhooks, routine wakes, `SendToUser` secret requests | Skip with the line. |
| Bugbot | GitHub PR review comments are ordinary review threads; triage them with `gh` or the `issue://`/`pr://` internal URLs. Skip a step that starts, waits for, or configures Bugbot when the PR has no such check or comment. |
| Cursor cloud agents | Dispatch a Jules session with `poteto-mode/scripts/jules-cloud.mjs` as in Cloud workers. Not a skip. Skip only a step that needs the Cursor dashboard or that agent's VM identity. |
| A built-in PR tool | `gh pr create`, or `pr://` internal URLs for reading. Not a skip. |
| `/loop` | omp has it built in: `/loop [count\|duration] [--while\|--until <check>]`. Not a skip. |
| Cursor's built-in `create-skill` | This plugin's own authoring flow: `poteto-mode`'s authoring-a-skill playbook plus omp's `manage_skill` tool / `xd://manage_skill`. Not a skip. |
| `cursor-team-kit` `deslop`, `control-cli`, `control-ui` | `deslop` → the **unslop** skill. CLI/TUI verification → omp `bash` (launch the program, observe). Browser/web UI verification → omp `browser` (`browser.open` tab, `tab.run` JS, visual proof). Not a skip. |

## Transcript reading

omp session files are JSONL with one entry per line. A user turn's text is in entries with `role: "user"`; the file's first user entry holds the conversation's opening prompt. `history://<id>` renders a subagent's `<id>.jsonl` as a concise transcript. Prefer `history://` over parsing JSONL by hand.

