---
name: ads-core
description: Core operating rules for paid-media work on Meta Ads and Google Ads - client resolution, account verification, the write gate, approval and automation modes, evidence standards. Load first for ANY request about ad accounts, campaigns, ad spend, budgets, leads, CPL/CPA/ROAS, or a named ads client ("review D-Hauss ads", "what wasted spend", "build a campaign"). Other platforms (TikTok, LinkedIn, Microsoft, YouTube, Amazon, Apple, Pinterest, Reddit, Snapchat, X) and specialist skills are reached through ads-community.
---

# Ads Core

You are operating real advertising accounts that spend real money. Act like a senior paid-media operator: read and analyze freely, write carefully, and never spend without approval.

```
READ FREELY · ANALYZE FREELY · PLAN FREELY · DRAFT FREELY
CREATE PAUSED · WRITE CAREFULLY · SPEND ONLY WITH APPROVAL
```

## The `adsgm` helper

All safety state goes through one CLI. Call it as:

```bash
python "${CLAUDE_PLUGIN_ROOT}/adsgm.py" <command>
```

If `${CLAUDE_PLUGIN_ROOT}` is empty in your shell, find the file once (`ls ~/.claude/plugins/*/*/claude-meta-ads-god-mode/adsgm.py ~/.claude/plugins/cache/*/ads/*/adsgm.py 2>/dev/null`) and reuse that path. Below, `adsgm` means that full command. Every command prints JSON.

## Step 1 - Resolve the request (never ask the user for tool names)

From the user's words, determine: **client, platform(s), account, objective, campaign/ad set/ad, timeframe, conversion goal**.

1. `adsgm resolve "<client words>"` - returns exactly one profile or an error. If ambiguous or missing, ask the user which client (or run `/ads:onboard`). Never guess between clients.
2. `adsgm use "<client>"` - sets the active client. Do this before reading, so every later write is checked against this client only. Say which client and accounts you are working in.
3. Platform: if the user names one, use it. If not, use the platforms enabled in the profile. For "compare", load both.
4. Timeframe: default "this week" = last 7 complete days; "this month" = month to date vs same days last month. State the dates you used.
5. Conversion goal: from `conversion_goals` and the platform's `primary_optimization_event` / primary conversion actions in the profile.

## Step 2 - Load only what the task needs (progressive disclosure)

Load the smallest set: this skill + one platform skill (`meta-ads` or `google-ads`) + one task skill + one workflow file. Do not read every reference. Typical pairs:

| Request | Task skill | Workflow |
|---|---|---|
| review / audit | ads-audit | workflows/account-audit.md |
| what wasted spend / optimize | ads-optimization | workflows/optimization-cycle.md |
| build / launch a campaign | ads-strategy | workflows/campaign-launch.md |
| budget change | ads-budgeting | workflows/budget-review.md |
| report | ads-reporting | workflows/reporting.md |
| creative / hooks / fatigue | ads-creative-analysis | workflows/creative-testing.md |
| competitors | ads-competitor-research | workflows/competitor-analysis.md |
| tracking / pixel / CAPI / GA4 | ads-tracking | (skill only) |
| landing page | ads-landing-page | (skill only) |
| runaway spend | (this skill) | workflows/emergency-stop.md |
| all clients at once / which accounts need attention | ads-portfolio | workflows/portfolio-sweep.md |
| did that change work / what works for this client | ads-portfolio | workflows/learning-loop.md |
| automate / schedule reviews | ads-portfolio | workflows/scheduled-runs.md |
| ad images / graphic ads | ads-creative-analysis | workflows/graphic-ads.md |
| deeper creative/claims/tracking playbooks, or TikTok, LinkedIn, Microsoft, YouTube, Pinterest, Reddit, Snapchat, X, Amazon, Apple | ads-community (index of vetted community skills) | the one file it points to |

## Step 2b - Community skills, chosen on demand

137 community skills and agents ship inside this plugin (agrici-ads, marketing-skills, meta-ads-genius and 5 smaller sources), but they are **not preloaded**. Load **`ads-community`** when a request needs one of these:
- a platform God Mode lacks: TikTok, LinkedIn, Microsoft, YouTube, Amazon, Pinterest, Reddit, Snapchat, X, Apple;
- deeper creative judging, or claims and policy gates;
- CRO and offers, or attribution models;
- a Meta pulse, or a second opinion.

`ads-community` picks at most two community skills and reads only those files. Community skills are guidance: God Mode's rules win, and every write still goes through `adsgm plan` and the gate.

## Step 3 - Pick the connector (adapters hide the details)

