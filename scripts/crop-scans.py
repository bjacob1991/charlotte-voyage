#!/usr/bin/env python3
"""Crop final scan images from annotator JSON and exported page images."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def load_pages_map(data: dict) -> dict:
    if "pages" in data and isinstance(data["pages"], dict):
        return data["pages"]
    raise ValueError("Annotations JSON must contain a top-level 'pages' object.")


def crop_box(image: Image.Image, rect: dict) -> Image.Image:
    width, height = image.size
    left = max(0, int(rect["x"] * width))
    top = max(0, int(rect["y"] * height))
    right = min(width, int((rect["x"] + rect["w"]) * width))
    bottom = min(height, int((rect["y"] + rect["h"]) * height))
    if right <= left or bottom <= top:
        raise ValueError(f"Invalid crop rectangle: {rect}")
    return image.crop((left, top, right, bottom))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cropped scan images from annotations.")
    parser.add_argument(
        "--annotations",
        type=Path,
        default=Path("scan-crop-annotations.json"),
        help="Exported annotations JSON from the HTML tool",
    )
    parser.add_argument(
        "--pages-dir",
        type=Path,
        default=Path("images/scans/_pages"),
        help="Folder containing exported page JPGs",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("images/scans"),
        help="Folder for final cropped scan images",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned crops without writing files",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    annotations_path = (root / args.annotations).resolve()
    pages_dir = (root / args.pages_dir).resolve()
    out_dir = (root / args.out_dir).resolve()

    if not annotations_path.is_file():
        print(f"Annotations file not found: {annotations_path}", file=sys.stderr)
        sys.exit(1)
    if not pages_dir.is_dir():
        print(f"Pages folder not found: {pages_dir}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(annotations_path.read_text(encoding="utf-8"))
    pages = load_pages_map(data)

    written = 0
    skipped = 0
    for page_key, page_data in pages.items():
        image_name = page_data.get("image") or page_key
        page_path = pages_dir / image_name
        if not page_path.is_file():
            print(f"Missing page image: {page_path}")
            skipped += 1
            continue

        image = Image.open(page_path)
        for box in page_data.get("boxes", []):
            scan_path = box.get("scanPath")
            rect = box.get("rect")
            if not scan_path or not rect:
                continue

            out_path = root / scan_path
            if args.dry_run:
                print(f"Would write {out_path}")
                written += 1
                continue

            crop = crop_box(image, rect)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            crop.save(out_path, "JPEG", quality=92)
            print(f"Wrote {out_path}")
            written += 1

    print(f"\nDone. Wrote {written} image(s). Skipped {skipped} missing page(s).")


if __name__ == "__main__":
    main()
