---
name: vc-positioning
description: Helps a founder tune a raise's messaging before VCs see it. It checks a founder's one-liner, story and ask against public frameworks (YC's pitch questions, Sequoia's outline) and runs an adversarial review in which lenses list the strongest reasons a VC would pass, each quoting the founder's line, and a refute pass drops each objection the material answers. One lens tests whether a contrarian insight is non-consensus and has evidence. It flags phrases that cost credibility (no competitors, our projections are conservative, we only need 1% of the market) and returns surviving objections with rewrites, a tighter narrative, a say-and-avoid list and a prep script. Use when a founder says tighten my pitch, stress-test my pitch, check our story and our ask, how should we position this round, what is our contrarian insight, what do we believe that others don't, what should I not say to VCs, or prep me before we go out to raise. Never invents traction; the ask's figures go to the calculator. Not investment advice.
---

# VC positioning

Helps a founder package a raise before the first outside meeting: one plain sentence that says what the company does,
a story a partner can repeat to their colleagues, and the phrases to keep or drop. It reads the founder's own material,
checks it against public frameworks for how investors read a pitch, attacks it the way a skeptical partner would, then
tests each objection against the founder's own words, and returns what survives: the objections still standing, a tightened
narrative, a say-and-avoid list and a script for a prep session with an existing investor: test the packaging with
someone already on your cap table before going wide. The prep session has no public source read and is marked
unverified.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, and never
adds a fact about the company that the founder did not give.

## When to use it

- "Tighten my pitch." "Stress-test my pitch." "Why would a VC pass on us?" "How should we position this round?"
  "What should I not say to VCs?" "Is my one-liner clear?" "Prep me before we go out to raise."
- A request about the story and the ask's numbers together ("check our story and our ask"): this skill runs it, and
  step 4 sends the ask's figures to `equity_deal_check`.
- A pasted one-liner, elevator pitch, deck outline or slide text, executive summary or intro blurb. Any of these may
  come as a file the agent can read in this session.
- Hand off:
  - The arithmetic in the ask (valuation, percent sold, option pool, SAFEs and notes, runway, use of funds): follow the
    vc-deal-math skill, which calls `equity_deal_check`. New money on a SAFE or note: `equity_round` (equity-calculator
    skill), and its runway and use of funds `equity_runway_plan`. A stake through later rounds: `equity_dilution`.
  - Each claim's evidence, and figures that disagree across the deck, one-pager and narrative: the vc-claims-check
    skill (preview). Point the founder to it when they give more than one document or a claim has no evidence named.
  - A slide-by-slide deck review: the vc-deck-review skill. Point the founder to it when they share a whole
    deck.
  - Rehearsing the partner meeting: the vc-partner-meeting skill (preview).
  - The decisions behind the product and what was said no to: the vc-taste-check skill (preview).
  - How much to raise and what it buys: the vc-round-sizing skill (preview).
  - A term sheet you were offered: the vc-term-sheet-review skill (preview).
  - Diligence after the first meeting, with a data-room checklist: the vc-diligence-questions skill (preview).
  - Writing the investor updates themselves: the vc-current-investor-update skill (preview).
  - Metrics and their definitions: the vc-metrics-readiness skill (preview).
  - The memo a champion partner is likely to write for the partnership: the vc-investor-memo skill (preview).
  - Market size, bottom-up: the vc-market-sizing skill (preview).
  - Keeping prospective investors updated before the raise: the vc-prospective-investor-update skill (preview).
  - The competition map and slide: the vc-competitive-landscape skill (preview).
  - The intro emails themselves (a forwardable blurb, a cold email, follow-ups): the vc-intro-email skill (preview).
  - Passes investors have already sent, read and answered: the vc-pass-debrief skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess. When the founder gives a file the agent can
read (a PDF, HTML, a slides export, Markdown), read it yourself and list what it holds place by place (slide by slide
for a deck), in the file's own words, so the founder sees what was read from each. A place you could not read (a slide
that is only a picture, a page whose text did not come out, a file that opened only in part) is listed as not read and
asked for, never filled in from its title or the places around it, and a figure is never read off a chart or a picture.
Ask only for what you could not read and what the file does not show (speaker notes, the figures behind a chart, an
input below that it leaves out), and never ask the founder to paste what you already read.

