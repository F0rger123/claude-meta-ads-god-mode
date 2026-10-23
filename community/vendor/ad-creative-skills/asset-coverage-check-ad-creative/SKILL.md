---
name: asset-coverage-check-ad-creative
description: Counts what is actually live in an ad set, distinct angles, formats and aspect ratios, and reports whether the account has enough variety to learn anything from a week of spend. Use when nobody can say how many angles are running behind this week's budget. Boundary against its nearest siblings: this skill reads only what is serving right now and asks whether the variety on the account is enough to learn anything from the spend going out this week, while angle-inventory asks the historical question of what the account has argued across the whole served library including paused ads; and it never reads performance decay on one creative over time, which belongs to creative-fatigue-read-ad-creative.
---

# Asset Coverage Check

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.

A coverage gap is a supply problem, not a performance problem. An ad set that
never had enough distinct material cannot produce a readable result, so every
verdict downstream inherits the gap.

## Use this skill when

Somebody asks how much creative is live, or the pipeline has stalled and new
assets are not arriving, or a losing week needs to be explained before any ad
is blamed. Also run it before commissioning production, so the brief fills a
counted gap rather than adding another version of what already runs.

Its window is now and its subject is the live set: is there enough variety
serving this week for the money going out this week to teach anybody anything.
The historical question, what arguments this account has actually put in front
of buyers across the whole served library including everything paused, belongs
to `angle-inventory-ad-creative`. Run that one when the complaint is that the
account has tested a lot and learned nothing; run this one when the complaint is
about the spend that is running today.

## Required input

- A list of live ads per ad set: ad ID, ad name, launch date, last edit date.
- For each ad, the angle it argues, stated as a sentence.
- For each ad, the format, static or video, and the aspect ratios uploaded.
- Which placements the ad set is eligible for, and whether placements are
  automatic or manual.
- Which Advantage+ creative enhancements are on for the ad set, image expansion
  in particular, and the date any of them changed
  (`test.creative_enhancements_rule`).
- For search assets, the headline and description counts per ad group.

## Analysis workflow

1. Count creatives using the denominator in `thresholds.md`: one ad ID with its
   own creative and its own delivery. Two ads sharing an image with different
   copy count as two. Reject any count supplied as concepts or file names.
2. Group the live creatives by angle, written as a sentence naming the argument
   for acting. Two entries collapse into one angle under
   `coverage.angle_distinctness` when they share their main claim AND their
   reason for it. This is a test on the argument and not on the words: "save
   time" and "stop wasting hours" have no word in common and are still one
   angle. The noun and verb test is a different rule, it belongs to
   `coverage.rsa_headline_floor`, and it is about headline slots rather than
   angles.
3. Compare the angle count per ad set against `coverage.angles_per_ad_set`, and
   apply its recalibration rule where the ad set sits under
   `test.volume_floor`. Say in the output if you moved the value.
4. Within each angle, count formats and compare against
   `coverage.formats_per_angle`. An angle running in one format only cannot
   separate a format effect from an angle effect, so record that as a limit on
   every later read of that angle.
5. Check uploaded aspect ratios against `coverage.ratio_set`, which is two
   ratios, 4:5 and 9:16. A missing ratio does not remove the placement: with
   placement asset customisation off, the platform crops, letterboxes or pads
   whatever you gave it, so the ad still serves to that surface in a frame
   nobody chose. Name that mechanism by its product name, because the account
   can switch it off: image expansion is the Advantage+ creative enhancement
   that generates the vertical crop and the padded background this rule has been
   describing, and it is covered by `test.creative_enhancements_rule`. Record
   whether it is on, and report the ratio gap as a production job either way.
6. Read supply against `coverage.stale_spend_share`: take each ad set's spend
   in the window and work out what share of it rode creatives older than the age
   that key names. The measure is money, not the launch date of the newest file,
   because an account shipping every week always has a young newest asset while
   most of its budget still sits on three files from the spring. This is a
   supply reading only. Do not translate it into a fatigue verdict; that
   comparison lives under `fatigue.*` and requires the signals in
   `fatigue.verdict_rule`.
7. For search ad groups, count distinct headlines against
   `coverage.rsa_headline_floor`, applying the distinctness test in that entry.
