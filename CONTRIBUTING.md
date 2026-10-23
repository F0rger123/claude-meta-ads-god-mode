# Contributing

Thanks for helping. This project manages real ad spend, so the bar for safety changes is high.

## Ground rules

1. **No secrets, no client data.** Use fake ids (`act_000000000000001`, `0000000001`) in tests and examples.
2. **Safety changes need tests.** Anything touching `godmode/`, `hooks/`, `connectors/registry.json` or `connectors/*/writer.py` needs tests in the matching `tests/` suite (routing, isolation, gating, budget, approval).
3. **Fail closed.** New tools default to `unknown_write` (approval). Loosening a rule needs a written reason in the PR.
4. **Knowledge is labeled.** In skills and references, mark claims as PLATFORM FACT (with a source URL and date), BEST PRACTICE, HEURISTIC, EXPERIMENT or CLIENT-SPECIFIC RULE. No growth hacks presented as facts. No guaranteed-results language.
5. **Progressive disclosure.** Keep each `SKILL.md` short (under ~200 lines, hard test limit 500); put depth in `references/` and link to it.
6. **Original text only.** Do not paste text or code from other projects unless its license is MIT-compatible and attribution is added to [THIRD_PARTY.md](THIRD_PARTY.md).

## Development

```bash
python tests/run_all.py          # stdlib only, no network
python adsgm.py doctor
claude plugin validate .claude-plugin/plugin.json
```

Python 3.9+. The core has no dependencies; the Google writer needs `google-ads` only at runtime.

## Adding a connector

See [connectors/README.md](connectors/README.md#adding-a-connector).

## Pull requests

Describe what changed, which safety layer it touches, and how you tested it (including a mocked or sandbox run for anything that writes). Live-account testing must use Google Ads test accounts or a Meta sandbox/test ad account.
