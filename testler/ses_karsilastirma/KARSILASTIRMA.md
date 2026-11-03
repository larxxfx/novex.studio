---
konu: Yusuf & Zeynep ses motoru karşılaştırması — Google Cloud TTS vs Chatterbox Multilingual v3
tarih: 2026-11-03
hazirlayan: claude
durum: TEST BEKLİYOR (ses dosyası üretilemedi — erişim engeli, bkz. §1)
karar: YOK — Emir'in kararı beklenmeden mevcut üretim sistemine geçilmez
---
# Ses motoru karşılaştırması

Bu klasör **yalnızca test** içindir; `araclar/` altındaki mevcut seslendirme altyapısı değiştirilmedi.

| Dosya | İçerik |
|---|---|
| `metin_yusuf.txt` | Yusuf test metni (ilk videonun seslendirmesi, 12 cümle, 602 karakter) |
| `metin_zeynep.txt` | Zeynep test metni (SON SİNYAL tonunda özgün metin, 10 cümle) |
| `degerlendir.py` | Ses dosyası → ölçüm (CER, perde, hız, duraklama, LUFS, gürültü) + 1080×1920 / 30 FPS test MP4 + QC |

## 1. Bu oturumda gerçekten ne yapılabildi?

| Adım | Durum | Kanıt |
|---|---|---|
| Google Cloud TTS ile ses üretmek | ❌ Yapılamadı | `texttospeech.googleapis.com` bu ortamdan erişilemiyor; ayrıca proje + faturalandırma hesabı + kimlik bilgisi gerekiyor (Emir'den anahtar istenmedi, kart eklenmedi) |
| Google konsolunda Türkçe ses listesini doğrulamak | ❌ Yapılamadı | Konsola erişim yok. Belge düzeyinde: Chirp 3 HD `tr-TR`'yi destekliyor; ses adı kalıbı `tr-TR-Chirp3-HD-<Ad>` |
| Chatterbox v3'ü yerelde çalıştırmak | ❌ Yapılamadı | PyTorch yok; PyPI (DNS) ve Hugging Face (proxy 403) kapalı; model ağırlıkları yalnızca HF'de |
| Değerlendirme + test MP4 hattı | ✅ Çalışıyor | Piper taslak sesiyle prova: test.mp4 1080×1920, 30/1, H.264 High, yuv420p, bt709, AAC 48 kHz, −14,8 LUFS, tam çözümleme hatasız |

**Sonuç:** Google ve Chatterbox için **hiçbir test ses dosyası ve test MP4'ü üretilmedi.** Ses dosyaları
§4'teki yolla sohbete eklenince her biri tek komutla ölçülür ve test MP4'ü oluşturulur.

## 2. Google Cloud TTS

**Sesler (konsoldan `voices.list` ile teyit edilecek):** Chirp 3 HD ses adları `tr-TR-Chirp3-HD-<Ad>` kalıbında;
diğer dillerde aynı ad kümesi erkek (Charon, Fenrir, Orus, Puck, Iapetus, Algenib…) ve kadın (Kore, Leda, Aoede,
Despina, Sulafat, Achernar…) olarak listeleniyor. Türkçe için hangi adların açık olduğu **doğrulanmadı**.
WaveNet Türkçe ses adları (`tr-TR-Wavenet-*`) ve cinsiyetleri **doğrulanmadı**.

Test adayları (teyit sonrası): YUSUF → 2 erkek Chirp 3 HD + 1 WaveNet erkek · ZEYNEP → 2 kadın Chirp 3 HD + 1 WaveNet kadın.

**Ücretlendirme (Google fiyat sayfası):**

| Ses türü | Aylık ücretsiz | Sonrası |
|---|---|---|
| WaveNet | 0–4 milyon karakter | 4 $ / 1 milyon karakter |
| Chirp 3 HD | 0–1 milyon karakter | 30 $ / 1 milyon karakter |

**NØVEX tüketimi (120 video/ay):** Mevcut metin 602 karakter; 45 sn üst sınır için ~1.000 karakter varsayımı.
- Tek çekim: 120 × 1.000 = **120.000 karakter/ay**
- Video başına 3 deneme (yeniden üretim payı): **360.000 karakter/ay**
- Chirp 3 HD ücretsiz kotanın %36'sı, WaveNet'in %9'u → **tahmini maliyet: 0 $**. Ücret ancak Chirp 3 HD'de ayda 1 milyon karakter aşılırsa başlar (≈ 1.000 video × 1.000 karakter).

**Koşullar:**
- Ücretsiz kota için **faturalandırma hesabı şart** (kart veya banka bilgisi). Kota aşımı standart fiyatla faturalanır.
- SSML etiketleri (`<mark>` hariç), boşluk ve satır sonları karaktere dahil.

**Ücret çıkmasını teknik olarak önleme (bütçe uyarısı dışında):**
1. **Ücretsiz deneme hesabında kalmak (en güçlü sınır):** Google'a göre deneme süresince fatura kesilmez; deneme bitince kaynaklar durur ve hesap ücretli hesaba elle yükseltilmedikçe ücret alınmaz. Deneme 300 $ kredi veya 90 gün (hangisi önce) ile sınırlı; ücretsiz kota bu süre boyunca krediden düşmez. **Sınırlama:** 90 gün sonra devam için ücretli hesaba yükseltme gerekir.
2. **Bütçe → Pub/Sub → Cloud Run fonksiyonu → faturalandırmayı kapatma** (Google'ın resmî yöntemi). **Sınırlama:** Maliyet ile bildirim arasında gecikme var, bu sürede ek maliyet oluşabilir; faturalandırma kapanınca projedeki tüm servisler durur.
3. **API kotasını düşürmek** (IAM & Admin → Kotalar, istek/dakika). Karakter bazlı günlük tavan bulunduğu **doğrulanmadı**.
4. **Uygulama içi sayaç:** Üretim betiği ayda 800.000 karakterde (Chirp 3 HD kotasının %80'i) kendini durdurur. (Henüz yazılmadı; geçiş onaylanırsa eklenir.)

**Ticari lisans:** Google belgesi, üretilen ses dosyalarının uygulamalarda veya videolar gibi medyada kullanılabileceğini söylüyor (GCP Hizmet Şartları'na uyulması koşuluyla). Ücretsiz kotaya özel bir ticari kısıt bulunamadı (araştırma raporu). Atıf zorunluluğu yok. → **Belge düzeyinde uygun; kanıt dosyası arşivlenmeli** (`marka/lisans_kanitlari/`).

## 3. Chatterbox Multilingual v3 — üç ayrı lisans katmanı

| Katman | Durum | Not |
|---|---|---|
| Model ağırlıkları ve kod | ✅ MIT (Resemble AI) | Ticari kullanım serbest; her çıktıya görünmez Perth filigranı eklenir |
| Eğitim verisi | ⚠️ Açıklanmamış | Piper'ı "türetilmiş veri" gerekçesiyle elediğimiz için aynı not düşülür: model lisansı temiz, veri kökeni doğrulanamadı |
| Referans ses (Yusuf/Zeynep kimliği) | ✅ Uygun referans mevcut: **Alania Turkish Synthetic Speech**, `voices` ve `cc-by` alt kümeleri, CC BY 4.0 (gerçek kişi sesi değil, VoxCPM2 ile tasarlanmış) | Atıf zorunlu. `cc-by-sa` alt kümesi **kullanılmaz**. Gerçek bir kişinin sesi izinsiz referans olarak kullanılmaz |

- **Bu ortamda çalışma:** ❌ (PyTorch + HF gerekli). CPU'da çalışabilen ONNX dışa aktarımları var ama onlar da HF'de.
- **Kimlik sabitliği:** Sabit referans klibi + sabit tohum (seed) + sabit `exaggeration`/`cfg` ayarları kaydedilir.
- **Maliyet:** 0 $ (yerel). Gereken: PyTorch/HF açık bir ortam ya da Emir'in iPad'den kullanabileceği ücretsiz Hugging Face demo alanı.

## 4. Testi tamamlamak için gerçekçi yol (iPad)

**A — Google (kart gerekir; Emir'in kararı):**
1. console.cloud.google.com → **Ücretsiz deneme** ile proje aç. **Ücretli hesaba yükseltme.**
2. Text-to-Speech API'yi etkinleştir → konsoldaki sentez ekranında dil olarak Türkçe seç → listelenen `tr-TR-Chirp3-HD-*` ve `tr-TR-Wavenet-*` adlarını yaz.
3. `metin_yusuf.txt` metnini 2–3 erkek sesle, `metin_zeynep.txt` metnini 2–3 kadın sesle üret; hız 1,0, perde 0. MP3/WAV'ları sohbete ekle.

**B — Chatterbox (kart gerekmez):**
1. Safari → Hugging Face "Chatterbox Multilingual" demo alanı (Resemble AI), dil: Turkish.
2. Referans: Alania veri setinin `voices` alt kümesinden 1 erkek + 1 kadın klip (CC BY 4.0). Klip kimliklerini not et.
3. Aynı iki metni üret. Ayarları not et (exaggeration, cfg, seed). WAV'ları sohbete ekle.

**C — Claude:** Her dosya için:
`python3 testler/ses_karsilastirma/degerlendir.py <ses> <metin> "<sistem · ses adı · YUSUF|ZEYNEP>" <klasör>`
→ rapor.md + test.mp4 + qc_rapor.md, ardından aşağıdaki tablo doldurulur.

## 5. Karşılaştırma tablosu (doldurulmadı — ses dosyası yok)

| Ses | CER | Hız (hece/sn) | Perde aralığı | Duraklama | Gürültü/bozulma | Telaffuz (Emir) | Doğallık (Emir) | Vurgu/duygu (Emir) | Marka uyumu (Emir) |
|---|---|---|---|---|---|---|---|---|---|
| Google · ? · YUSUF | | | | | | | | | |
| Chatterbox · Alania ? · YUSUF | | | | | | | | | |
| Google · ? · ZEYNEP | | | | | | | | | |
| Chatterbox · Alania ? · ZEYNEP | | | | | | | | | |
| *Referans: Piper fettah (taslak, aday değil)* | *%13,4* | *5,14* | *4,9 yt* | *0,57 sn* | *5. cümle bozuk (CER %82)* | | | | |

Not: Yusuf test metni Piper'da 48 sn sürdü. 30–45 sn hedefi için metnin yaklaşık 1–2 cümle kısaltılması gerekebilir (ChatGPT incelemesine).

## Kaynaklar
- Google Cloud TTS fiyatları: cloud.google.com/text-to-speech/pricing
- Chirp 3 HD dil listesi (tr-TR): docs.cloud.google.com/text-to-speech/docs/chirp3-hd
- Ses adları tablosu: cloud.google.com/text-to-speech/docs/voices
- Ticari kullanım ifadesi: docs.cloud.google.com/text-to-speech/docs/basics
- Ücretsiz deneme koşulları: docs.cloud.google.com/free · cloud.google.com/signup-faqs
- Faturalandırmayı otomatik kapatma: docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications
- Chatterbox Multilingual v3 (MIT): resemble.ai duyurusu · huggingface.co/ResembleAI/chatterbox
- Alania Turkish Synthetic Speech (CC BY 4.0): huggingface.co/datasets/cloud0day3/alania-synthetic-speech-tr
