# Question bank

The questions a partner is likely to ask in a meeting, by category. The vc-partner-meeting skill reads this file only
after the attack stage of its adversarial review, to word the questions its lenses kept, so no lens anchors on it. A
question here enters the drill only when it is tied to a line of the founder's material quoted word for word and then
passes the quote check and the refute pass; otherwise it becomes an open ask, or it is one of the standing prep
questions. The vc-diligence-questions skill reads the same file: the ID, Question, Probes, Stages, Grounding and
Diligence columns and each category heading, so renaming one fails that skill's test.

The list and its wording are this skill's own and unverified. A few topics, among them the round-so-far rows, came as
ideas from the investor-persona prompts the skill's Sources credit, which cite no source for them.

## How to read a row

| Column    | What it holds                                                                                              |
| --------- | ---------------------------------------------------------------------------------------------------------- |
| ID        | The category and a number, unique across the file                                                          |
| Question  | As a partner is likely to put it; the skill puts it in the third person when it asks it                    |
| Probes    | What a good answer shows, in one line                                                                      |
| Lenses    | The lenses that raise it, named as in the skill's lens table                                               |
| Stages    | pre-seed, seed, Series A, later, or all                                                                    |
| Grounding | The kind of founder line that makes it a drill question, or standing for a question every founder prepares |
| Diligence | What a partner may ask to see afterwards, or none; read by the vc-diligence-questions skill                |

Rules for every row: a question, never an answer; no figure, benchmark or bar, since what counts as enough varies by
sector, region and year; no person or firm named. Competition rows read the market at four levels, and each one's
Probes cell starts with its level: **Direct** (the same product for the same buyer), **Indirect** (the same need met
another way), **Adjacent and platform** (a larger product the buyer already uses that could add this as a feature),
and **Doing nothing** (spreadsheets, phone calls, an outsourced service, or living with the problem).

## The one sentence

| ID    | Question                                                                      | Probes                                    | Lenses                  | Stages         | Grounding     | Diligence             |
| ----- | ----------------------------------------------------------------------------- | ----------------------------------------- | ----------------------- | -------------- | ------------- | --------------------- |
| ONE-1 | What does the company do, in one sentence a customer would use?               | The category is clear without jargon      | Pre-seed, Seed, Product | all            | the one-liner | none                  |
| ONE-2 | Which known kind of company is this most like, and where does it differ?      | A comparison a partner can repeat         | Seed, Sector thesis     | all            | the one-liner | none                  |
| ONE-3 | Who is the first user, by role, and what do they do with it on the first day? | A named role and a first action           | Product, Pre-seed       | pre-seed, seed | the one-liner | a product walkthrough |
| ONE-4 | How should a partner describe the company to colleagues after this meeting?   | A line that survives being retold         | Network, Seed           | all            | the one-liner | none                  |
| ONE-5 | Which words in that sentence would a customer never use?                      | Plain words over category terms           | Product                 | all            | the one-liner | none                  |
| ONE-6 | What does the company deliberately not do?                                    | Focus, with a stated boundary             | Operator, Product       | all            | the one-liner | none                  |
| ONE-7 | How has the description of the company changed since it started, and why?     | Learning from customers rather than drift | Pre-seed, Seed          | pre-seed, seed | the one-liner | none                  |

## Users and growth

| ID       | Question                                                                     | Probes                                           | Lenses                  | Stages                | Grounding       | Diligence                                |
| -------- | ---------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------- | --------------------- | --------------- | ---------------------------------------- |
| GROWTH-1 | How many users or customers use it today, and how is each one counted?       | A count with its definition                      | Seed, Series A          | all                   | a traction line | an export of active accounts             |
| GROWTH-2 | Of the users who started last quarter, how many still use it?                | Retention defined, with a period                 | Seed, Series A, Product | seed, Series A        | a traction line | retention by monthly cohort              |
| GROWTH-3 | What did the last few months look like, month by month?                      | Figures period by period, not a cumulative chart | Series A, Finance       | seed, Series A, later | a traction line | monthly metrics since launch             |
| GROWTH-4 | Where did the last few customers come from?                                  | A channel that can repeat                        | Series A, Operator      | seed, Series A        | a traction line | recent customers by source               |
| GROWTH-5 | Which customer uses it most, and what would they lose if it went away?       | Depth of use and a named pain                    | Product, Seed           | pre-seed, seed        | a traction line | a customer call, with the customer's yes |
| GROWTH-6 | Is the revenue recurring, one-off, or committed but not yet paid?            | Each figure named for what it is                 | Finance, Series A       | seed, Series A, later | a traction line | invoices and contracts                   |
| GROWTH-7 | How much of the revenue comes from the largest few customers?                | Concentration named, not hidden                  | Finance, Later stage    | Series A, later       | a traction line | revenue by customer                      |
| GROWTH-8 | The last time growth slowed, what caused it and what did the team change?    | An honest reading of a dip                       | Operator, Series A      | Series A, later       | a traction line | none                                     |
| GROWTH-9 | What has the company learned or shipped for the time and money spent so far? | The pace of progress                             | Pre-seed, Seed          | pre-seed, seed        | a traction line | none                                     |

