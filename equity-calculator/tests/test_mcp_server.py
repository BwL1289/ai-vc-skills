"""``equity-calculator-mcp``: one tool per scenario, refusals as tool errors, the workbook tool's folder rule, stdio.

No network: most tests drive the server in process through the MCP SDK's memory transport, and one starts the real
server as a child process and talks to it over stdio. The only files written are under pytest's temporary directory.
The whole module is skipped when the ``mcp`` extra is not installed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
import unicodedata
import warnings
from pathlib import Path
from typing import Any

import pytest
from equity_calculator.__main__ import _INPUT_MODELS, run
from equity_calculator.result_range import OUT_OF_RANGE_REASON
from equity_calculator.scenarios import compute
from openpyxl import load_workbook
from tests.support import (
    DILUTION_ROUNDS,
    POOL_EXAMPLE,
    ROUND_EXAMPLE,
    ROUND_NOTE,
    ROUND_SAFES,
    SAFES_PAST_RANGE,
    WATERFALL_A,
    WATERFALL_B,
    WATERFALL_COMMON,
    sliver_round,
)

anyio = pytest.importorskip("anyio")
mcp = pytest.importorskip("mcp")
memory = pytest.importorskip("mcp.shared.memory")
stdio = pytest.importorskip("mcp.client.stdio")
mcp_server = pytest.importorskip("equity_calculator.mcp_server")

_WORKBOOK_TOOL = "equity_workbook"
_STDIO_TIMEOUT_S = 60
_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
# A valid value, unlike the SDK's default, for every setting the SDK's settings class reads from FASTMCP_* variables
# and a .env file (nested fields through "__"); test_the_settings_table_names_every_sdk_setting keeps it complete.
_SDK_SETTINGS = {
    "FASTMCP_DEBUG": "true",
    "FASTMCP_LOG_LEVEL": "DEBUG",
    "FASTMCP_HOST": "0.0.0.0",
    "FASTMCP_PORT": "9999",
    "FASTMCP_MOUNT_PATH": "/other",
    "FASTMCP_SSE_PATH": "/other-sse",
    "FASTMCP_MESSAGE_PATH": "/other-messages/",
    "FASTMCP_STREAMABLE_HTTP_PATH": "/other-mcp",
    "FASTMCP_JSON_RESPONSE": "true",
    "FASTMCP_STATELESS_HTTP": "true",
    "FASTMCP_WARN_ON_DUPLICATE_RESOURCES": "false",
    "FASTMCP_WARN_ON_DUPLICATE_TOOLS": "false",
    "FASTMCP_WARN_ON_DUPLICATE_PROMPTS": "false",
    "FASTMCP_DEPENDENCIES": '["requests"]',
    "FASTMCP_LIFESPAN": "null",
    "FASTMCP_AUTH__ISSUER_URL": "http://0.0.0.0:9/",
    "FASTMCP_AUTH__SERVICE_DOCUMENTATION_URL": "http://0.0.0.0:9/docs",
    "FASTMCP_AUTH__CLIENT_REGISTRATION_OPTIONS__ENABLED": "true",
    "FASTMCP_AUTH__REVOCATION_OPTIONS__ENABLED": "true",
    "FASTMCP_AUTH__REQUIRED_SCOPES": '["read"]',
    "FASTMCP_AUTH__RESOURCE_SERVER_URL": "http://0.0.0.0:9/mcp",
    "FASTMCP_TRANSPORT_SECURITY__ENABLE_DNS_REBINDING_PROTECTION": "false",
    "FASTMCP_TRANSPORT_SECURITY__ALLOWED_HOSTS": '["0.0.0.0:*"]',
    "FASTMCP_TRANSPORT_SECURITY__ALLOWED_ORIGINS": '["http://0.0.0.0:9"]',
}
# The settings whose value the SDK parses as JSON before the server's own arguments win, so a value that is not JSON
# stops start-up. An empty FASTMCP_DEPENDENCIES stops it too, while the two nested lists treat an empty value as unset.
# Every other setting ignores any value, empty or not JSON.
_JSON_PARSED = (
    "FASTMCP_DEPENDENCIES",
    "FASTMCP_TRANSPORT_SECURITY__ALLOWED_HOSTS",
    "FASTMCP_TRANSPORT_SECURITY__ALLOWED_ORIGINS",
)
_NOT_JSON = "requests"
# The one setting an empty value stops at start-up: the SDK parses even an empty value of it as JSON.
_EMPTY_STOPS = "FASTMCP_DEPENDENCIES"
# The names that hold a whole object rather than one value; the SDK reads them too.
_OBJECT_SETTINGS = (
    "FASTMCP_AUTH",
    "FASTMCP_AUTH__CLIENT_REGISTRATION_OPTIONS",
    "FASTMCP_AUTH__REVOCATION_OPTIONS",
    "FASTMCP_TRANSPORT_SECURITY",
)
# Names the SDK has no setting for, flat and nested.
_UNKNOWN_SETTINGS = ("FASTMCP_NOT_A_SETTING", "FASTMCP_AUTH__NOT_A_FIELD")
# File mode for a .env file that nobody but root may read.
_NO_PERMISSIONS = 0o000
# One name per kind of control character: line breaks, a tab, a terminal colour escape, delete, a bell, a C1 control
# (U+0085 NEXT LINE) and NUL.
_CONTROL_NAMES = (
    "new\nline.xlsx",
    "tab\t.xlsx",
    "cr\r.xlsx",
    "esc\x1b[31m.xlsx",
    "del\x7f.xlsx",
    "bell\x07.xlsx",
    "c1\x85.xlsx",
    "nul\x00.xlsx",
)
# A format character (U+202E RIGHT-TO-LEFT OVERRIDE, which shows "a\u202eslx.xlsx" as "axslx.xls") and a lone surrogate
# (half of a UTF-16 pair, which no file system can store on its own).
_FORMAT_AND_SURROGATE_NAMES = ("a\u202eslx.xlsx", "x\ud800.xlsx")
_REFUSED_CATEGORIES = frozenset({"Cc", "Cf", "Cs"})
_REFUSED_KINDS = "control, format or surrogate character"
_FIRST = 0

# One valid input per scenario, without the scenario tag (each scenario's own tool fills it in).
_SAMPLES: dict[str, dict[str, object]] = {
    "investor": {"equity_percent": "7", "outcome_multiplier": "1.10"},
    "employee": {"gain_percent": "20", "annual_cost": "60000", "valuation": "2000000", "margin_percent": "50"},
    "pool": POOL_EXAMPLE,
    "round": {**ROUND_EXAMPLE, "instruments": [*ROUND_SAFES, ROUND_NOTE]},
    "dilution": {"holder_percent": "50", "rounds": DILUTION_ROUNDS},
    "vesting": {"grant_shares": 48_000, "month": 30, "strike_price": "0.50", "common_price": "2"},
    "waterfall": {"exit_amount": "50000000", "common_shares": WATERFALL_COMMON, "classes": [WATERFALL_A, WATERFALL_B]},
}
# $1M in at a $1M pre-money with a 25% pre-money pool target and a $250k SAFE at a 50% discount: the pooled price is
# exactly zero, so the round has no price (the same case as test_round_pool.py).
_NO_PRICE_ROUND: dict[str, object] = {
    **ROUND_EXAMPLE,
    "pre_money": "1000000",
    "investment": "1000000",
    "target_pool_percent": "25",
    "pool_timing": "pre_money",
    "instruments": [{"kind": "safe", "purchase_amount": "250000", "discount_percent": "50"}],
}
_NO_ANSWER = "no answer for these inputs"
_TAGGED_INVESTOR = {"scenario": "investor", **_SAMPLES["investor"]}


def _expected(scenario: str, sample: dict[str, object]) -> str:
    return compute(_INPUT_MODELS[scenario].model_validate(sample)).model_dump_json(indent=2)


def _text(result: Any) -> str:
    assert len(result.content) == 1
    text = result.content[0].text
    assert isinstance(text, str)
    return text


async def _tools(server: Any) -> list[Any]:
    async with memory.create_connected_server_and_client_session(server._mcp_server) as session:
        tools = (await session.list_tools()).tools
    assert isinstance(tools, list)
    return tools


async def _call(server: Any, name: str, arguments: dict[str, object]) -> Any:
    async with memory.create_connected_server_and_client_session(server._mcp_server) as session:
        return await session.call_tool(name, arguments)


async def _write(folder: Path, file_name: str, inputs: dict[str, object] = _TAGGED_INVESTOR) -> Any:
    return await _call(mcp_server.build_server(folder), _WORKBOOK_TOOL, {"inputs": inputs, "file_name": file_name})


async def test_one_read_only_tool_per_scenario_and_no_workbook_tool_without_a_folder() -> None:
    tools = await _tools(mcp_server.build_server())

    assert sorted(tool.name for tool in tools) == sorted(f"equity_{scenario}" for scenario in _INPUT_MODELS)
    assert len(tools) == len(_SAMPLES) == 7
    for tool in tools:
        assert tool.annotations.readOnlyHint is True
        assert tool.annotations.openWorldHint is False
        assert tool.inputSchema["required"] == ["inputs"]


@pytest.mark.parametrize("scenario", sorted(_SAMPLES))
async def test_each_tool_returns_the_scenario_result_as_json(scenario: str) -> None:
    result = await _call(mcp_server.build_server(), f"equity_{scenario}", {"inputs": _SAMPLES[scenario]})

    assert result.isError is False
    assert _text(result) == _expected(scenario, _SAMPLES[scenario])
    assert json.loads(_text(result))["scenario"] == scenario


async def test_the_investor_tool_answers_what_the_cli_prints_with_json() -> None:
    printed = await run(["investor", "--equity-percent", "7", "--outcome-multiplier", "1.10", "--json"])
    result = await _call(mcp_server.build_server(), "equity_investor", {"inputs": _SAMPLES["investor"]})

    assert _text(result) == printed.rstrip("\n")


async def test_a_tool_takes_its_own_scenario_tag_and_refuses_another() -> None:
    server = mcp_server.build_server()

    tagged = await _call(server, "equity_investor", {"inputs": _TAGGED_INVESTOR})
    wrong = await _call(server, "equity_investor", {"inputs": {**_SAMPLES["investor"], "scenario": "pool"}})

    assert tagged.isError is False
    assert _text(tagged) == _expected("investor", _SAMPLES["investor"])
    assert wrong.isError is True


@pytest.mark.parametrize(
    "inputs",
    [
        {"equity_percent": "7"},
        {**_SAMPLES["investor"], "unknown_field": "1"},
        {**_SAMPLES["investor"], "equity_percent": "-7"},
        {**_SAMPLES["investor"], "equity_percent": "1e4400"},
        {**_SAMPLES["investor"], "equity_percent": "seven"},
    ],
    ids=["missing", "unknown", "negative", "huge", "not-a-number"],
)
async def test_an_invalid_input_is_a_tool_error(inputs: dict[str, object]) -> None:
    result = await _call(mcp_server.build_server(), "equity_investor", {"inputs": inputs})

    assert result.isError is True


async def test_a_round_with_no_price_is_refused_with_the_reason() -> None:
    result = await _call(mcp_server.build_server(), "equity_round", {"inputs": _NO_PRICE_ROUND})

    assert result.isError is True
    assert _NO_ANSWER in _text(result)


async def test_the_workbook_tool_is_listed_with_its_folder_and_writes_one_sheet(tmp_path: Path) -> None:
    folder = tmp_path / "out"
    tools = {tool.name: tool for tool in await _tools(mcp_server.build_server(folder))}

    workbook = tools[_WORKBOOK_TOOL]
    assert len(tools) == len(_SAMPLES) + 1
    assert str(folder.resolve()) in workbook.description
    assert "written ONLY inside that folder" in workbook.description
    assert "temporary folder" in workbook.description
    assert "refused" in workbook.description
    assert workbook.annotations.readOnlyHint is False
    assert workbook.annotations.destructiveHint is False
    assert sorted(workbook.inputSchema["required"]) == ["file_name", "inputs"]

    result = await _write(folder, "round.xlsx", {"scenario": "round", **_SAMPLES["round"]})

    assert result.isError is False
    assert str(folder.resolve() / "round.xlsx") in _text(result)
    assert [path.name for path in folder.iterdir()] == ["round.xlsx"]
    assert len(load_workbook(folder / "round.xlsx").worksheets) == 1


async def test_the_workbook_tool_needs_the_scenario_tag(tmp_path: Path) -> None:
    folder = tmp_path / "out"

    result = await _write(folder, "a.xlsx", _SAMPLES["investor"])

    assert result.isError is True
    assert list(folder.iterdir()) == []


@pytest.mark.parametrize(
    "file_name",
    [
        "../a.xlsx",
        "sub/a.xlsx",
        "sub\\a.xlsx",
        "a.txt",
        "a.xlsx.txt",
        "",
        "..",
        ".xlsx",
        ".a.xlsx",
        "x" * 251 + ".xlsx",
    ],
)
async def test_the_workbook_tool_refuses_a_name_that_is_not_a_plain_file_in_the_folder(
    tmp_path: Path, file_name: str
) -> None:
    folder = tmp_path / "out"

    result = await _write(folder, file_name)

    assert result.isError is True
    assert list(folder.iterdir()) == []
    assert sorted(path.name for path in tmp_path.iterdir()) == ["out"]


@pytest.mark.parametrize("file_name", _CONTROL_NAMES + _FORMAT_AND_SURROGATE_NAMES)
async def test_the_workbook_tool_refuses_a_name_with_a_control_format_or_surrogate_character(
    tmp_path: Path, file_name: str
) -> None:
    folder = tmp_path / "out"

    result = await _write(folder, file_name)

    assert result.isError is True
    assert _REFUSED_KINDS in _text(result)
    assert not any(unicodedata.category(character) in _REFUSED_CATEGORIES for character in _text(result))
    assert list(folder.iterdir()) == []
    assert sorted(path.name for path in tmp_path.iterdir()) == ["out"]


async def test_the_workbook_tool_writes_a_name_with_printable_characters_beyond_ascii(tmp_path: Path) -> None:
    folder = tmp_path / "out"

    result = await _write(folder, "café ±.xlsx")

    assert result.isError is False
    assert [path.name for path in folder.iterdir()] == ["café ±.xlsx"]


async def test_the_workbook_tool_refuses_an_absolute_path(tmp_path: Path) -> None:
    folder = tmp_path / "out"
    target = tmp_path / "elsewhere.xlsx"

    result = await _write(folder, str(target))

    assert result.isError is True
    assert not target.exists()
    assert list(folder.iterdir()) == []


async def test_the_workbook_tool_never_overwrites_a_file(tmp_path: Path) -> None:
    folder = tmp_path / "out"
    first = await _write(folder, "a.xlsx")
    before = (folder / "a.xlsx").read_bytes()

    second = await _write(folder, "a.xlsx", {"scenario": "pool", **POOL_EXAMPLE})

    assert first.isError is False
    assert second.isError is True
    assert "already exists" in _text(second)
    assert (folder / "a.xlsx").read_bytes() == before


async def test_the_workbook_tool_never_follows_a_link_out_of_the_folder(tmp_path: Path) -> None:
    folder = tmp_path / "out"
    folder.mkdir()
    outside = tmp_path / "outside.xlsx"
    outside.write_bytes(b"keep")
    (folder / "link.xlsx").symlink_to(outside)
    (folder / "dangling.xlsx").symlink_to(tmp_path / "nowhere.xlsx")

    to_file = await _write(folder, "link.xlsx")
    to_nothing = await _write(folder, "dangling.xlsx")

    assert to_file.isError is True
    assert to_nothing.isError is True
    assert outside.read_bytes() == b"keep"
    assert not (tmp_path / "nowhere.xlsx").exists()


async def test_the_workbook_tool_writes_nothing_when_the_scenario_has_no_answer(tmp_path: Path) -> None:
    folder = tmp_path / "out"

    result = await _write(folder, "a.xlsx", {"scenario": "round", **_NO_PRICE_ROUND})

    assert result.isError is True
    assert _NO_ANSWER in _text(result)
    assert list(folder.iterdir()) == []


async def test_the_workbook_tool_writes_nothing_when_the_answer_is_too_large_for_a_workbook(tmp_path: Path) -> None:
    folder = tmp_path / "out"

    result = await _write(folder, "a.xlsx", {"scenario": "round", **sliver_round(SAFES_PAST_RANGE[_FIRST])})

    assert result.isError is True
    assert _NO_ANSWER in _text(result)
    assert OUT_OF_RANGE_REASON in _text(result)
    assert list(folder.iterdir()) == []
    assert sorted(path.name for path in tmp_path.iterdir()) == ["out"]


def test_an_output_folder_that_is_a_file_stops_the_server(tmp_path: Path) -> None:
    not_a_folder = tmp_path / "file"
    not_a_folder.write_text("x")

    with pytest.raises(SystemExit):
        mcp_server.build_server(not_a_folder)


async def test_one_round_trip_over_stdio_with_the_real_server(tmp_path: Path) -> None:
    folder = tmp_path / "out"
    params = mcp.StdioServerParameters(
        command=sys.executable,
        args=["-m", "equity_calculator.mcp_server", "--output-dir", str(folder)],
        env=dict(os.environ),
    )

    with anyio.fail_after(_STDIO_TIMEOUT_S):
        async with stdio.stdio_client(params) as (read, write), mcp.ClientSession(read, write) as session:
            await session.initialize()
            names = sorted(tool.name for tool in (await session.list_tools()).tools)
            answer = await session.call_tool("equity_investor", {"inputs": _SAMPLES["investor"]})
            written = await session.call_tool(_WORKBOOK_TOOL, {"inputs": _TAGGED_INVESTOR, "file_name": "a.xlsx"})

    assert names == sorted([*(f"equity_{scenario}" for scenario in _INPUT_MODELS), _WORKBOOK_TOOL])
    assert answer.isError is False
    assert _text(answer) == _expected("investor", _SAMPLES["investor"])
    assert written.isError is False
    assert len(load_workbook(folder / "a.xlsx").worksheets) == 1


def _settings(server: Any) -> dict[str, Any]:
    settings = server.settings.model_dump(exclude={"lifespan"})
    assert isinstance(settings, dict)
    return settings


def _child_env(**extra: str) -> dict[str, str]:
    """The test's environment for a child Python, without warning filters or FASTMCP_* values from outside."""
    env = {
        key: value for key, value in os.environ.items() if key != "PYTHONWARNINGS" and not key.startswith("FASTMCP_")
    }
    env.update(extra)

    return env


