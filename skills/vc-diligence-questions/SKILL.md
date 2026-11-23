---
name: vc-diligence-questions
description: Helps a founder prepare for the due-diligence questions a fund asks after a first meeting. By area (team, market, product, traction and metrics, financials and cap table, legal) it finds the questions the founder's own material leaves open, ranks them by how much each answer moves the fund's decision, drafts an answer to each from the founder's material only, and builds a data-room checklist scaled to the stage, each item marked ready, missing or contradicted. An adversarial review has one lens per area attack the founder's lines and a refute pass drop what the material already answers. The questions come from the question bank the vc-partner-meeting skill keeps, read as one shared file. The cap table and the ask go to the calculator's deal_check tool. Use when a founder says prepare me for diligence, what will they ask in diligence, build my data room, data-room checklist, or the fund wants to start diligence. Never invents documents or figures. Not legal, tax or investment advice.
---

# VC diligence questions

Helps a founder get ready for what a fund does after a good first meeting: diligence. It finds the questions a partner
is likely to ask next, in six areas, ranks the ones the founder's material leaves open by how much each answer moves
the fund's decision, drafts an answer to each from what the founder gave, and builds a data-room checklist scaled to
the stage, each item marked ready, missing or contradicted. The cap table and the ask are checked by the equity
calculator, never by hand.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, gives no
score and no readiness percentage, and never adds a fact, a figure or a document the founder did not give.

## When to use it

- "Prepare me for diligence." "What will they ask in diligence?" "Build my data room." "Give me a data-room
  checklist." "The fund wants to start diligence; what do I need?"
- After a first meeting or a partner meeting, with the deck, a one-pager, the cap table, the ask, and a list of the
  documents the founder has today.
- Hand off:
  - Rehearsing the meeting itself, one question at a time with a debrief: the vc-partner-meeting skill.
  - Each claim's evidence and figures that disagree across documents, in full: the vc-claims-check skill.
  - The ask's arithmetic in full (ownership after the round, the pool, the SAFE stack, runway): the vc-deal-math
    skill, whose steps this skill follows for the cap table and the ask. One equity question with no diligence
    around it: the equity-calculator skill.
  - The story and the phrases to drop: the vc-positioning skill.
  - "Review my term sheet": the vc-term-sheet-review skill, clause by clause. This skill lists the term sheet as a
    data-room document and takes its pool for the calculator, but never reviews or judges its clauses.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess. At most five questions:

1. The material the fund has seen or will see: the deck, a one-pager, the answers given in the meeting as the founder
   remembers them, and anything the fund has already asked for, in its words.
2. The stage and the round: pre-seed, seed, Series A or later; the amount, the instrument (priced round, SAFE or
   note), the valuation or cap with its label (pre- or post-money), and the percent sold if stated.
3. The cap table as the founder has it: each holder group's shares (founders, other common, granted options, the
   unissued pool, preferred), the fully diluted total, and each SAFE or note with its terms, as vc-deal-math step 2
   lists them; plus every place the deck or a document states an ownership percent.
