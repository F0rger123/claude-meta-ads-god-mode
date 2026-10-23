# Attribution across platforms

## Each source counts differently

| Source | Model | Typical bias |
|---|---|---|
| Meta Ads | click windows 1/7/28 day, 1-day view, 1-day engaged-view (7d/28d view removed from API in 2026) | can claim conversions also claimed by Google; modeled conversions |
| Google Ads | data-driven attribution by default, click date | claims demand created elsewhere (branded search) |
| GA4 | data-driven / last click across channels, session-based | under-credits view-through and cross-device |
| CRM | first touch / last touch / self-reported source | most truthful on outcomes, weakest on touchpoints |

Platform totals usually exceed real conversions. Never add Meta + Google conversions and call it the total.

## Practical hierarchy (BEST PRACTICE)

1. CRM-qualified leads and revenue by source (with UTMs + click ids captured in the form).
2. Blended efficiency: total qualified leads / total spend over time; MER.
3. GA4 by source/medium for directional channel comparison.
4. Platform-reported conversions for in-platform optimization decisions.

## UTM standard

```
utm_source   = facebook | instagram | google
utm_medium   = paid_social | cpc
utm_campaign = <campaign name>          (Meta: {{campaign.name}})
utm_content  = <ad name>                (Meta: {{ad.name}})
utm_term     = <keyword>                (Google: {keyword}) - optional with auto-tagging
```
Google auto-tagging (gclid) stays on. Capture gclid/fbclid/fbc and UTMs into hidden form fields so the CRM can attribute and feed offline conversions back.

## Incrementality

Platform attribution is not incrementality. When budget decisions are large, propose a test: geo holdout, Meta conversion lift study (`ads_experiment_lift_create_test`, experiment action + approval), or time-based on/off with caution. Label results EXPERIMENT until replicated.
