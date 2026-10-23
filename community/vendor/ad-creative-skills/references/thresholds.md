# Thresholds

Single home for every number used across this pack. Skills cite this file by
key instead of restating a value. If a skill needs a number that is not here,
add it here first, then cite it.

Every entry carries a unit and a tag:

- `[platform guidance]` - stated by Google, Meta or LinkedIn in their own
  documentation or interface.
- `[heuristic]` - a practitioner starting point, not a platform rule.

## Every threshold is ONE number, not a range

A range is not a threshold. "three to five variants" means two people applying
the same rule to the same account land two variants apart, both correctly, and
neither can defend the number to a client. So every entry states a single
default and, where the value genuinely depends on the account, the rule for
moving it.

**Use the default unless the recalibration rule fires.** When you move a value,
say in the output which one you moved, to what, and why. An unexplained
recalibration is worse than the default, because it reads as a fact.

## Denominators

Half of a threshold is the number; the other half is what it is measured
against. These seven decide the most verdicts in this pack and are fixed here
rather than left to the reader.

| Term | Means | Not |
|---|---|---|
| **creative** | one ad as the platform counts it: one ad ID with its own creative and its own delivery | an ad name, a concept, or a file. Two ads carrying the same image with different copy are two creatives |
| **angle** | the argument the ad makes for why to act, stated as a sentence | the format, the offer, or the visual. "Cheaper than an agency" is an angle; "carousel" is not |
| **impressions** | impressions on that creative, that placement, that date range | account impressions. A fatigue read on account impressions measures the account, not the ad |
| **frequency** | impressions divided by reach for the SAME window as the CTR you compare it to | lifetime frequency. Lifetime frequency only ever rises and will "prove" fatigue on any ad old enough |
| **CTR** | link clicks divided by impressions, stated as `link CTR` | all clicks divided by impressions. The all-clicks figure counts reactions and profile taps on paid social and moves for reasons that have nothing to do with the creative. Always name which one you used |
| **attribution setting** | the click and view window the export was pulled on, stated in the output every time | a default nobody checked. A variant read on 7-day click against one read on 1-day click is not a comparison, and the difference is invisible in the file. Never compare two numbers pulled on different settings |
| **conversions** | primary conversion actions only, as configured on the campaign | all reported conversions including secondary. Where a skill needs the real-money subset it says "purchases" or "qualified" and you must state which you used |

## Character and slot limits

| Key | Value | Tag | Notes |
|---|---|---|---|
| `limits.rsa_headline_chars` | **30 characters** | [platform guidance] | Google Responsive Search Ads headline limit. Counted including spaces. |
| `limits.rsa_description_chars` | **90 characters** | [platform guidance] | Google Responsive Search Ads description limit. |
| `limits.rsa_headline_slots` | **15 headlines, 4 descriptions** | [platform guidance] | Maximum an RSA accepts. Maximum is not a target; see `coverage.rsa_headline_floor`. |
| `limits.meta_primary_text_visible` | **125 characters** | [platform guidance] | Meta truncates primary text with "See more" around this point on most feed placements. The exact cut varies by device, so treat it as where the reader stops, not as a hard limit. |
| `limits.meta_headline_visible` | **40 characters** | [platform guidance] | Meta's own recommendation for headline length before truncation risk. |
| `limits.linkedin_intro_text_visible` | **150 characters** | [heuristic] | Where LinkedIn collapses Sponsored Content introductory text behind "see more" on a desktop feed. Listed as a heuristic rather than platform guidance because LinkedIn does not publish the cut and it moves by device and by surface. Verify against a live preview before treating it as a hard boundary. |
| `limits.linkedin_headline_target` | **70 characters** | [heuristic] | Working target for a LinkedIn Sponsored Content headline. The field accepts far more; this is the length that survives on a phone. |
| `limits.rsa_pin_ceiling` | **2 pinned assets per position** | [heuristic] | Above this, the ad has stopped being responsive at that position and Google has almost nothing left to assemble from. Pinning is a legal or brand instrument, not an optimisation one; every pin is a permutation removed. |
| `limits.hook_spoken_words` | **8 words** | [heuristic] | What fits comfortably in `limits.video_hook_seconds` at ordinary delivery. Count the words in the spoken line, not in the on-screen line, which can be shorter and simultaneous. |
| `limits.video_hook_seconds` | **3 seconds** | [heuristic] | The window a hook has to earn the rest of the view. Widely used, not published by any platform as a rule. |

