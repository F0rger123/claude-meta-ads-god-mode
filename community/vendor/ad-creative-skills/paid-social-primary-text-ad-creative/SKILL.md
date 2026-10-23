---
name: paid-social-primary-text-ad-creative
description: Writes Meta and LinkedIn primary text, headline and link description variants for one stated angle, built around the point where the feed reader stops reading. Use when the deliverable is static or single-image feed copy for one angle in one ad set. Not for the spoken or on-screen opening of a video, which is video-hook-lines-ad-creative.
---

# Paid Social Primary Text

Shared quality bar: `../references/output-standard.md`. All numbers cited here live in `../references/thresholds.md`.
One angle per run. A batch mixing angles produces copy nobody can read a
result from later.

## Use this skill when

Feed copy is needed for Meta or LinkedIn on one named angle: primary text,
headline and link description, as a set of testable variants. Also use it when
existing feed copy buries its point below the truncation line. The angle must
already be chosen; this skill writes it, it does not pick between angles. Not
for Google search assets tied to keywords, which is
search-headline-set-ad-creative. Not for the spoken and on-screen opening of a
video, which is video-hook-lines-ad-creative. Not for taking one proven angle and
splitting it across cold, warm and retargeting audiences, which is
funnel-stage-variants-ad-creative.

## Required input

- The angle, written as one sentence naming the argument for acting, per the
  denominator table in `thresholds.md`.
- Platform and placement family: Meta feed, Meta reels, LinkedIn feed.
- Audience: who they are and what they already know about the advertiser.
- The offer and the call to action, exactly as the destination states them.
- Every claim the advertiser wants used, each with its source.
- Number of variants required, and the named control they run against.

## Analysis workflow

1. Restate the angle in one sentence and get it confirmed. If the supplied
   angle names a format or an offer rather than an argument, stop and ask.
2. Identify the single idea that must survive truncation. On Meta that is
   whatever sits before `limits.meta_primary_text_visible`; on LinkedIn it is
   whatever sits before `limits.linkedin_intro_text_visible`. Both cuts move by
   device, so treat them as where the reader stops rather than as hard limits,
   and hold LinkedIn headlines to `limits.linkedin_headline_target`.
3. Write the opening line for each variant first, in isolation. Judge each one
   with the rest of the copy hidden.
4. Write the body under each opening: the mechanism, then one proof, then the
   call to action. One proof, not three.
5. Write headlines within `limits.meta_headline_visible` and link descriptions
   that add a fact rather than repeat the headline.
6. Apply `test.one_change_rule` across the variant set. If two variants differ
   in opening line and offer at once, split them or drop one.
7. Cap the set at `test.concurrent_variant_cap` and state the named control.
   Check the ad set volume against `test.volume_floor` and say plainly whether
   a readable result is possible at that spend.
8. Apply `claims.evidence_rule`, `claims.superlative_rule` and
   `claims.restricted_topics`. Mark unsourced factual lines
   `[claim: needs source]` and list what was declined.

## Decision rules

- The point of the angle appears after `limits.meta_primary_text_visible`:
  `rewrite`, and say which sentence has to move up.
- Variants differing in more than one element: not a test, per
  `test.one_change_rule`. Relabel them as separate creatives, not a pair.
- Requested variant count above `test.concurrent_variant_cap`: write the cap,
  and explain that the extra variants split budget below `test.volume_floor`.
- Angle falls inside `claims.restricted_topics`: write nothing until the
  advertiser confirms the platform's category requirements. Label
  `approval_needed`.
- No proof supplied for the central promise: write the variant without a proof
  line and say the set is weaker for it, rather than substituting a plausible
  number.
- Any line this skill produced that carries `[claim: needs source]` is
  `approval_needed`, whatever else its verdict says, and the marker is never
  stripped to make the set look finished. A marked line is not shippable copy:
  it waits for the named source, or it is rewritten without the claim. A marked variant is listed apart from the
  ones that can go live this week, so nobody uploads it by accident.

## Output format

No verdict line. One block per variant: primary text, headline, link
description, the one changed element versus the control, evidence label,
decision label. Then a truncation note stating what each variant says before
the visible cut. Then `What this could not see`, `Missing data`,
`Approval gates`.

This skill writes copy rather than reading a test or a time series, so it issues
no `high` confidence label. The comparison family's `high` rests on `test.min_runtime`
and `test.volume_floor`, which are properties of a test that has not been run on
this copy. Confidence here attaches only to the account evidence these variants
would later be read on, stated as a forecast about whether a result will be
readable, and never as a judgement of the writing.

## Practical example

Illustrative and fictional. Advertiser "Foldbrook". Angle: "an in-house team can
run paid social without hiring an agency". Meta feed, a variant set requested
against a live control at `test.concurrent_variant_cap`. The ad set delivers about 22 purchases a week, so
against `test.volume_floor` no variant reaches a readable sample inside
`test.min_runtime`. That is stated before the copy, and every downstream verdict
on these variants is fixed at `low` for the volume reason alone.

Variant 1, primary text:

> You do not need an agency to run paid social. You need the routine they
> already run, written down. Foldbrook gives an in-house team the weekly loop: brief on
> Monday, launch on Tuesday, read the numbers on Friday, decide what to build
> next. Start free.

Headline: "Run Paid Social In House" (24). Link description: "The weekly loop,
not another dashboard." Opening sentence pair is 98 characters, so the whole
argument sits above the point where the reader stops.

Variant 2 changes the opening line only, which is the one changed element under
`test.one_change_rule`:

> Your agency's real product is a weekly routine. You can run that yourself.

Body, headline and link description are identical to variant 1.

Declined, and reported apart from the launchable set:

- "Agencies charge 4x what this costs." Refused: no agency pricing source was
  supplied, so `claims.evidence_rule` and `claims.superlative_rule` both bite,
  and it is not rewritten as a vaguer comparison either.
- "Used by 340 in-house teams." Written, but carries `[claim: needs source]`
  because the figure arrived verbally, so the variant holding it is
  `approval_needed` and does not go up this week.
- A fourth variant built on a named customer's quote. Not written at all:
  `claims.testimonial_permission` requires written permission on file and none
  was supplied, and the permission is the customer's, not the advertiser's.

Two variants can go live this week, one waits on a source, one waits on
permission, and the output says which is which rather than handing over four
that look equally finished.

## Guardrails

- Never write past the point where the reader stops without checking what
  survives above it.
- Never invent a statistic, price, rating, customer name or comparison.
- Never present variants differing in two elements as a test.
- Never name a winner between variants inside `test.material_gap`.
- Do not publish, boost or edit anything in the ad account.
- Report every declined variant with the reason, including ones asked for by
  name.
