---
name: winning-ad-teardown-ad-creative
description: Takes one named ad, your own top performer or a competitor ad pulled from a public ad library, and reverse-engineers it into a reusable pattern of angle, promise, proof and structure, separating what transfers from what does not. Use when a single ad has been singled out for imitation and somebody needs to know which part is actually copyable. Boundary against siblings: creative-brief-from-account-data reads a whole export and issues production slots, angle-inventory counts coverage across the library, and this skill looks at exactly one ad.
---

# Winning Ad Teardown

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.
The output is a pattern with an explicit transferability verdict, not praise for
an ad somebody already likes.

## Use this skill when

One specific ad has been singled out and the next question is what to copy from
it. Typical triggers: a competitor ad someone screenshotted from a public ad
library, an ad a client keeps citing, or your own single best performer that the
team wants to clone. The unit of work is one ad. If the question spans the whole
library, use `angle-inventory-ad-creative`. If the deliverable is a set of
production slots, use `creative-brief-from-account-data-ad-creative`.

## Required input

- The ad itself: image or video, headline, primary text, call to action button,
  and the destination URL.
- Its source: own account, or a public ad library with the library page cited.
- For an own ad: spend, impressions, link CTR, conversions and the live dates,
  so the claim that it won can be tested.
- For a competitor ad: first seen and last seen dates only, nothing else is
  available.
- The audience and offer the ad ran against, where known.

## Analysis workflow

1. Establish provenance before analysis. Own ad with an export, or competitor ad
   from a library. The two paths produce different evidence labels and different
   ceilings on confidence, and mixing them is the main failure of this exercise.
2. For an own ad, test whether it actually won: check the window against
   `test.min_runtime`, the volume against `test.volume_floor`, and the gap to the
   next ad against the right relevance key: `money.relevance_floor` where the gap
   is in cost per acquisition, which owns that comparison everywhere in this
   pack, and `test.material_gap` where it is in a rate such as link CTR. Say
   which you used. An ad inside whichever key applied is a tie and is torn
   down as a sample, not as a winner.
3. For a competitor ad, check it clears `teardown.observation_floor` before
   spending any effort on it, then apply `reporting.no_competitor_spend` in the first line
   of the output. Longevity shows a decision somebody kept making. It shows no
   spend, no result and no verdict, and any inference from run length is labelled
   `hypothesis`.
4. Set the ceiling now, before decomposing anything, because this is where the
   exercise usually goes wrong: it neuters the evidence correctly in one
   sentence and then carries on producing recommendations as though it had not.
   Where the ad sits below `teardown.observation_floor`, or where the only
   evidence available is a public ad library whatever the run length, this skill
   produces exactly one thing: the structure. It states plainly that structure
   is the only transferable output, that no performance conclusion is available
   from this input, and that nothing here says the ad worked. It then writes the
   structure with no recommendation attached to it: no slate, no ranking, no
   "worth testing", because a recommendation is a performance claim wearing a
   verb. What the reader does with the structure is their decision, made on
   their own evidence, and the output says so in that many words.
5. Decompose the ad into four named parts: the angle as a sentence, the promise
   made to the reader, the proof offered for that promise, and the structure of
   the opening, which is the window named in `limits.video_hook_seconds` for
   video and the first line for feed text, read against
   `limits.meta_primary_text_visible`.
6. Classify every element as transferable or not. Transferable means it survives
   without this brand's price point, distribution, catalogue, recognition or
   licensed footage. Name the specific dependency for each element you rule out.
7. Check the destination. An ad whose promise is carried by its landing page is
   only half copyable from the ad alone, and the page check belongs to
   `ad-to-landing-page-match-ad-creative`.
8. Convert what survives into one testable variant, and only where the ceiling
   in step 4 did not fire. On the library-only path this step does not run:
   there is no variant to propose, because proposing one asserts the pattern is
   worth spending against and nothing in the input supports that. Otherwise, one
   variant against a named control, one
   changed element only (`test.one_change_rule`), and mark any factual line the
   pattern would require with `[claim: needs source]` under
   `claims.evidence_rule`.
9. State what you declined to lift and why, including anything touching
   `claims.restricted_topics`.

## Decision rules

- Own ad clearing volume, runtime and gap: `ship` the pattern into the next
  round, confidence `high`.
- Own ad under `test.volume_floor`: `monitor` and name a read date. Confidence is
  `low` whatever else is in place.
- Competitor ad, or any ad below `teardown.observation_floor`, or any ad whose
  only evidence is a public ad library: the output is structure only. No
  performance conclusion, and no recommendation attached to the structure. The
  decision column on every row reads `needs_data`, not `test`, because `test`
  is a recommendation and this input cannot support one. Say in the opening
  line that the pattern is offered as description and that the decision to try
  it belongs to whoever holds evidence this skill was not given.
- Element depends on brand recognition, catalogue depth or a licensed asset:
  `cut` it from the pattern and say which dependency.
- Element is a format or pacing choice with no brand dependency: `test`.
- Any lifted line stating a number or an outcome: `approval_needed` until the
  user supplies the source.

## Output format

Open with one line naming what this ad is evidence of, and what it is not.

| Element | What it does | Transferable | Dependency if not | Evidence label | Confidence | Decision |
|---|---|---|---|---|---|---|

Then the pattern written as one paragraph a writer can build from, then the
single variant to test, then `What this could not see`, `Missing data`,
`Approval gates`.

On the structure-only path, which is every competitor ad and every ad below
`teardown.observation_floor`, the variant block is absent rather than empty and
the output says why in one line: no performance conclusion is available from
this input, so the structure is offered as description and carries no
recommendation. An output that ends in something to try has quietly promoted
longevity into evidence, which is the failure this whole skill exists to
prevent.

## Practical example

Illustrative made-up data, not a real advertiser. A competitor ad has been live
in a public library for 214 days across 6 creative variants. The team wants it
called a proven winner.

Reading: refused. Under `reporting.no_competitor_spend`, 214 days shows only
that somebody kept the ad on. Spend is `needs_data`, results are `needs_data`,
and the opening line says so. What can be read is structure: the first line is
19 characters and lands inside `limits.meta_primary_text_visible`, the proof is a
named third party rather than a self-reported figure, and the angle is a single
sentence about switching cost.

Transferable: the switching-cost angle and the short opening line. Not
transferable: the named third party, which the account does not have, and a
"rated number one" line, cut under `claims.superlative_rule` because no
comparison was supplied.

Output: the structure, and nothing else. The 214 days clear
`teardown.observation_floor`, so the decomposition was worth doing at all, but
the only evidence is a public ad library, so no variant is proposed and no row
carries `test`. Every performance row is `needs_data`. The team asked for a
slate built on this ad and does not get one: what they get is a description of
how the ad is built, with the decision to spend against it left to whoever holds
account evidence this teardown was never given.

## Guardrails

- Never treat run length, comment count or reaction count as performance.
- Never lift a claim, statistic, customer name or review from another brand's ad.
- Never call an own ad a winner inside `money.relevance_floor` on cost per
  acquisition, or inside `test.material_gap` on a rate.
- Do not fill a missing dependency with an invented equivalent for this brand.
