# Diagnostics: Relevance Rankings, Auction Overlap, Fluctuation Triage

## Ad relevance diagnostics
Three per-ad rankings vs. competitors for the same audience (Above Average / Below Average bottom 35% / 20% / 10%). Diagnostic only — **not** auction inputs. Unavailable under 500 impressions.

| Pattern | Likely issue | Action |
|---|---|---|
| Low **Quality** | Creative perceived low quality / clickbaity | Improve creative craft; remove engagement-bait patterns |
| Low **Engagement rate** | Ad doesn't compel interaction | New angles; stronger hook (first 3 seconds / first line) |
| Low **Conversion rate** | Post-click problem | Landing page speed/message match; audience-offer fit |
| **All three low** | Audience-creative mismatch | Rethink targeting or the creative strategy wholesale |

Use for: localizing *which element* underperforms (creative vs. targeting vs. post-click). Don't use for: predicting future results, or as a standalone verdict.

## Auction overlap
Ad sets from the same account targeting overlapping people are deduplicated per auction — only the highest-total-value ad enters; the others are suppressed (you don't outbid yourself, but you do starve yourself).

Symptoms: ad sets that can't spend budget, stuck in learning limited, unpredictable scaling. Separate Pages don't avoid it when the account/audiences overlap.

Fixes, in order: (1) combine similar ad sets — consolidates learning; (2) turn off the learning-limited / lowest-result overlapping ad sets and move budget to the strongest.

## Performance fluctuation triage

**Normal (don't react):**
- Day-to-day CPA swings within 20–30%
- Weekend vs. weekday deltas
- Gradual drift over weeks
- Volatility during learning phase

**Concerning (investigate now):**
- Sustained cost increase >50% for multiple days
- Delivery dropping to near zero
- CVR declining while spend rises
- Degradation with no account changes (check optimization/CHANGELOG.md first if the workspace has one)

**Pre-diagnosis checklist:** (1) learning phase? (2) what's baseline variance for this ad set? (3) external factors — seasonality, news, platform changes, competitor surges? (4) sample size sufficient? Evaluate stable ad sets over 7+ day windows.

**Common causes map:** learning phase → wait; audience saturation (frequency climbing, CTR falling) → expand audience or refresh creative; auction dynamics (CPM up, CTR flat) → competition, ride it out or improve quality; creative fatigue (frequency >2.5–3 with CTR decay over 2+ weeks) → refresh creative, don't just cut budget; seasonality → compare to the same period historically, not last week.
