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
  [bwl1289.github.io/ai-vc-skills](https://bwl1289.github.io/ai-vc-skills/): install lines, a card per skill, real
  calculator output for the two calculator skills and eval excerpts for two of the reviews, light and dark themes.
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
  note). A question bank by category sits in
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
- The `vc-diligence-questions` skill, in preview: a founder prepares for a fund's due diligence after the first
  meeting. One lens per area (team, market, product, traction and metrics, financials and cap table, legal) attacks the
  founder's own lines, and a refute pass drops every question the material or a document on the founder's list already
  answers. The questions that remain are ranked in three tiers (stops the process, slows it, minor), each with a draft
  answer built only from the founder's material and its gaps as bracketed asks. An area prep list and a data-room
  checklist scaled to the stage follow, each document marked Contradicted, Missing or Ready. The questions come from
  `vc-partner-meeting`'s question bank, read in place and never copied (a test ties the two); the skill's own legal and
  cap-table questions and the checklist sit in `skills/vc-diligence-questions/references/data-room.md`. The cap table
  goes to `equity_deal_check` (`equity_round` for a SAFE or note raise), runway with no raise or on a SAFE or note
  raise to `equity_runway_plan`, and the cap table's own sums are quoted, not computed. No score, no investor voice, no
  legal opinion, and no invented or backdated document. `vc-positioning` and `vc-partner-meeting` now point to it. Five
  evals are in `evals/vc-diligence-questions/`.
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
- The `vc-current-investor-update` skill, in preview: a founder drafts or reviews the monthly or quarterly update to
  their current investors in one fixed shape (summary, the same metrics with the same definitions, highlights,
  lowlights, asks, cash and runway, next period, definitions). Every metric and every promise in the last update is tied
  out as stated with fixed status words (Same, Restated, Different form, Changed definition, Dropped, New), never
  recomputed; the runway claim goes to `equity_runway_plan` with no raise and no milestone, and a claim stated as a
  floor ("30+ months") is judged by the printed runway rather than the tool's two-sided verdict. A reader pass has four
  lenses (spin, missing bad news, definitions, tie-out) attack the draft (in review mode, the founder's draft as given)
  and a refute pass drop what the founder's own material answers; the rest becomes a ranked fix list that revises the
  draft. It keeps every lowlight the founder gives and writes no version for people who are not yet investors.
  `vc-positioning` now points to it. Five evals are in `evals/vc-current-investor-update/`.
- The calculator's `metrics_check` scenario, also an MCP tool (`equity_metrics_check`), a command and a workbook
  sheet: a founder's ARR, net and gross revenue retention, churn (logo, gross and net revenue), CAC, CAC payback and
  burn multiple worked exactly from their parts over one period, each figure the document states returned as
  consistent or a mismatch, with flags naming the likely cause (a run-rate called ARR, new customers in net
  retention, payback on revenue rather than gross margin, a multiple on new rather than net new ARR) and three
  benchmark questions. Its definitions and benchmarks quote a16z, Bessemer, David Sacks and David Skok.
- The `vc-metrics-readiness` skill, in preview: a founder checks their traction metrics before a VC does. Each metric
  in the deck, model and investor update is listed word for word with where it appears, its definition named (ARR or
  a run-rate, gross or net revenue retention, logo or revenue churn, blended or paid CAC, CAC payback on gross margin,
  a burn multiple on net new ARR) and its agreement across the documents checked as stated. Every ratio comes from
  `equity_metrics_check`, one call per document's version of the figures; growth rates and LTV are quoted, not
  computed. Five lenses make the definitional attacks a partner makes, a refute pass drops what the founder's material
  answers, and the survivors become a ranked fix list, with the calculator's mismatches first. It lists which metrics
  a fund at the founder's stage usually expects, never what values, and gives no score and no ready-or-not verdict.
  `vc-positioning` now points to it. Five evals are in `evals/vc-metrics-readiness/`.
- The `vc-investor-memo` skill, in preview: a founder drafts, ahead of time, the internal investment memo their
  champion partner is likely to write for the partnership, in ten fixed sections, in the third person and with no
  recommendation. The round's figures go to `equity_deal_check` (or `equity_round` and `equity_runway_plan` for a SAFE
  or note); the outcome case shows what the round's class is paid at the founder's own exit values (`equity_pool` for
  whole share counts, one `equity_waterfall` call per exit) and its stake after the founder's assumed later rounds
  (`equity_dilution`), labelled apart, with no fund size and no fund math. A dissent pass (five lenses, then a refute
  pass with the founder's material) turns what survives into a ranked fix list, and a risk the founder cannot fix goes
  into the memo's Top risks. `vc-positioning` now points to it. Six evals are in `evals/vc-investor-memo/`.
- The calculator's `market_sizing` scenario, also an MCP tool (`equity_market_sizing`), a command and a workbook
  sheet: a founder's market built bottom-up from their own segments (customers, price and the months it covers,
  units, take rate, serviceable share and the customers to win), giving TAM, SAM and SOM per segment and in total,
  the deck's stated figures returned as consistent or a mismatch, top-down figures as a cross-check only, and
  sensitivity rows with the exact value at which SOM reaches the plan's target. Flags name what a VC is likely to
  ask (a price period left out and read as yearly, double counting, SAM equal to TAM, a SOM given only as a percent
  or below the target). A new `count` unit prints customer counts. It quotes Y Combinator's "How to Pitch Your Company" and its seed guide's glossary.
