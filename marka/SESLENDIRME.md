# NØVEX seslendirme politikası — Yusuf & Zeynep

> **Karar (Emir, 3 Kasım 2026):** NØVEX'in iki kalıcı ana anlatıcısı **YUSUF** ve **ZEYNEP**'tir.
> Emir'in kendi sesi ana anlatıcı **değildir**; yalnızca yedektir.
> Ödeme yok · ElevenLabs askıda · **Ticari lisansı doğrulanmamış hiçbir ses yayın için onaylanmaz.**

## 1. Anlatıcılar

| Anlatıcı | Alan | Slotlar (varsayılan) | Ton | Hedef hız |
|---|---|---|---|---|
| **YUSUF** | Bilim, teknoloji, tarih, doğa, keşif | 08.00 Harita Şoku · 11.00 Ya Şöyle Olsaydı? · 14.00 Tarih Dosyası | Net, sakin, merak uyandıran belgesel anlatıcısı | ~2,6–2,9 kelime/sn |
| **ZEYNEP** | Gizem, hikâye, atmosferik anlatım, **SON SİNYAL** | 17.00 SON SİNYAL · 20.00 Dünya Düzeni* | Alçak, ölçülü, gerilimi taşıyan anlatım | ~2,4–2,7 kelime/sn |

\* 20.00 slotu konu gizem/hikâye ağırlıklıysa Zeynep, bilgi ağırlıklıysa Yusuf. Hedef denge: günde 5 videoda 3 Yusuf / 2 Zeynep;
haftalık dağılım `plan/` dosyasında anlatıcı sütunuyla izlenir.