## Why now

| ID    | Question                                                                        | Probes                                      | Lenses                     | Stages                | Grounding      | Diligence             |
| ----- | ------------------------------------------------------------------------------- | ------------------------------------------- | -------------------------- | --------------------- | -------------- | --------------------- |
| NOW-1 | What changed that makes this possible now, and not some years ago?              | A specific shift, not a trend word          | Sector thesis, Pre-seed    | all                   | a why-now line | none                  |
| NOW-2 | Who tried this before, and why did it not work then?                            | Earlier attempts, and what is different now | Sector thesis, Seed        | all                   | a why-now line | none                  |
| NOW-3 | If the shift is real, why will others not act on it at the same time?           | A lead the founders can hold                | Sector thesis              | all                   | a why-now line | none                  |
| NOW-4 | What has to stay true about the market for this timing to hold?                 | The assumption under the timing             | Sector thesis, Finance     | seed, Series A, later | a why-now line | none                  |
| NOW-5 | Is the change a rule, a technology, a cost or a habit, and when did it happen?  | A dated change that can be checked          | Sector thesis, Product     | all                   | a why-now line | a public record of it |
| NOW-6 | Where is the category going, and where does the company sit when it gets there? | A view of the future, not a forecast figure | Sector thesis, Later stage | Series A, later       | a why-now line | none                  |

## Insight and wedge

| ID        | Question                                                                           | Probes                                     | Lenses              | Stages                | Grounding         | Diligence               |
| --------- | ---------------------------------------------------------------------------------- | ------------------------------------------ | ------------------- | --------------------- | ----------------- | ----------------------- |
| INSIGHT-1 | What do the founders know about this problem that most people in the field do not? | A specific insight, not a general belief   | Pre-seed, Product   | pre-seed, seed        | an insight line   | none                    |
| INSIGHT-2 | How did the founders come to know it?                                              | First-hand experience                      | Pre-seed, Network   | pre-seed, seed        | an insight line   | none                    |
| INSIGHT-3 | Which narrow group of customers is the first market, and why that group?           | A first market with a reason               | Seed, Product       | pre-seed, seed        | an insight line   | none                    |
| INSIGHT-4 | What does winning the first market make easier next?                               | The path from the first market to the next | Seed, Sector thesis | seed, Series A        | an insight line   | none                    |
| INSIGHT-5 | What does the product do that a capable rival could not copy quickly?              | An advantage that lasts, named             | Product, Series A   | seed, Series A, later | a moat line       | none                    |
| INSIGHT-6 | What does the technology do that the product could not do without it?              | Technology tied to a customer outcome      | Product, Operator   | all                   | a technology line | a technical walkthrough |
| INSIGHT-7 | What have the founders been wrong about so far, and what changed their minds?      | Learning rather than certainty             | Pre-seed, Operator  | pre-seed, seed        | an insight line   | none                    |

## Market

| ID       | Question                                                                    | Probes                                       | Lenses                 | Stages          | Grounding     | Diligence                    |
| -------- | --------------------------------------------------------------------------- | -------------------------------------------- | ---------------------- | --------------- | ------------- | ---------------------------- |
| MARKET-1 | Who exactly buys, and how many of them are there?                           | A count of buyers built from the bottom up   | Seed, Finance          | all             | a market line | the source of the count      |
| MARKET-2 | What does each buyer pay, and who in the buyer's company signs?             | The price and the budget holder              | Finance, Operator      | all             | a market line | a signed order or price list |
| MARKET-3 | How was the market size worked out, and from what source?                   | A method and a source, not a headline figure | Finance, Sector thesis | all             | a market line | the sizing model             |
| MARKET-4 | How large can the company get if it wins only the first market?             | The ceiling of the first market              | Later stage, Finance   | Series A, later | a market line | none                         |
| MARKET-5 | Which part of the market will not buy, and why?                             | Who is out of scope                          | Sector thesis, Product | all             | a market line | none                         |
| MARKET-6 | Is the market growing, shrinking or shifting, and how do the founders know? | Evidence for the direction                   | Sector thesis          | all             | a market line | the source                   |
| MARKET-7 | How large could the company become if the plan works?                       | The size of the outcome, reasoned            | Later stage, Finance   | Series A, later | a market line | none                         |

## Competition

