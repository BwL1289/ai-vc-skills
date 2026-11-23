---
name: vc-current-investor-update
description: Helps a founder write the monthly or quarterly update they send their current investors, so it builds the trust the next raise needs. It drafts or reviews the update in one fixed shape (a short summary, the same metrics with the same definitions every time, highlights, lowlights told straight, asks, cash and runway, the next period), ties every figure and promise out to the last update as stated, never recomputed, and checks the runway claim with the calculator's runway_plan tool. An adversarial reader pass has independent lenses flag spin, missing bad news, changed metric definitions and figures that do not tie out, and a refute pass drops what the founder's own material answers. Use when a founder says write my investor update, review my investor update before I send it, draft our monthly update, how do I tell investors about a bad month, or should I skip this month's update. Never invents or hides numbers. Not investment advice.
---

# VC current investor update

Helps a founder write the regular update they send to the investors who already own part of the company. An update
sent every month or quarter, good or bad, in the same shape and with the same definitions, is the record those
investors read when the next round comes: did the numbers keep their meaning, did the bad months get reported, did
last period's "next month" happen? This skill drafts the update from the founder's own material, or reviews a draft
they paste. It ties every figure and promise out to the last update word for word, checks the runway claim with the
equity calculator, and runs a reader pass that flags spin, missing bad news, changed definitions and figures that do
not tie out. Then a refute pass drops each flag the founder's own material answers.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
adds a figure, customer or event the founder did not give, and never leaves out bad news the founder gave it.

## When to use it

- "Write my investor update." "Review my investor update before I send it." "Draft our monthly update." "How do I
  tell investors about a bad month?" "Should I skip this month's update?" "Write our Q3 investor update."
- Pasted material: the last update, this period's notes, a metrics table, a cash and burn figure, a draft update.
- A founder who wants to skip a bad month: the sources below say to send it anyway (stopping is itself read as a
  warning). Say so once, then write the update.
- Built for the founder's current investors: people who already hold shares, SAFEs or notes in the company.
- Hand off:
  - Each claim's evidence across several documents (a deck sent with the update, a one-pager): the vc-claims-check
    skill.
  - A raise that closed in the period (ownership, the SAFE stack, the pool): the vc-deal-math skill, or the
    equity-calculator skill for one scenario on its own.
  - The story for the coming raise and the say-and-avoid list: the vc-positioning skill.
  - How much to raise next and which milestone it buys: the vc-round-sizing skill (preview).
  - Whether a metric's definition is the one investors expect, and ARR, retention, churn, CAC payback or burn multiple
    checked from their parts: the vc-metrics-readiness skill (preview).
  - The short update a founder sends prospective investors before a raise, cut from this one when both go out in the
    same period: the vc-prospective-investor-update skill (preview). This skill's runway call carries no raise and no
    milestone, and it writes no version for people who are not yet investors.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. The last update, word for word, with its date and period; or "this is the first one".
2. What happened this period, in the founder's notes: what went right, what went wrong, what slipped, who left,
   which customers were won or lost, what the last update said would happen next and what did.
3. Each metric: its name, its definition (what counts, and whether it is gross or net, cumulative or per period), its
   period, this period's value, and the value the last update gave for the same metric.
4. Cash on hand and its date; monthly spend (gross burn) and revenue today; and any planned change, as phases ("from
   month 4, $120,000 spend and $30,000 revenue"), counting the month after the cash date as month 1. The runway claim,
   if the founder makes one. Optionally, how many months the founder expects the next raise to take.
5. The asks: who or what, and why.
6. Monthly or quarterly, and anything in the founder's notes that is not for investors at all (a personal matter, a
   customer who has not agreed to be named).