8. Write the single production instruction the account most needs: which angle,
   which format, which ratio, and which ad set it fills.

## Decision rules

- Angle count below `coverage.angles_per_ad_set` and the ad set is spending:
  `approval_needed` on production, because the fix costs money outside this
  pack.
- Format coverage below `coverage.formats_per_angle`: `test` on the missing
  format against the existing one as control.
- A ratio in `coverage.ratio_set` absent while placements are automatic:
  `rewrite`, naming the surfaces now being served from a transformed asset. Not
  `investigate` on delivery, because the ad is being delivered; it is being
  delivered in a frame nobody chose.
- Image expansion on while 9:16 is missing: `rewrite`, and say the vertical
  frame currently running was generated rather than designed. Where the account
  cannot say when it was switched on, `test.creative_enhancements_rule` also
  puts every later comparison across that date at `low`, and the coverage output
  carries that forward so a fatigue read does not inherit it silently.
- Share of spend on old creatives above `coverage.stale_spend_share`: `monitor`,
  with the date the next asset is due, plus a note that every performance
  verdict in this ad set is now read on ageing supply.
- Coverage clear on all four counts: say so plainly and name what made it
  clear. Other skills in this pack read that as a green light.

## Output format

No opening verdict line. This skill returns a count, and a verdict line over a
list is theatre.

| Ad set | Creatives | Angles | Formats per angle | Ratios present | Share of spend on old creatives | Evidence | Decision | Confidence |
|---|---|---|---|---|---|---|---|---|

What `high` means in this skill, since it counts supply rather than reading a
test or a time series: the ad list came from an export or from the interface
listing every live ad in the ad set, every angle sentence was written from the
creative itself rather than from the ad name, the aspect ratios were read off
the uploaded assets, and the spend share was computed from the same export. The
comparison family's `test.min_runtime` and `test.volume_floor` conditions are
conditions of a test and are not borrowed to dress a count as a measurement.

Then one sentence naming the single production instruction, then `What this
could not see`, `Missing data`, `Approval gates`.

## Practical example

Illustrative made-up account data, not a real advertiser.

Input: ad set "Prospecting UK", 6 live ads. Angles, as sentences, reduce to
two: "cheaper than hiring an agency" and "set it up in an afternoon". Ads 1, 2
and 3 argue the first; ads 4, 5 and 6 argue the second. All six are static.
Ad set spend in the window 6,400, of which 4,350 ran on ads launched before the
age named in `coverage.stale_spend_share`. Headline counts not supplied. Aspect
ratios not supplied.

Reading: 6 creatives, 2 angles, which sits below `coverage.angles_per_ad_set`,
and the ad set is above `test.volume_floor` so the recalibration rule inside that entry does
not fire. Formats per angle is 1 against `coverage.formats_per_angle`, so any
weak result on either angle is unverified as an angle effect. Old creatives
carried 4,350 of 6,400 spend, which is 68 per cent and above
`coverage.stale_spend_share`, so the supply reading fails on money even though
nobody in the account would have called this library old.

Declined: no aspect ratio verdict. The upload list was not supplied, so ratio
coverage on both entries in `coverage.ratio_set` is `needs_data` and the row is
left empty rather than inferred from the placement setting. Saying the account is
missing 9:16 because it is a feed account would be an assumption presented as a
count. The enhancement state was not supplied either, so whether the vertical
frame now serving was generated by image expansion is `needs_data` under
`test.creative_enhancements_rule` rather than assumed off.

Output: three findings, all `export` except the ratio row, which is
`needs_data`. Production instruction: one video for "set it up in an
afternoon", 9:16, into Prospecting UK.

## Guardrails

- Never count concepts, files or ad names as creatives.
- Never convert an ageing library into a fatigue verdict.
- Never infer aspect ratio coverage from placement settings.
- Never state a per-placement cost per creative as fact. On campaigns using
  dynamic creative or Advantage+ creative asset variations the served asset
  differs per impression, so `reporting.no_creative_level_placement_cost`
  applies and any such figure is an estimate that must be labelled one.
- Do not upload, pause or edit anything. Recommend, and let a human approve.
