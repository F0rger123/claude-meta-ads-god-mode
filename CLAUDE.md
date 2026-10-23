# CLAUDE.md - working on this repository

This repo is a Claude Code plugin (`ads`) that operates real ad accounts. Two audiences use these instructions: Claude **running the plugin** (start at `skills/ads-core/SKILL.md`) and Claude **developing the plugin** (this file).

## Developing

- Layout: `skills/` (SKILL.md + references/workflows), `workflows/`, `references/`, `templates/`, `commands/` (slash commands `/ads:*`), `hooks/` (write gate), `godmode/` (stdlib safety core + `adsgm` CLI), `connectors/` (adapters, registry, Google writer), `bundles/` (bundled companion plugins) and `community/` (vendored third-party skills) - never edit either by hand; bump the pin in `community/sources.json` and run `scripts/sync_community.py` then `scripts/build_catalog.py`. Routing rules: `community/router_rules.json` (every pick must exist in the catalog). `.codex-plugin/` + `.agents/plugins/` make the repo a Codex plugin marketplace. `tests/`.
- Run `python tests/run_all.py` after every change. All suites must pass; they need no network.
- Never add credentials, real account ids, client names with real data, or anything from `~/.ads-godmode/` to the repo.
- Safety code fails closed. New tool -> registry rule + test. Do not widen `ALWAYS_BLOCKED`/`ALWAYS_APPROVAL` exceptions without a test and a reason.
- Keep SKILL.md files lean (progressive disclosure); depth goes in references.
- Label knowledge (PLATFORM FACT with source + date / BEST PRACTICE / HEURISTIC / EXPERIMENT / CLIENT-SPECIFIC RULE). Never promise ad results.
- Match the surrounding style: small modules, docstrings that explain why, JSON output from the CLI.

## Running (summary - the skill is authoritative)

Resolve the client -> `adsgm use` -> read -> plan (`adsgm plan`) -> show summary -> write -> read back. Create PAUSED. Spend only with approval.