**Kurallar**
1. **Tek anlatıcı:** Bir videoda anlatıcı sebepsiz değişmez. (İstisna: SON SİNYAL'de karakter replikleri — anlatıcı yine Zeynep.)
2. **Hata olursa önce rapor:** Bir seste telaffuz/kalite/üretim hatası olursa diğer sese **geçilmez**; hata `GUNLUK.md` ve videonun
   `ses/LISANS.txt` notuna yazılır, Emir'e raporlanır, karar Emir'indir.
3. **Kimlik sabit:** Ses kimliği (araç, ses adı/ID, model, ayarlar) aşağıdaki tabloda kilitlidir; değişiklik yalnızca Emir onayıyla ve
   aynı metinle A/B testi sonrası yapılır. Ücretli plana geçilirse **aynı ses kimlikleri** korunur.
4. **Standart:** Konuşma −16 LUFS (işlenmiş) → miks −14 LUFS, true peak ≤ −1 dBTP; müzik konuşmanın ≥ 12 dB altında (ducking);
   sayılar yazıyla; vurgu `*yıldız*`; özel adların telaffuzu §4 sözlüğünde.
5. **Lisans:** Ücretsiz kullanım ile ticari kullanım **ayrı ayrı** doğrulanır. `ses/LISANS.txt` → `yayin_uygun: evet` olmadan `qc.py --lisans` ❌ verir.

## 2. Ses kimliği kaydı (kilit tablo)

| Alan | YUSUF | ZEYNEP |
|---|---|---|
| Üretim aracı | Descript (AI Speech) | Descript (AI Speech) |
| Test projesi | "NØVEX — Sabit Türkçe Ses Testi" · proje `3a0e4396-1b86-4e24-86f7-f6e6b00c7317` · kompozisyon `aa71b69c…` | aynı proje · kompozisyon `39401c26…` |
| Stok ses adı / ses ID | ⏳ **bilinmiyor** — Descript'te *Speakers → Yusuf → Voice* altından okunup buraya yazılacak | ⏳ **bilinmiyor** — aynı yerden |
| Model / motor | ⏳ bilinmiyor | ⏳ bilinmiyor |
| Dil / hız / ton ayarı | ⏳ bilinmiyor | ⏳ bilinmiyor |
| Test metni | "Dünya, bize gösterdiğinden çok daha fazlasını saklıyor. …" (13,12 sn) | aynı metin (13,28 sn) |
| Örnek dinleme | Descript özel paylaşım (Emir'in hesabı) — bağlantı depoya yazılmaz | aynı |
| Ücretsiz kullanım | ✅ Ücretsiz planda **sınırlı deneme**; tek seferlik 100 AI kredisi **tükendi** (3 Kasım) | aynı |
| Ticari lisans | ❌ **doğrulanmadı** (bkz. §3) | ❌ **doğrulanmadı** |
| Yayına uygun | **HAYIR** (lisans yazılı olarak doğrulanana kadar) | **HAYIR** |

## 3. Descript lisans durumu (3 Kasım 2026)

- Descript Kullanım Şartları (son güncelleme 25 Şubat 2025) §8.4: Kullanıcı girdinin ve çıktının sahibidir ("to the extent protectable"),
  ama hizmet lisansı §5.1'de "personal or internal business use" olarak tanımlı; **stok AI seslerinden ve ticari/para kazanan yayından açıkça söz edilmiyor.**
  Planlar arası fark "subscription plan limitations"a bırakılmış.
- Descript fiyat sayfası ticari kullanım satırı içermiyor; üçüncü taraf kaynaklar "ticari kullanım ücretli planlarda" diyor (birincil kaynak değil).
- Storyblocks stok **müzik/görüntü** için ticari kullanım açıkça var (§25.2) — bu **sesleri kapsamaz**.
- **Sonuç:** Yusuf/Zeynep sesleri yayın için **onaylanmadı**. Doğrulama yolu: Descript desteğine yazılı soru
  ("Free/Hobbyist planda stok AI Speech seslerini para kazanan YouTube/TikTok/Instagram videolarında kullanabilir miyim?") →
  yanıt `marka/lisans_yazismalari.md`'ye özet olarak işlenir (kişisel veri ve bağlantı olmadan).
- YouTube: Yapay zekâ sesi yasak değil; gerçekçi sentetik içerik için "değiştirilmiş/sentetik içerik" beyanı işaretlenir;
  seri üretim görünümünden kaçınılır (inauthentic content, 15 Temmuz 2025).

## 4. Telaffuz sözlüğü (her iki ses)

| Yazım | Okunuş / not |
|---|---|
| NØVEX | "Novex" (Ø = o) — testte doğru okunup okunmadığı Emir'in dinlemesiyle doğrulanacak |
| Kamçatka, Madagaskar, Quanzhou | Testten sonra doldurulacak |

## 5. Yedek ve taslak sesler

| Kaynak | Rol | Lisans | Not |
|---|---|---|---|
| Emir'in kendi kaydı | **Yedek** (Yusuf/Zeynep lisansı onaylanmazsa veya hata çözülmezse, Emir'in kararıyla) | ✅ Tüm haklar Emir'de | Kayıt rehberi §8 |
| Piper fettah / fahrettin, Coqui tr | Yalnızca zamanlama/animatik taslağı | ❌ Yayın için uygun değil | Bu ortamda çalışıyor |
| Chatterbox Multilingual | Aday | ✅ MIT | Bu ortamda çalışmıyor (PyTorch/HF kapalı) |
| ElevenLabs | Askıda | Ücretsiz plan ticari değil | Emir'in kararı |
| Piper dfki, MMS, XTTS-v2, F5, Edge-TTS | Elendi | Ticari değil | — |

## 6. Descript üretim hattı ve aktarım düzeni

```
ChatGPT ──(senaryo onayı, inceleme_chatgpt.md)──► GitHub: 05_seslendirme.txt  (Okuyan: YUSUF | ZEYNEP)
Claude ──(Descript bağlayıcısı)──► Descript projesi "NØVEX — <video klasörü>"
        AI Speech ile seslendirme (AI kredisi gerekir) ──► ses dışa aktarımı (özel/private, .m4a)
Emir (iPad) ──► dışa aktarılan sesi indirir ──► Claude sohbetine ekler
Claude ──► ses_isle.py → hizala.py --whisper (CER ≤ %8) → 1080×1920 render → miks.py → qc.py --lisans → MP4
GitHub ◄── ses/LISANS.txt (araç, ses ID, plan, lisans durumu, sha256) + 07_ses_zamanlama.json + qc/
```

- **Neden MP4 Descript'te değil:** Ücretsiz planda dışa aktarım 720p; NØVEX standardı 1080×1920. Kurgu ve render Claude'un yerel hattında yapılır.
- **Neden Emir iPad'den aktarıyor:** Claude'un çalışma ortamı Descript'in dosya sunucusuna (storage.googleapis.com) erişemiyor (proxy 403).
  Bu engel kalkarsa adım otomatikleşir.
- **Paylaşım:** Descript'teki proje adı ve ID'si `01_brief.md`'ye yazılır; ChatGPT projeyi göremez, `05_seslendirme.txt` ve QC raporu üzerinden inceler.
- **Hiçbir Descript işlemi herkese açık yayın değildir:** Dışa aktarımlar `private` yapılır; YouTube/TikTok/Instagram'a Descript üzerinden yükleme yapılmaz.

## 7. Yerel TTS kalite testi (3 Kasım 2026, aynı metin, Whisper-medium ile geri çözümleme)

Metin: "Bu gemi, dümeni hiç kırmadan otuz iki bin kilometre gidebilir. Pakistan'dan Kamçatka'ya, tek bir düz çizgi.
Peki, bu nasıl mümkün? Cevap haritada değil, kürenin üzerinde saklı."

| Ses | Karakter hata oranı (CER) | Kelime hata oranı (WER) | Hız (hece/sn) | Perde aralığı (yarım ton) | Gözlem |
|---|---|---|---|---|---|
| Piper fettah | **%0,6** | %7,1 | 5,18 | 3,9 | En anlaşılır; tonlama **düz/monoton** |
| Piper fahrettin | %1,2 | %10,7 | 5,77 | **12,4** | Daha canlı; "Pakistan" → "Akistan" |
| Coqui tr | %7,7 | %10,7 | 5,41 | 7,6 | "Kamçatka'ya" → "kan çıkarıyor"; "Peki" düştü |

Ölçümler nesneldir ama kulak testinin yerini tutmaz: duygu, vurgu ve doğallık Emir'in dinlemesiyle değerlendirilir.
Hiçbiri Emir'in sesi kadar doğal ve özgün olmayacaktır.

## 8. Yedek: kendi sesimizle kayıt (iPad)

1. **Ayar:** Ayarlar → Sesli Notlar → Ses Kalitesi → **Kayıpsız**. Uçak modu; bildirimler kapalı.
2. **Ortam:** Küçük, eşyalı oda (perde, yatak, dolap yankıyı keser). Klima/buzdolabı kapalı. Ağızdan 15–20 cm, iPad'in mikrofonuna doğru, hafif açılı.
3. **Okuma:** `05_seslendirme.txt` dosyasını ikinci bir ekranda (veya telefonda) aç. Her cümleden sonra yarım saniye dur.
   Yanlış okunan cümleyi baştan tekrar et; kesmeyi Claude yapar (`yt-edit` tekrar çekimleri bulur).
4. **İlk 2 saniye:** Kayda başlarken 2 saniye sessiz kal (gürültü profili için).
5. **Teslim:** Sesli Notlar → Paylaş → Dosyalara Kaydet → Claude sohbetine ekle. Dosya adı: `<video-klasörü>_ses.m4a`.
6. **SON SİNYAL karakterleri:** Her karakter için `seriler/son-sinyal/ses/SES_PROFILLERI.md`'deki mesafe, ton ve efekt kuralı.

## 9. Ses işleme hattı (Claude)

```
ses.m4a (Descript veya yedek kayıt) ──► araclar/ses_isle.py ──► ses.wav (48 kHz, temiz, −16 LUFS) + ses_rapor.json
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

## 10. Ses kaynağı lisans kaydı (`ses/LISANS.txt`, her video)
```
anlatici: YUSUF | ZEYNEP
kaynak: descript-ai-speech | emir-kayit (yedek) | TASLAK-piper-fettah | ...
ses_id: <Descript stok ses adı/ID>
plan: free | hobbyist | ...   (sesin üretildiği andaki plan)
lisans: <kısa açıklama + doğrulama kaynağı>
yayin_uygun: evet | hayir
sha256: <ses.wav özeti>
not: <hata raporu, varsa>
```

## Kaynaklar
- Descript Kullanım Şartları (25 Şubat 2025): descript.com/terms §5.1, §8.4, §9.3, §25.2
- Descript fiyatlandırma / TTS sayfası: descript.com/pricing · descript.com/tools/text-to-speech
- Piper dfki model kartı (CC BY-NC-SA 4.0): huggingface.co/rhasspy/piper-checkpoints · tr/tr_TR/dfki/medium/MODEL_CARD
- Piper fahrettin/fettah model kartları (CC0 beyanı, lessac'tan ince ayar): sherpa-onnx `tts-models` sürüm arşivleri içindeki MODEL_CARD
- NabuCasa voice-datasets (Türkçe veri listede yok): github.com/NabuCasa/voice-datasets
- Lessac/Blizzard 2013 lisansı ("Research Purposes only"): cstr.ed.ac.uk/projects/blizzard/2013/lessac_blizzard2013/license.html
- Piper lisans tartışmaları: github.com/rhasspy/piper/discussions/271 · huggingface.co/rhasspy/piper-voices/discussions/94
- Chatterbox (MIT, Türkçe): huggingface.co/ResembleAI/chatterbox
- YouTube "inauthentic content" (15 Temmuz 2025) ve gerçekçi sentetik içerik beyanı: YouTube yardım/YPP politikaları
