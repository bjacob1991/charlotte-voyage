#!/usr/bin/env python3
"""Rebuild photo-albums.json from images/photos/albums/ and wire photo_set on legs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALBUMS = ROOT / "images/photos/albums"
PHOTO_JSON = ROOT / "data/photo-albums.json"
REVIEW = ROOT / "images/photos/intake/needs-review"

TITLE = {
    "bahamas": "The Bahamas",
    "jamaica": "Jamaica",
    "portobelo": "Portobelo, Panama",
    "panama-canal": "Panama Canal",
    "san-blas": "San Blas Islands",
    "galapagos": "Galápagos Islands",
    "marquesas": "Marquesas",
    "tuamotus": "Tuamotus (Fakarava)",
    "society-islands": "Society Islands",
    "tonga": "Tonga & Niue",
    "new-zealand": "New Zealand",
    "fiji": "Fiji",
    "vanuatu": "Vanuatu",
    "australia-south": "Australia — South Queensland",
    "australia-north": "Australia — GBR & North",
    "bali": "Bali",
    "cocos-keeling": "Cocos (Keeling) Islands",
    "rodrigues": "Rodrigues",
    "mauritius": "Mauritius",
    "reunion": "Réunion",
    "south-africa": "South Africa (Cape & Mossel Bay)",
    "hluhluwe": "Hluhluwe Game Park",
    "st-helena": "St Helena",
    "fernando-de-noronha": "Fernando de Noronha",
    "tobago": "Tobago",
    "georgetown": "George Town (final leg — not yet wired)",
}

ORDER = list(TITLE.keys())


def build_albums() -> dict:
    albums = {}
    for key in ORDER:
        album_dir = ALBUMS / key
        if not album_dir.is_dir():
            continue
        photos = sorted(album_dir.glob("*.jpg"))
        if not photos:
            continue
        title = TITLE[key]
        albums[key] = {
            "title": title,
            "amazon_album": None,
            "photos": [
                {
                    "file": f"images/photos/albums/{key}/{ph.name}",
                    "caption": f"{title} — {ph.stem}",
                }
                for ph in photos
            ],
        }
    return albums


def set_photo_set(leg_path: Path, stop_ns: list[int], album: str) -> None:
    leg = json.loads(leg_path.read_text(encoding="utf-8"))
    for s in leg["stops"]:
        if s["n"] in stop_ns:
            s["photo_set"] = album
    leg_path.write_text(
        json.dumps(leg, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    albums = build_albums()
    payload = {
        "version": 1,
        "_howto": (
            "Shared photo albums. Stops reference an album key via photo_set in leg JSON. "
            "Albums without photo_set still appear in the Photo Galleries index."
        ),
        "albums": albums,
    }
    PHOTO_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {PHOTO_JSON} with {len(albums)} albums, {sum(len(a['photos']) for a in albums.values())} photos")

    # leg-03 FP split
    set_photo_set(ROOT / "data/leg-03-french-polynesia.json", [2], "marquesas")
    set_photo_set(ROOT / "data/leg-03-french-polynesia.json", [4], "tuamotus")
    # Re-read and set society on 6,7,8 — set_photo_set rewrites whole file so do in one pass
    leg3 = json.loads((ROOT / "data/leg-03-french-polynesia.json").read_text(encoding="utf-8"))
    for s in leg3["stops"]:
        if s["n"] == 2:
            s["photo_set"] = "marquesas"
        elif s["n"] == 4:
            s["photo_set"] = "tuamotus"
        elif s["n"] in (6, 7, 8):
            s["photo_set"] = "society-islands"
        # remove old french-polynesia if any remain on other stops
        elif s.get("photo_set") == "french-polynesia":
            del s["photo_set"]
    (ROOT / "data/leg-03-french-polynesia.json").write_text(
        json.dumps(leg3, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print("Wired leg-03: marquesas / tuamotus / society-islands")

    # leg-06 fiji + vanuatu
    leg6 = json.loads((ROOT / "data/leg-06-fiji-vanuatu.json").read_text(encoding="utf-8"))
    for s in leg6["stops"]:
        if s["n"] in (2, 3, 4, 5, 6, 7):
            s["photo_set"] = "fiji"
        elif s["n"] in (9, 10, 11, 12, 13):
            s["photo_set"] = "vanuatu"
    (ROOT / "data/leg-06-fiji-vanuatu.json").write_text(
        json.dumps(leg6, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print("Wired leg-06: fiji (02-07), vanuatu (09-13)")

    # leg-07 australia-south on stops 3-4
    leg7 = json.loads((ROOT / "data/leg-07-australia.json").read_text(encoding="utf-8"))
    for s in leg7["stops"]:
        if s["n"] in (3, 4):
            s["photo_set"] = "australia-south"
    (ROOT / "data/leg-07-australia.json").write_text(
        json.dumps(leg7, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print("Wired leg-07: australia-south (03-04)")

    # Review README
    if REVIEW.exists():
        lines = ["Photos needing your location assignment.", ""]
        for bucket in sorted(p for p in REVIEW.iterdir() if p.is_dir()):
            files = sorted(bucket.glob("*"))
            lines.append(f"## {bucket.name} ({len(files)} files)")
            lines.append(f"Path: {bucket.relative_to(ROOT)}")
            lines.append("")
        (REVIEW / "README.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Review README -> {REVIEW / 'README.txt'}")


if __name__ == "__main__":
    main()
