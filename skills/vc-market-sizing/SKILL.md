---
name: vc-market-sizing
description: Helps a founder build a market size a VC can check, bottom-up from the founder's own evidence. It asks who buys, how many there are, what each pays, which of them the product can serve today and how many the founder plans to win by when, records each assumption with the founder's source, and works TAM, SAM and SOM per segment exactly with the calculator's market_sizing tool, which also checks the deck's stated figures, compares the result with any top-down figure, and reruns it on the founder's low and high values for the shakiest assumptions. An adversarial review has three lenses attack the market story as partners do (an inflated TAM, a SOM with no path, double counting), and a refute pass keeps only what the founder's material grounds. Use when a founder asks how big is our market, help me size our market, build our TAM SAM SOM, is our TAM credible, bottom-up or top-down, or pastes a market slide or a 1% of the market line. Never looks up or invents a market figure, price or share. Not investment advice.
---

# VC market sizing

Helps a founder answer "how big is this?" the way a partner will check it: who exactly buys, how many of them there
are, what each pays, and how many the company can win, each figure the founder's own and each with its source. The
`equity_market_sizing` tool works every total exactly, segment by segment, checks the deck's stated market figures,
compares the result with any top-down figure as a cross-check, and reruns it on the founder's own low and high values
for the assumptions they are least sure of. A short adversarial review then attacks the market story the way partners
do and keeps only the attacks the founder's material grounds.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
looks up a market figure, and never adds a count, price, share, adoption rate or horizon the founder did not give.

## When to use it

- "How big is our market?" "Help me size our market." "Build our TAM, SAM and SOM." "Is our TAM credible?" "Will a
  VC believe our market size?" "Bottom-up or top-down?" "What if our price is lower?" "Which assumption matters most?"
- A pasted market slide, an analyst figure ("$40B by 2030"), or a "we only need 1% of the market" line.
- Hand off:
  - Every claim in the materials checked, market size among them, with no sizing asked for: the vc-claims-check skill.
  - The deck as a whole, slide by slide: the vc-deck-review skill (preview).
  - The story, the one-liner and the say-and-avoid list: the vc-positioning skill.
  - The ask's arithmetic (valuation, ownership, runway): the vc-deal-math skill. One scenario on its own: the
    equity-calculator skill.
  - Traction metrics beside the market (ARR, retention, churn, CAC payback, burn multiple): the vc-metrics-readiness
    skill (preview).
  - How much to raise and what each amount reaches: the vc-round-sizing skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess, never look anything up, and never fill a
gap with a typical figure.

1. **Who buys, as segments** (one to eight): the buying customer (a clinic, a household, a store), how many there
   are, and where that count comes from. Segments must not overlap: one buyer in one segment only.