1. The one-liner as the founder says it today, word for word.
2. The narrative in order: slide titles and text, or the spoken pitch.
3. The ask: the amount, the instrument (priced round, SAFE or note), the valuation or cap with its label (pre- or
   post-money), and the milestones the money is meant to reach.
4. Each metric as the founder states it, with its definition and period: revenue (recurring or not; bookings, GMV and
   letters of intent named as such), users, growth, retention, pipeline.
5. The stage of the raise and the kind of investor it is aimed at, in the founder's words.
6. What customers use today instead of the product, as the founder sees it.
7. Who the founder can run a prep session with: an existing investor or, with none, the closest substitute.

A missing input does not stop the review. It becomes a named gap in the answer, never a plausible figure.

## The dimensions

Each row is a question a partner answers about the company whether or not they ask it aloud. "Category" and "wedge"
are this skill's own terms, not headings in the sources; every other row follows a named public source. The last
column names the adversarial lens that attacks the row.

| #   | Dimension          | What a clear answer does                                                              | Source                                                                        | Lens                     |
| --- | ------------------ | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------ |
| 1   | What you do        | One matter-of-fact sentence a reader could describe back; "X for Y" is fine           | YC seven questions (1); Sequoia "Company purpose"; YC "How to Apply"          | Clarity and problem      |
| 2   | Category           | Tells the partner which known kind of company this is, so they know how to compare it | Our term; YC "How to Apply" (a variant of something known)                    | Clarity and problem      |
| 3   | Problem            | Whose pain, how it is handled today, why that falls short                             | Sequoia "Problem"; YC seed deck guide                                         | Clarity and problem      |
| 4   | Why now            | What changed that makes this possible or needed now, and why it was not built before  | Sequoia "Why now?"; YC seed fundraising guide (the solution slide)            | Market and why now       |
| 5   | Insight and wedge  | What the founders know that others do not, and the narrow first market they win from  | YC seven questions (4); YC "How to Apply" (insight, a toehold); wedge is ours | Competition and wedge    |
| 6   | Traction           | Period-by-period numbers with definitions; progress for the time spent                | YC seven questions (3); YC seed deck guide; a16z "16 Startup Metrics"         | Traction and proof       |
| 7   | Market             | Who exactly buys, how many, what they pay: bottom-up, with evidence                   | YC seven questions (2); YC seed fundraising guide                             | Market and why now       |
| 8   | Competition        | Direct and indirect alternatives, earlier attempts, and why customers pick this       | Sequoia "Competition / alternatives"; Dixon "The idea maze"                   | Competition and wedge    |
| 9   | Business model     | One simple way the company makes money, owned plainly                                 | YC seven questions (5); Sequoia "Business model"                              | Traction and proof       |
| 10  | Team               | Why these founders: one specific achievement each, founders before advisors           | YC seven questions (6); YC "How to Apply"; YC seed deck guide                 | Team and why you         |
| 11  | Ask and milestones | How much, on what instrument, and what it gets the company to                         | YC seven questions (7); YC seed deck guide; YC seed fundraising guide         | The ask and milestones   |
| 12  | Contrarian insight | One-sentence belief most people reject today; who disagrees and why; the evidence     | Thiel, "Zero to One"; YC "How to Apply" (best ideas seem crazy at first)      | Is it really contrarian? |

Row 12 is not row 5: row 5 is what the founders know, row 12 is a belief the business rests on that most people,
investors included, would reject today. One line may serve both; quote it under each. Contrarian and wrong is only
wrong, so the row is clear only when the founder names their evidence: customer behaviour, data, a technical result, or
their own unusual first-hand experience. The two sources give only the belief few accept; who disagrees, the evidence
test and the business resting on it are this skill's own framing.

Row 12 is a question, not a required box: many good companies have no contrarian story. When the founder states no
such belief, mark the row Not stated, never Missing, keep it out of the survivors and the biggest issues, and ask for it
once, in the message that asks for the missing inputs, with two prompts: "What do you believe about this market that
most investors would reject?" and "What did you see first-hand that others have not?" When a belief is stated as
contrarian and the lens's objection that most investors already hold it survives, ask the same two prompts once, so the
founder can give a sharper one; a surviving objection about its evidence, or about whether the business depends on it,
asks for that instead, as a bracketed ask. Never write a contrarian belief for the founder, in a rewrite, the narrative
or a refute pass: a belief the founder did not state is an invented one, however well the material seems to support it.

## Steps

