---
name: context-curation
description: >-
  Audit and restructure a project's persistent documentation layer — AGENTS.md, plan.md,
  DECISIONS.md, and the architecture / domain / rules / reference docs beneath them. Use this
  skill whenever facts learned during recent sessions should be promoted into permanent project
  docs, when AGENTS.md has grown past its read budget, when docs have gone stale, contradictory,
  duplicated, or unreachable, when a milestone closes, when a project has session logs but no
  structured knowledge layer yet, before first-session context initialization when an initial
  project plan already exists, when scientific theories, mechanisms, equations, assumptions, or
  validation evidence need traceable project memory, or when the user says anything like
  "tune the docs",
  "restructure AGENTS.md", "the agent keeps forgetting X", "our docs have drifted", or "where
  should this fact live". Do NOT use for routine end-of-session handoff writing — that belongs
  to the session-handoff skill.
---

# Context Curation

## Where this sits

Three skills manage the project's memory. Keep the division sharp:

| Skill | Runs | Owns |
|---|---|---|
| `session-context-init` | Session 1, after pre-init curation | Creates root `AGENTS.md` and `plan.md`, then initializes files under `docs/handoff/` from the project spec |
| `session-handoff` | Every session end | Appends to `docs/handoff/SESSION_LOG.md`, rewrites `docs/handoff/HANDOFF.md`, and appends on-event records under `docs/handoff/` |
| **`context-curation`** | Once before init, then every ~5 sessions | **The doc layer and the project memory contract consumed by both session skills** |

Handoff answers *where did we stop*. This skill answers *what should stop being session state
and become project state, is that state still healthy, and — critically — **is handoff still
capturing the right things**.*

Run curation before init once an initial project concept and rough plan exist. That first pass
defines the minimum memory contract; later passes revise it from session evidence as the project
reveals what it actually needs.

The constraint behind every rule below: whatever sits in the always-read layer is paid for on
**every session, forever**. The goal is never "document more". It is to keep the always-read
layer minimal while making everything else findable at the moment it is needed.

## The layer model

Classify by **how often a doc is read**, not by how important it feels.

| Layer | Documents | Read when | Budget |
|---|---|---|---|
| **L0** | `AGENTS.md` | Every session, unconditionally | **2,000 tokens hard cap** |
| **L1** | `docs/handoff/HANDOFF.md`, root `plan.md` | Every session start, via pointer | ~1,500 tokens each |
| **L2** | `docs/handoff/DECISIONS.md`, `docs/architecture.md`, `docs/domain/*.md`, `docs/rules/*.md`, `docs/reference/*.md` | **Conditionally**, only when the task matches | Unbounded, pointer mandatory |
| **L3** | `docs/handoff/SESSION_LOG.md`, `docs/archive/` | Never read whole; grep only | Append-only |

Two failure modes this prevents: **L0 bloat**, where every session gets more expensive and the
important lines get buried; and **L2 orphans**, where a doc is correct but nothing points to it,
so it is never read. An unreachable doc is worse than no doc — it creates false confidence.

## Non-negotiables

1. **Never delete a persistent document.** Move it to `docs/archive/YYYY-MM-DD-<name>.md` with a note on what superseded it. The temporary `docs/_tuning-proposal.md` is the sole exception: remove it after approved changes are fully applied.
2. **One fact, one home.** State a fact in exactly one place; point at it everywhere else. Copying content into AGENTS.md is the most common cause of drift, because the copy never gets updated.
3. **Propose, then stop.** See Step 5. Doc restructuring is hard to review after the fact.
4. **Cite the source of every promoted fact, and show the command output that proves it** — session number, file path, or commit, plus the `grep` line it came from, pasted verbatim. Never promote something inferred rather than observed. A wrong fact in the persistent layer poisons every future session, and a citation nobody can check is indistinguishable from one that was invented.
5. **Max 2 new durable L2 knowledge files per run.** The proposal, curation state, and handoff control spec do not count. If bootstrap needs more than two L2 files, split it across runs or request explicit approval for the larger document set.
6. **Follow the project's existing conventions** — language, heading style, numbering. If the docs are Korean, write Korean.

## How this run is structured

**Run this in a fresh session, and normally across two of them.**

This is not a normal-session activity. The audit reads the doc set, the harvest reads project
history, and the verification at the end re-reads everything that changed — a lot of context, and
none of it belongs on top of a session already half-full of code.

