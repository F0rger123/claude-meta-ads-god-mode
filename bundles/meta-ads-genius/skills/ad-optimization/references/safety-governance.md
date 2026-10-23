# Live-Change Safety & Governance

Load before executing ANY write against a Meta ad account (API, MCP tool, or guided Ads Manager steps). These rules exist because accounts get permanently banned for exactly the behavior an eager automation loop produces.

## The cautionary tale
A developer ran an autonomous Claude loop managing campaigns: rapid sequential API calls, multiple budget adjustments per hour, no human approval. Meta's fraud detection permanently disabled the ad account within a week. **There was no appeal.** Semi-automation — AI drafts, human approves — captures most of the efficiency with none of the ban risk.

## Hard rules
1. **Read-only by default.** Request/use `ads_read` scope unless the user has explicitly chosen write access (`ads_management`).
2. **Human approval gate on every write.** Each mutation (budget, status, targeting, creative, bid) is presented as a draft — entity name + id, before → after, reason, expected effect, rollback — and executed only after the user approves it in conversation. A plan-level "yes to all" covers the listed changes only.
3. **Paused-by-default.** Anything created (campaign, ad set, ad) is created with `status=PAUSED`. Activation is its own approved step.
4. **No autonomous budget loops.** Never chain budget changes on a timer or trigger without a human between iterations. Budget changes above ~25% of an entity's daily budget (or your workspace guardrail, whichever is stricter) need their own explicit approval line.
5. **Rate discipline.** Stay far below ~200 calls/hour per ad account; space mutations by minutes, not milliseconds. Burst-writing is a fraud-detection trigger independent of what the writes do.
6. **One edit session per entity.** Batch all approved edits to an ad set into a single session (each session can reset learning; a drip of sessions resets it repeatedly).
7. **Verify remote state before and after.** Re-read the entity before mutating (it may have changed since analysis) and after (confirm the write took). Record both in the changelog.
8. **Prefer reversible.** Pause over delete, always. Archive only on explicit instruction; never hard-delete.
9. **Log ≥90 days.** Every executed change: timestamp, entity id, field, before/after, approver, reason. In this workspace: `optimization/CHANGELOG.md`.
10. **Stop conditions.** Any policy rejection, spend anomaly, or API error mentioning restrictions → stop all writes, report, wait for the user.

## Token & credential handling
- Tokens live in env vars (`META_ACCESS_TOKEN`) or a secret manager — never in files, configs, chat, or logs. Reference by name, never echo values.
- Long-lived user tokens expire ~60 days: on auth errors, tell the user to re-exchange (`check_token.sh` shows expiry) rather than debugging blind.
- Scope minimalism: analysis work should run on a token that *cannot* write.

## Execution paths, in order of preference
1. **Guided manual** — hand the user exact Ads Manager click-paths for each approved change (zero API risk; default for low-volume changes).
2. **Official Meta Ads MCP** (`mcp.facebook.com/ads`, Business OAuth) — created campaigns default to paused; still subject to every rule above.
3. **Direct Graph API scripts** — only for reads in this plugin by design; write scripts are deliberately not shipped.
