---
name: vc-investor-memo
description: Helps a founder draft the internal investment memo their champion partner is likely to write for the partnership, so the founder sees the raise as the partnership will, finds the holes first and hands the champion clean material. From the founder's own material it writes the case in one shape (the company, why now, market and competition, traction, team, the round, top risks with the founder's mitigations, the outcome case), in the third person, no recommendation. The round's figures go to the calculator's deal_check or round tool, the outcome case to its waterfall and dilution tools on the founder's own exit assumptions, labelled as such; no fund size, no fund math. A dissent pass attacks the memo as a partner arguing against the deal would, and a refute pass drops what the founder's material answers. Use when a founder says write the investment memo for my champion, draft our IC memo, what will the partner write about us, or make the case for us internally. Never invents traction. Not investment advice.
---

# VC investor memo

Helps a founder write, ahead of time, the memo their champion partner is likely to write for the rest of the
partnership. A venture firm rarely decides on one partner's word: the YC seed guide says VCs "will have multiple
partners involved in the final decision", and that founders may leave a deck and an executive summary behind "so VCs
can show to other partners". The partner who likes the company then makes its case to colleagues who did not meet the
founder, often in writing (this skill's assumption, unverified; firms differ). This skill drafts that case from the
founder's own material, checks every figure of the round with the equity calculator, works the outcome case on the
founder's own exit assumptions with the calculator, then has a dissent pass attack the memo the way a partner arguing
against the deal is likely to. A refute pass drops every objection the founder's own material answers; the survivors
become a ranked fix list.

The founder is always the user. The memo is written in the third person about the company and carries no
recommendation: whether to invest is the partners' call, not the founder's or this skill's. The skill never plays an
investor, never writes as a named investor or firm, never claims to know any fund's memo format or decision process,
and never adds a figure, customer or fact the founder did not give. It takes no fund size and does no fund math.

## When to use it

- "Write the investment memo for my champion." "Draft our IC memo." "What will the partner write about us?" "Make the
  case for us internally." "What would a partner arguing against us say?" "Review the memo I drafted for our lead."
- Pasted material: a deck or its text, a one-pager, the round's terms, a cap table, metrics, the founder's notes on the
  team and the risks, and the exits the founder believes in. Or a memo draft the founder wrote (review mode). Any of
  these may come as a file the agent can read in this session.
- A founder who asks "show that we return their fund": the skill shows what the round's stake pays at the founder's
  own exit values, takes no fund size and says why once (see "The outcome case").
- Hand off:
  - A slide-by-slide read of the deck this memo draws on: the vc-deck-review skill.
  - Each claim's evidence, and figures that disagree across the deck, one-pager and memo: the vc-claims-check skill.
  - Rehearsing the questions the memo leaves open, before the partner meeting: the vc-partner-meeting skill.
  - The diligence questions and data-room checklist behind each section of the memo: the vc-diligence-questions
    skill (preview).
  - The ask's arithmetic in full (ownership after the round, the pool, the SAFE stack, runway): the vc-deal-math
    skill, whose steps this skill follows. One equity question on its own: the equity-calculator skill.
  - The one-liner, the story and the say-and-avoid list: the vc-positioning skill.
  - The traction section's ARR, retention, churn, CAC payback and burn multiple, checked against their parts: the
    vc-metrics-readiness skill (preview).
  - The market section's size, built bottom-up from buyers and price: the vc-market-sizing skill (preview).
  - How much to raise and what each amount reaches: the vc-round-sizing skill (preview).
  - The term sheet, once one arrives, line by line against a standard baseline: the vc-term-sheet-review skill
    (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess. When the founder gives a file the agent can
read (a PDF, HTML, a slides export, Markdown), read it yourself and list what it holds place by place (slide by slide
for a deck), in the file's own words, so the founder sees what was read from each. A place you could not read (a slide
that is only a picture, a page whose text did not come out, a file that opened only in part) is listed as not read and
asked for, never filled in from its title or the places around it, and a figure is never read off a chart or a picture.
Ask only for what you could not read and what the file does not show (speaker notes, the figures behind a chart, an
input below that it leaves out), and never ask the founder to paste what you already read.

1. The founder's material, each document named and its places marked (slide, page or paragraph), so every line the
   memo uses can be quoted with where it comes from. In review mode, the memo draft too.
2. The round as the founder states it: amount, instrument (priced round, SAFE or note), valuation or cap with its
   label (pre- or post-money), percent sold, pool target and its timing, SAFEs and notes converting, cash on hand,
   monthly burn and revenue as planned after the raise and today's, the runway claim, the use-of-funds lines, and what
   the round reaches.
3. The cap table: fully diluted shares, the unissued pool, the founders' shares, earlier preferred classes and their
   terms, and whether granted options are to be counted as exercised; the pro forma cap table if there is one. Ask
   whether the fully diluted total counts SAFEs and notes: the calculator's count leaves them out.
4. The outcome assumptions, in the founder's own figures: one exit value if things go badly, one on plan, one if the
   company wins; optionally the later rounds the founder expects before an exit (each as the percent it sells and any
   pool it adds). The founder's own words for why the company could become very large.
5. The top risks as the founder sees them, each with what they are doing about it and what shows it.
6. Stage, and anything the founder already knows the partner is worried about.

A missing input never stops the draft. It becomes a bracketed ask in the memo (`[the exit value if things go badly]`),
never a plausible figure.

## The memo's shape

Bullet points and short paragraphs, in this order. The shape is this skill's own, unverified: no public source this
skill's authors read describes a venture firm's internal memo, and each firm has its own. It follows the founder
guides below, so the partner gets the material in the order those guides use, and can re-cut it for their firm.

| Section                   | What it holds                                                                                             | Source                                                                                      |
| ------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Summary                   | Three to five points the case rests on, each one a fact from the sections below                           | YC seed guide (deck part 11, "3-5 key takeaways")                                           |
| The company               | What it does in one declarative sentence, for whom                                                        | Sequoia "Company purpose"; YC seed guide (deck part 1)                                      |
| Why now                   | What changed that makes this possible or needed now                                                       | Sequoia "Why now?"; YC seed guide (deck part 5)                                             |
| Market and competition    | Who buys, how many, what each pays, with the founder's evidence; the alternatives at four levels          | Sequoia "Market potential", "Competition / alternatives"; YC seed guide (6, 7)              |
| Traction                  | Period-by-period figures with their definitions, as the founder states them                               | YC seed guide (deck part 8); Sequoia "Financials"; periods and definitions ours, unverified |
| Team                      | Why these founders, one specific achievement each, and roles                                              | Sequoia "Team"; YC seed guide (deck part 10); one achievement each ours, unverified         |
| The round                 | Amount, instrument, valuation with its label, ownership sold, what the money reaches, from the calculator | YC seed guide (deck part 12, "Fundraising"); the calculator                                 |
| Top risks and mitigations | The three to five risks most likely to stop the case, each with the founder's mitigation and its evidence | Ours, unverified                                                                            |
| The outcome case          | What the round's stake pays at the founder's own exit values, from the calculator, labelled assumptions   | Graham, "Black Swan Farming"; Sequoia "Vision"; the calculator                              |
| Open questions            | What the material does not answer yet, each as a bracketed ask                                            | Ours, unverified                                                                            |

Rules for the text:

- **Third person, no verdict.** "The company sells ...", never "we recommend", "we should invest", "pass" or "a strong
  yes". No conviction score, no grade, no odds. The champion adds their own view; the memo leaves no slot for one.
- **The founder's facts only.** Each line quotes or closely restates a line of the founder's material; a figure is
  quoted as stated or comes from a tool. A target is written as a plan with its date ("plans to reach ... by ..."),
  never as a result.
- **Market:** bottom-up from the founder's evidence; a top-down figure only as the founder gives it, with its
  publisher and date, or with `[publisher and year]`. The YC guide's DON'T list includes "Use ridiculous / silly market
  size numbers without clear justification". Never volunteer a market-size threshold.
- **Competition** at four levels (Direct, Indirect, Adjacent and platform, Doing nothing), the same grouping as the
  vc-deck-review skill, its own and unverified. The skill names no competitor itself: a missing level is a bracketed
  ask.
- **Risks are the hard ones.** A risks section that lists only what the founder already has an answer for reads as
  spin. Each risk the founder's material shows (a lost customer, a slipped launch, one customer making up most of
  revenue, a platform that could add the feature) is in it, whether or not the founder listed it, in the founder's
  words. A mitigation is what is being done and what shows it; a hope is labelled as a plan.
