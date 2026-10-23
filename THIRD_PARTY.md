# Third-party software and licenses

No third-party code is vendored in this repository. The components below are **installed separately by the user** and run as their own processes or services. This repository is MIT-licensed; using these components alongside it does not change their licenses.

| Component | Role here | License | Notes |
|---|---|---|---|
| Meta Ads MCP server (`https://mcp.facebook.com/ads`) | primary Meta connector | Meta Platform Terms / service terms | hosted by Meta |
| [getmcpads-com/meta-ads-mcp-server](https://github.com/getmcpads-com/meta-ads-mcp-server) | optional Meta fallback | Apache-2.0 | run via npx; not redistributed |
| [byadsco/meta-ads-mcp](https://github.com/byadsco/meta-ads-mcp) | optional agency fallback | MIT | not redistributed |
| [googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp) | Google Ads reads | Apache-2.0 | run via pipx; adds a usage header to API calls per its README |
| [google-ads (Python client)](https://github.com/googleads/google-ads-python) | Google Ads writes (bundled writer) | Apache-2.0 | `pip install google-ads`; imported at runtime only |
| [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp) | GA4 reads | Apache-2.0 | run via pipx |
| Python standard library | core | PSF License | |

## Influences (no code or text copied)

These MIT-licensed projects were reviewed during connector research; their topics influenced which mechanics the knowledge layer covers. All text here is original.

- [aaronpdoherty/meta-ads-genius](https://github.com/aaronpdoherty/meta-ads-genius) (MIT)
- [sepivip/meta-ads-skill](https://github.com/sepivip/meta-ads-skill) (MIT)

Platform mechanics cite Meta and Google documentation; see the source URLs in each reference file.

## Trademarks

Meta, Facebook and Instagram are trademarks of Meta Platforms, Inc. Google Ads and Google Analytics are trademarks of Google LLC. This project is independent and not affiliated with, endorsed by, or sponsored by Meta or Google.
