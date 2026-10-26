# Setup wizard — for AI agents

Use this when someone pastes a link to this repository into a chat and says anything like *"set this up"*, *"what is this?"*, *"install this for my ad accounts"* or *"use this to run my Meta ads"*. You are the setup wizard: figure out where you are running, interview the person briefly, install what fits, prove it works with **read-only** checks, then onboard their first client.

This plugin touches real ad accounts and real money. The rules in [`AGENTS.md`](../AGENTS.md) and [`skills/ads-core/SKILL.md`](../skills/ads-core/SKILL.md) apply from the first minute:

- **Read, analyse, plan and draft freely. Create PAUSED. Spend only with an explicit yes.**
- Never ask for, paste or print tokens, secrets or passwords. Sign-ins happen in the person's own browser (OAuth) or their OS environment.
- Never mix clients. Verify every account id with a read before saving it.

---

## Step 0 — Where are you running?

| You are… | You can… | Go to |
|---|---|---|
| **Claude Code** | Install the plugin with its write gate (hooks) | Step 1, then Step 2A |
| **Codex CLI** | Install the plugin; the write gate is **not** automatic | Step 1, then Step 2B |
| **Another local agent** (Cursor, Gemini CLI, OpenCode) | Clone and use the `adsgm` CLI; call the gate yourself | Step 1, then Step 2B rules |
| **A chat app with no local machine** | Explain and plan only | Step 1, then Step 2C |

If you can't tell, ask: *"Are you talking to me in Claude Code or Codex on your computer, or in a browser chat?"*

## Step 1 — Interview (short groups, reflect back after each)

**A. Accounts**
- Which platforms: Meta (Facebook/Instagram), Google Ads, or both?
- Do you manage ads for your own business or for clients? How many clients?
- Is there a Business Manager / Google Ads manager (MCC) account?

**B. The first client**
- Business name, what they sell, service area (cities/radius), website.
- Monthly budget and what a lead or sale is worth to them (job value, close rate) — used for CPL/CPA targets.
- Is the Meta Pixel / Conversions API, or Google conversion tracking, already set up?

**C. How hands-on should Claude be?**
- Advisor only (reads and recommendations), drafts that you approve, or approved changes made for you?
- Anything that must always need your approval (budgets above a limit, new geos, new audiences)?

**D. Your machine** (local agents only)
- OS, and whether Python 3.9+ is installed (`python --version`).

**E. Several clients?** (if they manage more than one)
- Onboard the rest now or later? Each gets its own profile (`/ads:onboard <name>`).
- Want a weekly all-clients review on autopilot? (`/ads:schedule`. It's read-only by default, and fixes wait for their yes.)
- Brand colors and logo per client, for graphic ads (optional; stored in the profile's `brand`).

Unsure whether it's worth it? Offer the no-accounts demo first: `python scripts/demo.py` builds four made-up clients and shows the sweep dashboard, learning report and graphic ads.

## Step 2A — Install in Claude Code (recommended)

| # | Do | Check it worked |
|---|---|---|
| 1 | `claude plugin marketplace add F0rger123/claude-meta-ads-god-mode` | Command succeeds |
| 2 | `claude plugin install ads@claude-meta-ads-god-mode` | `/plugin` lists `ads` (community skills ship inside it and are routed on demand; nothing else installs) |
| 3 | In Claude Code: `/mcp` → **meta-ads** → the person signs in with Facebook in their browser and grants `ads_read` (add `ads_management` only if they chose drafts/changes in 1C) | `/mcp` shows meta-ads connected |
| 3′ | If the bundled entry won't connect: `claude mcp add --transport http meta-ads https://mcp.facebook.com/ads` | Same |
| 4 | Google Ads (if chosen): follow the "Google setup" section of the README; reads need the official Google Ads MCP, writes need `pip install -r requirements-google.txt` and the `GOOGLE_ADS_*` variables set privately | `/ads:doctor` shows Google ready |
| 5 | `/ads:doctor` | Everything they chose is green; nothing secret is printed |

## Step 2B — Install in Codex (and other local agents)

```bash
codex plugin marketplace add F0rger123/claude-meta-ads-god-mode
codex plugin add ads@claude-meta-ads-god-mode
```

Companions: nothing extra to install. `agrici-ads`, `marketing-skills` and `meta-ads-genius` ship inside `ads`, and the `ads-community` skill picks them on demand. Codex has no prompt-router hook, so it relies on that skill and its catalog. Only if the person wants them always loaded (about +17k tokens of context per session): run `python scripts/install.py --codex --native` (dry run), then add `--yes` after they agree.

**Codex does not run Claude Code hooks.** Before every ad-platform write, call `python hooks/write_gate.py pre` with the hook JSON (`tool_name`, `tool_input`, `permission_mode`) and obey its decision. If the person wants a hard guarantee, keep write-capable connectors off in Codex. Tell them this plainly.

Check: `python adsgm.py doctor` prints JSON with no failures for the platforms they chose.

## Step 2C — Chat app with no local machine

Explain what the plugin does in three sentences, recommend Claude Code (2A) for real account work, and offer read-only help now: an account-structure plan, a campaign brief, or a creative/hook review — labelled as advice, with no invented metrics.

## Step 3 — Onboard the first client

Claude Code: `/ads:onboard <client name>`. Elsewhere:

```bash
python adsgm.py clients new <client-slug>
python adsgm.py clients validate ~/.ads-godmode/clients/<client-slug>.json
python adsgm.py clients check-isolation
```

Fill the profile from the Step 1 answers ([template](../templates/client-profile.json)); verify every account, Page and dataset id with a read. Then a safe first task: `/ads:audit <client>` (read-only).

## Step 4 — Tell them what's next

End with a short message that covers:
- what is installed and verified, and whether the write gate is automatic (Claude Code) or manual (Codex);
- which platforms are connected and with which permissions;
- three example prompts from the README ("Just talk to it"), including "Review all my clients" if they have several;
- if they want it: `/ads:schedule` for daily, weekly and monthly reports (read-only by default);
- that nothing is ever launched or activated without their explicit yes.
