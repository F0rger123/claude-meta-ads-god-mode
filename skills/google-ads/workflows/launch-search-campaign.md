# Google Search campaign build (paused-first)

Generic flow: [workflows/campaign-launch.md](../../../workflows/campaign-launch.md). Google specifics:

1. **Context** - `adsgm use`; `list_accessible_customers` confirms the profile's customer id is accessible; GAQL: existing campaigns (overlap?), conversion actions (is the primary lead action clean?), existing shared negative lists.
2. **Keyword plan** - 1-3 tightly themed ad groups (e.g., "kitchen remodel", "kitchen design", "kitchen renovation cost" only if converting intent). Phrase + exact to start; broad only with Smart Bidding and clean tracking. Seed negatives: jobs, careers, diy, how to, ideas, pictures, free, cheap (if the data later disagrees, remove), supplier brands the client does not install.
3. **Geo** - proximity radius around the business or location ids; the writer sets presence-only targeting ("People in or regularly in your included locations"). Stay inside `geographic_limits`.
4. **Bidding** - maximize conversions when primary conversions are clean; manual CPC / maximize clicks only for a new account without tracking (say why). Target CPA only with history.
5. **Budget** - daily budget so that expected clicks/day x CVR yields learnable conversions; compute with the client's CPL target and say what to expect.
6. **Ads** - one RSA per ad group with 10-15 headlines (keyword theme, offer, location, trust, CTA) and 4 descriptions; pin only if legally required. Assets: sitelinks, callouts, call asset, location asset (account level) - recommend them; the writer does not create assets yet.
7. **Plan file** - write [writer-plan-format.md](../references/writer-plan-format.md) JSON; `adsgm google apply --plan plan.json` (validate_only). Fix any errors Google returns.
8. **Ticket + create** - `adsgm plan create --google-plan plan.json`; `adsgm google apply --plan plan.json --ticket tkt_... --execute`. Campaign is created PAUSED.
9. **Read back** - GAQL the new campaign/ad groups/keywords/ads; show the user exactly what exists, with ids.
10. **Activation** - separate: plan with `{"op":"set_status","resource":"campaign","id":"<id>","status":"ENABLED"}`, `adsgm plan activate --google-plan`, approval, execute.
