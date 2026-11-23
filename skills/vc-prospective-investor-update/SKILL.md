---
name: vc-prospective-investor-update
description: Helps a founder write the short update they send to investors they hope to raise from, in the months before the raise, so each reader sees a line of progress and not a single dot. It keeps the same few metrics with the same definitions in every update, shows each metric's earlier values as stated, ties the last update's promises to what happened, and makes one ask. Investors are only names the founder supplies; it looks nobody up and sends nothing. A runway figure, when the update shows one, goes to the calculator's runway_plan tool. A skeptical reader pass has independent lenses flag spin, moved goalposts, changed metric definitions and promises left unreported, and a refute pass drops what the founder's material answers. Use when a founder says write an update for the VCs we're warming up, draft my monthly update to prospective investors, keep investors warm before our raise, or review my prospect update. Never invents or hides numbers. Not investment or legal advice.
---

# VC prospective investor update

Helps a founder keep in touch with the investors they hope to raise from, before the raise starts. A partner meeting a
company once sees one point; a partner who has had a short update every month or quarter, with the same metrics and the
same definitions each time, and who has seen last time's plans happen or not, sees a line. This skill drafts that update
from the founder's own material, or reviews a draft they paste. It lays out each metric's earlier values as the founder
stated them, ties the last update's promises to what happened, keeps one ask, checks a runway claim with the equity
calculator, and runs a skeptical reader pass that flags spin, moved goalposts, changed definitions and promises left
unreported. Then a refute pass drops each flag the founder's own material answers.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
adds a figure, customer, event or investor the founder did not give, and never looks anyone up.

## When to use it

- "Write an update for the VCs we're warming up." "Draft my monthly update to prospective investors." "Keep investors
  warm before our raise." "Review my prospect update before I send it." "What should I send the investors I met at
  demo day?" "We missed what we told them last month: how do I say it?"
- Pasted material: the earlier updates sent to these investors, this period's notes, a metrics table, a draft update,
  the founder's list of names, or this period's update to current investors.
