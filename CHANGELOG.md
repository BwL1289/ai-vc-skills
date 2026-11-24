# Changelog

All notable changes to this repository. Dates are UTC.

## Unreleased

### Added

- Plugin version 0.3.8 (the plugin's, the marketplace's and the `equity_calculator` package's), so an installed copy
  picks up the `runway_plan` report fix and the `vc-partner-meeting` "Draft taken" label, listed under Changed.
- Plugin version 0.3.7 (the plugin's, the marketplace's and the `equity_calculator` package's), so an installed copy
  picks up the `vc-partner-meeting` fixes from its first live drill, listed under Changed.
- Live runs of four more evals on plugin 0.3.5 (Claude Code 2.1.331), each recorded in its eval with an excerpt and a
  verdict under the README's rule: `vc-positioning` (Company BK), `vc-metrics-readiness` (Company DL) and
  `vc-cap-table-check` (Company CQ) passed, each with shortfalls against its expected answer noted, and `vc-deal-math`
  (Company DX) failed, with three clauses met only in part: its session loaded the `equity-calculator` skill, never
  `vc-deal-math`, so step 7's rules never reached it. These are the first recorded live runs of `vc-cap-table-check`
  and `vc-deal-math`. Earlier runs of the same four evals that day, on plugin 0.3.2, are not recorded.
- Plugin version 0.3.6 (the plugin's, the marketplace's and the `equity_calculator` package's), so an installed copy
  picks up the skill fixes from those runs, listed under Changed.
- Plugin version 0.3.5, and the `equity_calculator` package now carries the plugin's version (it had stayed at 0.1.0):
  the plugin starts the calculator's server with `uvx` from the package's folder, and uv kept serving its cached build
  of that folder until the package's `pyproject.toml` changed, so live runs, which loaded the plugin from one clone
  pulled in place, met an old server with 8 of today's 15 tools, the seven from `equity_runway_plan` to
  `equity_cap_table_check` missing (a plugin installed from the marketplace gets a new folder with each version, and so
  a new build). A test now fails when the package's, the plugin's and the marketplace's versions differ, and
  CONTRIBUTING.md has a Releasing section that says every release bumps all three. The package's `[tool.uv]` cache keys
  name `pyproject.toml` and `src/**/*.py`, so an edited or added module rebuilds the server between releases too; both
  cures were checked on uv 0.11.16 with a private cache, each on its own (a source-only edit kept the old build without
  them).
- `vc-deal-math`, `vc-round-sizing`, `vc-market-sizing`, `vc-positioning`, `vc-investor-memo`, `vc-taste-check`,
  `vc-diligence-questions` and `vc-partner-meeting` are out of preview: each was run on a real deck, and the deck's
  founder agreed with its output; plugin version 0.3.4.
- Live runs of five of the six skills added on 2026-11-24 (Claude Code 2.1.331), one eval each, each recorded in its
  eval with a trimmed excerpt and a verdict under the README's rule: `vc-competitive-landscape` (Company CM),
  `vc-option-pool-plan` (Company CP), `vc-pass-debrief` (Company CQ) and `vc-intro-email` (Company CU) passed, each
  with a shortfall against its expected answer noted, and `vc-raise-plan` (Company RA) passed in part. The
  raise-plan and option-pool-plan runs are second attempts: the first of each reached an out-of-date build of the
  calculator's server that lacked its tool, and is not graded. No live run of `vc-cap-table-check` is recorded yet.
- Plugin version 0.3.3, so an installed copy picks up the skill fixes from those runs, listed under Changed.
- The calculator's fifteenth scenario, `cap_table_check` (MCP tool `equity_cap_table_check`, a command and a
  `Cap table check` workbook sheet): a founder's cap table by class and holder line added up to the fully diluted
  shares, each class's and holder's exact percent set beside the percent the table states (rounding-aware, as in
  `deal_check`), each percent column against 100%, issued against authorised shares, the SAFEs and notes outstanding,
  and the departed holders' share. A class that gives both its shares and holder lines says whether the lines are
  every holder of it (`holder_lines`), never assumed. On the founder's own next round it previews the conversions
  through `round`, and on their planned rounds it follows the founders through `dilution`, from their share after
  that preview when there is one. It never rules on legal validity: its flags name the questions for the company's
  lawyer. The new `vc-cap-table-check` skill (preview, four evals) runs it.
- `metrics_check` (MCP tool `equity_metrics_check`) now works LTV on contribution margin (ARPA × the period's units ×
  margin / the churn the founder names, the gross margin flagged when no contribution margin is given, a churn at or
  below zero refused), LTV/CAC on blended CAC, the Rule of 40 from the founder's own growth and margin percents with the
  margin's basis named, and the magic number on revenue (4 × the quarter's change / the prior quarter's sales and
  marketing spend) or on ARR, and checks a deck's stated figures for each; seven new flags name an LTV on gross margin,
  a contribution margin above the gross margin, a stated LTV on revenue alone or on gross margin, an unnamed Rule of 40
  margin, a stated Rule of 40 on gross margin and a stated magic number without its 4. No benchmark is set for any of
  them. `vc-metrics-readiness` (and the skills that quoted LTV as unchecked) now send these to the tool, with a Company
  DL eval (unrecorded).
- `instrument_compare` runs with no next round, for a founder who hopes today's raise is the only one (mode
  `no_next_round`, flag `no_next_round_given`, in place of the refusal): ownership today with the note unconverted,
  what the note owes at each month named, the note at its maturity (the repayment, and a conversion only at a valuation
  or price the founder gives), and each exit as a sale before any priced round, option A through the waterfall and
  option B on the note's own change-of-control term (a multiple of its principal, or conversion at its cap). A sale
  with no such term, or with existing SAFEs or notes outstanding, gives option B as not worked with the reason; an
  uncapped note works in both modes. The mode flags a cap that sets no price there (`cap_unused_without_round`) and a
  note converted at its cap that a sale pays less than it owes (`note_paid_below_owed_at_sale`). `vc-deal-math` step 7
  asks for those terms and a Company DX eval runs the mode.