Without a subagent tool, run Stage A of the adversarial review first, before step 1, as "How to run the lenses" says,
so the lenses do not anchor on the dimension marks; step 5 then starts at the quote check.

1. **Quote first.** List what the founder said under each dimension, word for word. Do not tidy it yet.
2. **Mark each dimension** Clear, Needs work or Missing, quoting the line that decides it. Give no overall score: a
   number from one conversation is not calibrated and invites false comfort.
3. **Scan for phrases** from the table below, and for anything that works the same way. For each hit: quote it, say
   what a partner is likely to hear, name the source, and give a rewrite that uses only facts the founder gave. Where
   a rewrite needs a fact they did not give, write a bracketed ask: `[number of paying customers today]`.
4. **Numbers.** Collect every figure the founder states.
   - The ask's figures (raise, valuation and its label, percent sold, pool, SAFEs and notes, cash, burn, runway claim,
     use-of-funds lines): run the check as the vc-deal-math skill describes, with `equity_deal_check`, and use only
     the tool's values, as printed, in the rewrites too (20.83 months stays 20.83 months, never "about 21"). Make one
     call per version of the ask the founder states (two for a valuation with no label, as vc-deal-math step 4 says),
     and run no what-if they did not ask for. A raise on a SAFE or note goes to
     `equity_round` as vc-deal-math step 2 says. A mismatch goes to the top of the answer: a story whose numbers
     disagree undercuts every message in it.
   - Fully diluted shares, for the tool, count every share before the round, granted options and the unissued pool
     included and SAFEs and notes excluded. Some cap tables count SAFEs and notes in their fully diluted total; ask
     which way the founder's does, and pass the tool its own basis. If the founder's total counts them, ask for the
     total without them, as a bracketed ask, `[fully diluted shares before the round, SAFEs and notes left out]`, and
     make no call that needs it until they give it; never subtract the SAFE or note shares yourself.
   - A valuation with no label: show both readings side by side and say a partner will ask which one is meant. A
     check that is a mismatch under one reading only is not a calculator mismatch: it becomes one fix, to label the
     valuation pre- or post-money, quoting both readings in the tool's values. Only a check that is a mismatch under
     every reading is the calculator's mismatch.
   - Runway with no raise, or on a SAFE or note raise, and the use-of-funds lines on such a raise go to
     `equity_runway_plan`, as vc-deal-math step 2 says: `cash_on_hand`, today's monthly spend and revenue as the plan's
     first phase, the SAFE or note as a raise with its stated runway and use-of-funds lines, and a runway stated with no
     raise as the top-level `stated_runway_months`. On a SAFE or note raise, the `plan` case's phases are the founder's
     own figures: today's monthly spend and revenue as the first phase, from month 1, and each change the founder plans
     (more spend after the raise, say) as a later phase from the month the founder names, each asked for by name when
     missing (`[planned monthly spend and revenue, from which month]`), never assumed. Until a planned change's start
     month, its monthly spend and its monthly revenue are all given, make no runway call and give no runway figure; mark
     the runway line "not checked: waiting for [the month the planned spend starts]" while the month is missing, "not
     checked: waiting for [the planned monthly spend from that month]" while the month is given and the spend is
     missing, or "not checked: waiting for [the planned monthly revenue from that month]" while only the revenue is
     missing. With no cash or burn given, ask for them by name (`[cash on hand, monthly spend and revenue]`) and make no
     call until they are given; quote the claim as stated meanwhile, and never work it out by hand.
   - Each code in a result's `flags` goes to the answer as a question a partner is likely to ask, with its meaning
     from "Calculator flags" below, since the MCP result gives the codes only. The benchmark flags are common
     benchmarks, not rules: say so and quote the tool's assumption row with the source that row gives.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point of
     its `rounded` value two places to the right, keeping every digit (0.166667 is 16.6667%, -0.033333 is -3.3333%),
     which is what the command line's report prints. That is a change of notation, not a calculation; never round it.
   - ARR, retention, churn, CAC payback and burn multiple are checked by the vc-metrics-readiness skill
     (`equity_metrics_check`), and a market size by the vc-market-sizing skill (`equity_market_sizing`): quote each as
     stated, check that it has a definition and a period, and name the skill that checks it. LTV, LTV/CAC, the Rule
     of 40 and the magic number go to the vc-metrics-readiness skill too. Growth rates: no tool computes them; quote
     them as stated with "not checked: no tool computes this". Never compute, convert or round any of these (no
     monthly growth turned into yearly, no "1% of the market is").
