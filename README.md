# Claude Meta Ads God Mode

**A safety-first paid-media operating system for Claude.** Meta Ads is the strongest module, Google Ads is built in, and there are extension points for other platforms.

This is more than a prompt file or an MCP wrapper. It is a Claude Code plugin with:

- **Skills** that encode how the platforms actually work: the breakdown effect, the learning phase, attribution windows, match types, impression share, conversion lag.
- **Connector adapters**, so skills never depend on one MCP provider.
- **Client profiles** with strict account isolation.
- **A write gate.** It verifies the client, platform, account and entity before every write. It creates objects **PAUSED** and spends **only with approval**.
- **Workflows** for onboarding, audits, launches, optimization, budgets, creative testing, competitor research, reporting and emergency stops.
- **Tests** for routing, isolation, gating, budget limits, approvals and repository hygiene.

```
READ FREELY · ANALYZE FREELY · PLAN FREELY · DRAFT FREELY
CREATE PAUSED · WRITE CAREFULLY · SPEND ONLY WITH APPROVAL
```

> No tool can guarantee advertising results, and this one does not. It aims to make Claude a careful, evidence-driven operator that does not spend money by mistake.

---

## What you can say

```
Add D-Hauss Remodeling as a new ads client.
Review D-Hauss ads this week.
Show me what wasted the most spend this month.
Build a York, PA kitchen-remodel lead campaign at $60/day on Meta.
Compare Meta and Google for this client.
Something is overspending on D-Hauss - stop it.
```

Claude works out the client, platform, account, objective, campaign, timeframe and conversion goal on its own. You never need to know an MCP tool name.

## Commands

| Command | Does |
|---|---|
| `/ads:onboard <client>` | create or update a client profile; asks questions in small groups and checks every account id with a read |
| `/ads:audit <client> [meta\|google]` | severity-ranked audit; each finding has evidence, impact, confidence, action and an approval flag |
| `/ads:report <client> [period]` | owner summary (spend, results, cost per result, ROAS, what won, what lost, what changed, next steps), then platform detail |
| `/ads:launch <client> <platform> <brief>` | strategy, then a full build created PAUSED; shows exactly what was created; activation waits for your yes |
| `/ads:optimize <client>` | multi-window analysis; separates certain waste from probable waste; changes graded HIGH, MODERATE or EXPERIMENT |
| `/ads:budget <client>` | budget changes with current, proposed, % and $ change, reason, data, expected effect, risks and confidence |
| `/ads:creative <client>` | hooks, retention and fatigue, then structured creative briefs for your video workflow and single-variable tests |
| `/ads:competitors <client>` | Meta Ad Library and Google Ads Transparency Center research; never copies ads |
| `/ads:tracking <client>` | checks Pixel, CAPI, Google conversions, GA4, GTM, UTMs and CRM attribution |
| `/ads:pause <client> <entities>` | pauses exactly the named entities after verifying them |
| `/ads:emergency-stop <client>` | finds runaway spend and pauses precisely identified entities, then summarizes what happened |
| `/ads:doctor` | checks the setup: Python, profiles, isolation, connectors, which env vars are set (never their values) |

## Architecture

```
You ──► Claude + skills (ads-core → meta-ads | google-ads → task skill → workflow)
              │
              │  logical operation ("update_budget", "search_terms")
              ▼
        adapters ── MetaAdsAdapter:     official Meta Ads MCP │ self-hosted getmcpads MCP
                 ── GoogleAdsAdapter:   official Google Ads MCP (reads) │ bundled writer (writes)
                 ── AnalyticsAdapter:   official GA4 MCP │ any Search Console connector
              │
              ▼
   PreToolUse write gate (hooks/write_gate.py)
     active client? platform enabled? account owned by this client?
     created PAUSED? matching change ticket? budget amount matches the plan?
     policy verdict → allow / ask (human prompt) / deny
              │
              ▼
   PostToolUse: close the ticket, redacted audit log, change history (cooldowns)
```

### Selected connectors

The connectors below were chosen after researching 12+ projects. The full comparison is in [references/tool-comparison.md](references/tool-comparison.md).

