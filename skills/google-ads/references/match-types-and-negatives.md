# Match types, search terms and negatives

## Match types (PLATFORM FACT)

- **Exact** `[kitchen remodel york]` - same meaning as the keyword, including close variants.
- **Phrase** `"kitchen remodel"` - searches that include the meaning of the keyword.
- **Broad** `kitchen remodel` - related searches; relies on Smart Bidding and signals. Works best with healthy conversion tracking and Smart Bidding; risky with Manual CPC or weak tracking.

Negative keywords match differently: **negatives do not expand to close variants or synonyms**. A negative `free` blocks "free" but not "freebie"; add variants you need.

## Intent classification for search-term review

| Class | Example (kitchen remodel, York PA) | Action |
|---|---|---|
| High intent, in-area | "kitchen remodel contractors york pa" | keep; consider exact keyword |
| High intent, out-of-area | "kitchen remodel baltimore" | location issue first (presence vs interest), then negative |
| Research / DIY | "how to remodel a kitchen yourself", "kitchen remodel ideas" | negative phrase ("how to", "diy", "ideas") if no conversions |
| Wrong service | "kitchen cabinet painting", "countertop only" | negative if client does not offer |
| Jobs / supplier | "kitchen remodel jobs", "home depot kitchen" | negative |
| Competitor brand | "<competitor> remodeling" | client decision (policy + cost); not auto-negative |
| Price shopper | "cheap kitchen remodel" | judge by conversion data, not by word |

## Rules for proposing negatives

1. Use 30-90 days of search terms; very low-volume terms (1-2 clicks) are aggregated by theme (n-grams), not judged one by one.
2. Before adding any negative, check it against **converting** search terms in the same window. If it would block a converter, do not add it (or use a narrower exact negative).
3. Level: campaign-level for campaign-specific waste, shared list for account-wide junk (jobs, DIY, free). Ad-group-level negatives for routing between ad groups (cannibalization).
4. Prefer phrase negatives for themes, exact negatives for single bad queries.
5. Present the list with spend, clicks, conversions per term and the expected weekly savings (HEURISTIC: past waste ≈ future waste only if traffic is stable).
6. Large lists (> client's `max_negative_keywords_per_change`, default 10) require approval even in guarded_auto.

## Cannibalization / overlap

Same query matching several ad groups or campaigns: check `search_term_view` grouped by search term across ad groups. Fix with ad-group negatives (route to the best ad group) and consistent match type strategy, not by deleting keywords blindly.
