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
- [x] Legs 01–06 on site (`in-progress`); legs 07–10 `planned` in `data/manifest.json` (10-leg breakdown)
- [x] Pg8–Pg53 scan crops on disk (151/151 expected coverage)
- [x] Crop annotator, `scan-layout.json`, multi-page A/B splits
- [x] Passage meta, at-sea/anchorage icons, map photo badges

**Next:**
1. Transcribe **Pg54–Pg69** → draft in `transcripts/drafts/`, then extend leg-06 / open leg-07 (Australia) as the log requires
2. Crop new entries: `tools/scan-crop-annotator.html` → `python scripts/crop-scans.py`
3. `python scripts/check-scan-coverage.py` before committing a batch
4. Continue until all ten legs are `"complete"` in the manifest

## Phase 3 — IN PROGRESS (trip photos)

**Done so far:**
- [x] Shared albums in `data/photo-albums.json` + `photo_set` on stops
- [x] Albums: Bahamas, Jamaica, San Blas, Portobelo, Panama Canal, Galápagos, French Polynesia, Tonga & Niue, New Zealand
- [x] Gallery index, lightbox, map camera badges

**Next:**
1. Fiji / Vanuatu (and later) prints as they are sorted from intake
2. Amazon Photos links via `amazon_album` when ready for full-res external viewing
3. Optional later: `resize-photos.py` / `match-photos.py` for digital photo volume

## Phase 4 — Later

- Timeline scrubber, landing page, gift presentation polish
- Git LFS or companion host if repo approaches GitHub size limits

## Hosting

Live site: **https://bjacob1991.github.io/charlotte-voyage/**

```bash
git push origin main
```

Preview locally: `python -m http.server 8000` → http://localhost:8000