- Hand off:
  - The update to investors already on the cap table: the vc-current-investor-update skill. When the founder sends
    both in one period, write that one first; this skill then takes its figures (the section "Built from this period's
    current-investor update").
  - Each claim's evidence across a deck and a one-pager sent with the update: the vc-claims-check skill.
  - The story and the say-and-avoid list for the raise itself: the vc-positioning skill.
  - How much to raise and which milestone it buys: the vc-round-sizing skill. This skill's runway call carries no raise
    and no milestone.
  - Whether a metric's definition is the one investors expect: the vc-metrics-readiness skill. This skill keeps a
    definition the same over time without judging it.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. Every earlier update sent to these investors, word for word, each with its date and period; or "this is the first".
2. This period's notes: what went right, what went wrong, what slipped, who joined or left, customers won and lost,
   what the last update said would happen by now and what did, and any question readers asked since.
3. Each metric: its name, its definition (what counts; gross or net; cumulative or per period), its period and this
   period's value. The values sent before come from the earlier updates, as stated there.
4. The one ask for this update: who or what, and why.
5. If the update will show runway: cash on hand and its date, monthly spend (gross burn) and revenue today, and any
   planned change as phases counted from the month after the cash date ("from month 4, $120,000 spend and $30,000
   revenue"); the runway claim; optionally how many months the founder expects the raise to take.
6. The names the update goes to, as the founder writes them, and the cadence (monthly or quarterly).

A missing input never stops the work. It becomes a bracketed ask in the draft (`[paying customers on 30 November]`),
never a plausible figure. A customer who has not agreed to be named stays in as an unnamed description ("a regional
grocer"); the event and its figures are kept.

## The shared rules for metrics

The rules for keeping metrics consistent from one update to the next, and the six status words for tying each metric
to the last update, live in one file the vc-current-investor-update skill keeps:
[`../vc-current-investor-update/references/metric-consistency.md`](../vc-current-investor-update/references/metric-consistency.md)
from this skill's folder (the plugin installs both folders side by side under `skills/`). Read it at step 3. This skill
keeps no copy. If the file is not there (the vc-current-investor-update folder was not installed), say so in one line,
name the folder to add, and go on with the line quoting every value as stated, each metric status written as
`[not tied out: the shared rules file is missing]`; never write the rules or what each status means from memory.

From that file this skill uses the metric rules, the six metric statuses (Same, Restated, Different form, Changed
definition, Dropped, New), the Definitions block and the list of figures no tool here checks. The promise statuses are
this skill's own (below).

## The update's shape

Short, bullet points, the same sections in the same order every time, so a reader can lay two updates side by side.

| Section                   | What it holds                                                                                                                | Source                                                                                             |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Where we are              | Two or three sentences: was the period good, bad or in between, and the key takeaways                                        | Mercury guide (introduction)                                                                       |
| The line                  | The same few metrics every time, each with this period's value beside the values sent before (next section)                  | Mercury guide (performance); Suster post (lines, not dots); the table's layout is ours, unverified |
| Last time we said         | Each thing the last update said would happen by now, and what did, in the founder's words, with its status                   | Suster post (what you plan to achieve by next time)                                                |
| Highlights                | What went right, with the figure or name the founder gave                                                                    | Mercury guide; 500 Global guide                                                                    |
| Lowlights                 | What went wrong or slipped, said plainly, with what the founder is doing about it                                            | Mercury guide; 500 Global guide; Suster post (adversity)                                           |
| By the next update        | The few things the founder plans to have done by the next update, not a forecast of metrics; next time's "Last time we said" | Suster post (what you plan to achieve by next time); Mercury guide (next month)                    |
| One ask                   | One specific request: who or what, and why                                                                                   | Mercury guide (asks); one ask only is ours, unverified                                             |
| Cash and runway, optional | Cash with its date and the runway as the calculator gives it, when the founder chooses to show it                            | Mercury guide (burn rate and cash runway)                                                          |
| Definitions               | Every metric's definition, word for word the same each time; a change says so                                                | The shared rules file                                                                              |

The section names are this skill's own. Two of the sources describe updates to investors already on the cap table;
one of those notes that sending updates to potential investors has been suggested as a fundraising tactic. The third
(about meetings, not written updates) describes showing potential investors progress over time. Using the update's
shape for prospects, the line table, the one ask and the "Last time we said" section are this skill's own judgment,
unverified.

## The line

The section that makes the update a line and not a dot.

- **One table, every update.** A row per metric, in the order of the first update that reported it; a column per
  update sent to these investors, oldest first, this one last, each headed by its period. At most the last six
  columns, and always the first update's column, so a reader who joined late still sees where the line started.
- **Each cell as the founder stated it** in that update, with its period. A cell is empty with "not reported" when that
  update did not give the metric; a period with no update says "no update sent".
- **No arithmetic.** No growth rate, no change, no total, no average, no conversion and no chart drawn from the
  figures. A growth rate the founder states goes in the cell as stated, with its method and period, or a bracketed ask
  for them.
- **Status, against the last update,** in a column of the tie-out table in the answer, not in the update itself: one of
  the shared file's six metric statuses. What the update does for each:
  - **Same:** nothing more; this period's value sits beside the earlier ones.
  - **Restated:** the earlier update's cell stays as stated, and the restated value goes beside it, labelled restated,
    with the reason (`[why it changed]`).
  - **Different form:** the line keeps the last update's form and asks for this period's figure in it, or how the two
    lines relate.
  - **Changed definition:** the Definitions block shows both labels and both definitions; the two are never compared
    or converted.
  - **Dropped:** the metric stays in the line, or the update says it is dropped and why.
  - **New:** a new row, with its definition in the Definitions block.
- **A metric is never removed** because it went down. It stays, or the update says it is dropped and why.

## Last time we said

Every item the last update put under "By the next update" (or said would happen, or set as a target) gets one line
here, with one of six promise statuses and the founder's own words for what happened:

- **Done**, **Partly done** and **Not done** follow the founder's notes, quoted. The skill never decides that something
  was done; with no word in the notes, the line is a bracketed ask (`[what happened with the scheduling launch]`).
- **Moved** is a target that comes back with a later date, a lower figure, a narrower scope or a different metric than
  it was given. The update says so in words ("we said December; it is now March, because ..."), with the old and new
  target both quoted. A moved goalpost that the update does not name is a finding for the reader pass.
- **No word** is an item the founder's draft does not mention at all, even when the notes say what happened. It never
  ships: the line is written, from the notes or as a bracketed ask, or the item is said to be dropped and why.
- **Not yet due** is an item whose date has not come; it carries over.

Only the last update's items get a status. An item from an older update that the last one did not carry forward gets
none here; the reader pass's Unreported promise lens finds it, and its tier is the lens's judgment.

"By the next update" says what will be done (a launch, a hire, a pilot decided), not a forecast of metrics. A founder
who sets a metric target anyway labels it as a target, with its date, and it is tied out next time like any other item.
The first update has no "Last time we said" section; it starts the line with its "By the next update" items.

## The names

The founder keeps the list of investors. This skill takes the names only, as the founder writes them, and adds none.

- It never adds, suggests, ranks, scores or researches an investor or a firm, finds an email address, or keeps the list
  between conversations.
- It gives the list back at the end of the answer as "Goes to", unchanged, with any name that appears twice marked.
- No name on the list appears in the update itself, except in a thanks the founder says that person agreed to. No
  other investor is named or hinted at either (the pattern row on other investors).

## Steps

In review mode without a subagent tool, run Stage A of the reader pass first, before step 1, as "How to run the
lenses" says; step 9 then starts at the quote check.

The reader pass judges the draft before this skill changes it. In review mode, both its stages read the founder's draft
as given, never the revised one: a line this skill adds at step 8 answers no objection. In draft mode, they read the
draft written at step 8.

1. **Quote first.** List, word for word with their update and section, every figure, target and "By the next update"
   item in every earlier update, every figure and event in this period's notes and any draft, and every figure and
   definition in this period's update to current investors, when given.
2. **Ask for what is missing,** once, in one message (Inputs above).
3. **Read the shared rules file** (above), or take its fallback.
4. **Build the line:** the metric rows and the update columns, each cell as stated.
5. **Tie out** each metric against the last update (metric statuses) and each item of "Last time we said" (promise
   statuses). When this period's update to current investors is given, also set each figure and definition the founder
   gives for this update (in a draft, the notes or the request) beside that update's for the same metric and period,
   compared as written: **Matches** or **Differs from the current-investor update**. This check is this skill's own,
   not a metric status.
6. **Runway,** only when the update shows one: call `equity_runway_plan` (next section).
7. **Other figures:** quote each as stated, with "not checked: no tool computes this".
8. **Draft or revise.** Draft mode: write the update in the shape above from the founder's material only, every gap a
   bracketed ask. Review mode: keep the founder's draft and words; change only what a status, the calculator, a figure
   or definition that Differs from the current-investor update or a kept finding requires. With more than one ask in the
   material, keep one and put the choice in the open asks (`[the one ask for this update: A or B]`).
9. **Run the reader pass** (below) on the draft it judges (the founder's draft as given in review mode): attack, check
   the quotes, refute, rank. Revise the draft for every kept finding, using only the founder's facts or a bracketed
   ask.
10. **Check before answering.** Every figure is quoted as stated or comes from a tool; every lowlight the founder gave
    is in the draft; every figure and definition this period's current-investor update also gives is word for word the
    same as there; every metric an earlier update reported is in the line or said to be dropped; every last-time item
    has a line; one ask; no investor named in the update, except in a thanks the founder says that person agreed to;
    no sentence speaks as an investor or names a firm as a voice; nothing is sent anywhere.

## Runway

Whether an update to prospects shows runway is the founder's choice; with no runway in it, this skill asks for no cash
or burn. When the update shows a runway, it goes to `equity_runway_plan` (from the command line,
`equity_calculator runway_plan`), as the founder's plan with no raise:

- `cash_on_hand`: cash at the update's date. Money as strings.
- One `plan` case: the first phase is today's monthly spend (`gross_burn`) and `revenue`, from month 1 (the month after
  the cash date); each planned change is another phase, from its month. When the founder gives cash collected rather
  than revenue, pass that and say so. When the founder gives only net burn, ask for spend and revenue; until then, pass
  the net burn as `gross_burn` with `revenue` `"0"`, and label the line as net burn in the update. A net burn of zero
  or less gets no call until spend and revenue are given (the tool refuses a `gross_burn` of 0 or less); meanwhile
  quote the founder's words, as for "default alive".
- `stated_runway_months`: the runway the update states; a "30+ months" claim is passed as `"30"`. With no figure stated
  ("default alive", "profitable soon"), call without it and quote the founder's words beside the tool's result; never
  turn those words into a figure.
- `months_to_raise`, only when the founder gives how long the raise will take: a whole number, as a JSON integer, never
  a string. A range ("4 to 6 months") is asked about once; until answered, pass the upper figure and say so. The tool
  then prints, in the "Start raising by" row, how many months from the cash date the raise has to start by. That figure
  is for the founder; it goes in the update only if they want it there.
- No `raises` and no `milestones`: sizing the round is the vc-round-sizing skill's job.
- One call for the update, and none the founder did not ask for. Built from this period's current-investor update: the
  same cash, spend and revenue as that update's call.

**A claim stated as a floor** ("30+ months", "over 30 months", "at least 30 months") is passed as its number, but the
tool's verdict row does not decide it: the tool calls a figure within its tolerance either way consistent. Compare the
tool's printed runway with that number as written, saying only which is larger. A printed runway at or above the number
keeps the claim: the update may keep it or state the printed runway, and it goes in no tier. A printed runway below the
number is a fix before sending, even when the verdict row says consistent.

```json
{
  "inputs": {
    "cash_on_hand": "2600000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "150000", "revenue": "40000" }
        ]
      }
    ],
    "months_to_raise": 6,
    "stated_runway_months": "30"
  }
}
```

The same check from the command line:

```
equity_calculator runway_plan --cash-on-hand 2600000 --phase "from-month=1 gross-burn=150000 revenue=40000" --stated-runway-months 30 --months-to-raise 6
```

Part of what it prints (Company BG, made up: $2,600,000 in the bank, $150,000 spend and $40,000 revenue a month, "30+
months of runway" in the draft, and a raise the founder expects to take six months):

```text
  Runway, plan, no raise                           23.64 months  months until cash less the floor goes below zero
  Start raising by, plan, no raise                 17.64 months  runway - months to raise
  Runway, no raise: stated                         30.00 months  given
  Runway, no raise: the calculator gives           23.64 months  the plan case's runway
  Runway, no raise: difference                     -6.36 months  computed - stated
  Runway, no raise: verdict                            mismatch  within the tolerance is consistent
```

The "30+ months" does not hold: it is a claim stated as a floor, and the printed runway is below 30. The update states
23.64 months, as the tool prints it, or leaves runway out. The 17.64 months to start raising by goes to the founder, not
into the update.

Read every row, the `flags` and the `assumptions` before answering. Use the printed values (23.64 months stays 23.64
months, never "about two years"); never round again or recompute. A refusal is the answer for those inputs: relay its
reason. A mismatch on an exact claim is a figure to fix before sending, never softened, when the claim is above the
printed runway. A mismatch with the claim below the printed runway understates it: the update may keep it or state the
printed runway, and it goes in the minor tier at most. An exact claim the verdict row calls consistent may stay as the
founder wrote it, and the Numbers section gives the printed runway. A claim stated as a floor follows the rule above
instead.

| Flag                        | What it means for the founder                                                         | What the update does                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `cash_never_runs_out`       | Revenue covers the spend before the cash runs out, so the runway has no end           | Says so in the founder's words with the plan behind it; no runway figure; a stated one is not checked |
| `start_raising_date_passed` | With the months to raise given, the date to start raising is already at or past today | Nothing; the founder hears, outside the update, that the raise should already be starting             |

With no raise and no milestone in the call, the tool raises no other flag.

## Reader pass (adversarial review)

The tie-out catches what can be matched line by line. This pass reads the draft the way an investor who kept every
earlier update will, and finds what would make that reader trust the line less. Independent lenses attack the draft,
a refute pass judges each objection using only the founder's material, and only what that material does not answer
reaches the founder.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people.

| Lens                | What it tests                                                                                                                                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spin                | A summary, highlight or label that reads better than the facts under it: adjectives with no figure, a percent with no figures, a cumulative total, a plan written as a result, a lowlight framed as a highlight |
| Moved goalposts     | A target or "By the next update" item from an earlier update that comes back later, lower, narrower or as another metric, without the update saying so                                                          |
| Changed definitions | A metric whose label, definition, form or period differs from an earlier update's, has none, or is gone; a new metric that takes the place of one that fell                                                     |
| Unreported promise  | An item an earlier update said would happen by now, or a question readers asked, with no line in the draft                                                                                                      |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("an investor who kept the last
  update is likely to notice ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here: the earlier updates, this period's notes, this period's update to current
  investors when given, and the draft. Bring in no outside fact about the company, its market or its customers, and do
  no arithmetic. Saying that one stated figure is larger than another, or one date later, is allowed; working out by how
  much is not.
- Return at most three objections, strongest first. For each: the draft's line it is about (or, for something left
  out, the earlier update's or the notes' line the draft omits), quoted word for word with its place; why an investor
  is likely to read it as a reason to trust the line less; and how much it costs (fix before sending, worth fixing, or
  minor).
- A reason you cannot tie to a line of the material is not an objection. List it apart as a question to the founder.
- Do not judge whether another line of the draft answers an objection: raise it anyway, and the refute pass decides.
  Return "nothing found" only when no line of the material gives this lens an objection worth an investor's time.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the four lenses as
parallel subagents, each given only the founder's material, the draft it judges (Steps) and its lens brief: not this
skill's other sections, not the line or the tie-out table, not another lens's output. Without one, in review mode run
the lenses before step 1, one after another, writing each lens's objections down in full before reading the next brief.
In draft mode the same agent wrote the draft, so the lenses run after step 8, still one after another. Either way the
answer says the lenses ran in one agent and are less independent than subagents.

**The calculator's mismatches** do not go through the lenses or the refute pass, and neither does a printed runway
below a claim stated as a floor, nor a figure or definition that Differs from the current-investor update (step 5).
Each leads the first tier, quoting the update's figure with the tool's value, or the current-investor update's line,
as the reason. A mismatch with the claim below the printed runway goes in the minor tier at most, the same way.

### Check the quotes

Before Stage B, check every objection's quote against the founder's material and the draft. A quote that does not
appear there word for word (spacing and line breaks aside) is dropped as not grounded. Two lenses raising the same
objection about the same line merge, keeping both lens names. Questions go to the open asks.

### Stage B: refute

Each objection gets its own refute pass. With a subagent tool, run one subagent per objection, given the founder's
material, the draft, that one objection, the Pattern column of the table below, and everything from "The refute
brief:" to the end of this stage, and nothing else; without one, decide the objections one at a time against the same
brief.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third person;
  you are not an investor and do not speak as one, named or not.
- Use only the founder's material and the draft given here. Bring in no outside fact, and do no arithmetic.
- How an investor is likely to read a line is not an outside fact: judge whether the material answers that reading.
- A line that matches a pattern in the list you were given never answers an objection.
- Return one verdict from the three below, quoting the founder's line word for word where it needs one. When you
  cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the draft given here, other than the objected line, already says what the objection
  says is missing, moved or changed. Quote it. When it sits where a reader will not look first, say to move it up.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact.
- **Kept:** neither holds. When the fix needs something the material does not contain, it becomes a bracketed ask.

An objection about an earlier update's target, item or definition may also be answered by a later update sent to these
same investors, after the one the objection quotes: a line of it that already said the target moved, the item was
dropped or done, or the definition changed. That is **Dropped, answered** too, quoting the line word for word with its
update and date. It answers only what it said: when the draft states something other than what that line announced (it
said March; the draft says June), the objection is Kept.

The refute pass invents nothing on the founder's behalf. An answering line that is not, word for word, in the draft or
in such a later update, or is the objected line itself, does not drop the objection. In review mode the draft given here
is the founder's, as given: a line this skill added at step 8 is not in it.

### The ranked fix list

Order the kept objections in three tiers: **fix before sending**, **worth fixing**, **minor**. The calculator's
mismatches lead the first tier, with every figure or definition that Differs from the current-investor update (step 5),
though a mismatch with the claim below the printed runway is minor at most (Runway); a Dropped or Restated metric
status, or a last-time item with no line in the founder's draft (No word, whatever the notes say), goes in it too, even
though the revised draft adds its line. An entry the tie-out put in the list takes the lens names of any kept objection
about the same line, and is not listed twice. Within a tier, an objection raised by more than one lens comes first. The
tier is a judgment: give no percentages and no score. Each entry: the section, the line quoted, why an investor is
likely to read it that way in one or two plain sentences, and the change, using only the founder's facts or a bracketed
ask. The draft is revised for every kept entry.

## Patterns that cost a prospect's trust

Signals, not rules: a founder may have a reason. A row marked unverified has no public source behind it that this
skill's authors read; say so when it is used.

| Pattern                                                                   | Why an investor is likely to discount it                      | Fix                                                                       | Source                                                                                               |
| ------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| A summary of adjectives ("great momentum") with no figure                 | Nothing to check, and it reads as hiding the facts            | Say whether the period was good, bad or in between, and the key takeaways | Mercury guide (introduction); pattern and reason unverified                                          |
| Highlights and no lowlights                                               | Investors assume something is being hidden                    | The lowlights the founder gave, said plainly                              | Mercury guide (mistakes to avoid)                                                                    |
| Updates that stop, or a bad month skipped                                 | Silence is read as a warning that things are going badly      | Send on the same schedule, good or bad                                    | Mercury guide (mistakes to avoid); 500 Global guide (every month, good or bad)                       |
| A metric from an earlier update missing now                               | The picture over time stops being consistent and predictable  | Keep it in the line, or say it is dropped and why                         | Mercury guide (performance)                                                                          |
| A new metric that appears as an old one falls                             | Reads as changing the scoreboard                              | Keep the old metric beside the new one, with both definitions             | Unverified                                                                                           |
| A definition changed without notice                                       | The line breaks: two points that cannot be compared           | Announce it, with both labels and definitions                             | Unverified (the rule is in the shared rules file)                                                    |
| A target that comes back later, lower or narrower without saying so       | A moved goalpost, read as a miss being hidden                 | Name the move: the old target, the new one, and why                       | Unverified                                                                                           |
| An item from "By the next update" with no word now                        | The reader was told to expect it                              | One line on what happened, in the founder's words                         | Suster post (what you plan to achieve by next time); the gap is ours, unverified                     |
| A target written as a result, or a metric target with no date or no label | A promise that the next update will have to walk back         | Results as results; a target labelled as one, with its date               | Mercury guide (next month); target as result unverified                                              |
| Paragraphs of prose; an update that takes long to read                    | It goes unread                                                | Bullet points, short lines                                                | 500 Global guide (no paragraphs); Suster post (low-key and short, about meetings); reason unverified |
| More than one ask, or an ask with no who and no why                       | Nothing a reader can act on                                   | One ask: the kind of person or help, and why                              | Mercury guide (asks); one ask and specificity unverified                                             |
| Other investors named or hinted at ("several funds are already in")       | Reads as pressure, and may break a confidence                 | Leave other investors out                                                 | Unverified                                                                                           |
| A figure that differs from this period's update to current investors      | A reader who later sees both finds two figures for one period | The same figure, word for word                                            | Unverified                                                                                           |

## Built from this period's current-investor update

When the founder also sends an update to current investors this period (the vc-current-investor-update skill), this
update is cut from it, never written apart from it:

- The same figures, word for word, and the same metric definitions. Step 5 sets each figure and definition the founder
  gives for this update beside that update's. One that differs, in a draft or in the founder's request, gives way to
  that update's in the draft and leads the first tier of the fix list with the calculator's mismatches (the last
  pattern row). One `equity_runway_plan` call for this update when it shows a runway, using that update's cash, spend
  and revenue.
- It may leave out whole sections the founder keeps for current investors (named customers who have not agreed to be
  named, team matters, the cap table, the asks meant for current investors). It does not drop a lowlight while keeping
  the highlights: a founder who asks for that hears once why a reader may later see it as spin, and the draft keeps the
  lowlight; the founder, who sends the update, may cut it in their own edit. A lowlight inside a section that may be
  left out (a departure under team matters) stays in, under Lowlights.

## Answering

Review mode leads with what to fix; draft mode leads with the draft.

1. **The draft or the revised draft,** in the shape above, ready to copy, every gap a bracketed ask. In review mode,
   first **the biggest fixes,** at most three, one line each.
2. **Reader pass:** the ranked fix list as a table (Rank, Tier, Section, Lens, The line (quoted), Why an investor reads
   it that way, Fix), then **Dropped,** one line each with why it fell. Say whether the lenses ran as subagents.
3. **Tie-out table:** Metric or item, Period, The last update said (quoted), This update says (quoted), Status.
4. **Numbers:** each `equity_runway_plan` call's verdict and runway rows in the tool's values, with its flags and the
   assumptions it leans on; then each other figure quoted with "not checked: no tool computes this".
5. **Goes to:** the founder's names, unchanged, any duplicate marked.
6. **Open asks:** every bracketed gap and every lens question in one list, to answer in one sitting.
7. **Sources:** the guides used, with links, and which points are this skill's own, unverified.
8. **Close:** this is not investment, legal or tax advice; the founder sends the update; a lawyer should look at an
   update that mentions a coming raise before it goes to people who are not yet investors; customers and people named
   should have agreed.

## Sources

- Mark Suster, "Invest in Lines, Not Dots" (Both Sides of the Table, 16 November 2010):
  https://medium.com/both-sides-of-the-table/invest-in-lines-not-dots-611f36491d73
- 500 Global, "A Founder's Guide for Sending Investor Updates" (6 March 2025, a guest post by a portfolio founder):
  https://500.co/content/founders-guide-sending-investor-updates
- Mercury, "How to write an effective investor update" (17 November 2024):
  https://mercury.com/blog/how-to-write-an-effective-investor-update

These are frameworks, not voices: the post's author and the people the guides quote are not imitated. The Suster post
is about meeting potential investors early, not written updates, and is from 2010; say so when a founder leans on it.
The section names, the line table's layout, the one ask, the promise statuses, the rows marked unverified and the rules
for an update cut from the current-investor one are this skill's own judgment, unverified. The metric rules and the
Definitions block come from the shared rules file, which is the vc-current-investor-update skill's: that skill's
pattern table gives their sources, not re-read for this one, so here they are unverified. The two-stage reader pass
(attack, then refute with the founder's own material) is this repository's own method.

## Limits

- Not investment, legal or tax advice. It does not say what a founder may tell people who are not yet investors, or
  how to mention a coming raise.
- It drafts and reviews only. It sends nothing, schedules nothing, tracks no opens or replies, keeps no list between
  conversations, and looks nothing up. Investors are names the founder supplies; it never adds, ranks or researches one.
- It never invents, strengthens or hides a figure, customer, event, target or lowlight, in a draft or in a refute pass.
  A founder who asks to leave out bad news hears once why it costs trust; the draft keeps it, and the founder may cut it
  in their own edit. A target is never written as a result.
- No arithmetic outside the equity calculator's tools: no growth rates, changes, totals, conversions or charts. Stated
  figures are compared as written.
- The runway is the founder's plan worked by the tool: flat spend and revenue within each phase, no fees, interest or
  collection lag. It applies no runway benchmark of its own.
- It never role-plays or speaks as a named investor, firm or author; asked to, it offers the public guides above.
- The reader pass predicts what an investor is likely to notice; a real investor may notice other things.
