---
description: "Research a client's niche: sourced benchmarks (CPL, conversion rate, CTR), what converts, offers, hooks, competitors, seasonality - saved as a reusable niche playbook with launch recommendations"
argument-hint: "<client or niche>"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/workflows/niche-research.md`.
2. Reuse a fresh playbook (`adsgm niche show <niche>`) and fill gaps; otherwise research, label every fact with source and date, and `adsgm niche save --file <playbook.json>`.
3. End with 3-5 recommendations for the client, each naming its evidence, plus `adsgm learn summary --niche <niche>` if other clients share the niche.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`.
