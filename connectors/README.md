# Connectors

Skills never hard-code an MCP provider. They ask for a logical operation; an adapter picks the backend.

```
skills / workflows
      │  logical op: "update_budget", "search_terms", "create_campaign"
      ▼
adapters (connectors/*/adapter.py)        adsgm route <platform> <op> --available <servers>
  MetaAdsAdapter     -> official Meta Ads MCP  | self-hosted getmcpads MCP
  GoogleAdsAdapter   -> official Google Ads MCP (reads) | bundled writer (writes)
  AnalyticsAdapter   -> official GA4 MCP | any Search Console connector
      │
      ▼
write gate (hooks/write_gate.py + connectors/registry.json)   classifies every tool call
```

| Folder | Contents |
|---|---|
| [meta/](meta/) | adapter, self-hosted MCP example config |
| [google/](google/) | adapter, bundled writer (`writer.py`), official MCP example config |
| [analytics/](analytics/) | adapter, GA4 MCP example config |
| [registry.json](registry.json) | tool-name -> action rules the write gate uses |
| [base.py](base.py) | Backend / Adapter / Route types |

## MCP server names matter

The gate recognises ad servers by name. Use names containing `meta` (or `facebook`) for Meta, `google-ads` for Google Ads, `analytics`/`ga4` for GA4, and `ads` or the vendor name for others. The plugin registers the official Meta server as `meta-ads`.

## Adding a connector

1. Add a `Backend` with its op -> tool map to the right adapter (lower `priority` wins).
2. Add a family to `registry.json` with read/write rules (put read rules first; anything unmatched becomes `unknown_write` = approval).
3. Add routing and classification tests in `tests/connector-routing/`.
4. Document it in `references/tool-comparison.md` with license and safety notes.

Hosted multi-platform services (Adplane, Synter, AdKit, NotFair, Pipeboard) are already classified by the `generic_ads` family; their write tools fall under the same gate.
