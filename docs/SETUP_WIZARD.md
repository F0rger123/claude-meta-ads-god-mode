# Setup wizard — for AI agents

Use this when someone pastes a link to this repository into a chat and says anything like *"set this up for my business"*, *"what is this?"*, *"install this for my ad accounts"* or *"I want to run ads for my clients"*. You are the setup wizard.

## How to run this wizard (read first)

1. **One step at a time.** Show only the current step. End every step with its **✅ check** and a direct question ("Done? Tell me when you see …"). **Do not move on** until the person confirms or you've verified it yourself. If something fails, fix it inside that step.
2. **Clickable links.** Every step that happens on a website gets the full link as a markdown link. Tell them exactly what to click, in order. If a menu or URL changed, say so honestly and describe where it lives.
3. **Short and plain.** Two or three questions at a time, plain words, no jargon without a one-line explanation. Reflect their answers back before acting.
4. **Progress line.** Start each message with where they are: `Step 3 of 9 · Connect Meta`.
5. **Safety from minute one.** Read, analyse, plan and draft freely. Create PAUSED. Spend only with an explicit yes. Never ask for, paste or print passwords, card numbers or tokens:
   - sign-ins happen in the person's own browser;
   - payment details are typed by the person on Meta's or Google's own billing page.

   Rules: [`AGENTS.md`](../AGENTS.md), [`skills/ads-core/SKILL.md`](../skills/ads-core/SKILL.md).

**Steps:** 0 Where are we · 1 Interview · 2 Install · 3 Meta business and ad account · 4 Billing · 5 Connect Meta · 6 Google (optional) · 7 First client and budget plan · 8 Autopilot and schedules · 9 First safe task

---

## Step 0 · Where are you running?

| You are… | Full setup? | Next |
|---|---|---|
| **Claude Code** (desktop app, Code tab, or terminal) | ✅ everything, including the automatic safety gate | Step 1 |
| **Codex CLI** | ✅, but you run the safety gate yourself | Step 1 (install via 2B) |
| **claude.ai browser chat** | Partly: reviews, plans, briefs and careful one-by-one changes through Meta's connector. No automatic safety gate and no saved profiles. | Step 1, then the [browser-chat path](#browser-chat-path) |

Can't tell? Ask: *"Are you in the Claude desktop app (Code tab) or the Claude website?"*

