---
name: creative-test-readout-ad-creative
description: Reads a finished creative test across two or more variants and says whether one genuinely won or the result is a tie that should be reported as a tie. Use when a structured test has ended and somebody wants to declare a winner and roll it out. Boundary against its nearest siblings: this skill compares variants against a named control inside one test, not one creative against its own past, which is creative-fatigue-read-ad-creative, and not a single ad diagnosed on its own funnel, which is losing-ad-diagnosis-ad-creative.
---

# Creative Test Readout

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.

Most creative tests end in a tie and get reported as a win. That is how a
programme spends a quarter rolling out differences that were never there.

## Use this skill when

A test with a named control has finished and the next step is a rollout, a
budget shift or a production brief based on the result. Also use it mid-flight
to check whether the test can ever become readable at current spend.

## Required input

- The variant list with a control named explicitly, and what single element
  differs in each pair.
- Per variant: impressions, link clicks, conversions, spend, over the test
  window.
- The test window as start and end dates.
- Whether any creative, budget or audience change happened inside the window.
- Which conversion action counted, primary only or a real-money subset.
- Impressions per variant, needed for `test.impression_share_skew`, and whether
  the variants co-existed in one ad set or ran as a real split.
- Which Advantage+ creative enhancements were enabled on the ads, or a
  statement that nobody knows.

## Analysis workflow

1. Confirm a control is named. Without one there is no test, only several ads,
   and the readout stops here.
2. Ask which Advantage+ creative enhancements were on. Under
   `test.creative_enhancements_rule`, text variation, image expansion, music or
   3D animation change the served asset per impression, so you changed one
   element and the platform changed several more per person. With any of them
   on, the readout says so and no creative conclusion is drawn. Where nobody
   can say, the readout stops at `low` confidence and says why.
3. Check each pair against `test.one_change_rule`. A pair differing in two
   elements produces a result that cannot be applied anywhere else, so report
   it as unusable rather than ranking it.
4. Check the elapsed window against `test.min_runtime` and state it as dates.
5. Check the variant count being READ as a test against
   `test.concurrent_variant_cap`.
6. Check delivery before reading any result, and separate the two states low
   spend can mean before the skew check runs. A variant under
   `delivery.never_delivered_floor` did not lose the test, it never entered it:
   drop it out of the compared set entirely, give it its own row saying so, and
   do not count its impressions in the total the skew check divides by. A
   variant that cleared exposure and is still under `delivery.starved_flag` is
   the opposite case and carries a verdict of its own, but under
   `delivery.ranking_floor` it may not be compared with another variant, so it
   leaves the winner comparison too and the row says which of the two floors
   moved it. Then compute each remaining variant's
   share of the compared set's total impressions and put it against
   `test.impression_share_skew`. Below the floor, the variants ran against
   different people at different times, so the comparison is confounded rather
   than merely noisy and it is void: report no gap, name the skew, and stop.
   No conversion count repairs this, so this check comes before the arithmetic,
   not after it.
7. Run `../scripts/test_readout.py` over the variant CSV. It reports, per
   variant, whether it clears `test.volume_floor` and `test.click_floor`, the
   relative gap against the control, and whether that gap clears
   `test.material_gap`. It also prints the minimum detectable difference at
   each variant's own sample size for `test.statistical_gate`, so the gate is
   read rather than trusted. Do not compute any of this by eye.
8. Drop any variant under `test.volume_floor` out of the winner comparison. It
   can still be reported, but at `low` confidence under the confidence scale,
   and it cannot win.
9. Apply BOTH gates to every surviving variant. A winner has to clear
   `test.material_gap`, which says the difference is worth acting on, AND
   `test.statistical_gate`, which says the difference is there at all. Clearing
   one and failing the other is a tie, and the output names which of the two
   failed, because the two failures lead to opposite next moves: failing the
   material gap means stop testing this element, failing the statistical gate
   means keep going for more sample.
10. Cap confidence on structure. Under `test.assignment_rule`, variants that
    co-existed in one ad set were allocated by predicted performance rather
    than at random, so the readout cannot exceed `medium` however clean the
    numbers are. `high` needs a real split: the platform's own A/B test tool,
    or separate cells.
11. Confirm which conversion denominator was used, primary actions or the
    real-money subset, and state it. Also check
    `reporting.no_view_through_in_ctr` before ranking anything on clicks. Where
    the readout compares this window's conversions with a prior window, either
    wait out the attribution window or state `reporting.conversion_lag_bias`
    beside the number, since the current window is still filling in and the
    comparison is biased against it by construction.
12. Count the distinct live angles in the ad set against
    `coverage.angles_per_ad_set` after collapsing them under
    `coverage.angle_distinctness`. Below the floor, an angle effect and an
    execution effect cannot be separated, so every verdict here drops to `low`.
13. Write what would separate the variants next time: more spend, a wider
    single change, or a different measure.

## Decision rules

- Variant under `delivery.never_delivered_floor`: it is not a result of any
  kind. Keep it out of the compared set, out of the impression total behind
  `test.impression_share_skew`, and out of the cut list, and say the finding is
  allocation rather than the creative. A variant above that floor but under
  `delivery.ranking_floor` ran and may carry a verdict elsewhere, but its share
  of delivery is too thin for a like-for-like comparison, so it leaves the
  winner comparison and the row names the floor that moved it.
- Any verdict arriving from the `early.*` block: it does not enter this readout.
  Under blocking rule 10 in `../AGENTS.md`, everything in that block is `low` by
  definition and is a cheap decision on creatives that will never reach
  `test.volume_floor`, so an early hook or cost verdict is not a variant result,
  is never compared against a control here, and does not become a finding
  because it was repeated across a batch. Where somebody offers one as a test
  input, say which skill produced it and read the test without it.
