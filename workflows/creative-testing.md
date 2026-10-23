# Workflow: creative testing

Trigger: `/ads:creative`, "test new ads", "which creative is winning". Skill: [ads-creative-analysis](../skills/ads-creative-analysis/SKILL.md).

1. **Analyze current creative** (hooks, retention, offer/CTA, format, fatigue, fit).
2. **Hypothesis** - one sentence: "A founder-on-site UGC hook will raise hook rate vs the polished showroom video, because local homeowners trust the owner." 
3. **Design** - control vs variant(s); **one variable** (hook OR format OR offer OR audience); same ad set, same window, same budget logic. If you must change two things, call it a new concept, not a test.
4. **Size** - each variant needs ≥ 2x target CPA spend (HEURISTIC floor) or ~100+ link clicks for CTR reads; estimate days needed at current budget and say it.
5. **Brief** - [templates/creative-brief.md](../templates/creative-brief.md) per variant -> the user's production workflow.
6. **Log** - add to the experiment log ([templates/experiment-log.json](../templates/experiment-log.json)): hypothesis, control, variable, creative, audience, offer, start date.
7. **Launch PAUSED -> activate with plan/approval** (`creative_swap` may be guarded-auto).
8. **Read** at the planned date: spend, conversions, CPA, CTR, hook/hold; `evidence.compare_rates` / `adsgm quality`; confidence; conclusion; next action. Record it.
9. For formal tests use Meta A/B tests (`ads_experiment_abtest_create_test`, experiment action, ticket) when budget allows a clean split.

Guard: never run more than one test per ad set at a time; never read a test while the ad set is in learning from an unrelated edit.
