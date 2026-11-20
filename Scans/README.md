# Original logbook scan PDFs

Drop incoming scan batches here as you receive them. **Do not edit these files** — they are the archival originals.

## Naming convention

Name each PDF for the **logbook page range** it contains:

```
Pg1-Pg7.pdf
Pg8-Pg38.pdf
Pg39-Pg53.pdf
Pg54-Pg69.pdf
Pg70-Pg99.pdf
Pg100-Pg118.pdf    ← final batch; the logbook ends on page 118
```

The export script uses this filename to assign `logbookPage` numbers in `images/scans/_pages/manifest.json`.

## Inventory (verified 2026-11-18)

| File | PDF pages | Notes |
|------|-----------|-------|
| `Pg1-Pg7.pdf` | 7 | Matches name |
| `Pg8-Pg38.pdf` | 31 | Matches name |
| `Pg39-Pg53.pdf` | 15 | Matches name |
| `Pg54-Pg69.pdf` | 16 | Matches name; proofread, JSON, and crops done |
| `Pg70-Pg99.pdf` | 30 | Renamed from `Scan 70-99.pdf`. Page rotation set (odd pages 90°, even pages 270°) so every page reads upright. Transcription loaded into leg-07 and leg-08; crops not drawn yet |
| `Pg100-Pg118.pdf` | 19 | Corrected scan received 2026-11-18 (the earlier `Scan 100-118.pdf` was a duplicate of 70–99). Same page rotation applied; unrotated original kept in `VOID/`. Transcription loaded into leg-09 and leg-10; crops not drawn yet |

The scanner feeds facing pages in opposite directions, so in these two batches every even-numbered PDF page came in upside down. The rotation is stored as a page setting only; the scanned images are unchanged.

When you transcribe, crop individual log entries and save them in `images/scans/` using the entry date (see root `README.md`).
