---
name: offer-and-proof-line-ad-creative
description: Converts a vague benefit into a stated offer, the single proof that carries it, and a risk reducer, and refuses to supply proof the advertiser has not evidenced. Use when the weakness is the substance of what is being promised rather than the wording. Not for producing platform-shaped variants of an already settled offer, which is paid-social-primary-text-ad-creative.
---

# Offer And Proof Line

Shared quality bar: `../references/output-standard.md`. All numbers cited here live in `../references/thresholds.md`.
Most creative that fails does not fail on wording. It fails because nothing
specific was promised, nothing supported the promise, and nothing reduced the
risk of acting.

## Use this skill when

The copy says something like "grow faster" or "save time" and nobody can state
what is actually being offered. Also use it before a creative sprint, so every
downstream skill in this pack writes against one settled offer, and when an
advertiser asks for a proof line the account may not be able to evidence. Not
for shaping a settled offer into platform variants, which is
paid-social-primary-text-ad-creative. Not for the opening seconds of a video,
which is video-hook-lines-ad-creative. Not for splitting a proven angle across
audience temperatures, which is funnel-stage-variants-ad-creative.

## Required input

- The vague benefit as it is currently written.
- What the product actually does, in one paragraph, in plain terms.
- The commercial terms available: price, trial length, guarantee, contract
  length, onboarding time.
- Every candidate proof and where it lives: a dashboard, a document, a named
  customer with permission, a public review.
- The category, checked against `claims.restricted_topics`.
- Who can approve a guarantee or a refund promise.

## Analysis workflow

1. Restate the vague benefit and name what it is missing: the outcome, the
   subject, the timeframe or the mechanism. Usually more than one.
2. Write the offer as a specific exchange: what the reader gets, what it costs
   them in money and effort, and by when.
3. List every candidate proof and classify each with an evidence label from the
   output standard. A proof labelled `hypothesis` or `notes` is not usable in
   an ad until it becomes `export`, `url` or a cleared customer statement.
4. Select one proof, not three. The strongest proof is weakened by being
   stacked with weaker ones, and each extra proof adds an approval dependency.
5. Write the risk reducer from what actually exists in the commercial terms:
   trial, guarantee, cancellation, or a smaller first step. Do not invent one.
6. Test the offer against the destination with `match.promise_pairs` and
   `match.above_fold_rule`. An offer the page does not state is not an offer.
7. Apply `claims.evidence_rule` and `claims.superlative_rule` line by line.
   Mark anything unsourced `[claim: needs source]` and refuse rather than
   soften.
8. Produce the refusal list: every proof or reducer requested that cannot be
   written, with the exact artefact that would unlock it.

## Decision rules

- No usable proof at any evidence label: write the offer and the risk reducer
  only, and state that the creative ships without proof. Do not construct a
  category-typical statistic to fill the gap.
- Proof exists but is unverified in the account: `approval_needed` on producing
  the source before launch, not after.
- Guarantee or refund language: always `approval_needed`, whoever asked for it.
- Category inside `claims.restricted_topics`: route the offer and proof to the
  platform policy page before writing, and label the whole set
  `approval_needed`.
- The page does not state the offer: `investigate` the page. A page and ad
  disagreeing on the offer is the most expensive mismatch on this list.
- Any line this skill produced that carries `[claim: needs source]` is
  `approval_needed`, whatever else its verdict says, and the marker is never
  stripped to make the set look finished. A marked line is not shippable copy:
  it waits for the named source, or it is rewritten without the claim. This bites hardest on the proof row, which
  is the row most likely to carry a number: a marked proof does not ship as a
  proof, and the block goes out with the offer and the risk reducer while the
  proof waits.

## Output format

No verdict line. A three row block: offer, proof, risk reducer. Each row shows
the line as it would run, the evidence label, the source named or `needs_data`,
and the decision label. Then the vague original alongside the specific
replacement, so the change is visible. Then the refusal list. Then
`What this could not see`, `Missing data`, `Approval gates`.

This skill settles an offer rather than reading a test or a time series, so it
issues no `high` confidence label. `high` on the comparison family's conditions rest on
`test.min_runtime` and `test.volume_floor`, which describe a test nobody has run
on this offer. What stands in for it here is the evidence label on the proof
row: `export` or `url` with a named source is as strong as this skill gets, and
`notes` is not usable in an ad whatever anybody remembers being told.

## Practical example

Illustrative and fictional. Advertiser "Ravenscourt". Vague benefit as written
today: "grow your pipeline faster". Commercial terms supplied: 14 day trial, no
card required, monthly rolling, no guarantee. Candidate proofs offered in
conversation: "customers see 3x more meetings", "rated best in category", and an
internal dashboard showing a median of 9 days to a first booked meeting across
27 accounts.

The three row block, as it would run:

- Offer: "14 days of Ravenscourt, no card, cancel any month." Evidence `url`,
  source the pricing page, which states the same terms above the fold under
  `match.above_fold_rule`. Decision `ship`. The trial length carries no
  `[claim: needs source]` marker because its source is named in the same line
  and a reader can check it; the marker exists for numbers that cannot be.
- Proof: "Median 9 days to a first booked meeting, across 27 accounts."
  `[claim: needs source]`. Evidence `notes`, source `needs_data`. Decision
  `approval_needed`, so this row does not ship.
- Risk reducer: "No card to start. Cancel in one click, any month." Evidence
  `url`, same page. Decision `ship`.

Vague original against the specific replacement: "grow your pipeline faster"
becomes "14 days of Ravenscourt, no card, cancel any month", which names the
exchange, the cost in money and effort, and the point at which the reader can
leave.

Refusal list:

- "Customers see 3x more meetings." Refused. It arrived as `notes`, no export
  was supplied, and under `claims.evidence_rule` it is not written in any form,
  including a hedged "many customers see a large lift". Unlocked by the
  dashboard export.
- "Rated best in category." Refused under `claims.superlative_rule`, no
  comparison behind it. Unlocked by a named ranking with its publisher.
- The proof row above ships the day the dashboard export is attached. It is not
  quietly published in the meantime because it happens to be true.

What ships today is the offer and the risk reducer, with the proof row named and
waiting.

## Guardrails

- Never supply proof the advertiser has not evidenced, in any wording.
- Never soften a refused claim into a vaguer one to get it past this rule.
- Never write a guarantee that nobody has approved.
- Never stack three weak proofs in place of one strong one.
- Do not alter pricing pages or account settings. Recommend only.
- Report every refused line and the exact artefact that would unlock it.