The natural split falls exactly where the approval boundary already is:

| Pass | Steps | Ends with |
|---|---|---|
| **A — Propose** | 0–5 | `docs/_tuning-proposal.md` written, session ends |
| **B — Apply** | 6–7 | Changes applied and verified, in a fresh session |

Pass B rereads the proposal rather than relying on Pass A's context, so it starts clean. Doing
both in one session is fine when the project is small, but check the headroom rule below first.

**Headroom rule:** Steps 5–7 need room to work — the proposal, the adversarial re-read, and the
final verification pass are where quality is won or lost, and they come last. If harvesting has
consumed more than roughly half the window, stop at the end of Pass A regardless. A rushed
verification is worse than a deferred one, because it reports success either way.

## Run procedure

### Step 0 — Determine the mode

Resolve `<skill-dir>` as the directory containing the `SKILL.md` you actually loaded and announce
that base directory. The skill may be global or project-local. If both copies exist, the
project-local copy is the intended override; if the resolved directory is not the one the user
intended, stop and report the mismatch. For the entire run, load scripts, templates, references,
and integration blocks only from this same `<skill-dir>`; never mix resources from different
copies.

From the project root, run the lifecycle-aware inventory without a mode flag:

```bash
python <skill-dir>/scripts/docs_inventory.py --root .
```

Also take a read-only Git baseline. Run `git --version`, then `git rev-parse --show-toplevel`; when
they succeed, verify whether the reported top level is the project root and record the branch,
HEAD, `git status --short --branch`, and pre-existing staged paths from
`git diff --cached --name-only`. Distinguish `Git unavailable`, `not a Git work tree`, and `inside a
parent work tree`. Do not run `git init`, stage, commit, configure Git, or alter the work tree
during this baseline.

Before branching by mode, inspect `references/profiles/` using the evidence available now: the
initial concept and rough plan in pre-init, and the repository plus session history later. Read and
name every matching profile before designing the contract. Scientific projects that apply or
combine theories, mechanisms, or equations must read
`references/profiles/scientific-modeling.md`; also read a more specific profile when one matches.
Record the selected profile names in the handoff spec as `context-curation:<profile-name>` IDs,
not as Markdown paths; bundled profile files may be global and are not project-doc links.
A profile is a prior, not a checklist: propose only entries supported by project evidence.

Trust the inventory's evidence-based mode result:

- **`pre-init` → pre-init mode.** Both root startup files and initialized-session evidence are
  absent. Use the current project concept, rough plan, repository contents, and project-local
  session skills as evidence. Design only the minimum memory contract. Do not invent mature L2
  knowledge, require session logs, or treat missing startup files as defects.
- **`normal`, but no durable L2 layer exists → bootstrap mode.** Build the minimum viable L2
  set *from what the logs actually contain*, not from a fixed list — creating docs the project
  has no material for produces empty files that then rot.
- **`normal`, and a durable L2 layer exists → tune mode.** Proceed normally.
- **`ambiguous` → stop.** Startup files are partial or contradict session evidence. Show the
  reported evidence and ask the user whether initialization completed. Use `--pre-init` or
  `--normal` only after that ambiguity is explicitly resolved; ordinary invocation needs no mode
  argument.

Announce which mode is in effect before continuing.

### Step 1 — Inventory

Use the inventory report produced in Step 0. It reports per-doc token counts, L0 budget status,
orphans, broken pointers, stale docs,
duplicated passages, and how many sessions are pending harvest. If Python is unavailable,
approximate with `wc -l` and `grep -rn "docs/" AGENTS.md`.

Then check the two fixed project-local session skill paths:

```bash
python <skill-dir>/scripts/session_contract_blocks.py --root .
```

This check is read-only. `skill-missing`, `block-missing`, `legacy-markers`, `outdated`,
`malformed-block-markers`, or `duplicate-block-markers` must
become a blocking proposal item. Do not inspect or modify a global session skill as a substitute.
If `docs/handoff/handoff-spec.md` exists but lacks `AGENTS.md initialization` or `Git checkpoint
policy`, add a blocking spec item as well; the installed session blocks depend on both sections.

For how to fix each finding, read `references/audit-checks.md` now.

### Step 2 — Harvest

