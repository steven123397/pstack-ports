---
name: setup-pstack
description: Configure which models pstack uses per role. Detects the pool aliases your subagents can run on and writes pstack's role mapping into the pool hints. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write pstack's role-to-model mapping into the `[secondary_model.models]` hints in `~/.kimi-code/config.toml`. Pool hints ride the `Agent` tool description, so the mapping is in context at every spawn.

## Steps

### 1. Detect available models

Read `~/.kimi-code/config.toml`. The keys of `[secondary_model.models]` are the pool aliases an `Agent` spawn accepts, and each alias's `[models]` entry carries its thinking level as `default_effort`. That file is the dependable source; there is no model-probing CLI. `primary` (the parent session model) is always valid even though it is not a pool alias. Never write an alias you have not seen in the pool. If the pool is missing or empty, stop and ask the user to configure `[secondary_model]` first.

### 2. Load current state

The role list in step 5 is the canonical set. If any pool hint already carries a `| pstack roles:` segment, parse the segments across every entry (including a `pstack roles on primary:` segment) and treat them as the current choices. A role in a segment that is not in step 5's list, such as `how critics`, belongs to a retired role. Drop it. A step-5 role that appears in no segment takes its default from step 3's answers.

### 3. Pick the two defaults, then confirm

**(a) Ask for the fast/code model.** Prefer AskUserQuestion over free text; in non-interactive mode ask in plain text. Offer every pool alias plus `primary` (the role runs on the parent session model), and name the current choice when step 2 found one. This succeeds the Cursor default `grok-4.7-xhigh-fast`, so it serves: feature, refactoring; bug-fix; perf-issue; hillclimb; how explorer; why investigators; reflect tooling; swarm workers.

**(b) Ask for the judgment/prose model.** Same options. This succeeds the Cursor default `claude-opus-5-5-xhigh`, so it serves: judgment and prose; hardest tasks; how explainer; why synthesizer; reflect judgment, divergent, synthesizer.

**(c) Show the roles and confirm.** Show every role with its model from the default split. For panel roles (arena runners, architect runners, interrogate reviewers, arena cross-judge pool) the value is a list of two seats: the judgment alias first, the fast alias second. One subagent runs per entry, so the list length sets the fan-out count. `arena cross-judge pool` is a pool Arena draws one value from, preferring a model family that differs from the parent's. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm. Ask whether to accept as-is or change specific roles; any role may take any pool alias or `primary`.

### 4. Validate

Every written value must be a pool alias exactly as keyed in `[secondary_model.models]`, or `primary`. If a chosen value is neither, stop and ask again.

### 5. Write the hints

Edit `~/.kimi-code/config.toml`. Back it up first (`config.toml.pstack-bak`), show the exact new hint text, and write only after the user approves.

- For each chosen alias, rewrite its hint as a TOML multi-line string: keep or compose the leading routing sentence, then the `| pstack roles:` segment with one role per line. Shape:

```toml
[secondary_model.models]
"acme/fast-model" = """
Fast/code model. | pstack roles:
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
"acme/wise-model" = """
Judgment/prose model. | pstack roles:
judgment and prose
hardest tasks
how explainer
why synthesizer
reflect judgment, divergent, synthesizer
panel first seat: arena runners, arena cross-judge pool, architect runners, interrogate reviewers
"""
```

- Roles answered `primary` go into a `pstack roles on primary:` segment on the pool default's hint (the `[secondary_model] default_model` entry), same one-role-per-line shape.
- Never edit an unchosen alias's hint. Never add or remove pool entries, and never touch any other key in the file. Re-running rewrites only the pstack segments, so it stays idempotent.
- Register an effort variant (a second `[models]` entry for the same provider and model at another `default_effort`, added to the pool) only when the user asks for one, and only with explicit approval.

### 6. Confirm

Tell the user the hints were written. Kimi Code watches and reloads `config.toml`, so the mapping applies to subsequent subagent launches without a restart. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /skill:pstack:create-verification-skill." On yes, invoke `/skill:pstack:create-verification-skill`. On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /skill:pstack:create-formal-verification-skill." On yes, invoke `/skill:pstack:create-formal-verification-skill`. On no, move on without pushing.
