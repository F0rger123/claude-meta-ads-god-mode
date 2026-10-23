# Output standard

Shared across every skill in this pack.

## Required sections

Every skill returns, in this order:

1. Its own findings table, or its own produced copy where the skill writes
   rather than diagnoses.
2. `What this could not see` - the limits that apply to this specific answer.
   Cite `thresholds.md` (Reporting limits) rather than restating them.
3. `Missing data` - the exact export, screenshot or field that would change the
   answer, and which finding each one would firm up.
4. `Approval gates` - what needs a human yes before anything is published or
   spent against.

Skills that produce a single verdict (fatigue read, test readout, weekly
readout) open with a one-line verdict before the table. Skills that produce a
ranked list or a set of variants do not; a verdict line on a list of headlines
is theatre.

## Skills that write copy carry two extra obligations

This pack produces public advertising, which the diagnosis-only packs do not.
Any skill whose output is copy a human could paste into an ad platform must:

- **Mark every factual claim it wrote.** Each produced line that states a
  number, a comparison or an outcome carries `[claim: needs source]` until the
  user supplies one. A skill never invents a statistic, a customer name, a
  review, a price or a result, and never fills one in from the brand's
  category. This is `claims.evidence_rule` in `thresholds.md`.
- **Say what it did not write.** Name the variants it declined to produce and
  why: a restricted category, a claim with no evidence, a format the account
  has no asset for.

## Evidence labels

Use exactly one per row:

- `export` - came from a downloaded report.
- `screenshot` - read off the interface.
- `url` - checked on a live page.
- `notes` - supplied by the user in conversation.
- `hypothesis` - inferred, not observed.
- `needs_data` - cannot be assessed with what was provided.

## Decision labels

Use exactly one per row:

- `ship` - write it, launch it, no gate beyond normal review.
- `test` - launch it against a named control.
- `rewrite` - the idea holds, the execution does not.
- `investigate` - the answer is outside the creative.
- `monitor` - leave it running and read it again on a stated date.
- `cut` - stop serving it.
- `approval_needed` - a human must approve before this runs.

## Confidence

Three values, each with a stated test, so two people reading the same evidence
land on the same label.

**The principle first, because it is the same everywhere in this pack.**

- **`high`** - every condition this kind of evidence could meet is met, so what
  limits the finding is the world rather than the read.
- **`medium`** - exactly one condition is missing, it is not the volume one, and
  the row says which one it is.
- **`low`** - two or more are missing, OR the evidence sits under the volume
  floor its own family names even where that is the only thing missing, OR
  something changed inside the window that moves the number on its own. Any one
  of these is enough.

**A comparison that fails `test.impression_share_skew` never reaches this scale
at all.** Unequal delivery means the arms ran against different people at
different times, so the comparison is void before any gap is printed, and a void
comparison carries no confidence label of any kind. Void is the absence of a
finding rather than a weak one, which is why a skew failure is never reported as
`medium` and never as `low`. Settle this before labelling anything.

**The conditions differ by what the skill reads, so there are three families.**

*Comparison skills*, reading variants against a named control or one ad against
its ad set. `high` needs all five of: the finding came from an export, the
window clears `test.min_runtime`, the variant clears `test.volume_floor`, the
gap clears `test.statistical_gate`, and no creative or budget change happened
inside the window.

*Time-series skills*, reading one creative against its own past. `high` needs
all four of: the finding came from an export, both windows are set by
`fatigue.window` and stated as dates, both windows clear
`fatigue.volume_floor`, and no creative edit and no Advantage+ creative
enhancement change fell inside either window
(`test.creative_enhancements_rule`). The volume condition here is
`fatigue.volume_floor` and not `test.volume_floor`; either window under it is
`low`, whatever else is in place.

*Skills reading a page, a draft or a library*, where there is no time series and
no test. Each states its own conditions in its own `Output format` section, in
terms of how completely the thing in front of it was read.
`test.min_runtime` and `test.volume_floor` describe a test and are never
borrowed to dress a count, a page read or a piece of copy as a measurement.
Where one of these skills reports whether something was tested, that row alone
inherits the comparison family's conditions and is labelled on them.

**Two structural caps sit above all three families and are not exceptions to
them.**
`test.assignment_rule` caps any readout on variants co-existing in one ad set
at `medium`, because they were never randomly assigned, so a co-existing
readout cannot reach `high` however clean its numbers are. And every verdict in
the `early.*` block is `low` by definition.

**The B2B case, written out because it is where this scale gets misread.** On an
account whose ad sets never reach `test.volume_floor`, readouts run on
`test.click_floor` instead. That does not promote them: a variant under
`test.volume_floor` is `low`, always, and a click-based read on a conversion
question stays `low` no matter how many clicks it has. What the click floor
buys is the right to state a click-side finding at `medium`, on the click-side
question only. Say which question you answered.

The volume condition is listed in both directions on purpose so there is no
overlap: under the floor is always `low`, never `medium`, whatever else is in
place.

A row labelled `high` on a creative whose spend moved mid-window is the most
common way this scale gets abused. Spend changes redistribute impressions
across placements, and placement mix moves CTR on its own.

## Hard rules

- Diagnosis and drafting only. Nothing in this pack logs into an account,
  uploads an asset, publishes an ad, pauses an ad or moves a budget. Every
  recommendation is a decision put in front of a human.
- Separate what was observed from what was inferred. An inference never enters
  a findings table labelled `export`.
- Never declare fatigue on one signal. `fatigue.verdict_rule` requires two.
- Never name a winner on one gate. A difference has to clear
  `test.material_gap` (worth acting on) AND `test.statistical_gate` (actually
  there). Clearing one and not the other is a tie, and which one it failed is
  the finding.
- Never read a comparison that fails `test.impression_share_skew`. Unequal
  delivery is confounding, not noise, and no sample size repairs it.
- Never state a period-over-period conversion comparison without either
  waiting out the attribution window or naming `reporting.conversion_lag_bias`.
- Never write a claim the user has not evidenced, and never soften an
  unevidenced claim into a vaguer one to get it past this rule. A vague
  unevidenced claim is the same defect with worse copy.
- Never treat a competitor ad's longevity as proof it performs
  (`reporting.no_competitor_spend`).
- Name missing data. An answer that hides its own gaps is worse than no answer,
  because it reads as complete.
