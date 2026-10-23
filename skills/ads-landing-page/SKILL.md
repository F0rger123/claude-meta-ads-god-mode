---
name: ads-landing-page
description: Evaluates the full path from ad to offer to landing page to form/call to follow-up - message match, CTA, trust, speed, mobile UX, form friction, offer clarity and tracking - and recommends fixes ranked by expected impact on conversion rate. Use for "landing page", "why don't clicks convert", "CVR is low", "review the page the ads send to".
---

# Landing page and conversion path

```
AD  ->  OFFER  ->  LANDING PAGE  ->  FORM / CALL  ->  FOLLOW-UP
```

A low conversion rate with healthy CTR is almost never a targeting problem.

## Gather

- The ads' final URLs (with UTMs) from the platform; open each in the browser (mobile viewport first).
- Page speed: PageSpeed Insights / CrUX if a connector is available; otherwise note load time observed.
- The CRM/follow-up process from the profile (`crm`) or by asking: speed to lead, who calls back, hours.

## Evaluate (score each 1-5, with evidence)

| Area | Questions |
|---|---|
| Message match | Does the headline repeat the ad's promise/keyword/location? Same offer, same words? |
| Offer clarity | Is it obvious what you get, what it costs (or that it is free), and what happens next? |
| CTA | One primary action above the fold; button text says the outcome ("Book my free design consult") |
| Trust | real reviews, photos of real work, license/insurance only if verified, local address, guarantees only if real |
| Speed | LCP on mobile; heavy sliders/video; layout shift |
| Mobile UX | tap targets, sticky call button, readable text, no intrusive popups |
| Form friction | number of fields (name, phone, email, zip, project type is often enough), required fields, multi-step vs single |
| Tracking | form submit and call clicks fire Meta/Google/GA4 events; thank-you state; no double firing |
| Follow-up | response time, call-back process, lead-to-appointment rate |

## Output

Top fixes ranked by expected impact x ease, each labeled BEST PRACTICE / HEURISTIC / EXPERIMENT, with a suggested A/B test where uncertain. Page edits are made by the client's web team or the user - this plugin does not change websites.
