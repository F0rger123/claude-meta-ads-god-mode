---
name: creative-brief-from-account-data-ad-creative
description: Turns a pasted ad-level performance export into the brief for the next production round, so the next batch is derived from what the account already ran rather than from a brainstorm. Use when creative production is about to start and someone needs to decide what gets made next. Boundary against siblings: winning-ad-teardown dissects one named ad into a pattern, angle-inventory maps which arguments the library has already covered, asset-coverage-check counts what is live right now, and none of the three issues production instructions. Boundary against weekly-creative-readout, which starts from the same weekly ad-level export: that skill reports the week that has happened to a client and commissions nothing, while this one commissions the next round; if the deliverable is a Monday report rather than a set of production slots, it is that skill and not this one.
---

# Creative Brief From Account Data

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.
Input is an export, output is a brief a designer or copywriter can build from
without asking a follow-up question.

## Use this skill when

A production round is about to be commissioned and the account has run enough
ads to have an opinion. Use it when a designer, editor or freelancer is waiting
for instructions, when a monthly creative batch is being scoped, or when the
last batch was briefed from opinion and nobody can say what it was answering.
Do not use it to dissect one ad into a transferable pattern; that is
`winning-ad-teardown-ad-creative`. Do not use it to audit coverage on its own,
and route that question by its window rather than by the word coverage: what is
live right now, and whether this week's spend can teach anybody anything, is
`asset-coverage-check-ad-creative`; what the account has argued across the whole
served library including everything paused is
`angle-inventory-ad-creative`. This skill consumes a coverage count, it does not
produce one.

Do not use it for the Monday report either. `weekly-creative-readout-ad-creative`
starts from the same weekly ad-level export and also states spend, delivery
share and the collapsed angle count, so the two look alike at the point of
routing. They differ on the deliverable: that skill writes the week that has
happened for a client and commissions nothing, and this skill commissions the
next production round. If nobody is waiting to build anything, it is that skill.

## Required input

- An ad-level export covering at least `test.min_runtime`: ad name or ID, spend,
  impressions, link clicks, link CTR, conversions, cost per conversion, and the
  first date the ad served.
- The creative itself, or a description of each ad's hook, offer and format.
- The objective the campaign optimises toward, and which conversion action
  counts as primary.
- Any creative or budget change made inside the window, with dates.
- Production constraints: who builds it, what assets exist, what cannot be shot.

## Analysis workflow

1. Confirm the export is readable as creative evidence: check the date range
   against `test.min_runtime` and the per-ad volume against
   `test.volume_floor`. Ads below the floor enter the brief as context, never as
   proof, and every finding drawn from them is capped at `low` confidence.
   Then check each ad against `delivery.never_delivered_floor`. An ad under it
   did not lose, it did not run: mark it `never_delivered`, drop it out of the
   ranking and out of any cut list, and never let it enter the brief as a failed
   angle. Its angle goes back on the untested list. Then check each surviving ad
   against `delivery.ranking_floor`. Below that share the spend is too
   concentrated for a like-for-like comparison, so the ad may appear as context
   but not inside the ranking the brief is built from.
2. Label each ad with its angle stated as a sentence, its offer and its format.
   Use the definitions of creative and angle fixed in `thresholds.md`.
3. Rank on the objective's own metric, not on CTR, and record which metric you
   ranked on. `reporting.no_view_through_in_ctr` explains why a CTR ranking can
   invert a conversion ranking.
4. Collapse ties, and pick the key by what the difference is measured on. A gap
   in cost per acquisition, which is the metric most briefs are actually ranked
   on, is judged by `money.relevance_floor` and by nothing else; that key owns
   every cost per acquisition comparison in this pack, so the same gap is not a
   tie here and actionable in the readouts. `test.material_gap` stays where it
   belongs, on rate differences such as link CTR. Say which of the two you
   applied, collapse anything inside it into a single tie, and do not brief
   against a difference you have just called a tie.
5. Separate the angle effect from the execution effect. Where an angle appears
   in fewer than `coverage.formats_per_angle`, the result is about that one
   execution and the brief says so, labelled `hypothesis`.
6. Check supply: read the share of ad set spend riding old creatives against
   `coverage.stale_spend_share`, and the live angle count against
   `coverage.angles_per_ad_set`. The supply reading is on money rather than on
   the launch date of the newest file, because an account shipping every month
   always has a young newest asset while most of its budget can still sit on a
   handful of files from the spring. A shortfall on either sets the size of the
   round.
7. Where any figure in the brief rests on this period's conversions against a
   previous period's, either wait out the account's attribution window or state
   `reporting.conversion_lag_bias` next to the number. The current window is
   still filling in while the prior one has closed, so a flat month reads as a
   falling one and the brief would commission work against a decline nobody
   had.
8. Write the brief. Each item names the angle, the one element it changes
   against a named control (`test.one_change_rule`), the format, and the result
   that would make it a keeper. Cap the round at `test.concurrent_variant_cap`
   per ad set.
