# Workflow: graphic ads

Trigger: `/ads:creative <client> graphics`, "make some ad images", "create graphic ads".

1. **Brief first.** Use the creative analysis (what's fatiguing, which hooks win, `adsgm learn summary`) and the client profile: offer, brand voice, prohibited claims, service area. Write 2–4 variants that each test **one** idea (offer-first vs testimonial vs before/after vs lifestyle photo).
2. **Pick templates:**

   | Template | Best for | Needs |
   |---|---|---|
   | `offer-card` | clear offer, cold audiences | headline, optional badge/subhead/CTA |
   | `photo-overlay` | lifestyle or project photo | `image` (client-supplied photo) |
   | `quote` | social proof | a real review the client approved |
   | `split` | before / after | `image` + `image2` (client-supplied, real) |

   Never invent reviews or use photos the client didn't supply (most profiles list this as a prohibited claim).
3. **Formats:** `1x1` (feed), `4x5` (feed, recommended), `9x16` (Stories/Reels, text kept out of the top 14% and bottom 20%), `1.91x1` (link ads / Google display).
4. **Render:** write the brief JSON (format in `godmode/creative.py`) and run `adsgm creative render --brief brief.json`.
   - It uses the profile's `brand` colors, font and logo.
   - It refuses variants that contain a prohibited claim, and warns on long headlines or text-heavy images.
   - It writes SVG, plus PNG when Edge or Chrome is installed, and a contact sheet `index.html`.
5. **Show the user** the contact sheet. Iterate on copy or templates as needed.
6. **To use an image:** upload it and create the ad **PAUSED** in the right ad set (Meta: `ads_create_creative` then `ads_create_ad`). Activation is a separate approved step. Log the test (`adsgm plan ... --tags offer-card --predict-metric ctr ...`) so the learning loop judges it.
7. **For AI-generated photography** (not just layouts), use the user's own image tool or service and feed the result in as `image`. This plugin calls no paid image API.
