# Reference session skills

`context-curation` does not work alone. It writes `docs/handoff/handoff-spec.md`, and two other
skills read it: `session-context-init` creates the document set the spec declares, and
`session-handoff` writes into it at the end of every session.

Those two skills used to exist here only as the contract fragments in
[`../context-curation/integration/`](../context-curation/integration/) — instructions to paste
into a skill kept somewhere else. That left the contract with no implementation to check against,
and a mismatch could only be found in production. It was: the audit looked for
`SESSION-LOG.md` while the runtime skills wrote `SESSION_LOG.md`, and nothing noticed until a user
said so.

These are the implementations the curation skill is developed and tested against.
[`../tests/test_lifecycle_contract.py`](../tests/test_lifecycle_contract.py) feeds one skill's
documented output to another skill's reader, so that class of seam bug fails a test instead of a
project.

## They are a reference, not a mandate

The spec is the contract. These files are one correct reading of it, useful because it can be
executed and tested — but a project that pins its own copies is doing the intended thing, and its
copies stay authoritative for that project.

Where a reference skill and the spec disagree, **the spec wins and the reference skill is the
bug.** Both files say so in their own text.

## Using them in a project

```bash
PROJECT_DIR=/path/to/project
mkdir -p "$PROJECT_DIR/.opencode/skills"
cp -r reference-skills/session-context-init "$PROJECT_DIR/.opencode/skills/"
cp -r reference-skills/session-handoff      "$PROJECT_DIR/.opencode/skills/"
```

They ship with their contract blocks already installed, so
`session_contract_blocks.py --root <project>` reports `installed` for both without an apply step.

If you already run your own copies, keep them. Compare against these when a curation run reports a
contract finding, and treat any difference as a question about which side is right — the answer is
whichever one matches the spec.

## Keeping them honest

The contract tests check the seams, not the prose: that the session-log heading the handoff skill
documents is the one `docs_inventory.py` counts, that both skills carry valid contract blocks,
that every path they name matches the audit's path contract, that the handoff skill defers the
field list to the spec rather than copying it, and that neither skill reaches into the other's
half of the lifecycle.

Change the spec and these tests will tell you which skill has to change with it.