- **Metrics and market size.** This skill computes neither. ARR, retention, churn, CAC payback and burn multiple are
  checked against their parts by the vc-metrics-readiness skill, as are LTV, LTV/CAC, the Rule of 40 and the magic
  number; a market size is built bottom-up by the vc-market-sizing skill; here all are quoted, with the skill named.
  Growth rates are quoted as stated, with "not checked: no tool computes this". None is computed, converted or rounded.
- **Figures as stated, everywhere.** In the memo, the fix list and the biggest fixes, a figure is quoted as the founder
  states it (45%), never restated in words ("nearly half", "most").

## Steps

With a subagent tool (in Claude Code, the Agent or Task tool), step 7 runs the five lenses as subagents launched in one
message, however short the material, then one refute subagent per objection, as "How to run the lenses" says.
Without a subagent tool, run Stage A of the dissent pass first, before step 1, on the founder's material (and the
memo draft, in review mode), as "How to run the lenses" says; step 7 then starts at the draft checks there (draft
mode) or at the quote check (review mode).

1. **Quote first.** List every line of the founder's material the memo can use, word for word with its document and
   place, under the section it belongs to. Do not tidy anything yet.
2. **Ask for what is missing,** once, in one message (Inputs above).
3. **Figures across the documents.** Put every place a figure appears side by side, quoted. The same metric, in the
   same form, for the same period, with different values is a contradiction: both lines go to the fix list. Lines in
   different forms (MRR against ARR, a month against a quarter) are never compared or converted: ask for one figure,
   in one form, with its period. For every claim's evidence, the founder runs the vc-claims-check skill.
