---
description: "Plan a client's budget: daily vs monthly vs fixed flight, Meta/Google split, what it buys, whether to spend more or less - with the math"
argument-hint: "<client> [monthly or daily amount]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-budgeting/SKILL.md` ("Planning a budget").
2. Ask only for what is missing: monthly or daily amount, whether the month is a hard ceiling, target cost per lead (or job value + close rate + margin), platforms, Google cost per click if known.
3. Run `adsgm budget-plan --client <slug> ...`, show the `text` result, discuss it (squeeze more, monthly vs daily, one platform first), and `--save` the agreed plan with their OK.
4. Nothing changes in the ad accounts here; launches and budget changes go through `adsgm plan` and approval.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`.