| ID     | Question                                                                                 | Probes                                                | Lenses                     | Stages                | Grounding          | Diligence          |
| ------ | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------- | --------------------- | ------------------ | ------------------ |
| COMP-1 | Who else sells the same thing to the same buyer, and why do customers pick this company? | Direct: named rivals and a reason to win              | Product, Sector thesis     | all                   | a competition line | win and loss notes |
| COMP-2 | When a customer chose a rival, what reason did they give?                                | Direct: losses explained honestly                     | Operator, Series A         | seed, Series A, later | a competition line | win and loss notes |
| COMP-3 | Who tried to build this product before, and what did they miss?                          | Direct: earlier attempts studied                      | Sector thesis, Pre-seed    | all                   | a competition line | none               |
| COMP-4 | What other way do buyers meet the same need today?                                       | Indirect: substitutes named                           | Sector thesis, Seed        | all                   | a competition line | none               |
| COMP-5 | Which larger product the buyer already uses could add this as a feature?                 | Adjacent and platform: the feature risk named         | Product, Sector thesis     | all                   | a competition line | none               |
| COMP-6 | What happens to the company if that product adds the feature next year?                  | Adjacent and platform: the plan if it does            | Sector thesis, Later stage | seed, Series A, later | a competition line | none               |
| COMP-7 | What do customers do today when they do not buy anything?                                | Doing nothing: the status quo treated as a competitor | Product, Sector thesis     | all                   | a competition line | none               |
| COMP-8 | Why would a customer who manages this by hand switch now?                                | Doing nothing: what the status quo costs the customer | Product, Seed              | pre-seed, seed        | a competition line | none               |

## Business model

| ID      | Question                                                                 | Probes                                     | Lenses               | Stages                | Grounding             | Diligence                        |
| ------- | ------------------------------------------------------------------------ | ------------------------------------------ | -------------------- | --------------------- | --------------------- | -------------------------------- |
| MODEL-1 | How does the company make money, in one sentence?                        | One simple model, owned plainly            | Seed, Finance        | all                   | a business-model line | none                             |
| MODEL-2 | What does a customer pay, how often, and how was the price set?          | Pricing tested with customers              | Finance, Product     | all                   | a pricing line        | the price list and recent quotes |
| MODEL-3 | What does it cost to win a customer, and how is that measured?           | An acquisition cost defined, with a period | Finance, Series A    | Series A, later       | a business-model line | acquisition cost by channel      |
| MODEL-4 | What does it cost to serve a customer once they are live?                | The cost of delivery defined               | Finance, Operator    | seed, Series A, later | a business-model line | cost of revenue by month         |
| MODEL-5 | How long does a sale take, from first call to signed contract?           | The sales cycle, with an example           | Operator, Series A   | seed, Series A        | a business-model line | the pipeline with dates          |
| MODEL-6 | Do customers spend more over time, and why?                              | Expansion defined                          | Finance, Later stage | Series A, later       | a business-model line | revenue by cohort                |
| MODEL-7 | What has to change for the company to make money on each customer?       | The path to a profit per customer          | Finance, Later stage | seed, Series A, later | a business-model line | none                             |
| MODEL-8 | Is anyone paying yet, and if not, what will make the first customer pay? | The first paid proof                       | Pre-seed, Finance    | pre-seed, seed        | a business-model line | none                             |

## Team

| ID     | Question                                                                           | Probes                        | Lenses                | Stages                | Grounding   | Diligence             |
| ------ | ---------------------------------------------------------------------------------- | ----------------------------- | --------------------- | --------------------- | ----------- | --------------------- |
| TEAM-1 | Why are these founders the ones to build this?                                     | One specific achievement each | Pre-seed, Network     | all                   | a team line | none                  |
| TEAM-2 | How long have the founders worked together, and on what?                           | A shared history              | Pre-seed, Operator    | pre-seed, seed        | a team line | none                  |
| TEAM-3 | Who was the last person hired, and how were they found?                            | The ability to recruit        | Operator, Series A    | seed, Series A, later | a team line | an organisation chart |
| TEAM-4 | Which role is missing, and when will it be filled?                                 | The gap named, with a plan    | Operator, Series A    | all                   | a team line | the hiring plan       |
| TEAM-5 | Who decides when the founders disagree?                                            | Roles that are clear          | Operator              | all                   | a team line | none                  |
| TEAM-6 | Who knows the founders' work and would speak to it?                                | References ready              | Network               | all                   | a team line | a reference list      |
| TEAM-7 | Is every founder working on the company full time?                                 | Commitment stated plainly     | Pre-seed, Seed        | pre-seed, seed        | a team line | none                  |
| TEAM-8 | What does the team need to look like at the next stage, and who leads that change? | A team built to scale         | Series A, Later stage | Series A, later       | a team line | the hiring plan       |

## The ask and use of funds

