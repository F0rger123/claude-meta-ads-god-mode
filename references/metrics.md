# Metrics, definitions and evidence thresholds

## Knowledge labels used everywhere

| Label | Meaning | Example |
|---|---|---|
| PLATFORM FACT | documented mechanics | "ad set budget changes are limited to 4/hour" |
| BEST PRACTICE | widely recommended by platforms/practitioners, context-dependent | "consolidate ad sets for learning" |
| HEURISTIC | rule of thumb; recalibrate per client | "≥2x target CPA spend before judging an ad" |
| EXPERIMENT | hypothesis to test | "UGC hook beats showroom video" |
| CLIENT-SPECIFIC RULE | from the client profile or history | "never target Maryland" |

## Definitions

| Metric | Formula | Notes |
|---|---|---|
| CPM | spend / impressions x 1000 | auction cost; season and audience driven |
| CTR (link) | link clicks / impressions | Meta: prefer link CTR over all-clicks CTR |
| CPC (link) | spend / link clicks | |
| CVR | conversions / link clicks (or clicks) | landing page + offer + tracking |
| CPL / CPA | spend / leads (or acquisitions) | define the conversion used |
| Cost per qualified lead | spend / CRM-qualified leads | business truth |
| ROAS | conversion value / spend | only with reliable values |
| MER / blended ROAS | total revenue / total ad spend | cross-channel sanity check |
| Frequency | impressions / reach | per window; 7-day for fatigue |
| Hook rate | 3-s video plays / impressions | Meta video |
| Hold rate | ThruPlays / 3-s plays | Meta video |
| Impression share | impressions / eligible impressions | Google Search |
| Max affordable CPL | job value x close rate x gross margin x acquisition share | HEURISTIC planning tool |

Identity: CPA = CPM / (1000 x CTR x CVR). Use it to find which term moved.

## Evidence thresholds (HEURISTIC defaults; encoded in `godmode/evidence.py`)

| Question | Minimum before a verdict |
|---|---|
| Is this ad/keyword failing? | spend ≥ 2-3x target CPA with 0 conversions, out of learning, tracking verified |
| Is CPA different between two entities? | ≥ 10 conversions each (directional), ≥ 30 (confident) |
| Is CTR/CVR different? | two-proportion z: \|z\| ≥ 1.96 MODERATE, ≥ 2.58 HIGH |
| Is a trend real? | ≥ 7 days; compare equal windows; exclude conversion-lag days |
| Scale budget? | guarded-auto: ≥ min_spend, ≥ min_conversions, ≥ MODERATE confidence |

Rough precision: n conversions give about ±1/√n relative error on CPA (12 conv ≈ ±30%, 25 ≈ ±20%, 100 ≈ ±10%).

## Data-quality checklist (before strong recommendations)

sample size · timeframe · tracking health · attribution quality · conversion lag · seasonality · recent major changes · learning status. If any fails, downgrade confidence and say which.