- Plugin version 0.3.2, so an installed copy picks up the fixes a real deck run's feedback asked for: the phased
  runway, the instrument comparison's summary, the market-sizing paths, lean mode without a subagent tool, and the
  per-skill rules listed under Changed.
- Plugin version 0.3.1, so an installed copy picks up the `vc-cap-table-check` skill, the calculator's fifteenth
  scenario, the new metrics in `metrics_check` and the no-next-round mode of `instrument_compare`; the README, the
  website, the plugin and marketplace descriptions and AGENTS.md list them, `vc-cap-table-check` hands the pool to the
  now-built `vc-option-pool-plan`, and the README's roadmap adds `vc-retention-cohorts` (planned: retention by customer
  cohort and where the curve flattens, with the deck's retention claims checked).
- Plugin version 0.3.0, so an installed copy picks up the five new skills and the calculator's two new scenarios;
  the README, the website, the plugin and marketplace descriptions and AGENTS.md list them, and the existing skills
  hand the topics they own to them.
- The calculator's thirteenth scenario, `pool_plan` (MCP tool `equity_pool_plan`, a command and a `Pool plan` workbook
  sheet): the option pool a founder's hiring plan needs until the next round beside the pool a term sheet asks for,
  both created in the pre-money and worked by the option-pool shuffle's own code, with the price per share, the
  effective pre-money, who owns what and the pool left ungranted at the next round side by side and requested - plan
  for each. Grants come in shares or as percents of the post-round shares, never a mix; it never picks a pool.
- The calculator's fourteenth scenario, `raise_pipeline` (MCP tool `equity_raise_pipeline`, a command and a
  `Raise pipeline` workbook sheet): what is left of a round after the lead's cheque, the firm commitments and pro rata
  (soft commitments shown, never counted), the term sheets the founder's funnel is expected to give on the founder's
  own stage rates (a benchmark rate only with its source, and flagged), the targets needed, and the start-raising month
  from the runway plan's own row. It flags a lead cheque, pro rata or a funnel left out, and names no investor.
- The `vc-competitive-landscape` skill, in preview: a founder builds the competition map and slide before a VC builds
  one about them. The competitors the founder names, each fact with its source, are placed at four levels (direct,
  indirect, adjacent, and substitutes, doing nothing included); three to five axes come with 1-to-5 anchors stated up
  front and the founder places every company; it writes the substitutes story, a why-customers-pick-us line per
  competitor and the answer to "what if the big platform builds this?", drafts the slide as a table and a 2x2, and
  runs an adversarial review with a refute pass. It looks nothing up. Four evals are in
  `evals/vc-competitive-landscape/`.
- The `vc-raise-plan` skill, in preview: a founder plans the raise from their own investor list. It tiers the list by
  the founder's own criteria, each attribute with its source or marked unverified, batches first meetings so they land
  within a few weeks of each other, dates the plan from the start-raising month and keeps a tracker table, with the
  room left, the expected term sheets and the targets needed from `equity_raise_pipeline`. It never looks anyone up,
  never names a firm as a fit and sends nothing. Four evals are in `evals/vc-raise-plan/`.
