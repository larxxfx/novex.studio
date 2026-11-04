# NØVEX resmî sesi — "Adam" (Emir, 4 Kasım 2026 11:07)

| Bilgi | Değer |
|---|---|
| Karar | "erkek_3_Adam_ABD.mp3 NØVEX'in RESMÎ SES REFERANSIDIR." Norman ve diğer anlatıcılar kullanılmaz. |
| Referans dosya | `erkek_3_Adam_ABD.mp3`, 40,6 sn, 48 kHz mono, SHA-256 `2596c85ad98561dd…` (depoya girmez) |
| İçerik | Antikythera senaryosu (4 Kas 08:00 Short'u) — bu hattın daha önce ürettiği bir örnek |
| Motor | Kokoro-82M v0.19, ses `am_adam` (sherpa-onnx `kokoro-en-v0_19`, sid 5) → `ses_motoru: kokoro:5`, `hiz_carpani: 1.0` |
| Model paketi | GitHub k2-fsa/sherpa-onnx `tts-models/kokoro-en-v0_19.tar.bz2`, SHA-256 `912804855a04745fa77a30be545b3f9a5d15c4d66db00b88cbcd4921df605ac7` |

## Doğrulama (4 Kas 11:25, aynı metin, ilk 13 sn)
| Aday | Tını uzaklığı (MFCC) | Perde (f0) | Perde oynaklığı | Tını merkezi |
|---|---|---|---|---|
| **Referans** | — | 130 Hz | 3,67 yt | 503 Hz |
| **Kokoro am_adam** | **2,3** | 129 Hz | 3,82 | 520 Hz |
| Kokoro bm_lewis | 4,3 | 123 | 3,46 | 422 |
| Piper john | 6,1 | 115 | 2,24 | 459 |
| Kokoro am_michael | 8,6 | 128 | 2,91 | 368 |
| Piper norman | 8,9 | 114 | 3,33 | 422 |
Cümle başlangıçları (sn) referans 0,4/6,2/8,1/12,6/15,1/18,5/22,8 — hattımız (kokoro:5, ×1,0) 0,3/6,3/8,2/12,7/15,2/18,6/22,9.

## ElevenLabs
Hesapta "Adam" sesleri var (`pNInz6obpgDQGcFmaJgB` orijinal hazır ses; `IRHApOXLvnW57QJPQH2P` "Dark and Tough"). Referans dosya bunlardan değil, Kokoro'dan. ElevenLabs kredi harcar (Emir onayı yok) ve bu ortamdan ElevenLabs sunucularına bağlantı reddediliyor; kullanılmıyor.

## Lisans ve haklar
- Ağırlıklar Apache-2.0: ticari kullanım, YouTube/Instagram/TikTok yayını serbest; çıktı sese ek kısıt yok.
- Ses klonlama yok: hazır, sentetik bir ses; gerçek bir kişinin taklidi değil.
- Kalan risk: eğitim verisinin bir kısmı kapalı ticari TTS çıktısı ve ses bazında açıklanmıyor (`SES_LISANS_ARASTIRMASI_EN.md`). Bu yüzden `yayin_uygun: hayir` — Emir bu riski yazılı kabul edince `evet`.
