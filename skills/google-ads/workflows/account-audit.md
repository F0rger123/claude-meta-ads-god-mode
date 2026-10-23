# Google Ads account audit checklist

Output format and severity: [workflows/account-audit.md](../../../workflows/account-audit.md).

| Area | Check | Typical severity |
|---|---|---|
| Conversions | primary actions correct; no double counting; calls with duration; values; enhanced conversions; GA4 link | CRITICAL (none/wrong primary), HIGH (duplicates) |
| Tracking health | daily conversions vs GA4/CRM; sudden drops; conversion lag considered | HIGH |
| Location | presence vs interest; spend outside service area (`geographic_view`) | HIGH |
| Search terms | waste %, irrelevant themes, missing negatives, shared lists | HIGH if >10% waste (HEURISTIC) |
| Keyword structure | themed ad groups, match type mix, duplicates, cannibalization | MEDIUM |
| Ads | RSAs per ad group, message match, ad strength, disapprovals, assets coverage | MEDIUM |
| Quality Score | spend-weighted QS, weakest component | MEDIUM |
| Impression share | budget-lost vs rank-lost per campaign | OPPORTUNITY / MEDIUM |
| Bidding | strategy fits conversion volume; tCPA near actual; learning status | MEDIUM-HIGH |
| Budgets | budget-limited winners, overfunded losers, shared budgets | OPPORTUNITY |
| Networks | search partners / display expansion on Search campaigns | LOW-MEDIUM |
| Segments | device, hour, location performance (only with enough data) | LOW |
| PMax | brand cannibalization, search term insight categories, asset groups | MEDIUM |
| Landing pages | speed, mobile, message match, form, call tracking | MEDIUM-HIGH |
| Change history | recent big changes explaining trend breaks | context |

Each finding: severity · evidence (GAQL numbers, dates) · likely impact ($ or leads) · confidence · recommended action · approval required.
