#!/usr/bin/env python3
"""Check or install context-curation hooks in project-local session skills.

Only the two fixed paths below are inspected or changed:
  .opencode/skills/session-context-init/SKILL.md
  .opencode/skills/session-handoff/SKILL.md

The default mode is read-only. Use --apply only after the corresponding proposal
item has been approved. Repeated application is idempotent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


HOOKS = {
    "session-context-init": {
        "target": ".opencode/skills/session-context-init/SKILL.md",
        "template": "session-context-init-snippet.md",
    },
    "session-handoff": {
        "target": ".opencode/skills/session-handoff/SKILL.md",
        "template": "session-handoff-snippet.md",
    },
}

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n.*?\n---[ \t]*\n", re.DOTALL)


def read_template(skill_dir: Path, name: str) -> str:
    path = skill_dir / "integration" / HOOKS[name]["template"]
    block = path.read_text(encoding="utf-8").strip()
    start = f"<!-- context-curation:{name}-hook:start -->"
    end = f"<!-- context-curation:{name}-hook:end -->"
    if not (block.startswith(start) and block.endswith(end)):
        raise ValueError(f"Invalid hook template markers: {path}")
    return block


def marker_pair(name: str) -> Tuple[str, str]:
    return (
        f"<!-- context-curation:{name}-hook:start -->",
        f"<!-- context-curation:{name}-hook:end -->",
    )


def inspect_target(root: Path, skill_dir: Path, name: str) -> Dict[str, str]:
    relative = HOOKS[name]["target"]
    target = root / relative
    if not target.is_file():
        return {"skill": name, "path": relative, "status": "skill-missing"}

    text = target.read_text(encoding="utf-8")
    start, end = marker_pair(name)
    has_start = start in text
    has_end = end in text
    if has_start != has_end:
        status = "malformed-markers"
    elif has_start:
        expected = read_template(skill_dir, name)
        installed = text[text.index(start):text.index(end) + len(end)]
        status = "installed" if installed == expected else "outdated"
    else:
        status = "hook-missing"
    return {"skill": name, "path": relative, "status": status}


def insert_after_frontmatter(text: str, block: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if match:
        head = text[:match.end()].rstrip("\n")
        tail = text[match.end():].lstrip("\n")
        return f"{head}\n\n{block}\n\n{tail}" if tail else f"{head}\n\n{block}\n"
    body = text.lstrip("\n")
    return f"{block}\n\n{body}" if body else f"{block}\n"


def apply_target(root: Path, skill_dir: Path, name: str) -> Dict[str, str]:
    result = inspect_target(root, skill_dir, name)
    status = result["status"]
    if status in {"skill-missing", "malformed-markers"}:
        return result
    if status == "installed":
        result["action"] = "unchanged"
        return result

    target = root / result["path"]
    text = target.read_text(encoding="utf-8")
    block = read_template(skill_dir, name)
    start, end = marker_pair(name)

    if status == "outdated":
        before = text[:text.index(start)]
        after = text[text.index(end) + len(end):]
        updated = before + block + after
        action = "updated"
    else:
        core = block[len(start):len(block) - len(end)].strip()
        if core in text:
            updated = text.replace(core, block, 1)
            action = "marked-existing"
        else:
            updated = insert_after_frontmatter(text, block)
            action = "installed"

    target.write_text(updated, encoding="utf-8")
    result["status"] = "installed"
    result["action"] = action
    return result


def run(root: Path, apply: bool = False) -> List[Dict[str, str]]:
    root = root.resolve()
    skill_dir = Path(__file__).resolve().parents[1]
    operation = apply_target if apply else inspect_target
    return [operation(root, skill_dir, name) for name in HOOKS]


def print_human(results: List[Dict[str, str]], apply: bool) -> None:
    label = "apply" if apply else "check"
    print(f"Project session hook {label}: .opencode/skills/")
    for item in results:
        suffix = f" ({item['action']})" if "action" in item else ""
        print(f"- {item['skill']}: {item['status']}{suffix} — {item['path']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Install or update hooks. Use only after explicit proposal approval.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = run(Path(args.root), apply=args.apply)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_human(results, args.apply)
    return 0 if all(item["status"] == "installed" for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
