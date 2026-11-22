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
  A holder group can be given as a share count and the unissued pool as a percent of the fully diluted shares, so
  no one divides by hand. It works the new money as a priced round; a raise on a SAFE goes to `round`. Results gain
  a `months` unit.
- The `vc-positioning` skill, in preview: a founder tightens the messaging and positioning of a raise before going
  out to VCs. It checks the one-liner, narrative, ask and metrics against public frameworks, flags phrases that cost
  credibility, and runs an adversarial review: independent skeptical lenses list the strongest reasons a VC would pass,
  each quoting the founder's own line, and a refute pass drops every objection the founder's material already answers.
  It returns the surviving objections with rewrites, a tightened narrative, a say-and-avoid list and a script for a
  prep session with an existing investor. The ask's figures go to `equity_deal_check`; it invents no traction. Four
  evals are in `evals/vc-positioning/`.
- The `vc-claims-check` skill, in preview: a founder checks every quantitative or verifiable claim in their deck,
  one-pager and narrative before a VC does. Each claim is listed with where it appears and its class (figure, market
  size, customer or partner, team credential, competition, technology claim), checked for evidence the founder can
  show, for agreement across the materials (compared as stated, never converted) and for patterns a VC discounts, and
  returned as supported, needs a source, contradicted or will be discounted, with the fix. Deal terms go to
  `equity_deal_check`, one call per document's version of the ask. A short adversarial review has a skeptic pick the
  claims a partner is likely to check first, and a refute pass keeps an attack only when the founder's material
  grounds it. `vc-positioning` now points to it. Three evals are in `evals/vc-claims-check/`.
- New logo: a chess knight whose head is cut into cap-table slices.
- A one-page website for the skills, served by GitHub Pages from `docs/` at
  [bwl1289.github.io/ai-vc-skills](https://bwl1289.github.io/ai-vc-skills/): install lines, the four skills, real
  calculator output for the two calculator skills and eval excerpts for the two reviews, light and dark themes.

### Changed

- The repository was renamed from `opensource-content` to `ai-vc-skills`; GitHub redirects the old address.
- The knight logo has a little depth: a soft drop shadow, each slice shaded lighter at the top, and a faint
  highlight along the head's top edges. The banners, the site's logo and favicon (which follow the light or dark
  theme), the plugin icon and the social image all use it; shapes and base colours are unchanged.

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
