---
name: video-hook-lines-ad-creative
description: Writes and ranks the opening of a video ad as three synchronised parts, spoken line, on-screen line and opening shot, for one angle at one audience temperature. Use when the deliverable is the first few seconds of a video before any body script exists. Not for feed body copy under the video, which is paid-social-primary-text-ad-creative.
---

# Video Hook Lines

Shared quality bar: `../references/output-standard.md`. All numbers cited here live in `../references/thresholds.md`.
The hook is three things happening at once and they are judged together. A
strong spoken line over a shot that shows nothing is a weak hook.

## Use this skill when

A video ad needs its opening built or rebuilt: what is said, what is shown as
text, and what is on screen inside `limits.video_hook_seconds`. Also use it
when watch time collapses in the first seconds while the rest of the video
holds. The angle and the audience temperature are given, not chosen here. Not
for the primary text that sits above the video in the feed, which is
paid-social-primary-text-ad-creative. Not for Google search assets, which is
search-headline-set-ad-creative. Not for producing one angle across all three
funnel stages at once, which is funnel-stage-variants-ad-creative.

## Required input

- The angle as one sentence, and the audience temperature: cold, warm or
  retargeting.
- Placement and aspect ratio, against `coverage.ratio_set`.
- Sound assumption: does this play with sound on or off by default.
- What footage or assets actually exist. Shots that must be produced are
  flagged, not assumed.
- The claims available with their sources, and any brand or legal constraint.
- Existing hook performance if there is any: retention curve, thumbstop rate.

## Analysis workflow

1. Confirm the angle and temperature in one sentence each. A cold hook and a
   retargeting hook for the same angle are different jobs and are not ranked
   against each other in the same list.
2. Name the moment of recognition: the specific thing the viewer sees or hears
   that tells them the ad is about their problem. Write it before writing any
   line.
3. Write spoken lines that can be delivered inside
   `limits.video_hook_seconds` at normal speaking pace, which is
   `limits.hook_spoken_words` for the spoken line. Count words and syllables,
   never characters.
4. Write the on-screen line for each hook so it stands alone with sound off,
   and check it does not simply transcribe the spoken line.
5. Specify the opening shot for each hook and mark whether the footage exists,
   `needs_data` where the asset library was not supplied.
6. Check the vertical crop. A hook whose on-screen text or subject falls out of
   frame at 9:16 fails at that placement, per `coverage.ratio_set`.
7. Rank the hooks and state the ranking basis explicitly as a judgement, not a
   measurement, labelled `hypothesis` per
   `reporting.no_causal_read_from_export`.
8. Apply `claims.evidence_rule`, `claims.superlative_rule` and
   `claims.restricted_topics` to spoken and on-screen lines alike, marking
   unsourced factual lines `[claim: needs source]`.

## Decision rules

- Spoken line cannot be delivered inside `limits.video_hook_seconds`:
  `rewrite`, and cut the qualifier, never the subject.
- On-screen line that only repeats the spoken line: `rewrite`. Two channels
  saying one thing wastes the sound-off viewer.
- Opening shot with no existing footage: keep the hook, label it
  `approval_needed` on a production cost, and rank it separately from hooks
  that can ship this week.
- Hook that only works for a viewer who already knows the brand, submitted as
  cold: reclassify it as warm rather than repairing it.
- Any line this skill produced that carries `[claim: needs source]` is
  `approval_needed`, whatever else its verdict says, and the marker is never
  stripped to make the set look finished. A marked line is not shippable copy:
  it waits for the named source, or it is rewritten without the claim. A marked hook is ranked outside the
  shippable set, never inside it.
- Existing hook underperforming, read on retention: judge the opening with
  `early.hook_rate`, which is 3-second plays over impressions, and the body with
  `early.hold_rate`, which divides video plays at its own pinned percentage
  over 3-second plays.
  Both are read against the median of the video's own `early.duration_band` and
  never against a median mixing lengths, and neither fires unless the band holds
  at least `early.median_stability_floor` creatives. Neither may fire until the
  creative clears `early.min_exposure` on both its halves, impressions and
  spend against one target cost per acquisition. Both are `low` by definition
  and neither is reported as a result.
- Under `early.min_exposure`: state the retention read is not usable and rank
  on judgement only. Do not reach for `test.click_floor` here. That floor is
  the CTR-judged fallback for a test being read on clicks, and a click count
  says nothing about whether the opening held a viewer; using it would answer a
  different question in the right-looking notation.
- `early.hook_rate` failing while `early.hold_rate` passes: `rewrite` the
  opening only. The reverse, hold failing while hook passes, is a body problem
  and this skill hands it back rather than rewriting an opening inside
  `limits.video_hook_seconds` that already worked.

## Output format

No verdict line. A ranked table: rank, spoken line, on-screen line, opening
shot, footage exists yes or no, sound-off readable yes or no, evidence label,
decision label. Then one paragraph naming the ranking basis. Then
`What this could not see`, `Missing data`, `Approval gates`.

This skill writes and ranks openings rather than reading a test or a time
series, so it issues no `high` confidence label. The comparison family's `high` rests
on `test.min_runtime` and `test.volume_floor`, conditions of a test that has not
been run on these hooks. Where an existing hook's retention is read, that read
sits in the `early.*` block and is `low` by definition, and the ranking itself is
a judgement labelled `hypothesis`, which carries no confidence label at all.

## Practical example

Illustrative and fictional. Advertiser "Placewise". Angle: "your ad budget is
being spent on the wrong placements". Cold audience, 9:16 reels, sound off
assumed. Six hooks requested. Existing footage: 4 clips of a screen recording.

Shippable, ranked 1 to 3. Each is spoken line, on-screen line, opening shot:

1. "Your budget went somewhere you never chose." / "You did not pick these
   placements" / the placement breakdown scrolling under the cursor. Footage
   exists.
2. "This ad worked. Look where it ran." / "It worked. Now look where." / split
   frame, the ad on the left, one placement row highlighted on the right.
   Footage exists.
3. "Nobody opens the placement report. Watch." / "The report nobody opens" /
   cursor clicking through to the breakdown tab. Footage exists.

All three sit inside `limits.hook_spoken_words` and inside
`limits.video_hook_seconds` at normal pace, and each on-screen line stands alone
with sound off rather than transcribing the spoken one.

Ranked outside the shippable set:

4. "We found four placements doing nothing." `[claim: needs source]`. The count
   came from a screenshot nobody attached, so it is `approval_needed` and waits
   for the export.
5. A hook opening on a founder face to camera. Kept, but there is no such
   footage, so it is `approval_needed` on a shoot.

Declined, not written in any form: "Most advertisers waste 60% of their budget."
The figure has no source, `claims.evidence_rule` bites, and it is not softened
into "most advertisers waste a big share" either. It would be written the day a
named study or the account's own export is supplied.

Retention read: refused. The supplied data covers 640 impressions on the
existing hook with spend under one target cost per acquisition, so
`early.min_exposure` is not met and neither `early.hook_rate` nor
`early.hold_rate` may fire. Video length was also not supplied, so under
`early.duration_band` there is no band to take a median inside. The ranking above
is therefore judgement, labelled `hypothesis`. The click count was offered as a
substitute gate and is declined: `test.click_floor` answers a CTR question and
this is a retention one.

## Guardrails

- Never rank a hook you have not checked with sound off.
- Never write an opening that depends on footage nobody has confirmed exists.
- Never invent a statistic, a study, a customer or a comparison.
- Never present a judgement ranking as a measured result.
- Do not edit, upload or publish video assets.
- Report every hook declined and why, including hooks requested by name.