## Coverage

| Key | Value | Tag | Notes |
|---|---|---|---|
| `coverage.rsa_headline_floor` | **8 distinct headlines** | [heuristic] | Below this an RSA has too little to assemble from and Ad Strength usually reflects it. Distinct means a different claim, not a reworded one; two headlines sharing their main noun and verb count as one. |
| `coverage.angles_per_ad_set` | **3 angles** | [heuristic] | Fewer than three live angles in one ad set and a losing week cannot tell you whether the angle failed or the execution did. Move to 2 only when the ad set is under `test.volume_floor`, because more variants on thin volume just splits it further. |
| `coverage.formats_per_angle` | **2 formats** | [heuristic] | One static and one video per angle. Below this, a format effect reads as an angle effect. |
| `coverage.ratio_set` | **2 aspect ratios: 4:5 and 9:16** | [heuristic] | Feed and story or reel surfaces each want their own frame. **1:1 is not on this list and was removed on 2026-08-30**: Meta feed serves 4:5 at full height, so a square costs production time and buys nothing a 4:5 does not already cover. Add 1:1 back only for a surface that genuinely needs it and say which. **Missing 9:16 does not remove the vertical placements.** With placement asset customisation off, which is the default, Meta transforms whatever you gave it: it crops, letterboxes or pads with a generated background, and you get delivered to Reels and Stories in a worse frame than you would have chosen. That is a different defect from not being served and it has a different fix, so a coverage gap here is reported as `rewrite`, never as `investigate` on delivery. Corrected 2026-08-30 after a practitioner review; the earlier wording said the placements were removed and was tagged as platform guidance, and both were wrong. |
| `coverage.angle_distinctness` | **two angles are the same angle when they share their main claim AND their reason** | [heuristic] | The test for collapsing an angle list. "Save time" and "stop wasting hours" share both and count as one. "Save time" and "cheaper than an agency" share neither and count as two. Applied before any angle is counted against `coverage.angles_per_ad_set`, because an inflated angle count is the most flattering error an account can make about itself. |
| `coverage.stale_spend_share` | **40% of ad set spend sitting on creatives older than 60 days** | [heuristic] | The supply signal. Measured on SPEND, not on the age of the newest asset, because an account shipping thirty creatives a month always has a young newest asset while most of its money can still be riding three files from the spring. This is a supply signal, not a fatigue verdict; fatigue lives under `fatigue.*`. Replaced `coverage.stale_library_days` on 2026-08-30: that key measured the newest creative in the ad set and therefore passed forever on exactly the accounts it was meant to catch. |
| `delivery.never_delivered_floor` | **under `early.min_exposure` in absolute terms** | [heuristic] | A creative the platform genuinely never gave a chance. Mark it `never_delivered`, exclude it from every ranking, cut list and brief input, and never report it as a performance finding. This is the only case where low spend carries no information. |
| `delivery.starved_flag` | **cleared `early.min_exposure` and still under 10% of ad set spend after 72 hours live** | [heuristic] | Different state, different verdict. Delivery on paid social is allocated by predicted performance, and that prediction is trained on the creative's own early response, so repeated non-allocation is the platform's read of the creative rather than an absence of one. Verdict `cut` at `low` confidence, and it goes ON the cut list rather than being excluded from it. Added 2026-08-30 after a high-volume review pointed out that a single floor marked twelve of fifteen live ads as unreadable and left the pack with nothing to say about most of a real library. Same trade as the `early.*` block: assume the same order of false negatives as `early.false_negative_rate` and log your cuts so you can replace the assumption with your own number. |
| `delivery.ranking_floor` | **10% of ad set spend in the window**, per creative | [heuristic] | The separate question of whether a creative belongs in a RANKING or a brief input. Below it the spend is too concentrated for a like-for-like comparison, whatever verdict `delivery.starved_flag` produced. Keep the two apart: one decides whether the creative gets a decision, the other decides whether it gets compared. |

