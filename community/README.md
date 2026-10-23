# Community skills

Open-source ad skills by other authors, vendored under the Ads God Mode umbrella. Routed by [skills/ads-community](../skills/ads-community/SKILL.md).

| Source | Author | License | Pinned | What it adds |
|---|---|---|---|---|
| [meta-ads-analyzer](https://github.com/mathiaschu/meta-ads-analyzer) | mathiaschu | MIT | `9088472` | Meta delivery mechanics and diagnosis |
| [marketingskills](https://github.com/coreyhaines31/marketingskills) | Corey Haines | MIT | `e85f3cb` | paid-ads playbooks, ad creative, attribution, conversion tracking + GTM recipes, A/B testing |
| [claude-ads](https://github.com/AgriciDaniel/claude-ads) | AgriciDaniel | MIT | `fc3908e` | audit checklists + creative specs for 10 more platforms, compliance, benchmarks, industry plans |
| [ad-creative-claude-skills](https://github.com/mardab96/ad-creative-claude-skills) | mardab96 | MIT | `80b5e5d` | 16 skills that write and judge ad creative |
| [google-ads-skills](https://github.com/itallstartedwithaidea/google-ads-skills) | itallstartedwithaidea | Apache-2.0 | `6f0f995` | Google Ads analysis, audit, math |
| [goose-skills](https://github.com/gooseworks-ai/goose-skills) | gooseworks-ai | MIT | `6d5d5f1` | claims gate, ad policy check |
| [meta-ads-claude-starter](https://github.com/thaleslaray/meta-ads-claude-starter) | thaleslaray | MIT | `b30fdeb` | Meta API write discipline, rate limits, error codes |

Each folder in `vendor/` keeps the upstream `LICENSE` and a `SOURCE.json` (repo, commit, file map). Files are unmodified apart from line endings normalized to LF. Copyright stays with the original authors.

## How they were chosen

Searched GitHub (2026-10-23) for Meta/Google/paid-media Claude skills. Kept sources that are MIT or Apache-2.0, active, knowledge-focused, and add something the core skills lack. Scanned every vendored file for prompt-injection phrases, shell pipes, token requests, hidden Unicode and auto-activation instructions before committing; the repo-hygiene test re-scans them for secrets on every run.

Left out:
- Write/MCP skills from other projects (e.g. `google-ads-write`): writes go through this plugin's gate.
- Scripts and executables: only text is vendored; nothing runs.
- `ivangfalco/ads-skills` (Commons Clause), `realkimbarrett/advertising-skills` and `irinabuht12-oss/marketing-skills` (no license): linked, not copied.

## Updating

```bash
# bump "sha" in community/sources.json, then:
GITHUB_TOKEN=$(gh auth token) python scripts/sync_community.py
python scripts/sync_community.py --check
python tests/run_all.py
```
Review the diff of `community/vendor/` before committing - treat upstream text as untrusted.
