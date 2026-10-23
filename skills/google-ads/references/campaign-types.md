# Google campaign types - what you can see and change here

| Type | Analysis through official MCP | Write through bundled writer |
|---|---|---|
| Search | full: keywords, search terms, QS, IS, ads, assets | create (PAUSED), budget, status, negatives |
| Performance Max | campaign/asset group metrics, search term **insight categories**, placements limited | budget and status only (via `update_budget` / `set_status` on the campaign) |
| Display | campaign/ad group/placement metrics | budget, status |
| Video (YouTube) | campaign metrics, some view metrics | budget, status |
| Demand Gen | campaign metrics | budget, status |
| Local Services | not covered | none - use the LSA UI |

Notes:
- PMax overlaps Search: exact-match Search keywords that match the query exactly take priority (PLATFORM FACT as documented by Google); other queries may go to PMax. Brand exclusions on PMax and account-level negatives control leakage.
- PMax reporting is less granular. Do not over-read asset-level numbers; judge at campaign level against business outcomes.
- For local lead gen with modest budgets, a well-structured Search campaign is usually the base; PMax is an EXPERIMENT once conversion tracking is clean and volume exists.
