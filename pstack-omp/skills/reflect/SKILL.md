---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript in the current workspace's omp session bucket, `~/.omp/agent/sessions/<encoded-cwd>/`, where `<encoded-cwd>` encodes the canonical workspace path (`-<relative>` under home, `--<absolute>--` otherwise, separators as `-`). Do not glob across `~/.omp/agent/sessions/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.

```bash
ls -t <session-bucket>/*.jsonl <session-bucket>/*/*.jsonl 2>/dev/null | head -10
```

That covers session files (`<timestamp>_<id>.jsonl`) and subagent transcripts in the session's artifacts directory (`<timestamp>_<id>/<AgentName>.jsonl`; `history://<id>` renders one). For each candidate, read the first user entry, a line with `type: "message"` whose `message.role` is `user`. Take the file whose first user text contains the conversation's opening user prompt. If none matches, pass a tight digest of the session instead.

## 2. Spawn three reviewers in parallel

One `task` call with three items, one per lens. Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references; omp keeps MCP tools additive for every agent.

Each reviewer and the synthesizer names the agent whose frontmatter pins its role. Omit per-item `model`; a role left unset runs on the parent model, and a role that resolves to nothing falls back to the parent model, so say so. Pick each subagent's thinking level per the Subagents section of the **poteto-mode** skill.

| Lens | Agent | Role | Prompt template |
|---|---|---|---|
| Judgment | `pstack-judge` | `@pstack-judge` | `references/judgment-reviewer.md` |
| Tooling | `pstack-worker` | `@pstack-fast` | `references/tooling-reviewer.md` |
| Divergent | `pstack-judge` | `@pstack-judge` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the `task` result body.

## 3. Synthesize

One `task` item on `agent: "pstack-judge"` (`@pstack-judge`). It spot-verifies citations through MCP. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): follow the **authoring-a-skill** playbook (`skill://poteto-mode/playbooks/authoring-a-skill.md`) and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): rewrite the `description` under the **authoring-a-skill** playbook's rules, then verify the trigger words against the skill's `description`.
- `new skill via manage_skill: <kebab-name>`: create it with the `manage_skill` tool, or write `SKILL.md` directly when it belongs to a project. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