4. The documents the founder has today, by name, one line each on what each shows ("bookings by month since
   January"). The skill works from this list and from text the founder pastes; it does not open a folder of files.
5. The company's legal home in the founder's words (country, kind of company), so legal items are worded as questions
   for the founder's lawyer, not as rules of one country.

A missing input does not stop the work. It becomes a named gap and a bracketed ask, never a plausible fact. **The
founder's material** means the pasted text plus every answer the founder gives in this session; label each part as it
arrives (M1, M2 ... for the material; D1, D2 ... for the document list), so every quote can be located.

## The six areas and the shared question bank

The questions come from one file: the question bank the vc-partner-meeting skill keeps, at
[`../vc-partner-meeting/references/question-bank.md`](../vc-partner-meeting/references/question-bank.md) from this
skill's folder (the plugin installs both folders side by side under `skills/`; a manual install copies both folders).
This skill reads that file; it keeps no copy of it. If the file is not there (the vc-partner-meeting folder was not
installed), say so in one line, name the folder to add, and go on with this skill's own file; never write bank
questions from memory and cite no bank ID.

From each bank row this skill reads the ID, Question, Probes, Stages, Grounding and Diligence columns; it does not use
the Lenses column, which belongs to the partner-meeting rehearsal. Each bank category belongs to one area:

| Bank category            | Area                     | Also read by                  |
| ------------------------ | ------------------------ | ----------------------------- |
| The one sentence         | Product                  |                               |
| Insight and wedge        | Product                  |                               |
| Risks and what breaks    | Product                  | Legal reads RISK-3 and RISK-4 |
| Why now                  | Market                   |                               |
| Market                   | Market                   |                               |
| Competition              | Market                   |                               |
| Users and growth         | Traction and metrics     |                               |
| Business model           | Traction and metrics     |                               |
| Team                     | Team                     |                               |
| The ask and use of funds | Financials and cap table |                               |
| The round                | Financials and cap table |                               |

The bank holds meeting questions; diligence also asks about the company's legal footing and the cap table's own
records, which no meeting question covers. Those questions, and the data-room checklist, are in this skill's own
file, [`references/data-room.md`](references/data-room.md). Each checklist row names the bank IDs whose Diligence
cell it answers, so the bank stays the one place a question is worded.

| Area                     | What a partner checks in diligence                                                           |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| Team                     | Who the founders are, shown by checkable achievements; who else is on the team; references   |
| Market                   | Who buys and how many there are, from what source; the alternatives at four levels; why now  |
| Product                  | What exists and works today, what the technology does, what breaks, the next quarter's plan  |
| Traction and metrics     | Each metric's definition, its history period by period, its source records, its customers    |
| Financials and cap table | The plan, the cash, the ask, who owns what before and after the round, every SAFE and note   |
| Legal                    | The company's formation, who owns the work, the main contracts, disputes, rules it must meet |

## Steps

Without a subagent tool, run Stage A of the adversarial review right after step 1, before step 2, as "How to run the
lenses" says, so the lenses do not anchor on the numbers, the bank or the checklist; step 4 then starts at the quote
check.

1. **Intake.** Ask for the missing inputs in one message. Label the material as it arrives.
2. **The cap table and the ask go to the calculator.** Follow the vc-deal-math skill's steps; use only the tools'
   values.
   - A priced round: `equity_deal_check` (from the command line, `equity_calculator deal_check`), money and percents
     as strings, with `fully_diluted_shares`, `unissued_pool_shares`, `target_pool_percent` and `pool_timing`, every
     SAFE and note as `instruments`, and each ownership figure a document states: the investors' percent as
     `stated_investor_percent`, the founders' percent after the round as `stated_holder_percent` with the founders'
     shares today as `holder_shares`. One call per document's version of the ask. Never divide the shares yourself.
   - Fully diluted shares, for the tool, count every share before the round, granted options and the unissued pool
     included and SAFEs and notes excluded. Some cap tables count SAFEs and notes in their fully diluted total; ask
     which way the founder's does, and pass the tool its own basis.
   - A raise on a SAFE or note is not passed as `investment`: route it as vc-deal-math step 2 does, to `equity_round`,
     with the next priced round the founder expects.
   - Runway: a runway claim on a priced round is part of the `equity_deal_check` call. Runway with no raise, or on a
     SAFE or note raise, goes to `equity_runway_plan`: `cash_on_hand`, a plan case
     (`{"name": "plan", "phases": [{"from_month": 1, "gross_burn": "...", "revenue": "..."}]}`), the stated runway as
     `stated_runway_months` (no raise) or as a raise option's own `stated_runway_months` (`raises: [{"amount": "..."}]`).
   - A tool's mismatch is a diligence question a partner will ask first, so it goes to the top of the ranked list.
   - Read every code in the tool's `flags` too, and relay each in the tool's words: beside the mismatch it explains,
     or, with no mismatch, as a kept question at slows it, not refuted. A flag that rests on a benchmark band quotes
     the band only as the tool's assumption row gives it, with its `unverified` source, never as a bar to clear.
   - What no tool checks: whether the cap table's rows add up to its total, and any percent of the company the
     founder states for today. Quote them as stated, mark them "not checked: no tool adds up a cap table", and never
     add, subtract or divide shares yourself.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point of
     its `rounded` value two places to the right, keeping every digit (0.166667 is 16.6667%), which is what the
     command line's report prints. That is a change of notation, not a calculation; never round it.
   - Growth rates, retention, market sizes and unit economics have no tool here: quote them as stated, check only that
     each has a definition, a period and a record behind it, and never compute, convert or round one.
3. **Run the adversarial review** (next section): attack, check the quotes, refute, rank.
4. **Read the bank and the checklist,** only now. Word each kept question with a bank row's Question, or a row of
   this skill's own question table, when one asks the same thing, and cite its ID; otherwise keep the lens's
   wording. Then build the area prep list and the data-room checklist (the sections after the review).
5. **Draft an answer** to each kept question (the section "Draft answers").
6. **Check before answering.** Every kept question quotes a line that is in the founder's material word for word;
   every draft answer uses only facts from the material or a tool result and marks each gap as a bracketed ask; every
   figure is quoted as stated or comes from a tool; every checklist status rests on the document list or a quoted
   line; no document is described that the founder did not name; no sentence speaks as an investor, imitates a named
   person or firm, or gives a score.

## Adversarial review

A partner's diligence goes where the founder's material is thinnest. One lens per area attacks the material and
proposes the questions it leaves open; a second pass judges each question using only that material; only the
questions the material does not answer are ranked. The founder sees both lists.

### Stage A: attack

Each area is one lens, named by what it tests (the area table above), never by a person or firm. Every lens gets the
same brief, with its own name and test filled in:

- You test one area: the lens's name and what it checks. Write in the third person ("a partner is likely to ask in
  diligence ... because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material and document list given here. Bring in no outside fact about the company, its
  market, its competitors, its investors or the law, and do no arithmetic.
- Return at most three questions, the one that moves the decision most first. For each: the founder's line it is
  about, quoted word for word with its label; the question as a partner is likely to put it; the document or answer
  that would settle it; and how much an unsettled answer moves the decision (stops the process, slows it, or minor).
- A question you cannot tie to a line the founder wrote is not an attack. List it apart as a gap, worded as a
  question to the founder.
- Return "nothing found" rather than a weak question.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the six
lenses as parallel subagents. Give each one only the founder's material, the document list and its lens brief: not
this skill's other sections, not the bank, not the checklist, not the calculator's output, not another lens's output.
Without a subagent tool, run Stage A right after step 1, before step 2, without reading the bank or the checklist: run
the lenses one after another, write each lens's questions down in full before reading the next lens's brief, and never
revise an earlier lens's list after a later one. Lenses run this way are less independent than subagents, and the
same agent then judges them in Stage B, so the answer says so.

**The calculator's mismatches** from step 2 do not go through the lenses. Each mismatch row is added to the kept
questions as stops the process, in the Financials and cap table area, quoting the figure as the founder's document
states it, with the tool's value as the reason. It is not refuted: the calculator computed it.

### Check the quotes

Before Stage B, check every question's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same question about
the same line, merge them and keep both area names. Gaps from every lens go to the open asks.

### Stage B: refute

Each question gets its own refute pass. With a subagent tool, run one subagent per question, given the founder's
material, the document list, that one question, and everything from "The refute brief:" to the end of this stage, and
nothing else; without one, take the questions one at a time and decide each against the same brief before reading the
next.

The refute brief:

- You decide whether the founder's material already answers one diligence question; you argue neither side. Write in
  the third person; you are not an investor and do not speak as one, named or not.
- Use only the founder's material and document list given here. Bring in no outside fact, and do no arithmetic.
- How a partner is likely to read a line is not an outside fact. Judge whether the material answers the question.
- A document the founder names counts only for what the founder says it shows; never assume what is in it.
- Return one verdict from the three below, with the founder's line quoted word for word where the verdict needs one.
  When you cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the material other than the questioned line, or a document on the founder's list,
  gives the specific thing the question asks for (a definition, a figure with its period, a signed document). Quote
  that line or name that document. The question is not ranked; it goes to the have-it-ready list with that line or
  document as the answer to point to.
- **Dropped, not grounded:** the quoted line does not say what the question assumes, or the question rests on an
  outside fact about the company, its market, its investors or the law.
- **Kept:** neither holds. When the best answer would need something the material does not contain, that something
  becomes a bracketed ask, such as `[a signed assignment of the contractor's work to the company]`.

The refute pass invents nothing on the founder's behalf: no figure, document, customer, investor or argument. After
the passes, an answering line that is not in the material word for word does not drop the question, which stays
kept, and neither does one that is the questioned line itself.

### Rank what survives

Order the kept questions in three tiers, by how much each answer moves the fund's decision: **stops the process** (left
unanswered, it is likely to end diligence: a calculator mismatch, work the company may not own, a dispute, figures
that disagree), **slows it** (a document a partner will ask for that does not exist yet, a metric with no definition),
**minor**. The calculator's mismatches lead the first tier. Within a tier, a question raised by more than one lens
comes first. The tier is a judgment, not a probability: give no percentages and no score.

