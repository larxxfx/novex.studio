# QC checklist — mark each ✅ / ❌ / NOT PERFORMED (never leave blank)

## Editorial
- [ ] Fits "Beyond the Ordinary" · interesting to a global audience · opening strong · story coherent · ending satisfying · question natural
## Factual integrity
- [ ] Important claims verified (`02_sources.md`) · sources credible · speculation identified · fiction distinguishable · AI visuals represented honestly
## Audio (automatic: `araclar/hizala.py --whisper`, `araclar/qc.py`)
- [ ] Narration clear · English pronunciation natural (listen) · pacing · music balanced (speech ≥ 12 dB above bed) · SFX fit · no clipping / sync issues · −14 LUFS, TP ≤ −1 dBTP
## Video (automatic: `araclar/qc.py`)
- [ ] 1080×1920 (long-form 1920×1080) · 30 FPS · duration · no black/frozen frames · clean transitions · subtitles readable and timed · safe areas (x 140–940, y < 1520) · consistent visual quality
## Licensing
- [ ] Music/SFX license · voice commercial license (`ses/LISANS.txt` → `yayin_uygun: evet`) · generated assets' commercial rights · no unauthorized footage
