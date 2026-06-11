# Charlotte — Voyage Archive

An interactive web archive of a four-year family circumnavigation aboard the sailing vessel *Charlotte* (2001–2005), built from a handwritten logbook and a library of ~5,500 photos. Intended as a gift: a way for the family to relive the trip virtually — map, timeline, and photos synced together.

---

## 1. Project overview

**The voyage:** Florida → Bahamas → Panama Canal → across the Pacific → Indian Ocean → around South Africa → across the Atlantic → back through the Bahamas to Florida. ~4 years, 2001–2005.

**The sources:**
- A handwritten logbook kept by the mother for the entire trip. Being scanned and transcribed incrementally.
- ~5,500 photos. Mix of digital (with timestamps) and scanned prints (often without reliable dates). Note: roughly the first year has no photos.

**The goal:** A self-contained, hostable website with a split-view interface — interactive map on one side, log entries and photos on the other — that stays synced. Map-first exploration, chronological timeline, and photo-album browsing should feel equally well supported.

**Audience:** The parents, as a gift. Prioritize ease of use, emotional resonance, and reliability over technical sophistication.

---

## 2. Guiding principles

1. **Data is separate from code.** Entries and photo references live in plain data files (JSON). The application code never needs editing to add content. This is the single most important architectural decision — it's what lets the archive grow to hundreds of entries and thousands of photos over time.
2. **The maintainer follows clear instructions, not code.** Workflows are documented step-by-step. Helper scripts do the heavy lifting (resizing, date-matching, validation). No hand-editing thousands of records.
3. **Originals are never modified.** All scripts work from copies. Full-resolution photos and original scans are preserved untouched.
4. **Build incrementally.** The archive is usable and shippable at every phase, growing leg by leg as scans arrive.
5. **It's a gift.** Polish, warmth, and reliability matter as much as features.

---

## 3. Architecture

### Directory structure

```
LogBook/
├── index.html              # The application (rarely changes)
├── plan.md                 # This document
├── README.md               # Maintainer guide — start here for adding content
├── Scans/                  # Original PDF batches as received (archive)
├── transcripts/drafts/     # Optional scratch notes while transcribing
├── css/style.css
├── js/
│   ├── app.js              # Core app logic
│   ├── map.js              # Leaflet map (+ clustering in Phase 4)
│   └── timeline.js         # Timeline scrubber (Phase 4)
├── data/
│   ├── manifest.json       # Lists legs in order; global metadata
│   ├── leg-01-florida-bahamas.json
│   └── ...                 # One file per leg/region
├── images/
│   ├── scans/              # Cropped logbook images by entry date (2001-11-20.jpg)
│   └── photos/
│       ├── intake/         # Drop new photos here (Phase 3)
│       ├── web/            # Web-sized (auto-generated, Phase 3)
│       └── thumbs/         # Thumbnails (auto-generated, Phase 3)
│   └── originals/          # NOT committed to git — local backup
└── scripts/                # Helper scripts (Phase 3)
```

### Tech stack

- **Leaflet** + OpenStreetMap tiles for the map (free, no API key).
- **Leaflet.markercluster** plugin for pin clustering at world zoom.
- Vanilla JavaScript, HTML, CSS. No build step, no framework — keeps it maintainable for years and hostable as static files.
- **Python** helper scripts for the photo/data workflows (run locally, not part of the website).

### Hosting

- **GitHub Pages** — free, renders static sites properly, gives a shareable URL.
- ⚠️ **Google Drive will NOT work** — it no longer serves HTML as web pages; shared files just download.
- ⚠️ **Repo size:** GitHub repos work best under ~1 GB. 5,500 web-sized photos + thumbnails may approach this. Options when we get closer: Git LFS (large file storage), or a companion image host. Decide in Phase 3.
- Alternatives if GitHub Pages becomes limiting: Netlify Drop, Cloudflare Pages (both free, drag-and-drop friendly).

---

## 4. Data format

### `data/manifest.json`

Lists the legs in order and holds global metadata.

```json
{
  "title": "Charlotte — Voyage Archive",
  "vessel": "Charlotte",
  "years": "2001–2005",
  "legs": [
    { "id": "leg-01", "name": "Florida & the Bahamas", "file": "leg-01-florida-bahamas.json" },
    { "id": "leg-02", "name": "Caribbean & Panama", "file": "leg-02-caribbean-panama.json" }
  ]
}
```

### Leg file (e.g. `data/leg-01-florida-bahamas.json`)

Each leg holds an ordered list of **stops**. Each stop has coordinates, a **passage** label (shown in the UI), one or more dated **entries** (each with its own logbook **scan**), and optional **photos**.

```json
{
  "id": "leg-01",
  "name": "Florida & the Bahamas",
  "stops": [
    {
      "id": "stop-01",
      "n": 1,
      "name": "Rock Harbor, Key Largo",
      "passage": "Florida–Bahamas Passage",
      "lat": 25.077,
      "lng": -80.460,
      "photo_album": null,
      "entries": [
        {
          "date": "2001-11-20",
          "date_display": "Tuesday, November 20, 2001",
          "scan": "images/scans/2001-11-20.jpg",
          "body": "After five months of hard work...",
          "conditions": "Wind: NE–ENE, 8 knots... 70 miles in 12 hours, motoring."
        }
      ],
      "photos": []
    }
  ]
}
```

