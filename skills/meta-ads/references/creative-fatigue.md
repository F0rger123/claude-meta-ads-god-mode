# Creative fatigue and video metrics

## Fatigue signature (HEURISTIC - needs all of these, not one)

Over 7-14 days at roughly stable spend and targeting:
- frequency rising (prospecting audiences in small local markets fatigue faster),
- CTR (link) falling,
- CPM stable or rising, CPA rising,
- the same ad has carried most of the ad set's spend for weeks.

A single bad day, or a CTR drop that coincides with a CPM spike across the whole account (auction/season), is not fatigue.

Frequency rule of thumb (HEURISTIC): prospecting frequency above ~3 per 7 days with falling CTR is a refresh signal; retargeting tolerates more. Recalibrate per client from history.

## Video metrics

| Metric | Definition (derive from insights fields) | Diagnoses |
|---|---|---|
| Hook rate | 3-second video plays / impressions | first 1-3 s: pattern interrupt, opening frame, first line |
| Hold rate | ThruPlays (or 15 s plays) / 3-second plays | does the body deliver on the hook |
| p25/p50/p75/p100 | video_p25_watched_actions etc. / plays | where attention drops |
| CTR (link) | link clicks / impressions | offer + CTA strength |

Benchmarks vary widely by industry and placement. Compare against the client's own history and against other ads in the same ad set, not against internet numbers.

## What to change (one variable at a time)

- Low hook rate, fine hold rate -> new openings (first 3 s, first line of primary text, thumbnail) on the same body.
- Good hook, poor hold -> body/script problem; tighten, show the result earlier.
- Good video metrics, low CTR -> offer/CTA problem.
- Good CTR, poor CVR -> landing page/form/lead quality, not creative.

## Refresh mechanics

- Add new ads to the existing ad set (adding an ad is a significant edit - do it in one batch).
- Keep the winner running while the new ads gather data; pause it only after a replacement proves itself.
- New ads are created PAUSED and activated with approval (`ads_activate_entity`) - or as a `creative_swap` within guarded-auto limits if the client policy lists it.
- Output a creative brief for the user's production workflow; do not produce final video here. Template: [templates/creative-brief.md](../../../templates/creative-brief.md).