- The `vc-intro-email` skill, in preview: a founder drafts the emails that open investor conversations from their own
  material: a forwardable intro blurb with a note asking the connector for the intro, a cold email and two follow-ups,
  each short with one ask and every figure quoted as the founder gave it. A reader pass flags hype words, claims with
  no source and figures that disagree, and hands them to `vc-claims-check`. It looks nobody up and sends nothing. Four
  evals are in `evals/vc-intro-email/`.
- The `vc-pass-debrief` skill, in preview: a founder learns from the passes VCs send. Each pass is quoted word for word
  and grouped by the reason given, common readings of each phrase are labelled unverified (never what the investor
  meant), each reason maps to its fix or the skill that works on it, every come-back-when condition sits beside the
  founder's own figure, and a short reply per pass keeps the door open and asks for at most one referral. It sends
  nothing and keeps no list. Four evals are in `evals/vc-pass-debrief/`.
- The `vc-option-pool-plan` skill, in preview: a founder sizes the pool their own hiring plan needs until the next
  round and sets it beside the pool a term sheet asks for, both ways on `equity_pool_plan`: the price per share, the
  effective pre-money, the founders' ownership and the pool left at the next round, with one evidence line for the
  pool conversation built only from the founder's plan. It never says which pool to accept. Four evals are in
  `evals/vc-option-pool-plan/`.
- `vc-positioning` asks "what's contrarian?": a twelfth dimension, Contrarian insight (a belief most investors would
  reject today, who disagrees and why, and the founder's evidence), and a lens named by its test, Is it really
  contrarian?, which attacks a consensus view dressed up as an insight, a belief with no evidence, and one the business
  does not depend on. A founder with no such belief is asked once, with two prompts, and never given one; the answer
  gains a Contrarian insight block with at most two rewrites from the founder's own material; a Company BK eval
  (unrecorded) checks that a consensus claim is caught.
- `vc-deck-review` is out of preview after its first run on a real deck, whose founder adopted most of its fix list;
  plugin version 0.2.7.
- A `vc-deal-math` eval (Company BW, unrecorded) for a SAFE raise whose planned rise has its start month but no
  monthly spend, marked "not checked: waiting for [the planned monthly spend from that month]". It and the Company BV
  eval also expect the `equity_round` offer for the SAFE's ownership while the runway waits.
- Plugin version 0.2.6: every printed figure now rounds half away from zero (12.125 prints 12.13, -12.125 prints
  -12.13), the rule the rounding test of a deck's stated figure uses, so a deck that copies the report's figure holds;
  a note's interest keeps its own half-even rounding to the cent. The shared SAFE runway sentence also holds a planned
  change that has its start month but no amount, marking the runway line "not checked: waiting for [the planned monthly
  spend from that month]"; `vc-claims-check` names that held runway, and one held for its month, Needs a source; a
  `vc-deal-math` eval (Company BV) checks the month hold; and `vc-metrics-readiness` says what stays out of its tool.
- Plugin version 0.2.5: the priced-round-or-note comparison reaches installed copies, and `vc-deal-math` now triggers on "should we raise a priced round or a note".
- The calculator's twelfth scenario, `instrument_compare` (MCP tool `equity_instrument_compare`, a command and a
  `Priced vs note` workbook sheet): a founder choosing between a priced round now and a convertible note now gives
  both sets of terms, the next round (up to four alternatives for it, each worked from today) and the exits, and gets
  ownership by holder group after today and after each next round, and each group's payout at each exit, option A beside option B with B - A, worked through the
  round and waterfall code with every series' preference honoured. It never picks one; no next round is refused
  (`no_next_round_given`). The `vc-deal-math` skill routes that question to it (a new step 7 and a Company BU eval),
  and the `equity-calculator` skill lists it.
- Plugin version 0.2.1, so an installed copy picks up the rounding rule in the deal and metrics checks.
- The website shows the two demo recordings (Claude Code calling the calculator's MCP tool, and the calculator in a
  terminal) in a "See it work" section; the plugin's version is now 0.2.0, so an installed copy updates to the fifteen
  skills.
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

- `runway_plan`'s report says "not given: read as none" beside a phase's revenue a month that was left out, in the
  plan or in a downside or lean case given its own phases, where it printed "$0.00 given" as if the founder had stated
  0; a revenue given as 0 still reads "given", and the runway is the same either way. The words and the test of a null
  in the echoed inputs are `raise_pipeline`'s, now one shared constant beside "given", so a result fed back from its
  JSON keeps the difference. A case given as percents of the plan keeps "the plan's, scaled by the case's percent". No
  README or eval excerpt printed the old line; the calculator README's `runway_plan` usage now describes the new one.