4. **The round** (below): `equity_deal_check` or `equity_round`, and the runway claim.
5. **The outcome case** (below): `equity_pool` for whole share counts, `equity_waterfall` once per exit value, and
   `equity_dilution` for the founder's assumed later rounds.
6. **Draft or revise.** Draft mode: write the memo in the shape above from the founder's material and the tools'
   values only, every gap a bracketed ask. Review mode: keep the founder's draft and words; change only what step 3,
   a tool or a kept objection requires.
7. **Run the dissent pass** (below): attack, check the quotes, refute, rank. Revise the memo for every kept
   objection, using only the founder's facts or a bracketed ask.
8. **Check before answering.** Every line of the memo appears in the founder's material or in a tool result; every
   figure is quoted as stated or comes from a tool, as printed; every exit value is the founder's and labelled an
   assumption; no fund size, fund share, multiple on invested or return rate appears; no sentence recommends, speaks as
   an investor, names a firm as a voice or claims to know a firm's process; every surviving objection quotes a line that
   is in the material word for word; every risk the founder's material shows is in Top risks; every Summary point is a
   fact from a section below; the `exit_is_shared_amount` statement is quoted word for word, with its key, directly
   under the outcome table; the memo's Open questions lists its bracketed asks in full; no figure is restated in words.
   Never work out how two of the founder's figures relate (a difference, a sum, a ratio or multiple, a share left over,
   "doubled") in a rewrite, a line or a table cell unless the founder's material states it or a tool returned it; quote
   both figures as stated instead ("from 2,000 to 4,500", never "more than doubled").

## The round

The round's figures are checked once, as the vc-deal-math skill describes:

- **A priced round:** `equity_deal_check` (from the command line, `equity_calculator deal_check`), money and percents as
  strings (a stated percent or runway with the document's own places), share counts as integers, with every figure the
  memo states: the raise, the valuation and its label, the percent sold (`stated_investor_percent`), the founders'
  percent after (`holder_shares`, `stated_holder_percent`), each SAFE or note converting in this round as `instruments`
  (its terms as the founder gives them; left out, the founders' percent comes out too high), cash, burn and revenue as
  planned (`planned_monthly_gross_burn`, `planned_monthly_revenue`) and today's (`current_monthly_gross_burn`,
  `current_monthly_revenue`) only when the founder gives a different figure for today, the runway claim and the
  use-of-funds lines. One call per document that states the round differently. A valuation with no label: call twice,
  once as `pre_money`, once as `post_money`, and show both readings side by side, as vc-deal-math step 4 does. A
  mismatch that appears under only one reading is not listed as a computed mismatch: its fix is "say whether the
  valuation is pre- or post-money", with both readings quoted.
- **A SAFE or note:** not passed as `investment`. Route it as vc-deal-math step 2 does, to `equity_round`, with the
  next priced round the founder expects, labelled the founder's assumption in the memo. `equity_round` compares no
  stated figure, so quote its values beside the memo's, without a verdict. The runway claim and the use-of-funds lines
  on a SAFE or note raise go to `equity_runway_plan` with the raise as cash only
  (`raises: [{"amount", "stated_runway_months", "use_of_funds": [{"percent"}]}]`). On a SAFE or note raise, the `plan`
  case's phases are the founder's own figures: today's monthly spend and revenue as the first phase, from month 1, and
  each change the founder plans (more spend after the raise, say) as a later phase from the month the founder names,
  each asked for by name when missing (`[planned monthly spend and revenue, from which month]`), never assumed. Until a
  planned change's start month, its monthly spend and its monthly revenue are all given, make no runway call and give no
  runway figure; mark the runway line "not checked: waiting for [the month the planned spend starts]" while the month is
  missing, "not checked: waiting for [the planned monthly spend from that month]" while the month is given and the spend
  is missing, or "not checked: waiting for [the planned monthly revenue from that month]" while only the revenue is
  missing.
- **Runway with no raise** (what happens if the round does not close), on any instrument: `equity_runway_plan`, whose
  no-raise row is the figure, with the memo's stated no-raise runway as the top-level `stated_runway_months`. With no
  cash on hand or no burn given, ask for them; make no runway call until they are in.
- Fully diluted shares, for the tool, count every share before the round, granted options and the unissued pool
  included and SAFEs and notes excluded. Some cap tables count SAFEs and notes in their fully diluted total; ask which
  way the founder's does, and pass the tool its own basis. If the founder's total counts them, ask for the total
  without them, `[fully diluted shares before the round, SAFEs and notes left out]`, and leave the cap-table fields
  out of the call until it comes; never subtract the SAFE or note shares yourself.
- A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point of its
  `rounded` value two places to the right, keeping every digit (0.200000 is 20.0000%). That is notation, not a
  calculation; never round it.
- Each code in `flags` goes into the fix list, after the computed mismatches and with no tier, as a question a partner
  is likely to ask, and into Numbers. Over MCP a flag comes back as a bare code: give it with its meaning from this
  skill's flag table ("Flags"). The benchmark flags (`dilution_above_band`, `runway_below_band`) are common
  benchmarks, not rules: say so and quote the tool's assumption row with the source that row gives.

Part of what `equity_deal_check` prints for Company BM (made up: $3,000,000 at a $12,000,000 pre-money, a pool topped
up to 10% in the pre-money, founders with 8,000,000 of 10,000,000 shares, and the memo's "founders keep 59%" and
"23 months of runway"):

```text
  Investors' share of the cap table                                              20.0000%  N/T
  Effective pre-money                                                      $10,500,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  Holder group's percent after: the calculator gives                             58.9474%  h·(share every pre-round share keeps)
  Holder group's percent after: verdict                                        consistent  within the tolerance, or rounding to the deck's, is consistent
  Runway: the calculator gives                                               22.67 months  (cash + I)/net burn, planned (else current)
  Runway: verdict                                                              consistent  within the tolerance, or rounding to the deck's, is consistent
  A VC is likely to ask                                    pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
```

The memo then states the round with the tool's values ("founders hold 58.9474% after the round") and the effective
pre-money beside the headline, since a partner prices it that way.

## The outcome case

Startup returns are uneven: Paul Graham writes that "effectively all the returns are concentrated in a few big
winners", and that "it's not their chances of succeeding that matter but their chances of succeeding really big"
("Black Swan Farming", 2012). So the partnership asks how big the outcome could be. This section shows what the
round's stake pays at the founder's own exit values. It is a lens on the founder's deal, never fund math: the skill
takes no fund size, works out no share of a fund, no multiple on invested and no return rate, and never writes "this
returns the fund". Whether an outcome matters to a given fund is the partner's judgment. Sequoia's outline asks the
same question from the founder's side: "If all goes well, what will you have built in five years?"

1. **Exit values** are the founder's own (Inputs 4), each labelled "the founder's assumption" in the memo, with the
   founder's reason quoted beside it. Never an exit the model worked out: no revenue multiple applied, no comparable
   company, no "half the post-money". A founder who states an exit as a multiple of revenue is asked for the dollar
   figure.
2. **Whole share counts.** `equity_waterfall` takes whole shares. With a pool top-up and no SAFE or note converting,
   call `equity_pool`, only for share counts: the same round with `share_rounding` set to `whole_shares`. Its
   `pre_money` is `equity_deal_check`'s `pre_money` ("Pre-money valuation (V)"), passed on, never subtracted by hand.
   Take `investor_shares` and the `existing_holders` row from `pool_in_pre_money` (or `pool_in_post_money`, by the
   round's pool timing). A whole share count comes back as `"2714285.000"`; pass it as the integer `2714285`
   (notation, not rounding). Every price, valuation and percent in the memo comes from the round's tool (whole shares
   move the pool's figures by cents, $10,500,000.83 against $10,500,000.00 for Company BM's effective pre-money). When
   SAFEs or notes convert in this priced round, the calculator's converted shares are fractional and
   `equity_waterfall` takes whole shares: run the waterfall only with the pro forma cap table's counts. Without them,
   say "not run: the waterfall needs whole share counts; send the pro forma cap table" and ask for it. With no pool
   top-up, no tool prints share counts (`equity_pool` refuses a `target_pool_percent` of 0): use the pro forma's
   counts, or the same string. When the round itself is a SAFE or note, run no waterfall, pro forma or not, and say
   "not run: a SAFE or note holds no shares until the priced round it converts in, so this round has no payout to
   show"; step 7 says what the memo gives instead.
3. **`common_shares`:** the issued common that takes part in a sale (the founders' shares, other issued common, and
   granted options only when the founder says to count them as exercised). The unissued pool and unexercised options
   are left out: the tool's `exit_is_shared_amount` assumption (unverified) has `common_shares` count only the common
   that takes part. Take the count from the pro forma cap table or a count of issued common the founder states. The
   `existing_holders` row of `equity_pool` (every share but the unissued pool, so earlier preferred shares too) serves
   only when there are no granted options (or the founder says to count them all as exercised) and no earlier
   preferred class; otherwise take issued common from the pro forma or the founder's count, or the earlier class is
   counted twice. Never add or subtract shares yourself.
4. **Classes.** The round's new series is one class: its shares (from the pro forma or the `investor` row of
   `equity_pool`), `invested` = the raise, and the `preference_multiple`, `participation` and `rank` the term sheet
   gives. With no term sheet yet, call with the tool's defaults (1x, rank 1, no participation) and say in the memo that
   these are the calculator's defaults, not agreed terms. Each earlier preferred class is its own class with the terms
   the founder gives. Each SAFE or note converted in this priced round is its own class too, never part of
   `common_shares`: its shares from the pro forma, `invested` = its purchase amount (for a note, the amount the
   founder states as converting; never principal plus interest worked out by hand), and the preference the founder's
   documents give; with none given, the tool's defaults at the new series' rank, said in the memo as for the new
   series. Seniority: every class at rank 1 when the terms say pari passu or are silent (say so); the new
   series at rank 1 and earlier ones at 2 when the terms stack them.
