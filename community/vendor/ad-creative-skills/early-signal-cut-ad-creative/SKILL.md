---
name: early-signal-cut-ad-creative
description: Decides which newly launched creatives to cut in their first days on leading indicators, and states the error rate it accepts for doing so. Use when a batch of new creatives has launched, most of them will never reach a readable conversion sample, and somebody still has to decide what stays on. Boundary against its nearest siblings: this reads a NEW creative in its first days against its ad set's own medians, not a long-running creative against its own past, which is creative-fatigue-read-ad-creative, and not a finished comparison against a control, which is creative-test-readout-ad-creative.
---

# Early Signal Cut

Shared quality bar: `../references/output-standard.md`. All numbers cited here live in `../references/thresholds.md`.

Every verdict here is `low` confidence by definition, and that is the point
rather than a caveat. A buyer shipping dozens of creatives a month gets
`needs_data` on most of the library, because most creatives never reach
`test.volume_floor`. This layer trades a stated error rate for throughput.
Nothing it returns is a result.

## Use this skill when

A batch launched in the last few days, the ad set is spending, and the decision
is which ones to switch off now. This reads a NEW creative against its ad set's
own medians. A long-running creative against its own past is
creative-fatigue-read-ad-creative. A finished comparison against a named control
is creative-test-readout-ad-creative. If these creatives can plausibly reach
`test.volume_floor` inside `test.min_runtime`, wait and read them properly.

## Required input

- Per creative since launch: impressions, spend, outbound clicks, and on video,
  3-second plays and the video-play figure `early.hold_rate` is measured on.
- Video length in seconds for every video creative. This sets its
  `early.duration_band` and without it no hold read runs at all.
- Total ad set spend over the same window, and hours live per creative.
- Target cost per acquisition, and per-creative cost per acquisition if any.
- Launch date per creative, and whether any changed after launch.
- Which Advantage+ creative enhancements are on and the date each was switched
  on (`test.creative_enhancements_rule`).

On LinkedIn this skill runs on `early.cost_multiple` alone. LinkedIn does not
report the video play metrics that `early.hook_rate` and `early.hold_rate` are
built from, so both rows are `needs_data` on every creative and the cut list
rests on cost per outbound click. Say that in the output rather than letting two
empty columns pass as passing ones.

## Analysis workflow

1. Apply `delivery.never_delivered_floor` first, and let it be the only
   exclusion this skill makes. A creative under it never got a chance, so it
   gets its own row, stays off the cut list, out of the medians and out of any
   brief input, and is never reported as a performance finding.
2. Apply `delivery.starved_flag` to everything that cleared step 1. A creative
   that cleared exposure and still holds a thin slice of spend after its first
   days has not gone unread; it has been read. Delivery allocates on predicted
   performance and that prediction is trained on the creative's own early
   response, so repeated non-allocation is the platform's verdict on the
   creative rather than an absence of one. Decision `cut`, confidence `low`, and
   it goes ON the cut list with that reasoning written into the row.
3. Group the survivors by `early.duration_band`. Every `early.*` median is
   computed inside a band, never across an ad set holding several, because hold
   on a short video and hold on a long one are different questions.
4. Check each band against `early.median_stability_floor`, counted after steps 1
   and 2. Under the floor the band's median is one middle number driving real
   cuts, so hook and hold are `needs_data` there and no cut fires on them.
   `early.cost_multiple` may still run against the whole ad set, and the row
   says that is what it did.
5. In each band that clears the floor, compute the band's own median hook rate
   and hold rate, then test each creative against `early.hook_rate` and
   `early.hold_rate` separately and record which failed. Reporting them together
   as one bad creative destroys the only information an early read produces.
   Never import a benchmark from another account.
6. On statics, on LinkedIn and on any account without video metrics, use
   `early.cost_multiple` instead and say so.
7. Before ranking anything or handing a creative to a brief, apply
   `delivery.ranking_floor`. It answers a different question from step 2: one
   decides whether a creative gets a decision, the other decides whether it gets
   compared.
8. Check `test.creative_enhancements_rule`. An enhancement switched on since
   launch means the served asset changed under the read, so the creative goes to
   `monitor` with no verdict.
9. Check `money.relevance_floor` before recommending any budget move. Where cost
   per acquisition is not supplied, name the decision you cannot make.
10. Put `early.false_negative_rate` in the output every time, and tell the
    account how to replace it: log each early cut with its date and reason, then
    check later winners against that log. After a few dozen entries it has its
    own measured rate and retires this assumption. The same trade applies to the
    cuts made under `delivery.starved_flag`.

## Decision rules

- Under `delivery.never_delivered_floor`: `never_delivered`, `monitor`, evidence
  `export`, no performance claim of any kind, excluded from the cut list.
