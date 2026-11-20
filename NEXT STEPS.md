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
- [x] Pg54–Pg69 proofread, loaded, and cropped (189/189 coverage through that batch)
- [x] Crop annotator, `scan-layout.json`, multi-page A/B splits
- [x] Passage meta, at-sea/anchorage icons, map photo badges
- [x] Pg70–Pg118 reviewed and loaded (2026-11-20). Leg-07 runs through Darwin (Jul 16, 2004). Legs 08–10 are `in-progress`: Indian Ocean, South Africa & the South Atlantic, Caribbean & home (last entry Apr 18, 2005, Gibson Dry Dock). 151 new scan targets; 15 of them span two or three pages.

**Next:**
1. **Crop Pg70–Pg118** — `tools/scan-crop-annotator.html` → draw boxes for `Pg70-Pg99_p01`…`p30` and `Pg100-Pg118_p01`…`p19` (targets and page jumps are already in `data/scan-layout.json`) → `python scripts/crop-scans.py`
2. `python scripts/check-scan-coverage.py` before committing that batch
3. Mark legs `"complete"` in `data/manifest.json` once the crops are on disk and the text has had a final read on the site

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
