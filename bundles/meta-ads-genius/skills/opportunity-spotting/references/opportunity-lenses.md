# Opportunity Lenses & Brief Template

## Lens checklists

### Account mining
- [ ] Pull daily-grain insights (14–28d) at ad set + ad level; segment by placement, geo, age/gender where relevant.
- [ ] Rank segments by cost-per-result vs. account average; shortlist those beating it with <15% spend share.
- [ ] For each shortlisted segment, check the marginal curve (daily cost trend as spend grows). Flat/falling → headroom; rising → already harvested (breakdown effect — don't chase).
- [ ] Diff live creative against the buyer-situations list → uncovered situations.
- [ ] List never-tested rungs: lookalike tiers, seed sources, formats, placements, geos.

### Competitor recon
Run `ad-library-recon.md`. Output the angle map + a top-3 white-space list.

### Timing
- [ ] Seasonal calendar for the vertical (from `_config/account.md` or research) mapped against auction seasonality (Q1 cheap, Q4 dear).
- [ ] Upcoming platform changes/format launches worth an early-adopter test.
- [ ] Launch-lead-time check: campaigns need 2–3 weeks of learning before the demand moment.

### Expansion
- [ ] Nearest-rung-first ladder: LAL tier → new seed → adjacent segment → new geo.
- [ ] For each rung: is there evidence the offer resonates there (closed deals, inbound, competitor presence), or is this pure inference? Grade accordingly.

### Offer
- [ ] Current offer vs. traffic temperature table — is cold traffic being asked for a hot-traffic commitment?
- [ ] One lower-friction offer candidate (calculator/report/assessment) and one higher-intent variant defined.
- [ ] If many creative tests plateaued at bad quality: the offer is the suspect, not the ads.

## Sizing method
1. **Audience size**: Meta audience estimates for the targeting, or list size × expected match rate (~30–60% for personal-email lists) — as a range.
2. **Expected cost per result**: nearest analogous segment in the account (best), competitor-implied (medium), vertical benchmark (weakest — label it).
3. **Budget to significance**: 3 × target cost per concept tested, × number of concepts.
4. **Ceiling**: audience size ÷ effective frequency cap → impression ceiling → spend ceiling at expected CPM. Small ceilings are fine for acceleration plays, disqualifying for scaling plays — say which this is.

## Opportunity brief template
```markdown
# OPP: <name>  (<date>)
**Hypothesis**: We believe <audience/angle/offer/timing move> will achieve ≤ <target> per <result>
because <core evidence>. We'll know within <days> / $<budget>.

**Evidence** (graded)
| Evidence | Source | Grade |
|---|---|---|
| <observation> | <file/link/screenshot> | account data / competitor behavior / market inference |

**Sizing**: audience <range> · expected cost <range> (basis: <analog/benchmark>) · ceiling <spend/mo>
**Test design**: audience <…> · creative <n concepts, from situations X/Y> · budget $<3×target×concepts> · duration <weeks> · structure <testing campaign / ABO validation>
**Success criteria**: <metric ≤ threshold with n ≥ floor>   **Kill criteria**: <spend/date trigger>
**Displaces/supplements**: <what saturating spend this redirects>
**Recommendation**: GO / NO-GO / GATHER (<what's missing>)
```
