# session-handoff — project-local contract hook

Copy the shared skill into `.opencode/skill/session-handoff/`, pin its upstream version, and add
this near the top of the project-local `SKILL.md`:

```markdown
## Project memory contract

Read `docs/handoff/handoff-spec.md` before writing any session state. Follow its document paths,
cadences, handoff fields, and session-log entry format. It overrides this skill's defaults.

The spec is maintained by `context-curation`. Do not edit it during routine handoff. If it is
missing after initialization, stop and report the broken project setup instead of falling back to
a different path layout.
```

Keep project-specific schema in the spec, not duplicated in the local skill. If a procedural
improvement would benefit every project, propose it separately for the shared upstream template.
