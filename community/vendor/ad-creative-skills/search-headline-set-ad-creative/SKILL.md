---
name: search-headline-set-ad-creative
description: Builds a full Responsive Search Ad asset set for one Google Ads ad group, decides pinning, and names which headlines are duplicates wearing different words. Use when the deliverable is search text tied to keyword intent and a landing page. Not for Meta or LinkedIn feed copy, which is paid-social-primary-text-ad-creative.
---

# Search Headline Set

Shared quality bar: `../references/output-standard.md`. All numbers cited here live in `../references/thresholds.md`.
This skill produces search assets for one ad group at a time, because pinning
and duplication are only judgeable against a single keyword set.

## Use this skill when

A Google Ads ad group needs its Responsive Search Ad headlines and descriptions
written or rebuilt, or an existing asset set has weak Ad Strength, or nobody
can say which headlines are pinned and why. Also use it when an ad group has
fewer live headlines than `coverage.rsa_headline_floor`. Not for Meta or
LinkedIn feed copy, which is paid-social-primary-text-ad-creative. Not for the
opening seconds of a video, which is video-hook-lines-ad-creative. Not for
rewriting one proven angle across funnel stages, which is
funnel-stage-variants-ad-creative.

## Required input

- Ad group name and its keyword list, with match types.
- The destination URL, and the text of its first heading and first paragraph.
- The offer as it exists today: price, trial, guarantee, delivery promise.
- Any claim the advertiser wants used, with its source.
- Legal or brand constraints: forbidden words, mandatory disclaimers.
- Existing asset set and Ad Strength, if one is live.

## Analysis workflow

1. Group the keywords by the job the searcher is doing, not by match type.
   Each job becomes a claim family. A family with no keyword behind it does not
   get a headline.
2. Read the destination heading and first paragraph and record the claim, the
   offer and the call to action present there. Apply `match.above_fold_rule`
   and `match.promise_pairs` before writing a single line.
3. Draft headlines one claim family at a time, each within
   `limits.rsa_headline_chars`. Write past the count you need, then cut.
4. Run the duplication pass. Two headlines sharing their main noun and verb are
   one headline, per the note on `coverage.rsa_headline_floor`. Merge them and
   record the merge, so the set is not padded to look full.
5. Count distinct claims against `coverage.rsa_headline_floor` and total slots
   against `limits.rsa_headline_slots`. Report the gap as a number of missing
   claim families, not as a request for more words.
6. Write descriptions within `limits.rsa_description_chars`, each carrying one
   proof or one mechanism, never a restatement of a headline.
7. Decide pinning. Pin only what must appear on every impression: a legal line,
   a brand requirement, a price the page contradicts if absent. Everything else
   stays unpinned so the system can assemble.
8. Apply `claims.evidence_rule` and `claims.superlative_rule` to every line.
   Mark unsourced factual lines `[claim: needs source]`. Check
   `claims.restricted_topics` and route those to the platform policy page.

## Decision rules

- Distinct claims below `coverage.rsa_headline_floor` and no further evidenced
  claim available: report the shortfall, do not invent a family to fill it.
- Pins in one position above `limits.rsa_pin_ceiling`: `rewrite`. Heavy pinning
  removes the combinations the format exists to test.
- A headline whose claim is absent from the destination above the fold:
  `investigate` the landing page, and hold the headline out of the shipped set.
- Two headlines inside one claim family with no wording difference that changes
  the promise: keep one, label the other a duplicate.
- Any superlative without a cited comparison: cut it, and say what evidence
  would let it back in.
- Any line this skill produced that carries `[claim: needs source]` is
  `approval_needed`, whatever else its verdict says, and the marker is never
  stripped to make the set look finished. A marked line is not shippable copy:
  it waits for the named source, or it is rewritten without the claim. A marked headline is reported outside the
  shipped set, not inside it with a footnote.

## Output format

No verdict line. Return a headline table with columns: headline, character
count, claim family, pinned position or unpinned, evidence label, decision
label. Then a description table with the same evidence and decision columns.
Then a short duplication list naming each merged pair. Then
`What this could not see`, `Missing data`, `Approval gates`.

This skill writes assets rather than reading a test or a time series, so it
issues no `high` confidence label and does not borrow the comparison family's
conditions, which belong to a test nobody has run on this copy yet. Where a row
carries a confidence label it is about the evidence behind a claim and never
about the writing: a line whose source was produced and checked is `ship`, an
unsourced one is `approval_needed`. `test.min_runtime` and `test.volume_floor`
start to apply the day the set goes live, not while it is being written.

## Practical example

Illustrative and fictional. Advertiser "Bramble PM", ad group "project
management software for agencies", 14 keywords. The advertiser supplies 11 draft
headlines, asks for 15, and asks for a claim that the tool has the fastest
onboarding in the category.

Duplication pass: "Set Up In Minutes", "Fast Setup For Teams" and "Quick
Onboarding" share their noun and verb, so those three merge into one claim
family. Three further pairs merge the same way. Eleven drafts minus two from the
trio and one from each pair leaves 6 distinct claims, below
`coverage.rsa_headline_floor`.
Two evidenced families come off the destination page, taking the set to 8. The
remaining slots up to `limits.rsa_headline_slots` are left empty rather than
padded.

Shipped headlines, with character counts:

- Agency Project Management (25)
- Built For Agency Teams (22)
- Onboard A Client In A Day (25)
- See Every Project Deadline (26)
- Stop Chasing Timesheets (23)
- One Place For Client Work (25)
- Try Bramble PM Free (19)
- Start Free, No Card Needed (26)

Description 1 (89): "Brief, plan and invoice client work in one place, then give
the client a live view of it."

Declined, and reported outside the shipped set:

- "Fastest Onboarding In The Category" (34). Refused under
  `claims.superlative_rule`: no comparison was supplied, so it is not written in
  any form, including a softened "onboarding that is hard to beat". It also runs
  past `limits.rsa_headline_chars`, which is the smaller of the two problems.
  Unlocked by a named benchmark against named competitors.
- "Cuts Admin By 6 Hours A Week" (28) `[claim: needs source]`. The 6 hour figure
  arrived in conversation only, so the line is `approval_needed` and is not one
  of the 8. It joins them the day somebody names the dashboard behind it.

Pinning: one legal line pinned to description 2, nothing else pinned.

## Guardrails

- Never pad an asset set with reworded duplicates to reach a slot count.
- Never write a claim the destination page does not carry above the fold.
- Never invent a price, a customer count, a rating or a comparison.
- Never soften an unevidenced claim into a vaguer one to get it past review.
- Do not upload, edit or pause anything in the account. Recommend only.
- Report every line declined and the reason, including lines the advertiser
  asked for by name.