**In pre-init mode, skip session harvesting.** Extract candidate structure only from the initial
plan, current conversation, existing repository evidence, and any explicitly supplied project
constraints. When the inventory's section 7 lists `.omo/plans/`, that plan is the primary evidence
— read it and cite it by path. Do not copy it into root `plan.md` wholesale: the plan file is a
point-in-time planning artefact, while root `plan.md` is the living plan that milestones update. A first-pass contract is a prior to test, not proof that the project already needs a
large document set. Continue at Step 4 and propose the root startup files, the minimum
`docs/handoff/` set, and the shared spec consumed by both local session skills. The spec must
include the `AGENTS.md initialization` and `Git checkpoint policy` sections from
`templates/handoff-spec.md`; do not require the user to locate or apply a separate snippet.

For bootstrap and tune modes, continue below.

Step 3's recurrence criterion asks whether something has appeared across *multiple* sessions, so
the harvest needs to see the whole history. But full-history **coverage** does not require
full-text **reading**, and conflating the two is how a curation run arrives at Step 5 with no room
left to think.

**First, extract across the entire log — always, regardless of size:**

```bash
grep -n "\[candidate\]\|\[gotcha\]\|\[decision\]" docs/handoff/SESSION_LOG.md
```

This is complete recurrence coverage for a fraction of the cost, and it is why the handoff spec
asks for those tags. A fact surfacing in sessions 2, 9, and 14 shows up here; an incremental read
would have missed it entirely.

**Then read full text selectively**, in this priority order, stopping when roughly half the
window is consumed:

1. The sessions surrounding each tag hit — enough context to judge the candidate
2. The unharvested range since `harvested_through_session` in `docs/handoff/.curation-state.json`. If no usable checkpoint exists, read the latest five session entries.
3. Earlier sessions, only if room remains and the tag extraction looked thin

With a single append-only log, seek to a session by heading:

```bash
grep -n "^#\{1,4\} *[Ss]ession *0*7" docs/handoff/SESSION_LOG.md
sed -n '<line>,$p' docs/handoff/SESSION_LOG.md
```

If the whole log is small — the audit report gives its token count — reading it entirely is
simplest and best. The point is to decide that from the measured size rather than by starting to
read and finding out.

**Then read whatever the inventory's section 7 lists.** Under the oh-my-openagent harness, notepad
entries arrive already sorted by kind — `learnings.md`, `decisions.md`, `issues.md`,
`problems.md` — which makes them a higher-quality candidate source than session-log tags, and one
that survives a project where tagging never took hold. They are evidence only: never audit them
for reachability or staleness, and never edit them. Cite them by path like any other source.

State what was read. If the tag extraction returns nothing, tagging is not happening; say so, note
it for the handoff spec, and fall back to reading the unharvested range and section 7.

Extract candidates: things learned, decided, discovered broken, or repeatedly re-explained.
Then scan `docs/handoff/HANDOFF.md` — items that have survived several handoffs unchanged are usually
project state wearing a disguise.

Read `rejected_candidates` as prior decisions, not permanent suppression. Reconsider a rejected
candidate if it appeared again after rejection, its evidence changed, or its recorded
`reconsider_if` condition is now true. Recurrence is allowed to change the answer over time.
Treat legacy string entries as labels with unknown evidence; reconsider them on their next
appearance and migrate them to structured records when writing state.

### Step 3 — Classify

Score each candidate. **2 or more → promote.**

| Criterion | Passes when |
|---|---|
| **Recurrence** | Appeared in 2+ distinct sessions, or the user re-explained it |
| **Cost of loss** | Forgetting causes rework or a **wrong result** (not mere inconvenience) |
| **Stability** | Still true in 5 sessions (if volatile → leave in `HANDOFF.md`) |
| **Non-derivability** | Not cheaply rediscovered by reading the code or data |

Promote without scoring: **invariants** ("never" / "must always"), **rejected alternatives**
("tried X, failed because Y" — otherwise the agent proposes X again, confidently), and
**external-system quirks** the agent cannot inspect.

Reject without scoring: task progress (→ root `plan.md`), stopping point (→ `docs/handoff/HANDOFF.md`), anything
already stated elsewhere (→ add a pointer), anything inferred but unverified (→ open question).

When `references/profiles/scientific-modeling.md` applies, classify the candidate's evidence state
before promotion. Recurrence does not turn a hypothesis into an accepted scientific claim.
Require the profile's source → canonical equation or claim → implementation → verification chain;
leave any missing link explicit rather than filling it from inference.