5. **One `equity_waterfall` call per exit value.** Read `rows[]` (`payout`, `converts`, `preference_owed`) and
   `common_payout`. The memo gives, for each exit value, each class's payout as printed with whether it converted, and
   common's payout. The amount invested never sits beside a payout, in the table or in a sentence: side by side they
   read as a return multiple, which is fund math.
6. **Later rounds**, only when the founder gives them: `equity_dilution` with `holder_percent` = this round's
   percent as the round's tool printed it, and `rounds` = the founder's assumed later rounds (`investor_percent`,
   `pool_percent`), labelled assumptions. For a priced round, that percent is `equity_deal_check`'s "Investors' share
   of the cap table". For a SAFE or note, it is the row `equity_round` prints for the instrument this round sells, never
   "Ownership: investor", which is the expected priced round's buyer. `equity_round` numbers SAFEs and notes in one
   count, in the order they are passed ("Ownership: SAFE 1", "Ownership: Note 2"): pass the outstanding ones first and
   this round's last, and take the row with that number. `rounds` holds only the rounds after that priced round, which
   `equity_round` has already counted. A round sold as several SAFEs or notes has one row each: one `equity_dilution`
   call per row, each final stake quoted as printed; their combined stake is not checked: no tool computes this. The
   memo gives the final stake as printed.
