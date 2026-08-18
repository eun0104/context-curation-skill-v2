# session-context-init — project-local contract hook

Copy the shared skill into `.opencode/skill/session-context-init/`, pin its upstream version, and
add this before its file-creation procedure:

```markdown
## Project memory contract

Require `docs/handoff/handoff-spec.md` before initialization and read it first. Keep `AGENTS.md`
and `PLAN.md` at the project root. Create handoff-owned files only under `docs/handoff/`, using
the paths, initial fields, and cadences declared in the spec.

If the spec is missing, ask the user to run `context-curation` in pre-init mode. Do not invent a
default document layout.
```

This makes curation-before-init deterministic: curation designs the contract, then init creates
the first concrete files from that approved contract.
