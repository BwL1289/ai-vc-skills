"""The skill validator passes this repository and names each kind of broken skill."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from validate_skills import DESCRIPTION_MAX, ROOT, check_repository, main

_GOOD = "---\nname: {name}\ndescription: Does one thing. Use when asked.\n---\n\n# Body\n"


def _repo(tmp_path: Path, skills: dict[str, str], readme_links: list[str] | None = None) -> Path:
    for folder, text in skills.items():
        (tmp_path / "skills" / folder).mkdir(parents=True)
        (tmp_path / "skills" / folder / "SKILL.md").write_text(text, encoding="utf-8")
    links = skills if readme_links is None else readme_links
    (tmp_path / "README.md").write_text("".join(f"[x](skills/{name}/SKILL.md)\n" for name in links), encoding="utf-8")
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(json.dumps({"skills": "./skills"}), encoding="utf-8")
    return tmp_path


def test_this_repository_passes(capsys: pytest.CaptureFixture[str]) -> None:
    count, problems = check_repository(ROOT)

    assert problems == []
    assert count >= 1
    assert main() == 0
    assert "no problems" in capsys.readouterr().out


def test_a_good_skill_passes(tmp_path: Path) -> None:
    assert check_repository(_repo(tmp_path, {"deal-math": _GOOD.format(name="deal-math")})) == (1, [])


@pytest.mark.parametrize(
    ("folder", "text", "expected"),
    [
        ("deal-math", "# no frontmatter\n", "no frontmatter"),
        ("deal-math", _GOOD.format(name="term-sheet"), "differs from the folder"),
        ("Deal_Math", _GOOD.format(name="Deal_Math"), "lowercase letters"),
        ("deal-math", "---\nname: deal-math\n---\n", "no description"),
        ("deal-math", f"---\nname: deal-math\ndescription: {'x' * (DESCRIPTION_MAX + 1)}\n---\n", "over 1024"),
        ("deal-math", "---\nname: deal-math\ndescription: Use <when> asked.\n---\n", "may not contain"),
    ],
)
def test_each_broken_skill_is_named(tmp_path: Path, folder: str, text: str, expected: str) -> None:
    _, problems = check_repository(_repo(tmp_path, {folder: text}))

    assert any(expected in problem and folder in problem for problem in problems), problems


def test_a_skill_missing_from_the_readme_is_named(tmp_path: Path) -> None:
    _, problems = check_repository(_repo(tmp_path, {"deal-math": _GOOD.format(name="deal-math")}, readme_links=[]))

    assert problems == ["README.md: no link to skills/deal-math/ in the skills table"]


def test_a_manifest_pointing_elsewhere_is_named(tmp_path: Path) -> None:
    root = _repo(tmp_path, {"deal-math": _GOOD.format(name="deal-math")})
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"skills": "./other"}), encoding="utf-8")

    _, problems = check_repository(root)

    assert problems == [".claude-plugin/plugin.json: skills is './other', not './skills'"]


def test_no_skills_at_all_is_named(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("", encoding="utf-8")

    assert check_repository(tmp_path) == (0, ["skills/: no skill folders"])
