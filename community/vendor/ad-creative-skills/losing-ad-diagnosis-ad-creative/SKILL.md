---
name: losing-ad-diagnosis-ad-creative
description: Takes one underperforming ad and locates the stage where it loses people, so a hook problem, an offer problem and a targeting or delivery problem are told apart instead of guessed at. Use when an ad has never worked and the team is about to rewrite it. Whether it ever worked is often exactly what nobody can say, so sort on the input, which anybody can check: this skill needs four counts for that ad over one window, impressions then link clicks then landing sessions then conversions, and it cannot locate a stage without all four. A daily export carrying reach for the same ad across two consecutive windows is the other question, and it belongs to creative-fatigue-read-ad-creative. Boundary against its nearest siblings: this skill reads one ad down its own funnel from impression to conversion, not a decline over time on a creative that used to work, which is creative-fatigue-read-ad-creative, and not a comparison between variants in a finished test, which is creative-test-readout-ad-creative. This skill owns the session to conversion step, so an ad whose clicks convert poorly starts here rather than at ad-to-landing-page-match-ad-creative: that one reads a page against an ad and no performance counts at all, so it cannot tell you whether the loss is on the page or at the hook. It is where this skill routes once the located step is the destination.
---

# Losing Ad Diagnosis

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.

A weak ad is usually rewritten at the wrong layer. The stage where people stop
tells you which layer to touch, and rewriting any other layer is expensive
guessing.

## Use this skill when

One named ad is underperforming its ad set and the proposed action is a
rewrite, a new image or a new offer. It applies to an ad that never worked. An
ad that worked and slid belongs to the fatigue read.

"The clicks do not convert" is this skill's trigger, not
`ad-to-landing-page-match-ad-creative`'s. That one compares one ad against one
destination and reads no impressions, clicks, sessions or conversions, so it
cannot establish that the loss sits on the page rather than at the hook or at
the click to session step. This skill locates the step first; where the located
step is session to conversion, it hands the destination to that skill, which is
the point at which a page check is worth doing.

## Required input

- For that ad: impressions, link clicks, landing page sessions or views,
  conversions, spend, over one stated window.
- The same four figures for the ad set as a whole, or a median across its live
  ads, as the comparison.
- The destination URL and what it promises above the fold.
- Audience or targeting definition, and whether placements are automatic.
- Whether the ad carries the same offer as the ads it is being compared with.
- Which Advantage+ creative enhancements were on during the window and whether
  any changed inside it (`test.creative_enhancements_rule`). With image expansion
  or text variation running, the asset that served differs per impression, so
  the ad being diagnosed is not exactly the one that was uploaded.

## Analysis workflow

1. State the window as dates and confirm the ad has no creative edit inside it.
2. Check the ad against `delivery.never_delivered_floor`. An ad under it did not
   lose, it did not run. Mark it `never_delivered`, stop, and say the finding is
   allocation rather than creative. Then check it against
   `delivery.starved_flag`: an ad that cleared exposure and still holds a thin
   slice of its ad set's spend has been read by delivery and repeatedly passed
   over, which is a verdict on the creative rather than an absence of one. That
   ad may still be diagnosed here, but every funnel row on it carries the
   starved state, because its counts came from whatever narrow slice of the
   audience delivery kept giving it. Where its share is also under
   `delivery.ranking_floor`, say that the ad set median it is being compared
   against is not a like-for-like comparison.
3. Build the funnel as four counts in order: impressions, link clicks, landing
   sessions, conversions. Missing any one of these makes the stage below it
   unreadable, and that is reported rather than modelled.
4. Compute the rate at each step and put each against the ad set comparison.
   Confirm the click figure is link CTR as defined in the denominators table,
   not all clicks.
5. Find the first step where this ad falls materially behind the comparison.
   Judge a rate step with `test.material_gap`, and say in the output that the
   key is being used outside its home. Its home is the relative difference
   between variants inside one test; here it is being applied to one ad against
   an ad set median, which is not a test and was never randomised. The reuse is
   defensible on one ground and only one: that entry is a business relevance
   floor, a difference too small to act on whatever produced it, and that half
   travels. The statistical half does not travel, so no confidence is drawn
   from clearing it. Where the located step is a cost question rather than a
   rate one, cost per outbound click or cost per acquisition against the ad set
   median, use `money.relevance_floor` instead, which is written for exactly
   that comparison.
6. Read the located step. A shortfall from impression to click is a hook, a
   visual or a first-line problem. A shortfall from click to session is
   delivery: load time, redirect, or broken tracking, not creative. A shortfall
   from session to conversion is offer or message match, and routes to the
   landing page match check rather than to a new headline.
7. Check the volume behind the located step against `test.click_floor` and
   `test.volume_floor`. Under either, the diagnosis is a `hypothesis` and
   carries `low` confidence, whatever the gap looks like.
8. Where any part of the read compares this window's conversions against a
   prior window, either wait out the account's attribution window before
   reading it or state `reporting.conversion_lag_bias` in the same sentence as
   the number. The current window is still filling in while the prior one has
   finished, so the comparison is biased against the present by construction,
   and it will read as a decline that is not there. Click and impression
   comparisons do not carry this and may be read as they stand.
9. Check the destination against `match.above_fold_rule` before blaming the
   ad's copy. A promise the page does not repeat produces a session to
   conversion collapse that looks like a bad offer.
10. Count the distinct live angles in the ad set against
    `coverage.angles_per_ad_set`, applying `coverage.angle_distinctness` first.
    Below the floor a weak angle and a weak execution cannot be told apart, so
    the whole diagnosis is capped at `low` confidence and the output says which
    count capped it.
11. Name the one change to make, at the located layer only, and name what would
    confirm the diagnosis was right.

## Decision rules

- Impression to click behind by more than `test.material_gap`, that key read as
  a relevance floor outside its home as the workflow states: `rewrite` the
  hook, one element at a time under `test.one_change_rule`.
- The located step is a cost step and the gap is inside `money.relevance_floor`:
  no rewrite. A difference that does not move cost per acquisition by that
  much is not worth production time, whatever the rate table shows.
- Ad under `delivery.never_delivered_floor`: `investigate` allocation, issue no
  creative verdict, and keep the ad out of any cut list. It never had the
  delivery to fail with.
- Ad flagged by `delivery.starved_flag`: diagnose it, but say in every row that
  the counts come from a slice of delivery the platform kept shrinking, and cap
  the diagnosis at `low`. The starved state is itself a finding and belongs in
  the output beside the funnel step.
- Distinct live angles in the ad set below `coverage.angles_per_ad_set`: every
  row in this diagnosis drops to `low` confidence, including rows that would
  otherwise qualify, because the angle and the execution are confounded. Say
  the coverage count is what capped it.
- A conversion figure compared against a prior period without the attribution
  window having closed: do not report the change as a change. Either wait, or
  carry `reporting.conversion_lag_bias` in the same line as the number.
- Click to session loss crossing `funnel.click_session_loss_flag`:
  `investigate` delivery and tracking. Do
  not touch the creative.
- Session to conversion behind while the click rate is at or above the
  comparison: `investigate` the destination, and route to the ad to landing
  page match check.
- Volume under `test.click_floor` at the located step: `monitor`, and state how
  much longer at current spend makes it readable.
- An Advantage+ enhancement changed inside the window, or the change dates are
  unknown: cap the whole diagnosis at `low` under
  `test.creative_enhancements_rule` and say the funnel counts span two different
  served assets. The located step is still worth reporting; the rewrite
  instruction that follows from it is not, until the account can say which asset
  produced the counts.
- Restricted category in `claims.restricted_topics`: `approval_needed`, and
  route to the platform's own policy page rather than issuing a verdict.

## Output format

Open with one line naming the stage where this ad loses people.

| Funnel step | This ad | Comparison | Relative gap | Material | Reads as | Evidence | Decision | Confidence |
|---|---|---|---|---|---|---|---|---|

Then the one change to make, then `What this could not see`, `Missing data`,
`Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser.

Input: one ad, 96,000 impressions, 118 link clicks, 96 landing sessions, 1
conversion. Ad set median link CTR 0.41 per cent. No landing page benchmark
supplied for the other ads. This ad took 1,180 of the ad set's 4,300 spend in
the window, which is 27 per cent, clear of `delivery.never_delivered_floor` and
clear of `delivery.starved_flag`, so it genuinely ran and may be diagnosed. The ad
set holds 4 distinct live angles once `coverage.angle_distinctness` is applied,
above `coverage.angles_per_ad_set`, so the coverage cap does not fire and the
confidence label below comes from volume alone.

Reading: this ad's link CTR is 118 over 96,000, which is 0.12 per cent. Against
0.41 per cent, that is a relative shortfall of about 70 per cent, far past
`test.material_gap`, and it is the first step where the ad falls behind. Stated
in the output: that key is being read here as a relevance floor against an ad
set median rather than inside a test, so it says the gap is worth acting on and
says nothing about whether it is statistically there. Click
to session loses 22 of 118, which is normal and not the finding.

Declined: the session to conversion step is not diagnosed. One conversion on 96
sessions is under `test.volume_floor` by a wide margin, and no comparison rate
was supplied for the other ads, so that row is `needs_data` and the offer is
neither cleared nor blamed. Calling the offer weak here would be an assumption
dressed as a funnel reading.

Output: "This ad loses people at the first step, impression to click." The hook
row is `export` with decision `rewrite`, but confidence is `low`, because 118
clicks sits under `test.click_floor` and the diagnosis is therefore a
`hypothesis` about the hook rather than a measured fact. Confirmation: one
hook variant against this ad as control, read once it clears the click floor.

## Guardrails

- Never rewrite a layer the funnel did not implicate.
- Never diagnose a step whose count was not supplied.
- Never treat a click to session gap as a creative defect.
- Never call an offer weak on volume under `test.volume_floor`.
- Do not edit or pause the ad. Recommend, and let a human approve.
