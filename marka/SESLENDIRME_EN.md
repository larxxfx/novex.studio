# English narration — evaluation (3 Nov 2026)

Turkish voice identities (Yusuf/Zeynep, `SESLENDIRME.md`) are **not** assumed to work in English. This file tracks English narrator candidates.

## Candidate: Kokoro v0.19 (hexgrad/Kokoro-82M) — free, local, runs in this environment
- **License:** model weights Apache-2.0 (model card on Hugging Face, checked 3 Nov 2026); card states training on
  "permissive/non-copyrighted audio" (<100 h, v0.19). espeak-ng (GPLv3) is a runtime dependency only. Output audio: ours.
- **Runtime:** `sherpa-onnx-offline-tts --kokoro-*` (sherpa-onnx v1.12.15), model from `k2-fsa/sherpa-onnx` release `tts-models/kokoro-en-v0_19`.
- **Cost:** $0. ~22 s CPU time per 37 s of audio (2 threads).

| Voice (sid) | Gender / accent | Duration (105 words) | Whisper WER | Words/s | Median F0 | Pitch range (p5–p95) | Note |
|---|---|---|---|---|---|---|---|
| af_sarah (3) | F · US | 37.7 s | 0.0 % | 2.78 | 188 Hz | 12.9 st | lively, clear |
| af_bella (1) | F · US | 36.2 s | 0.0 % | 2.90 | 200 Hz | 8.8 st | flatter |
| am_michael (6) | M · US | 39.0 s | 1.9 % | 2.69 | 120 Hz | 11.3 st | calm documentary pace |
| am_adam (5) | M · US | 34.5 s | 1.9 % | 3.05 | 121 Hz | 11.7 st | fast |
| bf_emma (7) | F · UK | 36.4 s | partial* | 2.88 | 185 Hz | 7.2 st | flat |
| bm_george (9) | M · UK | 39.3 s | partial* | 2.67 | 143 Hz | 13.8 st | expressive |
\* Whisper skipped the last ~8 s of these takes (measurement tool issue, not the voice); WER on the transcribed part ≈ 0.

**Shortlist:** am_michael (male) and af_sarah (female). **Status: awaiting Emir's listening approval** → only then
`ses/LISANS.txt: yayin_uygun: evet`. Limitations: g2p via espeak-ng can mispronounce rare names → per-video Whisper check.

## Other options (from 3 Nov research)
Google Cloud TTS (Chirp 3 HD / WaveNet en-US): commercial use OK per docs, free quota, **needs billing account** — not tested.
Chatterbox Multilingual v3 (MIT): not runnable here (PyTorch/HF blocked). ElevenLabs free: non-commercial. Descript: no credits.
