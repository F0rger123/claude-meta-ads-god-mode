# Google Ads connectors

| Layer | Component | Handles |
|---|---|---|
| Reads | official Google Ads MCP (`googleads/google-ads-mcp`, Apache-2.0) | GAQL reports, search terms, QS, impression share, conversion actions |
| Writes | bundled writer [writer.py](writer.py) via `adsgm google apply` | Search campaign creation (PAUSED), budget changes, status changes, negative keywords |

The official MCP is **read-only**. Nothing in this plugin pretends otherwise.

## Prerequisites (both layers)

1. A Google Ads **developer token** (API Center in a manager account). Explorer access or higher to touch production accounts; Basic/Standard for higher limits.
2. A Google Cloud project with the Google Ads API enabled.
3. OAuth credentials for a user who can access the client accounts.

## Reads - official MCP

Merge [mcp.google-ads.example.json](mcp.google-ads.example.json) (from Google's README) into your Claude config, with credentials from Application Default Credentials (`gcloud auth application-default login --scopes https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform`) or the server's OAuth proxy mode. Keep the server name `google-ads` so the gate recognises it.

## Writes - bundled writer

```bash
pip install -r requirements-google.txt
# GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
# GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID (if via MCC) in your private env
python adsgm.py google apply --plan plan.json            # validate_only - changes nothing
python adsgm.py plan create --google-plan plan.json      # ticket
python adsgm.py google apply --plan plan.json --ticket tkt_... --execute
```

Plan format: [skills/google-ads/references/writer-plan-format.md](../../skills/google-ads/references/writer-plan-format.md). The writer refuses plans for any customer id not in the active client's profile, refuses `status` on new campaigns (always PAUSED), and refuses `--execute` without a matching ticket. The PreToolUse hook additionally prompts (or denies) based on the ticket's policy verdict.

Test safely first: Google offers **test accounts** under a test manager account; a developer token with only Test access works against them without touching real spend.