Then route:

| The fact is… | Destination | AGENTS.md entry |
|---|---|---|
| A hard constraint | `docs/rules/<topic>-invariants.md` | **One line, verbatim** + link |
| A choice + reasoning | `docs/handoff/DECISIONS.md` | Conditional pointer |
| System structure, data flow | `docs/architecture.md` | Conditional pointer |
| External-system oddity | `docs/domain/gotchas.md` | Conditional pointer |
| Domain knowledge the agent lacks | `docs/domain/<topic>.md` | Conditional pointer |
| Settled parameters, paths, numbers | `docs/reference/<topic>.md` | Conditional pointer |

Invariants are the **only** category whose content is copied into AGENTS.md — a rule the agent
never reads is a rule that does not exist. One sentence each, roughly seven maximum.

For borderline cases, worked examples, and the exact format of each doc type, read
`references/promotion-test.md` and `references/routing-table.md`.

### Step 4 — Structural fixes

Combine Step 1's findings with Step 3's additions: L0 over budget → demote content to L2, leave
a pointer; orphan → add a pointer or archive; duplication → pick the canonical home, replace the
rest with pointers.

Staleness flags from the script are suspicions based on the last commit (or filesystem mtime
outside Git) and the latest verification marker, not verdicts. Where context allows, **open the
code or data each flagged doc describes and check whether it still
holds** rather than asking the user. A doc confirmed accurate gets a `<!-- verified: DATE -->`
marker that resets its staleness clock; it becomes eligible again after the threshold. A doc
found wrong becomes a rewrite plus, usually, an ADR recording what changed.

For scientific model documents, code is not the sole authority. Follow the verification protocol
in `references/profiles/scientific-modeling.md`: check the cited source or derivation, canonical
equation and conventions, implementation mapping, and validation evidence as separate links. A
mismatch is a finding to resolve, not permission to rewrite the theory to match the code.

Read `references/agents-md-contract.md` before touching AGENTS.md.

### Step 5 — Proposal, then STOP

Write `docs/_tuning-proposal.md` using `templates/tuning-proposal.md`, ordered by impact (L0
budget first, then invariants, then the rest). Each item needs its source citation, destination,
and a before/after. Scientific items also need their traceability chain and evidence state; use
`[TBD]` for a missing link and make it a blocker or open question. Changes to the handoff spec go
in their own section — they alter what
happens every session from now on, so they deserve separate scrutiny from one-off doc edits.
Include the read-only Git baseline. Treat a missing or stale `Git checkpoint policy` as a handoff
spec proposal item, not as permission to initialize or commit.

Then **re-read the proposal as an adversary before showing it.** Re-apply the promotion test to
every item in section B and cut anything that no longer scores 2. Check that no item restates
content that already exists elsewhere in the doc set. This pass is cheap and it protects the one
thing that does not scale: a proposal with twelve items, four of them weak, gets a worse review
than one with eight solid items, because the reviewer's scepticism is spent on the wrong ones.

**Then verify every citation in section B by re-reading it, and paste the output.** For each
promoted fact, run the command that retrieves its cited line and copy the result into the item's
`Evidence` field verbatim:

```bash
grep -n "<distinctive phrase from the fact>" docs/handoff/SESSION_LOG.md
sed -n '<line>p' <cited file>          # for a non-log source
```

Do not paraphrase the output, and do not write the field from memory — re-run the command even
when you are confident, because confidence is exactly what a fabricated citation also feels like.
If the command returns nothing, or returns a line that does not support the claim, the item is
not promotable: cut it, or demote it to an open question. Say which items this removed.

This is the one check the user cannot perform by reading the proposal alone. Everything else in
Pass A is visible in the diff at approval time; a citation is not, so a wrong one survives review
and lands in the permanent layer, where rule 4 says it poisons every future session.

State how many items were cut by each of the two passes, separately.

This is the end of Pass A. Unless the project is small and the window still has clear headroom,
end the session here — Pass B will reread the proposal and start clean.

**Do not create, edit, move, or archive any persistent project file in this step.** The temporary
proposal file is the only thing written. Present it and wait for explicit approval, item by item. Section G is
informational — there is nothing there to approve, because nothing there gets applied. If the user rejects an
item, ask whether the underlying rule should change — pushback usually generalizes.

