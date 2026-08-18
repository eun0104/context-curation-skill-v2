import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = (Path(__file__).resolve().parents[1]
          / "context-curation" / "scripts" / "session_skill_hooks.py")
SPEC = importlib.util.spec_from_file_location("session_skill_hooks", SCRIPT)
hooks = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(hooks)


def write_skill(root: Path, name: str, text: str) -> Path:
    path = root / ".opencode" / "skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class SessionSkillHookTests(unittest.TestCase):
    def test_check_uses_only_plural_project_skill_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            singular = root / ".opencode" / "skill" / "session-context-init" / "SKILL.md"
            singular.parent.mkdir(parents=True)
            singular.write_text("# Wrong location\n", encoding="utf-8")

            results = hooks.run(root)

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

            first = hooks.run(root, apply=True)
            first_text = {path: path.read_text(encoding="utf-8") for path in (init, handoff)}
            second = hooks.run(root, apply=True)

            self.assertEqual(["installed", "installed"], [item["status"] for item in first])
            self.assertEqual(["unchanged", "unchanged"], [item["action"] for item in second])
            self.assertEqual(first_text[init], init.read_text(encoding="utf-8"))
            self.assertEqual(first_text[handoff], handoff.read_text(encoding="utf-8"))
            self.assertLess(first_text[init].index("hook:start"), first_text[init].index("# Init"))
            self.assertGreater(first_text[init].index("hook:start"), first_text[init].index("name: init"))

    def test_apply_marks_an_existing_unmarked_hook_without_duplication(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill_dir = SCRIPT.parents[1]
            for name in hooks.HOOKS:
                block = hooks.read_template(skill_dir, name)
                start, end = hooks.marker_pair(name)
                core = block[len(start):len(block) - len(end)].strip()
                write_skill(root, name, f"# Existing\n\n{core}\n")

            results = hooks.run(root, apply=True)

            self.assertEqual(["marked-existing", "marked-existing"],
                             [item["action"] for item in results])
            for name in hooks.HOOKS:
                text = (root / hooks.HOOKS[name]["target"]).read_text(encoding="utf-8")
                self.assertEqual(1, text.count("## Project memory contract"))
                self.assertEqual(1, text.count("hook:start"))

    def test_partial_markers_are_reported_and_not_modified(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init = write_skill(
                root,
                "session-context-init",
                "<!-- context-curation:session-context-init-hook:start -->\n# Broken\n",
            )
            original = init.read_text(encoding="utf-8")
            write_skill(root, "session-handoff", "# Handoff\n")

            results = hooks.run(root, apply=True)

            self.assertEqual("malformed-markers", results[0]["status"])
            self.assertEqual(original, init.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
