# Meta connectors

## 1. Official Meta Ads MCP (primary)

The plugin's `.mcp.json` registers `https://mcp.facebook.com/ads` as `meta-ads`. To add it yourself instead:

```bash
claude mcp add --transport http meta-ads https://mcp.facebook.com/ads
```

Then run `/mcp`, choose `meta-ads`, and sign in with the Facebook account that manages the client's business. Grant `ads_read` for analysis; `ads_management` only if Claude should create paused drafts and make approved changes. If your Meta app is required, Meta documents `--client-id <META_APP_ID>`.

No token is stored by this plugin. Tool contracts: [skills/meta-ads/references/mcp-tool-contracts.md](../../skills/meta-ads/references/mcp-tool-contracts.md).

## 2. Self-hosted fallback - getmcpads meta-ads-mcp-server (Apache-2.0)

Use when the official server is not enabled for an account or lacks a field/breakdown.

1. Create a Meta **System User** (Business Settings -> Users -> System Users), assign only this client's ad accounts, generate a token with `ads_read` (add `ads_management` only for writes), expiry Never.
2. Put the token in the MCP server's environment (your OS keychain / shell profile), not in this repo and not in Claude's chat.
3. Merge [mcp.selfhosted.example.json](mcp.selfhosted.example.json) into your Claude config (`~/.claude.json` via `claude mcp add` or a project `.mcp.json` that is gitignored).
4. Keep `META_ENABLE_WRITES=0` until you need writes. With writes on, every write previews until re-sent with `confirm: true`; the Ads God Mode gate treats the preview as read and the confirmed call as a write.
5. First call: `meta_health_check`.

## Agencies hosting a shared server

Consider **byadsco/meta-ads-mcp** (MIT): multi-tenant Facebook Login, AES-256-GCM encrypted tokens in Firestore, Meta rate-limit header parsing with a circuit breaker. Its `ads_*` tool names match the official server, so the gate already classifies most tools; review its extra write tools before enabling them.