5. **Run the adversarial review** (next section): attack, check the quotes, refute, rank.
6. **Draft the tightened narrative** (rules below), starting from the surviving objections' rewrites.
7. **Draft the prep script** (below), with the branch for a founder who has no existing investor.
8. **Check before answering.** Every fact in the narrative appears in the founder's material or in a tool result; every
   figure is quoted as stated or comes from a tool; every surviving objection quotes a line that is in the material word
   for word; no sentence speaks as an investor or imitates a named person. Never work out how two of the founder's
   figures relate (a difference, a sum, a ratio or multiple, a share left over, "doubled") in a rewrite, a line or a
   table cell unless the founder's material states it or a tool returned it; quote both figures as stated instead ("from
   2,000 to 4,500", never "more than doubled").

## Adversarial review

The dimension table says what is missing; this review says what will lose the meeting. One set of independent lenses
attacks the founder's material, a second pass judges each objection using only that material, and only the
objections that material does not answer reach the founder. The founder then sees both: what survived, and what was tested and fell.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people: none is a named investor, firm
or author, and none speaks in the first person as an investor.

| Lens                     | What it tests                                                                                             | Dimensions |
| ------------------------ | --------------------------------------------------------------------------------------------------------- | ---------- |
| Clarity and problem      | Could a partner say back what the company does, which known kind of company it is, and whose pain it ends | 1, 2, 3    |
| Market and why now       | Who exactly buys, how many there are, and what changed to make this the moment                            | 4, 7       |
| Traction and proof       | Whether the numbers show progress, each with a definition and a period, and how the company makes money   | 6, 9       |
| Competition and wedge    | The alternatives (doing nothing included), earlier attempts, the insight, and the narrow first market     | 5, 8       |
| Team and why you         | Why these founders, shown by specific achievements rather than adjectives                                 | 10         |
| The ask and milestones   | The amount, the instrument, what the money reaches, and whether the obvious risk is named                 | 11         |
| Is it really contrarian? | Whether the founder's contrarian belief is held by few, shown right, and needed by the business (below)   | 12         |

**Is it really contrarian?** tests one thing, whether the founder's contrarian belief holds up, through four
questions, and its brief carries this paragraph as its test. Is the belief the founder states as contrarian one that
most people, investors included, would reject today, and does the founder say who disagrees and why they are wrong?
Or is it a consensus view reworded: a trend most investors already expect (such as "AI will change X"), or a side
already taken in a well-known argument? That is a partner's likely reading of the founder's line, not an outside
fact; tie it to that line, and to any line of the material that shows others already act on the belief. Does the
material show evidence the belief is right (customer behaviour, data, a technical result, the founder's unusual
first-hand experience)? Contrarian with no evidence is only a guess. And does the business depend on it? When no line
of the material puts a belief forward as contrarian, or as one others reject, the lens raises no objection and returns
one gap, what the founder believes about this market that most investors would reject and what they saw first-hand
that others have not; it never writes a belief for the founder.

Every lens gets the same brief, with its own name and test filled in (for Is it really contrarian?, the whole
paragraph above):

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to pass
  because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the founder's line it is about, quoted word for word;
  why a partner is likely to read that line as a reason to pass; and how much it hurts (ends the meeting, weakens it,
  or minor).
- A reason you cannot tie to a line the founder wrote is not an objection. List it apart as a gap, worded as a
  question to the founder.
- Do not judge whether another line of the material answers an objection: raise it anyway, however short the
  material; the refute pass decides. Return "nothing found" only when no line of the material gives this lens an
  objection worth a partner's time.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the lenses
as parallel subagents, however short the material. Give each one only the founder's material and its lens brief: not
this skill's other sections, not the dimension table, not another lens's output, so no lens anchors on another. Without
a subagent tool, run Stage A first, before step 1, without consulting the dimension table, the phrase table or any
dimension mark: run the lenses one after another, write each lens's objections down in full before reading the next
lens's brief, and never revise an earlier lens's list after a later one. Lenses run this way are less independent than
subagents, and the same agent then judges them in Stage B, so the answer says so.

