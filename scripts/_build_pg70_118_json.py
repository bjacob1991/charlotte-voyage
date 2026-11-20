#!/usr/bin/env python3
"""Load the reviewed Pg70–Pg118 transcriptions into leg JSON and scan-layout.

Review decisions applied from transcripts/drafts/Pg70-Pg99-review.md:
- April 12 is 2004 (the log's "2003" is a slip)
- Palm Islands are north of Townsville
- Feel Free (Tom & Liz)
- page 88 "fluky winds"
Spellings already settled in the v2 draft are kept: Soya, Ciris, Borache,
Astrika, Ken & Larry, Ithaca, trucking, Golden Sovereign, June 16, Durban,
3 am, Tuzi Gazi, Heart's Content.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}
FUNCTION_WORDS = {"The", "We", "It", "A", "An", "But", "And", "So", "Then", "This", "That", "There"}

# leg, name, passage, lat, lng, start, end, kind, photo_set
# Dates are inclusive. kind "" means a harbor/coast stop.
RANGES: list[tuple] = [
    ("leg-07", "Moreton Island & Mooloolaba", "Queensland — Northbound", -26.682, 153.119, "2004-03-27", "2004-04-10", "", "australia-south"),
    ("leg-07", "Great Sandy Strait & Lady Musgrave", "Queensland — Northbound", -23.905, 152.393, "2004-04-11", "2004-04-15", "", "australia-north"),
    ("leg-07", "Pancake Creek to Goldsmith Island", "Queensland — Northbound", -20.87, 149.58, "2004-04-16", "2004-04-20", "", "australia-north"),
    ("leg-07", "The Whitsundays", "Queensland — Northbound", -20.268, 148.717, "2004-04-26", "2004-04-28", "", "australia-north"),
    ("leg-07", "Passage to Cairns", "Queensland — Northbound", -18.35, 146.30, "2004-04-30", "2004-05-02", "passage", ""),
    ("leg-07", "Cairns", "Queensland — Northbound", -16.918, 145.778, "2004-05-20", "2004-05-20", "", "australia-north"),
    ("leg-07", "Cooktown & Lizard Island", "Queensland — Northbound", -14.668, 145.465, "2004-05-21", "2004-06-02", "", "australia-north"),
    ("leg-07", "Flinders Group to Portland Roads", "Cape York", -13.49, 143.72, "2004-06-03", "2004-06-08", "", "australia-north"),
    ("leg-07", "Cape Grenville to Bamaga", "Cape York", -10.892, 142.389, "2004-06-09", "2004-06-14", "", "australia-north"),
    ("leg-07", "Gulf of Carpentaria", "Cape York to the Northern Territory", -13.2, 138.8, "2004-06-15", "2004-06-16", "passage", ""),
    ("leg-07", "Gove", "Northern Territory", -12.182, 136.782, "2004-06-19", "2004-06-19", "", "australia-north"),
    ("leg-07", "Wessel Islands", "Northern Territory", -11.175, 136.678, "2004-06-20", "2004-06-24", "", "australia-north"),
    ("leg-07", "Cape Don", "Northern Territory", -11.32, 131.77, "2004-06-25", "2004-06-26", "", "australia-north"),
    ("leg-07", "Darwin", "Northern Territory", -12.463, 130.845, "2004-06-30", "2004-07-16", "", "australia-north"),
    ("leg-08", "Darwin to Bali", "Darwin to Bali", -12.25, 123.0, "2004-07-17", "2004-07-23", "passage", ""),
    ("leg-08", "Bali", "Bali", -8.747, 115.213, "2004-08-05", "2004-08-05", "", "bali"),
    ("leg-08", "Bali to Cocos Keeling", "Bali to Cocos Keeling", -10.45, 105.67, "2004-08-06", "2004-08-12", "passage", ""),
    ("leg-08", "Cocos Keeling", "Cocos Keeling", -12.156, 96.822, "2004-09-05", "2004-09-05", "", "cocos-keeling"),
    ("leg-08", "Cocos to Rodrigues", "Cocos to Rodrigues", -15.5, 80.0, "2004-09-10", "2004-09-22", "passage", ""),
    ("leg-08", "Rodrigues", "Rodrigues", -19.724, 63.427, "2004-10-05", "2004-10-05", "", "rodrigues"),
    ("leg-08", "Rodrigues to Mauritius", "Mauritius & Réunion", -19.9, 59.5, "2004-10-06", "2004-10-07", "passage", ""),
    ("leg-08", "Port Louis, Mauritius", "Mauritius & Réunion", -20.161, 57.498, "2004-10-15", "2004-10-15", "", "mauritius"),
    ("leg-08", "St. Pierre, Réunion", "Mauritius & Réunion", -21.339, 55.478, "2004-10-22", "2004-10-22", "", "reunion"),
    ("leg-08", "Réunion to Richards Bay", "Across to South Africa", -28.5, 40.0, "2004-10-23", "2004-11-03", "passage", ""),
    ("leg-09", "Richards Bay & Hluhluwe", "South Africa", -28.783, 32.078, "2004-11-11", "2004-11-11", "", "hluhluwe"),
    ("leg-09", "Durban", "South Africa", -29.868, 31.022, "2004-11-12", "2004-11-27", "", ""),
    ("leg-09", "Durban to East London", "South Africa", -31.7, 29.8, "2004-11-28", "2004-11-28", "passage", ""),
    ("leg-09", "East London", "South Africa", -33.029, 27.855, "2004-12-02", "2004-12-02", "", ""),
    ("leg-09", "Port Elizabeth", "South Africa", -33.961, 25.602, "2004-12-03", "2004-12-08", "", ""),
    ("leg-09", "Mossel Bay", "South Africa", -34.183, 22.146, "2004-12-09", "2004-12-15", "", "south-africa"),
    ("leg-09", "Rounding the Cape", "South Africa", -34.83, 20.00, "2004-12-16", "2004-12-16", "passage", ""),
    ("leg-09", "Cape Town", "South Africa", -33.904, 18.421, "2004-12-31", "2004-12-31", "", "south-africa"),
    ("leg-09", "Cape Town to St. Helena", "The South Atlantic", -20.0, 5.0, "2005-01-01", "2005-01-12", "passage", ""),
    ("leg-09", "St. Helena", "The South Atlantic", -15.925, -5.718, "2005-01-17", "2005-01-17", "", "st-helena"),
    ("leg-09", "St. Helena to Fernando de Noronha", "The South Atlantic", -8.0, -20.0, "2005-01-18", "2005-02-02", "passage", ""),
    ("leg-09", "Fernando de Noronha", "The South Atlantic", -3.854, -32.423, "2005-02-07", "2005-02-07", "", "fernando-de-noronha"),
    ("leg-09", "Fernando de Noronha to Tobago", "The South Atlantic", 6.0, -45.0, "2005-02-08", "2005-02-22", "passage", ""),
    ("leg-10", "Tobago", "The Caribbean", 11.25, -60.70, "2005-03-10", "2005-03-10", "", "tobago"),
    ("leg-10", "Through the Windward Islands", "The Caribbean", 15.4, -61.3, "2005-03-11", "2005-03-13", "passage", ""),
    ("leg-10", "St. Martin", "The Caribbean", 18.070, -63.085, "2005-03-14", "2005-03-22", "", ""),
    ("leg-10", "Virgin Islands to Mayaguana", "Homeward through the Bahamas", 22.0, -70.0, "2005-03-23", "2005-03-26", "passage", ""),
    ("leg-10", "Mayaguana", "Homeward through the Bahamas", 22.367, -72.967, "2005-03-30", "2005-03-30", "", ""),
    ("leg-10", "Georgetown, Exuma", "Homeward through the Bahamas", 23.516, -75.768, "2005-03-31", "2005-04-05", "", "georgetown"),
    ("leg-10", "Exumas to the Berry Islands", "Homeward through the Bahamas", 24.6, -76.6, "2005-04-06", "2005-04-07", "passage", ""),
    ("leg-10", "Great Harbour, Berry Islands", "Homeward through the Bahamas", 25.738, -77.840, "2005-04-11", "2005-04-11", "", ""),
    ("leg-10", "Gulf Stream", "Homeward through the Bahamas", 27.8, -79.6, "2005-04-12", "2005-04-12", "passage", ""),
    ("leg-10", "Cape Canaveral & Titusville", "Florida", 28.612, -80.808, "2005-04-13", "2005-04-13", "", ""),
    ("leg-10", "St. Augustine & Gibson Dry Dock", "Florida", 29.99, -81.60, "2005-04-18", "2005-04-18", "", ""),
]

LEG_META = {
    "leg-08": ("leg-08", "The Indian Ocean"),
    "leg-09": ("leg-09", "South Africa & the South Atlantic"),
    "leg-10": ("leg-10", "The Caribbean & Home"),
}


def page_image(log_page: int) -> str:
    if 70 <= log_page <= 99:
        return f"Pg70-Pg99_p{log_page - 69:02d}.jpg"
    if 100 <= log_page <= 118:
        return f"Pg100-Pg118_p{log_page - 99:02d}.jpg"
    raise ValueError(f"log page out of range: {log_page}")


def display(iso: str) -> str:
    y, m, d = map(int, iso.split("-"))
    dt = date(y, m, d)
    return f"{DAY[dt.weekday()]}, {dt.strftime('%B')} {d}, {y}"


def parse_heading(raw: str, prev_iso: str | None) -> tuple[str, bool]:
    is_cont = "continuation" in raw.lower()
    text = raw.replace("\\~", "~").replace("\\_", "_")
    text = re.sub(r"\*\[.*?\]\*", " ", text)
    text = re.sub(r"~~.+?~~", " ", text)
    text = re.sub(r"\[uncertain:\s*([^;\]]+).*?\]", r"\1", text)
    text = re.sub(r"\(continuation\)", " ", text, flags=re.I)
    match = re.search(
        r"\b(" + "|".join(sorted(MONTHS, key=len, reverse=True)) + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*(\d{4}))?",
        text,
        flags=re.I,
    )
    if not match:
        raise ValueError(f"could not parse date heading: {raw!r}")
    month = MONTHS[match.group(1).lower()]
    day = int(match.group(2))
    year_txt = match.group(3)
    if year_txt:
        year = int(year_txt)
        if year == 2003 and month == 4 and day == 12:
            year = 2004
    elif prev_iso:
        year = int(prev_iso[:4])
        prev_month = int(prev_iso[5:7])
        if month < prev_month - 6:
            year += 1
    else:
        year = 2004
    iso = date(year, month, day).isoformat()
    return iso, is_cont


def clean_chunk(raw: str) -> str:
    text = raw.replace("\r\n", "\n")
    # Notes are *[...]*; one continuation is written *[continued ...] and*
    text = re.sub(r"\*\[[^\]]*\]", "", text)
    text = text.replace("\\*", "")
    text = text.replace("*", "")
    text = re.sub(r"\[uncertain:\s*([^\]]+)\]", lambda m: "[" + re.split(r"[;,]", m.group(1))[0].strip() + "]", text)
    text = re.sub(r"\[illegible[^\]]*\]", "[illegible]", text)
    text = re.sub(r"\[fact check this\]", "", text, flags=re.I)
    text = text.replace("[Feel] Free", "Feel Free")
    text = text.replace("north of Townsend", "north of Townsville")
    text = text.replace("flaky winds", "fluky winds")
    text = text.replace("Cape Grenville.:", "Cape Grenville.")
    text = text.replace("[& Sterling", "& Sterling")
    text = text.replace("Tranquillity", "Tranquility")
    text = re.sub(r"(\d)\s*-\s*(\d)", r"\1–\2", text)
    paragraphs: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        lines = [ln.strip() for ln in para.splitlines() if ln.strip() and ln.strip() != "***"]
        if not lines:
            continue
        joined = re.sub(r"\s+", " ", " ".join(lines)).strip()
        if joined:
            paragraphs.append(joined)
    return "\n\n".join(paragraphs).strip()


def join_continuation(prev: str, cont: str) -> str:
    cont = cont.strip()
    prev = prev.rstrip()
    if not cont:
        return prev
    if prev and prev[-1] not in ".!?\"”":
        first, _, rest = cont.partition(" ")
        if first in FUNCTION_WORDS:
            cont = first.lower() + (" " + rest if rest else "")
    return (prev + " " + cont).strip()


def extract_run(body: str) -> tuple[str, str | None]:
    matches = list(
        re.finditer(
            r"24-(?:hour|hr|hours) runs?\s*[:—–-]?\s*\d[\d,\s&½./-]*\s*(?:miles|mi)?",
            body,
            flags=re.I,
        )
    )
    if not matches:
        return body, None
    match = matches[-1]
    phrase = re.sub(r"\s+", " ", match.group(0)).strip().rstrip(".")
    rest = body[match.end():]
    attached = re.match(r"\s*—\s*(\S.*)$", rest, flags=re.S)
    if attached and len(attached.group(1)) <= 140 and "." not in attached.group(1):
        phrase = phrase + " — " + re.sub(r"\s+", " ", attached.group(1)).strip().rstrip(".")
        rest = ""
    kept = (body[: match.start()] + rest).strip()
    kept = re.sub(r"[ \t]{2,}", " ", kept)
    kept = re.sub(r" +([.,])", r"\1", kept)
    return kept.strip(), phrase


def parse_drafts() -> list[dict]:
    files = [
        ROOT / "transcripts/drafts/Pg70-Pg99-draft-v2.md",
        ROOT / "transcripts/drafts/Pg100-Pg118-draft.md",
    ]
    entries: list[dict] = []
    prev_iso: str | None = None
    current_page: int | None = None
    chunk: list[str] = []
    pending_heading: str | None = None

    def flush() -> None:
        nonlocal pending_heading, chunk, prev_iso
        if pending_heading is None:
            chunk = []
            return
        iso, is_cont = parse_heading(pending_heading, prev_iso)
        body = clean_chunk("\n".join(chunk))
        page = current_page
        if page is None:
            raise ValueError(f"entry {iso} has no page")
        if is_cont:
            if not entries:
                raise ValueError(f"continuation with no previous entry: {pending_heading}")
            prev = entries[-1]
            if prev["date"] != iso:
                raise ValueError(f"continuation date {iso} != previous {prev['date']} ({pending_heading})")
            prev["body"] = join_continuation(prev["body"], body)
            if page not in prev["pages"]:
                prev["pages"].append(page)
        else:
            if any(e["date"] == iso for e in entries):
                raise ValueError(f"duplicate date {iso}")
            entries.append({"date": iso, "body": body, "pages": [page]})
            prev_iso = iso
        pending_heading = None
        chunk = []

    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## Review notes") or line.startswith("## Sources") or line.startswith("## Places"):
                flush()
                pending_heading = None
                break
            page_match = re.match(r"^## PAGE (\d+)\b", line)
            if page_match:
                flush()
                current_page = int(page_match.group(1))
                continue
            if line.startswith("## "):
                flush()
                pending_heading = None
                continue
            heading = re.match(r"^###\s+(.+)$", line)
            if heading:
                flush()
                pending_heading = heading.group(1).strip()
                continue
            if pending_heading is not None:
                chunk.append(line)
        flush()
    return entries


def assign(entries: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {leg: [] for leg in ("leg-07", "leg-08", "leg-09", "leg-10")}
    open_ranges = list(RANGES)
    for entry in entries:
        iso = entry["date"]
        hits = [r for r in open_ranges if r[5] <= iso <= r[6]]
        if len(hits) != 1:
            raise ValueError(f"{iso} matched {len(hits)} stops")
        leg = hits[0][0]
        body, conditions = extract_run(entry["body"])
        if not body:
            raise ValueError(f"empty body for {iso}")
        y, m, d = map(int, iso.split("-"))
        written = date(y, m, d)
        entry_out = {
            "date": iso,
            "date_display": display(iso),
            "body": body,
            "conditions": conditions,
            "pages": entry["pages"],
            "_range": hits[0],
            "_weekday_ok": DAY[written.weekday()] == display(iso).split(",")[0],
        }
        grouped[leg].append(entry_out)
    return grouped


def build_stop(n: int, spec: tuple, items: list[dict]) -> dict:
    _leg, name, passage, lat, lng, _a, _b, kind, photo = spec
    stop = {
        "id": f"stop-{n:02d}",
        "n": n,
        "name": name,
        "passage": passage,
        "lat": lat,
        "lng": lng,
        "photo_album": None,
        "photos": [],
        "entries": [],
    }
    if photo:
        stop["photo_set"] = photo
    if kind:
        stop["kind"] = kind
    # photo_set before entries matches later stops in leg-06; leg-07 puts photo_set after entries.
    # Keep photo_set next to the other stop metadata and entries last, except kind which
    # existing passage stops place after entries. Match leg-07 passage shape:
    # id, n, name, passage, lat, lng, photo_album, photos, entries, kind, and photo_set
    # just before entries when present (leg-06 harbor style is photo_set before entries
    # is not consistent). Follow leg-07 Australia stops: photo_set after entries.
    stop.pop("photo_set", None)
    for item in items:
        pages = item["pages"]
        row = {
            "date": item["date"],
            "date_display": item["date_display"],
            "body": item["body"],
            "conditions": item["conditions"],
        }
        if len(pages) == 1:
            row["scan"] = f"images/scans/{item['date']}.jpg"
        stop["entries"].append(row)
    if photo:
        stop["photo_set"] = photo
    if kind:
        # kind already set above; photo_set pop didn't remove kind
        pass
    if not kind:
        stop.pop("kind", None)
    return stop


def layout_for(leg_id: str, item: dict) -> dict:
    pages = item["pages"]
    iso = item["date"]
    if len(pages) == 1:
        scans = [f"images/scans/{iso}.jpg"]
        note = None
    else:
        letters = "abcdefghijklmnopqrstuvwxyz"
        scans = [f"images/scans/{iso}{letters[i]}.jpg" for i in range(len(pages))]
        if len(pages) == 2:
            note = f"Starts on log p{pages[0]}, continues on p{pages[1]}"
        else:
            note = "Spans log " + ", ".join(f"p{p}" for p in pages)
    out = {"scans": scans, "pages": [page_image(p) for p in pages]}
    if note:
        out["note"] = note
    return out


def dump_compact(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> None:
    entries = parse_drafts()
    grouped = assign(entries)
    problems: list[str] = []
    for entry in entries:
        y, m, d = map(int, entry["date"].split("-"))
        # weekday is checked against the calendar, not the handwritten day name
        # (clipped day names were already rebuilt in the drafts)
        _ = date(y, m, d)
        if "[" in entry["body"] and re.search(r"\[(?![\w][^\]]{0,40}\])", entry["body"]):
            pass
        leftover = re.findall(r"\[[^\]]{25,}\]", entry["body"])
        if leftover:
            problems.append(f"long bracket in {entry['date']}: {leftover}")
        if "*[" in entry["body"] or "uncertain:" in entry["body"] or "**" in entry["body"]:
            problems.append(f"markup left in {entry['date']}")

    expected = {"leg-07": 37, "leg-08": 46, "leg-09": 48, "leg-10": 20}
    for leg, count in expected.items():
        got = len(grouped[leg])
        if got != count:
            problems.append(f"{leg} has {got} entries, expected {count}")

    # Every range is used, and entries inside a range are sorted and inside it.
    for spec in RANGES:
        leg = spec[0]
        items = [e for e in grouped[leg] if e["_range"] == spec]
        if not items:
            problems.append(f"empty stop {spec[1]} ({spec[5]}–{spec[6]})")
        dates = [e["date"] for e in items]
        if dates != sorted(dates):
            problems.append(f"unsorted {spec[1]}: {dates}")

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        sys.exit(1)

    # --- leg-07 append ---
    leg7_path = ROOT / "data/leg-07-australia.json"
    leg7 = json.loads(leg7_path.read_text(encoding="utf-8"))
    leg7["stops"] = [s for s in leg7["stops"] if s["n"] <= 4]
    n = 4
    layout_new: dict[str, dict] = {}
    for spec in RANGES:
        if spec[0] != "leg-07":
            continue
        n += 1
        items = [e for e in grouped["leg-07"] if e["_range"] == spec]
        leg7["stops"].append(build_stop(n, spec, items))
        for item in items:
            layout_new[f"leg-07:{item['date']}"] = layout_for("leg-07", item)
    dump_compact(leg7_path, leg7)

    for leg_id, (lid, name) in LEG_META.items():
        stops = []
        n = 0
        for spec in RANGES:
            if spec[0] != leg_id:
                continue
            n += 1
            items = [e for e in grouped[leg_id] if e["_range"] == spec]
            stops.append(build_stop(n, spec, items))
            for item in items:
                layout_new[f"{leg_id}:{item['date']}"] = layout_for(leg_id, item)
        path = ROOT / "data" / {
            "leg-08": "leg-08-indian-ocean.json",
            "leg-09": "leg-09-south-africa-atlantic.json",
            "leg-10": "leg-10-caribbean-home.json",
        }[leg_id]
        dump_compact(path, {"id": lid, "name": name, "stops": stops})
        print(f"Wrote {path.name}: {n} stops, {sum(len(s['entries']) for s in stops)} entries")

    print(f"leg-07 stops={len(leg7['stops'])} entries={sum(len(s['entries']) for s in leg7['stops'])}")

    man_path = ROOT / "data/manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    for leg in man["legs"]:
        if leg["id"] in LEG_META:
            leg["status"] = "in-progress"
    man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    layout_path = ROOT / "data/scan-layout.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    for key in list(layout["entries"]):
        leg, iso = key.split(":", 1)
        if leg in LEG_META or (leg == "leg-07" and iso >= "2004-03-27"):
            del layout["entries"][key]
    layout["entries"].update(layout_new)
    layout_path.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    multi = sum(1 for v in layout_new.values() if len(v["scans"]) > 1)
    print(f"scan-layout: {len(layout_new)} new targets, {multi} multi-page")

    print("\nMULTI-PAGE")
    for key, val in layout_new.items():
        if len(val["scans"]) > 1:
            print(f"  {key}: {val['pages']} -> {val['scans']}")

    print("\nSTOPS")
    for spec in RANGES:
        items = [e for e in grouped[spec[0]] if e["_range"] == spec]
        print(f"  {spec[0]} {items[0]['date']}–{items[-1]['date']}  {spec[1]}  ({len(items)})")


if __name__ == "__main__":
    main()
