# Video klasörleri

Ad: `YYYY-AA-GG_SSDD_kisa-ad/` (ör. `2026-11-04_0800_en-uzun-duz-rota/`). Yeni klasör: `python3 araclar/video_klasoru_olustur.py`
(listeye satır ekleyerek; var olan dosyaların üzerine yazmaz).

| Dosya | Aşama | Yazan |
|---|---|---|
| `01_brief.md` | Fikir karşılaştırması, seçim, kanca, `durum:` alanı | Claude → ChatGPT §1 |
| `02_kaynaklar.md` | İddia–kaynak tablosu | Claude + ChatGPT |
| `03_senaryo.md` | Seslendirme + ekrandaki metin, zaman kodlu | Claude → ChatGPT §2 |
| `04_sahne_plani.md` | Görsel, kamera, geçiş, efekt, varlık lisansı | Claude |
| `05_seslendirme_elevenlabs.txt` | ElevenLabs'e giden son metin + model/ses | Claude |
| `06_paket.md` | YouTube / TikTok / Reels metinleri, sabit yorum | Claude → ChatGPT |
| `qc/` | QC raporu, kontrol kareleri, dosya özeti (SHA-256) | Claude → ChatGPT §3 |
| `kapak/` | Kapak (1280×720 YouTube, 1080×1920 dikey) | Claude |
| `inceleme_chatgpt.md` | ChatGPT kararları (§1 fikir, §2 senaryo, §3 son QC) | ChatGPT / Emir |

MP4, WAV ve MP3 depoya girmez (`.gitignore`).
