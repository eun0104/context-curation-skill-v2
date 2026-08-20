# Handoff Spec — <Project>

Project-local memory contract for both `session-context-init` and `session-handoff`. Their pinned
project-local copies read this file before creating or updating persistent context.

Maintained by `context-curation`. Do not hand-edit during a session — changes here alter every
future session, so they belong in a tuning proposal where they get reviewed as a unit.

**Last tuned:** YYYY-MM-DD (session NNN)
**Base skill versions:** `session-context-init` <version> · `session-handoff` <version>

The base-skill line matters because project-local copies are pinned. At each tuning run, compare
them with their shared upstream templates and note anything worth adopting.

## Document set

| Document | Cadence | What goes in it |
|---|---|---|
| `AGENTS.md` | init | Created at the project root; routing table only. |
| `PLAN.md` | init / on-event | Created at the project root; updated when plan state changes. |
| `docs/handoff/handoff.md` | per-session | Rewritten fully. Fields below. |
| `docs/handoff/session-log.md` | per-session | Appended. Entry format below. |
| `docs/handoff/decisions.md` | on-event | Only when a real choice was made between alternatives |
| `docs/reference/parameters.md` | on-event | When a fitted value is accepted as settled |
| `docs/domain/gotchas.md` | on-event | When an external system behaved unexpectedly |
| `docs/architecture.md` | frozen | Curation only |

`init` = created by session-context-init · `per-session` = written every session · `on-event` = only when the trigger occurs ·
`frozen` = not touched by handoff at all

## AGENTS.md initialization

When `session-context-init` creates root `AGENTS.md`, include this entry in its read-on-demand
routing table. This makes later curation discoverable without requiring the user to install or
apply a separate snippet.

| Read this | When |
|---|---|
| skill `context-curation` | When AGENTS.md exceeds its budget, docs contradict each other, a milestone closes, no curation state exists after several sessions, or 5+ sessions have passed since `docs/handoff/.curation-state.json` `last_tuned` |

Also include this budget marker near the top of `AGENTS.md`:

```markdown
<!-- L0 budget: 2000 tokens. Adding a line here requires removing one.
     Run the context-curation skill when over. -->
```

## Git checkpoint policy

This is a reminder and safety policy, not a branching workflow. Apply it during
`session-context-init`, at the end of every `session-handoff`, and after an approved normal-mode
curation apply.

- **Repository check:** run `git --version` first. If Git is unavailable, report it and skip the
  checkpoint without blocking the session operation. Otherwise run
  `git rev-parse --show-toplevel`. If it fails, tell the user and ask whether to run `git init`.
  If it resolves above the project root, report the parent repository and ask whether that scope
  is intentional. Never initialize silently. Declining does not block init or handoff.
- **Checkpoint check:** run `git status --short --branch`, then summarize unstaged and staged diffs.
  If changes exist, offer a checkpoint commit with the exact candidate paths and proposed message.
- **Approval boundary:** do not initialize, stage, or commit until the user explicitly approves
  the operation, exact paths, and commit message. A general request to finish init or handoff is
  not Git approval.
- **Existing staged work:** inspect `git diff --cached --name-only` before staging. If it is not
  empty, do not disturb or silently include it; show it separately and ask how the user wants it
  handled.
- **Narrow staging:** stage only approved literal paths with `git add -- <path>...`. Do not use
  `git add -A`, `git add .`, wildcards, or a path derived from unverified output. Before committing,
  show `git diff --cached --name-only` and `git diff --cached --stat` and confirm they match the
  approved scope.
- **No workflow automation:** never push, merge, rebase, reset, stash, amend, switch branches, or
  create branches under this policy. Do not change local or global Git configuration. Those actions
  require a separate user request; if commit identity is missing, report it instead of configuring
  one silently.
- **Declined checkpoint:** finish the session operation normally and report that uncommitted work
  remains; include affected paths in handoff `In flight` when they matter to the next session.

## handoff.md fields

Required. If a field is genuinely empty, write `none` — an omitted field is
indistinguishable from a forgotten one.

1. **Stopped at** — the exact next action, specific enough to start without re-reading anything
2. **Blocked by** — what prevents it, or `none`
3. **In flight** — files edited but not finished or verified
4. **Do not repeat** — approaches tried this session that failed, so the next session skips them
5. <project-specific fields — see the profile, if one applies>

Fields are a budget. When adding one, name the one it replaces. Fifteen fields at the end of a
long session produce fifteen shallow answers.

## session-log.md entry format

```markdown
## Session NNN — YYYY-MM-DD

### Did
- <what changed, briefly>

### Learned
- [candidate] <fact that may deserve a permanent home>
- [gotcha] <external system behaved unexpectedly>
- [decision] <chose X over Y because Z>
```

Keep the `## Session NNN` heading exactly in that form — the audit script counts sessions from
it and the harvest step seeks to it by line number.

Tags are what make the next harvest a `grep` rather than a full re-read of the log.

## Curation check

At the end of handoff, read `docs/handoff/.curation-state.json` and suggest running `context-curation`
if any hold: the state is absent or unreadable after several sessions · 5+ sessions since
`last_tuned` · AGENTS.md over budget · a milestone closed · 3+ tags accumulated · new subsystem ·
the user re-explained something the agent should have known.

Suggest, do not run.
