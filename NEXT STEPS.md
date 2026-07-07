# NEXT STEPS

Full design rationale lives in `plan.md`. Maintainer workflows live in `README.md`.

## Phase 1 — COMPLETE

- [x] `index.html` — data-driven shell
- [x] `css/style.css` — extracted from prototype
- [x] `js/app.js` — manifest → legs → log → scroll sync → gallery
- [x] `js/map.js` — Leaflet pins, route, click-to-scroll
- [x] `data/leg-01-florida-bahamas.json` — entry-level scans by date, passage labels
- [x] `README.md` — maintainer guide (scans, transcripts, photos)
- [x] `.gitignore`
- [x] Folder structure: `Scans/`, `transcripts/drafts/`, `images/scans/`

## Phase 2 — IN PROGRESS (transcription + scans)

**Done so far:**
- [x] Legs 01–05 transcribed (in-progress on site)
- [x] Leg 06 JSON started (`leg-06-pacific-indian.json`)
- [x] Pg8–Pg38 scan crops committed
- [x] Crop annotator, `scan-layout.json`, multi-page entry splits
- [x] Passage meta, at-sea/anchorage icons, map photo badges

**Next:**
1. Transcribe Pg39–Pg53 → finish leg 05 entries, extend leg 06
2. Export pages: `python scripts/export-pdf-pages.py --only Pg39-Pg53.pdf` (and later batches)
3. Crop new entries in `tools/scan-crop-annotator.html` → `crop-scans.py`
4. Run `python scripts/check-scan-coverage.py` before commit
5. Continue leg-by-leg until all 8 legs are `"complete"` in manifest

## Phase 3 — STARTED (trip photos)

**Done so far:**
- [x] `data/photo-albums.json` — shared location albums
- [x] 31 scanned prints in `images/photos/albums/` (Bahamas, Jamaica, San Blas, Portobelo, Panama Canal, Galápagos)
- [x] `photo_set` on relevant stops in legs 01–02
- [x] Album-grouped gallery index, on-site photo lightbox, map camera badges

**Next:**
1. Add more scanned prints as they are sorted (intake → albums → `photo-albums.json` → `photo_set`)
2. Add Amazon Photos links via `amazon_album` when ready for full-res external viewing
3. Optional: `scripts/resize-photos.py` for web/thumb copies when digital photo volume grows
4. Optional: `scripts/match-photos.py` for EXIF-dated digital photos later in the voyage

## Phase 4 — Later

- Timeline scrubber, landing page, gift presentation polish
- Git LFS or companion host if repo approaches GitHub size limits

## Hosting

Site is on **GitHub Pages** (static). Push `main` to update the live site.

```bash
git push origin main
```

Preview locally: `python -m http.server 8000` → http://localhost:8000
