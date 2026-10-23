---
name: weekly-creative-readout-ad-creative
description: Assembles the Monday creative readout from the other skills' outputs and states what to ship, what to cut and what to test this week, in language a client will read without a glossary. Use when the weekly reporting slot comes round, or when a stakeholder asks what the creative programme did last week. Boundary against its siblings: this skill composes finished diagnoses and never produces one itself, so a fatigue verdict comes from creative-fatigue-read-ad-creative, a test result from creative-test-readout-ad-creative and a funnel verdict from losing-ad-diagnosis-ad-creative. Boundary against creative-brief-from-account-data, which is easy to confuse with this skill's degraded path because both start from the same weekly ad-level export and both state spend, delivery share and the collapsed angle count: that skill turns those figures into production slots for the next round, and this one reports the week that has happened and commissions nothing. Route on the deliverable, a report or a brief, not on the export.
---

# Weekly Creative Readout

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.

This is the only composing skill in the pack. It runs no new arithmetic and
issues no diagnosis of its own; it collects verdicts, resolves conflicts
between them and writes the week in plain words.

## Use this skill when

The weekly reporting slot is due, or a decision meeting needs one page. It is
not the place to diagnose a specific ad mid-week; route that to the skill that
owns it and bring the verdict back here.

It is also not the place to decide what gets built next.
`creative-brief-from-account-data-ad-creative` runs on the same weekly ad-level
export as the degraded path below, and reports the same three figures from it,
spend, delivery share and the collapsed angle count, so the two are genuinely
hard to tell apart at the point of routing. The deliverable separates them. If a
designer, editor or freelancer is waiting for instructions, it is that skill. If
a client or a meeting is waiting for the week, it is this one. This skill names
production as a priority where coverage is short, and stops there; it never
writes the brief items.

## Required input

Four upstream outputs, each optional but each named when absent:

- Asset coverage check, for angle, format, ratio and library age.
- Creative fatigue read, one per creative proposed for cutting.
- Creative test readout, one per finished test.
- Losing ad diagnosis, one per ad proposed for rewriting.

Plus the week as dates, spend by ad set, any change a human already made inside
the week, and which Advantage+ creative enhancements changed inside it
(`test.creative_enhancements_rule`). An enhancement switched on mid-week changes
the served asset, so any week-on-week creative comparison crossing that date is
comparing two things.

On a normal Monday none of the four exist. What exists is a raw ad-level export,
and the readout still has to happen, so the degraded path below is the default
case rather than the exception. The minimum this skill will run on is that
export: ad name or ID, ad set, spend, impressions, link clicks and conversions
for the week, with the attribution setting stated.

## Analysis workflow

1. List which of the four upstream outputs exist for this week and which do
   not. An absent input is written into the readout as `missing`, never
   silently skipped and never replaced by this skill's own judgement.
2. For each absent input, state the one decision it would have unblocked and
   what it costs to leave it unresolved for another week.
3. Collect every `ship`, `cut`, `test`, `rewrite`, `investigate` and `monitor`
   decision from the supplied outputs, carrying each one's evidence label and
   confidence through unchanged. Never upgrade a confidence on aggregation.
4. Resolve conflicts. Where a test readout says ship and a fatigue read on the
   same creative says cut, the later window wins and the conflict is stated in
   the readout rather than quietly dropped.
5. Drop any recommendation whose source row is `low` confidence out of the ship
   and cut lists, into monitor, with the date it becomes readable.
6. Check this week's proposed tests against `test.concurrent_variant_cap` and
   `test.one_change_rule` before they are committed, so the readout does not
   commission a test that cannot be read.
7. Check the coverage input against `coverage.stale_spend_share`, reading the
   share of each ad set's spend that rode old creatives rather than the launch
   date of the newest file, and where the share is above the key, put
   production ahead of optimisation in the priorities.
8. Say something about the money, because a readout that names what to ship and
   cut while issuing no number about spend has a hole in the middle of it.
   Judge every proposed shift against `money.relevance_floor`: a difference
   that does not move cost per acquisition by that much is not a reason to move
   budget, and the readout says so instead of recommending a shuffle. Where a
   move is justified, state it as a single step inside `money.budget_step_cap`,
   with the date it may next be stepped again, and hand it to a person. This
   pack never moves a budget. Where cost per acquisition was not supplied, name
   the decision the readout therefore cannot make rather than substituting a
   rate.