## Fatigue

Fatigue is a claim about a specific creative over time. Every key below is read
on one creative, on one placement family, over a defined window.

| Key | Value | Tag | Notes |
|---|---|---|---|
| `fatigue.window` | **14 days**, compared against the previous 14 | [heuristic] | The comparison window for every fatigue key. Shorter windows read weekday effects as decay. Move to 7 days only when the creative clears `test.volume_floor` by 3x within 7 days, and say you moved it. |
| `fatigue.ctr_decline_flag` | **link CTR down 25% or more** across `fatigue.window` versus the previous window | [heuristic] | The primary fatigue signal. Percentage change of the rate, not of the click count; a click count falls when spend falls and that is not fatigue. |
| `fatigue.frequency_ceiling` | **3.0 impressions per person** within `fatigue.window` | [heuristic] | Windowed, never lifetime. A creative above the ceiling with stable CTR is not tired; it is being served to a small audience and the finding is the audience size, not the creative. |
| `fatigue.cpm_rise_flag` | **CPM up 20% or more** across `fatigue.window` | [heuristic] | Rising CPM alongside falling CTR is the auction responding, not the creative dying. Reported together with `fatigue.ctr_decline_flag` or not at all. |
| `fatigue.frequency_rise_flag` | **windowed frequency up 40% or more** versus the prior window | [heuristic] | The second signal for retargeting and any small audience, where `fatigue.frequency_ceiling` is crossed permanently and therefore discriminates nothing. A relative rise says the pool is closing now; a high absolute number says it was always small. |
| `fatigue.saturation_flag` | **new reach down 30% or more** across `fatigue.window` while spend holds within 20% | [heuristic] | The second signal for broad prospecting, where `fatigue.frequency_ceiling` is never crossed because the addressable pool is large. What burns out is the slice delivery keeps re-serving, not the whole audience, and that shows up as the creative reaching fewer new people for the same money rather than as a high frequency. Compute new reach as window reach minus the reach the creative already had; where the export cannot give it, say so and fall back to `fatigue.frequency_ceiling`. Added 2026-08-30. |
| `fatigue.verdict_rule` | **fatigue requires `fatigue.ctr_decline_flag` AND at least one of `fatigue.frequency_rise_flag`, `fatigue.saturation_flag` or `fatigue.frequency_ceiling`, all inside the same window and above `fatigue.volume_floor`** | [heuristic] | One signal alone is not fatigue. CTR falling with flat frequency and flat new reach points at the audience or the auction; frequency or new reach moving with flat CTR points at audience size. Three candidate second signals rather than one, because the absolute frequency ceiling discriminates in neither direction where the decision actually gets made: on broad prospecting nobody reaches it, on retargeting everybody sits above it permanently. The relative rise and the new-reach decline are the ones that move. **Where the second signal is `fatigue.frequency_ceiling` alone and frequency was already above it in the prior window, the verdict is void**, because a flag that was on before the decline started did not fire, it was already lit. Revised 2026-08-30 for these reasons. |
| `fatigue.volume_floor` | **20,000 impressions in each of the two windows** | [heuristic] | No fatigue signal may fire below this in either window. Without it a 25% link CTR swing on a few thousand impressions is a Tuesday, and the fatigue read was the only place in the pack with no volume condition at all. Added 2026-08-30 after a practitioner review named the inconsistency: test readouts were gated on volume and fatigue flags were not. |
| `fatigue.refresh_floor` | **7 days** since the last creative change on that ad | [heuristic] | Do not declare fatigue on a creative that has been live less than this. Delivery has not settled and you would be reading the learning period. |

## Testing