### Step 6 — Apply

Only after approval, in this order:

Before writing, repeat the read-only Git baseline. If HEAD changed, an approved target changed, or
new staged paths appeared since the proposal, stop and show the difference. Never stash, reset,
checkout, or overwrite the user's work to make the baseline match.

1. If a session contract-block blocking item was approved, run
   `python <skill-dir>/scripts/session_contract_blocks.py --root . --apply`. It changes only the
   two known project-local SKILL.md files and is idempotent. Approved application migrates markers
   that used the inaccurate term `hook`. Resolve missing skills or malformed markers manually
   rather than writing elsewhere.
2. Create or edit the destination docs, using `templates/` for new files.
3. Update the AGENTS.md pointer table. Every new L2 doc needs a trigger condition phrased as a
   situation the agent will recognise itself to be in — "when working on this project" is not
   one. In pre-init mode, do not create AGENTS.md or plan.md; put their approved startup contract,
   including the required curation routing entry and L0 budget marker, in the spec and let
   `session-context-init` create both root files.
4. **Update `docs/handoff/handoff-spec.md`** — see the next section. Both project-local session
   skills consume it. Classify each doc `per-session` / `on-event` / `frozen` and add only
   `per-session` docs to the checklist.
5. Append an entry to `docs/handoff/DECISIONS.md` describing the restructuring itself. In pre-init
   mode, let `session-context-init` create this file from the approved spec instead.
6. Update `docs/handoff/.curation-state.json`: date, session number (null before init),
   `harvested_through_session`, one-line summary, and structured rejected-candidate records. Store
   each as `{"label": ..., "rejected_at_session": ..., "reason": ..., "reconsider_if": ...}`.
7. Remove `docs/_tuning-proposal.md` — it is a temporary review artifact, not a persistent document. A stale proposal left in `docs/` becomes an orphan at the next audit.

### Step 7 — Self-check

Before reporting done, verify and state each:

- [ ] AGENTS.md token count: before → after, and whether it is under budget
- [ ] Every new doc has an inbound pointer with a real trigger condition
- [ ] No content was copied rather than pointed at
- [ ] No persistent document was deleted — only archived; the temporary proposal was removed
- [ ] Every applied promotion carried a verified `Evidence` block, not a bare citation
- [ ] `docs/handoff/.curation-state.json` updated
- [ ] Net change to per-session work stated explicitly
- [ ] Git HEAD and pre-existing staged work were preserved
- [ ] Handoff spec contains the prompt-only `Git checkpoint policy`
- [ ] When a scientific profile applies, every accepted model claim has source, canonical form,
  implementation mapping, and verification evidence; unresolved links remain explicit

Re-run `docs_inventory.py` to confirm rather than asserting from memory. Then **re-read every
document that changed, plus AGENTS.md, in full**, and check that nothing now contradicts anything
else. Restructuring is exactly when contradictions get introduced — a fact moved to a new home
while an old summary of it survives elsewhere — and it is much cheaper to catch here than three
sessions later when a session has already acted on the wrong copy.

In pre-init mode, rerun `docs_inventory.py --root .` without a mode flag and require it to remain
`pre-init`. Verify that the spec contains its `AGENTS.md initialization` section, rerun
`session_contract_blocks.py --root .`, and require both statuses to be `installed`. Then instruct
the user to run `session-context-init`. Perform the normal AGENTS.md and plan.md checks after init
creates them.

After an approved **normal-mode** apply, follow the spec's `Git checkpoint policy`: show the final
read-only status and offer a commit for the exact curation-owned paths and proposed message. Do not
stage or commit without explicit approval. In pre-init mode, leave repository initialization and
the first checkpoint offer to `session-context-init`.

## Tuning the handoff spec

### Where a change goes

The question is not which directory a file sits in. It is **how many projects the change
affects**, and whether that blast radius was chosen deliberately rather than stumbled into.

| The change is… | Goes to | Who applies it |
|---|---|---|
| Project-specific — this project's doc set, cadences, fields | `docs/handoff/handoff-spec.md` | This skill, after approval |
| Generalizable — an improvement every project would want | Noted in section G | **The user, by hand** |

Default hard to the spec. A finding from one project is not evidence that it generalizes; it is
one data point. Mistaking a local need for a universal one is the cheap and common error here,
and it is the one whose consequences land somewhere you are not looking.

