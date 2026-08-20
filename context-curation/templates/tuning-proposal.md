# Doc Tuning Proposal — <YYYY-MM-DD>

**Sessions harvested:** <NNN>–<NNN> · **Last tuned:** <date or "never">
**Always-read cost:** ~<N> tokens → ~<N> tokens after this proposal
**Git baseline:** <Git unavailable | not a work tree | parent work tree | branch @ HEAD; clean/dirty; staged paths noted separately>

## Summary

<Two or three sentences. What is the main problem with the doc layer right now,
and what does this proposal do about it.>

---

## A. Blocking — apply first

Missing or stale project-local session contract blocks belong here. State that approved application
runs `scripts/session_contract_blocks.py --root . --apply` against `.opencode/skills/` only.

### A1. <Short title>
- **Finding:** <what the audit found>
- **Impact:** <what goes wrong if untouched>
- **Change:** <exact edit>
- **Files:** `<path>` <created | edited | archived>

---

## B. Promotions

### B1. <the fact, in one sentence>
- **Source:** `docs/handoff/session-log.md`, Session 007, line 42 <or file path / commit>
- **Test:** recurrence ✓ · loss ✓ · stability ✓ · non-derivable ✗ → **3/4, promote**
- **Destination:** `docs/domain/gotchas.md` (new section)
- **AGENTS.md:** pointer already exists / add row: `| docs/domain/gotchas.md | when a tool fails unexpectedly |`
- **Draft:**
  ```markdown
  <the exact text to be inserted>
  ```

---

## C. Structural changes

### C1. <e.g. Demote setup procedure out of AGENTS.md>
- **Before:** <lines 34–58 of AGENTS.md, ~400 tokens>
- **After:** moved to `docs/setup.md`; AGENTS.md keeps one pointer row
- **Net L0 change:** −380 tokens

---

## D. Archive

| File | Reason | Superseded by |
|---|---|---|
| `docs/old-plan.md` | milestone closed, content merged | `PLAN.md` |

---

## E. Considered, not promoted

Recorded to avoid unchanged re-litigation. Reopen a candidate when its evidence changes or its
`Reconsider if` condition becomes true.

| Candidate | Score | Why not | Reconsider if |
|---|---|---|---|
| <fact> | 1/4 | derivable from `--help`; no recurrence | it recurs after session NNN |

---

## F. Handoff spec changes

These alter what happens **every session from now on**, so review them separately from the
one-off doc edits above.

### F0. AGENTS.md initialization (pre-init only)

- **Curation routing entry:** <include the trigger row from templates/handoff-spec.md>
- **L0 budget marker:** <include / project-approved change>
- **Manual snippet required:** no

### F1. Git checkpoint policy

- **Current:** <missing / current policy summary>
- **Proposed:** <exact policy change, or no change>
- **Safety:** prompt-only init and commit; literal-path staging; no automatic branch or remote action

### F2. Document set / cadence

| Doc | Cadence now | Proposed | Why |
|---|---|---|---|
| `docs/handoff/decisions.md` | per-session | on-event | filler entries when no real decision was made |

### F3. handoff.md fields

| Change | Field | Evidence |
|---|---|---|
| add | <field> | session NNN opened by re-deriving this |
| remove | <field> | read "n/a" in N of the last M sessions |

**Fields before → after:** <N> → <N>. If this is a net increase, name what justifies the extra
cost at every future session end.

### F4. Draft spec diff

```markdown
<the exact lines changing in docs/handoff/handoff-spec.md>
```

**Net change to per-session work:** <none / +1 file / −1 field>

---

## G. Noted for the shared skill — NOT APPLIED

Observations that look like they belong in the shared `session-handoff` skill rather than in
this project. **Nothing in this section gets applied by the tuning run.** Apply by hand if you
agree. Empty is the normal outcome.

### G1. <observation>
- **Seen here as:** <what happened in this project, with session numbers>
- **Why it may generalize:** <the reason it is not project-specific>
- **Suggested edit:** <the exact line or change, if you want it>

---

## Open questions for the user

1. <anything the agent could not decide alone — especially archiving anything the user may read by hand>