| Layer | Connector | Why |
|---|---|---|
| Meta (primary) | **Official Meta Ads MCP** `https://mcp.facebook.com/ads` | First-party OAuth, with no token handling on our side. Objects are created PAUSED, and one tool (`ads_activate_entity`) starts spend. 86 tools, including datasets, Ad Library, anomaly signals and experiments. |
| Meta (fallback) | **getmcpads meta-ads-mcp-server** (Apache-2.0, self-hosted) | Writes are off by default, and every write previews until `confirm: true`. Uses Graph v26. For accounts the official server does not cover. |
| Google reads | **Official Google Ads MCP** (Apache-2.0) | GAQL over the official API. **Read-only.** |
| Google writes | **Bundled writer** (`adsgm google apply`, official `google-ads` client) | Validates with `validate_only` first. Creates campaigns PAUSED. Needs a ticket and passes through the gate. |
| GA4 | **Official Google Analytics MCP** (Apache-2.0) | Reports and the Google Ads link check. |

Who handles which job for Google:

| Job | Layer |
|---|---|
| Reads | official MCP |
| Writes, campaign creation, budget changes, status, negatives | bundled writer |
| PMax, Display and Video edits beyond budget and status | not supported; Claude will say so |

## Safety model

| Mode (per client) | Without asking | Needs your yes | Never |
|---|---|---|---|
| `read_only` | analyze, recommend | emergency pause | anything else |
| `draft` | create PAUSED | pause | activate, budgets, edits |
| `approval` *(default)* | create PAUSED | every other write | billing, admin, create ACTIVE |
| `guarded_auto` | small listed changes within limits (e.g. budget ±20%, ≤$50/day, ≥15 conversions, 72 h cooldown) | everything else | billing, admin, create ACTIVE |
| `full_auto` | disabled unless the operator sets `ADS_GODMODE_ENABLE_FULL_AUTO=1` | activation, deletes, tracking, geo expansion, >50% budget jumps | billing, admin |

These rules hold in every mode:
- **Wrong-account prevention.** Every account id in a write must belong to the active client. If the account belongs to another client, the gate names that client and refuses.
- **No hidden prompts.** In `bypassPermissions`, `dontAsk` or `auto` permission modes, any change that needs approval is **denied**, because nobody would see the prompt.
- **Fails closed.** If the gate itself errors on an ads write, the write is blocked.

Details: [references/safety-model.md](references/safety-model.md) · [references/approval-model.md](references/approval-model.md).

## Installation

Requirements: Claude Code, Python 3.9+, and access to the ad accounts.

```bash
claude plugin marketplace add F0rger123/claude-meta-ads-god-mode
claude plugin install ads@claude-meta-ads-god-mode
```

Or, inside Claude Code:

```
/plugin marketplace add F0rger123/claude-meta-ads-god-mode
/plugin install ads@claude-meta-ads-god-mode
```

The plugin installs skills, `/ads:*` commands, the write-gate hooks and the official Meta Ads MCP server entry (`meta-ads`). Run `/ads:doctor` afterwards.

### Meta setup

1. In Claude Code run `/mcp`, choose `meta-ads` and sign in with the Facebook account that manages the business. Grant `ads_read`. Grant `ads_management` only if Claude should create paused drafts and make approved changes.
2. If the plugin's server entry does not connect, add it by hand: `claude mcp add --transport http meta-ads https://mcp.facebook.com/ads`.
3. Optional fallback: [connectors/meta/README.md](connectors/meta/README.md) (self-hosted getmcpads with a System User token).

### Google setup

1. Get a developer token (Explorer access or higher) and enable the Google Ads API in a Cloud project.
2. Reads: add the official Google Ads MCP. The config is in [connectors/google/mcp.google-ads.example.json](connectors/google/mcp.google-ads.example.json). Keep the server name `google-ads`.
3. Writes: `pip install -r requirements-google.txt`, then set the `GOOGLE_ADS_*` variables privately. See [connectors/google/README.md](connectors/google/README.md).
4. Optional GA4: [connectors/analytics/README.md](connectors/analytics/README.md).

### Environment variables

See [.env.example](.env.example). It contains placeholders only. Keep real values in your OS keychain, your shell profile or the MCP server's env, and never in this repo. The official Meta MCP needs **no** env vars.

| Variable | Needed for |
|---|---|
| `ADS_GODMODE_HOME` | where profiles, tickets and the audit log live (default `~/.ads-godmode`) |
| `ADS_GODMODE_ENABLE_FULL_AUTO` | opt-in for `full_auto` (default off) |
| `META_ACCESS_TOKEN`, `META_ENABLE_WRITES` | self-hosted Meta fallback only |
| `GOOGLE_PROJECT_ID`, `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads MCP |
| `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Google writer |

