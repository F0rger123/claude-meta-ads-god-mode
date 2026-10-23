# Connector research and selection

Researched **2026-10-23** from each project's repository (GitHub API metadata + README), Meta's Ads AI Connectors documentation, and Google's repositories. Stars and dates change; re-check before relying on them. "Claimed" means stated by the project and not independently verified here.

## Decision

| Layer | Selected | Why |
|---|---|---|
| Meta reads + writes (primary) | **Meta Ads MCP (official)** `https://mcp.facebook.com/ads` | first-party, OAuth via Facebook Login for Business, no token handling by us, creates PAUSED, single explicit spend switch (`ads_activate_entity`), 86 tools incl. datasets, Ad Library, anomaly signals, experiments, activity logs |
| Meta fallback | **getmcpads-com/meta-ads-mcp-server** (Apache-2.0, self-hosted stdio) | writes disabled by default (`META_ENABLE_WRITES=1`), every write previews until re-sent with `confirm: true`, Graph API v26 (current), metric/breakdown compatibility planner, `meta_health_check` that never prints the token; covers accounts where the official server is not enabled |
| Google reads | **googleads/google-ads-mcp** (official, Apache-2.0) | first-party, GAQL `search` + resource metadata, OAuth proxy with encrypted token storage option; **read-only** |
| Google writes | **bundled writer** (`connectors/google/writer.py`, this repo, MIT) on Google's official `google-ads` client (Apache-2.0) | the official MCP cannot write; a thin, auditable, validate_only-first layer we control beats a third-party all-in-one with deletes exposed |
| Analytics | **googleanalytics/google-analytics-mcp** (official, Apache-2.0) | GA4 reports, Google Ads link check; read-only except annotations |

Not selected as defaults (documented extension points instead): byadsco (best agency/multi-tenant option - recommended if you host a shared server), Adplane / Synter / AdKit / NotFair / Pipeboard (hosted multi-platform services), Draivix (broad but exposes deletes without a preview layer), the skill-only projects (knowledge, not connectors).

Smallest strong combination: **official Meta MCP + official Google Ads MCP + bundled Google writer**, with getmcpads as an optional Meta fallback and GA4 MCP optional.

## Comparison

Legend: R read, W write, ✓ yes, ✗ no, ~ partial, ? not documented.

