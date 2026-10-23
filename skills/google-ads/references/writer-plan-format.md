# Google writer plan format

Write a JSON plan, validate it, then (with approval) execute it.

```bash
adsgm google apply --plan /path/plan.json                         # validate_only: Google checks, nothing changes
adsgm plan <action> --google-plan /path/plan.json                 # ticket: action + entities derived from the plan
adsgm google apply --plan /path/plan.json --ticket tkt_... --execute
```

Setup: `pip install google-ads` and the `GOOGLE_ADS_*` variables in [.env.example](../../../.env.example). The writer uses `GoogleAdsClient.load_from_env()`.

## Operations

```json
{
  "client": "example-remodeling",
  "customer_id": "1234567890",
  "operations": [
    {"op": "update_budget", "campaign_budget_id": "111", "amount": 65.0},

    {"op": "set_status", "resource": "campaign", "id": "222", "status": "PAUSED"},
    {"op": "set_status", "resource": "ad_group_criterion", "ad_group_id": "333", "id": "444", "status": "PAUSED"},

    {"op": "add_negative_keywords", "campaign_id": "222",
     "keywords": [{"text": "diy", "match_type": "PHRASE"}, {"text": "kitchen remodel jobs", "match_type": "EXACT"}]},

    {"op": "create_search_campaign",
     "name": "MDX_SEARCH_KitchenRemodel_York_2026-10",
     "daily_budget": 60,
     "bidding": {"strategy": "maximize_conversions", "target_cpa": null},
     "proximity": {"lat": 39.9626, "lng": -76.7277, "radius_miles": 25},
     "locations": [],
     "languages": ["1000"],
     "search_partners": false,
     "negative_keywords": [{"text": "jobs", "match_type": "PHRASE"}, {"text": "diy", "match_type": "PHRASE"}],
     "ad_groups": [
       {"name": "Kitchen Remodel - Core",
        "cpc_bid": null,
        "keywords": [{"text": "kitchen remodel york pa", "match_type": "PHRASE"},
                     {"text": "kitchen remodeling contractor", "match_type": "PHRASE"}],
        "rsa": {"headlines": ["Kitchen Remodeling in York", "Free In-Home Design Consult", "Local Craftsmen Since 2004"],
                "descriptions": ["Plan your new kitchen with a local design-build team.", "Book a free consult. Clear quotes, no pressure."],
                "final_url": "https://www.example.com/kitchen-remodeling", "path1": "kitchen", "path2": "york"}}
     ]}
  ]
}
```

Validation the writer enforces before calling Google:
- `client` equals the active client; `customer_id` is in that client's profile.
- `create_search_campaign`: no `status` field (always PAUSED); geo required (locations or proximity); at least one ad group; RSA 3-15 headlines ≤30 chars, 2-4 descriptions ≤90 chars, https final URL, paths ≤15 chars; Google Search only unless `search_partners` true; EU political advertising declared as "does not contain".
- Keywords 1-80 chars, match type EXACT/PHRASE/BROAD.
- Ad groups and ads inside the new campaign are ENABLED so one approved campaign status change activates it.

Ticket action derived from the plan (riskiest wins): delete > activate > budget > negative_keywords > pause > create. Language `1000` = English. Geo target constant ids: look them up with GAQL on `geo_target_constant` (`WHERE geo_target_constant.name = 'York'`).