- Gap measured on cost per acquisition: judge it on `money.relevance_floor`,
  which owns that comparison everywhere in this pack, and read
  `test.material_gap` only on rate gaps such as link CTR. `test.statistical_gate`
  still applies to either. Naming which of the two relevance keys you used is
  part of the output, because a cost gap judged on the rate key is how one
  skill calls actionable what another calls a tie.
- Any compared variant under `test.impression_share_skew`: the comparison is
  void. `investigate` the allocation, report no gap at all, and say the test
  cannot be repaired by running it longer. A void comparison carries no
  confidence label at all, because void is the absence of a finding rather than
  a weak one. This rule is applied before any other rule that reads a number,
  and after only the two delivery exclusions above, which decide who is in the
  compared set in the first place. A gap reported from skewed delivery is worse
  than no gap.
- Gap clears `test.material_gap` AND `test.statistical_gate`, and the winner
  clears `test.volume_floor`: `ship` the winner, and name the one element that
  carried it.
- Gap clears one gate and fails the other: tie, and the output names which one
  failed. Inside `test.material_gap` the decision is `test` again with a bigger
  single change; failing `test.statistical_gate` alone the decision is
  `monitor` and keep collecting, because the difference may be real and is not
  yet readable. Never `ship` on one gate.
- Variants co-existed in one ad set: confidence is capped at `medium` under
  `test.assignment_rule`, whatever the volume, and the row says so. `high` is
  available only on a real split.
- Any Advantage+ creative enhancement enabled, or nobody able to say: no
  creative verdict under `test.creative_enhancements_rule`. `investigate` which
  enhancements ran, and cap the readout at `low`.
- Winner under `test.volume_floor`: no winner, `monitor`, confidence `low`,
  and say how many conversions short it is.
- Window under `test.min_runtime`: `monitor`, no verdict, state the readable
  date.
- Distinct live angles in the ad set below `coverage.angles_per_ad_set`: every
  verdict here drops to `low`, because the losing variant's angle cannot be
  told apart from its execution. Name the count that capped it.
- Pair breaking `test.one_change_rule`: `investigate`, and say the result
  cannot be generalised.

## Output format

Open with one line: winner, tie or void, naming the threshold key that decided
it. Where it is a tie, the line names which of the two gates failed,
`test.material_gap` or `test.statistical_gate`, because that is the part a
reader acts on.

| Variant | Impressions | Link clicks | Conversions | Rate | Gap vs control | Clears volume floor | Evidence | Decision | Confidence |
|---|---|---|---|---|---|---|---|---|---|

Then one sentence on what would separate the variants, then `What this could
not see`, `Missing data`, `Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser.

Input: three variants over a window that clears `test.min_runtime`, all three
co-existing in one ad set. Variant A is the control, 260,000 impressions, 1,240
link clicks and 62 conversions. Variant B changes the hook only, 248,000
impressions, 1,190 link clicks and 71 conversions. Variant C changes the hook
and the image, 44,000 impressions, 210 link clicks and 9 conversions. No budget
or creative change inside the window, and the advertiser confirms every
Advantage+ creative enhancement was off, so `test.creative_enhancements_rule`
does not bite. The ad set holds 3 distinct live angles once
`coverage.angle_distinctness` is applied, at `coverage.angles_per_ad_set`, so no
coverage cap fires.

Delivery first. C is out of the comparison before any arithmetic, on
`test.one_change_rule` and on 9 conversions against `test.volume_floor`, so the
skew check runs across A and B, which total 508,000 impressions. A holds 51.2
per cent and B 48.8 per cent, both clear of `test.impression_share_skew`, so
the comparison is readable rather than void.

`../scripts/test_readout.py` output: A converts at 62 over 1,240, which is 5.00
per cent. B converts at 71 over 1,190, which is 5.97 per cent. The relative gap
is 0.97 over 5.00, which is 19.3 per cent, and that sits below
`test.material_gap`. The minimum detectable difference at these two sample
sizes is 1.81 percentage points against an observed difference of 0.97
percentage points, so the gap also fails `test.statistical_gate`. Both A and B
clear `test.volume_floor` and `test.click_floor`.

Declined: B is not named the winner, and the readout says which gates it
failed rather than reporting a bare tie. It failed both, which is the least
ambiguous outcome available here: the difference is neither big enough to act
on nor big enough to be sure it exists, so more sample would not rescue this
particular pair. Variant C is refused entirely, on the two counts above; even a
large gap on C would be unusable.

Output: "Tie. Failed `test.material_gap` and `test.statistical_gate`." A and B
rows are `export` at `medium` confidence, not `high`: they co-existed in one ad
set, so `test.assignment_rule` caps them by construction, and the row states
that rather than implying the numbers were the limit. C row `needs_data` and
`low`. Decision `test` again with a wider single change to the hook. What would
separate them: a change large enough to clear the material gap, run as a real
split rather than two ads sharing one ad set's delivery.

## Guardrails

- Never name a winner on one gate. `test.material_gap` and
  `test.statistical_gate` both, or it is a tie.
- Never report a gap from a comparison that failed
  `test.impression_share_skew`. Unequal delivery is confounding, not noise.
- Never label a readout on co-existing variants `high`.
- Never let a variant under `test.volume_floor` win on a large-looking rate.
- Never rank on link CTR alone where the objective is conversions.
- Never mix primary and real-money conversion counts across variants.
- Do not shift budget or pause a variant. Recommend, and let a human approve.
