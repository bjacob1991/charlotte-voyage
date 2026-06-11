# NEXT STEPS

Full design rationale lives in `plan.md`. Maintainer workflows live in `README.md`.

## Phase 1 — COMPLETE

- [x] `index.html` — data-driven shell
- [x] `css/style.css` — extracted from prototype
- [x] `js/app.js` — manifest → legs → log → scroll sync → gallery stub → divider
- [x] `js/map.js` — Leaflet pins, route, click-to-scroll
- [x] `data/leg-01-florida-bahamas.json` — entry-level scans by date, passage labels
- [x] `README.md` — maintainer guide (scans, transcripts, photos)
- [x] `.gitignore`
- [x] Folder structure: `Scans/`, `transcripts/drafts/`, `images/scans/`

**Acceptance check:** `python -m http.server 8000` → http://localhost:8000 — map with 10 pins, passage headers (not leg headers), per-entry scan placeholders, pin ↔ log sync, draggable divider.

## Your ongoing work (Phase 2)

1. Receive PDF batches → save to `Scans/`
2. Transcribe → edit `data/leg-XX-….json`
3. Crop entry images → `images/scans/YYYY-MM-DD.jpg`
4. When ready for leg 2: create `data/leg-02-caribbean-panama.json`, set `"status": "in-progress"` in manifest

## Later

- **Phase 3:** Photo intake scripts, resize workflow, external album links
- **Phase 4:** Timeline scrubber, map clustering, lightbox polish, landing page
- **Git + GitHub Pages** when you want a shareable URL
- Delete `scan images/` folder (old Bermuda test scans) whenever convenient
