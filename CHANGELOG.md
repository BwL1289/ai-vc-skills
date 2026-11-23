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
- The `vc-deck-review` skill, in preview: a founder reviews their own pitch deck the way a partner reads it. Each
  slide is mapped to ten dimensions (problem, solution, why now, market, product, traction, business model,
  competition, team, the ask and use of funds), each marked present, missing or contradicted from the deck's own
  lines with one fix; first- and last-slide rules; competition at four levels, platform risk and doing nothing
  included. Claims go through the vc-claims-check steps and the ask to `equity_deal_check` (a SAFE raise to
  `equity_round`). An adversarial review turns the surviving objections into a ranked fix list, and the answer says
  which kind of investor the story fits by stage and type. No score and no named firms. `vc-positioning` now points to
  it. Four evals are in `evals/vc-deck-review/`.
- The `vc-partner-meeting` skill, in preview: a founder rehearses a VC partner meeting. It picks question lenses by
  stage (pre-seed, seed, Series A, later) and by the partner's background (operator, finance, product, network, sector
  thesis), frameworks and never named people or firms, and runs an adversarial review: the lenses attack the founder's
  own lines, and a refute pass moves every question the material already answers to a quick-rehearsal list. It drills
  the questions that remain, live or in one message, preps what a partner checks around the meeting (who else is in the
  round, insiders, who has passed, references, no raise), and debriefs each weak answer with a stronger one built only
  from the founder's material, plus what a yes would need. It moderates and never plays an investor: no pass or invest
  verdict and no score. The ask's figures go to the calculator (`equity_deal_check`, or `equity_round` for a SAFE or
  note); runway with no raise is quoted, not computed. A question bank by category sits in
  `skills/vc-partner-meeting/references/`. `vc-positioning` now hands off to the new skill. Four evals are in
  `evals/vc-partner-meeting/`.
- The `vc-taste-check` skill, in preview: a founder lists their key product, brand and scope decisions, including what
  they said no to and why. Each decision is checked for clarity, usefulness and trust and flagged when it reads as
  generic, AI-sounding, copied or taste-washed (polish over generic work). The same two-stage adversarial review as
  `vc-positioning`, with lenses for scope discipline, distinctiveness, coherence of product, brand and story, customer
  trust, and timing and angle, keeps only objections the founder's material does not answer. Surviving decisions become
  why-we-built-it-this-way lines, with which to show in the deck (at most three) and which to keep for the meeting. It
  invents no decisions, scores no taste and calls no calculator tool. `vc-positioning` now points to it. Four evals are
  in `evals/vc-taste-check/`.
- The calculator's `runway_plan` scenario, also an MCP tool (`equity_runway_plan`), a command and a workbook sheet:
  how long each raise lasts on a founder's phased plan, a downside and a lean case, with a no-raise row (and its
  stated runway checked), milestones with time to raise the next round, the smallest raise per milestone and landing
  month, and raises that land later. Cash only; the use-of-funds check moved to a helper both scenarios share.
- The `vc-round-sizing` skill, in preview: a founder sizes their own raise on their own plan. One `equity_runway_plan`
  call works how long each amount lasts on plan, in a downside and with no raise, which milestone month its cash reaches
  with time to raise the next round, the smallest raise that gets there, and raise-now against wait side by side;
  ownership per option comes from `equity_deal_check`, `equity_round` and `equity_dilution`. A skeptic attacks the round
  story and a refute pass keeps only what the founder's material grounds. Benchmarks reach the answer only through the
  calculator's own assumption rows. It invents no burn, growth or valuation and gives no recommendation.
  `vc-positioning` now points to it. Four evals are in `evals/vc-round-sizing/`.
- The `vc-term-sheet-review` skill, in preview: a founder reads a term sheet they were offered before the call with
  their lawyer. Each term is quoted, explained in plain words and marked against one cited baseline, Y Combinator's
  standard and clean Series A term sheet, as Matches, Differs, Not in the baseline or Missing, with its source. The
  round runs on `equity_deal_check` and `equity_pool` (the pool's timing and the whole share counts), the exits on
  `equity_waterfall` at values the sheet, the tool or the founder gives, low ones included, beside a 1x
  non-participating baseline when the preference differs; a later round goes to `equity_dilution` and founder vesting
  to `equity_vesting` on request. Terms no tool models (cumulative dividends, anti-dilution, redemption, pay-to-play,
  warrants) are quoted as not modelled. Lenses for the next round's lead, an acquirer, the team and control attack
  the sheet, a refute pass drops what the sheet answers, and the survivors become questions for the lawyer. It never
  says whether to sign and quotes no survey percentages. `vc-positioning`, `vc-deck-review` and `vc-deal-math` now
  point to it. Five evals are in `evals/vc-term-sheet-review/`.

### Changed

- The repository was renamed from `opensource-content` to `ai-vc-skills`; GitHub redirects the old address.
- The knight logo has a little depth: a soft drop shadow, each slice shaded lighter at the top, and a faint
  highlight along the head's top edges. The banners, the site's logo and favicon (which follow the light or dark
  theme), the plugin icon and the social image all use it; shapes and base colours are unchanged.
- The seven `vc-positioning` and `vc-claims-check` evals were run in live Claude Code sessions (2.1.330, 2026-11-22).
  Each file keeps its expected answer and adds a trimmed excerpt of the recorded answer with a verdict against its pass
  sentence: two passed, four passed in part and one failed (Pass: every clause met; Partial: exactly one missed or met
  only in part; Fail: two or more missed). The `vc-deal-math` evals now say they have not been run live.
- Skill fixes from those runs. `vc-positioning` now owns "check our story and our ask" (a run had routed it to
  `vc-deal-math`), runs its lenses and refute passes as subagents however short the material, makes one calculator call
  per version of the ask (two for a valuation with no label) and keeps the tool's values as printed, and, asked to play
  a named investor, offers the public frameworks and the lenses together with the prep-session credit. `vc-deal-math`
  says to use `vc-positioning` for the story and the ask together, computes nothing outside the calculator's tools and
  runs no what-if the founder did not ask for. In `vc-claims-check`, the skeptic no longer judges whether the material
  answers an attack (the refute pass does), and the "AI-powered" pattern applies when nothing says what the model does.

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
