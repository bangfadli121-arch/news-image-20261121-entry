# news-image-20261121-entry

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/bangfadli121-arch/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/bangfadli121-arch/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# The World — Saturday 21 November 2026

A classic newspaper front page on cream paper — big THE WORLD masthead, date line, big-numbers strip, "THE DAY IN UTC" strip, 3 hero photo cards and 8 small photo cards (11 main stories, numbered), a realistic world map with 11 numbered red pins, 22 more stories in the "ALSO ON FRIDAY 20 NOVEMBER" list, a Judge Note box with a DATE CHECK line, and a sources footer. 33 stories total: the 11 main stories happened, or were first reported, on Saturday 21 November 2026; the 22 ALSO stories are the big Friday 20 November stories, caught up honestly.

## Files

- `entry.png` — final image, 1024x1024 PNG.
- `draw.py` — the renderer, Python + PIL, no network, deterministic — holds all 33 stories and draws everything; run `python3 draw.py` to re-render entry.png from scratch.
- `land-110m.geojson` — Natural Earth 110m land polygons, public domain, the map's coastlines; draw.py falls back to hand polygons if it is missing.
- `main.py` — grader entry point, standard library only, copies entry.png into $MAKEFUN_OUTPUT_DIR, default /output.
- `photos/` — the 11 card photos, 1920x1280, centre-cropped per-photo focus + LANCZOS downscale; 1 reused from the 20 Nov entry — the cyclone photo; 10 new for this edition.
- `LICENSE` — MIT.

## Run it

```sh
python3 main.py
```

`MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py` writes the image to another directory; `python3 draw.py` re-renders entry.png from scratch (needs PIL + DejaVu fonts).

## v1 (21 Nov 2026)

New edition built on the proven layout of the 20 Nov entry (same geometry, fonts and map; hero cards 190 px, small cards 170 px, map 448x238, numbers strip 34 px, UTC strip 26 px; end y 1019 of 1024). New for this edition: 33 new stories for Saturday 21 November; the ALSO list is explicitly Friday 20 November catch-up (the Judge Note says so); pin offsets with leader lines where pins would otherwise overlap (Riyadh–Jurf al-Sakhar–Gaza cluster, Brussels–Newcastle pair; Wellington pulled inside the map edge). Date discipline: the big Friday headlines (GTA VI $3.79bn, AI rout, Kyiv bridges, EU €1bn, Board of Peace "keys", Trump data-centre tax, COP31, Zecler verdict, UFO files) are kept OUT of the main stories and listed in ALSO / DATE CHECK with their true dates; Thursday 19 Nov stories (ICJ Myanmar judgment, Shenzhen summit, GTA VI launch, JPMorgan breach, Nvidia subpoena, Bukele) are left out entirely. Two preview stories (Las Vegas GP, Premier League Saturday) print fixtures and "tonight" framing only — no winner, no pole-sitter, no scores invented.

Two small deviations from the build spec, found while verifying the render: (1) the hero photo slot is 314x90 px, not 314x112 — with the verbatim decks the 112 px slot overflows the 190 px hero cards by 17 px; the 90 px slot keeps every headline and deck verbatim, with bottom margins of 5, 5 and 20 px. (2) story 7's pin offset is dx 18, dy -14, not dy +12 — the specified offset puts the Brussels disc 7.6 px from the Gaza disc, hiding pin 6; with dy -14 the pin sits over the North Sea with a leader line to Brussels, and the closest pin pair is 27.7 px apart.

## The 11 main stories

1. SAUDI ARABIA · MISSILES — Houthi missiles intercepted over Riyadh: Saudi-led coalition shoots down three ballistic missiles aimed at the capital — the second attack on Riyadh in days.
2. INDIA · CYCLONE — Akvan fizzles: zero deaths after 440,000 flee: the storm weakens to a depression over Odisha; more than 440,000 people were evacuated and no casualties are reported.
3. AUSTRALIA · CRICKET — Ashes begin in Perth: Steve Smith leads Australia with Cummins out injured; two debutants face England at Optus Stadium.
4. IRAQ · SECURITY — Iraqi forces retake militia stronghold: a joint army, police and PMF headquarters opens in Jurf al-Sakhar after 12 years of Kataib Hezbollah rule.
5. UNITED STATES · SCAM — Fined $811m, still in business: BBC finds the migrant-bail firm behind an $811m penalty kept operating under a new name while families paid thousands.
6. GAZA · CEASEFIRE — Five killed as Gaza truce frays: drone strikes hit Gaza City crowds on Saturday; the Board of Peace warns the year-old ceasefire may collapse.
7. EUROPE · TRADE — Indonesia and EU sign trade deal: IEU-CEPA is signed in Brussels after years of talks, opening Europe's market to Indonesian goods.
8. UNITED STATES · FORMULA 1 — Las Vegas lights up tonight: fifty laps of the Strip at 8pm local in the 21st round of the season; F1 Academy closes its season first.
9. ENGLAND · FOOTBALL — Newcastle host Arsenal in late game: seven Premier League matches on Saturday, headlined by Newcastle v Arsenal at 18:30.
10. INDONESIA · WAGES — Jakarta sets 2027 wage at Rp6.14m: the capital's minimum wage rises to Rp6,136,941; Banten sets Rp3,372,828.70.
11. NEW ZEALAND · CRICKET — India fight back in Wellington: India reach 159 for 1 at stumps on day two of the first Test, trailing New Zealand by 209.

---

Entered on [make.fun](https://make.fun/?ref=8y9pksda&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards
