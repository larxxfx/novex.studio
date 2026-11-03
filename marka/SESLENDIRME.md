# NØVEX seslendirme politikası ve araçları

> Karar (Emir, 3 Kasım 2026): Seslendirme için ödeme yok, ElevenLabs kullanılmıyor.
> Kural: **Ücretsiz olması yetmez; ticari kullanım (YouTube/TikTok/Instagram, para kazanma dahil) izni açıkça doğrulanmış olmalı.**
> Lisansı doğrulanmamış hiçbir ses "yayına hazır" işaretlenmez.

## 1. Karar özeti

| Öncelik | Çözüm | Lisans durumu | Bu ortamda çalışıyor mu? | Kullanım |
|---|---|---|---|---|
| **1 — Yayın** | **Emir'in kendi sesi** (iPad kaydı + Claude'un işleme hattı) | ✅ Tüm haklar Emir'de | ✅ (kayıt sohbete eklenince) | Yayınlanan tüm videolar |
| 2 — Aday | Chatterbox Multilingual (Resemble AI) | ✅ MIT (ticari kullanım serbest); Türkçe destekli; çıktıda görünmez filigran | ❌ PyTorch + Hugging Face gerekiyor, ikisi de bu ortamda kapalı | Ağ izni açılırsa yeniden test edilecek |
| 3 — Taslak | Piper `tr_TR-fettah-medium` / `fahrettin-medium` | ❌ Yayın için uygun değil: veri CC0 olarak beyan edilmiş ama kaynak depoda Türkçe veri yok; model, "yalnızca araştırma" lisanslı lessac sesinden türetilmiş | ✅ (sherpa-onnx, yerel) | Yalnızca zamanlama/animatik taslağı |
| 3 — Taslak | Coqui `tr/common-voice/glow-tts` + HiFiGAN | ⚠️ Model MIT ama veri kaynağı çelişkili ("Common Voice" ↔ yapılandırmada "Talent_TR_Male") | ✅ (NumPy, yerel) | Yalnızca taslak |
| — Elendi | Piper `tr_TR-dfki-medium` | ❌ Veri CC BY-NC-SA 4.0 (ticari yasak) | ✅ | Kullanılmaz |
| — Elendi | Meta MMS-TTS, Coqui XTTS-v2, Fish/OpenAudio, F5-TTS | ❌ Ticari olmayan lisanslar | — | Kullanılmaz |
| — Elendi | Edge-TTS / gTTS gibi resmî olmayan servis kullanımları | ❌ Hizmet şartları ticari kullanım vermiyor | — | Kullanılmaz |
| — Askıda | ElevenLabs | Ücretsiz plan ticari lisans vermiyor | — | Emir'in kararıyla kullanılmıyor |

**Sonuç:** Bugün, hem ücretsiz hem ticari kullanıma açıkça uygun hem de bu ortamda çalışan bir Türkçe TTS **yok**.
Yayın sesi Emir'in kendi kaydıdır. TTS sesleri yalnızca kurgu zamanlaması için taslak olarak kullanılır ve
`ses/LISANS.txt` dosyasında `TASLAK` yazdığı sürece `qc.py` videoyu yayına hazır saymaz.

## 2. Kalite testi (3 Kasım 2026, aynı metin, Whisper-medium ile geri çözümleme)

Metin: "Bu gemi, dümeni hiç kırmadan otuz iki bin kilometre gidebilir. Pakistan'dan Kamçatka'ya, tek bir düz çizgi.
Peki, bu nasıl mümkün? Cevap haritada değil, kürenin üzerinde saklı."

| Ses | Karakter hata oranı (CER) | Kelime hata oranı (WER) | Hız (hece/sn) | Perde aralığı (yarım ton) | Gözlem |
|---|---|---|---|---|---|
| Piper fettah | **%0,6** | %7,1 | 5,18 | 3,9 | En anlaşılır; tonlama **düz/monoton** |
| Piper fahrettin | %1,2 | %10,7 | 5,77 | **12,4** | Daha canlı; "Pakistan" → "Akistan" |
| Coqui tr | %7,7 | %10,7 | 5,41 | 7,6 | "Kamçatka'ya" → "kan çıkarıyor"; "Peki" düştü |

Ölçümler nesneldir ama kulak testinin yerini tutmaz: duygu, vurgu ve doğallık Emir'in dinlemesiyle değerlendirilir.
Hiçbiri Emir'in sesi kadar doğal ve özgün olmayacaktır.

## 3. Kendi sesimizle kayıt (iPad)

1. **Ayar:** Ayarlar → Sesli Notlar → Ses Kalitesi → **Kayıpsız**. Uçak modu; bildirimler kapalı.
2. **Ortam:** Küçük, eşyalı oda (perde, yatak, dolap yankıyı keser). Klima/buzdolabı kapalı. Ağızdan 15–20 cm, iPad'in mikrofonuna doğru, hafif açılı.
3. **Okuma:** `05_seslendirme.txt` dosyasını ikinci bir ekranda (veya telefonda) aç. Her cümleden sonra yarım saniye dur.
   Yanlış okunan cümleyi baştan tekrar et; kesmeyi Claude yapar (`yt-edit` tekrar çekimleri bulur).
4. **İlk 2 saniye:** Kayda başlarken 2 saniye sessiz kal (gürültü profili için).
5. **Teslim:** Sesli Notlar → Paylaş → Dosyalara Kaydet → Claude sohbetine ekle. Dosya adı: `<video-klasörü>_ses.m4a`.
6. **SON SİNYAL karakterleri:** Her karakter için `seriler/son-sinyal/ses/SES_PROFILLERI.md`'deki mesafe, ton ve efekt kuralı.

## 4. Üretim hattı (Claude)

```
kayıt.m4a ──► araclar/ses_isle.py ──► ses.wav (48 kHz, temiz, −16 LUFS) + ses_rapor.json
                                         │
03_senaryo.md ─► araclar/hizala.py ◄─────┘  → 07_ses_zamanlama.json (cümle + kelime zamanları, Whisper doğrulaması)
                                         │
render (görüntü, sessiz) ◄───────────────┘  sahneler ve altyazılar konuşmaya kilitlenir
müzik.wav + efekt.wav ──► araclar/miks.py (miks.json: ses/müzik/efekt seviyeleri, ducking) ──► miks.wav (−14 LUFS)
görüntü + miks ──► final MP4 ──► araclar/qc.py (teknik + LİSANS kontrolü)
```

- **Ayrı kontrol:** Ses, müzik ve efekt **ayrı dosyalar** olarak tutulur. Seviye değişikliği yalnızca `miks.json` değiştirilerek
  yapılır; görüntü yeniden render edilmez (ör. "müziği 3 dB kıs" → `muzik_db: -7`).
- Ses dosyaları depoya girmez; `videolar/<video>/ses/` altında yalnızca `LISANS.txt`, `ses_rapor.json` ve SHA-256 durur.

## 5. Ses kaynağı lisans kaydı (`ses/LISANS.txt`, her video)
```
kaynak: emir-kayit | chatterbox | TASLAK-piper-fettah | ...
lisans: <kısa açıklama>
yayin_uygun: evet | hayir
sha256: <ses.wav özeti>
```

## Kaynaklar
- Piper dfki model kartı (CC BY-NC-SA 4.0): huggingface.co/rhasspy/piper-checkpoints · tr/tr_TR/dfki/medium/MODEL_CARD
- Piper fahrettin/fettah model kartları (CC0 beyanı, lessac'tan ince ayar): sherpa-onnx `tts-models` sürüm arşivleri içindeki MODEL_CARD
- NabuCasa voice-datasets (Türkçe veri listede yok): github.com/NabuCasa/voice-datasets
- Lessac/Blizzard 2013 lisansı ("Research Purposes only"): cstr.ed.ac.uk/projects/blizzard/2013/lessac_blizzard2013/license.html
- Piper lisans tartışmaları: github.com/rhasspy/piper/discussions/271 · huggingface.co/rhasspy/piper-voices/discussions/94
- Chatterbox (MIT, Türkçe): huggingface.co/ResembleAI/chatterbox
- YouTube "inauthentic content" (15 Temmuz 2025) ve gerçekçi sentetik içerik beyanı: YouTube yardım/YPP politikaları