- `vc-partner-meeting`'s debrief has a named label for an answer that is the skill's draft the founder took: "Draft
  taken: rehearse it in your own words before the meeting.", in place of what was weak or "held up". The draft is
  quoted as the skill's text with no answer label and gets no weak notes and no stronger answer; an answer the founder
  also gave in their own words is debriefed as usual. `references/debrief.md` defines it beside "held up",
  `references/drill.md` names it after its rule on taken drafts, and the skill's debrief summary and its hardest three
  carry it, with SKILL.md still at 349 lines; a new test pins all four.
- `vc-partner-meeting` takes five rules from its first live drill, each pinned in its test. The first three
  questions, and every one in the ends-the-meeting tier, are answered in the founder's own words before any draft is
  shown, even when the founder asks for a draft on every question (with a one-click draft on every question, a founder
  may rehearse few answers in their own words); a draft is built as a stronger answer is, and one the founder takes is
  the skill's text, never debriefed as the founder's answer. A follow-up is the moderator's own question in the
  founder's everyday words, never the skill's terms or investors' jargon: a plain question, then what is enough to
  answer it. When the founder says a new figure replaces one they gave, every draft that cites the old one is marked
  stale and redone from the new figure, through the calculator again where a tool computed it, and the new call's
  results replace the old call's; a figure that only differs from the material's is a disagreement for the debrief. A
  spoken answer that claims less than the material's own line gets a tiered rewrite in the debrief, within its four
  sentences: the strongest items a partner can check first, the rest said plainly, never restoring a figure the answer
  changed or took back. Where the material says nothing on a standing question its bracketed ask carries it, and each
  short answer to one (one that does not yet give what the founder should have ready) gets one specific next step, now
  a column of the standing prep table (put spoken interest in writing, line up references before the meetings, have
  today's runway in months ready from `equity_runway_plan`). To keep the skill under its 350-line cap, the drill's
  first-turn and follow-up rules moved into a new `references/drill.md` beside the new ones, which step 6 links, the
  one change in wording being "below", which reads "in the skill's Answering section" there. A new eval, Company DM
  (made up, unrecorded), exercises the own-words rule and the next steps over scripted tester turns.
- Skill fixes from the four live runs on plugin 0.3.5, each pinned by a test:
  - `equity-calculator` sends a priced round weighed against a convertible note (`instrument_compare`) to
    `vc-deal-math`'s step 7, and says to load the review skill a question belongs to and answer from it. When it answers
    a comparison itself, it leads with the result's `summary`, says in words which mode ran, shows A, B and B - A for
    every row that has them, ownership included, names each flag by its code with its meaning from the review skill's
    table, and adds, subtracts or divides none of the tool's figures in its own text (the run stayed in this skill,
    left out the mode and the ownership B - A, named no flag and worked out a remainder and a crossover of its own).
  - `vc-positioning`'s refute pass keeps an objection that a belief stated as contrarian is one most investors already
    hold when its quoted line shows others acting on the belief without naming it (a run's judge dropped the one
    quoting the competition slide as not grounded).
  - `vc-cap-table-check` never says or hints which line or total is wrong, even when a difference the tool prints
    equals one line's shares (a run matched the 100,000-share gap to the warrants line), and names each assumption it
    leans on by its key, with its source (a run paraphrased them).
  - `vc-metrics-readiness` keeps no tier on a mismatch a flag explains as another definition, whichever way it errs (a
    run tiered a magic number without its 4 as an understatement, which the eval's expected answer does not).
- Every calculator-backed skill puts the MCP tool first. Each command line a skill prints follows the MCP call it
  repeats and is labelled "Only when the tool is not in the session (search for it by name first), the same call from
  the command line" (the `equity-calculator` skill, which prints several, labels them in its own words); a command named
  in a sentence is the "command-line fallback, after a search for the tool by name", so the six skills whose own
  SKILL.md prints no command line but names one in a sentence still say to search first; and the `equity-calculator`
  skill's description and "Running it" section name the MCP tools first and say to search for a tool by name where
  tools load on demand. Live runs whose server lacked a tool had gone to the printed command line, which the session's
  shell refused. Pinned in `test_pack_shared_rules.py`.
- The no-tool rule, which `vc-raise-plan` and `vc-option-pool-plan` had in their own words, is one sentence in every
  skill that calls the calculator (17 skills) and in the template: when neither the tool nor its command line runs, say
  so and give no figure in the tool's place, none worked by hand and none from a worked example (a run without the tool
  added up a cap table by hand). Pinned in `test_pack_shared_rules.py`. To keep `vc-partner-meeting` under its 350-line
  cap, how its answer lays out the Numbers moved into its `references/calculator-flags.md`, the one change in wording
  being "the calculator flags table", which reads "the tables below" there.