## The area prep list

Besides the ranked questions, a partner asks the usual questions of each area. For each area, list at most five bank
rows whose Stages include the founder's stage: first those whose Grounding is a kind of line the material has (a
traction line, the ask line), then those marked standing. Legal and Financials and cap table also list, in the same
order and at most five each, the rows of this skill's own question table in `references/data-room.md` for that area.
Give each its ID and Question, and the founder's line it touches, quoted, or "standing". These are not attacks and
are not refuted; the founder prepares a short answer to each. A bank row never enters the ranked list on its own: it
enters only when a lens tied it to a founder's line quoted word for word and it then passed the quote check and the
refute pass.

## The data-room checklist

Build it from [`references/data-room.md`](references/data-room.md): the rows for the founder's stage, by area. Mark
each row with one status; when a row earns more than one, take the first in this order: **Contradicted**, then
**Missing**, then **Ready**.

- **Contradicted:** a document or line the founder gave disagrees with another (both quoted), or the calculator
  reports a mismatch on what the document records (the cap table against the deck).
- **Missing:** no document on the founder's list shows what the row needs. Give the bracketed ask.
- **Ready:** a document on the founder's list shows it, named as the founder named it. The skill has not seen the
  document; the answer says a partner will open it.

Keep the data room to the stage: at seed, a short set (the deck, an executive summary, the cap table, the SAFE or
note forms, the formation documents and the work assignments) is usually enough, and the guide this skill relies on
says not to spend much time on diligence documents for a seed round. Rows for a later stage are not listed as
missing; name them once as "for the next round" when the founder asks for a fuller room.

