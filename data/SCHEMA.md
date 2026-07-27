# Data schema

Source of truth for the live site: JSON under `data/`, loaded by `js/app.js`.
Do not treat leg-01 as a rigid template — the schema has grown deliberately.

## `manifest.json`

| Field | Required | Notes |
|-------|----------|-------|
| `headline`, `vessel`, `tagline`, `years` | Yes | Header copy |
| `vessel_image`, `vessel_image_alt`, `vessel_caption` | Optional | Intro / vessel card |
| `legs[]` | Yes | Ordered voyage segments |

Each leg:

| Field | Required | Notes |
|-------|----------|-------|
| `id` | Yes | Stable id, e.g. `leg-06` |
| `name` | Yes | Display name |
| `file` | Yes | Filename under `data/` |
| `status` | Yes | `planned` (skipped), `in-progress`, or `complete` |

Only `in-progress` and `complete` legs are fetched by the site.

## Leg file (`leg-XX-….json`)

Top level: `id`, `name`, `stops[]`.

### Stop

| Field | Required | Notes |
|-------|----------|-------|
| `id` | Yes | e.g. `stop-01` |
| `n` | Yes | Order within the leg |
| `name` | Yes | Map / log title |
| `passage` | Yes | UI sticky section label (not the leg name) |
| `lat`, `lng` | Yes | Map pin (WGS84). Crossing the antimeridian is fine; `map.js` unwraps for display |
| `photo_album` | Yes* | External full-res URL, or `null` |
| `photos` | Yes* | Per-stop inline photo list; usually `[]` when using `photo_set` |
| `entries` | Yes | Dated log entries |
| `kind` | Optional | `"passage"` for at-sea / crossing stops (icon + map treatment) |
| `photo_set` | Optional | Key into `photo-albums.json` for a shared regional album |

\*Present on existing stops; keep them even when null/empty so the shape stays consistent.

### Entry

| Field | Required | Notes |
|-------|----------|-------|
| `date` | Yes | ISO `YYYY-MM-DD`, optional `a`/`b` suffix for two same-day entries |
| `date_display` | Yes | As written in the logbook |
| `body` | Yes | Narrative transcript |
| `conditions` | Optional | Wind / distance / run summary (or `null`) |
| `scan` | Usual | Single crop path `images/scans/YYYY-MM-DD.jpg` |
| `scans` | Optional | Multi-image list on the entry itself (rare; prefer `scan-layout.json`) |

When one diary entry spans two physical pages, prefer **`data/scan-layout.json`** over putting `scans` on the entry:

```json
"leg-05:2002-12-29": {
  "scans": ["images/scans/2002-12-29a.jpg", "images/scans/2002-12-29b.jpg"],
  "pages": ["Pg39-Pg53_p01.jpg", "Pg39-Pg53_p02.jpg"],
  "note": "optional"
}
```

Key format: `legId:date`. Layout overrides win over `entry.scan` in the UI.

Same-calendar-day **separate** diary entries still use dated suffixes in the leg JSON (`2002-01-18a` / `2002-01-18b`) — that is not the same as a multi-page split.

## `photo-albums.json`

```json
"albums": {
  "bahamas": {
    "title": "The Bahamas",
    "amazon_album": null,
    "photos": [{ "file": "images/photos/albums/bahamas/bahamas_001.jpg", "caption": "…" }]
  }
}
```

Stops reference an album with `"photo_set": "bahamas"`.

## Conventions

- Verbatim transcription; uncertain readings in `[brackets]`.
- Prefer spaced times (`3 pm`) site-wide.
- Numeric ranges use an en-dash (`6–8`) where established in later legs.
- Run figures belong in `conditions`, not duplicated in `body`, unless the voice line must stay in the narrative.