**Field notes:**
- **Leg files** organize data by voyage segment; the UI uses **passage** labels (e.g. `"Florida–Bahamas Passage"`), not leg numbers.
- `date` is ISO format (`YYYY-MM-DD`) for sorting, image naming, and photo-matching. `date_display` is the human-readable version as written in the log.
- Each **entry** has its own `scan` path. When one logbook page contains multiple entries, crop separate images named by date (`images/scans/YYYY-MM-DD.jpg`).
- Uncertain transcription readings are kept in `[brackets]` within `body`.
- `conditions` is the wind/distance summary line (optional, italic in display).
- `photos` starts empty; `photo_album` holds an external full-res link (e.g. Amazon Photos) when repo size is a concern. Phase 3.
- A stop may have multiple entries (e.g. a multi-day stay at one anchorage).

---

## 5. Photo workflow (Phase 3)

The "mix of dated and undated" reality drives this design.

**For dated (digital) photos:**
1. Drop them in an intake folder.
2. Run `match-photos.py` — reads the timestamp from each photo's metadata (EXIF), proposes a match to the entry/stop whose date range covers it.
3. Review the proposed matches (the script outputs a list to confirm, not silent auto-assignment).
4. Run `resize-photos.py` — generates web-sized (~1600px) and thumbnail (~300px) versions, writes the photo references into the right leg JSON.

**For undated (scanned print) photos:**
1. Drop them in a folder named for the stop they belong to (e.g. `intake/stop-14/`).
2. Run the same resize script — it assigns them to that stop without needing a date.

**Always:** originals are copied, never modified. Web versions are what the site serves. This keeps the page fast and the repo manageable.

---

## 6. Interface

Split view, synced across three modes:

- **Map (Leaflet):** Zoom from whole-world overview down to a single anchorage. Pins cluster when zoomed out, separate as you zoom in. Numbered/ordered along the route, with the track drawn as a line. Click a pin → log jumps to that stop.
- **Timeline:** Scrub across the four years. Click/drag to a date → map and log move to match. Gives the chronological "story" feel.
- **Log + photos:** Scrollable entries grouped by leg. Each entry shows transcribed text, the logbook scan (when available), and a gallery of matched photos with a lightbox for full-size viewing. Scrolling the log highlights the active pin and timeline position.

Visual direction: warm, nautical, document-like. Should feel like opening a treasured journal, not using software.

---

## 7. Phased plan

### Phase 1 — Foundation (current)
- Refactor the prototype to load from external JSON instead of inline data.
- Convert the existing 7 pages (10 stops, Florida → Jamaica) into the new data format.
- Establish the directory structure in the GitHub repo.
- Outcome: working split-view page driven by data files, on a small familiar dataset. Maintainer learns the data format here.

### Phase 2 — Transcription at scale
- Scans arrive incrementally as the mother completes them.
- Transcribe leg by leg into JSON data files.
- Preserve `[bracket]` convention for uncertain readings; flag anything illegible for confirmation.
- Outcome: the full logbook narrative, growing over time.

### Phase 3 — Photos
- Set up the intake → match → resize → reference workflow.
- Process photos in batches, region by region.
- Decide on repo-size strategy (Git LFS vs. companion host).
- Outcome: photos appear alongside entries from the point in the voyage where they begin (~year 2 onward).

### Phase 4 — Rich interface
- Marker clustering for the world map.
- Timeline scrubber.
- Photo galleries + lightbox.
- Visual polish, intro/landing screen, the "gift" presentation.
- Outcome: the finished, shippable archive.

**Parallelism:** Phases 2 and 3 (transcription and photo collection) can run in parallel at whatever pace scanning allows. Phase 1 must come first since everything builds on the data format.

---

## 8. Open decisions

- **Leg breakdown:** How many distinct legs/regions to divide the 4 years into. To be proposed/confirmed — a standard circumnavigation breakdown is a reasonable default (e.g. Florida & Bahamas / Caribbean & Panama / South Pacific / Western Pacific & Indian Ocean / South Africa & South Atlantic / Caribbean & home).
- **Photo starting state:** Are photos currently in dated folders, one big pile, or in between? Affects the matching script design.
- **Scan-to-entry mapping:** Resolved — one cropped image per entry, named by `date`. Original PDFs archived in `Scans/`.
- **Repo size / image hosting:** Resolve in Phase 3 (see Hosting notes).

---

## 9. Status log

- **2001–2005:** The voyage itself.
- **Phase 0 (done):** Prototype built — split-view interface, Leaflet map with real geography, 10 stops from the first 7 logbook pages (Florida → Jamaica), scroll-synced pins, scan placeholders. Single self-contained HTML file with inline data.
- **Phase 1 (done):** Refactored to external JSON + repo structure. Entry-level scans by date, passage-based UI headers, photo gallery stub. See `README.md` for maintainer workflows.
- **Phase 2 (current):** Transcription at scale — add entries and scans as batches arrive.

---

## 10. Transcription reference

Convention established in the prototype, to carry forward:
- Entries transcribed verbatim, preserving the original voice and phrasing.
- Uncertain readings marked in `[brackets]`.
- Each entry tagged with both ISO date and the as-written date display.
- Wind/distance/conditions summary lines kept separate from the narrative body.
- Entries grouped by leg; within a leg, by stop; within a stop, chronologically.

The first 7 pages (already transcribed) cover: Rock Harbor/Key Largo, Gun Cay, Chub Cay, Nassau, Allans Cay, Norman's Cay, Staniel Cay, George Town, Rum Cay, and the Windward Passage to Port Antonio, Jamaica — spanning Nov 20, 2001 to Jan 10, 2002.
