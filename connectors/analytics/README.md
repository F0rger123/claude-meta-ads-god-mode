# Analytics connectors

- **GA4** - official `googleanalytics/google-analytics-mcp` (Apache-2.0). Example config: [mcp.ga4.example.json](mcp.ga4.example.json). Credentials: Application Default Credentials with the `analytics.readonly` scope. Tools used: `run_report`, `get_account_summaries`, `get_property_details`, `list_google_ads_links`. Its only write (`create_property_annotation`) is gated as a tracking change.
- **Search Console** - no official Google MCP. Any installed Search Console connector works for landing-page and query context; ads analysis never depends on it.
- **CRM** - no connector bundled. Ask the user for qualified-lead counts or use a CRM MCP they already trust; CRM data is the most truthful outcome source.
