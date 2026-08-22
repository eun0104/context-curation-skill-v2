import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = (Path(__file__).resolve().parents[1]
          / "context-curation" / "scripts" / "session_contract_blocks.py")
SPEC = importlib.util.spec_from_file_location("session_contract_blocks", SCRIPT)
blocks = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(blocks)


def write_skill(root: Path, name: str, text: str) -> Path:
    path = root / ".opencode" / "skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class SessionContractBlockTests(unittest.TestCase):
    def test_init_contract_requires_agents_routing_from_spec(self):
        skill_dir = SCRIPT.parents[1]
        block = blocks.read_template(skill_dir, "session-context-init")
        spec = (skill_dir / "templates" / "handoff-spec.md").read_text(encoding="utf-8")

        self.assertIn("AGENTS.md initialization", block)
        self.assertIn("and `plan.md` at the project root", block)
        self.assertIn("skill `context-curation`", spec)
        self.assertIn("L0 budget: 2000 tokens", spec)
        self.assertIn("`docs/handoff/HANDOFF.md`", spec)
        self.assertIn("`docs/handoff/SESSION-LOG.md`", spec)
        self.assertIn("`docs/handoff/DECISIONS.md`", spec)

    def test_contracts_require_prompt_only_git_checkpoints(self):
        skill_dir = SCRIPT.parents[1]
        init = blocks.read_template(skill_dir, "session-context-init")
        handoff = blocks.read_template(skill_dir, "session-handoff")
        spec = (skill_dir / "templates" / "handoff-spec.md").read_text(encoding="utf-8")

        self.assertIn("ask whether to run `git init`", init)
        self.assertIn("exact paths and commit message", init)
        self.assertIn("Git checkpoint policy", handoff)
        self.assertIn("explicit approval", handoff)
        self.assertIn("git --version", spec)
        self.assertIn("git rev-parse --show-toplevel", spec)
        self.assertIn("parent repository", spec)
        self.assertIn("git status --short --branch", spec)
        self.assertIn("git diff --cached --name-only", spec)
        self.assertIn("git add -- <path>...", spec)
        self.assertIn("Do not use\n  `git add -A`, `git add .`", spec)
        self.assertIn("never push, merge, rebase, reset, stash, amend", spec)

    def test_scientific_profile_applies_pre_init_and_requires_traceability(self):
        skill_dir = SCRIPT.parents[1]
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        profile = (skill_dir / "references" / "profiles"
                   / "scientific-modeling.md").read_text(encoding="utf-8")
        spec = (skill_dir / "templates" / "handoff-spec.md").read_text(encoding="utf-8")

        self.assertIn("initial concept and rough plan in pre-init", skill)
        self.assertIn("references/profiles/scientific-modeling.md", skill)
        self.assertIn("source or explicit project derivation", profile)
        self.assertIn("→ canonical equation or claim", profile)
        self.assertIn("→ implementation location", profile)
        self.assertIn("→ verification evidence", profile)
        self.assertIn("Evidence state:", profile)
        self.assertIn("Recurrence does not turn a hypothesis", skill)
        self.assertIn("Applied curation profiles:", spec)
        self.assertIn("context-curation:<profile-name>", spec)
        self.assertNotIn("references/profiles/<name>.md", spec)
        self.assertIn("curation provenance only", spec)
        self.assertIn("do not need access", spec)

    def test_check_uses_only_plural_project_skill_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            singular = root / ".opencode" / "skill" / "session-context-init" / "SKILL.md"
            singular.parent.mkdir(parents=True)
            singular.write_text("# Wrong location\n", encoding="utf-8")

            results = blocks.run(root)

            self.assertEqual(
                ["skill-missing", "skill-missing"],
                [item["status"] for item in results],
            )
            self.assertTrue(all(".opencode/skills/" in item["path"] for item in results))

    def test_apply_inserts_after_frontmatter_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init = write_skill(root, "session-context-init", "---\nname: init\n---\n\n# Init\n")
            handoff = write_skill(root, "session-handoff", "# Handoff\n")

            first = blocks.run(root, apply=True)
            first_text = {path: path.read_text(encoding="utf-8") for path in (init, handoff)}
            second = blocks.run(root, apply=True)

            self.assertEqual(["installed", "installed"], [item["status"] for item in first])
            self.assertEqual(["unchanged", "unchanged"], [item["action"] for item in second])
            self.assertEqual(first_text[init], init.read_text(encoding="utf-8"))
            self.assertEqual(first_text[handoff], handoff.read_text(encoding="utf-8"))
            self.assertLess(first_text[init].index("contract-block:start"),
                            first_text[init].index("# Init"))
            self.assertGreater(first_text[init].index("contract-block:start"),
                               first_text[init].index("name: init"))

    def test_apply_marks_an_existing_unmarked_block_without_duplication(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill_dir = SCRIPT.parents[1]
            for name in blocks.BLOCKS:
                block = blocks.read_template(skill_dir, name)
                start, end = blocks.marker_pair(name)
                core = block[len(start):len(block) - len(end)].strip()
                write_skill(root, name, f"# Existing\n\n{core}\n")

            results = blocks.run(root, apply=True)

            self.assertEqual(["marked-existing", "marked-existing"],
                             [item["action"] for item in results])
            for name in blocks.BLOCKS:
                text = (root / blocks.BLOCKS[name]["target"]).read_text(encoding="utf-8")
                self.assertEqual(1, text.count("## Project memory contract"))
                self.assertEqual(1, text.count("contract-block:start"))

    def test_partial_markers_are_reported_and_not_modified(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init = write_skill(
                root,
                "session-context-init",
                "<!-- context-curation:session-context-init-contract-block:start -->\n# Broken\n",
            )
            original = init.read_text(encoding="utf-8")
            write_skill(root, "session-handoff", "# Handoff\n")

            results = blocks.run(root, apply=True)

            self.assertEqual("malformed-block-markers", results[0]["status"])
            self.assertEqual(original, init.read_text(encoding="utf-8"))

    def test_apply_migrates_legacy_hook_markers(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in blocks.BLOCKS:
                start, end = blocks.legacy_marker_pair(name)
                write_skill(root, name, f"# Existing\n\n{start}\nold\n{end}\n")

            results = blocks.run(root, apply=True)

            self.assertEqual(["migrated-legacy-markers", "migrated-legacy-markers"],
                             [item["action"] for item in results])
            for name in blocks.BLOCKS:
                text = (root / blocks.BLOCKS[name]["target"]).read_text(encoding="utf-8")
                self.assertIn("-contract-block:start", text)
                self.assertNotIn("-hook:start", text)

    def test_old_contract_blocks_upgrade_to_git_checkpoint_policy(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in blocks.BLOCKS:
                start, end = blocks.marker_pair(name)
                write_skill(root, name, f"# Existing\n\n{start}\nold contract\n{end}\n")

            checked = blocks.run(root)
            applied = blocks.run(root, apply=True)

            self.assertEqual(["outdated", "outdated"],
                             [item["status"] for item in checked])
            self.assertEqual(["updated", "updated"],
                             [item["action"] for item in applied])
            init = (root / blocks.BLOCKS["session-context-init"]["target"])
            handoff = (root / blocks.BLOCKS["session-handoff"]["target"])
            self.assertIn("ask whether to run `git init`", init.read_text(encoding="utf-8"))
            self.assertIn("Git checkpoint policy", handoff.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
