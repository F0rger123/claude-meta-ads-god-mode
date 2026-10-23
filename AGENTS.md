# AGENTS.md

Instructions for any AI agent (Claude Code, Codex, Cursor, Gemini CLI, etc.) using or modifying this repository.

## Using it to manage ads

1. Read `skills/ads-core/SKILL.md` first; it defines client resolution, connector routing and the write rules. Then load only the platform skill (`skills/meta-ads` or `skills/google-ads`) and the one task skill/workflow the request needs.
2. All safety state goes through `python adsgm.py ...` (JSON output). Before any write: `adsgm use <client>`, verify CLIENT / PLATFORM / ACCOUNT / ENTITY from fresh reads, `adsgm plan ...`, show the summary, then act.
3. Create campaigns, ad sets, ads PAUSED. Activation, deletes, tracking changes, geo expansion and out-of-policy budget changes require explicit human approval. Billing and admin changes are never made by an agent.
4. Hosts without Claude Code hooks do not get the PreToolUse gate automatically. Call `python hooks/write_gate.py pre` with the hook JSON shape (`tool_name`, `tool_input`, `permission_mode`) before every ad-platform write and obey its decision, or do not enable write-capable connectors.
5. Never print or request credentials. Never mix clients.
6. Companion plugins (`agrici-ads`, `marketing-skills`, `meta-ads-genius`) ship in `bundles/`. Codex: if they are not installed, offer the user `python scripts/install.py --codex` (dry run), then `--yes` after their OK. The Codex marketplace is `.agents/plugins/marketplace.json`. Use companions only under the rules in `skills/ads-core/SKILL.md` ("Bundled companion plugins"): God Mode rules win, and every write goes through `adsgm plan` and the gate.

## Modifying it

- `python tests/run_all.py` must pass (stdlib only, no network).
- No secrets or real client data in commits.
- Safety logic fails closed; every rule change needs a test.
- Keep knowledge labeled and sourced; no guaranteed-results claims.
