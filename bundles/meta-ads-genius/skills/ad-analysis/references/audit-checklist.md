# Account Audit Checklist

Weighted control catalog for full-account audits. Category weights reflect leverage: **Signals (pixel/CAPI) 30% · Creative 30% · Structure 20% · Audience 20%**.

Every threshold below is a **default hypothesis, not a law** — before scoring any check, gate on applicability: objective type, sample size, conversion lag, account maturity, and Special Ad Category status. Score each applicable check Pass (1) / Warning (0.5) / Fail (0); mark unknowns as `unknown` (reduces evidence coverage, never counts as a fail). Severity multipliers: Critical ×5, High ×3, Medium ×1.5, Low ×0.5.

`Score = Σ(result × severity × category weight) ÷ Σ(max × severity × category weight) × 100` — grade A ≥90, B ≥75, C ≥60, D ≥40, F <40. Report health, evidence coverage (% of checks with real evidence), and unscored opportunities as **separate axes** — never blend them.

## Signals — pixel & CAPI (30%)
| # | Check | Sev | Pass | Fail |
|---|---|---|---|---|
| S1 | Pixel firing on all key pages/events | Crit | All standard events verified in Events Manager | Missing/duplicate base events |
| S2 | CAPI running alongside pixel | Crit | Server events flowing | Pixel-only (major signal loss post-iOS14.5) |
| S3 | Event deduplication | Crit | `event_id` matched, dedup rate ≥90% | No dedup (double counting) |
| S4 | Event Match Quality | Crit | Purchase ≥8, mid-funnel ≥6.5, PV ≥5.5 | EMQ <6 on the optimized event |
| S5 | Attribution setting consistent & known | High | One setting, stated in reports | Mixed windows compared silently |
| S6 | Conversion event matches business goal | Crit | Optimizing on the event that maps to revenue/qualified leads | Optimizing on a vanity event |
| S7 | Domain verified; data freshness | Med | Events Manager lag <4h | Stale/no data |
| S8 | UTM template on all ads | Med | Consistent params incl. campaign/ad name | Missing/ad-hoc UTMs |
| S9 | CRM feedback loop (B2B) | High | Lead stages fed back via CAPI/Conversion Leads with stored click ID | Platform never learns lead quality |

## Creative (30%)
| # | Check | Sev | Pass | Fail |
|---|---|---|---|---|
| C1 | Creative volume per ad set | High | ≥5 live (≥10 for Advantage+ sales) | <3 |
| C2 | Concept diversity | High | ≥3 distinct angles live (diversity score ≥8/10 — see clustering rubric below) | Variations of one concept |
| C3 | Format mix | Med | ≥3 formats (static/video/carousel) | Single format |
| C4 | Fatigue | Crit | No live ad with CTR −20%+ over 14d at frequency >3 | Fatigued ads still spending |
| C5 | Freshness | Med | New creative shipped ≤21 days ago | Nothing new in 45+ days |
| C6 | Prospecting frequency (7d) | High | <3.0 | >5.0 |
| C7 | Retargeting frequency (7d) | Med | <8 | >12 |
| C8 | Link CTR | Med | ≥1.0% | <0.5% |
| C9 | Hook rate on video | Med | ≥25% 3-sec plays/impressions | <15% |
| C10 | Relevance rankings | Med | No ad Below Average on 2+ diagnostics | Multiple bottom-35% ads spending |

**Creative diversity rubric (0–2 each, total /10):** concept angles · formats · visual treatments · hooks · headlines. Cluster predictor — ads likely collapse into one delivery cluster when they share: same product/visual fingerprint; same first 4 headline tokens; same opening sentence or CTA verb; same 0–3s video shot. Clustered ads compete for the same retrieval slots; diversity is delivery reach.

## Structure (20%)
| # | Check | Sev | Pass | Fail |
|---|---|---|---|---|
| T1 | Campaign count sane | High | 1–3 campaigns per goal | >5 overlapping campaigns per goal |
| T2 | Budget model fits spend | Med | CBO at scale (~>$500/day); ABO for validation/tests | CBO on tiny fragmented budgets |
| T3 | Learning health | Crit | <30% of active ad sets Learning Limited | >50% Learning Limited |
| T4 | Budget-for-learning | High | Daily budget ≥5× target CPA per ad set (or ≥ CPA×50÷7) | <2× |
| T5 | No micro ad sets | Med | Each ad set ≥$10/day | <$5/day fragments |
| T6 | Testing separated from scaling | Med | Dedicated testing budget/campaign (~20%) | Tests starve inside winner campaigns |
| T7 | Recent-edit hygiene | Med | No cascade of learning-resetting edits in last 7d | Daily significant edits |

## Audience (20%)
| # | Check | Sev | Pass | Fail |
|---|---|---|---|---|
| A1 | Audience overlap | High | <20% between active prospecting ad sets | >40% |
| A2 | Exclusions | High | Customers/converters excluded from prospecting | Paying to re-acquire customers |
| A3 | Custom audience freshness | Med | Sources refreshed <180 days | Stale/dead sources |
| A4 | Lookalike seeds | Med | Seeded from ≥1,000 high-value users (best customers, not all leads) | Tiny or low-quality seeds |
| A5 | Remarketing pool coverage | Med | Warm audiences captured & served before prospecting scale-up | No remarketing layer |
| A6 | Special Ad Category compliance | Crit | Correctly declared if housing/employment/credit/politics | Undeclared restricted vertical |

## Quick wins
Flag any Critical/High fail fixable in <15 minutes, sorted by severity × impact. Typical: enable dedup `event_id`, verify domain, set consistent attribution, add purchaser exclusions, apply UTM template, pause one fatigued ad.

## Output contract
Report findings as: `check id · result · severity · confidence · observation (with the number seen) · evidence (file/screenshot/API field) · recommendation (testable hypothesis)`. Contradictory evidence gets surfaced side by side, never averaged.
