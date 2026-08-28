---
name: session-handoff
description: >-
  Write end-of-session state so the next session starts without re-deriving anything: rewrite
  docs/handoff/HANDOFF.md, append an entry to docs/handoff/SESSION_LOG.md, and update on-event
  documents when their trigger occurred. Use at the end of every working session, or when the
  user says "wrap up", "write the handoff", "we're done for today", or "hand this off". Do NOT
  use to create the initial document set — that belongs to session-context-init — and do NOT use
  to restructure or promote facts into permanent docs — that belongs to context-curation.
---

# Session Handoff

Reference implementation. This is the skill `context-curation` is developed and tested against;
a project may pin its own copy under `.opencode/skills/session-handoff/`. Behaviour is declared
by the spec, not by this file — where the two disagree, the spec wins and this file is the bug.

<!-- context-curation:session-handoff-contract-block:start -->
## Project memory contract

Read `docs/handoff/handoff-spec.md` before writing any session state. Follow its document paths,
cadences, handoff fields, and session-log entry format. It overrides this skill's defaults.

The spec is maintained by `context-curation`. Do not edit it during routine handoff. If it is
missing after initialization, stop and report the broken project setup instead of falling back to
a different path layout.

After all handoff-owned writes finish, follow the spec's `Git checkpoint policy`. If the project is
not a Git work tree, remind the user and ask whether to run `git init`; handoff still completes if
they decline. If changes exist, show the read-only status summary and offer a checkpoint commit.
Never initialize, stage, commit, or change branches without the user's explicit approval.
<!-- context-curation:session-handoff-contract-block:end -->

## What this skill is for

Handoff answers exactly one question: **where did we stop, and what does the next session need to
know to continue?** It records session state. It does not decide what becomes permanent project
knowledge — that judgement is `context-curation`'s, and it needs several sessions of evidence to
make well. Promoting a fact here, at the end of a long session when attention is lowest, is how
the permanent layer fills with things that turned out not to matter.

## Procedure

### 1 — Read the contract

Read `docs/handoff/handoff-spec.md`. It declares the document set and cadences, the required
`HANDOFF.md` fields, the `SESSION_LOG.md` entry format, and the Git checkpoint policy. If it is
missing, stop and report the broken setup — do not write to a guessed path layout.

### 2 — Rewrite HANDOFF.md

Rewrite it fully; do not append. This file answers *where did we stop*, and stale lines from three
sessions ago actively mislead.

Write every field the spec requires. Where a field is genuinely empty, write `none` — an omitted
field is indistinguishable from a forgotten one.

The test for **Stopped at** is whether the next session can begin from it without reading anything
else. "Continue the parser work" fails that test; "add the `--strict` branch to `parse_header`,
tests written and failing" passes it.

**Do not repeat** is the field that pays for itself most often: an approach tried and abandoned,
left unrecorded, gets confidently proposed again next session.

### 3 — Append to SESSION_LOG.md

Append one entry in the spec's exact format. Never rewrite earlier entries — the log is append-only
and the audit reads it as history.

Two mechanical requirements:

- **The `## Session NNN — YYYY-MM-DD` heading must match the spec form exactly.** The audit script
  counts sessions from that heading and the harvest seeks to it by line number. A reformatted
  heading makes the session invisible to both.
- **Tag lines with `[candidate]`, `[gotcha]`, and `[decision]`.** These are what let the next
  curation harvest run as a `grep` across the whole history instead of a full re-read. An untagged
  fact is findable only by reading every session, which at scale means it is not found.

Tag generously and promote nothing. A tag costs one line and is reversible; a wrong promotion sits
in the permanent layer and poisons later sessions.

### 4 — Update on-event documents

For each document the spec marks `on-event`, write to it **only if its trigger actually occurred
this session**:

| Cadence | This session |
|---|---|
| `per-session` | Always write |
| `on-event` | Write only when the spec's trigger fired |
| `frozen` | Never write; curation owns it |

A `DECISIONS.md` entry when no real choice was made between alternatives is filler, and filler is
what makes a reviewer stop reading the file that matters.

### 5 — Git checkpoint

Follow the spec's `Git checkpoint policy` after all handoff writes are done:

- read-only status first; show staged work separately and ask how to handle it
- offer a commit with exact literal paths and a proposed message
- stage only approved paths — never `git add -A`, `git add .`, or a wildcard
- never push, merge, rebase, reset, stash, amend, or switch branches under this policy

Declining does not block handoff. If work stays uncommitted, say so and put the affected paths in
`In flight` when the next session needs them.

### 6 — Curation check

Read `docs/handoff/.curation-state.json` and **suggest** running `context-curation` if any hold:

- the state is absent or unreadable after several sessions
- 5+ sessions since `last_tuned`
- `AGENTS.md` is over budget
- a milestone closed
- 3+ tags have accumulated since the last harvest
- work entered a new subsystem
- **the user re-explained something the agent should already have known**

Suggest, do not run. Curation needs a fresh session; starting it here, on top of a full working
session, is what the headroom rule in that skill exists to prevent.

The last trigger deserves action on its own. It is direct evidence that a fact belongs in the
permanent layer and is not there.