9. Run the degraded path when upstream outputs are missing, which is most
   weeks. From a raw ad-level export alone this skill may state: spend by ad
   set and how it moved; which creatives actually carried the delivery, which
   sat under `delivery.never_delivered_floor` and therefore did not run at all,
   and which were flagged by `delivery.starved_flag`, which is a different line
   in the readout because those ones did run and the platform kept declining to
   spend on them; which creatives clear `delivery.ranking_floor` and may
   therefore be compared with each other at all; the count of live creatives and, where angle sentences were supplied,
   the collapsed angle count against `coverage.angles_per_ad_set`; the share of
   spend on old creatives against `coverage.stale_spend_share`; and any
   human-made change already logged for the week. It may not state, and writes
   in as `missing` instead: any fatigue verdict, any winner or tie between
   variants, and any funnel-stage diagnosis of a weak ad. Those three sections
   carry the name of the skill that owns them and the decision each would have
   unblocked. The degraded readout is a shorter document that is true, not the
   same document with the gaps filled from the export.
10. Rewrite every line in client-readable language: what happens, to which ad,
    and what it is expected to change. No threshold keys and no internal labels
    in the client-facing paragraphs; those stay in the table.

## Decision rules

- Ship only what arrived as `ship` at `high` or `medium` confidence from a test
  readout.
- Cut only what arrived as `cut` from a fatigue read that satisfied
  `fatigue.verdict_rule`. A creative proposed for cutting without that verdict
  goes to monitor with its re-read date.
- An Advantage+ enhancement changed inside the week, or nobody can say: no
  week-on-week creative comparison is presented as one. Under
  `test.creative_enhancements_rule` the readout says the served asset changed
  mid-week and names that as the reason a comparison is absent, rather than
  printing the numbers and leaving the client to draw the line.
- Test only pairs that satisfy `test.one_change_rule` and fit inside
  `test.concurrent_variant_cap`.
- Where the coverage check is missing, do not commission production. State that
  the brief is blocked on a count nobody has run.
- No upstream skill output exists at all: produce the degraded readout. State
  the export-only sections, write the fatigue, test and diagnosis sections as
  `missing` with the skill that owns each, and do not let the export's own
  numbers stand in for a verdict. A ranked list of last week's ads is not a
  test result and is never presented as one.
- A budget move is proposed and the difference behind it is inside
  `money.relevance_floor`: do not recommend the move. Say the difference is
  real and not worth spending against, which is a finding.
- A budget move survives that floor: recommend exactly one step within
  `money.budget_step_cap` and name the earliest date for the next step. Larger
  steps destabilise delivery and make next week's readout unreadable.
- Cost per acquisition not supplied for the week: name the ship-and-cut
  decisions that therefore cannot be made, rather than making them on rates.
- Anything touching `claims.restricted_topics` is `approval_needed` before it
  reaches the client page.

## Output format

Open with one line: what changed in the creative programme this week.

| Ad or ad set | Decision | Why, in one clause | Source skill | Evidence | Confidence |
|---|---|---|---|---|---|

Then three short client-readable paragraphs, ship, cut, test this week, then
`What this could not see`, `Missing data`, `Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser.

Inputs supplied: a coverage check reporting 9 live creatives across 2 angles,
below `coverage.angles_per_ad_set`, with 71 per cent of the week's spend riding
creatives older than the age in `coverage.stale_spend_share`; two fatigue reads,
one satisfying `fatigue.verdict_rule` and one where only the CTR signal moved.
Spend for the week 18,400 across two ad sets, cost per acquisition 47 in ad set
A against 44 in ad set B. No test readout was supplied, and no losing ad
diagnosis.

Reading: one cut is supported, the creative whose fatigue read satisfied
`fatigue.verdict_rule`. The second creative moves to monitor, because one signal
is not fatigue and this skill does not re-decide that. Coverage puts production
ahead of optimisation, since the angle count is below
`coverage.angles_per_ad_set` and the spend share on old creatives is above
`coverage.stale_spend_share`, so next week's numbers will again be read on
ageing supply.

Money: the request to move budget from ad set A to ad set B is declined. 47
against 44 is a difference of 3, which is 6.4 per cent of 47, inside
`money.relevance_floor`, so it is not worth spending against and the readout
says which key stopped it. Had it cleared, the recommendation would have been a
single step inside `money.budget_step_cap` with the date it could next be
stepped, handed to a person to make.

Declined: nothing is shipped or scaled this week. The test readout is
`missing`, so no variant has a comparison against a control, and naming a
winner from raw weekly figures would invent a result the pack refuses to
produce. That absence is written into the readout with its cost: the hook test
that finished on Friday stays unread, so the rollout decision slips a week.

Output: one `cut`, one `monitor`, one `approval_needed` on production budget,
and `missing` against the test readout row.

## Guardrails

- Never issue a fatigue, test or funnel verdict in this skill.
- Never upgrade a confidence label while aggregating.
- Never present an absent input as a clean week.
- Never put threshold keys or internal labels into the client-facing
  paragraphs.
- Do not action anything. This readout is a decision put in front of a human.
