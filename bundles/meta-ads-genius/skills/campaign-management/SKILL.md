---
name: campaign-management
description: Plan, structure, and launch Meta Ads campaigns — account architecture (CBO/ABO, testing vs scaling), audience strategy and lookalikes, conversion tracking setup (pixel/CAPI/EMQ/Conversion Leads), lead forms, creative briefs, budgets, and launch checklists. Use when the user wants to launch or restructure campaigns, design a test, set up tracking, brief creatives, or plan budgets for a new initiative.
---

# Meta Ads Campaign Management

Campaigns succeed at design time. Structure, signal quality, and creative diversity decide more than any post-launch optimization — and every launch ships with its success criteria, kill criteria, and check dates already written.

## Design order (always this sequence)
1. **Goal & event** — the business outcome, and the conversion event that maps to it (deep enough to mean money, frequent enough to train on: ~50 events/week feasible at the planned budget; else pick one funnel step up).
2. **Economics** — TCPL/target CPA and budget-for-learning math: `daily budget ≥ (target × 50) ÷ 7` per ad set, or knowingly accept learning-limited.
3. **Audience** — per the data hierarchy in `references/structure-audiences.md`; exclusions listed before launch.
4. **Structure** — per the phase model below; naming + UTMs per workspace `_config/account.md` if present.
5. **Creative** — 3–6 genuinely distinct concepts per ad set, briefed per `references/creative-playbook.md`.
6. **Tracking verification** — per `references/tracking-signals.md`; nothing launches on an unverified pixel.
7. **Launch checklist** — below; everything created **paused**, activated only after the checklist passes and the user approves (see ad-optimization's `safety-governance.md` for execution rules).

## Account phase model
| Phase | When | Shape |
|---|---|---|
| **Validate** | New account/audience/offer | ABO, one ad set per audience source, identical ads across them, equal budgets, 2–4 weeks; judge in CRM, not Ads Manager |
| **Scale** | Validated audiences, steady volume | Two CBO campaigns: Scaling (~80%, graduated winners only) + Testing (~20%, protected budget) |
| **Automate** | ≥50 conversions/week sustained | Advantage+ variants; audiences become suggestions — don't use for strict ABM |

Build order for a new account: **Remarketing first** (cheapest wins), then Prospecting, then Acceleration (open-pipeline audiences). 1–3 campaigns per goal — proliferation fragments learning.

## Core structural rules
- CBO for consolidated scale; ABO only for controlled validation and tests.
- Ad sets ≥ learning-viable budget; consolidate rather than slice. 3–6 creatives per ad set (Advantage+ sales: up to 10).
- Exclude converters/customers from prospecting; exclude each prospecting audience from the others when overlap >20%.
- Bid strategy default: highest volume (lowest cost). Cost-per-result goal only with history, set at 1.2–1.5× realistic target — set below market, it simply won't spend.
- Special Ad Categories (housing/employment/credit/politics): declare before creation; expect targeting restrictions.

## Launch checklist (gate — all boxes before activation)
- [ ] Conversion event verified firing in Events Manager (test event + live check; dedup if CAPI)
- [ ] Links resolve; UTMs on every ad per convention
- [ ] Naming per convention; campaign in the right phase bucket (testing vs scaling)
- [ ] Budget-for-learning math shown, or learning-limited accepted in writing
- [ ] Audience exclusions applied; overlap checked against running campaigns
- [ ] Creative diversity: ≥3 distinct concepts, cluster-risk sanity check (see ad-analysis audit checklist rubric)
- [ ] Success criteria, kill criteria, and check dates written into the launch doc
- [ ] Everything created paused; activation approved by the user

## Deliverable templates
- **Campaign plan**: goal, event, economics, structure diagram (campaign→ad sets→ads), budgets, audiences + exclusions, phase, risks.
- **Creative brief**: per `references/creative-playbook.md` — concept table with hooks written out verbatim, formats, visual direction; concrete enough for a cold designer.
- **Launch doc**: the checklist above, filled, plus success/kill criteria and check dates. In this workspace: `campaigns/output/YYYY-MM-DD_launch_<slug>.md`.

## References
- `references/structure-audiences.md` — audience data hierarchy, lookalike construction, validation protocol, ABM patterns, lead-form friction design.
- `references/tracking-signals.md` — pixel + CAPI + dedup + EMQ, CRM feedback loops (Conversion Leads), UTM discipline. **Signal quality is the highest-leverage setup work.**
- `references/creative-playbook.md` — concept development from buyer situations, hook craft, formats, production ratios, copy formula, anti-slop rules.