9. Mark every factual claim the brief asks a writer to make with
   `[claim: needs source]` under `claims.evidence_rule`, and list what you
   declined to brief.

## Decision rules

- Angle beat its control on cost per acquisition by more than
  `money.relevance_floor`, or on a rate by more than `test.material_gap`, and
  cleared `test.volume_floor`: `ship` more of that angle, confidence `high` where
  the comparison came from a real split. Where the ads simply co-existed in one ad
  set, `test.assignment_rule` caps the row at `medium` and the brief says so.
- Cost per acquisition gap inside `money.relevance_floor`: a tie, whatever the
  rate table shows, and it is not briefed as a learning. That key owns this
  comparison and `test.material_gap` is not read against it here, so a brief
  written from this skill and a readout written from the money keys reach the
  same verdict on the same gap.
- Any verdict arriving from the `early.*` block: it is not a brief input. Under
  blocking rule 10 in `../AGENTS.md`, everything in that block is `low` by
  definition, exists to give a decision on creatives that will never reach
  `test.volume_floor`, and does not become evidence by being repeated. A
  creative cut on `early.hook_rate` or `early.cost_multiple` may be named as
  context, and its angle goes back on the untested list; it never enters the
  ranking the brief is built from and never counts as an angle that failed.
- Angle won on thin volume: `test` it again with a bigger share, confidence
  `low`, and say the floor was the missing condition.
- Angle lost in one format only: `rewrite` in the missing format rather than
  cutting the angle.
- Live angles under `coverage.angles_per_ad_set`: the round's first job is a new
  angle, not a new execution.
- Ad under `delivery.never_delivered_floor`: it is not a finding of any kind.
  `test` its angle again with a share that lets it run, and say the previous
  attempt never delivered.
- Ad above that floor but under `delivery.ranking_floor`: it ran, so it is not
  `never_delivered`, but it is not ranked either. Carry it as context and say
  which question its spend share stopped it answering.
- Share of spend on old creatives above `coverage.stale_spend_share`: size the
  round on supply first. Optimisation of the current set cannot fix a budget
  riding files nobody has replaced.
- Winner cannot be explained by anything in the export: `investigate`, and label
  the explanation `hypothesis` under `reporting.no_causal_read_from_export`.
- Any brief item touching `claims.restricted_topics`: `approval_needed`.

## Output format

No verdict line. A ranked evidence table, then the brief.

| Ad | Angle | Format | Ranked metric | Evidence label | Confidence | Decision |
|---|---|---|---|---|---|---|

Then one brief item per production slot: angle sentence, control it tests
against, single changed element, format, success condition. Then
`What this could not see`, `Missing data`, `Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser. Export covers 28 days,
11 ads. "Agency cost" angle: 62 conversions, cost per conversion 41. "Setup
speed" angle: 9 conversions, cost per conversion 38. "Founder story": 57
conversions, cost per conversion 44.

Two of the 11 ads fall under `delivery.never_delivered_floor`. They are marked
`never_delivered`, kept out of the ranking, and their angles go back on the
untested list rather than into the brief as things that failed. A third ran but
sat under `delivery.ranking_floor`, so it is carried as context and left out of
the ranking, which is a different exclusion for a different reason. The month against previous month conversion
comparison the client asked for is not stated at all: the current window is
still inside the account's attribution window, so `reporting.conversion_lag_bias`
biases it against the present, and reporting it would commission work against a
decline nobody has.

Reading: the ranked metric is cost per conversion, so the gap is judged on
`money.relevance_floor` and not on `test.material_gap`. Agency cost at 41
against founder story at 44 is a difference of 3, which is 7.3 per cent of 41,
inside `money.relevance_floor`, so they are a tie and no winner is named. Setup speed looks
cheapest but sits far under `test.volume_floor` at 9 conversions, so its
confidence is `low` and it is briefed as a retest, not as a finding. The claim
that agency cost wins on creative merit is refused: two budget edits fall inside
the window, which caps that row at `low` under the shared confidence scale.

Brief: three slots. One retest of setup speed at a larger share, one new angle
because only two live angles clear `coverage.angles_per_ad_set`, one format
extension of founder story into video. Declined: a "saves 37 per cent versus an
agency" line, because no source was supplied for the figure. Also declined as an
input: two further ads, both of which did deliver, were cut last week on
`early.cost_multiple`, and those verdicts stay out of the ranking under blocking
rule 10 in `../AGENTS.md`. Their angles go back on the untested list rather than
into the brief as arguments that failed.

## Guardrails

- Never brief a difference smaller than `money.relevance_floor` on cost per
  acquisition, or smaller than `test.material_gap` on a rate, as a learning.
- Never carry an `early.*` verdict into the brief as evidence.
- Never rank creatives on CTR when the objective is conversions.
- Never write a number into a brief that the user did not evidence.
- Do not upload, launch or pause anything. The brief is a decision for a human.
