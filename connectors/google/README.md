# Google Ads connectors

| Layer | Component | Handles |
|---|---|---|
| Reads | official Google Ads MCP (`googleads/google-ads-mcp`, Apache-2.0) | GAQL reports, search terms, QS, impression share, conversion actions |
| Writes | bundled writer [writer.py](writer.py) via `adsgm google apply` | Search campaign creation (PAUSED), budget changes, status changes, negative keywords |

The official MCP is **read-only**. Nothing in this plugin pretends otherwise.

## Prerequisites (both layers)

Google retired developer tokens on **2026-09-09**. API access now belongs to the **Google Cloud project** that owns your OAuth client ([Google's note](https://developers.google.com/google-ads/api/docs/first-call/dev-token)).

1. A Google Cloud project ([create one](https://console.cloud.google.com/projectcreate)) with the [Google Ads API enabled](https://console.cloud.google.com/apis/library/googleads.googleapis.com). Enabling it gives Test access (test accounts only).
2. Production access from the [Google Ads API overview page](https://console.cloud.google.com/google/ads-apis/overview): **Explorer** first (usually automatic), then **Basic**. Basic needs [brand verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification) of the project. Don't apply through the old API Center page in Google Ads; Google no longer processes those requests.
3. An OAuth client ([Credentials](https://console.cloud.google.com/apis/credentials), type Desktop app) and a Google user who can access the client accounts (directly or through a [manager account](https://ads.google.com/home/tools/manager-accounts/)).
4. If production calls fail with `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION`, the project only has Test access. Apply for Explorer or Basic.

## Reads - official MCP

Merge [mcp.google-ads.example.json](mcp.google-ads.example.json) (from Google's README) into your Claude config, with credentials from Application Default Credentials or the server's OAuth proxy mode. For ADC ([install gcloud](https://cloud.google.com/sdk/docs/install)):

```bash
gcloud auth application-default login --client-id-file=client_secret.json \n  --scopes=https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
```
Keep `client_secret.json` outside the repo. Keep the server name `google-ads` so the gate recognises it.

## Writes - bundled writer

```bash
pip install -r requirements-google.txt   # google-ads >= 34.0.0: developer token optional (verified 2026-10-26)
# GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
# GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_LOGIN_CUSTOMER_ID (if via MCC) in your private env
python adsgm.py google apply --plan plan.json            # validate_only - changes nothing
python adsgm.py plan create --google-plan plan.json      # ticket
python adsgm.py google apply --plan plan.json --ticket tkt_... --execute
```

Plan format: [skills/google-ads/references/writer-plan-format.md](../../skills/google-ads/references/writer-plan-format.md). The writer refuses plans for any customer id not in the active client's profile, refuses `status` on new campaigns (always PAUSED), and refuses `--execute` without a matching ticket. The PreToolUse hook additionally prompts (or denies) based on the ticket's policy verdict.

Test safely first: Google offers **test accounts** under a test manager account; a Cloud project with only Test access works against them without touching real spend.
