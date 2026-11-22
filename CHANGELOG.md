# Changelog

All notable changes to this repository. Dates are UTC.

## Unreleased

### Added

- The repository is now **AI VC skills**, a Claude Code plugin marketplace with one plugin, `ai-vc-skills`
  (`/plugin marketplace add BwL1289/ai-vc-skills`, then `/plugin install ai-vc-skills@ai-vc-skills`). The plugin
  carries every skill in `skills/` and starts the equity calculator's MCP server with `uvx`.
- Skills moved to a top-level `skills/` folder; `template/SKILL.md` starts a new one, and
  `scripts/validate_skills.py` checks them in CI.
- AGENTS.md, CONTRIBUTING.md, SECURITY.md, an install guide per client in `docs/`, issue templates and a CI workflow.
- The `vc-deal-math` skill, in preview: a founder checks their own fundraising ask before a VC does (valuation,
  ownership after the round with SAFEs, notes and the pool counted, effective pre-money, runway, use of funds). It
  runs on the calculator's new `deal_check` scenario, also an MCP tool (`equity_deal_check`), a command and a
  workbook sheet, which returns each stated figure as consistent or a mismatch and flags what a VC is likely to ask.
  Results gain a `months` unit.

### Changed

- The repository was renamed from `opensource-content` to `ai-vc-skills`; GitHub redirects the old address.

## 2026-11-21

### Added

- The equity calculator: seven scenarios (investor, employee, pool, round, dilution, vesting, waterfall) worked as
  exact fractions, as a command, an `.xlsx` workbook, an MCP server and a Python package, with an agent skill (#1).
- The investor sheet of the workbook is live: change the stake or the multiplier and the verdict re-works (#5).

### Changed

- Every public name uses underscores, with a root README and root setup (#2); the 2024 `src/` script was removed
  (#3) and the root settings moved into `pyproject.toml` (#4).

## 2024-10-17

### Added

- `src/equity_equation`, the original script that worked Paul Graham's investor test.
