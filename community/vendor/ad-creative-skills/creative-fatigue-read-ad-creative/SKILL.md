---
name: creative-fatigue-read-ad-creative
description: Decides whether one long-running creative is genuinely tired, or whether the audience got small or the auction got expensive underneath it. Use when a single ad that used to work is sliding week over week and somebody wants to pause it. Because nobody always knows whether an ad used to work, sort it by the input instead, which is checkable: this skill needs a daily export carrying reach alongside impressions for one ad ID over two consecutive windows, because every second signal is a reach figure. Daily reach summed across a window is enough to run it; deduplicated reach is needed only for the new-reach saturation signal, which falls back to the windowed frequency ceiling when the export cannot give it, so a missing deduplication degrades one signal rather than stopping the read. If what you have is one window of that ad's funnel, impressions then clicks then sessions then conversions, the question is losing-ad-diagnosis-ad-creative instead. Boundary against its nearest siblings: this skill reads one creative against its own past on a windowed comparison, not several variants against each other, which is creative-test-readout-ad-creative, and not an ad that never worked at all, which is losing-ad-diagnosis-ad-creative. Platform-agnostic: if a separately installed platform pack ships its own fatigue skill, that one owns the platform's reporting quirks and this one owns the decision.
---

# Creative Fatigue Read

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.

Fatigue is the most over-used word in creative reporting. Most ads called tired
are being served to a smaller audience, or into a more expensive auction, and
pausing them fixes nothing.

## Use this skill when

One named creative that previously performed is declining across consecutive
weeks and the proposed action is to pause or refresh it. Also use it before
approving a refresh budget, so the money goes to a creative whose decline was
actually caused by the creative.

## Required input

- A daily export for that one ad ID: date, impressions, reach, link clicks,
  spend. Reach is required for both windows and impressions cannot stand in for
  it. Daily reach summed across each window runs the frequency signals; where
  the platform reports deduplicated reach for the window, use that and say which
  of the two you used, since only the deduplicated figure supports the new-reach
  reading below.
- The reach the creative had already accumulated before the prior window opens,
  where the export can give it, since new reach cannot be computed without it.
- Placement breakdown for the same dates, or a statement that placements did
  not change.
- The date of the last creative edit on that ad.
- Which Advantage+ creative enhancements were on during each window and the date
  any of them changed (`test.creative_enhancements_rule`). Text variation, image
  expansion, music and 3D animation change the asset per impression, so an
  enhancement switched on between the two windows means the second window is a
  different asset and not a tired one.
- Any budget, bid or audience change inside the comparison period, with dates.

## Analysis workflow

1. Confirm the ad has been live longer than `fatigue.refresh_floor` since its
   last creative edit. Below that, stop and report that delivery has not
   settled; anything read now is the learning period.
2. Establish that both windows ran the same asset, using
   `test.creative_enhancements_rule`. The rule is about the CHANGE between the
   windows, not the enabled state: an enhancement on for both is a constant and
   costs nothing here, while one switched on between them makes the CTR decline
   a comparison of two different assets. This is the single most likely
   manufactured cause of a false fatigue verdict on a current account, because
   these features get enabled account-wide by default and nobody logs the date.
   Where the answer is unknown, say so, cap the read at `low`, and do not write
   the word fatigue.
3. Set the comparison period from `fatigue.window` and state it as two date
   ranges, not as a duration. Apply the recalibration rule in that entry only
   if it fires, and say so if you moved it.
4. Gate on volume before reading any rate. Both windows must clear
   `fatigue.volume_floor`. Below it in either window no signal may fire at all,
   whatever the percentages look like, and the honest output is that this
   creative has not been served enough to be read.
5. Run `../scripts/fatigue_curve.py` over the daily export for the signals it
   implements, which its own docstring names. This arithmetic is not eyeballed.
   A rate compared by eye across two uneven windows is the most reliable way to
   produce a confident wrong answer.
6. Read the CTR change against `fatigue.ctr_decline_flag`, confirming the
   figure is link CTR as defined in the denominators table, and confirming the
   change is in the rate rather than the click count. Without this one there is
   no fatigue verdict to reach, whatever else moved.
7. Read all three candidate second signals from the same export and the same
   two windows, since which one discriminates depends on the audience.
   `fatigue.frequency_rise_flag` is the relative move and is the one that works
   on retargeting and any small pool. `fatigue.saturation_flag` is the new
   reach decline and is the one that works on broad prospecting; compute new
   reach as window reach minus the reach the creative already had, and where the
   export cannot give that figure, say so in the output and fall back to
   `fatigue.frequency_ceiling`. Read `fatigue.frequency_ceiling` windowed, for
   the same window as the CTR you just used, and reject any lifetime frequency
   figure outright.
8. Apply `fatigue.verdict_rule` as revised: the CTR decline plus at least one of
   those three, inside the same window, both windows above the volume floor.
   Then apply its void condition. Where the only second signal is
   `fatigue.frequency_ceiling` and frequency was already above the ceiling in
   the prior window, the verdict is void, because a flag that was lit before the
   decline began did not fire. Say void, not fatigue, and name what the CTR fall
   points at instead.
9. Read CPM against `fatigue.cpm_rise_flag` last, and only as context on the
   auction. It is not one of the second signals in `fatigue.verdict_rule` and it
   never carries a verdict. Report it in the same breath as the CTR result or
   leave it out of the output entirely.
10. Check whether spend, placements or audience moved inside the window. If they
   did, the finding drops to `low` confidence under the confidence scale, and
   the change becomes the leading hypothesis.

## Decision rules

