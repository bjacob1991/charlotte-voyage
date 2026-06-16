#!/usr/bin/env python3
"""Export each page of logbook PDFs in Scans/ to JPG images for the crop annotator."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def parse_logbook_range(pdf_stem: str) -> tuple[int, int] | None:
    match = re.match(r"Pg(\d+)-Pg(\d+)", pdf_stem, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def sort_pdfs(pdfs: list[Path]) -> list[Path]:
    def sort_key(path: Path) -> int:
        span = parse_logbook_range(path.stem)
        return span[0] if span else 9999

    return sorted(pdfs, key=sort_key)


def pdf_export_signature(pdf_path: Path) -> dict:
    stat = pdf_path.stat()
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    doc.close()
    return {
        "mtime": int(stat.st_mtime),
        "size": stat.st_size,
        "pageCount": page_count,
    }


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.is_file():
        return {"version": 2, "sources": {}, "pages": []}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "sources" not in data:
        data["sources"] = {}
    if "pages" not in data:
        data["pages"] = []
    return data


def remove_pdf_exports(source_name: str, manifest_pages: list[dict], out_dir: Path) -> list[dict]:
    kept: list[dict] = []
    for entry in manifest_pages:
        if entry.get("source") == source_name:
            image_path = out_dir / entry["file"]
            if image_path.is_file():
                image_path.unlink()
        else:
            kept.append(entry)
    return kept


def needs_export(pdf_path: Path, manifest: dict, out_dir: Path) -> bool:
    source = pdf_path.name
    signature = pdf_export_signature(pdf_path)
    stored = manifest.get("sources", {}).get(source)
    if stored != signature:
        return True

    for entry in manifest.get("pages", []):
        if entry.get("source") != source:
            continue
        if not (out_dir / entry["file"]).is_file():
            return True

    return False


def export_pdf(
    pdf_path: Path,
    out_dir: Path,
    dpi: int,
    manifest_pages: list[dict],
) -> dict:
    doc = fitz.open(pdf_path)
    span = parse_logbook_range(pdf_path.stem)
    start_page = span[0] if span else 1
    new_entries: list[dict] = []

    for index in range(len(doc)):
        logbook_page = start_page + index if span else index + 1
        filename = f"{pdf_path.stem}_p{index + 1:02d}.jpg"
        out_path = out_dir / filename

        page = doc[index]
        pixmap = page.get_pixmap(dpi=dpi, alpha=False)
        pixmap.save(str(out_path), output="jpeg", jpg_quality=92)

        entry = {
            "file": filename,
            "source": pdf_path.name,
            "pdfPage": index + 1,
            "logbookPage": logbook_page,
        }
        new_entries.append(entry)
        print(f"  {pdf_path.name} page {index + 1} -> {filename} (logbook p.{logbook_page})")

    doc.close()
    manifest_pages.extend(new_entries)
    return pdf_export_signature(pdf_path)


def resolve_only_pdfs(scans_dir: Path, only_args: list[str]) -> set[str]:
    resolved: set[str] = set()
    for item in only_args:
        candidate = Path(item)
        if candidate.suffix.lower() == ".pdf":
            resolved.add(candidate.name)
            continue
        direct = scans_dir / f"{item}.pdf"
        if direct.is_file():
            resolved.add(direct.name)
            continue
        matches = list(scans_dir.glob(f"{item}*.pdf"))
        if len(matches) == 1:
            resolved.add(matches[0].name)
        elif len(matches) > 1:
            names = ", ".join(p.name for p in matches)
            raise ValueError(f"Ambiguous --only value {item!r}; matches: {names}")
        else:
            raise ValueError(f"No PDF found for --only value {item!r}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(description="Export logbook PDF pages to JPG images.")
    parser.add_argument(
        "--scans-dir",
        type=Path,
        default=Path("Scans"),
        help="Folder containing source PDFs (default: Scans/)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("images/scans/_pages"),
        help="Output folder for page images (default: images/scans/_pages/)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Render resolution (default: 200)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove all JPG/JSON exports in the output folder, then export every PDF",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="PDF",
        help="Export only these PDF(s), e.g. Pg39-Pg69.pdf or Pg39-Pg69",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-export even if the PDF has not changed since the last run",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    scans_dir = (root / args.scans_dir).resolve()
    out_dir = (root / args.out_dir).resolve()
    manifest_path = out_dir / "manifest.json"

    if not scans_dir.is_dir():
        print(f"Scans folder not found: {scans_dir}", file=sys.stderr)
        sys.exit(1)

    pdfs = sort_pdfs(list(scans_dir.glob("*.pdf")))
    if not pdfs:
        print(f"No PDF files found in {scans_dir}", file=sys.stderr)
        sys.exit(1)

    only_names: set[str] | None = None
    if args.only:
        only_names = resolve_only_pdfs(scans_dir, args.only)
        pdfs = [pdf for pdf in pdfs if pdf.name in only_names]
        if not pdfs:
            print("No matching PDFs found for --only.", file=sys.stderr)
            sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    if args.clean:
        removed = 0
        for pattern in ("*.jpg", "*.jpeg", "manifest.json"):
            for path in out_dir.glob(pattern):
                path.unlink()
                removed += 1
        if removed:
            print(f"Cleaned {removed} old file(s) from {out_dir}")
        manifest = {"version": 2, "sources": {}, "pages": []}
    else:
        manifest = load_manifest(manifest_path)

    manifest_pages = list(manifest.get("pages", []))
    sources = dict(manifest.get("sources", {}))
    exported_count = 0
    skipped_count = 0

    for pdf_path in pdfs:
        if not args.clean and not args.force and not needs_export(pdf_path, manifest, out_dir):
            print(f"Skipping {pdf_path.name} (already exported, unchanged)")
            skipped_count += 1
            continue

        print(f"Exporting {pdf_path.name}...")
        manifest_pages = remove_pdf_exports(pdf_path.name, manifest_pages, out_dir)
        signature = export_pdf(pdf_path, out_dir, args.dpi, manifest_pages)
        sources[pdf_path.name] = signature
        exported_count += 1

    # Drop manifest entries whose source PDF no longer exists.
    existing_sources = {pdf.name for pdf in scans_dir.glob("*.pdf")}
    removed_sources = [name for name in sources if name not in existing_sources]
    for source_name in removed_sources:
        del sources[source_name]
        manifest_pages = remove_pdf_exports(source_name, manifest_pages, out_dir)

    manifest_pages.sort(key=lambda entry: (entry.get("logbookPage", 0), entry.get("source", ""), entry.get("pdfPage", 0)))

    manifest = {
        "version": 2,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "dpi": args.dpi,
        "sources": sources,
        "pages": manifest_pages,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"\nExported {exported_count} PDF(s); skipped {skipped_count} unchanged PDF(s).")
    print(f"Manifest now lists {len(manifest_pages)} page image(s) in {out_dir}")
    print(f"Wrote manifest: {manifest_path}")
    print("\nNext: open tools/scan-crop-annotator.html and click 'Load exported pages'.")


if __name__ == "__main__":
    main()
