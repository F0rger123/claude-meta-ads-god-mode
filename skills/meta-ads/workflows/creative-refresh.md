# Meta creative refresh

1. **Detect** - for each active ad set (last 14 days vs prior 14): frequency, link CTR, CPM, CPA, top ad's share of spend and age. Apply the fatigue signature in [creative-fatigue.md](../references/creative-fatigue.md). Exclude ad sets in learning.
2. **Diagnose** - which part failed: hook (hook rate), body (hold rate), offer/CTA (CTR with good video metrics), or not creative at all (CVR drop = landing page/tracking).
3. **Brief** - one brief per new concept using [templates/creative-brief.md](../../../templates/creative-brief.md): hook, script/message, length, format, B-roll, CTA, caption, visual references, platform/placement, hypothesis. Change one variable versus the control. Hand the briefs to the user's content/video workflow.
4. **Log the test** - add it to the experiment log ([templates/experiment-log.json](../../../templates/experiment-log.json)) with control, variable, start date.
5. **Upload + create PAUSED** - when assets arrive: upload, `ads_create_creative`, `ads_create_ad` in the existing ad set (one batch - adding ads is a significant edit).
6. **Activate** - `adsgm plan creative_swap` (guarded-auto may allow it) or `adsgm plan activate`; approval as the verdict says.
7. **Read** - after ≥ 2x target CPA spend per new ad or 7 days, whichever is later, compare against the control at ad set level; classify HIGH / MODERATE / EXPERIMENT; update the log with result and next action.