**The calculator's mismatches** from step 4 do not go through the lenses. Each heads the survivors, ahead of the
tiers, under **figures that do not match (computed)**, quoting the figure as the founder states it with the tool's
value and difference as the reason. It is not refuted: the calculator computed it. It carries no tier: how much a gap
hurts depends on its size and on the term, which the founder weighs. One exception: a runway claim below the
computed runway understates it, so it does not head the survivors; the founder may keep it or state the printed
runway, and it goes in the minor tier at most. A fix to label the valuation (a mismatch under one reading only) is
not a calculator mismatch: it joins the tiers by the same judgment as the objections, and is not refuted.

### Check the quotes

Before Stage B, check every objection's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same objection about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each objection gets its own refute pass, which decides, using only the founder's material, whether that material answers
the objection. The pass is a judge, not the founder's advocate. With a subagent tool, launch one subagent per objection
in a single message, however few there are; never put two objections in one subagent. Give each the founder's
material, that one objection, the Phrase or pattern column of the phrase table below, and everything from "The
refute brief:" to the end of this stage, and nothing else; without one, take the objections one at a time and decide
each against the same brief before reading the next.

**Lean mode,** the one exception: with more than eight objections after the quote check, the refute pass may instead run
one subagent per lens, all in a single message. Each gets what a one-objection subagent gets, but with every objection
from its lens (one that two lenses raised goes to one of them only; one that no lens raised gets a subagent of its own),
and with this instruction, word for word: "Apply the brief to each objection as if it were the only one you were given.
Return one verdict for each, with its own quote where the verdict needs one. Never let one objection, its verdict or its
answering line decide another." Any objection that comes back without a verdict of its own stays Kept. The answer then
says the refute pass ran per lens, which is less independent than one subagent per objection, and that the founder may
ask for the full pass, one subagent per objection.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third
  person; you are not an investor and do not speak as one, named or not.
- Use only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic: no totals, conversions or growth rates worked out from the founder's figures.
- How a partner is likely to read a line is not an outside fact. An objection that letters of intent are not revenue,
  that a market's ceiling is small, or that a belief stated as contrarian is one most investors already hold, rests on
  that reading: judge whether the material answers it, and never drop it as not grounded for that reason. The last
  is answered only by a line that names who rejects the belief and why, never by the founder's own word that it is
  contrarian or by a different belief stated elsewhere.
- A line that itself matches a phrase or pattern in the list you were given never answers an objection.
- Return one verdict from the three below, with the founder's line quoted word for word where the verdict needs one.
  When you cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the material other than the objected line supplies the specific thing the
  objection says is missing (a figure with its period, a named alternative, a milestone, a specific achievement).
  Quote the founder's line that answers it. When that line should move earlier, where a partner will see it, say so.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact about the company, its market or its competitors.
- **Kept:** neither holds. When the founder's best answer would need something the material does not contain, the
  objection stays and that something becomes the evidence to add, as a bracketed ask.

The refute pass invents nothing on the founder's behalf: no figure, customer, plan, partnership or argument the
founder did not give. When it cannot decide, the objection is kept.

After the passes, check every answering line the same way as the objections' quotes: an answering line that is not in
the material word for word does not drop the objection, which stays kept, and neither does one that is the objected
line itself or that matches a phrase in the phrase table.

### Rank what survives

Order the kept objections in three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**. The
calculator's mismatches head the list, ahead of the tiers, with no tier, as Stage A says. Within a tier, an objection
raised by more than one lens comes first. The tier is a judgment, not a probability: give no percentages and no score.
For each survivor write:

- the founder's line, quoted word for word;
- why a partner is likely to read it that way, in one or two plain sentences;
- a concrete rewrite that uses only the founder's facts, or the evidence to add, as a bracketed ask.

**Where the survivors go.** The top three become the biggest issues at the head of the answer. A survivor that turns
on a phrase joins the say-and-avoid list. Each rewrite is carried into the tightened narrative, and so is the
advice to move a dropped objection's answering line earlier. The top survivors go into the prep script, so the
existing investor can say whether new investors will raise them too.

## Phrases that cost credibility

Signals, not rules: a founder may have a reason. Flag, explain, and let them decide. A row marked unverified has no
public source behind it that this skill's authors read; say so when you use it.

