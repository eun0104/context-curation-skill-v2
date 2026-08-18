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
