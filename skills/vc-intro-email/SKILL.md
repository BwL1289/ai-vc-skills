---
name: vc-intro-email
description: Helps a founder write the emails that open investor conversations, from the founder's own material only (deck, one-pager, the metrics the founder states). It drafts a forwardable intro blurb a mutual contact can send on, with a short note asking that contact for the intro, a cold email, and two follow-ups, each short with one ask and every figure quoted exactly as the founder gave it. A reader pass flags hype words, claims with no source the founder can show, and figures that disagree across the founder's documents, and hands those to the vc-claims-check skill. It never looks up the investor or anyone's contact details, never sends, and uses no personal data beyond what the founder pastes. Use when a founder says write an intro blurb, draft a forwardable email, write a cold email to a VC, help me follow up with an investor, or ask for a warm intro to a fund. Never invents traction. Not investment advice.
---

# VC intro email

Helps a founder write the short emails that get a first meeting: a blurb a mutual contact can forward as it stands, a
note asking that contact for the intro, a cold email for when there is no one to introduce them, and two follow-ups.
Every line comes from the founder's own material, and every figure is quoted exactly as the founder gave it. A reader
pass then reads the drafts the way a busy investor skims them and flags hype words, claims the founder cannot show a
source for, and figures that disagree across the founder's documents, which go to the vc-claims-check skill. The
founder sends every email; the skill sends nothing and looks nobody up.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
writes in a named person's voice, never names an investor to write to, never looks up an investor, a firm or anyone's
contact details, and never adds a figure, customer, credential or fact the founder did not give.

## When to use it

- "Write an intro blurb I can send to my contact." "Draft a forwardable email." "Write a cold email to a VC." "Help me
  follow up with an investor who hasn't replied." "Ask for a warm intro to a fund."
- Pasted material: the deck, the one-pager, the latest investor update, the metrics the founder states, the earlier
  emails to this investor, and what the founder knows of the investor and the connector. Any of these may come as a
  file the agent can read in this session.
- Hand off:
  - Messaging (the one-liner, the story and the say-and-avoid list): the vc-positioning skill (preview). Point the
    founder to it when the one-liner is not clear; an email cannot fix an unclear story.
  - Each claim's evidence, and figures that disagree across the documents: the vc-claims-check skill (preview). The
    reader pass hands it every such flag.
  - The update the founder sends prospective investors once a conversation has started: the
    vc-prospective-investor-update skill (preview).
  - The deck the email links to: the vc-deck-review skill.
  - A reply to an investor who passed: the vc-pass-debrief skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess, and never offer a figure or a reason to fill
in. When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and list
what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what was read
from each. A place you could not read (a slide that is only a picture, a page whose text did not come out, a file that
opened only in part) is listed as not read and asked for, never filled in from its title or the places around it, and a
figure is never read off a chart or a picture. Ask only for what you could not read and what the file does not show
(speaker notes, the figures behind a chart, an input below that it leaves out), and never ask the founder to paste what
you already read.

1. **The founder's material:** the one-liner, the deck or one-pager, and each metric to show as the founder states it,
   with its definition and period, each named by the document it comes from.
2. **Who it goes to:** the investor's name and firm as the founder writes them, and why this investor, in the
   founder's words (what the founder knows of their interests, from the founder's own reading or a conversation). The
   skill adds no reason of its own.
3. **For a forwardable blurb, the connector:** who will forward it, how they know the founder and the investor, in the
   founder's words, and whether the founder may name them.
4. **The ask:** one thing (a call, a meeting), and the raise as the founder wants to state it, if at all.
5. **For follow-ups:** what was sent before, with its date, and anything new since, in the founder's words.
6. **The sign-off:** the founder's name, title and company as they want them to appear.

A missing input does not stop the draft. It becomes a bracketed ask in the email (`[paying customers, as of which
date]`), never a plausible figure, reason or name. With no material at all (no one-liner, no metric, no reason for this
investor), write no email: give the shape below with every line a bracketed ask, ask for the inputs in one message, and
stop.

## The drafts

Each draft is short, in the founder's voice, with one ask, and reads on its own.

- **The note to the connector:** a few lines asking whether they would introduce the founder, saying why this investor
  in the founder's words, and asking them to check with the investor first that the intro is welcome (a common
  practice, unverified). The forwardable blurb sits below it.