| Phrase or pattern                                                                | What a partner is likely to hear                         | Say instead                                                                                    | Source                                                                                                             |
| -------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| "We have no competitors", "nobody else does this"                                | The market is not real, or the founder has not looked    | Name the alternatives, including doing it by hand or doing nothing, and why customers pick you | Sequoia "Competition / alternatives"; YC "How to Apply" (obstacles you have not considered); Dixon "The idea maze" |
| "We only need 1% of the market", "if we get just 1% of a $X billion market"      | Top-down sizing that never narrowed the customer         | Who exactly buys, how many of them, what each pays: the founder's own numbers                  | YC seven questions (2); YC seed fundraising guide (what not to do: inflated market sizes)                          |
| "Our projections are conservative"                                               | A claim no one can check; the assumptions are what count | Label projections as a plan and show the two or three assumptions that drive them              | Unverified; YC seed fundraising guide advises against detailed financials at seed                                  |
| "Transforming", "revolutionizing", "AI-powered platform for"                     | Nothing a reader could describe back                     | What it is, for whom, in plain words; an "X for Y" analogy is fine                             | YC "How to Apply" (marketing language); YC seven questions (jargon)                                                |
| "Our edge is a better UX", "we execute better", "easy to use"                    | A claim to execute well, not an insight                  | The specific thing you know or do that others do not                                           | YC "How to Apply"; YC seven questions (4)                                                                          |
| "Strong traction", "great momentum" with no number; cumulative charts; downloads | Vanity, or a number being hidden                         | A period-by-period figure with its definition                                                  | a16z "16 Startup Metrics" (13, 14); YC seed deck guide                                                             |
| Letters of intent or bookings called revenue; GMV called revenue                 | An inflated top line that diligence will undo            | Name each metric for what it is                                                                | a16z "16 Startup Metrics" (1, 6)                                                                                   |
| "We're raising $X" with nothing after it                                         | Cannot tell what the money buys                          | The amount and the milestones it reaches                                                       | YC seed deck guide; YC seven questions (7)                                                                         |
| Team as adjectives ("passionate", "world-class"); advisors up front              | Generic claims that carry no weight                      | One specific achievement per founder; founders before advisors                                 | YC "How to Apply"; YC seed deck guide                                                                              |
| The obvious risk left out                                                        | The founder has not thought of it                        | Name it and the plan for it                                                                    | YC "How to Apply"                                                                                                  |
| "What do you think?" as the close                                                | No ask                                                   | State the ask                                                                                  | YC seven questions (7)                                                                                             |
| Asking for an NDA; negotiating valuation in the first meeting                    | Inexperience                                             | Drop the NDA; take terms away to discuss later                                                 | YC seed fundraising guide (what not to do)                                                                         |

## Calculator flags