| Key | Value | Tag | Notes |
|---|---|---|---|
| `test.volume_floor` | **50 conversions per variant across the whole test**, whatever its length | [heuristic] | Stated as a single total on purpose, because a per-week rule is not applicable by anything that reads it: the export a readout runs on carries counts, not dates, so a rate-per-week floor cannot be evaluated and silently degrades into the total anyway. Loosely derived from Meta's 50 optimisation events per ad set per week, but applied per variant and as a test total, which is our choice and not Meta's statement, so the tag is heuristic. Below the floor, no creative verdict is reportable above `low` confidence. **Revised twice on 2026-08-30.** The first version was tagged platform guidance while admitting the per-variant application was ours. The second restated it per week, which no script and no skill ever implemented, so the file said 100 across a fortnight while every reader applied 50; an auditor found a 14-day test with 60 and 84 conversions per arm passing cleanly at a floor the file put at 100, and the self-test asserting the looser reading, which locked the discrepancy in. A threshold nothing can evaluate is worse than a looser one, because it makes the document and the behaviour disagree while both look right. |
| `test.click_floor` | **300 link clicks per variant** | [heuristic] | The fallback floor when the test is being judged on CTR rather than conversions. Below it, a CTR difference under `test.material_gap` is inside normal weekly swing. |
| `test.material_gap` | **20% relative difference** between variants | [heuristic] | The BUSINESS relevance floor: a difference smaller than this is not worth acting on even when it is real. It is not, and never was, a test of whether the difference exists. Pair it with `test.statistical_gate`; either one alone produces a confident wrong answer, in opposite directions. |
| `test.statistical_gate` | **the observed difference must clear the minimum detectable difference at that variant's own sample size**, computed as a two-proportion comparison at 95% | [heuristic] | The readability test, added 2026-08-30 after two practitioner reviews found the same hole. Without it, a 20% relative lift on 50 conversions per arm is reported as a `ship` at `high` confidence when it is inside noise, and a real 6% difference on 5,000 conversions per arm is thrown away as a tie. `scripts/test_readout.py` computes it and prints the minimum detectable difference alongside the observed one, so the answer is never "trust the gate". |
| `test.impression_share_skew` | **no variant below 15% of the test's total impressions** | [heuristic] | Delivery on paid social does not divide impressions evenly, and early allocation is sticky: one variant routinely takes most of the first 48 hours and holds it. Be careful with the mechanism, because the wrong version of it was stated here until 2026-08-30. The platform DOES keep re-evaluating allocation, and a starved ad can pick delivery up later when the leader's response decays. What it does not do is even the arms out for your benefit. Below this share the variants ran against different people at different times, so the difference is confounded by allocation rather than merely noisy, and extra sample does not fix a confound. Voids the comparison outright. |
| `test.assignment_rule` | **variants co-existing in one ad set are not randomly assigned** | [heuristic] | Meta documents that delivery allocates by predicted performance rather than at random, and that part is platform guidance. The consequence drawn here is ours, so the row is tagged heuristic. Be precise about the consequence: the arms are not disjoint samples, they are non-randomly OVERLAPPING ones, because one person can be served several ads from the same ad set across a fortnight. Any readout on co-existing ads is capped at `medium` confidence by construction, whatever the volume. `high` requires a real split: the platform's own A/B test tool, or separate cells. Retagged and corrected 2026-08-30. |
| `test.creative_enhancements_rule` | **Advantage+ creative enhancements void `test.one_change_rule`** | [heuristic] | Text variation, image expansion, music and 3D animation change the asset per impression, so the served creative is not the one you uploaded. With any of them on you changed one element and the platform changed several more, per user. Meta documents that these features exist and what each does; that they void a one-changed-element read is our inference, so the tag is heuristic. **The rule is about the CHANGE, not the state.** An enhancement that was on for both windows is a constant; one switched on between them is a different asset, and it is the most likely manufactured cause of a CTR decline on a 2026 account, because these get enabled account-wide by default. Ask which were enabled and WHEN they changed before reading any creative result across two windows or across variants; if the answer is unknown, the read says so and stops at `low`. |
| `test.min_runtime` | **14 days** | [heuristic] | Minimum elapsed time before reading a creative test, matching `fatigue.window` so the two are never read on mismatched periods. State the window as dates, not as a duration. |
| `test.one_change_rule` | **one changed element per variant pair** | [heuristic] | Hook, image, offer or format: change one. A pair differing in two elements produces a result that cannot be applied to anything else. |
| `test.concurrent_variant_cap` | **4 variants per ad set that are being READ as a test** | [heuristic] | Scoped deliberately to the variants a readout will judge, not to how many ads may be live. Running fifteen creatives in one ad set is normal practice and this key does not forbid it; what it forbids is treating fifteen as fifteen test cells. The control surface for the rest is `delivery.ranking_floor`, which tells you which ones may be compared, and `delivery.starved_flag`, which gives the others a verdict of their own. Rewritten 2026-08-30: the earlier version capped live ads on the reasoning that the budget splits evenly across them, which is not how Meta allocates. |