- `fatigue.ctr_decline_flag` crossed and at least one of
  `fatigue.frequency_rise_flag`, `fatigue.saturation_flag` or
  `fatigue.frequency_ceiling` crossed in the same window, both windows above
  `fatigue.volume_floor`: this is fatigue. `cut` the creative or `test` a
  refresh of the same angle, and say which, on whether the angle has ever
  produced a winner. Name in the row which second signal fired.
- CTR crossed and the only second signal is `fatigue.frequency_ceiling`, which
  the creative was already above in the prior window: the verdict is void under
  `fatigue.verdict_rule`, not fatigue. `investigate` the audience, and say
  plainly that the ceiling was already lit and therefore did not fire.
- CTR crossed and no second signal moved: `investigate` the audience and the
  auction. Label the creative reading `hypothesis`, not `export`.
- A second signal moved and CTR did not: `investigate` audience size. The
  finding is the audience, and the creative stays live.
- Either window under `fatigue.volume_floor`: no verdict of any kind.
  `monitor`, and state how much longer at current delivery puts both windows
  over the floor.
- New reach cannot be computed from the export: say so, read
  `fatigue.frequency_ceiling` in its place as `fatigue.saturation_flag`
  instructs, and mark the row `needs_data` on the saturation question rather
  than treating a missing signal as a negative one.
- CPM moved while CTR held: report no CPM row and issue no fatigue verdict, per
  `fatigue.cpm_rise_flag`, which is reported alongside
  `fatigue.ctr_decline_flag` or not at all. Decision `investigate`, because the
  auction is outside the creative.
- An Advantage+ enhancement switched on between the two windows, or the change
  dates are unknown: no fatigue verdict. `investigate` under
  `test.creative_enhancements_rule` and say that the current window served a
  different asset from the prior one, so the decline is a comparison of two
  creatives rather than a decay of one.
- Ad live under `fatigue.refresh_floor`: `monitor`, no verdict, state the date
  it becomes readable.

## Output format

Open with one line: is this creative tired, yes, no or void, naming the CTR
result and which second signal fired or failed to.

| Signal | Current window | Prior window | Change | Threshold key | Crossed | Evidence | Confidence |
|---|---|---|---|---|---|---|---|

This is the pack's time-series skill, so it labels confidence on the
time-series conditions in `../references/output-standard.md` rather than on the
comparison ones, and it can reach `high`. Those conditions, stated here so a row
can be checked rather than trusted: the signals came from an export, both
windows were set by `fatigue.window` and are stated as dates, both windows clear
`fatigue.volume_floor`, and no creative edit and no Advantage+ creative
enhancement change fell inside either window
(`test.creative_enhancements_rule`). All four. Exactly one missing, and not the
volume one, is `medium` with the missing condition named. Either window under
`fatigue.volume_floor` is `low` on its own, as is any window carrying a creative,
budget, placement or enhancement change. `test.volume_floor` is not read here at
all: it counts conversions per variant in a test, and this skill is not reading a
test.

Then the decision, then `What this could not see`, `Missing data`, `Approval
gates`.

## Practical example

Illustrative made-up account data, not a real advertiser.

Input, one ad ID, two consecutive windows set by `fatigue.window`. Current
window: 412,000 impressions, 158,000 reach, 1,030 link clicks, 4,120 spend.
Prior window: 380,000 impressions, 152,000 reach, 1,330 link clicks, 3,420
spend. Last creative edit 61 days ago, so `fatigue.refresh_floor` is cleared.
Enhancements: text variation was on across both windows and image expansion was
switched on four days into the current one. Under
`test.creative_enhancements_rule` the first is a constant and the second is not,
so before any signal is read the output records that part of the current window
served an asset the prior window never carried.
Both windows sit well above `fatigue.volume_floor` on impressions, so the
signals are allowed to fire at all, which is the first thing checked.

`../scripts/fatigue_curve.py` output: current link CTR 1,030 divided by 412,000
is 0.250 per cent. Prior link CTR 1,330 divided by 380,000 is 0.350 per cent.
The relative change is 0.100 over 0.350, a fall of 28.6 per cent, which crosses
`fatigue.ctr_decline_flag`.

Second signals, all three read on the same two windows. Windowed frequency is
412,000 over 158,000, which is 2.61 impressions per person, and sits below
`fatigue.frequency_ceiling`. Prior windowed frequency is 380,000 over 152,000,
which is 2.50, so the relative rise is 2.61 against 2.50, about 4 per cent, far
under `fatigue.frequency_rise_flag`. New reach cannot be computed: the export
supplied no cumulative reach before the prior window, so
`fatigue.saturation_flag` is `needs_data` and, as that entry instructs, the
fallback is the frequency ceiling, which is not crossed either. CPM is 10.00
against 9.00, a rise of 11.1 per cent, under `fatigue.cpm_rise_flag`, and it is
reported here only because the CTR result is being reported beside it.

Verdict: no. Two things stop it independently. The CTR decline crossed and not
one of the three second signals did, so `fatigue.verdict_rule` is not satisfied;
and the image expansion switched on mid-window means the two windows are not the
same asset, so under `test.creative_enhancements_rule` the decline has a
manufactured explanation before fatigue is even reached. This skill cannot
conclude fatigue. Falling CTR against flat frequency and unknown new reach points at the
audience or the auction, and reach grew alongside impressions, so the leading
`hypothesis` is a placement or audience shift. Decision `investigate`, not
`cut`. Three things would settle it: the placement breakdown, the creative's
cumulative reach, which would let `fatigue.saturation_flag` be read rather than
assumed absent, and a re-read on two windows that both sit entirely after the
enhancement change.

## Guardrails

- Never declare fatigue on one signal, whatever the client expects.
- Never use lifetime frequency.
- Never compare click counts where the rule is written on rates.
- Never read fatigue on account impressions instead of creative impressions.
- Do not pause anything. Recommend, and let a human approve.