The MCP result's `flags` holds codes only; the command line's report prints the meaning beside each one. This table,
the same as the vc-deal-math skill's, gives each `equity_deal_check` flag's meaning, so a flag reaches the founder in
words. A flag is a question a partner is likely to ask, never an error. From `equity_runway_plan` (no milestone,
months to raise or landing month passed), three flags can come back: `runway_below_band` (on the plan the raise lasts
under the runway benchmark, 18 months by default; a common benchmark, not a rule), `cash_never_runs_out` (revenue
covers the spend before the cash runs out, so there is no runway end and a stated runway is not checked) and
`consistent_beyond_rounding` (a stated runway holds by the tolerance alone, as the table's row says).

| Flag                                  | What it means for the founder                                                                                   | What to change or prepare                                                                      |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `valuation_back_solved`               | No valuation was given, so the post-money was worked from the raise and the percent.                            | Label the valuation pre- or post-money in the deck; a VC will ask which it is.                 |
| `pool_in_pre_money_lowers_price`      | The new pool is paid for out of the pre-money, so the effective pre-money and the price are below the headline. | Expect a VC to price it this way; show the effective pre-money beside the headline.            |
| `pool_in_post_money_dilutes_investor` | The pool is counted after the money, so the investor gets less than raise / post-money.                         | Expect a VC to ask to move the pool into the pre-money; show what that does to the founders.   |
| `pool_already_large_enough`           | The unissued pool already meets the target, so no new pool shares are needed.                                   | Say so in the deck; a VC may still ask for a bigger target.                                    |
| `conversions_bought_by_pre_money`     | SAFE and note shares come out of the pre-round holders, so their stake falls by more than the percent sold.     | Show ownership with the SAFEs and notes converted, as a VC reads the cap table.                |
| `discount_beat_cap`                   | A discount gave a lower price than the cap.                                                                     | Model that instrument at its discount price; a cap-only conversion in the deck would be wrong. |
| `note_interest_converts`              | Note interest converts too, so a note gets more than its principal's worth of shares.                           | Count the interest in the cap table.                                                           |
| `consistent_beyond_rounding`          | A stated percent or runway holds by the tolerance alone: it is not the tool's figure rounded to its own places. | Quote the tool's figure; a VC recomputing gets it.                                             |
| `net_burn_not_positive`               | Revenue covers the burn on those figures, so there is no net runway on it.                                      | A runway claim is checked on the other burn's net runway; with none, it is not checked.        |
| `current_burn_runway_longer`          | Runway on today's burn is longer than on the planned burn.                                                      | Say which burn the deck's runway uses; a VC will check it against the planned spend.           |
| `runway_below_band`                   | Planned net runway is under the runway benchmark (18 months by default).                                        | Be ready to say whether the raise reaches the next milestone (a common benchmark, not a rule). |
| `dilution_above_band`                 | The investors get more than the dilution benchmark (25% by default) in one round.                               | Be ready to say why so much is sold (a common benchmark, not a rule).                          |

## The tightened narrative

- **One-liner:** two or three options, matter-of-fact. Test each the way the sources suggest: could a reader who sees
  only this sentence describe the product back?
- **Order:** keep the founder's order unless a dimension is missing or buried. Offer YC's seed deck order (title,
  problem, solution, traction, insight, business model, market, team, ask) or Sequoia's outline as the alternative.
- **Never stronger than the facts.** No number, customer name, growth claim, partnership or credential that is not in
  the founder's material or a tool result. Every gap is a bracketed ask.
- **Shorter, in the founder's voice.** Cut words that carry nothing; keep the founder's own terms where they are clear.
- **Answer the survivors.** Each surviving objection's rewrite appears in the narrative, or its bracketed ask does.
  A dropped objection's answering line moves earlier where its Dropped line says so.
- **The repeatable line:** mark the one sentence a partner should be able to repeat to their partners on Monday.

## The prep script

Purpose: test the packaging with someone who already knows the company before the first outside meeting.

- **Who:** an existing investor, ideally the lead of the last round. With none, the closest substitute: a founder who
  recently raised from the same kind of investor, an accelerator partner, or an angel who knows the space. Say plainly
  that a substitute does not know the company's history, so steps 5 and 7 below become guesses.
- **Before:** send the one-liner, the narrative, the say-and-avoid list and the top surviving objections a day or two
  ahead.
- **Agenda** (about 45 minutes; a suggestion, not a source):
  1. Before any slides, ask them to say in one sentence what the company does. Compare it with the one-liner.
  2. Give the pitch in the time a first meeting allows. Ask them to stop you at the first line they would discount.
  3. Walk the say-and-avoid list: which would they also flag, and what would they add for the investors you are
     targeting?
  4. Ask for the three questions they expect first from a new partner. Compare them with the top surviving objections;
     a question on both lists is the one to rehearse first, out loud.
  5. The ask: does the amount and the milestone story hold up, and does every figure match what they have seen in
     your investor updates?
  6. Ask how they would describe the company in an intro email. That sentence tests the repeatable line.
  7. Ask what they would say if a new investor called them about the company, and whether they expect to take part in
     the round (our note, unverified: new investors often ask both).
- **After:** update the narrative and the list, then try it on one or two more friendly listeners before the main list.

## Answering

Lead with what to fix, then the material to take into the prep session.

1. **The biggest issues,** at most three, one line each: the top surviving objections.
2. **Adversarial review:**
   - **Survivors,** ranked, as a table: Rank, Tier, Lens, The founder's line (quoted), Why a partner reads it that way,
     Rewrite or evidence to add, with the figures that do not match (computed) first, then the tiers.
   - **Dropped,** one line each: the objection, its lens, and why it fell (answered, quoting the founder's line that
     answers it and saying whether to move that line earlier, or not grounded), so the founder sees it was tested.
   - When the lenses ran one after another in one agent, with no subagent tool, say so: they are less independent
     than separate subagents.
   - When the refute pass ran per lens (lean mode), say so, say it is less independent than one subagent per objection,
     and say the founder may ask for the full pass.
3. **Dimension table:** Dimension, What you say (quoted), Clear / Needs work / Missing (Not stated for row 12), Fix.
4. **Contrarian insight:** the belief as the founder stated it, quoted word for word, or "not stated"; the surviving
   objections of the Is it really contrarian? lens, or that none survived; and up to two rewrites of the one-sentence
   belief, each using only the founder's material, with the evidence it lacks as a bracketed ask. A rewrite only
   rewords, shortens or joins lines the founder wrote: it adds no claim about the market, the buyer or the product
   that no line of theirs states. A surviving objection about the evidence, or about whether the business depends on
   the belief, carries its own bracketed ask and no prompt. When the belief is not stated, or the objection that most
   investors already hold it survives: up to two includes none, so unless a line of the material states a sharper
   belief in the founder's own words, give the bracketed ask
   `[the belief about this market that most investors would reject today, in one sentence]`, never a belief written
   for the founder; the two prompts from row 12 go to the open asks once, as one item with that bracketed ask and the
   lens's gap, and this block points to it; and say that not every good company needs a contrarian story, so leaving
   the claim out is the founder's choice.
5. **Say and avoid:** each flagged phrase quoted, what a partner is likely to hear, the rewrite, the source.
6. **Numbers:** the `equity_deal_check` verdict with each mismatch row in the tool's values (for a valuation with no
   label, both readings side by side), and each flag as a question a partner is likely to ask, with its meaning; a
   runway with no raise or on a SAFE or note raise, and that raise's use-of-funds lines, with `equity_runway_plan`'s
   rows, or quoted as stated beside the ask for cash and burn when they were not given; each metric or market size
   with the skill that checks it (LTV and the magic number included); growth rates quoted as stated with "not
   checked: no tool computes this";
   and any figure that lacks a definition or a period.