## Funnel steps

| Key | Value | Tag | Notes |
|---|---|---|---|
| `funnel.click_session_loss_flag` | **20% on paid social, 10% on Google Ads with auto-tagging on** | [heuristic] | Two numbers because the normal loss differs by an order of magnitude and one number gives a false all-clear on Google and a false alarm on Meta. Some loss is always normal: people leave before the page paints and the two systems count different events. Above the flag the finding is almost never the creative, it is page speed, a redirect, a consent wall or broken measurement. Reported as `investigate`, never as a creative verdict. Split 2026-08-30. |

## Early signals

The pack's floors are built to stop confident wrong answers, and the cost of
that is silence on every creative that will never reach a readable sample,
which on a high-volume account is most of them. This block is the deliberate
exception: a cheap-decision layer that trades a stated error rate for
throughput. Everything here is capped at `low` confidence by definition and
none of it may be reported as a result.

| Key | Value | Tag | Notes |
|---|---|---|---|
| `early.min_exposure` | **1,000 impressions AND spend of at least 1x the target cost per acquisition** | [heuristic] | Nothing in this block may fire below both. The spend half matters more than the impression half: a creative that has not yet spent one target CPA has not had a chance to produce a conversion, so its zero is not information. |
| `early.hook_rate` | **3-second video plays divided by impressions, below 0.6x the ad set median** | [heuristic] | The opening is not stopping anyone. Only meaningful on video, and only against the ad set's own median, never against a published benchmark from another account. |
| `early.hold_rate` | **video plays at 50% divided by 3-second plays, below 0.6x the band median** | [heuristic] | The opening works and the rest does not. A creative failing hold while passing hook is a different rewrite from one failing hook, which is the whole reason to separate them. **Defined on the 50% play, not on ThruPlay.** ThruPlay is completion or fifteen seconds, whichever comes first, so on a twelve-second ad it means completion and on a forty-second ad it means fifteen seconds: two different questions wearing one column name. A median taken across an ad set holding both is meaningless and the cuts made from it are noise. The 50% play is length-relative by construction and comes from the same export. Corrected 2026-08-30. |
| `early.duration_band` | **under 15 seconds, 15 to 30 seconds, over 30 seconds** | [heuristic] | Every `early.*` median is computed WITHIN a band, never across an ad set holding several. Video length is a required input for any hold read; without it the read is `needs_data`. |
| `early.median_stability_floor` | **5 creatives in the band after the exposure and delivery steps** | [heuristic] | Below this the "median" is one middle number and it is driving real cut decisions. Under the floor, the hook and hold reads are `needs_data` and no cut fires on them. `early.cost_multiple` may still run, against the whole ad set rather than the band, and must say it did. |
| `early.cost_multiple` | **cost per outbound click at 2.5x the ad set median or worse** | [heuristic] | The platform-agnostic version, for static and for accounts without video metrics. |
| `early.false_negative_rate` | **assume roughly 1 in 5 creatives cut this way would have gone on to win** | [heuristic] | Stated rather than hidden, because that is the trade being made. This figure is a working assumption and not a measurement; an account that logs its own early cuts and their eventual outcomes should replace it with its own number, and the skill says so. |

## Money

The pack judges creative, and creative is judged on money. These two keep a
creative readout from being a report about rates.