2. **What each pays:** the price, the period it covers (a month, a year, or a device's life in months), units per
   customer if priced per seat or location, and for a marketplace or payments business the share of the spend the
   company keeps. Where the price comes from: what customers pay today, a pricing test, or the plan.
3. **Who the product can serve today:** the share of each segment it can serve and reach now (geography, the systems
   it works with, the channel), and why.
4. **What you plan to win, and by when:** per segment, the number of customers (preferred) or a share of the
   serviceable ones, the horizon in years, customers today, and how you will reach them (channel, sales capacity).
5. **Optional:** any top-down figure with its publisher, year and definition, and the share of it that matches your
   definition; the total population the segments come from, in the same buying unit; annual revenue today; the
   revenue your plan needs from this market by the horizon; and the deck's stated TAM, SAM and SOM, word for word.

A missing input becomes a named gap, written as a bracketed ask: `[the channel that reaches multi-site groups]`.

## The assumption ledger

Every input is one row: Segment, Assumption, Value (quoted as the founder states it), Founder's source, Kind. The
kind is the first that applies, in this order: **Own data**, then **Named third party**, then **Estimate**. Each
segment with a SOM has its own Horizon row: `<N> years (founder's)` when the founder gave that segment a year, or
`<N> years (the call's one horizon; the founder gave none for this segment)`, with the ask step 3 gives.

| Kind              | When                                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| Own data          | The founder's records: customers paying today, signed prices, a pricing test, a count built from a list they hold |
| Named third party | A publisher, a year and a definition the founder can show (a registry, a census table, an analyst report)         |
| Estimate          | The founder's judgment, or a source with no publisher or year                                                     |

The kinds are this skill's own grouping (unverified). The skill never upgrades a row: a figure with no publisher stays
an Estimate. It never describes a source the founder did not name.

## Steps

With a subagent tool (in Claude Code, the Agent or Task tool), step 8 runs the three lenses as subagents launched in
one message, however short the material, then one refute subagent per objection, as "How to run the lenses" says.
Without a subagent tool, run the three lenses (Adversarial review) in the turn that makes the call, before the ledger
and the call, on all the founder's material so far (every message, not only the first), as "How to run the lenses"
says. A turn that makes no call runs no review.

1. **Quote first.** List every market line in the founder's material word for word, with its place (slide, page):
   sizes, counts, prices, shares, "1% of", sources.
2. **A top-down-only size.** If the material has only an analyst figure or a share of one, say it matches the first
   pattern below, and ask for the bottom-up inputs. Make no call until there is at least one segment: stop after the
   ask, run neither the review nor the call, and wait for the founder's answers.
3. **Ask for what is missing** (Inputs), in one message. With at least one segment in, the call runs on what is there
   and each missing input stays a bracketed ask in the answer. For each Estimate row on a figure that moves its
   segment's SOM (at most three), and for any assumption the founder asks about ("what if our price is lower?"), also
   ask for a low and a high value: the founder's numbers, never a percentage the skill picks. The tool varies seven
   segment fields: `customers`, `price`, `units_per_customer`, `take_rate_percent`, `serviceable_percent`,
   `obtainable_percent` and `obtainable_customers`. Where a segment's SOM is a count of customers, its `customers` and
   `serviceable_percent` do not move the SOM; where a segment has no SOM, none of its fields does. An Estimate on any
   other figure (a top-down figure, the horizon, the population, customers today) gets an ask for its source, never
   for a range. When the founder gives none, the call still runs and that Estimate stays a bracketed ask for its
   range. An assumption shared by several segments (one fee, one price) gets one row per segment: the tool moves one
   segment at a time, so no single row is quoted as the whole company's case. One horizon (`som_years`) covers every
   segment: when the founder gave a year for some segments only, the ledger says so and the answer asks
   `[the year you expect to win that segment's customers]`.

   **What one call takes:** at most 8 segments, 3 top-down figures and 6 sensitivity rows of at most 4 values each.
   When the rows above come to more than 6, keep them in this order: the Estimate rows first, then the rows for an
   assumption of one segment the founder asked about, then a shared assumption's rows, segment by segment. Name every
   row left out in the answer; its range stays a bracketed ask, and a shared assumption the founder asked about is
   still answered by the whole-company runs in step 5.

4. **Build the ledger.**
5. **Call `equity_market_sizing` once,** with every segment, top-down figure, sensitivity row and stated figure; the
   only other calls are the whole-company runs below. Send money and percents as strings, and `price_period_months`,
   `som_years` and a sensitivity row's `segment` as whole numbers, never strings. Always send `price_period_months`
   (1 for a monthly price, 12 for a yearly one): left out, the tool reads the price as yearly and raises
   `price_period_defaulted`. Company AW (made up), software for vet clinics:

   ```json
   {
     "inputs": {
       "segments": [
         {
           "customers": "18000",
           "price": "400",
           "price_period_months": 1,
           "serviceable_percent": "60",
           "obtainable_customers": "900",
           "customers_today": "45"
         },
         {
           "customers": "400",
           "price": "300",
           "price_period_months": 1,
           "units_per_customer": "15",
           "serviceable_percent": "50",
           "obtainable_percent": "10",
           "customers_today": "2"
         }
       ],
       "top_down": [{ "amount": "2100000000", "comparable_percent": "40" }],
       "sensitivity": [
         { "field": "price", "segment": 1, "values": ["300", "500"] },
         {
           "field": "obtainable_customers",
           "segment": 1,
           "values": ["600", "1200"]
         },
         { "field": "obtainable_percent", "segment": 2, "values": ["5", "15"] }
       ],
       "annual_revenue_today": "324000",
       "som_years": 5,
       "som_target": "8000000",
       "stated_tam": "120000000"
     }
   }
   ```

   The same call from the command line:

   ```
   equity_calculator market_sizing --segment "customers=18000 price=400 price-period-months=1 serviceable-percent=60 obtainable-customers=900 customers-today=45" --segment "customers=400 price=300 price-period-months=1 units-per-customer=15 serviceable-percent=50 obtainable-percent=10 customers-today=2" --top-down "amount=2100000000 comparable-percent=40" --sensitivity "field=price segment=1 values=300/500" --sensitivity "field=obtainable-customers segment=1 values=600/1200" --sensitivity "field=obtainable-percent segment=2 values=5/15" --annual-revenue-today 324000 --som-years 5 --som-target 8000000 --stated-tam 120000000
   ```

   Part of what it prints:

   ```text
     Total gross spend (before the take rate)                                 $108,000,000.00  sum of the segments
     Total TAM                                                                $108,000,000.00  sum of the segments
     Total SAM                                                                 $62,640,000.00  sum of the segments
     Total SOM                                                                  $5,400,000.00  sum of the segments
     Top-down 1: bottom-up as a share of it                                          12.8571%  bottom-up TAM / comparable part (a cross-check)
     TAM: the deck says                                                       $120,000,000.00  given
     TAM: difference                                                          $-12,000,000.00  computed - stated
     TAM: verdict                                                                    mismatch  within the tolerance is consistent
     Sensitivity 1: SOM swing                                                   $2,160,000.00  SOM high - SOM low
     Sensitivity 1: segment 1 price at SOM = $8,000,000.00                            $640.74  base × (target - other segments' SOM) / this segment's SOM
     Sensitivity 2: SOM swing                                                   $2,880,000.00  SOM high - SOM low
     Sensitivity 2: segment 1 customers to win at SOM = $8,000,000.00                1,441.67  base × (target - other segments' SOM) / this segment's SOM
     Sensitivity 3: SOM swing                                                   $1,080,000.00  SOM high - SOM low
     A VC is likely to ask                                                som_as_percent_only  A SOM is given as a share of the serviceable customers, not as a count of customers; a VC is likely to ask for the customers, the channel and the year behind it
     A VC is likely to ask                                                   som_below_target  The SOM total is below the revenue the plan needs from this market; a VC is likely to ask where the rest comes from
   ```

   The deck's $120M TAM does not match the $108,000,000.00 its own inputs give, the SOM is below what the plan needs,
   the groups' SOM rests on a share (`som_as_percent_only`), and of the three rows the 900 clinics (an Estimate in
   eval AW's ledger) swing the SOM most.

   **The whole-company case.** When the founder asks about an assumption shared by several segments as a whole ("what
   if our fee is 10% or 20%?"), make one more call for each value they give: the same inputs, with that value in every
   segment that shares the assumption and no sensitivity rows. Quote only that run's Total TAM, SAM and SOM, as the
   whole-company case at that value: tool values, not arithmetic. Its flags, checks and top-down share are not new
   findings, and no difference between two runs is worked out by hand.

   A refusal or tool error is the answer for those inputs: relay its reason, fix what it names (a list over the limits
   in step 3, a whole number sent as a string) and call again. Never work the figures by hand instead.

6. **Read the result:** per segment and in total, gross spend, TAM, SAM and SOM (money and customers), each segment's
   share of TAM, the path per segment (`som_multiple_of_today`, `new_customers_per_year`), the top-down rows, the
   checks, the flags, and each sensitivity row's swing and break-even values. A break-even value against the top-down
   figure is a cross-check, never a target: never offer it as a price, a count or a share to aim for. A value at the
   SOM target is what the plan would need from that one field with the rest at base, never a recommendation either:
   quote it beside the founder's own low and high values, and when it is above their high value, say so with the
   row's SOM high beside the target: even at the founder's own best case, that assumption alone does not reach the
   plan. A top-down figure sent with no `comparable_percent` is compared in full: the tool reads the share that
   matches the founder's definition as 100% and prints it as given. Say the founder gave no share, so the bottom-up
   share and the difference are against the whole figure, and keep
   `[the share of the figure that matches your definition]` as an open ask.
7. **Name the shakiest assumption:** among the ledger rows of the weakest kind present whose sensitivity row has a
   `som_swing` above $0.00, the one with the largest `som_swing` in the result (the swing runs over the founder's
   values and the base). Quote its swing and its value at the SOM target beside the founder's high value, as step 6
   says. When the reach is `met_without_it`, also quote its `som_low` beside the target, so the founder sees whether
   their own low value still reaches the plan. That is a comparison of tool values, not a calculation. When no row of
   that kind has a sensitivity row, name none: the ask for its low and high values stands. When that kind's rows all
   swing by $0.00 or have no swing, name none and say why: the field does not move that segment's SOM
   (`does_not_move`), or no SOM is totalled (`som_not_given`). A shared assumption's rows move one segment each: when
   one is named, say so, and point to the whole-company runs for the company as a whole. Then, in one line, give each
   other sensitivity row's kind and swing and why it was not picked: a stronger kind (an Own data price is never a
   candidate while an Estimate is in play), or a smaller swing.
8. **Run the adversarial review** (below).
9. **Check before answering.** Every figure is quoted as stated or comes from a tool result; every objection quotes a
   founder line word for word; no market fact, source or competitor is brought in; nothing speaks as an investor; with
   a subagent tool, the number of refute subagents equals the number of objections that passed the quote check, each
   given exactly one; no reason for a top-down gap is offered except as a question.

Tool values: use each value's `rounded` with its unit; never round again or recompute. A `fraction` value is shown as
a percent by moving its decimal point two places right, keeping every digit (0.580000 is 58.0000%); a change of
notation, not a calculation. Never convert a monthly price to a year, apply a take rate, total segments, work out a
share of a market or a growth rate by hand: the tool gives each.

## Adversarial review

The tool says what the founder's inputs add up to. A partner also asks whether the inputs are the right ones. Three
lenses attack the market story; a refute pass keeps an objection only when the founder's material grounds it.

### Stage A: attack

Each lens tests one thing and is named by it; none is a person or a firm.

| Lens      | What it tests                                                                                                                                                                                                  |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inflation | Whether the number is revenue this company can earn from buyers who have the problem: no top-down or "1% of" size, no whole category counted, no gross spend counted for a fee business, a price customers pay |
| Path      | Whether the SOM rests on customers, a channel and a year, rather than a share picked with nothing behind it                                                                                                    |
| Overlap   | Whether a buyer or a dollar is counted twice: nested or overlapping segments, seats and companies both, both sides of one marketplace                                                                          |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to doubt
  this because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here and the pattern list. Bring in no outside fact about the market, the
  customers or the competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the founder's line, quoted word for word with its
  place; why a partner is likely to doubt it; and how much it hurts (ends the meeting, weakens it, or minor).
- A doubt you cannot tie to a line the founder wrote is not an objection: list it apart as a question to the founder.
- Do not judge whether another line of the material answers an objection: raise it anyway, however short the
  material; the refute pass decides. Return "nothing found" only when no line of the material gives this lens an objection worth a partner's
  time.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the three lenses as
parallel subagents, however short the material, all launched in one message, each given only the founder's material, its brief and the Pattern column below: never the tool's
result. Without one, run them in the turn that makes the call, before the call, one after another, on all the
founder's material so far (every message, not only the first), writing each lens's objections down in full before
reading the next brief, and never revising them after the tool results are in. A turn that makes no call runs no
review. Lenses run that way are less independent than subagents; say in the answer which way they ran.

**Computed findings do not go through the lenses or the refute pass.** Each check mismatch and each flag is a
computed fact, added to the survivors as is, quoting the founder's line it bears on with the tool's values as the
reason. A mismatch on a stated TAM, SAM or SOM heads the list, ahead of the tiers, with no tier: how much a gap hurts
depends on its size, which the founder weighs. The flags take the tier the Flags table gives.
A lens objection on the same line as a flag joins the flag's entry, keeping the lens name.

### Check the quotes

Drop any objection whose quoted line is not in the founder's material word for word (spacing aside) as not grounded.
Merge two lenses' objections on the same line, keeping both names. Questions go to the open asks.

### Stage B: refute

Each objection gets its own pass. With a subagent tool, N objections after the quote check means N subagents: launch
one subagent per objection in a single message; never put two objections in one subagent. Give each only the
founder's material, that objection, the Pattern column below and the brief, and add no rule of your own to the brief.
Without one, decide them one at a time against the same brief.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third
  person; you are not an investor and do not speak as one, named or not.
- Use only the founder's material. Bring in no outside fact about the market, and do no arithmetic.
- A line that itself matches a pattern in the list never answers an objection.
- Return one verdict, quoting the founder's line word for word where it needs one. When you cannot decide, return
  Kept.

The verdicts:

- **Dropped, answered:** a line of the material other than the objected line supplies what the objection says is
  missing (a source with its publisher and year, a customer count, a channel, a horizon). Quote it; say whether it
  should move onto the market slide.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact about the market.
- **Kept:** neither holds. What the founder would need becomes a bracketed ask.

What is missing is what the objection's pattern names in its Fix column, nothing more. A line that supplies all of it
drops the objection as answered; anything else the lens asked for (closes per rep, a hiring plan) goes to the open
asks as a question and does not keep it. A line that supplies only part of it (a channel but no year) does not drop
it: the objection is Kept for the part left, the answering line is quoted with the advice to put it on the market
slide, and the part left becomes the bracketed ask.

The pass invents nothing on the founder's behalf: no figure, source, customer or channel. After the passes, an
answering line that is not in the material word for word does not drop the objection, and neither does one that is the
objected line itself.

### Rank what survives

Three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**. Within a tier, an objection raised
by more than one lens comes first. The tier is a judgment: no percentages and no score. For each survivor: the line
quoted, why a partner is likely to read it that way, and the fix in the founder's facts or a bracketed ask.

### Patterns

Signals, not rules. A row marked unverified has no public source this skill's authors read; say so when you use it.

| Pattern                                                                           | Lens      | Fix                                                                                      | Source                                                                                                                                                         |
| --------------------------------------------------------------------------------- | --------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A market size from an analyst figure only, or "if we get 1% of it"                | Inflation | Build it bottom-up: who buys, how many, what each pays; the figure only as a cross-check | YC seven questions (2), the top-down pitfall; YC seed fundraising guide (its DON'T list: "ridiculous / silly market size numbers without clear justification") |
| Every buyer in a broad category counted                                           | Inflation | Count only the buyers who have the problem, and say how they were counted                | YC seven questions (2) ("assuming all women are in your market")                                                                                               |
| Total spend or GMV counted as the market of a company that keeps a fee            | Inflation | Give the take rate; the market is the revenue the company keeps                          | YC seed fundraising guide (glossary: TAM is "the estimated total revenue available for the product(s) you are selling")                                        |
| A one-off purchase priced as if bought every year                                 | Inflation | Give the months the price covers                                                         | YC seven questions (2) (the activity tracker's two-year "lifecycle")                                                                                           |
| A price no customer pays yet                                                      | Inflation | Use what customers pay today, or show the pricing test                                   | Unverified                                                                                                                                                     |
| A market size with no publisher or year, or figures from different years mixed    | Inflation | Name the publisher, year and definition, or drop it                                      | Unverified                                                                                                                                                     |
| A SOM given only as a share, with no customers, channel or year                   | Path      | The customers you plan to win, by when, and through which channel                        | Unverified                                                                                                                                                     |
| A SOM many times today's customers with nothing named to get there                | Path      | Name the channel behind the tool's new customers a year; its capacity is a question      | Unverified                                                                                                                                                     |
| Segments that overlap, or add up to more than the population they come from       | Overlap   | Cut the segments so no buyer is in two; give the population                              | Unverified                                                                                                                                                     |
| The same buyer counted per seat and per company, or both sides of one marketplace | Overlap   | Count each buyer once, at the level that pays                                            | Unverified                                                                                                                                                     |
| A bottom-up figure above the top-down figure it is compared with                  | Overlap   | Find the double count, or show why the definitions differ                                | Unverified                                                                                                                                                     |

## Flags

The result's `flags` holds codes only; over MCP no sentence comes with them (the command line prints one beside each),
so this table is what each means. A flag is a question to prepare for and never changes a verdict.

| Flag                         | What it means for the founder                                                                  | Tier             |
| ---------------------------- | ---------------------------------------------------------------------------------------------- | ---------------- |
| `price_period_defaulted`     | A price was sent with no months, so it was read as yearly: ask for the months and run it again | weakens it       |
| `segments_exceed_population` | The segments add up to more customers than the population you gave: a double count             | ends the meeting |
| `bottom_up_above_top_down`   | Your bottom-up figure is above the top-down figure you compared it with                        | ends the meeting |
| `sam_equals_tam`             | No segment is narrowed to the customers you can serve today                                    | minor            |
| `som_not_given`              | A segment has no customers to win, so the SOM is not totalled                                  | minor            |
| `som_as_percent_only`        | A SOM rests on a share, not a number of customers                                              | weakens it       |
| `som_from_zero_customers`    | A segment's SOM starts from no customers today                                                 | minor            |
| `som_below_customers_today`  | A segment's SOM is fewer customers than you have today                                         | minor            |
| `no_horizon_given`           | A SOM has no year by which it is won                                                           | minor            |
| `som_below_target`           | The SOM is below the revenue your own plan needs from this market                              | weakens it       |
| `som_target_out_of_reach`    | No sensitivity row you gave reaches your plan's revenue at a value its segment can take        | minor            |

The tiers are this skill's own ranking (unverified). A survivor from the lenses can still outrank a flag. The fix for
`som_as_percent_only` is always the three asks `[the number of <buyers> you plan to win]`,
`[the channel that reaches them]` and `[the year you expect to win them]`, with the segment's buyers named.

## Answering

Lead with what a partner will doubt first, then the numbers.

1. **Doubted first:** the computed findings (mismatches with no tier, then flags by tier), then the kept objections in
   their tiers, each with the line quoted, its lens or lenses in brackets after the quote ("(Path)", "(Inflation,
   Overlap)"), why, and the fix. Then **Dropped,** one line each with why it fell. Say whether the lenses ran as
   subagents, and give the number of refute subagents run.
2. **The market:** a table per segment and in total: Customers, Gross spend, TAM, SAM, SOM, Share of TAM, SOM
   customers / today, New customers a year. Tool values only. Each whole-company run's totals follow, labelled with
   its value.
3. **Against the deck,** its own section: each stated TAM, SAM or SOM, the tool's figure, the difference and the
   verdict. Beside a stated TAM, always give the tool's total gross spend, both quoted, and say whether the gap could
   be a gross-spend count: with no take rate the two figures are the same, so it cannot.
4. **Against the top-down figure:** the tool's share and difference only, as a cross-check, never as the market size;
   with no share given, say it is against the whole figure. Any reason for the gap is a question to the founder under
   Open asks, never a statement.
5. **The shakiest assumption:** the ledger row, its kind, its swing, and its value at the SOM target beside the
   founder's high value (or the tool's `met_without_it` with its `som_low` beside the target, `does_not_move` or
   `out_of_range`), quoted; or none, with why. Then the one line on each other row's kind and swing (step 7).
6. **The ledger:** every assumption with its source and kind.
7. **Assumptions** the tool's result lists, quoted with their sources.
8. **Open asks:** every bracketed gap, every sensitivity row left out, and every question from the lenses, in one
   list.
9. **Sources,** and which points rest on an unverified source.
10. **Close:** this is not investment, legal or tax advice; the market size is only as good as the founder's
    sources, and a partner will ask to see them.

## Sources

- Y Combinator, "How to Pitch Your Company" (Michael Seibel), read in full:
  https://www.ycombinator.com/library/4b-how-to-pitch-your-company
  Question 2, "How big is the market?": estimate "the number of customers that would want your product and
  approximate how much you could charge them"; "I prefer the bottom up method because it helps you avoid a common top
  down pitfall, which is not narrowing down the customer enough"; the activity tracker example and its two-year
  lifecycle.
- Y Combinator, "A guide to seed fundraising" (Geoff Ralston), read in full:
  https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising
  Its DON'T list ("Use ridiculous / silly market size numbers without clear justification") and its glossary (TAM is
  "the estimated total revenue available for the product(s) you are selling").
- Sequoia Capital, "Writing a Business Plan", read in full: https://www.sequoiacap.com/article/writing-a-business-plan/
  Its "Market potential" line ("Identify your customer and your market."), a framework line only.

Neither YC page carries a date; say so when a founder leans on one. All three were read in full by this skill's
authors. Neither YC page defines SAM or SOM: those definitions, the source kinds, the lens names, the flag tiers and
every row marked unverified are this skill's own.

## Limits

- Not investment, legal or tax advice. It says what the founder's inputs add up to and what a partner is likely to
  doubt, not whether the market is real or big enough for any investor.
- It never looks up, invents or suggests a market figure, customer count, price, share, adoption rate, horizon or
  population: no default price and no "industry average". A gap stays a bracketed ask.
- It never turns a top-down figure into a market size, never works out "1% of" anything, and never suggests widening
  the market to make a number bigger.
- No arithmetic outside the equity calculator's tools; no compound growth rate; no fund or exit math.
- It never role-plays or speaks as a named investor, firm or author, and gives no score.
- Each figure is one year of revenue at today's prices: no growth, churn or price change. Say so beside the results.
- The review predicts what a partner is likely to doubt; a real partner may doubt other things.
- It works from the founder's text and sends nothing anywhere.