7. **Tightened narrative:** one-liner options, a 30-second version, the section order with bracketed asks.
8. **Prep script,** filled in with the founder's material and the top survivors.
9. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
10. **Sources:** the frameworks used, with links, and which points rest on an unverified source.
11. **Close:** this is not investment, legal or tax advice; a lawyer should review fundraising materials before they
    are posted publicly or sent widely, and customers or partners named in a deck should have agreed to be named.

## Sources

- Y Combinator, "How to Pitch Your Company" (the seven questions):
  https://www.ycombinator.com/library/4b-how-to-pitch-your-company
- Y Combinator, "How to Apply to Y Combinator" (Paul Graham): https://www.ycombinator.com/howtoapply
- Y Combinator, "How to build your seed round pitch deck":
  https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck
- Y Combinator, "A guide to seed fundraising": https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising
- Sequoia Capital, "Writing a Business Plan": https://www.sequoiacap.com/article/writing-a-business-plan/
- Andreessen Horowitz, "16 Startup Metrics" (2015): https://a16z.com/16-startup-metrics/
- Chris Dixon, "The idea maze" (2013): https://cdixon.org/2013/08/04/the-idea-maze
- Peter Thiel with Blake Masters, "Zero to One" (2014), its interview question asking for an important truth few
  others accept, read in the excerpt Fortune published:
  https://fortune.com/2014/09/04/peter-thiels-the-challenge-of-the-future

Several of these guides are years old. They describe how investors read a pitch, which changes slowly, but say their
dates when a founder leans on one. The adversarial review's two-stage method (attack, then refute with the founder's
own material) is this skill's own, not taken from any source. The prep session has no public source read and is marked
unverified; no person or post is credited for it.

## Limits

- Not investment, legal or tax advice. It does not say whether to raise, from whom, or at what valuation.
- It never invents or strengthens traction, customers, partners, credentials or figures, in a rewrite or in a refute
  pass.
- It never role-plays or speaks as a named investor, firm or author. Asked to "be" one, it offers that firm's public
  framework instead (Sequoia's outline and YC's seven questions, with their links) and the adversarial review's
  lenses, plus the prep session (unverified: no public source read), and keeps the founder as the user.
- The adversarial review predicts likely objections from the founder's text; it is not a verdict on the company, and
  a real partner may raise others.
- No investor research: no target lists, fund look-ups, contact details or outreach. The founder names who they meet.
- No arithmetic outside the equity calculator's tools. Growth rates are quoted, not computed; metrics (LTV, the Rule
  of 40 and the magic number included) and market sizes are checked by the vc-metrics-readiness and vc-market-sizing
  skills.
- The phrase table holds common signals from public guides, not rules; they vary by stage, sector, region and
  investor. One row ("conservative projections") has no public source read and is marked unverified.
- It works from the founder's text and sends nothing anywhere.