Keep `session-context-init` and `session-handoff` project-local. Treat shared copies as upstream
templates and pin the runtime copies under `.opencode/skills/` so their behaviour is versioned with
the project. Keep the spec mandatory even when both skills are local: it is the single declarative
contract that prevents init and handoff from drifting apart. Edit a local SKILL.md only when the
change cannot be represented in the spec; record generalizable improvements for the shared
upstream in section G.

Both project-local session skills must read `docs/handoff/handoff-spec.md`. Install those contract
blocks during the first approved pre-init curation. If either local skill or block is missing, make
fixing the project-local copy a blocking proposal item; do not silently continue with two different
path contracts. Use `scripts/session_contract_blocks.py` so detection and insertion use the same markers.
These blocks are Markdown instructions, not deterministic runtime hooks.

### When a finding generalizes

Occasionally a candidate is not about this project at all — it is an improvement the shared
`session-handoff` skill should have for every project.

**Note it in section G of the proposal and stop there. Write no file outside the project.**

This boundary is not about what the model can be trusted to edit. It is what keeps the shared
skill worth sharing. A file that several projects depend on should change when a person decides
it should, having considered those other projects — not as a side effect of one project's tuning
pass, where the evidence is one project wide and the reviewer is looking at this project's docs
rather than at whatever else depends on that file. A shared-file edit also leaves no trace in any
project's history, so it is the one change here that cannot be reconstructed afterwards.

Section G is therefore a note, not an action: what was observed, why it looks general, and the
exact edit if the user wants it. One or two lines. Applying it is theirs.

Reading shared files is unrestricted — comparing the spec's `Base skill version` against the
installed skill each run is how a project avoids sitting on defaults that were improved
centrally months ago.

### What the spec controls

- **AGENTS.md initialization** — the required curation routing entry and L0 budget marker
- **Git checkpoints** — prompt-only repository initialization and narrow session-end commits
- **Document set** — which files handoff writes each session
- **Cadence** — `per-session` / `on-event` / `frozen` per document
- **HANDOFF.md fields** — the questions the next session actually needs answered
- **Tagging** — which markers to leave in the session log for the next harvest

### Reading the evidence

Symptoms come from the session log and from the harvest, not from taste:

| Symptom in the logs | Change to the spec |
|---|---|
| A session opened by re-deriving something the previous session knew | Add a required `HANDOFF.md` field for it |
| A field reads "n/a" in most sessions | Remove it — noise crowds out the fields that matter |
| A doc is rewritten every session but rarely changes | Move to `on-event` |
| A doc changed materially and nobody noticed for several sessions | Move to `per-session` |
| The same `[gotcha]` tag keeps reappearing | The fact belongs in L2; promote it and stop re-logging it |
| Harvest found nothing taggable | Tagging is not happening — restate it in the spec with an example |

**Fields are a budget, not a wishlist.** Every added field is filled in at the end of every
session, when attention is lowest. A spec with fifteen fields produces fifteen shallow answers.
When adding one, name the one it replaces.

## When to run

Every session wastes context; never lets the docs rot. Trigger on: 5+ sessions since
`last_tuned` · AGENTS.md over budget · a `plan.md` milestone closing · 3+ accumulated
learned/gotcha items · entering a new subsystem · **the user reporting that the agent keeps
forgetting or re-deriving something**.

That last one deserves action even if nothing else has triggered — it is direct evidence that a
fact belongs in the persistent layer and is not there.

## Bundled resources

| Path | Read when |
|---|---|
| `references/promotion-test.md` | Step 3 — borderline promotion calls, worked examples |
| `references/routing-table.md` | Step 3 — destination choice and exact doc formats |
| `references/audit-checks.md` | Steps 1 and 4 — interpreting each inventory finding |
| `references/agents-md-contract.md` | Steps 4 and 6 — before editing AGENTS.md |
| `references/profiles/*.md` | Step 0 — pre-init, bootstrap, and tune, when a profile matches the project type |
| `templates/handoff-spec.md` | When creating or changing the project memory contract |
| `templates/*.md` | Step 6 — creating a new persistent doc |
| `scripts/docs_inventory.py` | Step 1 — run it, no need to read it |
| `scripts/session_contract_blocks.py` | Steps 1, 6, and 7 — check, apply after approval, verify |
| `integration/` | First-time setup only |