def test_a_dotenv_file_and_fastmcp_variables_change_no_setting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clean_folder = tmp_path / "clean"
    clean_folder.mkdir()
    monkeypatch.chdir(clean_folder)
    clean = _settings(mcp_server.build_server())
    loaded_folder = tmp_path / "loaded"
    loaded_folder.mkdir()
    (loaded_folder / ".env").write_text("".join(f"{key}={value}\n" for key, value in _SDK_SETTINGS.items()))
    monkeypatch.chdir(loaded_folder)
    from_dotenv = _settings(mcp_server.build_server())
    for key, value in _SDK_SETTINGS.items():
        monkeypatch.setenv(key, value)
    from_both = _settings(mcp_server.build_server())

    assert clean["log_level"] == "WARNING"
    assert from_dotenv == clean
    assert from_both == clean


def test_the_settings_table_names_every_sdk_setting() -> None:
    from mcp.server.auth.settings import AuthSettings
    from mcp.server.fastmcp.server import Settings
    from mcp.server.transport_security import TransportSecuritySettings

    names = [key.removeprefix("FASTMCP_").lower().split("__") for key in _SDK_SETTINGS]

    assert {name[0] for name in names} == set(Settings.model_fields)
    for outer, model in (("auth", AuthSettings), ("transport_security", TransportSecuritySettings)):
        assert {name[1] for name in names if name[0] == outer} == set(model.model_fields)


