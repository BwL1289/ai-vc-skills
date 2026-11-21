"""The README's examples run as written: each ``equity-calculator`` command, every line it shows, and the Python one.

A fenced block whose first line is an ``equity-calculator`` command is run in process (lines ending `` \\`` join the
next), and every line the block shows after the command must appear in the printed report. The usage synopsis, which
has ``(``, ``[`` and ``|`` in it, is not a command and is skipped. The ``python`` block is run as written and its one
printed line must equal the comment on its ``print`` line.
"""

from __future__ import annotations

import contextlib
import io
import re
import shlex
from pathlib import Path

import pytest
from equity_calculator.__main__ import run

_README = Path(__file__).resolve().parents[1] / "README.md"
_FENCE = re.compile(r"^```([a-z]*)\n(.*?)^```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity-calculator "
_SYNOPSIS = ("(", "[", "|")
# The quick start, the investor and employee worked examples, and the round example.
_MIN_COMMANDS = 4


def _blocks(language: str) -> list[str]:
    return [body for tag, body in _FENCE.findall(_README.read_text(encoding="utf-8")) if tag == language]


def _examples() -> list[tuple[str, list[str]]]:
    examples: list[tuple[str, list[str]]] = []
    for body in _blocks(""):
        lines = body.splitlines()
        if not lines or not lines[0].startswith(_PROGRAM):
            continue
        command = lines.pop(0)
        while command.endswith(" \\"):
            command = command[:-2] + " " + lines.pop(0).strip()
        if any(mark in command for mark in _SYNOPSIS):
            continue
        examples.append((command, lines))
    return examples


_EXAMPLES = _examples()


def test_the_readme_has_its_command_examples() -> None:
    assert len(_EXAMPLES) >= _MIN_COMMANDS
    assert any(shown for _, shown in _EXAMPLES)


@pytest.mark.parametrize(("command", "shown"), _EXAMPLES, ids=[command.split()[1] for command, _ in _EXAMPLES])
async def test_each_readme_command_prints_every_line_it_shows(command: str, shown: list[str]) -> None:
    printed = (await run(shlex.split(command)[1:])).splitlines()

    missing = [line for line in shown if line not in printed]
    assert missing == []


def test_the_readme_python_example_prints_what_its_comment_says() -> None:
    (source,) = _blocks("python")
    (expected,) = (line.split("# ", 1)[1] for line in source.splitlines() if line.startswith("print("))
    captured = io.StringIO()

    with contextlib.redirect_stdout(captured):
        exec(compile(source, str(_README), "exec"), {"__name__": "readme_example"})

    assert captured.getvalue() == expected + "\n"
