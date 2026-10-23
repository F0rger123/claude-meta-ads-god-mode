---
name: ads-client-onboarding
description: Add or update an advertising client profile - business, offer, economics, service area, platforms and account ids, tracking, conversion goals, landing pages, approval policy, automation mode, reporting cadence. Use for "add <client> as a new ads client", "onboard", "set up ads for", or when adsgm resolve finds no matching client.
---

# Client onboarding

Goal: one validated JSON profile at `~/.ads-godmode/clients/<slug>.json` (outside the repo, never committed). Template: [templates/client-profile.json](../../templates/client-profile.json). Field meanings: [templates/ad-account-profile.json](../../templates/ad-account-profile.json) for per-account notes.

## Ask in small groups (3-5 questions per message), in this order

1. **Business** - legal/display name, website, industry, the one offer we advertise first, service area (city + radius or counties), excluded areas, target customer.
2. **Economics** - average job/order value, close rate (lead -> sale), gross margin if known, desired CPL / CPA / ROAS, monthly budget per platform. If the user does not know targets, compute a suggestion: max CPL ≈ average job value x close rate x margin x share of margin they will spend on acquisition. Show the math; label it HEURISTIC.
3. **Platforms and accounts** - Meta: ad account id(s) (`act_...`), Page id, Instagram account, dataset/pixel id(s), lead event name. Google: customer id(s), manager (login) customer id if accessed through an MCC, primary conversion actions. GA4 property, Search Console site, GTM container.
4. **Tracking + CRM** - is CAPI live? call tracking? CRM name and qualified-lead definition? offline conversion import?
5. **Brand + compliance** - brand voice, prohibited claims, required disclaimers, special ad category concerns (financing, housing).
6. **Approval + automation** - who approves, high-budget threshold, automation mode (recommend `approval` for new clients; `draft` if the user wants Claude to only build), guarded-auto limits if chosen.
7. **Reporting** - cadence, audience (owner vs marketing lead), format.

## Verify, do not trust

After the user gives account ids, verify each with a read before saving:
- Meta: `ads_get_ad_accounts` lists the `act_` id; the name looks like the client; `ads_get_ad_account_pages` shows the Page.
- Google: `list_accessible_customers` includes the id; GAQL `SELECT customer.descriptive_name, customer.currency_code, customer.time_zone FROM customer`.
- Record currency and timezone.
If a name does not match the client, stop and ask - this is the most common wrong-account error.

## Save

```bash
adsgm clients new <slug>          # creates a template file in ~/.ads-godmode/clients/
# fill it (Write tool) with the answers
adsgm clients validate ~/.ads-godmode/clients/<slug>.json
adsgm clients check-isolation     # no account may belong to two clients
adsgm use <slug>
```

Or write the full JSON to a temp file and `adsgm clients add <file>` (validates and checks isolation before saving).

Finish with a short summary: client, platforms, accounts (verified names), targets, mode, what is missing (e.g., "no CAPI - recommend /ads:tracking next").

Never paste tokens into the profile. Never create a profile for one client by copying another client's account ids.
