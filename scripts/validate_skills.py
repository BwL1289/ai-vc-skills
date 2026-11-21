"""Check every agent skill in skills/ against the Agent Skills rules and this repository's own.

Run from anywhere: ``python scripts/validate_skills.py``. It exits 1 and prints one line per problem, or prints how
many skills it checked. The rules:

- each ``skills/<folder>/SKILL.md`` starts with a ``---`` frontmatter block holding ``name`` and ``description``;
- ``name`` equals the folder, is at most 64 characters, and uses only lowercase letters, digits and single hyphens;
- ``description`` is at most 1,024 characters, and neither field contains ``<`` or ``>``;
- the root README links every skill folder, so the skills table never falls behind;
- ``.claude-plugin/plugin.json`` points its ``skills`` field at the skills folder.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
FENCE = "---"


def frontmatter(text: str) -> dict[str, str] | None:
    """The ``key: value`` lines of a leading ``---`` block, or None when the file has no such block."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FENCE:
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == FENCE:
            return fields
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return None


def check_skill(folder: Path) -> list[str]:
    """Every problem with one skill folder, each as a line naming the folder."""
    where = f"skills/{folder.name}"
    skill_file = folder / "SKILL.md"
    if not skill_file.is_file():
        return [f"{where}: no SKILL.md"]
    fields = frontmatter(skill_file.read_text(encoding="utf-8"))
    if fields is None:
        return [f"{where}/SKILL.md: no frontmatter block between --- lines at the top"]

    problems = []
    name, description = fields.get("name", ""), fields.get("description", "")
    if not name:
        problems.append(f"{where}/SKILL.md: no name")
    elif name != folder.name:
        problems.append(f"{where}/SKILL.md: name {name!r} differs from the folder {folder.name!r}")
    if name and (len(name) > NAME_MAX or not NAME_PATTERN.match(name)):
        problems.append(f"{where}/SKILL.md: name {name!r} must be lowercase letters, digits and single hyphens")
    if not description:
        problems.append(f"{where}/SKILL.md: no description")
    elif len(description) > DESCRIPTION_MAX:
        problems.append(f"{where}/SKILL.md: description is {len(description)} characters, over {DESCRIPTION_MAX}")
    if any(mark in name + description for mark in "<>"):
        problems.append(f"{where}/SKILL.md: name and description may not contain < or >")
    return problems


def check_repository(root: Path) -> tuple[int, list[str]]:
    """How many skills there are and every problem across the skills, the README and the plugin manifest."""
    skills_dir = root / "skills"
    folders = sorted(path for path in skills_dir.iterdir() if path.is_dir()) if skills_dir.is_dir() else []
    problems = [] if folders else ["skills/: no skill folders"]
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    for folder in folders:
        problems += check_skill(folder)
        if f"(skills/{folder.name}" not in readme:
            problems.append(f"README.md: no link to skills/{folder.name}/ in the skills table")

    manifest = root / ".claude-plugin" / "plugin.json"
    if manifest.is_file():
        skills_field = json.loads(manifest.read_text(encoding="utf-8")).get("skills")
        if skills_field not in ("./skills", "./skills/"):
            problems.append(f".claude-plugin/plugin.json: skills is {skills_field!r}, not './skills'")
    return len(folders), problems


def main() -> int:
    count, problems = check_repository(ROOT)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"{count} skill(s) checked, no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
