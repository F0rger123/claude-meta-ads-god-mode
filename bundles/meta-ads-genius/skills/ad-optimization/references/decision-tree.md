# The Optimization Decision Tree

Run every Monday on rolling 14-day data, per active ad. Requires: TCPL, per-ad spend, platform leads, CRM-qualified leads (QLs), frequency, days live. Thresholds are practitioner defaults (multi-account B2B data, blended test win rate ~17%: iterations ~25%, new concepts ~10%) — recalibrate to the account after ~2 months of logged decisions.

## Stage 1 — Delivery check (uses the optimizer's own behavior as signal)
Only valid at/below the ad-count ceiling `(daily budget × 14) ÷ (2 × TCPL)`.

| Observation (day 7+) | Verdict | Why |
|---|---|---|
| Spend ≈ $0 after 7 days in an active CBO campaign | **KILL** | The auction/retrieval rejected the creative outright |
| Spend ≥ TCPL lifetime but 7-day avg < ~$10/day | **KILL at next swap slot** | CBO tried it and pulled away |
| Spend below (daily campaign budget ÷ active ads ÷ 2) × 7 | **FLAG** | Under-delivered; judge on quality only after more spend |

Delivery-failure replacement rule: rebuild the **hook/visual/format** — the audience never got as far as your copy or CTA, so iterating those wastes a test slot.

## Stage 2 — Quality evaluation (per ad, 14-day window)
1. **Spend < 3 × TCPL → WAIT.** No verdicts. (Poisson: at 3× spend with zero results, the "it's just variance" hypothesis is ~5%.)
2. **Zero platform leads → SWAP.** Abandon the concept entirely; the angle doesn't stop the scroll into action.
3. **Platform leads but zero/low QLs:**
   - QL rate < 40% → **SWAP**: keep the format, rewrite for ICP specificity (name the audience, the use case, the disqualifier — creative is the targeting).
   - 40–60% → **MONITOR**, tighten copy next iteration.
   - ≥ 60% → healthy signal, continue to cost check.
4. **Cost per QL vs. TCPL:** ≤ 1× → winner track. 1–1.5× → **MONITOR** one more week. > 1.5× → **SWAP** (same angle, different execution).
5. **Graduation to the scaling campaign — ALL required:** ≥5 QLs · QL rate ≥60% · cost/QL ≤ TCPL · ≥14 days live · ≥1 QL in the last 7 days. Move the ad (or duplicate it) into scaling; free the test slot.
6. **Fatigue (scaling ads only):** frequency <3.0 = healthy. 3.0–3.5 **or** cost +20% vs. its own baseline → produce 2 iterations now, don't pause yet. >3.5 **or** cost +40% → swap immediately with the ready iteration. Retargeting tolerates far higher frequency (<8 fine; >12 excessive).

## Swap rules — every swap ships a replacement
| Failure | Replace with |
|---|---|
| Delivery failure (Stage 1) | Different hook/visual/format — not copy edits |
| Zero leads | New concept from an untested buyer situation |
| Leads, no QLs | Same format, ICP-filtering language (specific role/vertical/pain) |
| Cost > 1.5× TCPL | Same angle, new execution (format change, new hook) |
| Fatigue | The pre-built iteration (that's why iterations are produced at the 3.0 warning) |

## Lead-quality scoring (the layer Meta can't see)
After ~20 sales conversations, score each prospect 0–3 on **Urgency / Budget / Fit** (max 9), logged against the originating ad. Rank ads by **average quality score**, not CPL or CTR. The cheap-CPL ad that scores 3.5 loses to the pricier ad scoring 8 — the winner is the one that makes money downstream. Feed this ranking back into which angles get iterations.

## Diagnostic mini-trees
**CPA/CPL rising:** 1) tracking broken? (Events Manager first — always) 2) frequency/fatigue? 3) learning reset by a recent edit? (check the changelog) 4) audience saturation — expand or refresh 5) landing page/CVR shift 6) external: seasonality, competitor surge, auction CPMs. Fix in the order found; most "Meta got worse" reports are #1–#3.

**CTR dropping:** fatigue (same audience, tired creative) → refresh; audience drift (broadened delivery) → check breakdowns at the right evaluation level; competitive pressure (CPM up too) → improve quality rather than bid.

**Lead quality bad:** form friction too low (add work email + 2–3 qualifying questions, Higher Intent type) → targeting seeds polluted (rebuild lookalikes from best customers, not all leads) → creative attracts the wrong ICP (add disqualifying specificity) → optimization event too shallow (move to Conversion Leads / deeper funnel event). Nuclear option: if quality stays bad across all of it, the offer is wrong — route back to the opportunity-spotting skill.
