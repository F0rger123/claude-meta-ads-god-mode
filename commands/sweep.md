---
description: "Review every client at once: rank who is on track, overspending, broken or ready to scale; write the portfolio dashboard"
argument-hint: "[daily|weekly|monthly] [client,client]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/skills/ads-portfolio/SKILL.md`.
2. Run `${CLAUDE_PLUGIN_ROOT}/workflows/portfolio-sweep.md` in the mode given (default `weekly`), for all clients or the ones named.
3. Read-only. End with the portfolio table, RED clients first, then per-client what worked / what didn't / fix next, and the dashboard path.

If the arguments include `unattended` (scheduled runs from a scheduler that can't set environment variables), run `adsgm unattended on --hours 3` before anything else and `adsgm unattended off` at the very end. Don't ask questions in that mode; write the report.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`.
