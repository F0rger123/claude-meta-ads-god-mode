# Naming conventions

Consistent names make reporting, UTMs and the write gate's summaries readable. Use underscores between fields, CamelCase inside a field, no spaces.

## Campaign

```
<CLIENTCODE>_<OBJECTIVE>_<Offer/Service>_<Geo>_<YYYY-MM>[_<Test>]
MDX_LEADS_KitchenRemodel_York_2026-10
MDX_SEARCH_KitchenRemodel_York_2026-10
```
OBJECTIVE: LEADS, SALES, TRAFFIC, AWARE (Meta); SEARCH, PMAX, DISPLAY, VIDEO (Google).

## Ad set / ad group

```
Meta ad set : <Audience>_<Age>_<Geo><Radius>[_<Placement>]   Broad_HO_30-65_York25mi
Google group: <Theme> - <Match>                              Kitchen Remodel - Phrase
```

## Ad

```
<Format>_<Concept>_<Hook>_v<n>      UGC_FounderWalkthrough_QuestionHook_v1
                                     Static_FreeDesignConsult_Offer_v2
```
Format: UGC, Video, Static, Carousel, RSA.

## Tests

Append `_T<id>` matching the experiment log id: `UGC_FounderWalkthrough_v1_T07`.

The client code is a 2-4 letter code you choose per client (store it in the profile `aliases` if useful). Never put personal data or prices in names.
