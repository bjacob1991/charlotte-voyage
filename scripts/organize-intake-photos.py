#!/usr/bin/env python3
"""
Organize intake/Albums into images/photos/albums/.

- Resize to web size (max 1600px, q=82) to match existing live albums
- Split French Polynesia: marquesas / tuamotus / society-islands
- Ambiguous files → images/photos/intake/needs-review/
- Georgetown held for leg-10 (georgetown album, not wired)
- Future-leg albums created and populated
"""

from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INTAKE = ROOT / "images/photos/intake/Albums"
ALBUMS = ROOT / "images/photos/albums"
REVIEW = ROOT / "images/photos/intake/needs-review"
PHOTO_JSON = ROOT / "data/photo-albums.json"

MAX_EDGE = 1600
JPEG_QUALITY = 82

# Dedup: prefer these source folders over duplicates
SKIP_FOLDERS = {
    "St Helena Fernando de Noronha Tobago George town Bahamas Islands in the Stream",
    "cocos keeling reunion mauritius three islands",
}

GENERIC_RE = re.compile(
    r"^(picture|PICTURE|dscn|p\d+|100_|102-|106_|107_|Rotation|rotation|Rotation of|rotation of)",
    re.I,
)


def nkey(name: str) -> str:
    return name.lower().strip()


def is_generic(name: str) -> bool:
    base = Path(name).stem
    if GENERIC_RE.match(base):
        return True
    if base.lower() in {"picture", "james1"}:
        return True
    return False


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def save_web(src: Path, dest: Path) -> None:
    """Copy/resize image to dest as JPEG."""
    ensure_dir(dest.parent)
    try:
        with Image.open(src) as im:
            im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
            if im.mode == "L":
                im = im.convert("RGB")
            w, h = im.size
            scale = MAX_EDGE / max(w, h)
            if scale < 1:
                im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            dest = dest.with_suffix(".jpg")
            im.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)
    except Exception as e:
        print(f"  WARN resize failed {src.name}: {e} — raw copy")
        shutil.copy2(src, dest)


def next_name(album_dir: Path, prefix: str, counters: dict[str, int]) -> Path:
    counters[prefix] = counters.get(prefix, 0) + 1
    return album_dir / f"{prefix}_{counters[prefix]:03d}.jpg"


def classify_south_pacific(name: str) -> str | None:
    n = nkey(name)
    if any(x in n for x in ("nuku hiva", "ua pou", "marquesas", "daniels bay")):
        return "marquesas"
    if any(x in n for x in ("fakarava", "tuamotos", "tuamotu")):
        return "tuamotus"
    if any(x in n for x in ("tahiti", "moorea", "bora", "huahine", "raiatea", "tahaa")):
        return "society-islands"
    return None  # review


def classify_nz_fiji(name: str) -> str | None:
    n = nkey(name)
    if any(
        x in n
        for x in (
            "opua",
            "jills walk",
            "nz",
            "new zealand",
            "kawau",
            "whangarei",
        )
    ):
        return "new-zealand"
    if "vanuatu" in n or "fatfala" in n:
        return "vanuatu"
    if any(
        x in n
        for x in (
            "fiji",
            "figi",
            "savu",
            "kandav",
            "kanduv",
            "musket",
            "natadola",
            "vanua belavi",
            "vanua balavu",
            "kava",
            "kawa",
            "snorkeling in figi",
        )
    ):
        return "fiji"
    # person/boat shots without place — review
    if any(x in n for x in ("jill", "brian", "mahi", "chief", "teacher", "brother")):
        return None
    return None


def classify_australia(name: str) -> str | None:
    n = nkey(name)
    if any(
        x in n
        for x in (
            "lady musgrave",
            "flinder",
            "lizard",
            "airle",
            "airlie",
            "on the way",
            "top of australia",
            "darwin",
        )
    ):
        return "australia-north"
    if any(x in n for x in ("the spit", "manuhiri", "morton", "moreton", "tangalooma", "peel")):
        return "australia-south"
    if any(x in n for x in ("bundaberg", "fraser", "tin can", "mooloolaba", "gary", "garry")):
        return "australia-south"
    return None  # generic australia → review


def classify_bali_cocos(name: str) -> str | None:
    n = nkey(name)
    if n.startswith("bali") or " bali" in n:
        return "bali"
    if "cocos" in n:
        return "cocos-keeling"
    if "darwin" in n:
        return "australia-north"
    return None


