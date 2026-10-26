# Safety model

## Principles

```
READ FREELY · ANALYZE FREELY · PLAN FREELY · DRAFT FREELY
CREATE PAUSED · WRITE CAREFULLY · SPEND ONLY WITH APPROVAL
```

## Layers (defense in depth)

| Layer | Enforces | Where |
|---|---|---|
| 1. Skill instructions | verify client/platform/account/entity, plan before write, show summaries, read back | `skills/ads-core` |
| 2. Active-client session | writes are evaluated against one explicitly selected client; expires after 12 h | `godmode/session.py` |
| 3. Client profiles | account ownership; one account can belong to only one client | `godmode/profiles.py` |
| 4. Change tickets | entity-level writes need a fresh (30 min), single-use plan matching client, platform, action, entities and budget amount | `godmode/tickets.py` |
| 5. Policy | automation mode, guarded-auto limits, always-approval and always-blocked actions | `godmode/policy.py`, `godmode/budget.py` |
| 6. PreToolUse hook | allow / ask / deny for every ads MCP tool and the Google writer; fails closed on errors | `hooks/write_gate.py` |
| 7. Connector safeguards | official Meta MCP creates paused; getmcpads previews until `confirm: true`; Google writer is `validate_only` until `--execute` | connectors |
| 8. Platform | Meta/Google permissions, rate limits, review | platforms |

## What the hook does

1. Classifies the tool (registry) -> platform + action. Reads pass untouched.
2. No active client -> deny.
3. Platform not enabled for the client -> deny.
4. Any account id in the call that is not the client's -> deny, naming the owner if another client has it.
5. Create with ACTIVE/ENABLED status -> deny. Paused create -> policy (allowed except in read_only).
6. Billing / admin -> deny always.
7. Other writes -> must match an open ticket; budget amount must match the plan (major units, minor units or micros).
8. Ticket verdict: auto -> allow; approval -> ask (the human sees the plan summary in the permission prompt); blocked -> deny.
9. "ask" in `bypassPermissions` / `dontAsk` / `auto` permission modes -> deny, because nobody would see the prompt.
10. PostToolUse: closes the ticket (per entity), writes a redacted JSONL audit record, records change history for cooldowns.

## Scheduled / unattended runs

Jobs from `/ads:schedule` run headless with `ADS_GODMODE_UNATTENDED=1`. The gate then:
1. denies every ad-platform write for clients without `automation.allow_unattended_writes: true` (the default);
2. for opted-in clients, treats the session as unable to ask, so only `auto` verdicts (guarded-auto limits) can run, and anything needing approval is denied.

Learning-loop outcomes change recommendations only; they never edit profiles or limits.

## Autopilot (per client, off by default)

`automation.autopilot.enabled` plus a `daily_spend_cap`. Autopilot only works in approval, guarded_auto or full_auto mode. When it's on, policy returns `auto` for exactly three things:
- **pause**, at most 3 entities per run;
- **creative_swap** within the same ad set, while the account's total daily budget is at or under the cap, at most 3 a week;
- **Google negatives**, at most 10 per run.

A creative_swap ticket covers only two calls: activating its new ad and pausing the ad it replaces. Everything else falls through to the normal rules: activations of new campaigns or ad sets, budgets, geo, tracking, deletes and billing all still need a human yes, or stay blocked. Unattended runs may act only for autopilot clients, and only on `auto` verdicts.

Limit: the gate can't see an entity's type. The autopilot workflow must confirm by a read that the swap's new entity is an ad in the same ad set before planning, and every swap is in the audit log and the morning report.

## Known limits (be honest about them)

- The hook classifies by tool name and payload. A brand-new tool name on a known ads server is treated as `unknown_write` (approval), but a tool on a server whose name does not look like an ads server is not gated. Name ad connectors with `meta`, `google-ads`, `ads` etc. (see [connectors/README.md](../connectors/README.md)).
- Raw HTTP to the Graph API or Google Ads API from Bash/WebFetch is not intercepted. Skills forbid it; do not grant Claude long-lived tokens in its shell environment if you need hard guarantees - keep tokens inside the MCP servers.
- If Python is missing, Claude Code treats the hook failure as non-blocking. `adsgm doctor` checks Python; install it.
- Platform-reported data can be wrong. The gate prevents wrong writes, not wrong analysis - that is what the evidence standards are for.

## Always require a human yes (every mode, including full_auto)

activation of new spend · deletes/archives · tracking/conversion changes · geographic expansion · unknown write tools · budget increases beyond limits or above the high-budget threshold · large negative-keyword lists.

## Never through Claude

billing and payment methods · account spend limits · user roles, ownership, partner access, tokens · creating objects ACTIVE.