## Draft answers

For each kept question, in ranked order:

- **The question,** its area, the bank or own-table ID if one was used, and the founder's line it came from, quoted.
- **A draft answer,** at most four sentences, the point first, built only from the founder's material and tool
  results, each fact traceable to a label. Never stronger than the facts: no number, customer, document, signature,
  date or plan that is not in the material. Each gap is a bracketed ask. Where the founder does not know yet, the
  draft says so plainly and says when they will; saying "we don't know yet" is better than a guess.
- **What to put in the data room** to settle it: the checklist row's ID, or "nothing to add".

A legal question gets a draft answer that states the facts the founder gave and the question to put to their lawyer;
it never says whether something is legally sufficient.

## Answering

1. **The three that move the decision most,** one line each: the top of the ranked list.
2. **Ranked questions,** as a table: Rank, Tier, Area, The founder's line (quoted), The question, What settles it.
   Then **Dropped,** one line each: the question, its area, and why it fell (answered, naming the line or document to
   point to, which also goes to the have-it-ready list; or not grounded). When the lenses ran one after another in
   one agent, say they are less independent than separate subagents.
3. **Draft answers,** question by question, as above.
4. **Area prep list,** area by area, with bank IDs and this skill's own LEGAL and CAP IDs.
5. **Data-room checklist,** by area: Row, What it shows, Status (Contradicted, Missing or Ready), the founder's
   document or the bracketed ask.
6. **Numbers and cap table:** each `equity_deal_check`, `equity_round` or `equity_runway_plan` verdict with each
   mismatch row in the tool's values; each flag, one line, in the tool's words; the cap table's own sums and today's
   percents with "not checked: no tool adds up a cap table"; every other figure quoted as stated.
7. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
8. **Sources:** the frameworks used, with links, and which points rest on this skill's own unverified judgment.
9. **Close:** this is not legal, tax or investment advice; a lawyer should review the legal rows and every document
   before it goes into the data room; customer contracts and customer names may need the customer's consent before
   they are shared; the founder decides what to share and when.

## Sources

- Y Combinator, "A guide to seed fundraising": https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising
- Andreessen Horowitz, "16 Startup Metrics" (2015): https://a16z.com/16-startup-metrics/

The seed guide gives the stage rule ("Do not spend too much time developing diligence documents for a seed round"),
what a seed executive summary holds (vision, product, team, traction, market size and minimum financials: revenue,
if any, and fundraising prior and current), its list of what not to do with investors ("Be dishonest in any way";
saying "you don't know yet" is fine), and its glossary's fully diluted shares, which count convertible securities in;
the calculator's basis leaves SAFEs and notes out, so step 2 asks which way the founder's cap table counts. "16
Startup Metrics" gives the traction lens what a definition must settle: bookings are not revenue, letters of intent
are neither, a month's bookings times twelve is not recurring revenue, active users need a stated definition, churn
and retention by cohort, net against gross burn, and cumulative charts. The six areas, the bank-to-area mapping, the
legal and cap-table rows, the checklist and its stage column, and the three tiers are this skill's own judgment,
unverified. The question bank is the vc-partner-meeting skill's own list, also unverified. The two-stage review
(attack, then refute with the founder's own material) is shared with the vc-positioning skill.

## Limits

- Not legal, tax or investment advice. It never says whether a document is legally sufficient, whether an
  assignment, a filing or a contract is valid, or what a tax election means; those are questions for the founder's
  lawyer or accountant.
- It never invents, backdates or strengthens a document, a figure, a customer, a signature or a date, and never helps
  leave out a known dispute or claim a partner would ask about. Asked to, it declines in one line and drafts a true
  answer and the question for the founder's lawyer instead.
- It never plays an investor, never speaks as or imitates a named investor, firm or author, and gives no score or
  readiness percentage.
- No investor research: no look-ups of funds, partners or their diligence lists, and no outreach.
- No arithmetic outside the equity calculator's tools. The cap table's own sums and today's percents are quoted, not
  computed.
- It works from the founder's text and document list, opens no folder of files, uploads nothing and sends nothing
  anywhere.
