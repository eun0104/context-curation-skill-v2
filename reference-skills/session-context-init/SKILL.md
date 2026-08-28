---
name: session-context-init
description: >-
  Initialize a project's persistent context layer in the first working session: create root
  AGENTS.md and plan.md, then create the files declared under docs/handoff/. Runs once, after
  context-curation has produced docs/handoff/handoff-spec.md. Use when a project has an approved
  memory contract but no startup files yet, or when the user says "initialize the context",
  "set up the handoff docs", or "run context init". Do NOT use to write end-of-session state —
  that belongs to session-handoff — and do NOT use to restructure existing docs — that belongs
  to context-curation.
---

# Session Context Init

Reference implementation. This is the skill `context-curation` is developed and tested against;
a project may pin its own copy under `.opencode/skills/session-context-init/`. Behaviour is
declared by the spec, not by this file — where the two disagree, the spec wins and this file is
the bug.

<!-- context-curation:session-context-init-contract-block:start -->
## Project memory contract

Require `docs/handoff/handoff-spec.md` before initialization and read it first. Keep `AGENTS.md`
and `plan.md` at the project root. Create handoff-owned files only under `docs/handoff/`, using
the paths, initial fields, and cadences declared in the spec. When creating `AGENTS.md`, include
the routing entry and budget marker from the spec's `AGENTS.md initialization` section.

If the spec is missing, ask the user to run `context-curation`. That skill determines the lifecycle
from project evidence. Do not invent a default document layout.

Before creating project files, follow the spec's `Git checkpoint policy`. Check whether the project
is already a Git work tree. If it is not, tell the user and ask whether to run `git init`; continue
initialization if they decline, and never initialize silently. After initialization writes finish,
run the policy's read-only status check and offer a checkpoint commit when changes exist. Do not
stage or commit until the user approves the exact paths and commit message.
<!-- context-curation:session-context-init-contract-block:end -->

## When this runs

Once, in the first working session, **after** a pre-init `context-curation` pass has been approved.
Curation writes the spec; this skill turns the spec into files. Running it first has nothing to
read, which is why the contract above stops rather than guessing a layout.

If root `AGENTS.md` and `plan.md` already exist, initialization already happened. Stop and say so
rather than overwriting them — a second init silently discards whatever the project learned since
the first.

## Procedure

### 1 — Read the contract

Read `docs/handoff/handoff-spec.md` in full. Everything below is driven by it:

- **Document set** — which files to create, and each one's cadence
- **AGENTS.md initialization** — the routing entry and budget marker to embed
- **HANDOFF.md fields** — the fields to seed
- **SESSION_LOG.md entry format** — the heading form to seed
- **Git checkpoint policy** — the repository rules for this run

If the file is absent, stop and ask the user to run `context-curation`. Do not proceed from
memory of what a typical project looks like.

### 2 — Take the Git baseline

Follow the spec's `Git checkpoint policy` before writing anything: `git --version`, then
`git rev-parse --show-toplevel`. Report `Git unavailable`, `not a work tree`, or a top level above
the project root, and ask before `git init`. Declining does not block initialization.

### 3 — Create the startup files

**Root `AGENTS.md`** — a routing table, nothing else. It is read every session forever, so it
carries pointers and invariants, never content that belongs behind a pointer. Include verbatim
from the spec:

- the `context-curation` routing entry, so later curation is discoverable without a separate
  install step
- the L0 budget marker comment

**Root `plan.md`** — current goal, milestones, and where the work stands now.

Each doc the spec routes to needs a trigger phrased as a situation the agent will recognise itself
to be in. "When working on this project" is not one.

### 4 — Create the declared handoff files

Create exactly the files the spec's Document set declares, and nothing else. Cadence decides what
goes in each at init:

| Cadence | At init |
|---|---|
| `init` | Create with real content |
| `per-session` | Create with the spec's field or entry skeleton, marked as the pre-session-1 state |
| `on-event` | Create as an empty structured stub, so the first trigger has somewhere to write |
| `frozen` | Do not create; curation owns it |

Seed `docs/handoff/HANDOFF.md` with every required field from the spec, using `none` where a
field is genuinely empty. Seed `docs/handoff/SESSION_LOG.md` with the spec's exact heading form.

Do not invent documents the spec does not declare. An extra file is an orphan at the next audit.

### 5 — Verify and checkpoint

State each:

- [ ] Every document declared in the spec exists; no undeclared document was created
- [ ] `AGENTS.md` carries the curation routing entry and the budget marker
- [ ] `AGENTS.md` is within the spec's L0 budget
- [ ] `HANDOFF.md` has every required field
- [ ] `SESSION_LOG.md` heading matches the spec's entry format exactly

Then follow the spec's `Git checkpoint policy`: show the read-only status and offer a checkpoint
commit for the created paths with a proposed message. Stage only approved literal paths. Never
stage or commit without explicit approval.

Finally, tell the user that `session-handoff` runs at the end of every session from now on, and
that `context-curation` runs again roughly every five sessions.
