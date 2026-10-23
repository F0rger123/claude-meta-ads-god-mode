# Workflow: campaign launch (paused-first)

Trigger: `/ads:launch`, "Build a Meta campaign for D-Hauss Remodeling targeting homeowners around York, PA for kitchen remodel leads at $X/day." Platform detail: [Meta](../skills/meta-ads/workflows/launch-campaign.md) · [Google](../skills/google-ads/workflows/launch-search-campaign.md).

| # | Step | Writes? |
|---|---|---|
| 1 | Load client context (`adsgm use`, profile) | no |
| 2 | Inspect existing account and campaigns (overlap, naming, budgets) | no |
| 3 | Verify tracking (event/conversion action fires, deduped, right dataset/customer) | no |
| 4 | Understand the offer and landing page | no |
| 5 | Propose strategy ([campaign-planning.md](campaign-planning.md)); get OK on the brief | no |
| 6 | Build the hierarchy (campaign -> ad set/ad group -> ads) | create PAUSED |
| 7 | Generate targeting (geo radius inside limits, audience, exclusions) | (in step 6) |
| 8 | Generate ad copy within brand voice and prohibited claims | (in step 6) |
| 9 | Define creative needs as briefs ([templates/creative-brief.md](../templates/creative-brief.md)) | no |
| 10 | Select budget and bidding; explain expected volume and learning | (in step 6) |
| 11 | Identify risks | no |
| 12 | Create everything PAUSED, passing the account id explicitly | create PAUSED |
| 13 | Read back and show exactly what was created (ids, names, settings, previews) | no |
| 14 | Stop. Wait for explicit approval before activation | - |

Activation (separate turn, user said go): `adsgm plan activate --platform <p> --account <id> --entity <campaign id> --reason "user approved launch on <date>"` -> show summary -> activate (Meta `ads_activate_entity`; Google writer `set_status ENABLED`) -> read back status -> log launch date for the read date in [templates/launch-plan.md](../templates/launch-plan.md).

If the client is in `read_only`: produce the full plan and copy as a document only. In `draft`: create paused; activation is blocked by policy - tell the user to switch mode or activate in Ads Manager themselves.
