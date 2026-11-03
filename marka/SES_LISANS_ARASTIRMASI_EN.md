# EN anlatım sesleri — lisans araştırması (3 Kasım 2026)

**Sonuç: Kokoro (Michael `am_michael`, Sarah `af_sarah`) için ticari YouTube yayını DOĞRULANAMADI → `yayin_uygun: hayir` kalır.**
Bu bir hukuki görüş değildir; kaynaklardaki ifadelerin özeti ve risk değerlendirmesidir.

## 1. Kesin olanlar
| Konu | Durum | Kaynak |
|---|---|---|
| Model ağırlıkları | Apache-2.0; yazar ticari dağıtımı açıkça davet ediyor | hexgrad/Kokoro-82M model kartı (HF aynaları: indigoskyai, muratbuker) |
| Kullandığımız sürüm | v0.19 (25 Ara 2024, <100 saat veri, 10 ses) — sherpa-onnx `kokoro-en-v0_19` paketi | model kartı sürüm tablosu |
| Üretilen ses dosyası | Apache-2.0 çıktıya kısıt koymaz; ayrı bir "ses kullanım koşulu" belgesi bulunamadı | — (belge yok) |
| espeak-ng (GPLv3) | Yalnızca çalışma zamanı fonemleyicisi; çıktı sese GPL geçmez (yaygın yorum, mahkeme kararı yok) | — |
| YouTube | AI anlatım yasak değil; gerçek bir kişiyi taklit etmeyen sentetik anlatıcı tek başına "altered/synthetic" etiketi gerektirmez; risk "inauthentic/mass-produced" (özgün olmayan seri üretim) politikası | YouTube Yardım özetleri (layer3labs, AIR, narrationbox, 2026) |

## 2. Belirsiz olanlar (neden yayına onay verilmedi)
1. **Eğitim verisinin bir kısmı kapalı ticari TTS çıktısı.** Model kartı: veri = kamu malı ses + Apache/MIT ses +
   "büyük sağlayıcıların kapalı TTS modellerinden üretilmiş sentetik ses" (açık modeller ve "özel ses klonları" hariç).
   Hangi sağlayıcı ve hangi sesin hangisinden türetildiği **ses bazında açıklanmıyor**.
2. **Ses adları sağlayıcı seslerine işaret ediyor.** v1.0'da `af_alloy`, `af_nova`, `am_echo`, `am_onyx` (OpenAI ses adları);
   v0.19'daki `af_sky`'ın, OpenAI'nin kaldırdığı "Sky" sesinin yeniden kurulumu olduğu depo commit'inde açıkça yazıyor.
   `af_sarah` ve `am_michael`'ın kaynağı açıklanmamış.
3. **Sağlayıcı şartları.** OpenAI kullanım şartları çıktıyla "OpenAI ile rekabet eden model geliştirmeyi" yasaklar. Bu yükümlülük
   modeli eğiten kişiye aittir, biz kullanıcıya doğrudan geçip geçmediği belirsizdir; ama ses kaynağı itiraz ederse risk bizde de doğar.
4. **Ses benzerliği.** Bir sesin gerçek bir seslendirme sanatçısına (sağlayıcının kaydettiği kişiye) benzemesi kişilik/ses hakkı
   iddiasına yol açabilir; YouTube gerçek kişiyi taklit eden sentetik ses için kaldırma süreci işletiyor.

## 3. Ücretsiz, lisansı doğrulanabilir alternatifler (TEST EDİLMEDİ)
| Seçenek | Lisans zinciri | Not |
|---|---|---|
| Piper `en_US-libritts_r-medium` | LibriTTS-R veri seti CC BY 4.0 (atıf gerekir); bakımcı: "sıfırdan yeniden eğitildi" (lessac'tan türemiyor) | Çok konuşmacılı (erkek+kadın); kalite Kokoro'dan düşük olabilir |
| Piper `en_US-ljspeech-high/medium` | LJSpeech kamu malı (LibriVox) | Tek kadın ses; atıf gerekmez |
| Piper `lessac`, `ryan`, `hfc_*` | ❌ Araştırma / CC BY-NC | Kullanılmamalı |
| Kendi sesin (Emir) | Tam hak | `marka/SESLENDIRME.md`'de yedek olarak zaten var |
| Descript AI Speech / ElevenLabs | Ücretli plan şartlarına bağlı | Ücret ve izin gerektirir — denenmedi |

Önerilen sonraki adım (Emir onayıyla): Piper libritts_r (1 erkek + 1 kadın konuşmacı) ve ljspeech ile **aynı metni** üretip
Michael/Sarah ile karşılaştırmak. Modeller sherpa-onnx GitHub sürümlerinden ücretsiz indirilebilir (indirmeden önce boyut ve kaynak bildirilecek).

## Kaynaklar
- hexgrad/Kokoro-82M model kartı (sürümler, eğitim verisi, Apache-2.0) — HF aynaları
- Kokoro-82M commit "restoring-sky.md" (af_sky ↔ OpenAI Sky) — huggingface.co/hexgrad/Kokoro-82M/commit/723ee7dc
- OpenAI Terms of Use, "Use Output to develop models that compete with OpenAI"
- rhasspy/piper-voices tartışma #105 (lessac lisansı, libritts_r sıfırdan eğitim); Piper README (MODEL_CARD lisansları)
- YouTube altered/synthetic content ve inauthentic content özetleri (2026)
- Not: hexgrad model kartının özgün sayfası bu oturumda doğrudan açılamadı (onay bekledi); aynı içerikli HF aynaları ve arama özetleri kullanıldı.
