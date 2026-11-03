# ElevenLabs — bağlantı durumu ve kullanım (3 Kasım 2026 testi)

## Durum
- Claude'un ElevenLabs bağlantısı **çalışıyor** (ses listesi, model listesi, üretim).
- Hesap şu an **ücretsiz üretim kuyruğu** kullanıyor: yoğun saatte üretim başlamayabiliyor ("Free generations are busy"; kredi düşmüyor).
- **Engel:** Üretilen dosyalar (`elevenlabsusercontent.com`) Claude'un çalışma ortamına indirilemiyor (ağ izin listesi dışında).
  Bu çözülmeden Claude ElevenLabs sesini videoya **kendisi** bağlayamaz; MP3'ün sohbete eklenmesi gerekir.
  Kalıcı çözüm: claude.ai → Ayarlar → Yetenekler (Capabilities) → izinli alan adlarına `elevenlabsusercontent.com` eklemek.

## Bu çalışma alanında kullanılabilen modeller
| Tür | Modeller (seçme) | NØVEX'te kullanımı |
|---|---|---|
| Seslendirme | eleven_v4, eleven_v3, eleven_multilingual_v2, turbo/flash v2.5 | Anlatım; v4 duygu etiketleri ([whispers] vb.) |
| Ses efekti | eleven_text_to_sound_v2 (≤ 30 sn, döngü) | Rüzgâr, buz, radyo cızırtısı, geçişler |
| Müzik | eleven_music v1/v2/v2.5 (enstrümantal) | Telifsiz özgün müzik yatağı |
| Görsel | GPT Image 2/2.5, Nano Banana 2/Pro, FLUX.2/3, Seedream 5, Recraft, Ideogram | Kapak, SON SİNYAL karakter sayfaları ve anahtar kareler |
| Video | Veo 3.1, Kling 3/4, Seedance 2.5, Runway Gen-4.5, Wan 2.6 (9:16, 1080p, ≤ 30 sn) | SON SİNYAL sahneleri, belgesel B-roll canlandırmaları |
| Diğer | Konuşmadan metne (Scribe), ses yalıtma, ses efekti odaları | Altyazı zamanlaması, temizlik |

## Ses testi
| Model | Ses | Sonuç | Süre | Kredi |
|---|---|---|---|---|
| eleven_multilingual_v2 | Adam – Dominant, Firm (premade) | ✅ üretildi | 7,15 sn | 109 |
| eleven_v4 | Adam – Dominant, Firm (premade) | ⏸ 3 denemede de başlamadı (12.16, 12.33, 12.40; `free_shared`) | — | 0 |

Test cümlesi: "Bu gemi, dümeni hiç kırmadan otuz iki bin kilometre gidebilir. Pakistan'dan Kamçatka'ya... tek bir düz çizgi."
Karşılaştırma (telaffuz, vurgu, nefes, doğallık) **Emir'in dinlemesine** bağlı: Claude ses dosyasına erişemediği için kulak testi yapamadı.
Akış: https://elevenlabs.io/app/flows/aH3CBSc1KW8uAaJT3vd7

## Maliyet tahmini (ölçülen: Multilingual v2 ≈ 15 kredi/sn)
- 35 sn'lik anlatım ≈ 530 kredi · günde 5 video ≈ 2.650 kredi · ayda ≈ 80.000 kredi (yalnızca seslendirme, tek çekim).
- Video üretimi (Veo/Kling/Seedance) saniye başına çok daha pahalıdır; her uzun video üretiminden önce `estimate_only` ile fiyat alınıp Emir'e sorulur.
- Ücretsiz kotalar bu hacmi taşımaz; plan kararı Emir'indir.

## Hata araştırması (3 Kasım 2026, 12.30)
| Bulgu | Kanıt | Sonuç |
|---|---|---|
| v4 için hesapta engel yok | `estimate_only`: 109 kredi, engelleyici hata yok | Model ve ses kullanılabilir |
| Hata kodu `free_shared` | İki ayrı denemede v4, bir denemede Multilingual v2'nin 2. çekimi | Model değil, **ücretsiz paylaşımlı kapasite** dolu |
| Multilingual v2 1. çekim başarılı | 7,15 sn, 109 kredi | Kredi düşen üretim çalışıyor |
| Dosya indirme engeli | Claude ortamının ağ vekili `elevenlabsusercontent.com`, `api.elevenlabs.io`, `elevenlabs.io`, `storage.googleapis.com` için CONNECT 403 veriyor (politika) | Claude dosyayı alamaz; izinli alan adı eklenmeli ya da MP3 sohbete eklenmeli |

**En olası açıklama:** Çalışma alanı ücretsiz planda; ücretsiz plan yoğun saatlerde en düşük öncelikle çalışır.
Bunu Claude doğrudan göremez — plan bilgisini Emir ElevenLabs → Abonelik sayfasından kontrol etmeli.

**Lisans uyarısı (yayın öncesi kritik):** ElevenLabs ücretsiz planı ticari lisans içermez ve yayınlanan içerikte
ElevenLabs'e atıf ister. Para kazanan/kazanacak bir kanal için ticari lisanslı en düşük ücretli plan gerekir.
Plan doğrulanana kadar ElevenLabs sesiyle üretilen NØVEX videoları **yayına hazır sayılmaz**.