- The worked examples in `vc-option-pool-plan` (now Company PW) and `vc-raise-plan` (now Company RW) use made-up
  inputs no eval uses, with fresh calculator output, so a figure quoted from them can no longer match an eval's answer
  without a tool run; `vc-raise-plan`'s batch-planning step follows its example's start month. Six older worked
  examples still use an eval's inputs (`vc-cap-table-check`, `vc-current-investor-update`, `vc-deal-math`,
  `vc-investor-memo`, `vc-market-sizing`, `vc-prospective-investor-update`); a test lists them, so none can be added.
- Skill fixes from the 2026-11-24 live runs. `vc-competitive-landscape` keeps an objection to a line that matches a
  pattern in its patterns table until the founder replaces the line, whatever other line would answer it, and quotes
  that line in the fix (a run had dropped the objection to "the only" line as answered by other lines).
  `vc-raise-plan` never proposes an earlier start month of its own, outside its late-plan and no-runway flags: until
  the founder names one, every week keeps the printed month's label (a run numbered its weeks from a window of its
  own and advised opening it now). `vc-raise-plan` and
  `vc-option-pool-plan` say so and give no figure when neither their tool nor its command line runs, never one from
  their worked example (a run with no tool quoted the example's figures as the calculator's). `vc-pass-debrief` ends a
  reply that has no come-back condition and no update to offer on one line that keeps the door open and promises
  nothing, and offers no update the founder did not ask to send.
- Per-skill fixes from a real deck run's feedback (the figures and wording of that deck are in no file):
  - `vc-deal-math`: an instrument comparison leads with the result's `summary`, read first over MCP, before the
    side-by-side table.
  - `vc-investor-memo`: the `exit_is_shared_amount` statement is quoted only under an outcome table a waterfall made;
    a computed mismatch has no tier, with its two exceptions (an understated runway, a one-reading valuation) each
    said to sit in a tier; the Risks left out lens returns every left-out risk, however many, and Top risks holds
    them all; a milestone counted from another start than today keeps its own clock and is never set against the
    runway.
  - `vc-diligence-questions`: a fourth checklist status, Unknown: ask, for a row the founder has not been asked about
    (Missing now needs the founder's list); a listed row cites only the bank questions of the founder's stage (a test
    proves the rule is needed); an HTML file's alt text and a PDF's text layer count as read.
  - `vc-partner-meeting`: one cap rule for how many questions a lens returns, carried in the Stage A brief; a question
    answered in part stays one kept question and counts once; with no cash given, no runway call runs and each runway
    line reads "not computed", never 0.00 months (a zero the founder states is still sent). Where the calculator's
    mismatches and flags go moved to the skill's flags file, beside the codes' meanings.
  - `vc-round-sizing`: the Start raising by cell says "not computed" when the tool printed none for want of months to
    raise, and "none: the cash never runs out" when the months were given and the row's cash never runs out; a case
    whose rows are the plan's is said once; the tool's own difference row may be quoted; step 1's list leads the Deck
    claims heading.
  - `vc-taste-check`: decisions are numbered T1, T2, so a founder log's own D numbers never clash; a log of mostly
    layout detail, or partly written by assistant sessions, keeps only the founder's decisions; Usefulness counts a
    customer's trust, so an honesty choice can be Clear; a new Claimed quality flag; "needs a story" is defined and
    the deck and the meeting share one bar.
  - `vc-market-sizing`: the no-market-count path quotes "not worked" and sends no stated TAM or SAM, or a population,
    and a SOM in units sends no customers today; a deck figure built from a top-down one is checked by the tool's
    comparable part, sent after every true top-down figure, and that row's share, difference, flag and break-even are
    never put to the founder as findings; the tool varies nine segment fields (the second line and the units to win
    too), and a SOM in units does not move with the count, the share served or the units per customer; the shakiest
    pick sits beside the founder's highest value, not an assumed high one; a horizon in months stays in months in the
    ledger; the answer keeps its ten sections.
  - `vc-deal-math`: on a priced round on a phased plan, `deal_check` gets the spend and revenue of the phase the round
    lands in, and a `runway_below_band` it raises is the quick check's, never the plan's.
  - `vc-positioning`: "What is our contrarian insight?" and "What do we believe that others don't?" are listed under
    When to use it, as they already were in the description.
  - `vc-intro-email` and `vc-pass-debrief`: a hand-off back to the vc-raise-plan skill, for the investor list and the
    tracker.
- A priced round on a phased plan: `equity_deal_check`'s one flat burn can call a deck's runway a mismatch that
  `equity_runway_plan`, on the founder's phases, calls consistent. The claims-check, deck-review,
  diligence-questions, investor-memo, metrics-readiness, partner-meeting and positioning skills now say, right
  after their phases rule, that such a round goes to `equity_deal_check` without its runway claim, the plan's
  runway and the claim's check come from `equity_runway_plan` (the round's amount as one `raises` entry), and both
  runways are quoted, each named; the vc-deal-math step 2 says to leave the claim out of the `deal_check` call. A
  phased plan is a change from a later month the founder names: spend planned from the round on stays
  `deal_check`'s planned burn. Each skill's own priced-round sentence that lists the runway claim now says "not on
  a phased plan". The vc-deal-math step 2 also says an uncapped note with the next round given still runs in
  `equity_round`, at its discount price. The
  investor-memo skill's round section had two lines Prettier had left unindented after an inline code span was
  split across them; it is rewrapped with each span whole.
