#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

leg6 = json.loads((ROOT / "data/leg-06-fiji-vanuatu.json").read_text(encoding="utf-8"))
leg7 = json.loads((ROOT / "data/leg-07-australia.json").read_text(encoding="utf-8"))
man = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
layout = json.loads((ROOT / "data/scan-layout.json").read_text(encoding="utf-8"))

issues: list[str] = []


def check_leg(leg: dict) -> int:
    ecount = 0
    for s in leg["stops"]:
        for e in s["entries"]:
            ecount += 1
            y, m, d = map(int, e["date"].split("-"))
            dt = date(y, m, d)
            expected = DAY[dt.weekday()]
            if not e["date_display"].startswith(expected):
                issues.append(
                    f"{leg['id']} {e['date']}: date_display={e['date_display']!r} expected {expected}"
                )
            key = f"{leg['id']}:{e['date']}"
            has_scan = "scan" in e
            in_layout = key in layout["entries"]
            if in_layout and has_scan:
                issues.append(f"{key}: has both scan and layout")
            if not in_layout and not has_scan:
                issues.append(f"{key}: missing scan and layout")
    return ecount


e6 = check_leg(leg6)
e7 = check_leg(leg7)
sept1 = leg6["stops"][8]["entries"][0]
assert "also saw Onyx" in sept1["body"]
assert "Goodbye Vanuatu" in leg7["stops"][0]["entries"][0]["body"]
assert "[uncertain: Hans]" in json.dumps(leg6)
assert "[Chip]" in sept1["body"]
assert man["legs"][6]["status"] == "in-progress"
for k in [
    "leg-06:2003-09-01",
    "leg-06:2003-09-04",
    "leg-06:2003-09-29",
    "leg-06:2003-10-05",
    "leg-06:2003-10-11",
    "leg-07:2003-10-29",
    "leg-07:2004-01-05",
    "leg-07:2004-03-24",
]:
    assert k in layout["entries"], k

print("leg-06 stops", len(leg6["stops"]), "entries", e6)
print("leg-07 stops", len(leg7["stops"]), "entries", e7)
print("issues", issues or "none")
print(
    "last leg6",
    leg6["stops"][-1]["entries"][-1]["date"],
    leg6["stops"][-1]["name"],
)
print(
    "first/last leg7",
    leg7["stops"][0]["entries"][0]["date"],
    "...",
    leg7["stops"][-1]["entries"][-1]["date"],
)
if issues:
    raise SystemExit(1)