| Key | Value | Tag | Notes |
|---|---|---|---|
| `money.relevance_floor` | **a difference must move cost per acquisition by 10% or more** to be worth a budget change | [heuristic] | The rate-side twin of `test.material_gap`. A creative can win on click-through rate and lose on cost per acquisition, and only one of those pays. Where cost per acquisition is not supplied, the readout says which decision it therefore cannot make rather than substituting the rate. |
| `money.budget_step_cap` | **20% of the current ad set budget per step**, no more than one step per `test.min_runtime` | [heuristic] | Larger steps on paid social destabilise delivery and make the next readout unreadable, which turns one confident decision into a fortnight of noise. This pack never moves a budget; it states the step it would recommend and hands it to a person. |

## Message match

| Key | Value | Tag | Notes |
|---|---|---|---|
| `match.promise_pairs` | **the ad's main claim, the offer and the call to action** | [heuristic] | The three elements that must appear on the destination. Two of three present is a partial match and is reported as a finding, not waved through. |
| `match.above_fold_rule` | **the ad's main claim appears in the destination's first heading or first paragraph** | [heuristic] | Present further down the page counts as absent for this check, because the reader who clicked is confirming a promise, not reading an article. |

## Teardown

| Key | Value | Tag | Notes |
|---|---|---|---|
| `teardown.observation_floor` | **30 days of observed continuous running** before a competitor ad's structure is worth decomposing | [heuristic] | Thirty days rather than any other number because it is roughly two full learning periods on paid social, so an ad still live at that point has survived at least one deliberate keep-or-kill review by whoever runs the account. That is the whole of the reasoning, and it is thin; if you have a better basis, move it and say so. Below this you are studying a test, not a decision somebody kept making. Read alongside `reporting.no_competitor_spend`: longevity is the only signal a public ad library gives, and it is weak, so do not spend effort decoding an ad that has not yet shown even that. |

## Claim safety

| Key | Value | Tag | Notes |
|---|---|---|---|
| `claims.testimonial_permission` | **written permission on file before a customer name, quote, logo or review runs** | [heuristic] | A distinct defect from an unsourced number: the claim can be entirely true and still cannot run. Always `approval_needed`, never `ship`, and the approval is the customer's, not the marketer's. |
| `claims.evidence_rule` | **every number, comparison and outcome claim names its source before the ad runs** | [heuristic] | Source means a document, a dashboard or a named customer, not "the team said". An unsourced number in an ad is a legal exposure and a retraction risk, and it is the single most common defect in copy handed over by an agency. |
| `claims.restricted_topics` | **health, finance, credit, employment, housing, dating, politics, alcohol, gambling** | [platform guidance] | Categories every major ad platform documents special requirements for. This list routes to "read the platform's policy page", never to a verdict from this pack. |
| `claims.superlative_rule` | **an unqualified superlative needs a cited comparison or it is cut** | [heuristic] | "Best", "fastest", "number one", "the only". Qualified and sourced is fine; bare is not. |

## Reporting limits

The things this pack genuinely cannot see. Skills cite these in
`What this could not see` rather than restating them.

| Key | Limit |
|---|---|
| `reporting.no_creative_level_placement_cost` | Placement breakdowns work normally, including on campaigns using Advantage+ placements. What is restricted is combining certain breakdowns with **Dynamic Creative and Advantage+ creative asset variations**, where the asset that served differs per impression. Corrected 2026-08-30: the earlier wording named Advantage+ placements as the blocker, which is wrong and would have sent people looking for a report they can in fact pull. |
| `reporting.conversion_lag_bias` | The current window is still filling in while the previous one has finished. On a 7-day click setting, a current-versus-prior conversion comparison is biased against the current window by construction, and the size of the bias depends on the account's own lag. Click and impression comparisons do not carry it. Any conversion-side period comparison either waits out the window or states the bias. |
| `reporting.no_view_through_in_ctr` | View-through and engaged-view credit does not appear in CTR, so a creative can carry the account while its CTR sits at the bottom of the ad set. Never rank creatives on CTR alone when the objective is conversions. |
| `reporting.no_causal_read_from_export` | An export shows what happened, never why. Every attribution of a change to a creative decision in this pack is an inference and is labelled `hypothesis`. |
| `reporting.no_competitor_spend` | Public ad libraries show that an ad ran and roughly for how long. They do not show spend, results, or whether it worked. A competitor ad running for months is evidence of a decision somebody kept making, nothing more. |
