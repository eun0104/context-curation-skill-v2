"""Contract tests across the three skills.

The other suites test one script at a time. These check that the reference
session skills and the curation skill still agree about the things they have to
agree about: file paths, the session-log heading form, the required handoff
fields, and the contract blocks.

This is the suite that would have caught SESSION-LOG.md vs SESSION_LOG.md. A
mismatch there is invisible to a per-script test, because each side is
internally consistent; it only shows up when one skill's output is fed to
another skill's reader.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "context-curation"
REFERENCE = ROOT / "reference-skills"


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, SKILL_DIR / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


inventory = load("docs_inventory", "scripts/docs_inventory.py")
blocks = load("session_contract_blocks", "scripts/session_contract_blocks.py")

SPEC = (SKILL_DIR / "templates" / "handoff-spec.md").read_text(encoding="utf-8")
INIT = (REFERENCE / "session-context-init" / "SKILL.md").read_text(encoding="utf-8")
HANDOFF = (REFERENCE / "session-handoff" / "SKILL.md").read_text(encoding="utf-8")


class LifecycleContractTests(unittest.TestCase):
    def test_reference_skills_already_satisfy_the_contract_block_check(self):
        # Shipping the blocks pre-installed means the checker is exercised
        # against a real skill file, not only against fixtures it built itself.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in ("session-context-init", "session-handoff"):
                target = root / ".opencode" / "skills" / name
                target.mkdir(parents=True)
                shutil.copy(REFERENCE / name / "SKILL.md", target / "SKILL.md")

            results = blocks.run(root)

            self.assertEqual(["installed", "installed"],
                             [item["status"] for item in results])

    def test_the_session_heading_handoff_writes_is_the_one_the_audit_counts(self):
        # The SESSION-LOG.md/SESSION_LOG.md class of bug: each side self
        # consistent, the seam broken. Build a log the way the spec documents
        # it, then read it with the audit script's own parser.
        entry_format = SPEC.split("## SESSION_LOG.md entry format", 1)[1]
        heading = re.search(r"^## Session NNN — YYYY-MM-DD$", entry_format, re.MULTILINE)
        self.assertIsNotNone(heading, "spec no longer documents the heading form")

        with tempfile.TemporaryDirectory() as raw:
            log = Path(raw) / "SESSION_LOG.md"
            log.write_text(
                "## Session 001 — 2026-06-01\n\n### Did\n- Work.\n\n"
                "### Learned\n- [candidate] A fact.\n\n"
                "## Session 002 — 2026-06-08\n\n### Did\n- More work.\n",
                encoding="utf-8")

            stats = inventory.session_stats([log])

            self.assertEqual(2, stats["entries"])
            self.assertEqual(2, stats["latest"])

    def test_every_path_the_skills_name_matches_the_audit_contract(self):
        for path in inventory.REQUIRED_L1_PATHS:
            self.assertIn(path, SPEC, f"{path} is not declared in the spec")
        self.assertIn("docs/handoff/SESSION_LOG.md", inventory.SESSION_GLOBS)
        self.assertIn("docs/handoff/SESSION_LOG.md", SPEC)
        self.assertIn("SESSION_LOG.md", HANDOFF)
        self.assertIn("AGENTS.md", INIT)
        self.assertIn("plan.md", INIT)
        # The state file handoff reads must be the one curation writes.
        self.assertIn(inventory.STATE_FILE, HANDOFF)

    def test_handoff_defers_the_field_list_and_names_no_field_the_spec_dropped(self):
        # The spec owns the field list; repeating it in the skill would be the
        # copy that stops getting updated. So this checks deference, plus that
        # every field the skill does name for illustration still exists -- a
        # renamed field otherwise leaves a worked example quietly pointing at
        # something that is no longer written.
        fields = set(re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", SPEC, re.MULTILINE))
        self.assertGreaterEqual(len(fields), 4, "spec lost its required fields")
        self.assertIn("every field the spec requires", HANDOFF)

        section = HANDOFF.split("### 2 — Rewrite HANDOFF.md", 1)[1].split("\n### ", 1)[0]
        named = set(re.findall(r"\*\*([A-Z][a-z][^*]{2,24})\*\*", section))
        self.assertTrue(named, "handoff illustrates no field at all")
        self.assertEqual(set(), named - fields,
                         f"handoff names fields the spec does not declare: {named - fields}")

    def test_each_skill_owns_only_its_half_of_the_lifecycle(self):
        # Overlap here is how two skills quietly start writing the same file.
        self.assertIn("session-handoff", INIT)
        self.assertIn("context-curation", HANDOFF)
        self.assertIn("Suggest, do not run", HANDOFF)
        self.assertNotIn("_tuning-proposal", HANDOFF)
        self.assertNotIn("_tuning-proposal", INIT)

    def test_reference_skills_declare_the_frontmatter_a_harness_needs(self):
        for text, name in ((INIT, "session-context-init"), (HANDOFF, "session-handoff")):
            self.assertTrue(text.startswith("---\n"), f"{name} has no frontmatter")
            front = text.split("---", 2)[1]
            self.assertIn(f"name: {name}", front)
            self.assertIn("description:", front)

    def test_the_git_policy_both_skills_defer_to_stays_prompt_only(self):
        policy = SPEC.split("## Git checkpoint policy", 1)[1].split("\n## ", 1)[0]
        self.assertIn("never push, merge, rebase, reset, stash", policy)
        self.assertIn("git add -A", policy)
        for text in (INIT, HANDOFF):
            self.assertIn("Git checkpoint policy", text)
            self.assertIn("without explicit approval", text.replace(
                "without the user's explicit approval", "without explicit approval"))


if __name__ == "__main__":
    unittest.main()