7. **Label the two apart.** The waterfall's payouts use the cap table right after this round. No tool here combines a
   later round's dilution with an exit, so the memo says: "The payouts above use the cap table right after this round,
   before any later round. After the founder's assumed later rounds the stake is [final stake] (calculator); the payout
   after those rounds is not checked: no tool computes this." A SAFE or note round has no payouts (step 2), so its
   memo says instead: "The stake is [stake] after the founder's assumed priced round and [final stake] after the
   founder's assumed later rounds (calculator); what the stake pays at an exit is not checked: no tool computes this."
   Never multiply a stake by an exit value.

```json
{
  "inputs": {
    "exit_amount": "150000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "3000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      }
    ]
  }
}
```

The same call from the command line:

```
equity_calculator waterfall --exit-amount 150000000 --common-shares 9500000 --class "shares=2714285 invested=3000000 preference-multiple=1 rank=1 participation=none"
```

Part of what it prints for Company BM at the founder's plan exit of $150,000,000:

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                              $33,333,326.51  preference paid + part of the rest
  Common stock's payout                       $116,666,673.49  common shares × per-share part
```

The class's payout is not its cap-table percent times the exit: the unissued pool takes no part in a sale (step 3),
so the shares that do take part split the exit among fewer shares. Directly under the outcome table, quote the
waterfall's `exit_is_shared_amount` statement word for word, in quotation marks, with its key, so no reader takes the
payout for a mismatch: `exit_is_shared_amount`: "The exit amount is what the shareholders share: no debt, fees, escrow, accrued dividends or option exercise cash is taken out first, and common_shares counts every common share that takes part (exercised options included; unexercised options take nothing)."

## Dissent pass (adversarial review)

The memo is the case for the company; this pass is the case against it, made the way a partner arguing against the
deal is likely to make it, so the founder fixes the holes before the partnership finds them. Independent lenses attack
the memo, a second pass judges each objection using only the founder's material, and only what that material does not
answer reaches the ranked fix list. The founder sees both: what survived, and what was tested and fell.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people: none is a named investor, firm
or author, and none speaks in the first person as an investor.

| Lens                  | What it tests                                                                                              | Sections                        |
| --------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- |
| Market and why now    | Who exactly buys, how many there are, what changed, and whether the alternatives at four levels are faced  | Why now; Market and competition |
| Traction and evidence | Whether each figure has a definition and a period, and whether the summary claims more than the figures    | Summary; Traction               |
| Team                  | Why these founders, shown by specific achievements and roles rather than adjectives or advisors            | Team                            |
| Round and outcome     | What the money reaches, whether the round's figures agree, and whether each exit value has a stated basis  | The round; The outcome case     |
| Risks left out        | A risk the founder's material shows that the memo leaves out, and mitigations that are hopes, not evidence | Top risks and mitigations       |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner arguing against the
  deal is likely to say ..."); you are not an investor and do not speak as one, named or not.
- Read only the memo and the founder's material given here. Bring in no outside fact about the company, its market or
  its competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the memo's line it is about, quoted word for word with
  its section (for something left out, the founder's line the memo leaves out, with its document and place); why a
  partner arguing against the deal is likely to use it; and how much it hurts (sinks the case, weakens it, or minor).
- A reason you cannot tie to a line of the memo or the material is not an objection. List it apart as a gap, worded as
  a question to the founder.
- Do not judge whether another line answers an objection: raise it anyway, however short the material; the refute
  pass decides. A line that
  carries its own answer (a risk stated with what is being done and what shows it) is not objected to for lacking
  that answer. Return "nothing found" only when no line gives this lens an objection worth the partnership's time.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the lenses as parallel
subagents, however short the material, all launched in one message. Give each one only the memo, the founder's material and its lens brief: not this skill's other sections,
not the tool results, not another lens's output. Without one, run Stage A first, before step 1, on the founder's
material (and the founder's memo draft in review mode): run the lenses one after another, write each lens's objections
down in full before reading the next lens's brief, and never revise an earlier list. In draft mode without subagents
no memo exists yet and the same agent writes it, so the lenses read the founder's material only: each objection
quotes the founder's line with its document and place, the Risks left out lens lists every risk the material shows,
and the Traction and evidence lens lists what the figures do and do not show. After step 6, two draft checks run on
the drafted memo, each written down before Stage B: every risk on that list is in Top risks, and every Summary point
is a fact from a section below (the last pattern in the table). A miss is an objection quoting the memo's line, or
the founder's line the memo leaves out. The answer says these lenses are less independent than subagents.

**The calculator's mismatches** do not go through the lenses or the refute pass. Each heads the ranked fix list
under **figures that do not match (computed)**, quoting the memo's figure with the tool's value and difference. It is
not refuted: the calculator computed it. The one exception is a mismatch under only one reading of a valuation with no
label, which becomes the fix "The round" gives. A runway mismatch with the claim below the computed runway
understates it: the memo may keep it or state the computed runway, and it goes in the minor tier at most.

### Check the quotes

Before Stage B, check every objection's quote against the memo and the founder's material. A quote that does not
appear there word for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same
objection about the same line, merge them and keep both lens names. Gaps go to the open asks.

### Stage B: refute

Each objection gets its own refute pass. With a subagent tool, launch one subagent per objection in a single message;
never put two objections in one subagent. Give each the founder's material, the memo, that one objection, the Pattern
column of the table below and everything from "The refute brief:" to the end of this stage, and nothing else. Without
one, decide the objections one at a time against the same brief.

**Lean mode,** the one exception: with more than eight objections after the quote check, the refute pass may instead run
one subagent per lens, all in a single message. Each gets what a one-objection subagent gets, but with every objection
from its lens (one that two lenses raised goes to one of them only; one that no lens raised gets a subagent of its own),
and with this instruction, word for word: "Apply the brief to each objection as if it were the only one you were given.
Return one verdict for each, with its own quote where the verdict needs one. Never let one objection, its verdict or its
answering line decide another." Any objection that comes back without a verdict of its own stays Kept. The answer then
says the refute pass ran per lens, which is less independent than one subagent per objection, and that the founder may
ask for the full pass, one subagent per objection.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third person;
  you are not an investor and do not speak as one, named or not.
- Use only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic.
- How a partner is likely to read a line is not an outside fact: judge whether the material answers that reading.
- A line that matches a pattern in the list you were given never answers an objection.
- Return one verdict from the three below, quoting the founder's line word for word where it needs one. When you
  cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the founder's material other than the objected line supplies the specific thing the
  objection says is missing. Quote it with its place; when the memo leaves it out, say to add it.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact about the company, its market or its competitors.
- **Kept:** neither holds. When the best answer needs something the material does not contain, the objection stays
  and that something becomes the evidence to add, as a bracketed ask. A line that answers only part of the objection
  (one founder's achievement when the memo speaks for several founders) does not drop it: the objection is Kept for
  the part left, the answering line is quoted for the memo to carry, and the part left becomes the bracketed ask.

The refute pass invents nothing on the founder's behalf. Spacing and line breaks aside, an answering line that is not in
the material word for word does not drop the objection, and neither does one that is the objected line itself.

| Pattern                                                                             | Why a partner arguing against the deal uses it         | Source                                                                         |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------ |
| A market size with no basis, or a top-down figure only                              | Nothing ties it to who will buy                        | YC seed guide (DON'T list); vc-claims-check                                    |
| "No competitors", or a competition section with no doing-nothing level              | The need is not real or the founder has not looked     | Sequoia "Competition / alternatives"; the doing-nothing level ours, unverified |
| A target written as a result ("will reach", "is on track") with no figure behind it | A plan presented as traction                           | Ours, unverified                                                               |
| A risks section with no risk the founder has not already answered                   | Reads as spin; the dissent will name the real risk     | Ours, unverified                                                               |
| A mitigation that names an intention, not an action under way or its evidence       | A hope, not a mitigation                               | Ours, unverified                                                               |
| An exit value with no stated basis, or an outcome stated as a certainty             | The outcome case rests on nothing a partner can repeat | YC seed guide (DON'T "Claim you know something that you don't")                |
| Team described by adjectives ("world-class", "serial") or by advisors               | Nothing specific to check                              | vc-claims-check (its credentials and advisors rows)                            |
| A summary point that no section below supports                                      | The summary claims more than the memo shows            | Ours, unverified                                                               |

### The ranked fix list

Order the kept objections in three tiers, most damaging first: **sinks the case**, **weakens it**, **minor**. The
calculator's mismatches head the list, ahead of the tiers, under **figures that do not match (computed)**, with no
tier; the flags follow them, also with no tier, as questions a partner is likely to ask. Within a tier, an objection raised by more than one lens comes first. The tier is a judgment, not a probability:
give no percentages and no score. Each entry is one fix: the section, the line quoted word for word, why a partner
arguing against the deal is likely to use it in one or two plain sentences, and the change, using only the founder's
facts or a bracketed ask. A Kept objection answered in part says so in its Fix cell: it quotes the answering line
with its place and names the part left as the bracketed ask. A kept objection the founder cannot fix before the
meeting goes into the memo's Top risks, in the founder's words, and into Open questions.

## Answering

Lead with the biggest fixes, then the memo, then the full fix list.

1. **The biggest fixes,** at most three, one line each: the top of the ranked fix list.
2. **The memo,** ready to hand to the champion, in the shape above, revised for every kept objection, every gap a
   bracketed ask, every exit value labelled the founder's assumption, and one line at its head: "Drafted by the founders
   from their own material; figures from the equity calculator; not the firm's format." The memo is handed on alone, so
   its Open questions section lists its own bracketed asks in full and never points to the answer's Open asks.
3. **Ranked fix list,** as a table: Rank, Tier, Section, Lens, The line (quoted), Why a partner arguing against the deal
   uses it, Fix; the figures that do not match (computed) first, then the flags. Then **Dropped,** one line each: the
   objection, its lens, and why it fell. Say how the lenses and the refute pass ran (as subagents, one refute subagent
   per objection); in lean mode, one per lens. When the refute pass ran per lens (lean mode), say so, say it is less
   independent than one subagent per objection, and say the founder may ask for the full pass.
4. **Numbers:** each tool call's verdict and the rows the memo uses, as printed; each flag as its code with its meaning
   from the flag table; the outcome table (Exit value, the founder's reason, each class's payout, Converts?, Common's
   payout; never the amount invested) with the `exit_is_shared_amount` statement quoted under it; the stake after the
   founder's assumed later rounds; the assumption rows the figures lean on; metrics and market sizes quoted as stated,
   with the skill that checks them named (LTV and the magic number among them); growth rates and every other figure
   quoted as stated with "not checked: no tool computes this".
5. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
6. **Sources:** the guides used, with links, and which points are this skill's own judgment.
7. **Close:** this is not investment, legal or tax advice; the champion decides what to use and writes the firm's
   own memo; customers named in it should have agreed to be named; a lawyer should look at anything sent to people
   who are not yet investors.

## Flags

A tool's `flags` holds codes only; over MCP no sentence comes with them. What each code means for the founder (a
question a partner is likely to ask, never an error, and never a change to a verdict) is the flag table in
[`references/flags.md`](references/flags.md); read it when a tool returns a flag.

## Sources

- Y Combinator, "A guide to seed fundraising" (Geoff Ralston): https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising
- Sequoia Capital, "Writing a Business Plan": https://www.sequoiacap.com/article/writing-a-business-plan/
- Paul Graham, "Black Swan Farming" (September 2012): https://paulgraham.com/swan.html

The memo's shape, that a champion writes the case down at all, the Top risks and Open questions sections, the five
lenses, four of the eight patterns and where computed mismatches sit in the fix list are this skill's own judgment,
unverified. No public source its authors read
describes how any venture firm writes or uses an internal memo, and the skill claims no such knowledge. The two-stage
review (attack, then refute with the founder's own material) is this repository's own method.

## Limits

- Not investment, legal or tax advice. It does not say whether to invest, whether to raise, or at what valuation.
- It writes no recommendation, no conviction score, no grade and no odds of a yes.
- It never writes as, imitates or names as a voice any investor, firm or author, never claims to know a real fund's
  memo format or decision process, and does no investor research.
- No fund math: no fund size, no share of a fund, no multiple on invested, no return rate, no "returns the fund".
- It never invents or strengthens traction, customers, team credentials, risks' mitigations or exit values.
- No arithmetic outside the equity calculator's tools. Metrics and market sizes are quoted here and checked by the
  vc-metrics-readiness and vc-market-sizing skills (LTV and the Rule of 40 included); growth rates are quoted; a
  later round's payout at an exit is not checked.
- The dissent pass predicts likely objections from the memo's text; a real partnership may raise others.
- It works from the founder's material and sends nothing anywhere.
