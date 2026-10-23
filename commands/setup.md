---
description: "Install or repair the bundled companion plugins (agrici-ads, marketing-skills, meta-ads-genius) for Claude Code and Codex"
argument-hint: "[claude|codex|both] [--with-optional]"
---

Arguments: $ARGUMENTS

1. Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/install.py" --check` and show which of `ads`, `agrici-ads`, `marketing-skills`, `meta-ads-genius` are installed in Claude Code and Codex.
2. If something is missing, run the same script **without** `--yes` (dry run) and show the user the exact commands. Name each plugin's author and license from `${CLAUDE_PLUGIN_ROOT}/community/sources.json`.
3. Ask the user to confirm. Only after a clear yes, run it again with `--yes` (add `--claude` or `--codex` if the arguments name one). Use `--source "${CLAUDE_PLUGIN_ROOT}"` to install from this installed copy.
4. Install `adplane` only if the user explicitly asks (`--with-optional`): it is a hosted service that receives ad account data.
5. Tell the user to restart Claude Code / Codex, then summarize which companion skills are now available and that God Mode's rules (`ads-core`) still govern every ad-account write.