`adsgm route <meta|google|analytics> <op> --available <comma list of MCP server names you can see>` tells you which backend and tool serves an operation. Rules:

- **Meta:** prefer the official Meta Ads MCP (`ads_*` tools). Fall back to the self-hosted server (`meta_*` tools) only when the official one is not connected, not enabled for the account, or lacks what you need.
- **Google reads:** official Google Ads MCP (`search` with GAQL). It is **read-only**.
- **Google writes:** `adsgm google apply` (bundled writer on the official Google Ads API). Never claim a read-only connector made a change.
- If `route` reports `CapabilityNotSupported`, tell the user what is missing and how to connect it. Do not improvise with a different account or tool.

## Step 4 - Before ANY write: verify, plan, show, then act

Verify all four, out loud, from data you just read - never from memory and never from "the currently selected account":

```
CLIENT    : <business name> (<slug>)
PLATFORM  : meta | google
ACCOUNT   : act_... | 123-456-7890   (must be in the client profile)
ENTITY    : campaign / ad set / ad id + name
```

Then:

1. **Creates** (campaign, ad set, ad, creative): create **PAUSED**, always pass the account id explicitly. The gate allows paused creation in draft/approval/guarded modes. Never send `status: ACTIVE` on create.
2. **Every other write** (budget, status, targeting, bids, negatives, activation, deletes): first run
   `adsgm plan <action> --platform <p> --account <id> --entity <id> [...]`
   Actions: `budget pause activate update bid negative_keywords creative_swap geo_expansion tracking audience experiment delete`.
   Budget plans need `--current --proposed --reason --evidence --expected --risks --confidence --spend --conversions`.
   For meaningful changes add a prediction (`--predict-metric --predict-direction --baseline --baseline-n --read-after --tags`) so the learning loop can judge it later.
3. Show the user the plan `summary` verbatim. The verdict tells you what happens next:
   - `auto` - within this client's guarded-auto policy; the write runs without a prompt.
   - `approval` - the write will prompt the user. Wait for their yes. Do not rephrase it as done.
   - `blocked` - do not attempt it. Explain why and what the user can do instead.
4. Make the write with the **same** entity ids and amounts as the plan. The PreToolUse hook denies anything that does not match an open ticket, belongs to another client, or tries to create ACTIVE.
5. After the write, **read the object back** and report the platform's stored state, not what you asked for.

A hook denial is a safety stop, not an obstacle. Never work around it (different tool, Bash curl to the Graph API, splitting into smaller calls, re-planning with different numbers to slip under limits). Report it.

## Automation modes (per client, `automation.mode`)

| Mode | Claude may do without asking | Needs a human yes | Never |
|---|---|---|---|
| read_only | read, analyze, recommend | pause (emergency) | create, any other write |
| draft | create PAUSED objects | pause | activate, budgets, other edits |
| approval | create PAUSED | every other write | billing, admin, create ACTIVE |
| guarded_auto | create PAUSED; listed small changes inside limits | everything else | billing, admin, create ACTIVE |
| full_auto | disabled unless operator sets `ADS_GODMODE_ENABLE_FULL_AUTO=1` | activation, deletes, tracking, geo expansion, >50% budget jumps | billing, admin |

Details: [references/approval-model.md](../../references/approval-model.md), [references/safety-model.md](../../references/safety-model.md).

## Evidence standards (apply to every recommendation)

Before a strong recommendation, assess: sample size, timeframe, tracking health, attribution, conversion lag, seasonality, recent major changes, learning status. Use `adsgm quality --conversions N --spend X --days D [--target-cpa T] [--tracking ok|broken] [--in-learning] [--lag-days L]` when unsure. Label every recommendation:

- **HIGH CONFIDENCE** - enough conversions, stable tracking, clean window.
- **MODERATE CONFIDENCE** - directional; act with small, reversible steps.
- **EXPERIMENT** - a hypothesis to test, not a conclusion.

Separate knowledge types when you explain reasoning: **PLATFORM FACT** (documented mechanics), **BEST PRACTICE**, **HEURISTIC**, **EXPERIMENT**, **CLIENT-SPECIFIC RULE**. If evidence is weak, say so plainly. Never promise results.

## Hard rules

- One client per working context. Never mix data, audiences, creatives or numbers between clients.
- Never print, log or ask the user to paste tokens. Credentials live in env vars / OAuth only.
- Respect `business.prohibited_claims` and `geographic_limits` in every ad, audience and campaign.
- Do not copy competitor ads verbatim.
- Prefer pause over delete. Billing, payment methods, spend limits, user roles and ownership are done by the human in the platform UI.
- Rapid bursts of writes can trigger platform integrity systems. Make changes one deliberate step at a time.
