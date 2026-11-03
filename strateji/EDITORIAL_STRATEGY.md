---
status: active
version: 1.0
adopted: 2026-11-03
source: Emir's "MASTER GLOBAL CONTENT STRATEGY & PRODUCTION DIRECTIVE" (3 Nov 2026)
machine_readable: strateji/kategoriler.json
---
# NØVEX — Editorial Strategy (single source of truth)

**NØVEX — Beyond the Ordinary.** A global discovery and storytelling channel. Not a technology channel.
Every video should make someone stop scrolling, ask a question, discover something, imagine a possibility,
or reconsider what they thought they knew.

## 1. Language
- Default production language: **English** (natural, international, no Turkish-English mix). Titles, scripts, subtitles,
  descriptions, thumbnails, tags: English.
- Internal docs may stay Turkish. Turkish voice identities (Yusuf/Zeynep) are **not** assumed to work in English;
  English narrators must be evaluated separately (pronunciation, pacing, clarity, quality, commercial license).

## 2. Categories (`kategoriler.json` → `categories`)
A History & Ancient Civilizations · B Earth, Nature & the Unknown · C Space & the Universe · D Mysteries & Extraordinary Facts ·
E Science & Humanity · F Technology & the Future · G What If? · H Cinematic Fiction.
Categories are guides, not quotas. New subjects are welcome if they fit "Beyond the Ordinary".

## 3. Editorial modes (every video gets exactly one)
| Mode | Meaning | Hard rules |
|---|---|---|
| **REALITY** | Documented events, credible science, verified history | Research first; every number/claim in `02_sources.md` with a primary or institutional source; no invented quotes, studies, statistics; uncertainty stated as uncertainty |
| **SPECULATION** | Plausible futures, hypotheses, scientific possibilities | Separate known facts from assumptions on screen and in narration ("Scientists know… If… then…"); never imply it happened |
| **FICTION / WHAT IF** | Alternative realities, cinematic stories | Fiction is clear from title/description/narration/on-screen label; never packaged as news; AI visuals never presented as real footage |

What If videos may be SPECULATION (science-grounded, e.g. early NØVEX "Turkey in Antarctica") or FICTION (story-driven, e.g. SON SİNYAL).
The assumption sentence is mandatory ("This is a thought experiment: …").

## 4. Engagement (core requirement)
Structure: hook in 1–2 s → curiosity gap → progressive reveals → one unexpected turn → a **subject-specific** question at a
natural point → payoff → optional closing question. No misleading clickbait, no generic "like & subscribe" lines.
Checklist: `sablonlar/en/ENGAGEMENT_CHECKLIST.md`.

## 5. Cadence
- **4 original Shorts/day**: 08:00 · 12:00 · 16:00 · 20:00 (Europe/Istanbul). Slots are publishing times, **not** fixed categories.
  SON SİNYAL (fiction series) may use a recurring slot if Emir confirms (open decision).
- **1 long-form documentary/week**: Sunday 19:00, 8–12 min, English, separate production (`sablonlar/en/LONGFORM.md`).
- Shorts: 9:16 · 1080×1920 · 30 FPS · usually 35–55 s · strong opening · clear payoff.

## 6. Idea selection
- ≥ 6 candidates per day → best 4, scored on 100 points (`araclar/fikir_puanla.py`):
  hook 15 · global appeal 12 · curiosity 12 · retention 12 · comments 10 · visual producibility 10 · research reliability 12 ·
  originality 10 · repetition (inverted risk) 7.
- Diversity rules: ≥ 1 strong What If candidate per day; max 2 selected from one category; never 4 technology videos.
- Reject: repetitive, weakly researched, misleading, visually dull, too close to recent uploads, off-brand.
- Topic registry: `konu_kaydi.csv` (proposed + published). Scores support decisions; they do not predict virality.

## 7. Visual identity by category (`kategoriler.json` → `visual_styles`)
One brand, many atmospheres: history = grounded and cinematic; space = vast and scientifically informed; mysteries = controlled
suspense; Earth/nature = scale and realism (globe/map engine `motor/kure_v1`); fiction = illustrated character style
(`motor/karakter/STIL_KILAVUZU.md`); technology = modern and credible. Brand constants: NØVEX logo, typography, safe areas,
subtitle style, sound signature.

## 8. Tools and cost
Kling, Higgsfield, GPT Images, ElevenLabs, Descript: use only where they genuinely improve results, after checking availability,
working integration and cost; **explicit approval before any paid generation or subscription**. An adapter or placeholder is not
a working integration. A video is "done" only when a real MP4 exists and passed QC.

## 9. Quality control (no compromise)
Editorial · factual integrity · audio · video · licensing — `sablonlar/en/QC_CHECKLIST.md`. Any check that could not actually be
performed is reported as "not performed".

## 10. Analytics
When Studio data is available (exports from Emir): impressions, CTR, avg view duration, retention, viewed vs swiped away,
completion, rewatches, likes, comments, shares, subscribers, returning viewers. Weekly review; no category is dropped after one video.

## 11. Publishing and approvals
Claude never publishes, schedules or spends. Drafts live in `videolar/`, approved finals are marked in `yayin_kaydi.csv` by Emir.
