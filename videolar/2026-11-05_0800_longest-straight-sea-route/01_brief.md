---
video: 2026-11-05_0800_longest-straight-sea-route
slot: "08:00"
language: en
category: B
mode: REALITY
status: script-ready      # idea → script-ready → visuals-ready → audio-ready → rendered → qc-passed → awaiting-approval → published
narrator: "candidate: Kokoro v0.19 am_michael (Apache-2.0) — awaiting Emir's listening approval"
score: 82.0
---
# The longest straight line you can sail

Workflow test package (Phase 3). English remake of the Turkish draft `2026-11-04_0800_en-uzun-duz-rota` (sources reused, re-checked).

## 1. Topic, category, mode
- Topic: the longest great-circle path over water — Sonmiani (Pakistan) → Karaginsky (Kamchatka), ≈ 32,090 km.
- Audience: global, 16–40, map/geography/"I didn't know that" viewers.
- Why NØVEX: an impossible-sounding fact that is true, shown on a globe (early-NØVEX visual strength).
- REALITY: every claim sourced in `02_sources.md`. The open question (can a ship actually do it?) is asked, not answered.

## 2. Title
**This Line Never Touches Land for 32,000 km** (42 chars) · alt: *The Longest Straight Line You Can Sail*

## 3. Opening hook (0–2 s)
Visual: black space → a single white line shoots across a spinning globe, counter racing to "32,000 km".
Line: "This line runs thirty-two thousand kilometers, and never touches land."

## 4. Narration (`05_narration_en.txt`, 105 words, 44.9 s with candidate voice)
See file. Engagement question at the end: "So, could a real ship sail it without stopping? Yes or no?"

## 5. Scene plan (engine: `motor/kure_v1` globe, $0)
| # | Time (s) | Visual | On-screen text |
|---|---|---|---|
| S1 | 0.0–4.9 | Line shoots across the globe; counter | 32,000 km · NO LAND |
| S2 | 5.3–9.1 | Sonmiani coast at night, ship marker heads west | Pakistan |
| S3 | 9.5–12.2 | Flat Mercator map: route as an S-curve | FLAT MAP |
| S4 | 12.6–15.9 | Map wraps into a globe; camera aligns → the curve becomes a straight line | ON A GLOBE |
| S5 | 16.3–19.0 | Mozambique Channel between Africa and Madagascar | |
| S6 | 19.4–22.6 | Between Tierra del Fuego and Antarctica | |
| S7 | 23.0–25.0 | Fast fly across the Pacific, counter running | |
| S8 | 25.4–29.3 | Arrival: Kamchatka coast | KAMCHATKA · 32,090 km |
| S9 | 29.7–33.2 | Full route on globe + source card | Chabukswar & Mukherjee, 2018 |
| S10 | 33.6–39.7 | Land line Portugal → China in turquoise | 11,241 km ON LAND |
| S11 | 40.1–44.9 | Question card + NØVEX end | YES or NO? |
Production prerequisite: verify with Natural Earth 10 m polygons that the drawn line touches no land (not yet done).

## 6. Generation prompts — none needed (all visuals are code-rendered from public-domain geodata).
## 7. Voiceover — calm, confident documentary tone; slight lift on "never touches land" and the final question; 0.4 s pauses between sentences. Pronunciation: Kamchatka /kæmˈtʃætkə/, Madagascar, Pakistan.
## 8. Music & SFX — synthesized in code (no license needed): low pulse under the line, whoosh on map→globe wrap, wind in the passages, counter ticks, soft impact on arrival. Speech ≥ 12 dB above the bed; −14 LUFS.
## 9. Subtitles — `subtitles_en.srt` (timing exact from the candidate narration; numbers shown as digits).
## 10. Thumbnail — globe with a single glowing white line; text "32,000 km. NO LAND." (1280×720 + 1080×1920).
## 11–12. Description, hashtags → `06_package.md`
## 13. Sources → `02_sources.md`
## 14. Engagement question — end: "Could a real ship sail it without stopping? Yes or no?" (real constraints: Drake Passage weather, ice, fuel).
## 15. QC → `qc/qc_report.md`
## 16. Open issues — narrator approval; land-touch verification; globe engine scenes for this route (kure_v1 needs a route mode); no MP4 yet.
