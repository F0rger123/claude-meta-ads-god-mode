---
description: "Set up daily/weekly/monthly unattended runs (read-only by default) using the host scheduler or the OS scheduler"
argument-hint: "[show|install|remove]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/workflows/scheduled-runs.md`.
2. Show `adsgm schedule plan` output (with `--os windows` on Windows) and explain the read-only default.
3. Create tasks only after the user says yes. Prefer the host app's scheduler tool if one is available; otherwise give or run the OS commands.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`.