- `delivery.starved_flag` fires: `cut`, evidence `export`, confidence `low`, and
  the creative goes on the cut list. State in the row that the platform declined
  to spend on it repeatedly and that this is its read of the creative.
- Band under `early.median_stability_floor`: hook and hold are `needs_data`, no
  cut fires on them, and `early.cost_multiple` runs against the whole ad set
  with that substitution named.
- Video length not supplied: the hold read is `needs_data` under
  `early.duration_band`, and no band median is computed from mixed lengths to
  cover the gap.
- `early.hook_rate` fails against the band median, hold passes: `cut`, and the
  rewrite direction is the opening only.
- `early.hold_rate` fails, hook passes: `cut`, and the rewrite direction is
  everything after the opening. Keep the hook.
- Both fail, or `early.cost_multiple` fails on a static: `cut` the concept.
- Creative changed after launch, or an enhancement in
  `test.creative_enhancements_rule` switched on since launch: `monitor`, no
  verdict, because the window covers two different assets.
- Below `delivery.ranking_floor`: the creative may carry a verdict but may not
  be ranked against another creative or fed into a brief as evidence.

## Output format

No verdict line: this produces a list, and a verdict line on a cut list reads
as a result.

| Creative | Band | Spend share | Exposure met | Hook vs band median | Hold vs band median | Failing element | Evidence | Decision | Confidence |
|---|---|---|---|---|---|---|---|---|---|

Then the `early.false_negative_rate` sentence and how to replace it, then
`What this could not see`, `Missing data`, `Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser.

Ad set spend in the window: 4,000 units across 13 live creatives. Target cost
per acquisition 40. Text variation has been on for all 13 since launch and
nothing was switched on mid-window, so under `test.creative_enhancements_rule`
it is a constant here rather than a changed asset.

Delivery, step 1 and step 2. Four creatives sit under
`delivery.never_delivered_floor`, taking 100 units between them, 2.5 per cent of
ad set spend: `never_delivered`, off the cut list, out of the medians. Three
creatives carry the ad set: A on 1,180, B on 1,020 and C on 962, which is 29.5,
25.5 and 24.1 per cent, just over 79 per cent between them. The remaining six
cleared exposure and hold between 2.8 and 3.3 per cent of spend each after three
days live, so `delivery.starved_flag` fires on all six: `cut` at `low`, ON the
cut list, because the platform looked at each of them repeatedly and kept
deciding not to spend.

Bands. The 15 to 30 second band holds seven survivors, A, B, C and four of the
starved six, which clears `early.median_stability_floor`. Band hook rates are
0.130, 0.200, 0.220, 0.240, 0.260, 0.280 and 0.300, so the median is 0.240 and
`early.hook_rate` triggers at 0.144. Band hold rates are 0.150, 0.280, 0.300,
0.350, 0.360, 0.400 and 0.440, so the median is 0.350 and `early.hold_rate`
triggers at 0.210.

Creative A: 16,120 three-second plays over 124,000 impressions is 0.130, under
0.144, so hook fails. 5,642 fifty-per-cent plays over 16,120 three-second plays
is 0.350, above 0.210, so hold passes. Failing element: the opening alone. `cut`,
rewrite the first seconds and keep the rest.

Creative B: 26,520 over 102,000 is 0.260 and hook passes. 3,978 over 26,520 is
0.150, under 0.210, so hold fails. Failing element: everything after the
opening. `cut`, keep the hook, rebuild the body. Reporting A and B as one finding
would have produced two identical, wrong briefs.

Creative C: 0.300 hook and 0.440 hold, both above trigger. No cut.

The under-15-second band holds only two survivors, both from the starved six,
which is below `early.median_stability_floor`. Hook and hold there are
`needs_data` and no cut fires on them; that refusal is stated rather than papered
over with a two-creative median. `early.cost_multiple` runs against the whole ad
set instead, and the output says it did: ad set median cost per outbound click
1.80, so the trigger is 4.50. The 11-second creative spent 118 for 22 outbound
clicks, which is 5.36, and fires. The 13-second creative spent 115 for 41
outbound clicks, which is 2.80, and does not. Both are cut anyway under
`delivery.starved_flag`, one on two grounds and one on one.

Ranking: only A, B and C clear `delivery.ranking_floor`, so only those three may
be compared with each other or handed to a brief. The eight cuts are decisions,
not comparisons, and the output does not rank them.

## Guardrails

- Never report an early cut as a result. Everything here is `low`.
- Never put a `never_delivered` creative in the cut list or a brief input.
- Never exclude a starved creative from the cut list. Non-allocation is a
  verdict the platform reached, not a gap in the data.
- Never take an `early.*` median across mixed video lengths.
- Never collapse a hook failure and a hold failure into one row.
- Never omit `early.false_negative_rate` from the output.
- Never compare a creative to another account's benchmark.
- Do not pause anything. Recommend, and let a human approve.