## Client profiles and account mapping

Each client has one JSON file in `~/.ads-godmode/clients/<slug>.json`. That folder is outside the repo and is never committed. It holds:

- business details, offer and service area with geographic limits
- target customer, average job value, lead value and margin
- CPL, CPA and ROAS targets, and the monthly budget
- Meta account, Page and dataset; Google customer id and conversion actions
- GA4, Search Console, CRM and landing pages
- brand voice and prohibited claims
- approval rules, automation mode and guarded-auto limits

Template: [templates/client-profile.json](templates/client-profile.json).

```bash
python adsgm.py clients new d-hauss-remodeling
python adsgm.py clients validate ~/.ads-godmode/clients/d-hauss-remodeling.json
python adsgm.py clients check-isolation        # no account may belong to two clients
python adsgm.py use "D-Hauss"                  # active client for writes (expires after 12 h)
```

## Example: a paused-first Meta launch

```
You:    Build a Meta campaign for D-Hauss Remodeling targeting homeowners around York, PA
        for kitchen remodel leads at $60/day.
Claude: Loads the profile, checks the account and dataset, proposes a strategy (Leads objective,
        25-mile radius, Advantage+ placements). It warns that $60/day at a $90 CPL target
        will probably leave the ad set learning limited.
        Builds the campaign, ad set and ads PAUSED, then shows ids and previews.
You:    Looks good, launch it.
Claude: adsgm plan activate ... → the permission prompt shows the summary → you approve
        → ads_activate_entity → reads the status back.
```

## Example: a budget change

```
CLIENT: D-Hauss Remodeling (d-hauss-remodeling) | PLATFORM: meta | ACCOUNT: act_...
CURRENT BUDGET : 50.00 USD (daily)
PROPOSED BUDGET: 60.00 USD (daily)
PERCENT CHANGE : +20.0%
DOLLAR CHANGE  : +10.00 USD
REASON         : CPL $61 vs $90 target for 14 days, spending full budget
DATA           : 14d $700 spend, 11 leads; not in learning
EXPECTED EFFECT: +2-3 leads/week at CPL up to ~$75
RISKS          : marginal CPL rises; may re-enter learning
CONFIDENCE     : MODERATE
```

## Knowledge layer

Every claim in the references is labeled with one of these types:

- **PLATFORM FACT**, with its source URL and date
- **BEST PRACTICE**
- **HEURISTIC**
- **EXPERIMENT**
- **CLIENT-SPECIFIC RULE**

Start with [references/metrics.md](references/metrics.md), [references/attribution.md](references/attribution.md) and [references/platform-limitations.md](references/platform-limitations.md). Platform depth is in `skills/meta-ads/references/` and `skills/google-ads/references/`.

## Repository layout

```
.claude-plugin/      plugin.json, marketplace.json
.mcp.json            official Meta Ads MCP entry
commands/            /ads:* slash commands
skills/              ads-core, meta-ads, google-ads, onboarding, audit, strategy, budgeting,
                     optimization, creative-analysis, competitor-research, tracking, reporting, landing-page
workflows/           ten end-to-end workflows
references/          tool comparison, safety, approval, metrics, attribution, limits, naming
templates/           client profile, account profile, briefs, plans, reports, experiment log
connectors/          adapters, tool registry, Google writer, example MCP configs
godmode/             stdlib safety core + adsgm CLI
hooks/               PreToolUse / PostToolUse write gate
tests/               connector-routing, account-isolation, write-gating, budget-safety,
                     approval-flow, repo-hygiene
```

## Tests

```bash
python tests/run_all.py
```

The tests use only the standard library and never touch the network. Google API calls are mocked. They cover:

- client isolation and wrong-account prevention
- read/write routing, and connector failures that fail closed
- approval enforcement and paused-first creation
- budget safeguards, guarded-auto limits and the full-auto opt-in
- blocking of destructive actions
- the emergency stop
- secret scanning and manifest validity

Before any live write, use Google Ads test accounts or a Meta test ad account.

## Security

Read [SECURITY.md](SECURITY.md). In short:

- Never commit tokens or client data.
- Prefer official OAuth.
- Keep secrets server-side.
- Token values are never printed or logged.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Safety changes need tests. Knowledge must be labeled and sourced.

## License

[MIT](LICENSE). Third-party components and their licenses are listed in [THIRD_PARTY.md](THIRD_PARTY.md). This project is not affiliated with Meta or Google.
