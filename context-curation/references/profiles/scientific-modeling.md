# Profile: Scientific Theory and Mechanism Modeling

Applies when code implements, combines, fits, or tests scientific theories, mechanisms, governing
equations, or derived models. Use it during pre-init as soon as the initial concept provides that
evidence; do not wait for session logs. This is a prior, not a checklist.

## Contents

1. Scientific traceability contract
2. Minimum durable model ledger
3. Evidence-state boundary
4. Verification protocol
5. Project memory contract additions
6. Recommended invariants

## Scientific traceability contract

The code is neither the theory nor proof that the theory was implemented correctly. For every
accepted model claim, preserve this chain:

```text
source or explicit project derivation
  → canonical equation or claim
  → implementation location
  → verification evidence
```

Never fabricate a missing link. Mark it `[TBD: source]`, `[TBD: implementation]`, or
`[TBD: verification]` and route it to `HANDOFF.md` as an open scientific question or to the
proposal as a blocker. A citation alone is not verification, and a passing fit alone does not
identify the correct mechanism.

## Minimum durable model ledger

When the project has at least one non-trivial governing equation or mechanism, prefer one
`docs/domain/theory-ledger.md` before creating several topic files. Give every equation or claim a
stable project ID so the code, tests, decisions, and handoff can refer to the same object.

```markdown
### EQ-<stable-id> — <equation or claim name>
**Evidence state:** hypothesis | adopted | validated | rejected | superseded
**Canonical form:** <equation in project notation>
**Symbols and units:** <definitions, unit system, sign and boundary conventions>
**Source or derivation:** <paper/textbook section/equation, or project derivation with session>
**Assumes:** <scientific assumptions inherited by the form>
**Valid for:** <regime, scale, dimensionality, boundary conditions>
**Approximation:** <numerical or analytical approximation, or none>
**Combined with:** <other IDs and compatibility or known tension>
**Implemented in:** `<file>:<symbol>`
**Verified by:** <test, limiting case, benchmark, conservation check, or dataset>
**Last verified:** YYYY-MM-DD
```

Use exact internal citation locations that the corporate environment permits. Do not copy a
paper into project docs; record enough provenance for an authorized reader to recover the source.

## Evidence-state boundary

Keep these meanings separate:

| State or kind | Meaning | Durable destination |
|---|---|---|
| Hypothesis | Plausible but not established for this project | `HANDOFF.md` open question |
| Adopted model | Deliberately selected for implementation | Theory ledger + `DECISIONS.md` |
| Validated model | Passed named analytical, numerical, or empirical checks | Theory ledger with evidence |
| Numerical approximation | Computational substitution for a scientific form | Theory ledger; never disguise as theory |
| Fitted parameter | Empirical result tied to a dataset and free/fixed split | `docs/reference/parameters.md` after acceptance |
| Rejected/superseded model | Tested or replaced with a reason | `DECISIONS.md`, with revisit condition |

Repetition across sessions is evidence of persistence, not scientific truth. Do not promote a
hypothesis to `adopted` or `validated` merely because it recurs.

## Verification protocol

Verify each link independently when changing or curating a scientific model:

1. **Source fidelity:** confirm the cited source or project derivation supports the recorded form
   and assumptions. If the source is unavailable, retain the claim but mark verification pending.
2. **Mathematical integrity:** check notation, dimensions or units, signs, boundary/initial
   conditions, limiting behavior, and compatibility with mechanisms it is combined with.
3. **Implementation fidelity:** map each material term and approximation to code. Document any
   intentional computational difference and its error or applicability.
4. **Verification evidence:** prefer dimensional checks, limiting cases, conservation laws,
   analytic or published benchmarks, manufactured solutions, and controlled dataset comparisons.
   A unit test that only reproduces the current implementation is regression evidence, not model
   validation.
5. **Claim scope:** ensure conclusions do not exceed the intersection of the component models'
   validity domains or the range of the validation data.

When two links disagree, record the discrepancy and stop short of declaring the model verified.
Do not silently rewrite the canonical equation to match the implementation or vice versa.

## Project memory contract additions

During pre-init, propose only fields justified by the initial concept. For a model-centered
project, adapt the handoff spec with these fields, replacing weaker generic fields rather than
accumulating them:

1. **Active model and IDs** — current equation/mechanism set and version
2. **Changed assumptions or approximations** — changes made or proposed this session
3. **Verification state** — last check performed, outcome, and remaining `[TBD]` links
4. **Open scientific question** — hypothesis or validity issue distinct from a coding blocker

Use `[candidate]` in `SESSION_LOG.md` for a possible durable scientific fact and include its stable
ID when one exists. Use `[decision]` for an adopted, rejected, or superseded model choice. Keep raw
runs and transient numerical results in the session log; promote only accepted results with
dataset, method, uncertainty or fit quality, and provenance.

## Recommended invariants

- Never change a governing equation, scientific assumption, or model-validity claim silently.
- Never treat agreement with one dataset as proof that a mechanism is uniquely identified.
- Never omit units, sign conventions, or free/fixed parameter status at an interface.
- Never extrapolate beyond the recorded validity or validation domain without flagging it.
- Never convert an unavailable source or unresolved derivation into an uncited assertion.

Put only the applicable one-line invariants in AGENTS.md and route details to the ledger or rules
document. Every invariant needs an explicit alternative action so it can be followed rather than
worked around.
