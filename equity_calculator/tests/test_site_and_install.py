"""The website, the install guide and the plugin descriptions keep up with the skills folder.

docs/index.html carries one skill card and one GitHub link per folder under skills/, says in words how many skills
there are, and counts the calculator's scenarios as the root README does. Its two calculator examples are labelled real
output, so every line each one shows must appear in what its command prints today. docs/install.md tells a manual
install to load every folder under skills/ and repeats the README's two load-both-folders lines, because two skills
read a file in another skill's folder. The plugin and marketplace descriptions promise no skill as still to come.
"""

from __future__ import annotations

import html
import json
import re
import shlex
from pathlib import Path

import pytest
from equity_calculator.__main__ import run

_ROOT = Path(__file__).resolve().parents[2]
_SITE = _ROOT / "docs" / "index.html"
_INSTALL = _ROOT / "docs" / "install.md"
_README = _ROOT / "README.md"
_SKILLS = sorted(path.parent.name for path in (_ROOT / "skills").glob("*/SKILL.md"))
_ONES = "zero one two three four five six seven eight nine".split()
_NUMBER_WORDS = {
    word: value
    for value, word in enumerate(
        _ONES
        + "ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
        + [f"twenty-{one}" for one in _ONES[1:]]
    )
}
# A count word may be hyphenated ("twenty-one"), so each pattern takes the whole word, hyphen included.
_SITE_SKILL_COUNT = re.compile(r"([\w-]+) skills for Claude and any MCP client")
_SITE_SCENARIO_COUNT = re.compile(r"Works ([\w-]+) equity questions exactly")
_README_SCENARIO_COUNT = re.compile(r"The `equity-calculator` skill covers ([\w-]+) scenarios")
_SITE_CARD = re.compile(r'<article class="card">')
# A command block on the site, then the output block the page shows for it, in page order.
_SITE_COMMAND = re.compile(r"<pre[^>]*><code>(equity_calculator .*?)</code></pre>", re.DOTALL)
_SITE_OUTPUT = re.compile(r'<pre\s+class="output"[^>]*><code>(.*?)</code></pre>', re.DOTALL)
_PAIRS = (
    "`vc-diligence-questions` reads `vc-partner-meeting`'s question bank, so load both folders.",
    "`vc-prospective-investor-update` reads `vc-current-investor-update`'s metric rules file, so load both folders.",
)
_COPY_EVERY_FOLDER = "cp -r ai-vc-skills/skills/* ~/.claude/skills/"
_LOAD_EVERY_FOLDER = "every folder under `skills/`"
_STILL_TO_COME = "to come"


def _site() -> str:
    return _SITE.read_text(encoding="utf-8")


def _number(word: str) -> int:
    return _NUMBER_WORDS[word.lower()]


def _site_examples() -> list[tuple[str, list[str]]]:
    text = _site()
    commands = [html.unescape(body) for body in _SITE_COMMAND.findall(text)]
    outputs = [html.unescape(body).splitlines() for body in _SITE_OUTPUT.findall(text)]
    assert len(commands) == len(outputs), (len(commands), len(outputs))
    return [
        (" ".join(part.strip().removesuffix("\\").strip() for part in command.splitlines()), shown)
        for command, shown in zip(commands, outputs, strict=True)
    ]


_EXAMPLES = _site_examples()


def test_the_site_has_one_card_per_skill_folder() -> None:
    text = _site()

    assert len(_SITE_CARD.findall(text)) == len(_SKILLS)
    for name in _SKILLS:
        assert text.count(f"<h3><code>{name}</code></h3>") == 1, name


def test_the_site_links_every_skill_from_its_card_and_the_link_list() -> None:
    text = _site()

    for name in _SKILLS:
        assert text.count(f"/blob/main/skills/{name}/SKILL.md") == 2, name


def test_the_site_says_how_many_skills_there_are() -> None:
    match = _SITE_SKILL_COUNT.search(_site())

    assert match is not None
    assert _number(match.group(1)) == len(_SKILLS)


def test_the_site_counts_the_scenarios_as_the_readme_does() -> None:
    site = _SITE_SCENARIO_COUNT.search(_site())
    readme = _README_SCENARIO_COUNT.search(_README.read_text(encoding="utf-8"))

    assert site is not None and readme is not None
    assert _number(site.group(1)) == _number(readme.group(1))


def test_the_site_has_its_two_calculator_examples() -> None:
    assert [command.split()[1] for command, _ in _EXAMPLES] == ["investor", "deal_check"]


@pytest.mark.parametrize(("command", "shown"), _EXAMPLES, ids=[command.split()[1] for command, _ in _EXAMPLES])
async def test_each_site_example_prints_every_line_it_shows(command: str, shown: list[str]) -> None:
    printed = (await run(shlex.split(command)[1:])).splitlines()

    missing = [line for line in shown if line not in printed]
    assert missing == []


def test_the_install_guide_loads_every_folder_and_both_pairs() -> None:
    install = _INSTALL.read_text(encoding="utf-8")
    readme = _README.read_text(encoding="utf-8")

    assert _COPY_EVERY_FOLDER in install
    assert _LOAD_EVERY_FOLDER in install
    for line in _PAIRS:
        assert line in install, line
        assert line in readme, line


def test_the_plugin_descriptions_promise_nothing_still_to_come() -> None:
    plugin = json.loads((_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    descriptions = [plugin["description"], marketplace["metadata"]["description"]]
    descriptions += [entry["description"] for entry in marketplace["plugins"]]

    for description in descriptions:
        assert _STILL_TO_COME not in description, description


def test_every_image_the_site_shows_is_served_from_its_own_folder() -> None:
    """Pages serves docs/ only, so each image the page loads must sit in docs/, both demo recordings included."""
    sources = re.findall(r'<img[^>]*?\ssrc="([^"]+)"', _site(), flags=re.DOTALL)

    assert {"demo-claude.gif", "demo-cli.gif"} <= set(sources)
    for source in sources:
        assert "://" not in source and not source.startswith(("/", "..")), source
        assert (_SITE.parent / source).is_file(), source


def test_the_plugin_and_its_marketplace_entry_carry_the_same_version() -> None:
    plugin = json.loads((_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

    assert marketplace["metadata"]["version"] == plugin["version"]