| # | Project | Official | Meta | Google | Writes | Campaign / ad create | Budget edit | Targeting | Reporting | Multi-account / agency | Auth | Self-host | Token storage | Rate limiting | Destructive-action protection | API freshness | Maintenance (last push) | License | Setup |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Meta Ads MCP (mcp.facebook.com/ads) | ✓ Meta | R/W | ✗ | ✓ 36 write tools | ✓/✓ (PAUSED) | via `ads_update_entity` | ✓ | ✓ trends, anomalies, benchmarks | accounts the user can access; selection per call not documented | OAuth (FB Login for Business), user or Employee system-user token | ✗ hosted | Meta / client | Meta-side | paused creates, separate activate tool, no campaign delete, client-side confirmation | current (Meta-run) | active (2026) | Meta terms | low |
| 2 | attainmentlabs/meta-ads-mcp | ✗ | R/W | ✗ | ✓ | ✓/✓ PAUSED | ✓ | basic | ✓ | single account via env | long-lived token in env | ✓ | env | ? | `dry_run=True` default, `confirm=True`, daily budget cap env, JSONL audit log; exposes delete | ? | 2026-10-20, 17★ | MIT | low |
| 3 | getmcpads-com/meta-ads-mcp-server | ✗ | R/W | ✗ | ✓ 23 (off by default) | ✓ campaign; ad set/ad create | ✓ | ✓ search targeting | ✓ 190 metrics, query planner | any account the token sees | System User token (env) | ✓ | env | ? | writes disabled by default, preview-then-confirm on every write | Graph v26 | v2.0.0 2026-09-20, 1★ | Apache-2.0 | medium (Node 22) |
| 4 | byadsco/meta-ads-mcp | ✗ | R/W | ✗ | ✓ (142 tools) | ✓ | ✓ | ✓ audiences, lookalikes | ✓ portfolio summary | ✓ multi-tenant, per-request token | FB Login OAuth + System User registry | ✓ (Cloud Run) | AES-256-GCM in Firestore | ✓ BUC header parsing, circuit breaker, write pacing | tool hints (destructive/readOnly); includes deletes, WhatsApp, billing reads | Graph v26 | v4.0.0 2026-09-18, 23★ | MIT | high |
| 5 | rafaelszago/meta-ads-mcp | ✗ | R/W | ✗ | ✓ 24 | ✓ PAUSED default | ✓ | basic | ✓ | single | System User token | ✓ | env | ? | PAUSED default, soft warning on ACTIVE, no caps | ? | 2026-05-22, 3★ | MIT | low (Bun) |
| 6 | aaronpdoherty/meta-ads-genius | ✗ | R (scripts) | ✗ | ✗ (ships no write scripts) | ✗ | ✗ | - | CSV / read-only scripts | - | ads_read token / official MCP | n/a | env | - | read-only by design; strong governance docs | n/a | 2026-08-25, 1★ | MIT | low |
| 7 | sepivip/meta-ads-skill | ✗ | via official MCP | ✗ | via official MCP | via official MCP | via official MCP | radius recipes | - | - | official MCP OAuth | n/a | n/a | - | paused + two confirmation pauses | n/a | 2026-10-02, 14★ | MIT | low |
| 8 | adplane/claude-plugin | ✗ (hosted service) | R/W | R/W | ✓ | ✓ PAUSED | ✓ | ✓ | ✓ | per Adplane account | Google sign-in to Adplane, then platform OAuth | ✗ | Adplane servers | Adplane-side | paused creates, read-back after write, deletes limited to never-spent | ? | 2026-10-09, 0★ | MIT (plugin); service has its own terms | low |
| 9 | Draivix/aidvertaiser | ✗ | R/W 40 | R/W 81 | ✓ | ✓ | ✓ | ✓ | ✓ + GA4/GSC/GTM | multiple accounts | browser OAuth | ✓ | local cache | ? | none documented; many delete tools (campaigns, conversion actions, GA4 properties) | ? | 2026-09-24, 21★ | MIT (pyproject; no LICENSE file) | medium |
| 10 | himckub/toprank (NotFair) | ✗ (hosted) | R/W | R/W ~100 | ✓ | ✓ | ✓ | ✓ | ✓ | per NotFair account | OAuth 2.1 to notfair.co | ✗ | OS keychain + NotFair | ? | ? | ? | 2026-06-03, 0★ | MIT (skills); service terms | low |
| 11 | Synter-Media-AI/mcp-server | ✗ (hosted) | R/W | R/W | ✓ (paid tier) | ✓ | ✓ | ✓ | ✓ 43 platforms read | ✓ workspaces, scoped keys | OAuth 2.1 / API keys | partial (local stdio for 16 platforms) | Synter | ? | `dry_run`, read-only flag, server-side scopes, audit log (claimed) | ? | 2026-10-20, 21★ | MIT (client) | low |
| 12 | AdKit Ads Manager (adkit/ads-mcp) | ✗ (hosted, paid) | R/W | R/W | ✓ via `adkit_manage` | ✓ | ✓ | ✓ | ✓ | paid tier: multiple projects | sign-in to AdKit | ✗ | AdKit | ? | draft-first approval queue (claimed) | ? | 2026 | MIT (client manifests) | low |
| - | googleads/google-ads-mcp | ✓ Google | ✗ | R | ✗ **read-only** | ✗ | ✗ | ✗ | ✓ GAQL | accessible customers / login customer id | ADC or FastMCP OAuth proxy | ✓ | optional encrypted storage (filetree/redis/firestore) | Google-side | n/a (no writes) | v26 era | 2026-10-09, 1063★ | Apache-2.0 | medium |
| - | googleanalytics/google-analytics-mcp | ✓ Google | ✗ | GA4 | annotations only | ✗ | ✗ | ✗ | ✓ GA4 reports | properties the user can access | ADC | ✓ | ADC | Google-side | n/a | current | 2026-10-22, 3539★ | Apache-2.0 | medium |
| - | pipeboard-co/meta-ads-mcp (reference) | ✗ (hosted, Meta partner) | R/W | via family | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Pipeboard token / OAuth | advanced | Pipeboard | ? | confirmation on writes, paused creates | ? | 2026-10-20, 1325★ | **BUSL-1.1** (not OSI; competing hosted use restricted) | low |

## Notes per decision

- **Why not one all-in-one connector:** hosted multi-platform services (8, 10, 11, 12, Pipeboard) put tokens on a third party's servers and their safety model is opaque to us; several are paid for writes. They remain valid choices - add a family to `connectors/registry.json` and a Backend in the adapter, and the write gate still applies (unknown tools default to approval).
- **Why not Draivix as Google writer:** broad and MIT, but delete tools for campaigns, conversion actions and GA4 properties are exposed with no preview/confirm layer; our gate would catch them, but a smaller surface is safer.
- **Why getmcpads over byadsco as fallback:** for a single operator on one machine, getmcpads' preview-then-confirm and writes-off default match our model with less infrastructure. For agencies hosting a shared endpoint with many staff, **byadsco** is the better fallback (multi-tenant OAuth, encrypted tokens, rate-limit circuit breaker) - its `ads_*` naming matches the official server, so the registry already classifies most of its tools.
- **Knowledge sources:** aaronpdoherty/meta-ads-genius (MIT) and sepivip/meta-ads-skill (MIT) informed which mechanics to cover (breakdown effect, learning phase, signal quality, paused-first launch). No text or code was copied; all prose here is original. Mechanics come from Meta and Google documentation.

## Licenses of dependencies

See [THIRD_PARTY.md](../THIRD_PARTY.md). Connectors are installed by the user, not vendored. Community skill text vendored under `community/vendor/` is listed there with licenses.
