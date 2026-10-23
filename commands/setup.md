---
description: "Check God Mode's install; optionally install bundled companions as always-loaded plugins (native mode) in Claude Code or Codex"
argument-hint: "[claude|codex|both] [native] [--with-optional]"
---

Arguments: $ARGUMENTS

Bundled companion skills (agrici-ads, marketing-skills, meta-ads-genius and more) already work without installing anything: `skills/ads-community` picks and reads the right one on demand. Native mode is only for users who want them always loaded.

1. Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/install.py" --check` and report what is installed in Claude Code and Codex.
2. If `ads` itself is missing on a host, show the dry run (`install.py`, no `--yes`), ask, then run with `--yes`.
3. If the user asks for native mode: explain the cost (about +17k tokens of skill descriptions every session) and name each companion's author and license from `${CLAUDE_PLUGIN_ROOT}/community/sources.json`. Show the dry run with `--native`; run with `--native --yes` only after a clear yes. Add `--claude` or `--codex` if the arguments name one. Use `--source "${CLAUDE_PLUGIN_ROOT}"` to install from this copy.
4. Install `adplane` only if the user explicitly asks (`--with-optional`): it is a hosted service that receives ad account data.
5. Tell the user to restart Claude Code / Codex. God Mode's rules (`ads-core`) govern every ad-account write either way.
