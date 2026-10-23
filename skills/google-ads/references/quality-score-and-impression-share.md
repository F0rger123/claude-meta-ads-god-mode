# Quality Score and impression share

## Quality Score (PLATFORM FACT: diagnostic, 1-10, keyword level)

Components: expected CTR, ad relevance, landing page experience (each Below average / Average / Above average). It is a diagnostic summary, not a direct auction input you can set.

| Weak component | Fix |
|---|---|
| Expected CTR | tighter keyword themes, stronger headlines with the query's words, assets (sitelinks, callouts) |
| Ad relevance | ad group too broad - split themes; mirror keyword language in headlines |
| Landing page experience | message match, speed, mobile usability, clear offer, relevant content |

Prioritize by spend: a QS 4 keyword with $2k spend matters; a QS 3 keyword with $8 does not.

## Impression share (PLATFORM FACT)

- `search_impression_share` - impressions received / estimated eligible impressions.
- `search_budget_lost_impression_share` - lost because budget ran out.
- `search_rank_lost_impression_share` - lost because of Ad Rank (bid x quality x context).
- `search_top_impression_share`, `search_absolute_top_impression_share` - position-related share.

Reading:
- High lost-to-budget + CPA at or under target -> scaling candidate (ads-budgeting; budget increase plan).
- High lost-to-rank -> improve quality/relevance or bids; adding budget will not help.
- Both low and CPA poor -> fix conversion rate / targeting first.
- Impression share is less meaningful for broad match/PMax; read it alongside search terms.