- A note weighed against a priced round, or a SAFE or note with no next round: the investor-memo, partner-meeting,
  positioning and diligence-questions skills sent every SAFE or note to `equity_round`, which needs the next priced
  round. Each now says, in one sentence, that a note the founder weighs against a priced round now goes to
  `equity_instrument_compare` (vc-deal-math step 7, capped or not, in its no-next-round mode when no next round is
  expected), and that with no next round and nothing to weigh it against the instrument's share is "not computed:
  set at the next priced round". The vc-deal-math step 2 and its Limits say the same; the memo and diligence
  skills now name `equity_instrument_compare` among their tools.
- Lean mode with no subagent tool: every skill whose lenses feed a one-per-item refute pass now ends its lean
  paragraph by saying lean mode still applies past eight items, lens by lens in one agent, each item with a verdict
  of its own, the answer saying so and the full pass then one item at a time. The claims-check and round-sizing
  skills, whose one skeptic raises at most three attacks, each say in one sentence that lean mode never applies
  there. The deck-review and positioning skills no longer tell a no-subagent run to keep the lenses blind to tables
  in their own file, which the agent has already read: they say so, and that such lenses are less independent. The
  market-sizing check before answering now covers the no-subagent path too. The prospective-update skill drops a
  sentence its Runway bullet repeated from its "Built from" section, to stay under its line cap.
- Every skill with an intake (each Inputs section, the deal-math and cap-table steps that ask, and the calculator
  skill's first step) now says what to do when the founder cannot answer now: go on with what was given, keep any
  call or step that waits for an input waiting, invent nothing, list each ask in brackets under "Needs from the
  founder" (the open asks under that name), and keep a live drill for the founder. One sentence, word for word,
  pinned by the shared-rules test.
- To keep two skills under their line caps, the investor-memo skill's worked waterfall call (its JSON, the same
  command and part of what it prints) moves to `references/outcome-example.md`, and the partner-meeting skill's
  debrief shape and where its standing prep topics came from move to `references/debrief.md` and
  `references/standing-prep.md`; each skill links the file and keeps the rules that bind it, and their tests read
  the moved parts there.
- `market_sizing` takes a second revenue line from the same buyer (`second_line_percent`, `second-line-percent=`):
  a share of the main bill, kept whole and added to the take rate (annual revenue from one customer = the main bill
  × (take rate + second line)); the gross spend includes it; a `second_line_rule` assumption, a given line, a
  sensitivity field of its own, and break-evens on the take rate or the second line that hold the other fixed (a
  break-even at or below zero is out of range). The `equity_market_sizing` tool description now names the no-count
  path, `obtainable_units` and the second line.
- `raise_pipeline` keeps a cash floor or a phase's revenue left out as "not given: read as none" when a result's
  echoed inputs are read back from JSON (sent again, or to the workbook tool): a field left out is now null, not 0,
  in the inputs of both `raise_pipeline` and `runway_plan`, and a stated 0 stays "given".
- `market_sizing`'s `units_rule` row names the second line when a units segment has one; the `--sensitivity` help
  lists all nine fields; the `runway_plan` usage line names `--milestone-type`; the `runway_plan` and
  `instrument_compare` MCP descriptions name the run-rate, the milestone type, a raise of any instrument and the
  summary; the README's market-sizing assumptions table has the three new rule rows.
