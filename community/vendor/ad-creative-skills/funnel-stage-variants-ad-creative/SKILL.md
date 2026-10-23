---
name: funnel-stage-variants-ad-creative
description: Takes one angle that is already proven and rewrites it three ways, for cold prospecting, warm audiences and retargeting, naming what changes between stages and what must stay identical. Use when the input is an existing winner being extended across audience temperatures. Not for writing an untested angle from scratch, which is paid-social-primary-text-ad-creative.
---

# Funnel Stage Variants

Shared quality bar: `../references/output-standard.md`. All numbers cited here live in `../references/thresholds.md`.
The point of this skill is continuity. A retargeting ad that argues a different
case than the cold ad the viewer already saw restarts the sale instead of
closing it.

## Use this skill when

An angle has evidence behind it in one audience and the account wants it
running across cold, warm and retargeting placements. Also use it when the
three stages are already live and each says something unrelated to the others.
The angle must already be proven or explicitly labelled unproven. Not for
inventing or choosing an angle, and not for a first draft of feed copy, which
is paid-social-primary-text-ad-creative. Not for the opening seconds of a
video, which is video-hook-lines-ad-creative. Not for Google search assets tied
to a keyword set, which is search-headline-set-ad-creative.

## Required input

- The winning angle as one sentence, and the copy exactly as it runs today.
- The evidence it won on: window as dates, spend, `conversions` or link clicks,
  and the control it beat.
- Audience definitions for each stage, including what the retargeting pool
  actually did to enter it.
- The offer at each stage, if it differs, and who approved the difference.
- Any claim used in the current copy, with its source.

## Analysis workflow

1. Check whether the angle is genuinely proven. Test the supporting read
   against `test.volume_floor`, `test.min_runtime` and `test.material_gap`
   before rewriting anything. A win inside `test.material_gap` is a tie.
2. Extract the invariant: the promise, the mechanism and the proof. These are
   what must survive all three stages unchanged in substance.
3. Write the cold variant. Assume no prior contact, so the problem is named
   before the product and the proof carries more weight.
4. Write the warm variant. The problem is assumed known, so the space goes to
   the mechanism and to the objection that stops people at this stage.
5. Write the retargeting variant, and hold the line that makes this skill worth
   running. Stage is the one changed element under `test.one_change_rule`, so
   four things stay byte-identical across all three: the angle sentence, the
   main claim in the exact words it runs in today, the single proof, and the
   conversion action with the destination behind it. Change the opening, the
   emphasis and the reference to what the viewer already did. Change any of the
   four and the account can no longer tell a stage effect from an angle effect,
   because two things moved between the cells it is comparing; the retargeting
   ad will win, as retargeting ads do, and nobody will know whether the stage or
   the new argument did it. The offer is the one people move without noticing:
   a discount added at retargeting is a second changed element, not a stage
   adaptation.
6. Diff the three variants line by line and produce an explicit changed and
   unchanged list. Anything in the changed list that touches the promise or the
   proof is a defect, not a stage adaptation.
7. Check message match at every stage with `match.promise_pairs` and
   `match.above_fold_rule`, because stages often point at different pages.
8. Apply `claims.evidence_rule`, `claims.superlative_rule` and
   `claims.restricted_topics` to all three variants and mark unsourced factual
   lines `[claim: needs source]`.

## Decision rules

- The supporting result sits inside `test.material_gap` or under
  `test.volume_floor`: the angle is not proven. Write the variants if asked,
  label the whole set `test` at `low` confidence, and say the extension is a
  bet.
- Retargeting variant changes the promise, the proof or the angle sentence:
  `rewrite`. Stage changes emphasis and the reference to prior action, never
  the argument.
- The offer differs between stages: this is a second changed element under
  `test.one_change_rule` and the set stops being a stage test. Either hold one
  offer across the three, or run the offer change as its own test against a
  named control and say the stage question has been given up for this round.
  Decision `investigate` on which of the two questions the account actually
  wants answered.
- No stage reaches `test.volume_floor` on its own conversions inside
  `test.min_runtime`: the three cannot be compared on conversions at all. Read
  them on `test.click_floor`, state in the output that the answer is
  click-side only, and cap the whole set at `low` under the shared scale.