- The `vc-market-sizing` skill, in preview: a founder builds a market size bottom-up from their own evidence. It asks
  who buys, how many there are, what each pays, which of them the product can serve today and how many the founder
  plans to win by when, records each assumption with the founder's source and kind (own data, named third party or
  estimate), and works TAM, SAM and SOM per segment with `equity_market_sizing`, which also checks the deck's stated
  figures, sets any top-down figure beside it as a cross-check, and reruns it on the founder's own low and high values
  (for a fee or price the segments share, also for the whole company); the shakiest assumption is the row of the
  weakest source kind whose range moves the SOM most, or none when that kind has no range. Three lenses (inflation, a
  SOM with no path, double counting) attack the market story, a refute pass drops what the founder's material
  answers, and the survivors come back in three tiers, with the calculator's mismatches and flags first. It never
  looks up or invents a market figure, price or share. `vc-positioning` now points to it. Four evals are in `evals/vc-market-sizing/`.
- The `vc-prospective-investor-update` skill, in preview: a founder drafts or reviews the short update they send the
  investors they hope to raise from, in the months before the raise, so each reader sees a line rather than a single
  point. The update keeps one fixed shape; a line table sets each metric's earlier values side by side as stated (up
  to the last six updates, the first always shown, nothing computed); the last update's "By the next update" items are
  tied out with their own statuses (Done, Partly done, Not done, Moved, No word, Not yet due); it keeps one ask, takes
  investors only as names the founder supplies and keeps them out of the update. A runway the update shows goes to
  `equity_runway_plan` with no raise and no milestone. A reader pass has four lenses (spin, moved goalposts, changed
  definitions, unreported promises) and a refute pass. The metric rules and the six metric status words moved out of
  `vc-current-investor-update` into `skills/vc-current-investor-update/references/metric-consistency.md`, which both
  skills read; `vc-current-investor-update` and `vc-positioning` now point to the new skill. Four evals are in
  `evals/vc-prospective-investor-update/`.

### Changed

- The repository was renamed from `opensource-content` to `ai-vc-skills`; GitHub redirects the old address.
- The knight logo has a little depth: a soft drop shadow, each slice shaded lighter at the top, and a faint
  highlight along the head's top edges. The banners, the site's logo and favicon (which follow the light or dark
  theme), the plugin icon and the social image all use it; shapes and base colours are unchanged.
