# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's **"Report a vulnerability"** (Security tab -> Advisories) on this repository. Do not open a public issue for anything that could let Claude write to the wrong account, bypass approval, or leak credentials. Expect an acknowledgement within 7 days.

Especially in scope:
- a tool call that changes spend, status, budgets, targeting or tracking without passing the write gate,
- a way to make the gate approve a write for an account outside the active client's profile,
- secrets appearing in logs, audit records, error messages or committed files.

## Secrets

- This repository contains **no credentials** and must never contain any: no Meta access tokens, Google Ads developer tokens, OAuth client secrets, refresh tokens, API keys, client data or ad account data. A test (`tests/repo-hygiene`) scans for common token formats and runs in CI.
- Preferred auth: **official OAuth** in the MCP client (Meta Ads MCP via Facebook Login for Business; Google via Application Default Credentials or the Google Ads MCP OAuth proxy with encrypted token storage).
- Tokens that must exist (self-hosted Meta fallback, Google writer) belong in the MCP server's or your OS's secret storage / private environment, never in this repo, never in chat, never in client profiles.
- `adsgm doctor` reports only whether a variable is set, never its value. The audit log redacts token-shaped strings and any field named like token/secret/password/key.
- Client profiles, tickets and the audit log live in `ADS_GODMODE_HOME` (default `~/.ads-godmode`), outside the repo; `.gitignore` also excludes `clients/`, `.env*`, key files and audit logs.

## If a secret is committed

Revoke it at the source immediately (Meta Business Settings -> System Users / Graph API token debugger; Google Cloud console / Google Ads API Center), then purge it from history. Rotation first - history rewriting does not un-leak a public secret.

## Safety model

See [references/safety-model.md](references/safety-model.md) for the layered write protections and their known limits.
