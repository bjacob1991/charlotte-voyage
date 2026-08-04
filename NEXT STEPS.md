# NEXT STEPS

Full design rationale lives in `plan.md`. Maintainer workflows live in `README.md`.
Data field reference: `data/SCHEMA.md`.

**Live site:** https://bjacob1991.github.io/charlotte-voyage/

## Phase 1 — COMPLETE

- [x] Data-driven shell (`index.html`, `css/`, `js/app.js`, `js/map.js`)
- [x] Manifest → legs → log → scroll sync → gallery
- [x] Leaflet pins, route, clustering, dateline-safe unwrapped longitudes + bounded map
- [x] Maintainer README, folder structure, `.gitignore`

## Phase 2 — IN PROGRESS (transcription + scans)

**Done so far:**
- [x] Legs 01–07 on site (`in-progress`); legs 08–10 `planned` in `data/manifest.json` (10-leg breakdown)
- [x] Pg8–Pg53 scan crops on disk (151/151 expected coverage)
- [x] Pg54–Pg69 proofread and loaded into JSON — leg-06 through Oct 16; leg-07 Australia from Oct 29 (Coral Sea → Southport)
- [x] Crop annotator, `scan-layout.json`, multi-page A/B splits (including 8 Pg54–69 splits registered; crop images still pending)
- [x] Passage meta, at-sea/anchorage icons, map photo badges
- [x] Pg70–Pg99 AI draft in `transcripts/drafts/Pg70-Pg99-draft.md` (not proofread; do not generate JSON yet)

**Next:**
1. **Crop Pg54–Pg69** — `tools/scan-crop-annotator.html` → draw boxes for `Pg54-Pg69_p01`…`p16` (A/B targets already in `data/scan-layout.json`) → `python scripts/crop-scans.py`
2. `python scripts/check-scan-coverage.py` before committing that batch
3. **Proofread Pg70–Pg99** against page images, then extend leg-07 / open leg-08 (Indian Ocean) as the log requires
4. Continue until all ten legs are `"complete"` in the manifest

## Phase 3 — IN PROGRESS (trip photos)

**Done so far:**
- [x] Shared albums in `data/photo-albums.json` + `photo_set` on stops
- [x] Early voyage albums: Bahamas → New Zealand
- [x] **Aug 2026 intake sorted** into web-sized albums (~329 MB / 1075 photos on disk)
  - Wired: Marquesas, Tuamotus, Society Islands, Fiji, Vanuatu, Australia-south
  - Staged (gallery index, not linked to stops yet): Australia-north, Bali, Cocos, Rodrigues, Mauritius, Réunion, South Africa, Hluhluwe, St Helena, Fernando de Noronha, Tobago, Georgetown
- [x] Ambiguous filenames set aside in `images/photos/intake/needs-review/` for Brian
- [x] Gallery index, lightbox, map camera badges; catalog albums appear even before stop wiring

**Next:**
1. Review `images/photos/intake/needs-review/` and assign NZ vs Fiji vs Australia-south/north vs FP sub-regions
2. Amazon Photos links via `amazon_album` if GitHub repo size becomes painful (~329 MB photos now; watch total repo size)
3. Optional later: `resize-photos.py` / `match-photos.py` for digital photo volume
4. Wire staged albums to stops as legs 07–10 transcripts land

## Phase 4 — Later

- Timeline scrubber, landing page, gift presentation polish
- Git LFS or companion host if repo approaches GitHub size limits

## Hosting

Live site: **https://bjacob1991.github.io/charlotte-voyage/**

```bash
git push origin main
```

Preview locally: `python -m http.server 8000` → http://localhost:8000
