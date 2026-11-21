# Security

## What runs on your machine

- The skills are Markdown instructions; they run nothing by themselves.
- The MCP server (`equity_calculator_mcp`) runs locally over stdio. It makes no network calls, reads no files, and
  writes a workbook only when it is started with an output folder (the plugin starts it without one).
- The Claude Code plugin starts the server with `uvx`, which downloads the package's dependencies (Pydantic, openpyxl
  and the MCP SDK) from PyPI the first time.

No document, deal term or result leaves your machine through this repository's code. What your AI client sends to
its model provider is governed by that client.

## Reporting a vulnerability

Please report security problems privately through GitHub's
[private vulnerability reporting](https://github.com/BwL1289/ai-vc-skills/security/advisories/new) rather than in a
public issue. Include what you ran, what happened, and what you expected.
