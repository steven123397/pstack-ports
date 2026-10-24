# pstack in Kimi Code

Every skill in this plugin that names a tool, a path, or a model applies this file's mapping. When a skill and this file disagree, this file wins. `<pstack>` means the folder that holds `skills/` and `docs/` (the installed plugin directory).

## Tools

| Cursor | Kimi Code |
| --- | --- |
| `Task` | `Agent`. Spawn a batch as parallel `Agent` calls in one block, or as `AgentSwarm` when every item shares one prompt shape and one model. `AgentSwarm` takes a single `model` for the whole swarm, so a panel that gives each seat its own model is parallel `Agent` calls, never one swarm. |
| `AskQuestion` | `AskUserQuestion`. In `-p` / non-interactive mode it fails, so ask in plain text. Under the Never Ask permission mode it is refused; decide and report instead. |
| Open a todolist | `TodoList`. |
| Run another pstack skill | Slash references `` `/name` `` become `/skill:pstack:<name>`. Natural-language references like "the **name** skill" stay as written; read the sibling file `${KIMI_SKILL_DIR}/../<name>/SKILL.md` when you follow one. Skill invocations nest at most 3 deep. |
| `Grep`, `Glob` | Native `Grep` and `Glob`. |
| `Read` | `Read`. |
| Edit files | `Edit` for surgical changes, `Write` for new files. |
| Run shell commands | `Bash`. |
| Web search | `WebSearch`; fetch a specific page with `FetchURL`. |

## Subagent fields

`Agent`'s schema is `{ prompt, description, subagent_type?, model?, run_in_background?, resume? }`. There is no `readonly`, no `environment`, no `file_attachments`, and no per-item `model` on `AgentSwarm`. Map Cursor's fields like this:

| Cursor | Kimi Code |
| --- | --- |
| `subagent_type: generalPurpose` | `subagent_type: "coder"` (the default; keeps the session's MCP tools). |
| `subagent_type: poteto-agent` | `subagent_type: "poteto-agent"` (this plugin's `agents/`). |
| `subagent_type: comment-sicko` | `subagent_type: "comment-sicko"` (this plugin's `agents/`). |
| `readonly: true` | `subagent_type: "explore"` (read-only by tool set). When the brief needs real shell commands, use `coder`, put "do not edit files" in the brief, and check `git status` afterward. |
| `readonly: false`, agent mode with MCP | `coder`. |
| `environment: "cloud"` | A Jules cloud session dispatched through `poteto-mode/scripts/jules-cloud.mjs` (see Cloud workers). For work that must stay local, a `git worktree` plus a `coder` agent whose brief names the worktree path and branch; the worker commits there. There is no automatic patch capture. |
| `environment: "local"` | Omit. Workers share the parent checkout by default. |
| `cloud_base_branch: <b>` | Dispatch with `jules-cloud.mjs dispatch --branch <b>`; a local worktree worker checks out `<b>` first. |
| `run_in_background: true` | `run_in_background: true`. Completion arrives as a synthetic user message. Inspect with `TaskList`/`TaskOutput`, block briefly with `WaitFor` (90s cap), stop with `TaskStop`. |
| `resume` | `resume: "<agent-id>"` continues a live or finished subagent. pstack still prefers a fresh subagent with consolidated scope; resume only when state truly lives in that agent. |
| `file_attachments` | List the paths in the brief. |
| `model: <slug>` | Never a raw slug. Resolve the role through the model mapping (see Models) and pass its pool alias. |

## Cloud workers

Kimi Code's `Agent` is local. A worker that must outlive this machine is a **Jules cloud session**, dispatched through `poteto-mode/scripts/jules-cloud.mjs`. The script is the only place pstack names the provider; skills call it.

- **Prerequisites.** `JULES_API_KEY` in the environment, and the repository connected to Jules. Verify with `jules-cloud.mjs sources`; connect a missing repo in the Jules web app first. Set the key in the environment, never as a script argument, and never write it into the repo.
- **Dispatch.** `node jules-cloud.mjs dispatch --repo <owner/name> --brief <file> [--branch main] [--title <text>] [--no-pr]`. Put the brief in a file or stdin.
- **Observe.** `status --session <id>` or `wait --session <id> [--timeout 3600] [--require-pr]`. Poll `state` and `outputs[].pullRequest` together: the PR can appear while the session is still `IN_PROGRESS`. Terminal states are `COMPLETED` and `FAILED`; `AWAITING_PLAN_APPROVAL` and `AWAITING_USER_FEEDBACK` need a human and exit non-zero. A timeout is not success. A read-only session can stay `IN_PROGRESS` after it has answered: read `activities --session <id>` for the `agentMessaged` text and stop waiting.
- **Follow up.** `send --session <id> --brief <file>` posts another turn to the same cloud session. The session keeps its branch and context.
- **Deliverable.** The PR URL and its head branch. The cloud worker is the only writer on that branch. Read-only cloud workers produce no PR: dispatch with `--no-pr`, read the answer with `result --session <id>`, and do not wait for `COMPLETED`.
- **No cancel.** The API documents no cancel endpoint. Abandon a session by ignoring it and deleting any branch or PR it produced.

## Models

Kimi Code has no Cursor slugs, and skills never name a raw model. Role names in skill text stay as written. The role-to-model mapping lives in the `[secondary_model.models]` pool in `~/.kimi-code/config.toml`: every alias that serves pstack roles lists them in a marked segment at the end of its hint text. The pool hints are injected into the `Agent` tool description every session, so the mapping is in context at spawn time. This replaces Cursor's always-applied `~/.cursor/rules/pstack-models.mdc`. `/skill:pstack:setup-pstack` writes it.

Hint shape (the segment after `|` is pstack's; the leading sentence is ordinary routing guidance; TOML multi-line strings keep the one-role-per-line shape):

```toml
[secondary_model.models]
"alibaba-cn/kimi-k3" = """
Default subagent model. | pstack roles:
feature, refactoring
bug-fix
perf-issue
hillclimb
how explorer
why investigators
reflect tooling
swarm workers
panel second seat: arena runners, arena cross-judge pool, architect runners, interrogate reviewers
"""
"alibaba-cn/deepseek-v4.1-flash" = """
Judgment/prose model. | pstack roles:
judgment and prose
hardest tasks
how explainer
why synthesizer
reflect judgment, divergent, synthesizer
panel first seat: arena runners, arena cross-judge pool, architect runners, interrogate reviewers
"""
```

At spawn time:

- Look up the role in the pool hints and pass that alias as `model:`. Never pass an alias that is not in the pool.
- `inherit-parent` or `auto` as a role value maps to `model: "primary"` (the parent session model). `primary` has no hint of its own, so setup-pstack records such roles in a `pstack roles on primary:` segment on the pool default's hint. Do not omit `model` instead: an omitted `model` falls to the pool's configured default, which is not necessarily the parent.
- A role that appears in no hint maps to `model: "primary"`; suggest running `/skill:pstack:setup-pstack` once and move on.
- Effort rides the alias: each pool entry's `default_effort` in `config.toml` sets its thinking level. When a skill says to raise or lower the effort one step, pick a pool alias of the same model family at that level if one exists; if none does, keep the role's alias unchanged and say so.
- A `-fast` speed token has no Kimi Code counterpart; there is no speed axis on a model. Drop the token. A role that needs a faster lane maps to a different pool alias the user configured.
- If `Agent` rejects the alias, fall back to `model: "primary"` and say so rather than trying another alias.

## setup-pstack

Follow the skill's steps with these changes:

- **Detect.** Read `~/.kimi-code/config.toml`: the `[models]` aliases and the `[secondary_model.models]` pool are the available choices, and `primary` is always valid. There is no model-probing CLI; the config file is the dependable source.
- **Defaults, not budget.** There is no `unlimited`/`large`/`medium`/`small` budget step: effort is a property of the pool alias (its `default_effort`), not a global dial, and the right level differs per model. Ask exactly two questions — which pool alias succeeds the fast/code default (`grok-4.7-xhigh-fast`) and which succeeds the judgment/prose default (`claude-opus-5-5-xhigh`). `primary` is a valid answer to either.
- **Write.** For each chosen alias, rewrite its `[secondary_model.models]` hint in `~/.kimi-code/config.toml`: keep or compose a general routing sentence, then append the `| pstack roles: ...` segment listing the roles that follow the skill's default split. Panel lists keep both aliases in the skill's order, noted as first seat and second seat. Roles answered `primary` go into a `pstack roles on primary:` segment on the pool default's hint. Never edit an unchosen alias's hint, and never add or remove pool entries without explicit approval. Re-running rewrites only the pstack segments, so it stays idempotent.
- **Effort variants only on request.** If the user wants the same model at another thinking level, offer to register a second `[models]` entry (same provider and model, different `default_effort`) and add it to the pool. Leave every existing entry untouched.
- **Confirm.** Kimi Code watches and reloads `config.toml`, so the mapping applies to subsequent subagent launches without a restart; say so.

## Settings

pstack needs no setting changes on Kimi Code. There is no project-level config file; everything lives at user level.

- Permission modes: Always Ask (default), Ask When Needed (`/yolo`), Never Ask (`/auto`). Playbooks that promise full autonomy need Never Ask; say so at the start of the run.
- Plan mode (`/plan`, `EnterPlanMode`) restricts `Write`/`Edit` to the plan file and blocks `TaskStop` and `CronDelete`. Do not run playbooks that spawn or stop background workers from plan mode.
- `CronCreate` tasks are bound to the session (restored when the session resumes with `kimi --session`), at most 50 per session, and a recurring task older than 7 days fires one last time before the system deletes it.

## Paths

| Cursor | Kimi Code |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | This plugin installs to `~/.kimi-code/plugins/managed/pstack/`. Project-local skills: `.kimi-code/skills/<name>/SKILL.md`; user skills: `~/.kimi-code/skills/<name>/SKILL.md`. |
| `~/.cursor/rules/pstack-models.mdc` | The `pstack roles:` segments in the `[secondary_model.models]` hints in `~/.kimi-code/config.toml` (see Models). |
| `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | `~/.kimi-code/sessions/wd_<slug>_<sha12>/<sessionId>/agents/<agentId>/wire.jsonl`. `wd_<slug>_<sha12>` derives from the workspace path; `~/.kimi-code/session_index.jsonl` maps session ids to working directories. The main agent is `agents/main/`; each subagent gets its own `agents/<id>/wire.jsonl`. Read only the current workspace's bucket. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<pstack>/<path>` in this plugin for everything the plugin ships. Read the local copy, never fetch it. Give the user the URL when they need a link. |
| `/tmp/arena-<slug>/candidate-<n>/` | `$TMPDIR` or `%TEMP%` with the same shape, or a git worktree when one is available. |
| `.cursor/worktrees/` | Plain `git worktree` commands. |

## Cursor-only features

Kimi Code has no Cursor Automations, no Bugbot configuration, no Cursor cloud agents, and no built-in PR tool. When a step needs one and the table below gives no replacement, put one line in your reply, `Skipped in Kimi Code: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | Kimi Code |
| --- | --- |
| Cursor Automations: routines, webhooks, routine wakes, `SendToUser` secret requests | Skip with the line. |
| Bugbot | Bugbot comments on a GitHub PR are ordinary review threads, so triage them normally; the `watch-pr` scripts still identify automation-authored threads by GitHub author name. Skip a step that starts, waits for, or configures Bugbot. |
| Cursor cloud agents | Dispatch a Jules session with `poteto-mode/scripts/jules-cloud.mjs` as in Cloud workers. Not a skip. Skip only a step that needs the Cursor dashboard or that agent's VM identity. |
| A built-in PR tool | `gh pr create`; read PRs with `gh pr view` and `gh api`. Not a skip. Origin stays as written: it is an external CLI, used only when installed. |
| `/loop` | No `/loop` command. A periodic check maps to `CronCreate` (limits in Settings); "run until X" maps to `/goal` goal mode, which drives the task across turns to a verifiable end state. Not a skip. |
| `/visualize` | No equivalent. Numbers to compare go in a Markdown table. A table is not a picture; screenshots and generated images still carry visual claims. |
| Cursor's built-in `create-skill` | This plugin's own authoring flow: the authoring-a-skill playbook plus `Write` — a skill is a plain `SKILL.md` file under a skills directory. Not a skip. |
| `cursor-team-kit` `deslop`, `control-cli`, `control-ui` | `deslop` → the **unslop** skill. CLI/TUI verification → `Bash` (launch the program, observe). Browser / Electron / web UI verification → the official `kimi-webbridge` plugin (the user's real browser and login sessions); Windows desktop GUI → `kimi-cu-win`. If the needed plugin is missing, tell the user once to run `/plugins install kimi-webbridge`, then continue with the non-visual steps. Not a skip. |

## Transcript reading

`wire.jsonl` is an append-only event stream, one JSON object per line, each entry carrying a `type` (metadata, user or assistant message, tool call, and so on). The entry schema is undocumented: before parsing at scale, open the current session's own file and learn the shapes from it, or use `kimi export <sessionId>` for a ZIP archive and `/export-md` for a rendered transcript. Subagent transcripts are sibling `agents/<id>/wire.jsonl` files in the same session directory; there is no rendered subagent transcript URL, so read the file directly.