def classify_three_islands(name: str) -> str | None:
    n = nkey(name)
    if "cocos" in n:
        return "cocos-keeling"
    if "mauritius" in n or "mauritiuxs" in n:
        return "mauritius"
    if "reunion" in n:
        return "reunion"
    if "rodriguez" in n or "rodrigues" in n:
        return "rodrigues"
    return None


def classify_islands_stream(name: str) -> str | None:
    n = nkey(name)
    if "georgetown" in n or "george town" in n:
        return "georgetown"  # leg-10 hold, not wired
    if "naronha" in n or "noronha" in n:
        return "fernando-de-noronha"
    if "helena" in n:
        return "st-helena"
    if "tabago" in n or "tobago" in n:
        return "tobago"
    return None


def classify_capetown(name: str) -> str | None:
    n = nkey(name)
    if "helena" in n:
        return "st-helena"
    if any(x in n for x in ("capetown", "cape town", "table mountain", "mossel", "africa arrival", "africa mossel")):
        return "south-africa"
    return "south-africa"


def main() -> None:
    counters: dict[str, int] = {}
    # Seed counters from existing album files so we don't overwrite
    for album_dir in ALBUMS.iterdir() if ALBUMS.exists() else []:
        if not album_dir.is_dir():
            continue
        prefix = album_dir.name
        # special: existing french-polynesia will move
        nums = []
        for f in album_dir.glob("*.jpg"):
            m = re.search(r"_(\d+)\.jpg$", f.name, re.I)
            if m:
                nums.append(int(m.group(1)))
        if nums:
            counters[prefix] = max(nums)

    stats: dict[str, int] = defaultdict(int)
    review_notes: list[str] = []

    def add(album: str, src: Path, prefix: str | None = None) -> None:
        prefix = prefix or album
        dest_dir = ALBUMS / album
        ensure_dir(dest_dir)
        dest = next_name(dest_dir, prefix, counters)
        save_web(src, dest)
        stats[album] += 1

    def review(src: Path, reason: str, bucket: str) -> None:
        dest_dir = REVIEW / bucket
        ensure_dir(dest_dir)
        # keep original filename; avoid clobber
        dest = dest_dir / src.name
        if dest.exists():
            dest = dest_dir / f"{src.stem}__{src.parent.name.replace(' ', '_')}{src.suffix}"
        shutil.copy2(src, dest)
        stats["needs-review"] += 1
        review_notes.append(f"{bucket}: {src.name} ({reason})")

    # --- Move existing french-polynesia into society-islands (unlabeled prior set) ---
    fp_dir = ALBUMS / "french-polynesia"
    if fp_dir.exists():
        ensure_dir(ALBUMS / "society-islands")
        for f in sorted(fp_dir.glob("*.jpg")):
            add("society-islands", f, "society-islands")
            stats["migrated-from-french-polynesia"] += 1
        # remove old album files after copy
        for f in fp_dir.glob("*"):
            f.unlink()
        try:
            fp_dir.rmdir()
        except OSError:
            pass
        print("Migrated existing french-polynesia -> society-islands")

    # Seed society-islands counter already handled via next_name

    folders = [d for d in sorted(INTAKE.iterdir()) if d.is_dir() and d.name not in SKIP_FOLDERS]
    print("Processing folders:")
    for d in folders:
        print(f"  {d.name}")

    seen_hashes: set[str] = set()  # simple path-based skip for identical names across dup folders

    for folder in folders:
        files = [
            f
            for f in folder.rglob("*")
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
        ]
        for src in sorted(files, key=lambda p: p.name.lower()):
            name = src.name
            album: str | None = None
            reason = ""

            if folder.name == "2002 South Pacific":
                album = classify_south_pacific(name)
                if album is None:
                    review(src, "unnamed FP camera file", "french-polynesia-unsorted")
                    continue

            elif folder.name == "NZ to Fiji 2003":
                if is_generic(name):
                    review(src, "generic Picture/camera — NZ vs Fiji vs Vanuatu", "nz-fiji-unsorted")
                    continue
                album = classify_nz_fiji(name)
                if album is None:
                    review(src, "named but ambiguous place", "nz-fiji-unsorted")
                    continue

            elif folder.name == "Ambae Festival & Vanuatu Pics":
                if is_generic(name) or name.lower().startswith("102-"):
                    # festival folder is clearly Vanuatu — keep generics in vanuatu
                    album = "vanuatu"
                else:
                    album = "vanuatu"

            elif folder.name == "WATERFALL_BAY_FESTIFAL_2003":
                album = "vanuatu"

            elif folder.name == "Australia":
                if is_generic(name) or name.lower().startswith(("100_", "102-")):
                    review(src, "generic Australia — south vs north/GBR", "australia-unsorted")
                    continue
                album = classify_australia(name)
                if album is None:
                    review(src, "unclassified Australia name", "australia-unsorted")
                    continue

            elif folder.name == "Bali Cocos Keeling":
                album = classify_bali_cocos(name)
                if album is None:
                    review(src, "unclassified Bali/Cocos/Darwin", "bali-cocos-unsorted")
                    continue

            elif folder.name in ("three islands",):
                album = classify_three_islands(name)
                if album is None:
                    review(src, "unclassified three-islands", "indian-ocean-unsorted")
                    continue

            elif folder.name == "Islands in the Stream":
                album = classify_islands_stream(name)
                if album is None:
                    review(src, "unclassified Islands in the Stream", "atlantic-unsorted")
                    continue

            elif folder.name == "Capetown":
                album = classify_capetown(name)

            elif folder.name == "Hluhluwe Game Park":
                album = "hluhluwe"

            else:
                review(src, f"unhandled folder {folder.name}", "misc-unsorted")
                continue

            add(album, src)

    # Ensure empty future dirs exist even if somehow empty
    for key in [
        "marquesas",
        "tuamotus",
        "society-islands",
        "fiji",
        "vanuatu",
        "australia-south",
        "australia-north",
        "bali",
        "cocos-keeling",
        "rodrigues",
        "mauritius",
        "reunion",
        "south-africa",
        "hluhluwe",
        "st-helena",
        "fernando-de-noronha",
        "tobago",
        "georgetown",
    ]:
        ensure_dir(ALBUMS / key)

    print("\n=== Counts ===")
    for k in sorted(stats.keys()):
        print(f"  {k}: {stats[k]}")

    # Write review index
    ensure_dir(REVIEW)
    (REVIEW / "README.txt").write_text(
        "Photos that could not be confidently assigned by filename.\n"
        "Please sort into the correct images/photos/albums/<album>/ folder\n"
        "(or tell the agent the destination album key).\n\n"
        + "\n".join(review_notes[:500])
        + (f"\n... and {len(review_notes) - 500} more\n" if len(review_notes) > 500 else "\n"),
        encoding="utf-8",
    )
    print(f"\nReview pile: {stats['needs-review']} files -> {REVIEW}")

    # Build photo-albums.json
    # Live (wired) vs staged (on disk, shown in gallery index if we include them)
    # User wants all photos — include all albums in photo-albums.json.
    # Only wire photo_set for legs that exist; staged albums still appear in Photo Galleries.

    title_map = {
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

    # Preserve existing albums we didn't rebuild
    existing_keep = ["bahamas", "jamaica", "portobelo", "panama-canal", "san-blas", "galapagos", "tonga", "new-zealand"]

    albums_out: dict = {}
    # Order for gallery
    order = [
        "bahamas",
        "jamaica",
        "san-blas",
        "portobelo",
        "panama-canal",
        "galapagos",
        "marquesas",
        "tuamotus",
        "society-islands",
        "tonga",
        "new-zealand",
        "fiji",
        "vanuatu",
        "australia-south",
        "australia-north",
        "bali",
        "cocos-keeling",
        "rodrigues",
        "mauritius",
        "reunion",
        "south-africa",
        "hluhluwe",
        "st-helena",
        "fernando-de-noronha",
        "tobago",
        "georgetown",
    ]

    for key in order:
        album_dir = ALBUMS / key
        if not album_dir.exists():
            continue
        photos = sorted(album_dir.glob("*.jpg"))
        if not photos and key == "georgetown":
            # still list empty? skip empty except we expect files
            pass
        entries = []
        for ph in photos:
            # caption from stem without number padding noise
            caption = key.replace("-", " ").title() + " — " + ph.stem.split("_")[-1]
            # Better captions: use nicer title
            caption = f"{title_map.get(key, key)} — {ph.stem}"
            entries.append(
                {
                    "file": f"images/photos/albums/{key}/{ph.name}",
                    "caption": caption,
                }
            )
        albums_out[key] = {
            "title": title_map.get(key, key),
            "amazon_album": None,
            "photos": entries,
        }

    payload = {
        "version": 1,
        "_howto": "Shared photo albums. Stops reference an album key via photo_set in leg JSON. Albums without photo_set still appear in the Photo Galleries index.",
        "albums": albums_out,
    }
    PHOTO_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {PHOTO_JSON}")

    # Size report
    total = sum(f.stat().st_size for f in ALBUMS.rglob("*.jpg"))
    print(f"\nAlbums on disk: {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