For real ad accounts, recommend Claude Code: [download the Claude desktop app](https://claude.ai/download), open the **Code** tab.
✅ *"Which one are you in?"*

## Step 1 · Interview (short groups, reflect back after each)

**A. You**
- Your own business, or clients? How many? Do you have a Meta **Business portfolio** and/or a Google Ads **manager account**?
- Meta only, or Meta + Google?

**B. The first business** (repeat later for each client)
- Name, website, what you sell, the **niche** (e.g. roofing, dental implants), and the service area (cities and radius).
- What's a customer worth? Average job or order value, how many leads become customers (**close rate**), and margin if known.
- Is tracking set up (Meta Pixel / Conversions API, Google conversions)? "Not sure" is fine.

**C. Money**
- Budget: **per day**, **per month**, or **"tell me what you'd recommend"**?
- Is the monthly amount a hard ceiling, or a guide?

**D. How hands-on**
- Advisor only, drafts you approve, or approved changes made for you?
- Autopilot comes in Step 8. Mention now that it exists.

**E. Your computer** (Claude Code / Codex): Windows, Mac or Linux? Run `python --version`; it needs 3.9+ ([get Python](https://www.python.org/downloads/)).

Reflect back in five lines. ✅ *"Did I get that right?"*

## Step 2 · Install

**2A · Claude Code**, in the terminal, or ask Claude Code to run them:
```bash
claude plugin marketplace add F0rger123/claude-meta-ads-god-mode
claude plugin install ads@claude-meta-ads-god-mode
```
Then restart Claude Code. ✅ `/ads:doctor` runs and shows Python OK.

**2B · Codex:**
```bash
codex plugin marketplace add F0rger123/claude-meta-ads-god-mode
codex plugin add ads@claude-meta-ads-god-mode
```
Codex doesn't run Claude Code hooks. Before every ad-platform write, run `python hooks/write_gate.py pre` with the hook JSON and obey its answer, and tell the person this plainly. ✅ `python adsgm.py doctor` shows no failures.

**Optional, no accounts needed:** `python scripts/demo.py` shows the dashboard, learning report and graphic ads with made-up clients.

## Step 3 · Meta business portfolio and ad account

Skip any part they already have. Walk it one click at a time:
1. **Business portfolio:** [business.facebook.com/overview](https://business.facebook.com/overview) → **Create a business portfolio** → business name, their name, work email. (Meta may ask them to confirm the email.)
2. **Ad account:** [Business settings → Ad accounts](https://business.facebook.com/settings/ad-accounts) → **Add** → **Create a new ad account**.
   - Set the **time zone and currency carefully: they can't be changed later.**
   - Pick "My business" (own) or "Another business or client".
3. **Page:** [Business settings → Pages](https://business.facebook.com/settings/pages) → add the business's Facebook Page.
4. **Agencies:** for each client, the client adds you as a partner, or you request access to their ad account (Business settings → Ad accounts → Add → **Request access**). Never use a client's personal login.
5. **Pixel / dataset:** [Events Manager](https://business.facebook.com/events_manager2) → **Connect data sources** → Web. Installing it on the site is a web task; `/ads:tracking` checks it afterwards.

✅ *"Can you see the ad account in Business settings? What's its ID (starts with `act_`)?"*

## Step 4 · Billing (the person enters payment details themselves)

You never see or type card details. Guide them:
1. Open [Billing & payments](https://business.facebook.com/billing_hub/payment_settings). If that link doesn't land on the right account, use [Ads Manager](https://adsmanager.facebook.com/) → menu → **Billing & payments**.
2. Pick the **ad account** in the top selector → **Add payment method** → enter the card or PayPal themselves. Card country and currency must match the business.
3. **Optional safety net:** set an **account spending limit** on the same page.
   - Suggest a figure: the monthly budget from Step 7, plus about 10%.
   - Meta stops all ads when the limit is reached.
   - Only the owner sets this; God Mode never changes billing settings.
4. If "Add payment method" is greyed out, they need finance or admin permission on the ad account (Business settings → People → assign).

Explain how billing works: Meta charges the card **automatically as ads run** (at a threshold or monthly). Nothing gets paid by Claude. God Mode keeps spend inside the budgets and flags overspend or failed payments in its reports.

✅ *"Does the ad account show your payment method now?"*

## Step 5 · Connect Meta to Claude

- **Claude Code:** the plugin adds Meta's official connector. Type `/mcp` → **meta-ads** → **Authenticate**. Sign in with Facebook in the browser and approve access to the business.
  - Grant read access to start; add *manage ads* only if they chose drafts or changes in Step 1D.
  - If it won't connect: `claude mcp add --transport http meta-ads https://mcp.facebook.com/ads`, then `/mcp` again.
- **Codex:** add the same URL as an MCP server and sign in when asked.
- **Background:** [Meta's Ads MCP server guide](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-get-started). To see or remove the connection later, use [Facebook → Settings → Business integrations](https://www.facebook.com/settings/?tab=business_tools).

Verify with a **read**: list the ad accounts and confirm the name and `act_` ID with them.
✅ *"I can see 'Acme Roofing - act_123…'. Is that the right account?"*

## Step 6 · Google Ads (optional, takes longer)

Google changed API access on **2026-09-09**: developer tokens were retired. Access now belongs to a **Google Cloud project** ([Google's note](https://developers.google.com/google-ads/api/docs/first-call/dev-token)). Walk it in order and confirm each:
1. **Ads account:** [ads.google.com](https://ads.google.com/home/) → sign in → create the account. For agencies, a [manager account](https://ads.google.com/home/tools/manager-accounts/) to link clients under.
2. **Billing:** [Google Ads → Billing](https://ads.google.com/aw/billing/summary) → **Add payment method**. They type it themselves.
3. **Cloud project:** [create a project](https://console.cloud.google.com/projectcreate) → [enable the Google Ads API](https://console.cloud.google.com/apis/library/googleads.googleapis.com).
4. **OAuth app:**
   - Set up branding at [Google Auth Platform → Branding](https://console.cloud.google.com/auth/branding).
   - Create an **OAuth client** at [Credentials](https://console.cloud.google.com/apis/credentials). Use the Desktop app type for local use.
   - Brand verification is required for Basic access ([guide](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification)).
5. **API access level:** on the [Google Ads API overview page](https://console.cloud.google.com/google/ads-apis/overview), request **Explorer** access first (production, small daily limit, usually automatic), then **Basic** after brand verification. Don't use the old API Center page in Google Ads; Google no longer processes those requests.
6. **Connect reads** (official Google Ads MCP): add the config from [connectors/google/mcp.google-ads.example.json](../connectors/google/mcp.google-ads.example.json). Sign in with `gcloud auth application-default login` ([install gcloud](https://cloud.google.com/sdk/docs/install)) using the Ads scope shown in [connectors/google/README.md](../connectors/google/README.md).
7. **Writes** (optional): `pip install -r requirements-google.txt`. Set the `GOOGLE_ADS_*` variables in their **own** private environment, never in chat.

✅ After each item. At the end, run a read: list accessible customers and confirm the account name.

## Step 7 · First client profile and budget plan

1. `/ads:onboard <business name>`. Fill in the profile from Step 1, including `business.niche`, brand colors and logo (for graphic ads), and the account IDs verified in Steps 5 and 6.
2. `/ads:research <client>`. It builds or reuses the niche playbook: typical cost per lead, **conversion rate** (the % of clicks that become leads), offers and hooks that work, all with sources.
3. **Budget:** run `adsgm budget-plan --client <slug>` (with `--monthly` / `--daily` / `--hard-cap` as they said). Explain the result in plain words:
   - daily vs monthly vs a fixed flight, and why;
   - what the budget buys;
   - whether to start with one platform;
   - whether there's room to **spend a little more** (with the leads, jobs and revenue math) or a reason to hold back.

   Agree on a plan, then save it with `--save`.

✅ *"Happy with this plan: $X a month, as a daily $Y on Meta?"*

## Step 8 · Autopilot and scheduled reports (always ask)

Explain in a few lines, then ask. Both can be switched off any time.
- **Autopilot (on or off, per client).**
  - It can, on its own: pause ads that clearly lose money; fix tired or failing ads and relaunch the fix in the same ad set; and on Google, block a few wasted searches.
  - It stays under a daily spend cap you pick, and never launches new campaigns, raises budgets, changes billing or deletes anything.
  - Ask: *"Want autopilot on for this client? What's the most the account should ever spend per day?"* Suggest the plan's daily figure plus 10–20%.
  - Then run `adsgm autopilot on --client <slug> --cap <amount>` (the [workflow](../workflows/autopilot.md)).
- **Scheduled reports:** a daily overspend check, a Monday review (what worked, what didn't, what to fix) and a monthly report. They're read-only, except the autopilot run for clients with autopilot on.
  - Ask: *"Want these on autopilot too?"*
  - Then `/ads:schedule`, which shows the jobs and installs them only after a yes.

✅ *"Autopilot: on or off? Scheduled reports: yes or no?"*

## Step 9 · First safe task, and what's next

- First task: `/ads:audit <client>` (read-only), or `/ads:launch <client> <brief>` (everything built **paused**; nothing spends until they say "launch it").
- **More clients:** repeat Step 7 per client (and Step 3's agency access). In one chat you can then say *"Build a roofing campaign for Harbor Roofing and a dental one for Maple Dental"*. Claude switches between clients and checks every change against the right account.
- Wrap up:
  - what's connected and with which permissions;
  - whether the safety gate is automatic (Claude Code) or manual (Codex);
  - whether autopilot and schedules are on;
  - three example prompts ("Review all my clients", "What's working for Harbor Roofing?", "Make three graphic ads for the free-inspection offer").

✅ *"Setup's done. Want to start with the read-only audit, or build the first paused campaign?"*

---

## Browser-chat path

For claude.ai with no local machine:
1. **Skill:** download `meta-ads-god-mode-chat.zip` from the [latest release](https://github.com/F0rger123/claude-meta-ads-god-mode/releases/latest). In claude.ai open **Settings → Capabilities → Skills**, upload it, and turn it on. (If the menu is named differently, look for "Skills".)
2. **Meta connector:**
   - Go to [Settings → Connectors](https://claude.ai/settings/connectors) → **Add custom connector** → URL `https://mcp.facebook.com/ads` → **Connect**, and sign in with Facebook.
   - If Meta's server refuses the claude.ai sign-in, use Claude Code instead.
3. **One project per client:** create a Claude **Project** for each client and paste that client's profile (Step 1 answers) into the project instructions, so clients never mix.
4. Steps 3, 4 and 7 (business, billing, budget plan) work the same. The chat skill does the budget math.
5. Writes in chat have **no automatic safety gate**. The chat skill makes Claude show every change and wait for the person to type **yes** each time, and create everything paused. Autopilot and schedules need Claude Code.
