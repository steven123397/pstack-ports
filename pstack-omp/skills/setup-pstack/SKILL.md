---
name: setup-pstack
description: Configure which models pstack uses per role and at what thinking level, and check the isolation setting its swarm paths need. Detects your available models and writes omp modelRoles entries that override the inherit-parent default. Use for /skill:setup-pstack, "configure pstack models", "pstack budget", "pstack setup", or changing pstack's model choices.
---

# Setup pstack

Write pstack's three model roles into `modelRoles` in `~/.omp/agent/config.yml`.

pstack routes work by role, and each role is pinned by one agent definition. The whole routing contract:

| Role | Pinned by | Covers |
| --- | --- | --- |
| `@pstack-fast` | `pstack-worker` agent | Code delegates: playbook work (feature, bug-fix, refactoring, perf-issue, hillclimb), swarm workers, how explorers, why investigators, reflect tooling. Default for every worker unless a panel seat assigns `pstack-panel` per arm. |
| `@pstack-judge` | `pstack-judge` agent | Judgment and prose: hardest tasks, how explainers, why synthesizers, reflect judgment/divergent/synthesizer, arena cross-judge. |
| `@pstack-panel` | `pstack-panel` agent | Second seat of multi-model panels (arena runners, architect runners, interrogate reviewers). Pick a different model family from `@pstack-fast`, or the panel loses its point. |
| `@pstack-fast` | `pstack-reader` agent (read-only) | Read-only investigation: explorers, evidence gathering. Its `tools` list has no write tools, so it cannot edit. |

A role left unset inherits the parent session model. That is the out-of-box default for all three: pstack works before setup, just without model diversity.

## Steps

### 1. Detect available models

Run `omp models`. It lists the models usable in this installation and the thinking levels each supports. That output is the only dependable source. If it fails, ask the user to paste the selectors they have access to. Never write a real model selector you have not confirmed is available. The aliases `@smol`, `@default`, `@slow` (the user's chat-role tiers) and "inherit the parent session model" are always valid even though they are not detected models.

### 2. Load current state

Read `~/.omp/agent/config.yml`. Under `modelRoles:`, the current values of `pstack-fast`, `pstack-judge`, and `pstack-panel` are the current choices; a `# pstack budget:` comment line records the last budget. An absent key means inherit-parent. Any other `modelRoles` key is not pstack's — never touch it.

### 3. Check the isolation setting

pstack's `swarm`, `hillclimb`, `visual-parity`, and `figure-it-out` spawn `isolated: true`. omp exposes that field only when `task.isolation.enabled` is true, and it is off by default, so without it every worker shares the user's checkout.

Read the three settings that decide this:

```bash
omp config get task.isolation.enabled
omp config get task.isolation.apply
omp config get plan.defaultOnStartup
```

Then report and fix only what the user agrees to:

- `task.isolation.enabled` false. Say those four skills fall back to a shared checkout. Ask whether to enable it.
- `task.isolation.apply` true. Say every isolated worker's patch lands in the current checkout the moment it finishes, which defeats pstack's verify-then-land order. Ask whether to set it false, so the parent reads the captured patch and applies it deliberately.
- `plan.defaultOnStartup` true. Fresh sessions open in plan mode, and plan mode rejects the `isolated` field. Say pstack needs plan mode off, and leave the setting alone; the user exits plan mode per session.

On yes, `omp config set task.isolation.enabled true` and `omp config set task.isolation.apply false`. Write nothing else, and never touch a `task.*` key the user did not agree to.

### 4. Budget, map, and confirm

**(a) Ask for a budget.** Use the ask tool, not free text. Offer these four options with these exact labels, and name the current budget when the config records one. With no recorded budget, say that `large` is the recommendation for panels and long runs.

- `unlimited — max thinking`
- `large — xhigh thinking`
- `medium — high thinking`
- `small — medium thinking`

**(b) Apply it.** Build the working table from the current state (step 2). The budget rewrites only the thinking suffix of real model selectors, to `max`, `xhigh`, `high`, or `medium`, on the ladder `max` > `xhigh` > `high` > `medium` > `low`. If the target level is not in the model's supported list from `omp models`, use its highest supported level at or below the target. Aliases (`@smol` and friends) and inherit-parent entries never change — their thinking follows whatever they point at.

**(c) Show the roles and confirm.** Show every role from the contract table with its value, marking any real selector not in the detected set as needing a choice. Ask whether to accept as-is or change specific roles, offering the detected models, the `@smol`/`@default`/`@slow` aliases, and inherit-parent as the options. Use the ask tool. Remind the user that `@pstack-panel` should differ in family from `@pstack-fast`.

### 5. Validate

Every real selector must appear in the `omp models` output, with a thinking level that model supports (after the step 4b downgrade). Aliases and inherit-parent always pass. If a chosen selector fails, stop and ask again.

### 6. Write the config

Edit `~/.omp/agent/config.yml`. Under `modelRoles:`, set exactly the three pstack keys, preceded by one comment line recording the budget. Remove a key whose value is inherit-parent. Leave every other line of the file byte-for-byte untouched, apart from the `task.isolation` keys step 3 changed with the user's consent. Shape:

```yaml
modelRoles:
  # pstack budget: large (xhigh)
  pstack-fast: <detected code-capable model>:xhigh
  pstack-judge: <detected judgment model>:xhigh
  pstack-panel: <detected model from another family>:xhigh
```

Re-runs stay idempotent: same inputs, same three lines. Routing changes to `modelRoles` apply to subsequent subagent launches without restarting omp; already-running agents keep their model.

### 7. Confirm, and name the escape hatches

Tell the user the config was written and which roles now differ from inherit-parent. Then, once, name the two built-in ways to deviate without re-running this skill: `task.agentModelOverrides` overrides a named agent's model directly, and tagging a model with `^` in the composer mints an `m1`/`m2` agent for ad-hoc spawns. Per-project pstack roles are possible via `modelRoleStorage: project`, which writes role assignments to the project's `.omp/config.yml` instead.

### 8. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /skill:create-verification-skill." On yes, invoke `/skill:create-verification-skill`. On no, move on without pushing.

### 9. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /skill:create-formal-verification-skill." On yes, invoke `/skill:create-formal-verification-skill`. On no, move on without pushing.
