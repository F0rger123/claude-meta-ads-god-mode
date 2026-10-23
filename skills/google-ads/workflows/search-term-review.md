# Search-term review and negative keywords

1. **Pull** search terms for 30 days (90 for low-volume accounts) with cost, clicks, conversions, campaign, ad group ([gaql-cookbook.md](../references/gaql-cookbook.md#search-terms-with-spend-and-no-conversions-wasted-spend)). Pull existing negatives and shared lists.
2. **Classify** each term (or n-gram theme for long tails) by intent ([match-types-and-negatives.md](../references/match-types-and-negatives.md#intent-classification-for-search-term-review)).
3. **Quantify waste** - spend on terms/themes with zero conversions and clear irrelevance. Separate "irrelevant" (certain waste) from "relevant but not converting yet" (needs more data - EXPERIMENT).
4. **Check location** - spend from AREA_OF_INTEREST outside the service area is a location-setting problem, not a negative-keyword problem.
5. **Build the negative list** - theme, match type, level (campaign / shared list / ad group), spend saved in the window, and a confirmation that no converting term would be blocked.
6. **Show the preview** to the user:

```
NEGATIVE KEYWORD PROPOSAL - Example Remodeling - 123-456-7890 - last 30 days
Theme            Negative (match)     Level       Terms  Spend   Conv  Blocks a converter?
DIY / how-to     "diy" (phrase)       shared list    14  $96.40     0  no
Jobs             "jobs" (phrase)      shared list     6  $41.10     0  no
Cabinet painting "cabinet painting"   campaign        3  $28.75     0  no
Total waste addressed: $166.25 (5.8% of spend). Confidence: HIGH (clear intent mismatch).
```

7. **Plan + apply** - writer plan with `add_negative_keywords`; validate; `adsgm plan --google-plan` (verdict depends on mode and list size); approval if required; execute; read back negatives.
8. **Cannibalization** - list search terms served by more than one ad group/campaign; propose ad-group-level negatives to route them; same flow.
