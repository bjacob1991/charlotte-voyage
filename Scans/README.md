# Original logbook scan PDFs

Drop incoming scan batches here as you receive them. **Do not edit these files** — they are the archival originals.

## Naming convention

Name each PDF for the **logbook page range** it contains:

```
Pg1-Pg7.pdf      ← logbook pages 1 through 7
Pg8-Pg38.pdf     ← logbook pages 8 through 38
Pg39-Pg69.pdf    ← logbook pages 39 through 69
Pg70-Pg95.pdf    ← next batch when you receive it
```

The export script uses this filename to assign `logbookPage` numbers in `images/scans/_pages/manifest.json`.

When you transcribe, crop individual log entries and save them in `images/scans/` using the entry date (see root `README.md`).
