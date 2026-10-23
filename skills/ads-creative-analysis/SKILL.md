---
name: ads-creative-analysis
description: Meta-first creative intelligence - hooks, first seconds, messaging, offer, CTA, visual format, UGC vs polished, static vs video, fatigue, audience-message fit, pattern interrupts, video retention - and structured creative briefs plus single-variable creative tests. Use for "which creative is winning", "new ad ideas", "creative fatigue", "write ad copy", "brief for my video team".
---

# Creative analysis

## Analyze

For each ad with meaningful spend (≥ ~1x target CPA, HEURISTIC), within its ad set:

| Dimension | Read from |
|---|---|
| Hook / first 3 s | hook rate (3 s plays / impressions); opening frame; first line of primary text |
| Retention | hold rate, p25-p100 curve - where people leave |
| Message | the promise, pain, proof, objection handled |
| Offer + CTA | link CTR, CTA button, offer clarity |
| Format | static / video / carousel; UGC / founder / polished; aspect ratios available |
| Fatigue | frequency, CTR trend, age of ad ([fatigue signature](../meta-ads/references/creative-fatigue.md)) |
| Audience-message fit | does the creative speak to the target customer in the profile? |
| Downstream | CVR and lead quality (CRM) - a high-CTR ad can drive bad leads |

Compare ads within the same ad set and window; Meta concentrates spend on predicted winners, so low-spend ads are "untested", not "losers". Use `adsgm` evidence grading before calling a winner.

Tag each ad with a short taxonomy (hook type: question / bold claim / before-after / problem / demo / testimonial; format; talent; offer) so patterns across ads become visible.

## Produce briefs, not videos

Do not edit or render video. Output structured briefs the user's content/video workflow consumes: [templates/creative-brief.md](../../templates/creative-brief.md). Every brief has: hook, script/message, desired length, format, B-roll, CTA, caption, visual references, platform/placement, **hypothesis**. 3-5 hook variants per body are cheap and high-leverage.

## Copy rules

- Use the client's brand voice and service area; no prohibited claims; no invented proof (reviews, awards, years in business, prices, financing).
- Meta: primary text hook within the first ~125 characters; headline short; one CTA.
- Google RSA: headlines ≤30 chars, descriptions ≤90; include keyword theme, location, offer, trust, CTA.

## Testing

[workflows/creative-testing.md](../../workflows/creative-testing.md) - one variable per test, logged in [templates/experiment-log.json](../../templates/experiment-log.json), read at ≥2x target CPA per variant.
