#!/usr/bin/env python3
"""Compare expected scan targets vs annotations vs files on disk."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def expected_paths() -> dict[str, str]:
    layout = json.loads((ROOT / "data/scan-layout.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for leg in manifest["legs"]:
        if leg.get("status") == "planned":
            continue
        leg_data = json.loads((ROOT / "data" / leg["file"]).read_text(encoding="utf-8"))
        for stop in leg_data["stops"]:
            for entry in stop["entries"]:
                key = f"{leg['id']}:{entry['date']}"
                lay = layout["entries"].get(key)
                if lay and lay.get("scans"):
                    paths = lay["scans"]
                elif entry.get("scans"):
                    paths = entry["scans"]
                elif entry.get("scan"):
                    paths = [entry["scan"]]
                else:
                    paths = []
                for p in paths:
                    name = p.replace("images/scans/", "")
                    out[name] = key
    return out


def main() -> None:
    ann = json.loads((ROOT / "scan-crop-annotations.json").read_text(encoding="utf-8"))
    expected = expected_paths()
    scans_dir = ROOT / "images/scans"
    pages_dir = ROOT / "images/scans/_pages"

    boxed: dict[str, list[str]] = {}
    missing_pages: list[tuple[str, str]] = []
    for page_key, page_data in ann.get("pages", {}).items():
        image_name = page_data.get("image") or page_key
        page_path = pages_dir / image_name
        page_missing = not page_path.is_file()
        for box in page_data.get("boxes", []):
            sp = box.get("scanPath", "")
            if not sp:
                continue
            name = sp.replace("images/scans/", "")
            boxed.setdefault(name, []).append(page_key)
            if page_missing:
                missing_pages.append((page_key, name))

    on_disk = {f.name for f in scans_dir.glob("*.jpg") if f.name[:4].isdigit()}

    no_scan_ref: list[tuple[str, str]] = []
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    layout = json.loads((ROOT / "data/scan-layout.json").read_text(encoding="utf-8"))
    for leg in manifest["legs"]:
        if leg.get("status") == "planned":
            continue
        leg_data = json.loads((ROOT / "data" / leg["file"]).read_text(encoding="utf-8"))
        for stop in leg_data["stops"]:
            for entry in stop["entries"]:
                key = f"{leg['id']}:{entry['date']}"
                lay = layout["entries"].get(key)
                has_ref = bool(lay and lay.get("scans")) or entry.get("scan") or entry.get("scans")
                if not has_ref:
                    no_scan_ref.append((key, entry.get("date_display", entry["date"])))

    missing_pages: list[tuple[str, str]] = []
    print("=== ENTRIES WITH NO SCAN REFERENCE (site shows no image) ===")
    for key, label in no_scan_ref:
        print(f"  {key}  ({label})")

    print("\n=== SKIPPED: boxes on missing/stale page files ===")
    for page_key, name in missing_pages:
        print(f"  {name}  (annotation page key: {page_key})")

    print("\n=== EXPECTED BY DATA BUT NOT ON DISK ===")
    for name in sorted(expected):
        if name not in on_disk:
            print(f"  {name}  ({expected[name]})")

    print("\n=== BOXED IN ANNOTATIONS BUT NOT ON DISK ===")
    for name in sorted(boxed):
        if name not in on_disk:
            print(f"  {name}  (pages: {', '.join(boxed[name])})")

    print("\n=== ON DISK BUT NOT EXPECTED (stale single vs split?) ===")
    for name in sorted(on_disk - set(expected)):
        print(f"  {name}")

    print("\n=== NOT BOXED YET (expected, no annotation box) ===")
    for name in sorted(expected):
        if name not in boxed:
            print(f"  {name}  ({expected[name]})")

    print(f"\nSummary: {len(expected)} expected, {len(boxed)} boxed, {len(on_disk & set(expected))} on disk matching expected")


if __name__ == "__main__":
    main()
