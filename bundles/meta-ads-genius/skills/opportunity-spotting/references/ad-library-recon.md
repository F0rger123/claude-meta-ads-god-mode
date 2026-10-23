# Meta Ad Library Recon Protocol

The Ad Library (https://www.facebook.com/ads/library) shows every currently-running ad for any Page, free, no login. It is the single best competitive-intelligence source for Meta because it shows what advertisers *pay to keep running* — revealed preference, not marketing-blog claims.

## Setup
- Filter: country (target market) · "All ads" · platform as relevant.
- Search by competitor Page name; also search category keywords to discover competitors you didn't know (e.g., the product category + "software").
- Note: the public API only covers political/issue ads — for commercial ads, work the UI (browser tools) and record findings manually. EU trick: switching the country filter to an EU member state exposes reach ranges and demographic breakdowns under DSA transparency rules — useful for gauging competitor scale.

## Per-competitor sweep (record per advertiser)
| Field | What to capture | Signal |
|---|---|---|
| Ad volume | # of active ads | Investment level; sudden jumps = new push or fundraise |
| Longevity | Start dates (shown per ad) | **Ads live 3+ months ≈ profitable** — study these hardest |
| Angles | The argument each ad makes (map to buyer situations) | Their proven demand themes |
| Offers | What they ask for (demo, trial, report, calculator, discount) | What their funnel converts on |
| Formats | Static/video/carousel/UGC mix; aspect ratios | Production strategy |
| Hooks | First line / first 3 seconds, verbatim | The parts that survive their testing |
| Landing pages | Where ads click through | Funnel design, message match |
| Variations | Near-duplicates of one concept | Their iteration engine (many variants of one ad = it's a winner) |

## Synthesis: the angle map
Build a matrix: rows = buyer situations/angles (yours + all found), columns = competitors + you. Mark who runs what.
- **Crowded cells**: proven demand; enter only with a differentiated execution.
- **Empty rows a real buyer situation occupies**: white space — the highest-value output of the sweep.
- **Their long-runners you lack an answer to**: defensive test candidates.
- **Their conspicuous absences** (formats they never use, segments they never speak to): either they tested and failed, or they haven't tried — treat as a cheap test, not a sure thing.

## Rules
- Copy angles and structures of argument, never creative executions.
- Don't imitate advertisers 10× your size — their economics (LTV, brand baseline, retargeting pools) aren't yours.
- Date-stamp every sweep; re-run quarterly and diff (what died, what's new, what scaled) — the *changes* are the intelligence.
- Log findings with screenshots/links so briefs cite evidence, not memory.