A missing input never stops the work. It becomes a bracketed ask in the draft (`[cash on hand on 31 October]`),
never a plausible figure. A customer who has not agreed to be named stays in as an unnamed description ("our biggest
customer", "a regional grocer"); the event and its figures are kept.

## The update's shape

Bullet points, short lines, the same sections in the same order every time.

| Section         | What it holds                                                                                    | Source                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Summary         | Two or three sentences: was the period good, bad or in between, and the takeaway                 | Mercury guide (introduction)                                                                              |
| Metrics         | The same few metrics every time, each with its definition and period, last value beside this one | Mercury guide (performance); 500 Global guide (key updates); last value beside this one: ours, unverified |
| Highlights      | What went right, with the figure or the name the founder gave                                    | Mercury guide; 500 Global guide                                                                           |
| Lowlights       | What went wrong, slipped or was lost, said plainly, with what the founder is doing about it      | Mercury guide; 500 Global guide                                                                           |
| Asks            | Specific introductions or help: who, and why                                                     | Mercury guide (asks)                                                                                      |
| Cash and runway | Cash on hand with its date, monthly spend and revenue, runway from the calculator                | Mercury guide; 500 Global guide (cash in bank)                                                            |
| Next period     | What is happening next, not a forecast of metrics                                                | Mercury guide (next month)                                                                                |
| Thanks          | Optional: investors who helped since the last update, by name only if they agree                 | 500 Global guide                                                                                          |
| Definitions     | Every metric's definition, word for word the same each time; a change says so                    | Ours; a16z "16 Startup Metrics" (9)                                                                       |

Keep the founder's words where they are clear. The Definitions block is this skill's own addition, unverified: it
makes the next update's tie-out possible. A founder who asks to leave a section out, cash and runway included, hears
once that the update keeps the same sections every time; the section stays, with bracketed asks for what is missing.

## Metrics and tying out to the last update

The rules for metrics and their definitions, the six status words for tying each metric out to the last update, the
Definitions block and the figures no tool here checks live in one file this skill keeps:
[`references/metric-consistency.md`](references/metric-consistency.md). Read it before step 3. The
vc-prospective-investor-update skill reads the same file, so the two updates keep their metrics the same way. In short:
the same metrics with the same definitions every time; each metric set beside the last update's as stated, with one
status, compared as written and never computed; every figure no tool computes quoted as stated, unchecked.

What the draft does for each status:

- **Same:** nothing; a new period's value sits beside the last one.
- **Restated:** says so beside the figure, with the reason (`[why it changed]`).
- **Different form:** states one form, the last update's; asks for the figure, or how the two lines relate.
- **Changed definition:** announces the change, as the rules file says.
- **Dropped:** puts it back, or says it is dropped and why.
- **New:** gives its definition.

The last update's own promises are tied out too: each "next month" item, target or open lowlight in it gets a line in
this update saying what happened, in the founder's words, or a bracketed ask. Its status in the tie-out table follows
the founder's notes, never this skill's judgment: Done, Partly done, Not done, Moved (back with a later date, a lower
figure or a narrower scope) or No word (the founder's draft does not mention it). The runway row's status is the
calculator's verdict word, or the floor rule's result (Runway).

A first update has nothing to tie out: every metric is New, there are no promises to check, and its Definitions
block is the one the next update ties out to.

## Steps

With a subagent tool (the Agent or Task tool), the reader pass runs as subagents, however short the material: one per
lens, then one per objection. In review mode without a subagent tool, run Stage A of the reader pass first, before step
1, as "How to run the lenses" says; step 8 then starts at the quote check.

The reader pass judges the draft before this skill changes it. In review mode, both its stages read the founder's
draft as given, never the revised one: a line this skill adds at step 7 answers no objection. In draft mode, they read
the draft written at step 7.

1. **Quote first.** List, word for word with their sections, every figure, promise and target in the last update,
   and every figure and event in this period's material and in any draft.
2. **Ask for what is missing,** once, in one message (Inputs above).
3. **Build the metric list** in the last update's order: name, definition, form, period, the last update's value,
   this period's value.
4. **Tie out** each metric and each promise (the section above), and the runway claim against the runway the last
   update gave, compared as written (Runway).
5. **Runway:** call `equity_runway_plan` (next section).
6. **Other figures:** quote each as stated, with its line from the rules file's "Not checked here": ARR, retention,
   churn, CAC payback and burn multiple go to the vc-metrics-readiness skill; the rest are "not checked: no tool
   computes this".
7. **Draft or revise.** Draft mode: write the update in the shape above from the founder's material only, every gap a
   bracketed ask; the period is labelled as the founder gives it (`[year]` when no year is given). Review mode: keep the
   founder's draft and words; change only what a status, the calculator or a kept finding requires. Either way, a
   definition or lowlight the founder did not give is a bracketed ask (`[runway definition]`), never this skill's words.
8. **Run the reader pass** (below) on the draft it judges (the founder's draft as given in review mode): attack,
   check the quotes, refute, rank. Revise the draft for every kept finding, using only the founder's facts or a
   bracketed ask.
9. **Check before answering.** Every figure is quoted as stated or comes from a tool; every lowlight the founder gave is
   in the draft; no metric the last update reported is silently gone; no sentence speaks as an investor or names a firm
   as a voice; nothing is sent anywhere. Never work out how two of the founder's figures relate (a difference, a sum, a
   ratio or multiple, a share left over, "doubled") in a rewrite, a line or a table cell unless the founder's material
   states it or a tool returned it; quote both figures as stated instead ("from 2,000 to 4,500", never "more than
   doubled").

## Runway

The runway claim goes to `equity_runway_plan` (from the command line, `equity_calculator runway_plan`), as the
founder's plan with no raise:

- `cash_on_hand`: cash at the update's date. Money as strings.
- One `plan` case: the first phase is today's monthly spend (`gross_burn`) and `revenue`, from month 1 (the month
  after the cash date); each planned change is another phase, from its month. When the founder gives cash collected
  rather than revenue, pass that and say so. When the founder gives only net burn, ask for spend and revenue; until
  then, pass the net burn as `gross_burn` with `revenue` `"0"`, and label the line as net burn in the update. A net
  burn of zero or less gets no call until spend and revenue are given (the tool refuses a `gross_burn` of 0 or less);
  meanwhile quote the founder's words.
- `stated_runway_months`: the runway the update states, when it states one; a "30+ months" claim is passed as
  `"30"`. With no claim, call without it and put the tool's runway in the update.
- `months_to_raise`, only when the founder gives how long the next raise will take: a whole number, as a JSON integer,
  never a string. A range ("4 to 6 months") is asked about once; until answered, pass the upper figure and say so. The
  tool then prints, in the "Start raising by" row, how many months from the cash date the raise has to start by.
- No `raises` and no `milestones`: sizing the next round is not this skill's job.
- One call for the update. When the plan changes the burn and the claim does not hold (below), call once more with
  today's spend and revenue as the only phase, so the answer can say which burn the claim used. The tool names that
  case `plan` too; the answer calls it "today's spend held flat". Make no other call the founder did not ask for.

**A claim stated as a floor** ("30+ months", "over 30 months", "at least 30 months") is passed as its number, but the
tool's verdict row does not decide it: the tool calls a figure within its tolerance either way consistent. Compare the
tool's printed runway with that number as written, saying only which is larger. A printed runway at or above the number
keeps the claim: the update may keep it or state the printed runway, and it goes in no tier. A printed runway below the
number is a fix before sending, even when the verdict row says consistent.

```json
{
  "inputs": {
    "cash_on_hand": "1100000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "95000", "revenue": "22000" },
          { "from_month": 4, "gross_burn": "120000", "revenue": "30000" }
        ]
      }
    ],
    "stated_runway_months": "15"
  }
}
```

The same check from the command line:

```
equity_calculator runway_plan --cash-on-hand 1100000 --phase "from-month=1 gross-burn=95000 revenue=22000" --phase "from-month=4 gross-burn=120000 revenue=30000" --stated-runway-months 15
```

Part of what it prints (Company AG, made up: $1,100,000 in the bank, $95,000 spend and $22,000 revenue a month today,
$120,000 and $30,000 from month 4 after two hires, and "Runway: 15 months" in the update):

```text
  Runway, plan, no raise                           12.79 months  months until cash less the floor goes below zero
  Runway, no raise: stated                         15.00 months  given
  Runway, no raise: the calculator gives           12.79 months  the plan case's runway
  Runway, no raise: difference                     -2.21 months  computed - stated
  Runway, no raise: verdict                            mismatch  within the tolerance is consistent
```

The 15 months does not hold on the plan. Run once more with today's spend held flat, and the update can say both:
the plan's runway, and today's, each as the tool prints it.

Read every row, the `flags` and the `assumptions` before answering. Use the printed values (12.79 months stays 12.79
months, never "about 13"); never round again or recompute. A refusal is the answer for those inputs: relay its reason.
A mismatch on an exact claim is a figure to fix before sending, never softened, when the claim is above the printed
runway: the draft states the printed runway. A mismatch with the claim below the printed runway understates it: the
update may keep it or state the printed runway, and it goes in the minor tier at most. An exact claim the verdict row
calls consistent may stay as the founder wrote it, and the Numbers section gives the printed runway. A claim stated as a
floor follows the rule above instead.

**The same runway two updates running.** When the runway the update states is the figure the last update gave, the
runway's entry in the ranked fix list names the pattern "The same runway figure two updates running" (Patterns that
cost trust) and says it is unverified: the mismatch's entry, or, when the claim holds, its own entry in the worth fixing
tier, whose fix is the printed runway.

| Flag                        | What it means for the founder                                                         | What the update does                                                    |
| --------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `cash_never_runs_out`       | Revenue covers the spend before the cash runs out, so the runway has no end           | Says so instead of a runway figure; a stated runway is not checked      |
| `start_raising_date_passed` | With the months to raise given, the date to start raising is already at or past today | Says the next raise should already be under way, and what is being done |

With no raise and no milestone in the call, the tool raises no other flag.

## Reader pass (adversarial review)

The tie-out catches what can be matched line by line. This pass reads the draft the way an investor holding the last
update will, and finds what would cost the founder trust. Independent lenses attack the draft, a refute pass judges
each objection using only the founder's material, and only what that material does not answer reaches the founder.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people.

| Lens             | What it tests                                                                                                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spin             | A summary, highlight or label that reads better than the facts under it: adjectives with no figure, a percent with no figures, a cumulative total, a plan written as a result, a lowlight framed as a highlight |
| Missing bad news | A fact in the founder's material that the draft leaves out or buries: a loss, a slip, a departure, a metric lower than last time, a promise or target from the last update with no word now                     |
| Definitions      | A metric whose label, definition, form or period differs from the last update's or has none; a metric dropped                                                                                                   |
| Tie-out          | The same metric, in the same form, for the same period, stated differently between the last update and the draft, or in two places in the draft                                                                 |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("an investor holding the last
  update is likely to notice ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here: the last update, this period's notes, and the draft. Bring in no
  outside fact about the company, its market or its customers, and do no arithmetic. Saying that one stated figure is
  larger than another is allowed; working out by how much is not. Figures under different labels or definitions are
  never set side by side, not even as larger or smaller: say only that the label or definition changed.
- Return at most three objections, strongest first. For each: the draft's line it is about (or, for something left
  out, the material's line the draft omits), quoted word for word with its place; why an investor is likely to read
  it as a reason to trust the founder less; and how much it costs (fix before sending, worth fixing, or minor).
- A reason you cannot tie to a line of the material is not an objection. List it apart as a question to the founder.
  Never turn an objection into a question because another line may answer it.
- Do not judge whether another line of the draft answers an objection: raise it anyway, and the refute pass decides.
  Return "nothing found" only when no line of the material gives this lens an objection worth an investor's time.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the four lenses as
parallel subagents, however short the material, each given only the founder's material, the draft it judges (Steps) and
its lens brief: not this skill's other sections, not the tie-out table, not another lens's output. Without one, in
review mode run the lenses before step 1, one after another, writing each lens's objections down in full before reading
the next brief. In draft mode the same agent wrote the draft, so the lenses run after step 7, still one after another.
Either way the answer says the lenses ran in one agent and are less independent than subagents.

**The calculator's mismatches** do not go through the lenses or the refute pass, and neither does a printed runway
below a claim stated as a floor. A mismatch is added to the ranked fix list ahead of the tiers, quoting the update's
figure with the tool's value as the reason. It carries no tier: how much a gap hurts depends on its size, which the
founder weighs. One with the claim below the printed runway goes in the minor tier at most. A printed runway below a
claim stated as a floor leads the first tier, quoting the update's figure with the tool's value.

### Check the quotes

Before Stage B, check every objection's quote against the founder's material and the draft. A quote that does not
appear there word for word (spacing and line breaks aside) is dropped as not grounded. Two lenses raising the same
objection about the same line merge, keeping both lens names. Questions go to the open asks.

### Stage B: refute

Each objection gets its own refute pass. With a subagent tool, launch one subagent per objection in a single message,
so they run in parallel; never put two objections in one subagent, and never judge them in the main agent instead. Give
each the founder's material, the draft, that one objection, the Pattern column of the table below, and everything from
"The refute brief:" to the end of this stage, and nothing else. Without a subagent tool, decide the objections one at a
time against the same brief.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third
  person; you are not an investor and do not speak as one, named or not.
- Use only the founder's material and the draft given here. Bring in no outside fact, and do no arithmetic. Figures
  under different labels or definitions are never compared, not even as larger or smaller.
- How an investor is likely to read a line is not an outside fact: judge whether the material answers that reading.
- A line that matches a pattern in the list you were given never answers an objection.
- Return one verdict from the three below, quoting the founder's line word for word where it needs one. When you
  cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the draft given here, other than the objected line, already says what the objection
  says is missing or hidden. Quote it. When it sits where an investor will not look first, say to move it up.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact.
- **Kept:** neither holds. When the fix needs something the material does not contain, it becomes a bracketed ask.

The refute pass invents nothing on the founder's behalf. An answering line that is not in the draft word for word, or is
the objected line itself, does not drop the objection. In review mode the draft given here is the founder's, as given: a
line this skill added at step 7 is not in it.

### The ranked fix list

Order the kept objections in three tiers: **fix before sending**, **worth fixing**, **minor**. The calculator's
mismatches lead the list ahead of the tiers, with no tier, though a mismatch with the claim below the printed runway is
minor at most (Runway). The first tier opens with a printed runway below a claim stated as a floor; a Restated or
Dropped status with no word in the draft goes in it too. So does a "next month" item, target or open lowlight from the
last update with no word in the founder's draft (review mode), even though the revised draft adds its line. Within a
tier, an objection raised by more than one lens comes first. The tier is a judgment: give no percentages and no score.
Each entry: the section, the line quoted, why an investor is likely to read it that way in one or two plain sentences
(figures under different definitions never set side by side), and the change, using only the founder's facts or a
bracketed ask. The draft is revised for every kept entry.

## Patterns that cost trust

Signals, not rules: a founder may have a reason. A row marked unverified has no public source behind it that this
skill's authors read; say so when it is used.

| Pattern                                                                                              | Why an investor is likely to discount it                                       | Fix                                                                       | Source                                                      |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | ----------------------------------------------------------- |
| A summary of adjectives ("another great month", "strong momentum") with no figure                    | Nothing to check, and it reads as hiding the facts                             | Say whether the period was good, bad or in between, and the key takeaways | Mercury guide (introduction); pattern and reason unverified |
| Highlights and no lowlights                                                                          | Investors assume something is being hidden                                     | The lowlights the founder gave, said plainly                              | Mercury guide (mistakes to avoid)                           |
| Updates that stop, or a bad month skipped                                                            | Silence is read as a warning that things are going badly                       | Send it, on the usual schedule, with the lowlights                        | Mercury guide (mistakes to avoid)                           |
| A metric from the last update missing now                                                            | The picture over time stops being consistent and predictable                   | Put it back, or say it is dropped and why                                 | Mercury guide (performance)                                 |
| "Active" or another metric with no definition, or a definition changed without notice                | Figures cannot be compared from one update to the next                         | Define it; announce any change with both values for the overlap period    | a16z "16 Startup Metrics" (9)                               |
| A percent change with no absolute figures                                                            | A percent off a small base sounds bigger than it is                            | Give both figures beside the percent                                      | a16z "16 Startup Metrics" (15)                              |
| A cumulative total in place of the period's figure                                                   | Cumulative figures rise even when the business shrinks                         | The period's figure                                                       | a16z "16 Startup Metrics" (14)                              |
| Bookings or letters of intent called revenue; one-time fees in recurring revenue; GMV called revenue | An inflated top line                                                           | Name each metric for what it is, with its own figure                      | a16z "16 Startup Metrics" (1, 2, 6)                         |
| Churn with no gross or net said                                                                      | Net churn blends upsells with losses and understates them                      | Say which, and keep it the same each time                                 | a16z "16 Startup Metrics" (11)                              |
| Burn with no gross or net said                                                                       | Gross and net burn differ; investors read how long the cash lasts off net burn | Say which, and keep it the same each time                                 | a16z "16 Startup Metrics" (12)                              |
| A growth rate with no method or period                                                               | A simple average and a compounded rate differ                                  | Name the method and the period; the rate stays the founder's              | a16z "16 Startup Metrics" (10)                              |
| A target or forecast written as a result, or forecasts in the next-period section                    | A promise that the next update will have to walk back                          | Results as results; the next period says what is happening, not metrics   | Mercury guide (next month); target as result unverified     |
| A "next month" item, target or open lowlight from the last update with no word now                   | Investors remember what they were told to expect                               | One line on what happened, in the founder's words                         | Unverified                                                  |
| The same runway figure two updates running                                                           | A month passed; the reader asks what changed                                   | The calculator's runway on the current plan                               | Unverified                                                  |
| An ask with no who and no why ("any intros welcome")                                                 | Nothing an investor can act on                                                 | Name the kind of person, the company type and why                         | Mercury guide (asks); specificity unverified                |

## Answering

Review mode leads with what to fix; draft mode leads with the draft, with no status line or headline before it.

1. **The draft or the revised draft,** in the shape above, ready to copy, every gap a bracketed ask. In review mode,
   first **the biggest fixes,** at most three, one line each.
2. **Reader pass:** the ranked fix list as a table (Rank, Tier, Section, Lens, The line (quoted), Why an investor
   reads it that way, Fix), then **Dropped,** one line each with why it fell. Say whether the lenses ran as subagents,
   and how many refute subagents ran.
3. **Tie-out table:** Metric or item, Period, The last update said (quoted), This update says (quoted), Status. One row
   for each metric, each item of the last update and the runway, each with one status.
4. **Numbers:** each `equity_runway_plan` call's verdict and runway rows in the tool's values, with its flags and the
   assumptions it leans on; then each other figure quoted with its "Not checked here" line from the rules file.
5. **Open asks:** every bracketed gap and every lens question in one list, to answer in one sitting.
6. **Sources:** the guides used, with links, and which points are this skill's own, unverified.
7. **Close:** this is not investment, legal or tax advice; the founder sends the update; customers named should have
   agreed; an update forwarded beyond the company's investors, or one that mentions a coming raise, is worth a word
   with the founder's lawyer first.

## Sources

- 500 Global, "A Founder's Guide for Sending Investor Updates" (6 March 2025, a guest post by a portfolio founder):
  https://500.co/content/founders-guide-sending-investor-updates
- Mercury, "How to write an effective investor update" (17 November 2024):
  https://mercury.com/blog/how-to-write-an-effective-investor-update
- Andreessen Horowitz, "16 Startup Metrics" (2015): https://a16z.com/16-startup-metrics/

These are frameworks, not voices: the people they quote are not imitated. The a16z list is from 2015 and describes
how investors read metrics, which changes slowly; say its date when a founder leans on it. The Definitions block, the
tie-out statuses and the rows marked unverified are this skill's own judgment, unverified. The two-stage reader pass
(attack, then refute with the founder's own material) is this repository's own method.

## Limits

- Not investment, legal or tax advice. It does not say what a founder must disclose, or to whom.
- It drafts and reviews only. It sends nothing, keeps no list of investors, and looks nothing up.
- It writes for current investors only; an update for people who are not yet investors goes to the
  vc-prospective-investor-update skill.
- It never invents, strengthens or hides a figure, customer, event or lowlight, in a draft or in a refute pass. A
  founder who asks to leave out bad news hears once why it costs trust; the draft keeps it.
- No arithmetic outside the equity calculator's tools: no growth rates, deltas, cash bridges or conversions. Two
  stated figures are compared as written.
- The runway is the founder's plan worked by the tool: flat spend and revenue within each phase, no fees, interest or
  collection lag. It applies no runway benchmark of its own.
- It never role-plays or speaks as a named investor, firm or author; asked to, it offers the public guides above.
- The reader pass predicts what an investor is likely to notice; a real investor may notice other things.
