#!/usr/bin/env python3
"""One-shot: apply Pg54-Pg69 draft into leg-06 + new leg-07 JSON."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def display(iso: str, include_year: bool = True) -> str:
    y, m, d = map(int, iso.split("-"))
    dt = date(y, m, d)
    month = dt.strftime("%B")
    base = f"{DAY[dt.weekday()]}, {month} {d}"
    return f"{base}, {y}" if include_year else base


def entry(
    iso: str,
    body: str,
    *,
    conditions: str | None = None,
    scan: str | None = None,
    multi: bool = False,
    include_year: bool = True,
) -> dict:
    e = {
        "date": iso,
        "date_display": display(iso, include_year=include_year),
        "body": body.strip(),
        "conditions": conditions,
    }
    if multi:
        pass  # scan-layout supplies paths
    elif scan:
        e["scan"] = scan
    else:
        e["scan"] = f"images/scans/{iso}.jpg"
    return e


def stop(
    n: int,
    name: str,
    passage: str,
    lat: float,
    lng: float,
    entries: list,
    *,
    kind: str | None = None,
) -> dict:
    s = {
        "id": f"stop-{n:02d}",
        "n": n,
        "name": name,
        "passage": passage,
        "lat": lat,
        "lng": lng,
        "photo_album": None,
        "photos": [],
        "entries": entries,
    }
    if kind:
        s["kind"] = kind
    return s


def main() -> None:
    leg6_path = ROOT / "data/leg-06-fiji-vanuatu.json"
    leg6 = json.loads(leg6_path.read_text(encoding="utf-8"))

    # --- Extend Port Vila Sept 1 ---
    vila = leg6["stops"][8]
    assert vila["name"].startswith("Port Vila")
    sept1 = vila["entries"][0]
    assert sept1["date"] == "2003-09-01"
    continuation = (
        "also saw Onyx, Tranquility, Sayo, Gitano, Sojourner. Met a nice older Aussie couple, "
        "Iris & Graham on Time Wise. Brian got quite friendly with Iris and I got [Chip] going "
        "on her XP laptop with USB interface. Thomas enjoyed eating cheap tender steak, we shopped "
        "for DVDs and duty free liquor. No other bargains here — food in the supermarkets costs "
        "twice as much as Fiji. We attended a local play showing the history of Vanuatu. Had a "
        "really good time in general, Brian was happy to see the Desert Rose kids again. But it's "
        "a city, so Saturday, after we got our Australian visas (what a hassle — my last name, "
        "Brian's new passport, they were confused by the situation but finally gave in as we had "
        "all important documentation) we moved, with Desert Rose and Time Wise to Mele Bay 5 miles "
        "away. There we decided with Fidelio & Alderan to do an overnighter to Epi. Ian is usually "
        "good with the weather. He predicted a restful night, but that was not the case. We flew "
        "north in 20–25 knots SE on the beam, had to keep shortening sail to slow the boat down. "
        "Dawn found us 6 miles from Lamen Bay, and the wind died then turned NE. We were happy to "
        "get the hook down, not much rest last night. There is a resident dugong in the Bay and "
        "lots of loggerhead turtles."
    )
    if "also saw Onyx" not in sept1["body"]:
        sept1["body"] = sept1["body"].rstrip() + " " + continuation
    sept1["date_display"] = display("2003-09-01")
    # multi-page: drop flat scan; layout will supply a/b
    sept1.pop("scan", None)
    sept1["conditions"] = (
        "Anchored Port Vila near quarantine buoy; later Mele Bay, then overnight to Lamen Bay, Epi. "
        "Wind: SE 20–25 on the beam, then died / NE at dawn."
    )

    # Remove any previously appended Vanuatu stops beyond Vila (idempotent re-run)
    leg6["stops"] = [s for s in leg6["stops"] if s["n"] <= 9]

    leg6["stops"].extend(
        [
            stop(
                10,
                "Lamen Bay, Awei & Crab Bay",
                "Vanuatu",
                -16.58,
                168.16,
                [
                    entry(
                        "2003-09-04",
                        "Bunches of boats in Lamen Bay that we have met before — Fidelio, Time Wise, "
                        "Irish Alderan, some others. We swam with the dugong and got to pet him and "
                        "ride on him (kind of!) Had a birthday dinner with Time Wise. Thomas and Brian "
                        "gave me some beautiful earrings made of red coral and mother of pearl. Thomas "
                        "was just recovering from a stomach bug, then Brian & I got it on Wednesday. I "
                        "was awfully sick. What a 50th birthday — I will not forget it. Had to spend "
                        "the day at anchor until we recovered. We are feeling better today, light wind, "
                        "so we set sail for the Maskelyne Islands off the coast of Malekula. Before we "
                        "got there we had head winds! Pulled into a very nice snug little anchorage at "
                        "Awei Island, home of the magic weather stones — pieces of quartz that give off "
                        "blue sparks when you strike them together, and cause thunder storms. It is "
                        "very calm and peaceful here, surrounded by mangroves, tiny sand beaches, shy "
                        "natives paddling beautiful dugout canoes with proas. It is easy to trade old "
                        "clothes for fruit.",
                        conditions="Lamen Bay, Epi; later Awei Island, Maskelyne Islands. Light wind after illness.",
                        multi=True,
                    ),
                    entry(
                        "2003-09-06",
                        "Quiet day on Awei anchorage yesterday. We launched the dinghy in late afternoon "
                        "and looked for the magic quartz rocks on the beach. We found a number of "
                        "interesting, reddish & blueish quartz stones, some green stones, some white "
                        "quartz. Had to order Brian not to strike them together! Left today originally "
                        "for Ambrym, but the wind was easterly and it was a bit of a beat. After much "
                        "indecision, we set course for Crab Bay on Malekula, and down wind. Brian and I "
                        "are both still feeling a bit under. Great sail in 20 knots along the coast. "
                        "The volcano at Ambrym was spitting clouds of smoke & dust. Entered a nice "
                        "little cove with a beautiful long sandy beach. I'll rest here for a day!",
                        conditions="Wind: easterly beat toward Ambrym abandoned; downwind to Crab Bay, Malekula, ~20 knots.",
                    ),
                    entry(
                        "2003-09-08",
                        "Met some nice kiwis in Crab Bay — they actually came over to visit! Took a "
                        "walk on the long sand beach, I saw a lion fish snorkeling in the shallows. "
                        "I'm a bit nervous about swimming in Vanuatu — too many stories of tiger shark "
                        "attacks! 40 miles to go today to Santo today and we are drifting in light "
                        "winds, slowly heading north. It is peaceful out there at least! The air is "
                        "very hazy, can barely see any other islands.",
                        conditions="Departing Crab Bay for Santo; light winds, drifting north. ~40 miles.",
                    ),
                ],
            ),
            stop(
                11,
                "Luganville & the Banks Islands",
                "Vanuatu",
                -15.51,
                167.18,
                [
                    entry(
                        "2003-09-12",
                        "Just a few quick days in Luganville. Nice anchorage off the beach by the Beach "
                        "Front Resort, nice Aussie folks running it. I finally saw a doctor and he said "
                        "I have dengue fever. It explains my fatigue over the past month! Lucky I am "
                        "almost over it, just need to be careful, take it easy, not get bitten by a "
                        "mosquito! Thomas scuba dove the President Coolidge, an intact WWII wreck in "
                        "120 feet of water. He liked it, but it was very dark down there! Left town "
                        "yesterday morning to do an overnighter to Waterfall Bay, Vanua Lava, Banks "
                        "Islands, where a festival is being held. Great sailing day, wind a bit light "
                        "from the SE, broad reaching at 4½ knots. Wind turned twice during the night "
                        "to NE, picked up, then died. Anchored by 9 am in Waterfall Bay — incredibly "
                        "beautiful spot! There are 2 waterfalls cascading down the cliff side. The "
                        "local villagers are so happy to see us! Our t-shirt stash will go fast here.\n\n"
                        "Saw Yelo with Rolf & Daniella again in Santo, saw Mangwana (the Mongols) again, "
                        "met Fay & Ingrid on Moon Penny.",
                        conditions="Luganville then overnight to Waterfall Bay, Vanua Lava. Wind: light SE, 4½ knots; NE overnight.",
                    ),
                    entry(
                        "2003-09-18",
                        "Had a great time at the festival in Waterfall Bay. The winds were light while "
                        "we were there, the weather hot & sunny, 15 boats showed up. Yelo came, we "
                        "spent a lot of time with them. Met Ophelia, [uncertain: Hans], Eva and little Lola. "
                        "Thomas took lots of great pictures. Jimmy, a local, invited us to a meal at "
                        "his house — sweet potato laplap was surprisingly good, fresh water prawns "
                        "cooked with green onions, and cassava. They build beautiful huts from palm "
                        "and bamboo with woven walls in different designs, palm thatch roofs, little "
                        "windows covered with pieces of bamboo. Very airy and comfortable! On the "
                        "floor they put coral rubble to keep the sand down. Jimmy had a hand made "
                        "table and benches, woven mats on the floor. His entire family sat on the "
                        "floor and watched us while we ate.\n\n"
                        "The festival was a lot of fun, very intimate with only a few locals. [uncertain: Henaki] "
                        "was inaugurated as the first blood chief in 90 years. They killed a pig — "
                        "quite humanely by poisoning it with an arrow before beating it to death. All "
                        "the members of his extended family were anointed with pig blood on the "
                        "temples. Lots of dancing and singing. The men & women all wore grass skirts. "
                        "The snake dance with the men painted to look like black & white coral snakes "
                        "was cool. The 2nd day they prepared a traditional feast using all old "
                        "methods, scraping coconut with clam shells, cooking prawns and fish in pieces "
                        "of hollow bamboo on hot stones. They ground fresh kava root with a piece of "
                        "coral. Their kava bowls were made from plastic fishing floats — not exactly "
                        "traditional! The last day we climbed to the top of the waterfall and heard "
                        "the women making water music with their hands and arms. None of the white "
                        "women could do it! It was all very interesting, but we were exhausted from "
                        "being on shore all day. Sailed to the Reef Islands today.",
                        conditions="Waterfall Bay festival, Vanua Lava; light winds, hot & sunny. Sailed to the Reef Islands.",
                    ),
                    entry(
                        "2003-09-26",
                        "We left the Reef Islands with regret, were tired of the constant wind blowing "
                        "25 knots. It was beautiful there, white powdery sand beach on the island, "
                        "crystal clear water. Unfortunately the anchorage was exposed, behind the "
                        "reef, and the island was a half-mile dingy ride away. Had a great time "
                        "windsurfing, Brian graduated to my rig, and was very good. Namirda was "
                        "there, Niel & Greta are good wind surfers. Mangwana came in and the boys "
                        "were kite surfing. We spent most afternoons on the beach hanging out with "
                        "the other cruisers, enjoying the beach, getting out of the strong wind. Fast "
                        "windy passage down to Waterfall Bay today, fill up on water, get some fresh "
                        "fruit.",
                        conditions="Reef Islands; wind 25 knots. Fast windy return to Waterfall Bay.",
                    ),
                    entry(
                        "2003-09-27",
                        "Too much politics in Waterfall Bay, the chiefs are arguing with each other, "
                        "but we did get bananas, papayas, grapefruit and pumpkin from both of them. "
                        "Had dinner with Kerely last night. It is very windy today, we are hard on "
                        "it, bashing down to Gaua, no fun at all! But Charlotte is doing great, going "
                        "high to windward, 5 knots average in 25 knots of wind. Four other boats "
                        "heading to the same anchorage.",
                        conditions="Waterfall Bay to Gaua. Wind: 25 knots, hard on it; 5 knots average.",
                    ),
                    entry(
                        "2003-09-29",
                        "Much more pleasant sailing today! The village at Gaua was very poor, but I "
                        "did score a nice carving there. We took an extremely strenuous hike to the "
                        "lakes in the middle of the island with Namirda, 7 hours of hiking total. We "
                        "barely made it back, the boys got us some coconuts that rejuvenated us. We "
                        "were the big attraction in the village. The hike through the jungle was "
                        "interesting, no birds, no wildlife, lots of vines to trip over, We passed "
                        "steaming mud pools. The lake itself was quite hot along the edges and the "
                        "water was shallow and warm. We rested for an hour on the hot stones along "
                        "the shoreline and enjoyed the solitude. The walk back was a nightmare, "
                        "everyone was sore. Got a cool carving from the village.\n\n"
                        "Today there are 3 other boats out here, Namirda, Alderan and Flight of Time, "
                        "all going to Santo. The winds are much lighter, we are close reaching, quite "
                        "pleasant for a change.",
                        conditions="Gaua crater-lakes hike; then sailing toward Santo. Winds lighter, close reaching.",
                        multi=True,
                    ),
                ],
            ),
            stop(
                12,
                "Port Olry, Santo & Ambae",
                "Vanuatu",
                -15.05,
                167.07,
                [
                    entry(
                        "2003-10-02",
                        "Really enjoyed Port Orly. The island we anchored behind was deserted, with a "
                        "fresh water lake for swimming and laundry. It was pretty and peaceful there. "
                        "Good swimming, nice beach. Had dinner on Alderan and invited them over for a "
                        "movie. Today we are going somewhere, weren't sure, depended on how the wind "
                        "blew. Ended up in Peterson Bay, met Namirda, Pacific Bliss (another cat like "
                        "Yelo) with Gunther & Lois aboard, and Fidelio. Caught a large mahi which we "
                        "shared with our friends in return for cold beers — good trade! Nice "
                        "anchorage behind the reef here.",
                        conditions="Port Olry (written Port Orly) then Peterson Bay, Santo.",
                    ),
                    entry(
                        "2003-10-03",
                        "Decided to run to Loganville this afternoon, hit the stores and the market "
                        "tomorrow morning for supplies. Had a nice sail around the corner and all the "
                        "way to the anchorage. Lots of boats in Loganville.",
                        conditions="Peterson Bay to Luganville (written Loganville).",
                    ),
                    entry(
                        "2003-10-05",
                        "Wanted to head over to Ambae this morning for the festival at Lolowai, but "
                        "the wind is nonexistent. Instead, we stopped with Alderan at Million Dollar "
                        "Point and had a great snorkel. US dumped a lot of their leftover stuff in "
                        "the ocean here rather than leave it to the islanders. There were numerous "
                        "ships, pieces of jeeps, a fork lift, all covered with coral. It was a fun "
                        "dive. Then we continued around the corner and anchored in Palikulo Bay. Time "
                        "Wise was there, we enjoyed a potluck dinner together.",
                        conditions="Million Dollar Point snorkel; anchored Palikulo Bay. Wind nonexistent for Ambae.",
                        multi=True,
                    ),
                    entry(
                        "2003-10-06",
                        "Boisterous sail to Ambae today! We are out here with 3 other boats, Charlotte "
                        "is keeping up in speed and pointing to windward. It is an awful rough slog, "
                        "gusts to 30 knots, burying the bow to the mast at times, way overpowered "
                        "with the reefed genoa. But we make it, averaging 5 knots! The anchorage at "
                        "Lolowai is cute, surrounded on 3 sides by rock cliffs, with a narrow shallow "
                        "entrance. We meet Explorer here with Bob & Hella, hadn't seen them since the "
                        "Galapagos. Tevaki Nui is here with their 8-year-old girl, Brian is not "
                        "thrilled unfortunately.",
                        conditions="Santo to Lolowai, Ambae. Gusts to 30 knots; averaging 5 knots.",
                    ),
                    entry(
                        "2003-10-11",
                        "Loved the festival — it was a 20-minute truck ride up in the hills in a big "
                        "grassy meadow surrounded by huge banyan and mango trees. The dancing was "
                        "very colorful and quite powerful at times. The dancers here wear colored "
                        "mats — a diaper for the men, 2 wraps for the women — skirt & bodice. Lots of "
                        "chiefs dressed in full regalia, dancing to show their approval of the "
                        "presentations. 15 or more boats here, including Tranquility with Rick & Mary, "
                        "Silverfin with Carl & Kathleen, others. It is a good time. It's nice to get "
                        "away from the ocean and hang out in a cool green spot all day. We picked up "
                        "some really different baskets, a chief staff for Brian with a spear point "
                        "tip. We liked the peace and enclosedness of the anchorage and the snorkeling, "
                        "but decided to move over to Maewo today, 8 miles to an anchorage that I "
                        "heard was nice. Easy sail for a change, but that's because it's so early in "
                        "the morning, before the trades pick up. We are at Narovorovo or something "
                        "like that and the locals are listening to loud reggae music at 9 am!",
                        conditions="Lolowai festival, Ambae; then 8 miles to Narovorovo, Maewo.",
                        multi=True,
                    ),
                ],
            ),
            stop(
                13,
                "Maewo — Narovorovo & Asanvari",
                "Vanuatu",
                -15.38,
                168.12,
                [
                    entry(
                        "2003-10-14",
                        "Had a great time in Narovorovo — what a tongue twister!) Met the Peace Corps "
                        "worker, Jamie, and his girlfriend Valerie, fixed his XP laptop that was "
                        "crashed. He took us to the waterfall, along with Kathleen & Carl on "
                        "Silverfin, very hot walk. I did my laundry at the village spigot, got to "
                        "meet the shy but friendly villagers. We were only the 4th boat to stop "
                        "there. It was a pleasant interlude. This morning we punched down to "
                        "Asanvari, where there is a 'Yacht Club' hosted by Chief Nelson. Really glad "
                        "we came to Maewo!",
                        conditions="Narovorovo to Asanvari, Maewo.",
                    ),
                    entry(
                        "2003-10-16",
                        "Asanvari had a picture-perfect village and a nice view of the channel across "
                        "to Pentecost, but it was too nice, they are too used to having cruisers "
                        "there. We did trade for some more baskets, now we have lots of presents! "
                        "Took a great snorkel in clear water, saw big groupers and a family of eagle "
                        "rays. I did my laundry at the waterfall, very convenient! Today we left at "
                        "4am, hoping for a good wind to blow us the [illegible] miles to Luganville. "
                        "Instead, we got barely 10 knots, a slow but pleasant trip, made it in 13 "
                        "hours, right to the anchorage. We are next to Alderan again!",
                        conditions="Asanvari to Luganville in 13 hours. Wind: barely 10 knots.",
                    ),
                ],
            ),
        ]
    )

    leg6_path.write_text(
        json.dumps(leg6, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("Updated", leg6_path.name, "stops=", len(leg6["stops"]))

    # --- leg-07 Australia ---
    leg7 = {
        "id": "leg-07",
        "name": "Australia",
        "stops": [
            stop(
                1,
                "Vanuatu–Australia Passage",
                "Crossing to Australia",
                -18.0,
                160.0,
                [
                    entry(
                        "2003-10-29",
                        "Got stuck in Loganville for the weekend — the weather was awful — it blew & "
                        "rained on Saturday, then rained all Sunday. The Rally hype was intense — all "
                        "these boaters talking themselves into going to sea. Talked to Tranquility & "
                        "Silverfin Monday morning — they were in Peterson Bay so we went up there. "
                        "There we finally met Indulgence II with Mike, Elke and Ben; also Julia with "
                        "Larry & Ken; and Overproof with Virginia & Derek. We had seen these boats "
                        "since Fiji!\n\n"
                        "Brian was happy to hang out with Ben, or Larry from Julia, those guys are "
                        "big boys! We had a wonderful time there, dinghying to the Blue Hole, diving "
                        "the crashed airplane on the reef, partying with the other boats. Just before "
                        "they were planning to leave for Australia last Thursday, Ben was jumping off "
                        "our spreaders with Brian, slipped, and fell on the life lines, gashed his "
                        "head on the toerail. He looked pretty beat up at first. Got an ambulance and "
                        "got him to the hospital. Luckily, he only needed some stitches in his "
                        "forehead. He was back the next day, feeling fine. So, we stayed too, spent "
                        "a lot of time with Indulgence & Julia.\n\n"
                        "Finally got out of Peterson Bay on Monday, went down to Palikulo Bay. Had a "
                        "blast exploring the freighter beached there, swimming in the clear water. "
                        "Hung out with Carl & Kathleen on Silverfin for the day. Hated to leave! "
                        "But it is time to go on now — 2 weeks of light winds ahead and Chesterfield "
                        "Reef beckoned. We have 10–12 knots of wind from the SE, we are still sailing "
                        "along the south coast of Espiritu Santo. Goodbye Vanuatu — it has been a "
                        "memorable two months!",
                        conditions="Departed Luganville / Palikulo for Australia via Chesterfield. Wind: SE 10–12 knots.",
                        multi=True,
                    ),
                    entry(
                        "2003-10-30",
                        "Well it could be worse! Last night was peaceful after we poled out the "
                        "genoa, moving at 4½ knots, wind backed to the east. This morning the wind "
                        "almost died completely, we were bouncing along at 1½ knots for a while. Not "
                        "thrilling, but better than nothing. The wind came back this afternoon, 8–10 "
                        "knots and we are moving smoothly at 5 knots with four sails up. Nice "
                        "sailing! We expected very light winds for this trip, want to get to "
                        "Chesterfield and enjoy a few calm days there before the last leg back to a "
                        "continent.",
                        conditions="Wind: east then light, later 8–10 knots; 5 knots with four sails. 24-hour run — 105 miles.",
                    ),
                    entry(
                        "2003-10-31",
                        "Beautiful night last night, charging along up to 6 knots at times with 4 "
                        "sails up, following the path made by the extremely bright crescent moon. It "
                        "was quite comfortable — we are all enjoying this sail. Talked to Indulgence "
                        "& Julia this morning. Lost a big fish along with the lure, Thomas is hungry "
                        "for something different. He ate enough oysters and coconut crabs in "
                        "Peterson Bay!",
                        conditions="Up to 6 knots with 4 sails. 24-hour run — 115 miles.",
                    ),
                    entry(
                        "2003-11-01",
                        "Another nice night, but sunrise brought light winds. It was hot, progress "
                        "slow, boat didn't steer well. Finally got a bit more wind late in afternoon. "
                        "Caught a huge mahi just after sunrise.",
                        conditions="Light winds after sunrise. 24-hour run — 117 miles.",
                    ),
                    entry(
                        "2003-11-02",
                        "Not a very exciting day — been almost becalmed most of it. Trying to get the "
                        "boat going again now, before sunset. Morale is good, however!\n\n"
                        "Oh — had some hitch hikers last night! A tired booby landed on the mizzen "
                        "boom just after sunset. He was no problem — his ass was hanging over the "
                        "water, but then his buddies landed on the spreaders and all of a sudden "
                        "there was bird shit all over the place. Thomas chased them off, but the "
                        "first one stayed until sunrise.",
                        conditions="Almost becalmed. 24-hour run — 85 miles.",
                    ),
                    entry(
                        "2003-11-03",
                        "Today is flat calm, oily sea, totally hazy gray horizon, no visibility. We "
                        "play with the sails and then get tired of it. Very hot, good day to do "
                        "laundry!",
                        conditions="Flat calm. 24-hour run — 56 miles.",
                    ),
                    entry(
                        "2003-11-04",
                        "Wind came back late yesterday afternoon with a bang! Within an hour we had "
                        "the main down, mizzen reefed, furled genoa. It blew like stink all night — "
                        "30–35 knots from the south. It was relatively calm north of Chesterfield "
                        "Reef, which we passed in the middle of the night. No stopping at uncharted "
                        "reefs in this weather! Finally switched to staysail to try to slow the boat "
                        "down. Overproof and Indulgence II got nailed too, after us. Very "
                        "uncomfortable ride — food flying all over the place. Being becalmed sounds "
                        "good now! Will head to Frederick Reef now and stop there.",
                        conditions="Wind: S 30–35 knots; passed Chesterfield Reef at night. 24-hour run — 135 miles.",
                    ),
                    entry(
                        "2003-11-05",
                        "Today has been an exhilarating day — blue sky, big waves, lots of whitecaps. "
                        "30 knots of wind. Keep trying to slow the boat down, it is impossible. "
                        "Running 5½–6 under staysail only. Not so uncomfortable as yesterday. It is "
                        "possible to stand on deck without getting wet. We will be at Frederick Cay "
                        "Reef before sunrise tomorrow. Looking forward to peaceful anchorage in "
                        "clear blue water, a sandy beach.",
                        conditions="Wind: 30 knots; 5½–6 under staysail. Bound Frederick Reef. 24-hour run — 145 miles.",
                    ),
                    entry(
                        "2003-11-08",
                        "Arrived at Frederick Reef Thurs at sunrise, anchored just before the Namba "
                        "Net at 8 am. Not exactly a calm anchorage! The boat pitched and rolled, too "
                        "rough to get off or swim, still blowing 20+. We had reduced to bare poles "
                        "before sunrise and were still doing 3–4 knots. Indulgence II arrived at "
                        "10pm, rather frazzled from navigating into the reef in the dark. Had a fun "
                        "day yesterday — hanging out on the coral rubble hump that stuck out of the "
                        "sea at high tide, then had beers and dinner on Indulgence. Figured out a "
                        "new way to hoist the dinghy aboard last night, with the staysail halyard. "
                        "Left at 7 this morning, 15–20 SE wind, hard on it heading 195° to "
                        "Bundaberg. It's a beautiful day; just wish the wind was more easterly. As "
                        "long as it stays where it is and we can hold the course, no problem.",
                        conditions="Frederick Reef layover; departed for Bundaberg. Wind: SE 15–20, hard on it, course 195°.",
                    ),
                    entry(
                        "2003-11-09",
                        "What a nice night, full moon, light winds, calm seas, very comfortable. We "
                        "made lots of southing, can just hold our course today. Were doing 7 knots "
                        "for awhile! Hope the wind holds & doesn't turn more south.",
                        conditions="Light winds; up to 7 knots. 24-hour run — 140 miles.",
                    ),
                ],
                kind="passage",
            ),
            stop(
                2,
                "Bundaberg, Fraser Island & Tin Can Bay",
                "Queensland — Southbound",
                -24.87,
                152.35,
                [
                    entry(
                        "2003-11-24",
                        "We arrived in Bundaberg Monday morning at sunrise, had to slow down some "
                        "once we passed the reef. There were 20 boats ahead of us awaiting checkin! "
                        "Got through by 4pm, piece of cake. Relaxed with Indulgence II. Bundaberg "
                        "river entrance was not particularly thrilling — very flat, ugly gray water, "
                        "poisonous sea snakes. We went up river to the town with Virginia on "
                        "Overproof for a few days, to do some shopping. Bundaberg was neat and "
                        "clean, everything available. The men walk around in Crocodile Dundee "
                        "outfits, and the women are scantily dressed. Very redneck. Spent a couple "
                        "more days at the mouth of the river, until Julia with Ken & Larry showed "
                        "up. Left Mon the 17th for Fraser Island — what a great spot! It was "
                        "paradise there — miles of white sand beaches, crystal clear water, birds. "
                        "But the wind turned NW and we had to get out. Too bad — it would have been "
                        "perfect for windsurfing in the lagoon. Spent the next few days traveling "
                        "south in the Great Sandy Straits. Great sailing in flat water, but the NW "
                        "winds made anchoring uncomfortable. Finally found some protection in "
                        "Gary's Anchorage. Came down to Tin Can Bay yesterday, just before the wind "
                        "turned south again. Anchored in the river here, quite a way from town, but "
                        "it's peaceful. Lots of sand bars, sleepy little town. Overproof is here, "
                        "mostly Aussie boats. Will be stuck until wind turns NE again.\n\n"
                        "Bundaberg highlights: nasty thick gray sea snakes, 1000's of bats flying "
                        "across the river at sunset. Yucky water!",
                        conditions="Arrived Bundaberg; later Fraser Island, Great Sandy Strait, Garry's Anchorage (written Gary's), Tin Can Bay. Wind: NW then south.",
                    ),
                    entry(
                        "2003-12-01",
                        "Enjoyed our week in Tin Can Bay — we met Virginia on Overproof there and "
                        "she arranged a trip to a National Forest and a hike to Lake Boona with some "
                        "friends of hers. It was beautiful — huge old Kauri trees towering out of "
                        "sight, thousands of birds. I had a refreshing swim in the fresh water lake. "
                        "Tin Can Bay was very quiet, but people were friendly, and internet at the "
                        "library was free. The dinghy ride was a bit long and wet. Mostly only "
                        "Australian boats around. We spent one day at Inskip Point, and walked part "
                        "of the endless windward beach. Today we left at 4:30 to sail down to "
                        "Mooloolaba, 60 miles. Not a lot of wind in the morning, but it picked up to "
                        "15 in the afternoon. The bar crossing to offshore was crazy — 20 boats next "
                        "to each other, motoring through 6ft swells, trying to get out. What a zoo! "
                        "But of course eventually they all passed Charlotte. We got in and were "
                        "anchored by 4, found a nice hole to sit in. Very suburban here — fancy huge "
                        "holiday houses along the waterfront.",
                        conditions="Tin Can Bay via Inskip Point to Mooloolaba, 60 miles. Wind light then 15; rough bar exit.",
                    ),
                ],
            ),
            stop(
                3,
                "Mooloolaba & Moreton Bay",
                "Queensland — Southbound",
                -26.68,
                153.12,
                [
                    entry(
                        "2004-01-05",
                        "A month went by quickly in Mooloolaba! I guess we were comfortable there. "
                        "It took a while to get used to the scene, but we enjoyed afternoons on the "
                        "beach, with Brian on his boogie board. He really got into it! Suleika with "
                        "Martin, Katherine and 8-yr-old [illegible], showed up, so we decided to "
                        "spend Christmas with them. It was a fun day, spent time on the beach as "
                        "usual. Brian drove us crazy wanting things. Got into exercising every "
                        "morning, running, working out at an exercise site. Silent Runner came "
                        "through a few days before Christmas, also Tranquility. We went to the "
                        "Australia Zoo and saw crocodiles, kangaroos, and koalas, also many snakes, "
                        "poisonous & pythons. We saw the last Lord of the Rings movie. Got used to "
                        "the yuppie-tourist atmosphere but then the water cops came around and "
                        "bugged us to move on. Indulgence & Julia arrived, but they were "
                        "disappointing — too involved in each other. It was a fun month, but time "
                        "to move on. Today winds are light and we took all day to get 40 miles "
                        "south to Tangalooma, on Moreton Island. We saw Desert Rose sailing north "
                        "to Mooloolaba — what a shame to miss them by a day!",
                        conditions="After ~1 month at Mooloolaba; sailed ~40 miles to Tangalooma, Moreton Island. Light winds.",
                        multi=True,
                    ),
                    entry(
                        "2004-01-06",
                        "After a morning of school work, we decided to move on as the anchorage was "
                        "getting rolly. Today is great sailing — downwind with the genoa poled out. "
                        "Only 20 miles to Peel Island where we will wait out the NW flow. We meet "
                        "up with Virginia on Overproof here — lots of boats, but it is a big bay, "
                        "long sandy beach. Thomas is trying windsurfing here.\n\n"
                        "p.s. — New Years Eve in Mooloolaba was fantastic — lots of fireworks on "
                        "the beach, some in a boat out on the water. It was a sight with the lights "
                        "on the crashing surf, fireworks shooting into the waves. The Australians "
                        "worked very hard at getting drunk, what a scene.",
                        conditions="Tangalooma to Peel Island, ~20 miles. Downwind, genoa poled out; waiting out NW flow.",
                    ),
                ],
            ),
            stop(
                4,
                "Southport & the Spit",
                "Queensland — Southbound",
                -27.95,
                153.43,
                [
                    entry(
                        "2004-03-24",
                        "Lots of catching up to do! We arrived at the Spit in Southport on Sun Jan "
                        "11, after a fun weekend at Dux anchorage, on northern South Stradbroke, "
                        "where we met members of the Southport Yacht Club. Saw lots of wallabies "
                        "there, beautiful beach with perfect sand dunes. We were appalled when we "
                        "first dropped the hook in Southport, high rise buildings dotting the "
                        "skyline. But the Spit was very pretty, with the beach right next to the "
                        "boat and the ocean not far away. And there were kid boats!\n\n"
                        "We really enjoyed Manuhiri, a Kiwi ferro boat with Shawn, Angie and their "
                        "kids Alex, Rory, and Nikki. Brian became special buddies with all 3 of "
                        "them. Silent Sound, Canadian with Ray, Stella, boys Bradley & Harry, "
                        "stayed for a month. Brian and Bradley became quite good friends and made "
                        "up a game together.\n\n"
                        "Then there were the Aussie boats. La Passorala with Les, Colleen, Jordan "
                        "& Amy. Keemar III with Bruce, Robin, Jackson & Ryan, 2 big goofy boys that "
                        "Brian had a lot of fun with. The kids had fires on the beach at night and "
                        "had a life of their own. I enjoyed watching Brian interact — he has good "
                        "people skills. Thomas did a lot of wind surfing — figured out water starts "
                        "and jibes in the flat water behind the sandbars. We enjoyed friendship, "
                        "happy hours on the beach, lots of swimming & beach walks. Found a small "
                        "python, called a carpet snake, on the path down to the beach — he would "
                        "come out at evening, just before sundown. Rick & Mary on Tranquility "
                        "pulled in and stayed.\n\n"
                        "It was hard to leave — we felt part of a community for a change. After "
                        "much agonizing about what to do with our lives, we decided to sail "
                        "directly back to the U.S., unless plans change of course! So, it is time "
                        "to move on and we are on our way back to Mooloolaba, to take care of some "
                        "things, provision, and then on to the Great Barrier Reef. We have enjoyed "
                        "the fantastic weather, sand and surf of Australia, and Aussie English "
                        "sounds normal to us now!",
                        conditions="Catch-up entry: Southport Spit stay from mid-January; departing north toward Mooloolaba / GBR.",
                        multi=True,
                    ),
                ],
            ),
        ],
    }

    leg7_path = ROOT / "data/leg-07-australia.json"
    leg7_path.write_text(
        json.dumps(leg7, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("Wrote", leg7_path.name, "stops=", len(leg7["stops"]))

    # --- manifest ---
    man_path = ROOT / "data/manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    for leg in man["legs"]:
        if leg["id"] == "leg-07":
            leg["status"] = "in-progress"
            leg["file"] = "leg-07-australia.json"
    man_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Manifest: leg-07 -> in-progress")

    # --- scan-layout ---
    layout_path = ROOT / "data/scan-layout.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    splits = {
        "leg-06:2003-09-01": {
            "scans": ["images/scans/2003-09-01a.jpg", "images/scans/2003-09-01b.jpg"],
            "pages": ["Pg39-Pg53_p15.jpg", "Pg54-Pg69_p01.jpg"],
            "note": "Starts on log p53, continues on p54",
        },
        "leg-06:2003-09-04": {
            "scans": ["images/scans/2003-09-04a.jpg", "images/scans/2003-09-04b.jpg"],
            "pages": ["Pg54-Pg69_p01.jpg", "Pg54-Pg69_p02.jpg"],
            "note": "Starts on log p54, continues on p55",
        },
        "leg-06:2003-09-29": {
            "scans": ["images/scans/2003-09-29a.jpg", "images/scans/2003-09-29b.jpg"],
            "pages": ["Pg54-Pg69_p05.jpg", "Pg54-Pg69_p06.jpg"],
            "note": "Starts on log p58, continues on p59",
        },
        "leg-06:2003-10-05": {
            "scans": ["images/scans/2003-10-05a.jpg", "images/scans/2003-10-05b.jpg"],
            "pages": ["Pg54-Pg69_p06.jpg", "Pg54-Pg69_p07.jpg"],
            "note": "Starts on log p59, continues on p60",
        },
        "leg-06:2003-10-11": {
            "scans": ["images/scans/2003-10-11a.jpg", "images/scans/2003-10-11b.jpg"],
            "pages": ["Pg54-Pg69_p07.jpg", "Pg54-Pg69_p08.jpg"],
            "note": "Starts on log p60, continues on p61",
        },
        "leg-07:2003-10-29": {
            "scans": ["images/scans/2003-10-29a.jpg", "images/scans/2003-10-29b.jpg"],
            "pages": ["Pg54-Pg69_p09.jpg", "Pg54-Pg69_p10.jpg"],
            "note": "Starts on log p62, continues on p63",
        },
        "leg-07:2004-01-05": {
            "scans": ["images/scans/2004-01-05a.jpg", "images/scans/2004-01-05b.jpg"],
            "pages": ["Pg54-Pg69_p14.jpg", "Pg54-Pg69_p15.jpg"],
            "note": "Starts on log p67, continues on p68",
        },
        "leg-07:2004-03-24": {
            "scans": ["images/scans/2004-03-24a.jpg", "images/scans/2004-03-24b.jpg"],
            "pages": ["Pg54-Pg69_p15.jpg", "Pg54-Pg69_p16.jpg"],
            "note": "Starts on log p68, continues on p69",
        },
    }
    layout["entries"].update(splits)
    layout_path.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("scan-layout: added", len(splits), "splits")

    # counts
    e6 = sum(len(s["entries"]) for s in leg6["stops"])
    e7 = sum(len(s["entries"]) for s in leg7["stops"])
    print(f"leg-06 entries={e6} stops={len(leg6['stops'])}")
    print(f"leg-07 entries={e7} stops={len(leg7['stops'])}")


if __name__ == "__main__":
    main()
