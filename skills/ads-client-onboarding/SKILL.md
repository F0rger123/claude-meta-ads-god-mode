---
name: ads-client-onboarding
description: Add or update an advertising client step by step - business, niche, offer, economics, service area, brand colors, platforms and account ids, billing check, tracking, budget plan (daily vs monthly, how much), approval mode, autopilot on/off, scheduled reports. Use for "add <client> as a new ads client", "set up ads for my business", "onboard", or when adsgm resolve finds no matching client.
---

# Client onboarding

Goal: one validated profile at `~/.ads-godmode/clients/<slug>.json` (outside the repo, never committed). Template: [templates/client-profile.json](../../templates/client-profile.json).

## How to run it

- **One group per message**, 2–4 questions. Reflect back, then wait for "yes, correct" before the next group.
- Anything done on a website gets a **clickable link** and the exact clicks. The links are in [docs/SETUP_WIZARD.md](../../docs/SETUP_WIZARD.md), Steps 3–6.
- "Not sure" is a fine answer: record it empty and move on. Never guess an account ID.
- Progress line on every message: `Client setup · 3 of 8 · Money`.

## The groups

1. **Business:** name, website, what you sell, the one offer to advertise first, the **niche** (short slug, e.g. `roofing-storm`, `dental-implants`), service area (cities + radius), excluded areas.
2. **Customer and economics:** target customer; average job value; how many leads become customers (**close rate**); margin. If they don't know a target cost per lead, compute the most they can afford (job value × close rate × margin × ~30%) and show the math (HEURISTIC).
3. **Brand** (for graphic ads): main, background and accent colors (hex, or "take them from the website"), logo file path, a folder of real job photos. Approved reviews they're happy to quote.
4. **Accounts:**
   - Meta ad account (`act_…`), Page, Instagram, dataset/pixel.
   - Google customer ID (and manager ID).
   - GA4, Search Console, CRM.
   - Missing any? Walk them through creating it with the wizard links.
   - **Verify every ID with a read** and confirm the account name with them.
5. **Billing check:** does each ad account have a payment method? If not, link them to [Meta Billing & payments](https://business.facebook.com/billing_hub/payment_settings) / [Google Ads Billing](https://ads.google.com/aw/billing/summary). They enter the card themselves; you never see or type it. Offer to suggest an account spending limit after the budget plan.
6. **Money:**
   - Ask: per day, per month, a fixed promotion, or "you tell me"? Is the month a hard ceiling? Which platforms?
   - Run `adsgm budget-plan --client <slug> ...` and explain in plain words: budget type, what it buys, whether to start on one platform, and whether to spend a bit more (with the math) or hold back.
   - Agree on the plan, then `--save` it.
7. **Control:**
   - Approval mode: `approval` is recommended; `draft` if they only want builds.
   - Who approves, and the high-budget threshold.
   - Banned claims and required disclaimers.
   - Special ad category concerns (financing, housing).
8. **Autopilot and reports. Always offer both.**
   - Autopilot, on or off: it pauses clear losers, fixes and relaunches tired ads in the same ad set, and blocks a few wasted Google searches.
   - It stays under a daily spend cap they choose (suggest the plan's daily figure plus 10–20%), and never launches new campaigns, raises budgets or touches billing.
   - If yes: `adsgm autopilot on --client <slug> --cap <amount>`.
   - Scheduled reports (daily check, Monday review, monthly report): if yes, `/ads:schedule`.

## Save

```bash
adsgm clients new <slug>          # template in ~/.ads-godmode/clients/
# fill it (Write tool) with the answers
adsgm clients validate ~/.ads-godmode/clients/<slug>.json
adsgm clients check-isolation     # no account may belong to two clients
adsgm use <slug>
```

Then offer `/ads:research <client>` (niche playbook) and a first read-only `/ads:audit`.

Finish with a summary:
- client, niche and platforms;
- accounts, with the verified names;
- billing OK or not;
- the budget plan;
- the approval mode;
- autopilot and schedules, on or off;
- what's missing.

Never paste tokens or card details into a profile. Never copy one client's account IDs into another.

## Several clients in one chat

Onboard each one in turn, as separate profiles. Afterwards the person can mix requests in one chat ("roofing campaign for A, dental campaign for B"). Run `adsgm use` before each client's work, and the gate checks every change against that client's accounts.