- Cost per acquisition between two stages differing by less than
  `money.relevance_floor`: no stage won. Report a tie and leave the budget
  where it is; a rate difference that does not move cost per acquisition is not
  a reason to shift spend between temperatures.
- Retargeting pool sitting under `delivery.ranking_floor` of the campaign's
  spend: it may have run, but its share is too thin to compare against the cold
  and warm stages. `monitor`, and say the comparison between stages is
  unavailable until the pool gets a comparable share of delivery. Where the pool
  is under `delivery.never_delivered_floor` as well, it did not run at all and
  the finding is allocation rather than the copy.
- Retargeting pool defined by page view alone with no stated action: label
  `investigate`, because the copy cannot reference something unknown.
- A stage points at a page missing the ad's main claim above the fold:
  `investigate` the page, and hold that stage's variant.
- Fewer than `coverage.angles_per_ad_set` live angles once these variants ship:
  say so, because a losing week will not be readable. Three stage variants of
  one argument are one angle under `coverage.angle_distinctness`, not three,
  and an account that counts them as three has just talked itself into a
  coverage pass it did not earn.
- Any line this skill produced that carries `[claim: needs source]` is
  `approval_needed`, whatever else its verdict says, and the marker is never
  stripped to make the set look finished. A marked line is not shippable copy:
  it waits for the named source, or it is rewritten without the claim.

## Output format

No verdict line. Three copy blocks, one per stage, each with its audience,
offer, evidence label and decision label. Then two lists side by side: what
changed between stages and what stayed identical. Then a one-line statement of
the strength of the original result in its own numbers. Then the four elements
held identical across the three stages, listed literally, so a reader can check
them rather than trust them. Then `What this could not see`, `Missing data`,
`Approval gates`.

This skill writes copy rather than reading a test or a time series, so it issues
no `high` confidence label of its own. The confidence it does state is inherited
from the original result being extended, read on the shared scale in full, and it
never rises above what that result carried. Nothing about writing three variants
makes the evidence behind the angle stronger.

## Practical example

Illustrative and fictional. Advertiser "Halden". Angle: "you are paying twice
for the same lead". The cold ad is reported at 1.9% link CTR against a control
at 1.7%, over 9 days, 41 purchases across the ad set.

Strength of the original result: 1.9% against 1.7% is about 12% relative,
inside `test.material_gap`, and 9 days is short of `test.min_runtime`. The angle
is not proven and the claim that it won is refused as a tie. Variants are still
written, all labelled `test` at `low` confidence, and the extension is a bet.

Cold:

> Two of your lead sources are selling you the same person. You are paying twice
> for the same lead. Halden matches inbound records across sources before they
> reach your CRM. Book an audit.

Warm:

> You know about the duplicates. Here is where they start: two sources, one
> person, two invoices. You are paying twice for the same lead. Halden matches
> inbound records across sources before they reach your CRM. Book an audit.

Retargeting:

> You opened the duplicate check and left it. Nothing has changed since. You are
> paying twice for the same lead. Halden matches inbound records across sources
> before they reach your CRM. Book an audit.

Held identical: the angle sentence; the claim "You are paying twice for the same
lead" word for word; the single proof; the conversion action and its
destination. Changed: the opening line and the reference to prior action only.
One offer across all three, deliberately, so the account reads the stage rather
than a discount.

Declined:

- "You already know this works for teams like yours", in the retargeting draft.
  No case evidence was supplied, so it is not written. Its slot goes to the
  abandoned check, an observed action rather than a claim.
- "Cuts duplicate spend by a third" `[claim: needs source]`. This was the single
  proof, so all three ship without a proof line and the set is weaker for it.
  Any variant carrying it is `approval_needed` and none goes live with it.

## Guardrails

- Never call an angle proven on a result inside `test.material_gap`.
- Never let the promise or the proof drift between stages.
- Never reference a prior action the retargeting definition does not contain.
- Never invent a case study, a customer or a saving figure.
- Do not change audiences, budgets or ad status in the account.
- Report every line declined at every stage, with the reason.
