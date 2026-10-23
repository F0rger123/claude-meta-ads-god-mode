# Google Ads bidding

| Strategy | Needs | Use |
|---|---|---|
| Manual CPC | nothing | very low volume, brand-new accounts, tight control |
| Maximize clicks | nothing | early data gathering only; optimizes clicks, not leads |
| Maximize conversions | working conversion tracking | default for lead gen once primary conversions are clean |
| Maximize conversions + target CPA | ~15-30+ conversions/30 days per campaign (HEURISTIC) | protect CPA once stable |
| Maximize conversion value (+ target ROAS) | reliable conversion values | e-commerce, value-based lead scoring |

PLATFORM FACT: Smart Bidding optimizes toward the conversion actions marked **primary** (included in "Conversions"). If a page-view action is primary, the system buys page views.

Rules:
- Set target CPA near the recent actual CPA (within ~10-20%, HEURISTIC). A target far below reality throttles volume.
- Bid strategy changes restart a learning period (Google shows "Learning" status). Do not judge for 1-2 weeks or ~conversion-cycle length.
- Budget-limited Smart Bidding campaigns (high lost IS budget) can look worse when constrained - read impression share before cutting.
- Every bid-strategy change is approval-only. Target CPA/ROAS adjustments fall under `bid` (guarded-auto max ±15% by default).
- Seasonality adjustments / data exclusions exist for known events or tracking outages - recommend them when a tracking outage polluted data.