| ID    | Question                                                                  | Probes                                                    | Lenses                  | Stages                | Grounding           | Diligence                   |
| ----- | ------------------------------------------------------------------------- | --------------------------------------------------------- | ----------------------- | --------------------- | ------------------- | --------------------------- |
| ASK-1 | How much is the company raising, and on what terms?                       | The amount, the instrument, the valuation or cap labelled | Finance, Seed           | all                   | the ask line        | the term sheet or SAFE form |
| ASK-2 | What does this round get the company to, and what if it takes longer?     | Milestones and the downside plan                          | Finance, Seed           | all                   | the ask line        | the operating plan          |
| ASK-3 | Where does the money go, line by line?                                    | Use of funds that adds up to the raise                    | Finance, Operator       | all                   | a use-of-funds line | the budget                  |
| ASK-4 | How many months does the money last at the planned spend?                 | Runway stated with the burn it assumes                    | Finance                 | all                   | a runway line       | the monthly cash plan       |
| ASK-5 | What will be true at the next raise that is not true today?               | The milestone the next investor needs to see              | Seed, Series A, Finance | seed, Series A        | the ask line        | none                        |
| ASK-6 | Why this amount, and not more or less?                                    | The amount tied to the plan                               | Finance                 | all                   | the ask line        | the operating plan          |
| ASK-7 | What does the cap table look like after this round?                       | Ownership after the round, with the pool counted          | Finance, Series A       | seed, Series A, later | the ask line        | the cap table               |
| ASK-8 | What can the business do with the new money that it cannot do without it? | What the new money changes                                | Later stage, Finance    | later                 | the ask line        | the operating plan          |

## The round

The first six rows are the standing prep questions in the skill, word for word: every founder prepares them, and they
are not refuted.

| ID      | Question                                                      | Probes                                            | Lenses            | Stages                | Grounding    | Diligence             |
| ------- | ------------------------------------------------------------- | ------------------------------------------------- | ----------------- | --------------------- | ------------ | --------------------- |
| ROUND-1 | Which other investors are you meeting, and who has committed? | A true answer, never an implied interest          | Network, Finance  | all                   | standing     | none                  |
| ROUND-2 | Will your existing investors take part in this round?         | The insiders' answer as the founder has it        | Network, Finance  | all                   | standing     | none                  |
| ROUND-3 | Who has passed, and why?                                      | The reasons given, and what changed since         | Network           | all                   | standing     | none                  |
| ROUND-4 | Whom will the partner call, on your list and off it?          | References ready and briefed                      | Network           | all                   | standing     | a reference list      |
| ROUND-5 | What happens if this round does not close?                    | Runway on today's cash, what gets cut, the plan   | Finance, Operator | all                   | standing     | the monthly cash plan |
| ROUND-6 | What happens after this meeting, and when?                    | A question for the founder to ask, never to guess | Network           | all                   | standing     | none                  |
| ROUND-7 | Who is leading the round, and who sets the terms?             | The lead named only as the founder states it      | Finance, Network  | seed, Series A, later | a round line | none                  |
| ROUND-8 | How much of the round is committed, and by whom?              | Committed money stated, never implied             | Finance           | all                   | a round line | signed commitments    |

## Risks and what breaks

| ID     | Question                                                                      | Probes                              | Lenses                 | Stages                | Grounding   | Diligence          |
| ------ | ----------------------------------------------------------------------------- | ----------------------------------- | ---------------------- | --------------------- | ----------- | ------------------ |
| RISK-1 | What is the one thing most likely to kill the company?                        | The obvious risk named, with a plan | Operator, Pre-seed     | all                   | a risk line | none               |
| RISK-2 | What would make this fail even if the team executes well?                     | An outside risk named               | Sector thesis, Finance | all                   | a risk line | none               |
| RISK-3 | Which customer, supplier or partner could the company not survive losing?     | Dependence named                    | Operator, Finance      | seed, Series A, later | a risk line | the main contracts |
| RISK-4 | Which rule or law could change the business, and what is the plan if it does? | Regulatory exposure                 | Sector thesis          | all                   | a risk line | legal review notes |
| RISK-5 | What broke most recently, and how was it fixed?                               | Honesty about operations            | Operator               | all                   | a risk line | an incident log    |
| RISK-6 | What gets done in the next quarter, and how will the team know it worked?     | Near-term execution with a test     | Operator, Seed         | all                   | a risk line | the quarter's plan |
| RISK-7 | What would make the founders stop and work on something else?                 | A clear point at which to stop      | Pre-seed, Operator     | pre-seed, seed        | a risk line | none               |
| RISK-8 | Which assumption in the plan has been tested least?                           | Planning that knows its weak point  | Finance, Series A      | all                   | a risk line | the operating plan |
