---
name: ad-to-landing-page-match-ad-creative
description: Compares one ad against the page it clicks through to and reports whether the promise, the offer and the call to action are all delivered where the arriving reader can see them without scrolling. Use when spend is running to a page nobody has checked against its ad. Boundary against the nearest sibling: claim-safety-review judges the wording of the ad before launch and never opens the destination, while this skill judges the destination against an ad that already exists. Boundary against losing-ad-diagnosis, which owns the session to conversion step: clicks that convert poorly are that skill's trigger and not this one's, because locating which of the four funnel steps an ad loses people at needs impressions, clicks, sessions and conversions over one window, and this skill reads none of them. Run this one when that step has already been located and points at the destination, or when the page behind live spend has simply never been read next to its ad.
---

# Ad To Landing Page Match

Shared quality bar: `../references/output-standard.md`. All numbers cited here
live in `../references/thresholds.md`.
One ad, one destination, one verdict on whether the page keeps the ad's promise
in the reader's first screen.

## Use this skill when

An ad is live or about to be, and the page behind it has not been read next to
it. Typical triggers: a page was changed by somebody who never saw the ads
pointing at it, an offer changed in the ad and not on the page, or a funnel
diagnosis has already located the loss at the session to conversion step and
named this destination. It starts from a live URL.

Poor conversion on its own is not a trigger for this skill.
`losing-ad-diagnosis-ad-creative` owns the session to conversion step and
decides whether the loss is even on the page: it reads impressions, link
clicks, landing sessions and conversions for one ad over one window and locates
the first step that falls behind, which this skill cannot do because it reads no
performance counts at all. Send an ad that converts badly there first, then come
here with the step it named. Coming here first risks rewriting a page for an ad
that was losing people at the hook. It does not review ad wording for claim
exposure either, which is `claim-safety-review-ad-creative`.

## Required input

- The full ad: headline, primary text or descriptions, visible on-asset text,
  and the call to action button label.
- The exact destination URL including its query string, since parameters can
  change what the page shows.
- A screenshot or capture of the destination as it renders on mobile and on
  desktop, above the fold, or permission to read the live page.
- The offer as the advertiser understands it, including any condition the ad
  does not state.
- The conversion action the page is meant to produce.

## Analysis workflow

1. Extract the three elements from the ad that `match.promise_pairs` names: the
   main claim, the offer, and the call to action. Write each as one sentence
   before opening the page, so the page cannot quietly redefine what the ad
   promised.
2. Open the destination with the same URL the ad uses, parameters included, and
   record what actually loads: redirects, consent walls, interstitials and
   variant tests all change what the arriving reader sees.
3. Locate each of the three elements on the page and record where it appears:
   first heading, first paragraph, further down, or absent.
4. Apply `match.above_fold_rule` to the main claim. Present further down the page
   counts as absent for this check, because a reader who clicked is confirming a
   promise, not reading an article.
5. Check the offer word for word. A different amount, a different trial length or
   a condition present on the page and not in the ad counts as a mismatch rather
   than a nuance.
6. Check the call to action verb and destination. Whatever the ad's button says,
   the page's first action must be the same thing, and two different forms are
   still a mismatch.
7. Read the mobile rendering separately. Above the fold is a different amount of
   page on a phone, and a match confirmed on desktop is not a match confirmed.
8. Score against `match.promise_pairs`: three of three is a match, two of three
   is a partial match reported as a finding, one or none is a break. Report the
   count, name the missing element, and never wave a partial through.

## Decision rules

- Three of three present and the main claim clears `match.above_fold_rule`:
  `ship`, confidence `high` on this skill's own definition of `high`, set out
  in the output format below rather than borrowed from the test scale.
- Two of three present: `rewrite` the page section carrying the missing element,
  and name which of the three is missing in the row.
- Main claim present only below the fold: `rewrite`, because
  `match.above_fold_rule` treats it as absent.
- Offer differs between ad and page: `approval_needed` on which of the two is
  correct, since this is a commercial decision and not a copy fix.
- Destination redirects, gates or fails to load: `investigate` before any copy
  work, and mark the row `needs_data`.
- Poor conversion with a clean three of three match: `investigate` outside the
  creative. The answer is not on this page.

## Output format

Open with one line: does the page keep the ad's promise above the fold, yes or
no, with the count out of three.

| Element | As the ad states it | As the page states it | Position | Match | Evidence label | Confidence | Decision |
|---|---|---|---|---|---|---|---|

What `high` means in this skill, stated here because the comparison family's `high`
rests on `test.min_runtime` and `test.volume_floor`, which are conditions of a
test and cannot be met by a page check at all. Borrowing them would make every
row on this skill `low` for reasons that have nothing to do with how well the
page was read. Here, `high` means three things and only these three: the page
was opened at the ad's own destination URL with its parameters, it was read on
the device family the ad actually serves to, and all three elements of
`match.promise_pairs` were located on the page or positively ruled out. Miss any
one, a remembered version of the page, a desktop-only read on an ad delivering
to phones, or an element nobody looked for, and the row is `medium`. Two missing
is `low`, as is any row where the page did not load as the arriving reader would
see it.

Then the specific page edits required, then `What this could not see`,
`Missing data`, `Approval gates`.

## Practical example

Illustrative made-up campaign, not a real advertiser. Ad headline promises a
free 14 day trial with no card. Ad button says Start free trial. Destination is
a product page whose first heading names the product category and whose first
action is a Request a demo form. The trial is described in a paragraph 3 screens
down and states that a card is required.

Reading: "No. 0 of 3 above the fold." All three elements of
`match.promise_pairs` fail, and the count says so. The main claim fails
`match.above_fold_rule`, since the trial appears 3 screens down and therefore
counts as absent. The call to action does not match: the ad sells a self-serve
trial and the page's first action is a sales conversation. The offer conflicts
outright on the card requirement, so this row is `approval_needed`, and the
question of which version is true is not one this review can answer. The claim that the page underperforms because of its design is refused as
unverified: the mobile capture was not supplied, so mobile is `needs_data`. That
same gap sets the confidence. The page was read live at the ad's own URL and all
three elements were located, but not on the device family this ad mostly serves
to, so the rows are `medium` on this skill's definition of `high`, not `high`.

## Guardrails

- Never confirm a match from the ad and a remembered version of the page. Read
  the live URL, with its parameters.
- Never treat a claim below the fold as delivered.
- Never resolve a conflicting offer yourself. Route it to the human who owns it.
- Do not edit the page or change the ad's destination.