- The seven `vc-positioning` and `vc-claims-check` evals were run in live Claude Code sessions (2.1.330, 2026-11-22).
  Each file keeps its expected answer and adds a trimmed excerpt of the recorded answer with a verdict against its pass
  sentence: two passed and five passed in part (Pass: every clause met; Partial: exactly one missed or met only in
  part; Fail: two or more missed). Eval F failed in its first two runs and passed in part in a third run after the
  skill fixes below; the third is the one recorded. The `vc-deal-math` evals now say they have not been run live.
- Skill fixes from those runs. `vc-positioning` now owns "check our story and our ask" (a run had routed it to
  `vc-deal-math`), runs its lenses and refute passes as subagents however short the material, makes one calculator call
  per version of the ask (two for a valuation with no label) and keeps the tool's values as printed, and, asked to play
  a named investor, offers the public frameworks and the lenses together with the prep session. `vc-deal-math`
  says to use `vc-positioning` for the story and the ask together, computes nothing outside the calculator's tools and
  runs no what-if the founder did not ask for. In `vc-claims-check`, the skeptic no longer judges whether the material
  answers an attack (the refute pass does), and the "AI-powered" pattern applies when nothing says what the model does.
- An independent review of the whole pack (a second model) and one live run per new skill on 2026-11-23, eleven in all,
  each recorded in its eval with a verdict under the README's rule. Fixes from them: every skill that passes a fully
  diluted share count now asks whether that count includes SAFEs and notes, since one that does gives the founders a
  wrong ownership figure; a calculator mismatch heads the list with no tier rather than being ranked "ends the meeting",
  and only a runway claim below the computed runway counts as understated; each skill that reads the calculator's flags
  carries the meaning of every flag code, since a tool call returns bare codes; one shared sentence says which monthly
  spend goes into the runway of a SAFE or note raise, and another forbids working out how two of the founder's figures
  relate ("more than doubled"); the memo's outcome table no longer sets a payout beside the amount invested;
  `vc-positioning` no longer credits a post its authors never read; and hand-offs, runway and metrics checks now that
  the tools exist, the refute pass, and the site and install guide. Two evals were renamed to companies BS and BT, so no
  company letter is used twice.
- Calculator fixes from an independent recheck of `market_sizing`, `runway_plan` and `metrics_check`. A market's unit
  price prints as a price, to the cent when exact and with the places it needs otherwise ($0.0075, never $0.01), and
  a price period left out comes back null, so a result's echoed inputs fed back keep `price_period_defaulted`; the
  YC citation now says the customers-times-price build is YC's method for a new product or space. A runway plan's
  required raise is rounded up to the cent, and the downside flag says it counts the no-raise row. In a metrics check,
  a stated burn multiple with no multiple to work comes back `not_checked`, which keeps the overall verdict off
  consistent; each percent, months or multiple row says whether the stated figure is the computed one rounded to its
  own places, with two flags where that and the tolerance disagree (`consistent_beyond_rounding`,
  `mismatch_within_rounding`) and the tolerances unchanged; a net revenue churn below zero, a gross retention above
  100% and a 0x multiple are checked rather than refused; `arr_movement_and_month_disagree` names an ARR movement and
  a latest month that disagree; the payback benchmark applies to a revenue-only payback already past it; and the
  report prints primed formulas once a starting-customers figure is given.
- A metrics check's stated percent, months or multiple is now consistent when it is the computed figure rounded half
  away from zero to the places it is written with, even past the tolerance, since people write figures rounded to the
  places they show: 12 months against 12.40 and a 2% churn against 2.4% hold, 2% against 2.6% does not, and `12.0`
  against 12.40 does not. The tolerances and their defaults are unchanged and money keeps the tolerance alone. The
  four `stated_*` cause flags read agreement with the other definition the same way, `mismatch_within_rounding` is
  gone (a rounding is no longer a mismatch), and `consistent_beyond_rounding` now names a figure that holds by the
  tolerance alone. A verdict line on such a row reads "within the tolerance, or rounding to the deck's, is
  consistent"; the README, the two skills and the metrics evals' excerpts follow.

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