- `market_sizing` takes a SOM in the price's own unit (`obtainable_units`, `obtainable-units=`; seats, locations,
  licences): units × one unit's year × (the take rate + any second line), with no SOM customers, a `som_units` row, a
  `units_rule` assumption, a sensitivity field of its own, and refusals for units above the serviceable units or
  beside today's customers. Units no longer have to be typed as fractional customers.
- `market_sizing` has a path for a founder with only the customers to win and no count of the market: a segment
  with `customers` left out (its `obtainable_customers` then required), or given equal to the customers to win,
  works its SOM and leaves TAM and SAM unworked, with the totals, shares, top-down comparison and its break-even
  built on them, instead of printing the SOM again as a TAM. New flag `no_market_count` (and a row in
  vc-market-sizing's flag table), a `no_market_count_rule` assumption, "not worked" lines saying why, and refusals
  for what needs a market count (a stated TAM or SAM, a population, a share to win, a serviceable share, a
  sensitivity row on its customers or serviceable share).
- A `market_sizing` sensitivity row says where its SOM low and high come from: the field's value at each end and
  whether it is the base or one of the founder's values (`value_at_som_low`, `value_at_som_high`, `som_low_at`,
  `som_high_at`; a tie goes to the founder's value). With every value below the base, the report adds a line saying
  the SOM high is the base's, and vc-market-sizing's step 6 then quotes the SOM at the founder's highest value.
- `market_sizing` takes the SOM horizon in months (`som_months`, `--som-months`, 1 to 240) beside whole years: a
  30-month horizon is 5/2 years in the straight-line path, exactly; the years path is unchanged, and both at once is
  refused.
- `instrument_compare` opens with a short summary, in the report and as the JSON's `summary` (right after
  `scenario`): the founders' and the new money's ownership today and after each next round (or at the note's maturity
  conversion), then the founders' payout at each exit or sale, each under A, B and B - A and each a copy of a full
  row, with B "not worked" where a sale's term is missing. The full detail follows unchanged; the README and
  vc-deal-math eval excerpts are re-synced to the wider label column.
- `runway_plan` takes a phase's revenue as an annualised run-rate (`revenue_run_rate`, CLI `revenue-run-rate=`),
  divided by 12 exactly, with a `run_rate_rule` row saying so; and a `milestone_type` (`--milestone-type`): the
  default `next_round`, or `self_funding` for a founder's only round, where each milestone is checked at its own
  month, months to raise are refused, `no_time_to_raise_given` never fires and the milestone rule cites no source.
  `raise_pipeline`'s phases take the run-rate too.
- A runway-plan raise is cash of any instrument: a priced round, a SAFE or a note adds its amount at its month and
  converts nothing, as its `landing_rule` row and `--raise` help now say. `deal_check`'s `runway_rule` row names its
  runway as one flat burn, a quick check, and `vc-deal-math` sends a priced round on a phased plan to `runway_plan`
  for the plan's runway, quoting both runways by name.
- Every skill table that gives a scenario's flags their meaning now covers every code that scenario returns: the
  deal-math, positioning, deck-review and partner-meeting skills, which listed only the three runway-plan codes a call
  with no milestone returns, each keep a full `equity_runway_plan` table, and a new test registers every flag table
  against the schemas' flag lists.
- Every printed figure (the report, the JSON's `rounded`, workbook values, split cents and a message's percents) now
  rounds half away from zero, where it rounded half to even: 12.125 prints 12.13, not 12.12. No exact value, verdict
  or flag changes; a note's interest keeps its half-even rounding to the cent.
- The shared SAFE runway sentence (eight skills) also holds a planned change given with its start month and spend but
  no word on its revenue, marking the runway line "not checked: waiting for [the planned monthly revenue from that
  month]": the calculator reads a phase with no revenue as none, which shortens the runway (on one plan, 17.37 months
  for the raise against 20.06 with the revenue kept). `vc-claims-check` counts that wait among those that make a runway
  claim Needs a source, and gives a not-checked line only to a planned change's wait.
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
- Follow-ups from a check of that review. The shared SAFE runway sentence now says what to do while a planned change's
  start month is missing: make no runway call, give no runway figure and mark the runway line "not checked: waiting
  for [the month the planned spend starts]", as the skills already did for missing cash or burn. Every recorded verdict
  now counts the pass sentence as it was at the run, as the README says, and each eval whose sentence changed since
  names the changed clauses and how the run reads against today's sentence. That re-grades four: taste-check T from
  Partial to Fail, metrics-readiness AM from Partial to Pass, prospective-investor-update BE from Partial to Fail, and
  partner-meeting R, already Partial under that rule, now says so (a Fail against today's sentence). `vc-deal-math`
  carries the shared sentence against working out how two of the founder's figures relate.
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
- Metrics check follow-ups to that rule. The four `stated_*` cause flags are back on the tolerance alone, so the
  rounding rule decides a verdict, never a cause (a deck's 2x beside 1.5x on new ARR names no cause). A stated ARR is
  consistent within the tolerance of either the movement's ending ARR or the latest month's, and `arr_basis` and the
  report name the one it was checked against; `arr_movement_and_month_disagree` still says when the two differ. The
  rounding line shows the figure as typed (`rounds to the deck's "12"`), the six stated percent, months and multiple
  fields tell a JSON caller to send text with the document's places, and `vc-metrics-readiness` keeps "may be the
  founder's rounding" for an ARR or CAC mismatch, since money keeps the tolerance alone.
- A deal check's stated investors' percent, holder group's percent and runway now take the same rule: consistent
  within the tolerance or when the figure is the computed one rounded half away from zero to the places it is typed
  with (12 months against 12.40 holds, `12.0` does not; 17% sold against 16.6667% holds, 20% does not). The
  post-money (money) and the use-of-funds total (a sum of lines) keep the tolerance alone. Each such row says whether
  it is that rounding, `consistent_beyond_rounding` joins the deal check's flags, the three fields tell a JSON caller
  to send text with the deck's places, and the rounding test lives in one module both checks use. No eval's verdict
  changed; their excerpts, the README's and the site's were re-synced, and the skills' flag tables gained the row.
- A runway plan's stated runways (the no-raise one and each raise's, from today or from landing) take the same rule,
  with plugin version 0.2.2 so an installed copy picks it up: consistent within the tolerance or when the figure is the
  computed runway rounded half away from zero to the places it is typed with (12 against 12.40 months holds, `12.0`
  does not). The use-of-funds total keeps the tolerance alone. Each runway row says whether it is that rounding,
  `consistent_beyond_rounding` joins the runway plan's flags, both fields tell a JSON caller to send text with the
  founder's places, and the skills that relay the runway plan say so and explain the flag. One eval's verdict changed:
  Company R's "about 6 months" with no raise is 6.25 months rounded to whole months, so it is now consistent, not a
  minor-tier mismatch; every runway plan excerpt was re-synced.
- The README's front page describes the whole pack, with plugin version 0.2.3 so an installed copy carries it: the
  pitch, the opening paragraphs and "How it works" now cover the reviews as well as the calculator, "What you can
  ask" adds prompts for the metrics, market size, round size and product-decision skills, and the long caption under
  the demo recording is one line. The site's "See it work" introduction fits on one line, its first "How it works"
  step says the same as the README's, and AGENTS.md describes the pack the same way.
- After a real deck run, plugin version 0.2.4. Every review skill whose lenses feed one refute subagent per objection
  or question names one exception, in the same words: with more than eight after the quote check, one subagent per lens
  may take its lens's items, handed word for word an instruction to judge each as if it were the only one, with a
  verdict and quote of its own; an item no lens raised (a partner-meeting question from the bank) gets a subagent of its
  own, and one that comes back without its own verdict stays Kept (the deck review's seven lenses can raise up to three
  objections each). Each such skill's Answering section says when the pass ran per lens, that this is less
  independent, and that the founder may ask for the full pass, and the market-sizing count check allows it. Every skill
  with an Inputs section, and the deal-math skill's first step, reads a file the founder gives (a PDF, HTML, a slides
  export, Markdown), lists what it holds place by place in the file's own words, lists a place it could not read (a
  slide that is only a picture) as not read and asks for it, never reads a figure off a chart or a picture, and never
  asks for a paste of what it read; every "When to use it" bullet that names pasted material says it may come as a
  file, and the README and the site say a file may be given. In the eleven lens-review skills and the claims check, a
  refute pass now checks its answering line as the quote check does, spacing and line breaks aside, so a line that
  wraps in a file's text still answers; every quote check says "spacing and line breaks aside". The investor memo's
  flag table and the partner meeting's calculator flags and standing prep tables move to files beside each skill, so
  both stay under their line caps with every line wrapped. `test_pack_shared_rules.py` pins the shared sentences, the
  file note, the carve-out of the claims and round-sizing skills, and the width of the lines that carry them.

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
