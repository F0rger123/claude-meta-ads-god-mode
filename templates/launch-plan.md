# Launch plan - <Client> - <Campaign>

## Pre-flight (all must be ✓ before activation)

- [ ] Client and account verified by read: <name> / <account id> / <date>
- [ ] Payment method present (human-checked)
- [ ] Conversion event / primary action fires and is deduplicated
- [ ] UTMs on every ad; landing page loads on mobile; form/call tracked
- [ ] Geo inside `geographic_limits`; location type = people living in / presence
- [ ] Copy free of prohibited claims; special ad category correct
- [ ] Budget, bid strategy and schedule as in the brief
- [ ] Everything created PAUSED and read back

## Created objects (PAUSED)

| Level | Id | Name | Key settings |
|---|---|---|---|
| Campaign | | | |
| Ad set / ad group | | | |
| Ad | | | preview |

## Activation

- Approved by: ______ on ______ (chat / permission prompt)
- Ticket: tkt_______
- Activated at: ______ (timezone)

## Read schedule

| Date | Check | Decision allowed |
|---|---|---|
| +1 day | delivery, disapprovals, tracking firing | fix breakage only |
| +3 days | spend pacing, CPM/CTR sanity | no performance verdicts |
| +7 days | first read: CPL, CTR, CVR, learning status | small adjustments if out of learning |
| +14 days | creative read, search terms | creative swaps, negatives |
| +30 days | full review vs brief targets | budget / structure changes |