def _write_settings(where: str, folder: Path, values: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(folder)
    if where == "dotenv":
        (folder / ".env").write_text("".join(f"{key}={value}\n" for key, value in values.items()))
    else:
        for key, value in values.items():
            monkeypatch.setenv(key, value)


@pytest.mark.parametrize("where", ["dotenv", "variable"])
@pytest.mark.parametrize("key", sorted({*_SDK_SETTINGS, *_OBJECT_SETTINGS} - set(_JSON_PARSED)))
def test_a_value_that_is_not_json_in_any_other_setting_changes_nothing(
    key: str, where: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    clean = _settings(mcp_server.build_server())
    folder = tmp_path / "loaded"
    folder.mkdir()
    _write_settings(where, folder, {key: _NOT_JSON}, monkeypatch)

    assert _settings(mcp_server.build_server()) == clean


@pytest.mark.parametrize("where", ["dotenv", "variable"])
@pytest.mark.parametrize("key", _JSON_PARSED)
def test_a_value_that_is_not_json_in_a_json_parsed_setting_stops_start_up(
    key: str, where: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pydantic_settings import SettingsError

    _write_settings(where, tmp_path, {key: _NOT_JSON}, monkeypatch)
    field = key.removeprefix("FASTMCP_").lower().split("__")[0]

    with pytest.raises(SettingsError, match=field):
        mcp_server.build_server()


@pytest.mark.parametrize("where", ["dotenv", "variable"])
@pytest.mark.parametrize("key", [spelling for key in _JSON_PARSED for spelling in (key.lower(), key.title())])
def test_the_sdk_reads_a_json_parsed_setting_in_any_letter_case(
    key: str, where: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pydantic_settings import SettingsError

    _write_settings(where, tmp_path, {key: _NOT_JSON}, monkeypatch)
    field = key.lower().removeprefix("fastmcp_").split("__")[0]

    with pytest.raises(SettingsError, match=field):
        mcp_server.build_server()


@pytest.mark.parametrize("where", ["dotenv", "variable"])
def test_an_empty_dependencies_value_stops_start_up(
    where: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pydantic_settings import SettingsError

    _write_settings(where, tmp_path, {_EMPTY_STOPS: ""}, monkeypatch)

    with pytest.raises(SettingsError, match="dependencies"):
        mcp_server.build_server()


@pytest.mark.parametrize("where", ["dotenv", "variable"])
@pytest.mark.parametrize("key", sorted({*_SDK_SETTINGS, *_OBJECT_SETTINGS} - {_EMPTY_STOPS}))
def test_an_empty_value_in_any_other_setting_changes_nothing(
    key: str, where: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    clean = _settings(mcp_server.build_server())
    folder = tmp_path / "loaded"
    folder.mkdir()
    _write_settings(where, folder, {key: ""}, monkeypatch)

    assert _settings(mcp_server.build_server()) == clean


@pytest.mark.parametrize("where", ["dotenv", "variable"])
@pytest.mark.parametrize("value", [_NOT_JSON, ""])
@pytest.mark.parametrize("key", _UNKNOWN_SETTINGS)
def test_a_name_the_sdk_has_no_setting_for_changes_nothing(
    key: str, value: str, where: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    clean = _settings(mcp_server.build_server())
    folder = tmp_path / "loaded"
    folder.mkdir()
    _write_settings(where, folder, {key: value}, monkeypatch)

    assert _settings(mcp_server.build_server()) == clean


def test_a_dotenv_file_the_server_may_not_read_stops_start_up(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("FASTMCP_PORT=9999\n")
    dotenv.chmod(_NO_PERMISSIONS)
    monkeypatch.chdir(tmp_path)
    if os.access(dotenv, os.R_OK):
        pytest.skip("this user can read a file with no read permission (root), so the case cannot be made")

    with pytest.raises(PermissionError):
        mcp_server.build_server()


def test_a_dotenv_file_that_is_not_text_in_the_system_encoding_stops_start_up(tmp_path: Path) -> None:
    (tmp_path / ".env").write_bytes(b"FASTMCP_PORT=\xff\xfe\n")

    finished = subprocess.run(
        [sys.executable, "-c", "from equity_calculator.mcp_server import build_server; build_server()"],
        cwd=tmp_path,
        env=_child_env(PYTHONUTF8="1"),
        capture_output=True,
        text=True,
        timeout=_STDIO_TIMEOUT_S,
        check=False,
    )

    assert finished.returncode != 0
    assert "UnicodeDecodeError" in finished.stderr


def test_a_leading_tilde_in_the_output_folder_is_expanded_from_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(tmp_path)

    tools = {tool.name: tool for tool in anyio.run(_tools, mcp_server.build_server(Path("~/books")))}

    assert (home / "books").is_dir()
    assert not (tmp_path / "~").exists()
    assert str((home / "books").resolve()) in tools[_WORKBOOK_TOOL].description


def test_making_the_server_silences_only_the_sdk_settings_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The SDK warns once per process, so a stand-in raises both warnings on every build.
    real_server = mcp_server.FastMCP
    settings_warning = mcp_server._settings_warning()

    def warning_server(*args: Any, **kwargs: Any) -> Any:
        warnings.warn(settings_warning("Field 'lifespan' has an incomplete definition: a stand-in"), stacklevel=2)
        warnings.warn("another warning", UserWarning, stacklevel=2)
        return real_server(*args, **kwargs)

    monkeypatch.setattr(mcp_server, "FastMCP", warning_server)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        filters_before = list(warnings.filters)
        mcp_server.build_server(tmp_path / "out")
        filters_after = list(warnings.filters)

    assert [str(warning.message) for warning in caught] == ["another warning"]
    assert filters_after == filters_before


def test_starting_the_real_server_prints_nothing_to_stderr(tmp_path: Path) -> None:
    finished = subprocess.run(
        [sys.executable, "-m", "equity_calculator.mcp_server", "--output-dir", str(tmp_path / "out")],
        cwd=tmp_path,
        env=_child_env(),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=_STDIO_TIMEOUT_S,
        check=False,
    )

    assert finished.returncode == 0
    assert finished.stderr == ""
    assert finished.stdout == ""


def test_without_the_mcp_sdk_the_server_names_the_pinned_install_command() -> None:
    pin = tomllib.loads(_PYPROJECT.read_text())["project"]["optional-dependencies"]["mcp"]
    hide_the_sdk = "import sys; sys.modules['mcp'] = None; import equity_calculator.mcp_server"

    finished = subprocess.run(
        [sys.executable, "-c", hide_the_sdk],
        env=_child_env(),
        capture_output=True,
        text=True,
        timeout=_STDIO_TIMEOUT_S,
        check=False,
    )

    assert pin == ["mcp==1.28.1"]
    assert finished.returncode == 1
    assert finished.stderr.strip() == "equity-calculator-mcp needs the MCP SDK: pip install 'mcp==1.28.1'"
