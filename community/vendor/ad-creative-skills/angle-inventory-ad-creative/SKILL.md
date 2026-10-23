---
name: angle-inventory-ad-creative
description: Inventories the distinct arguments an account has genuinely put in front of buyers, collapses the ones that are the same argument in different clothes, and names the untested arguments that deserve a slot. Use when the account feels like it has tested a lot yet keeps learning nothing. Boundary against siblings: this skill answers what the account has actually argued, across the whole served library, live and paused, historically; asset-coverage-check answers the different question of whether enough variety is live right now to learn anything from this week's spend. creative-brief-from-account-data ranks performance and issues production slots, winning-ad-teardown decomposes a single ad into a pattern, and this skill produces no ranking.
---

# Angle Inventory

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.
The deliverable is a coverage map: which arguments exist, which are duplicates
wearing new art, and which gaps are worth filling.

## Use this skill when

The library has grown but the arguments have not, or an account claims dozens of
tests and cannot name what any of them established. Use it before a quarterly
plan, when onboarding an account whose history is unknown, or when every ad in an
ad set turns out to say the same thing. It counts and de-duplicates arguments
across the whole served library, live and paused, back through the period under
review, and its question is historical: what has this account actually argued.
Do not use it to ask whether enough variety is live right now to learn from this
week's spend, which is `asset-coverage-check-ad-creative` and reads only what is
serving today. It does not rank creatives or issue production instructions
(`creative-brief-from-account-data-ad-creative`) and it does not decompose one ad
(`winning-ad-teardown-ad-creative`).

## Required input

- The full list of ads served in the period under review, live and paused, with
  their headline, primary text and creative.
- Ad set membership for each ad, since `coverage.angles_per_ad_set` is read per
  ad set, not per account.
- First and last served date per ad.
- Format and aspect ratio per ad, to read against `coverage.formats_per_angle`
  and `coverage.ratio_set`.
- Optional: spend and conversions per ad, used only to mark which angles were
  ever given a readable chance.

## Analysis workflow

1. Write each ad's angle as one sentence in the buyer's terms, using the
   definition of angle fixed in `thresholds.md`. Format, offer and visual are not
   angles and are recorded in separate columns.
2. Collapse duplicates. Two angle sentences are one angle under
   `coverage.angle_distinctness` when they share their main claim AND their
   reason for it, which is a test on the argument, not on the wording. "Save
   time" and "stop wasting hours" share a word in neither position and are still
   one angle. Do not apply the noun and verb test here; that one belongs to
   `coverage.rsa_headline_floor` and is about headline slots. Record the
   collapsed count
   alongside the raw ad count; the gap between them is usually the finding.
3. Per ad set, count the surviving distinct angles against
   `coverage.angles_per_ad_set` and note where the recalibration to two applies
   because the ad set sits under `test.volume_floor`.
4. Per angle, count formats against `coverage.formats_per_angle` and ratios
   against `coverage.ratio_set`. An angle that only ever ran as one static in one
   ratio has not been tested, it has been mentioned.
5. Mark each angle tested or untested on evidence, not on intent. Tested means it
   ran for at least `test.min_runtime` and reached `test.volume_floor`, or
   `test.click_floor` where the read was on CTR. Everything else is `needs_data`.
6. Read supply against `coverage.stale_spend_share`: work out how much of each
   ad set's spend in the period rode creatives older than the age that key
   names. The reading is on money, not on the launch date of the newest file, so
   an account shipping constantly can still fail it. Above the share, the account
   is spending its inventory and the gap list is the pipeline.
7. Exclude every creative below `delivery.never_delivered_floor` from the tested
   and untested judgement. That creative did not lose its angle, it never ran.
   Mark it `never_delivered`, keep it out of any ranking or cut list, and count
   its angle as untested rather than as tried and failed. A creative that cleared
   exposure but stayed under `delivery.ranking_floor` is a separate case: it ran
   and it may carry a verdict of its own, but its share of delivery is too thin
   for its angle to count as tested here, so that angle also stays on the
   untested list.