- **The forwardable blurb:** written so the connector can forward it unchanged: what the company does in one plain
  sentence (the founder's one-liner), one or two lines of the founder's strongest facts with their figures as stated,
  why this investor in the founder's words, and the one ask. No attachment unless the founder gives one; a deck link is
  `[deck link, if you send one]`.
- **The cold email:** a subject line and at most five short sentences: who the founder is, what the company does, the
  strongest facts with their figures as stated, why this investor, and the one ask.
- **Follow-up 1:** shorter than the email, with one new fact from the founder's material since the last email, or a
  bracketed ask for one; never the same email again, never a guilt line ("just bumping this").
- **Follow-up 2:** the last one: one line of news if the founder has it, and an easy way to say no; it offers to keep
  the investor updated, which the vc-prospective-investor-update skill drafts.
- **Timing:** the founder picks when to send each follow-up; the skill suggests no interval.

## Figures as the founder gave them

- **Exactly as stated:** every figure keeps the founder's own words, units, period and form: "$38k MRR in October"
  stays "$38k MRR in October", never turned into a yearly figure, never "about $40k" or "nearly $40k". A figure with
  no period gets a bracketed ask for it.
- **From one document only when they agree:** a figure that appears in two of the founder's documents with different
  values for the same metric and period goes into no draft until the founder says which is right; the draft holds a
  bracketed ask naming both, and the reader pass flags it.
- **Never combined:** no growth rate, multiple, total or "doubled" worked out from two figures.
- **A claim the material does not state in those words** ("we tripled revenue", asked for in the request but not in
  the deck or one-pager): the draft quotes the figures the material does state, as stated; the reader pass flags the
  claim for the vc-claims-check skill; and the skill never says whether the claim holds, since that needs arithmetic.

## Reader pass

After drafting, read every draft once more for what costs an investor's attention or trust, and flag each hit: quote
the line, name the pattern, say what an investor is likely to read in it, and give the fix using only the founder's
facts or a bracketed ask. Signals, not rules: a founder may have a reason. Every row is this skill's own judgment,
unverified.

| Pattern                                                                                           | What an investor is likely to read in it          | Fix                                                                     |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------- |
| Hype words: "revolutionary", "disruptive", "game-changing", "world's first", "the next big thing" | Nothing they could check; the claim does the work | What the product does, for whom, in plain words                         |
| A claim with no source the founder can show ("the leading", "the fastest-growing", "the only")    | A claim the first call will test                  | The founder's evidence, or drop the claim; to the vc-claims-check skill |
| A figure that disagrees with the same figure in another of the founder's documents                | Two numbers for one fact                          | One figure, confirmed by the founder; to the vc-claims-check skill      |
| A figure with no period or definition ("$1M in revenue")                                          | Cannot tell what is counted, or when              | The figure with its definition and period, as the founder states it     |
| "AI-powered" with nothing that says what the model does                                           | A label, not a reason                             | What the model does for the customer, or drop the label                 |
| Other investors named or hinted at ("several funds are already in", "closing fast")               | Pressure, and it may break a confidence           | Leave other investors and deadlines out                                 |
| More than one ask, or no ask                                                                      | Nothing to act on                                 | One ask: a call or a meeting                                            |
| Flattery that rests on a fact the founder did not give ("loved your recent post")                 | A line written without reading their work         | The founder's own reason for this investor, or drop it                  |
| A long email, paragraphs of context, an attachment not asked for                                  | It goes unread                                    | At most five short sentences; a link only if the founder gives one      |
| A request for an NDA or for feedback on the whole deck                                            | A request a stranger is unlikely to grant         | Ask for the meeting                                                     |

Every flag on a claim's source or on figures that disagree is handed to the vc-claims-check skill, with the line and
the documents it appears in. The drafts are revised for every other flag.

## Personal data

- The investor and the connector are names the founder supplies, written as the founder writes them. The skill adds
  no name, title, firm, email address, phone number or link, and looks no one up: no search for an address, a
  portfolio, a post or a profile.
- Each draft's address line is `[the investor's email, from you]` unless the founder pasted the address; a pasted
  address is used only in that draft's address line.
- A detail about the investor or the connector goes into a draft only when the founder gives it and it is the
  founder's own reason for writing; the connector is named only with the founder's say-so.
- It keeps nothing between conversations.

## Steps

1. **Read the material** and list each figure word for word with the document it comes from; put every figure that
   appears in two documents side by side, as stated.
2. **Draft the note to the connector and the blurb, the cold email and the two follow-ups** (The drafts), every
   figure as the founder gave it (Figures as the founder gave them), every gap a bracketed ask.
3. **Run the reader pass** (Reader pass) and revise the drafts; hand every source and disagreement flag to the
   vc-claims-check skill.
4. **Check before answering.** Every fact in a draft appears in the founder's material; every figure is quoted as the
   founder gave it; no figure that disagrees across documents is in a draft; each draft has one ask; no other investor
   is named or hinted at; no name, address or detail appears that the founder did not give; no sentence speaks as an
   investor or imitates a named person. Never work out how two of the founder's figures relate (a difference, a sum, a
   ratio or multiple, a share left over, "doubled") in a rewrite, a line or a table cell unless the founder's material
   states it or a tool returned it; quote both figures as stated instead ("from 2,000 to 4,500", never "more than
   doubled").

## Answering

Lead with the drafts, then the flags.

1. **The drafts,** ready to copy: the note to the connector with the forwardable blurb under it, the cold email with
   its subject line, follow-up 1 and follow-up 2, every gap a bracketed ask.
2. **Reader pass:** each flag with the line quoted, its pattern, what an investor is likely to read in it and the fix;
   those handed to the vc-claims-check skill marked so.
3. **Figures used:** each figure in the drafts, as stated, with the document it comes from; each figure that disagrees
   across documents, side by side, waiting for the founder's choice.
4. **Open asks:** every bracketed gap in one list, to answer in one sitting.
5. **Close:** this is not investment, legal or tax advice; the founder sends every email; a lawyer should look at an
   email that mentions a raise before it goes to people the founder does not know, and customers named should have
   agreed to be named.

## Sources

None. This skill's authors read no public source on investor emails for it, so it cites none. The drafts' shapes, the
reader pass's patterns and the asking-first note to the connector are this skill's own judgment, common in founder
advice but unverified.

## Limits

- Not investment, legal or tax advice. It does not say whom to write to, whether to raise, or what to raise.
- No investor research: it names no investor to write to, looks up no investor, firm, portfolio, post or contact
  detail, and keeps no list between conversations.
- It drafts and sends nothing: no email, sequence, schedule or tracker entry.
- It never invents or strengthens a figure, customer, credential or fact, and never rounds, converts or combines a
  figure.
- It never role-plays or writes in the voice of a named investor, firm or author; asked to, it declines in one line
  and writes in the founder's own voice.
- No arithmetic and no calculator tool: figures are quoted as stated.
- It works from the founder's text and sends nothing anywhere.
