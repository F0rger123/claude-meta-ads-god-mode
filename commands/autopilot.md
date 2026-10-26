---
description: "Autopilot for a client: switch on/off, check status, or run it now - pauses losers, fixes and relaunches tired ads within approved budgets, adds small Google negative lists"
argument-hint: "<client> [on|off|status|run] [--cap <daily max>]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/workflows/autopilot.md`.
2. `on`: explain what autopilot does and never does, ask for the daily spend cap and which fixes to enable, then `adsgm autopilot on --client <slug> --cap <amount>`. `off`: `adsgm autopilot off --client <slug>`. `status`: `adsgm autopilot status --client <slug>`.
3. `all run`: every client with autopilot on (`adsgm autopilot status` per client), one at a time with `adsgm use`. `run` (or no action): run the "Each run" steps. Only `auto` verdicts are executed; everything else is listed as waiting for approval.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`.