8. Name the untested angles worth a slot. Derive each from something the user
   supplied: an objection they hear, a reason customers gave, a segment nobody
   addressed. Do not derive one from category convention, and label every
   proposed angle `hypothesis` until it has run.
9. Order the gaps by how cheaply each can be produced from assets that already
   exist, and cap the recommended slate at `test.concurrent_variant_cap` per ad
   set.

## Decision rules

- Distinct angles in an ad set below `coverage.angles_per_ad_set`: the gap is the
  finding, and the next round is angles rather than executions.
- Two angles collapse into one: `cut` the redundant slot and say what it was
  duplicating. Redundant slots are the mechanism by which an account tests a lot
  and learns nothing.
- Angle ran under `test.volume_floor`: `test` again with a real share, confidence
  `low`. Never `cut` an angle that never got a readable sample.
- Every creative carrying an angle sat under `delivery.never_delivered_floor`:
  the angle is `needs_data`, not a loser. Record it as untested, keep it out of
  the cut list, and say the ad set never gave it a share of delivery.
- Every creative carrying an angle ran but stayed under
  `delivery.ranking_floor`: the angle is `needs_data` on the tested question.
  Those creatives may still have been cut elsewhere in this pack; a cut on
  starved delivery is a verdict about that execution and is not evidence that
  the argument failed.
- Spend riding creatives older than `coverage.stale_spend_share` allows: the
  finding is supply, and the first item in the gap list is production rather
  than another argument.
- Angle covered in only one format: `rewrite` into the missing format before any
  conclusion about the angle is written down.
- Proposed angle rests on a claim with no source: `approval_needed` under
  `claims.evidence_rule`.
- Proposed angle falls in `claims.restricted_topics`: route to the platform's own
  policy page and issue no verdict here.

## Output format

No verdict line, this is a map. Two tables.

Covered angles:

| Angle sentence | Ads | Ad sets | Formats | Ratios | Tested | Evidence label | Confidence | Decision |
|---|---|---|---|---|---|---|---|---|

Gaps worth a slot:

| Proposed angle | Where it came from | Cheapest asset path | Evidence label | Decision |
|---|---|---|---|---|

What `high` means in this skill, since it reads a library rather than a test or
a time series: the ad list covered the whole period, live and paused, every angle
sentence was written from the creative itself rather than from the ad name, and
the collapse was applied under `coverage.angle_distinctness`. The comparison family's
`test.min_runtime` and `test.volume_floor` conditions belong to a test and are
not borrowed here; where a row states whether an angle was tested, that row
inherits those conditions and is labelled on the scale in full.

Then `What this could not see`, `Missing data`, `Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser. 23 ads across 3 ad
sets. Raw angle sentences: 11. After collapsing, 4 distinct angles remain, since
7 sentences reduce to one argument about being cheaper than an agency, phrased
seven ways across seven images.

Reading: ad set B carries 2 distinct angles, under `coverage.angles_per_ad_set`,
and its 12 ads created the impression of heavy testing. Three of the four angles
ran in a single format, below `coverage.formats_per_angle`, so no angle verdict
is written for them. The claim that the price angle is the account's proven
winner is refused: it ran in 7 ads but only 1 cleared `test.volume_floor`, and
the rest are `needs_data`.

Supply: 61 per cent of the three ad sets' spend in the period rode creatives
launched before the age named in `coverage.stale_spend_share`, past that key's
share, so production leads the gap list. Two of the 23 ads took under
`delivery.never_delivered_floor`; their angles are recorded as untested rather
than as tried, because they never ran.

Gaps proposed: one objection angle taken from a support transcript the user
supplied, one segment angle for the audience the library never addresses. Both
labelled `hypothesis`. A third idea about a compliance benefit was withheld,
because it sits in `claims.restricted_topics` and belongs on the platform's
policy page first.

## Guardrails

- Never count an ad as an angle. Count arguments after collapsing duplicates.
- Never mark an angle failed on a sample below `test.volume_floor`.
- Never invent a customer objection, a segment or a proof point to fill a gap.
- Do not pause or launch anything. The slate is a recommendation.
