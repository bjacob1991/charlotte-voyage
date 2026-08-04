# Original logbook scan PDFs

Drop incoming scan batches here as you receive them. **Do not edit these files** — they are the archival originals.

## Naming convention

Name each PDF for the **logbook page range** it contains:

```
Pg1-Pg7.pdf
Pg8-Pg38.pdf
Pg39-Pg53.pdf
Pg54-Pg69.pdf
Pg70-Pg99.pdf      ← rename from "Scan 70-99.pdf" when convenient
Pg100-Pg129.pdf    ← see note below on "Scan 100-118.pdf"
```

The export script uses this filename to assign `logbookPage` numbers in `images/scans/_pages/manifest.json`.

## Inventory (verified 2026-07-27)

| File | PDF pages | Notes |
|------|-----------|-------|
| `Pg1-Pg7.pdf` | 7 | Matches name |
| `Pg8-Pg38.pdf` | 31 | Matches name |
| `Pg39-Pg53.pdf` | 15 | Matches name |
| `Pg54-Pg69.pdf` | 16 | Matches name; proofread + JSON done; **scan crops still pending** |
| `Scan 70-99.pdf` | 30 | Matches 70–99 inclusive; AI draft in `transcripts/drafts/`; prefer rename to `Pg70-Pg99.pdf` |
| `Scan 100-118.pdf` | **30** | Name says 19 pages (100–118); file has 30 → likely **100–129**. Confirm against the paper log before renaming to `Pg100-Pg129.pdf`. |

When you transcribe, crop individual log entries and save them in `images/scans/` using the entry date (see root `README.md`).
