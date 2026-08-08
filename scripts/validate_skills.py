#!/usr/bin/env python3
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9-]+$")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("---\n"):
        return {}, ["missing YAML frontmatter"]

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, ["unterminated YAML frontmatter"]

    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata, errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"

    if not NAME_RE.fullmatch(skill_dir.name):
        errors.append("directory name must use lowercase letters, digits, and hyphens")

    if not skill_md.exists():
        return errors + ["missing SKILL.md"]

    metadata, frontmatter_errors = parse_frontmatter(skill_md)
    errors.extend(frontmatter_errors)

    name = metadata.get("name")
    description = metadata.get("description")

    if not name:
        errors.append("frontmatter missing name")
    elif name != skill_dir.name:
        errors.append(f"frontmatter name {name!r} must match directory {skill_dir.name!r}")
    elif not NAME_RE.fullmatch(name):
        errors.append("frontmatter name must use lowercase letters, digits, and hyphens")

    if not description:
        errors.append("frontmatter missing description")

    return errors


def main() -> int:
    if not SKILLS_DIR.exists():
        print("No skills/ directory found", file=sys.stderr)
        return 1

    failures: list[tuple[Path, list[str]]] = []
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())

    if not skill_dirs:
        print("No skills found", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            failures.append((skill_dir, errors))

    if failures:
        for skill_dir, errors in failures:
            print(f"{skill_dir.relative_to(ROOT)}:")
            for error in errors:
                print(f"  - {error}")
        return 1

    print(f"Validated {len(skill_dirs)} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
