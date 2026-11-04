# NØVEX üretim ve teslim standardı (Emir, 3 Kasım 2026, kalıcı)

## 1. Anlatım
- Düz/monoton anlatım yok. Konuya göre merak, şaşkınlık, gerilim, heyecan, hayranlık.
- Önemli kelime ve cümlelerde vurgu; cümle aralarında doğal duraklama; ton sahnenin atmosferine uygun.
- Seviye dengeli ve temiz: −16 LUFS anlatım → miks −14 LUFS, true peak ≤ −1 dBTP.
- Uygulama: duygu kontrolü olmayan modellerde `araclar/anlatim_ifade.py` + videonun `anlatim_performans.json` dosyası.
  Cümle başına duygu etiketi, parça başına hız, vurgu (dB), perde (yarım ton) ve duraklama.
- **Yeni ses modeli:** önce aynı metinle örnek → Emir dinler → onay. Onaysız mevcut model değiştirilmez.
  Model ticari kullanım lisansı doğrulanmadan yayına uygun sayılmaz.

## 2. Ses tasarımı
- Sahne geçişi: whoosh. Önemli bilgi: vurgu (impact/hit). Gizem: atmosfer/drone. Gerilim/keşif: riser, nabız.
- Açılış ve kapanış imzası; gerektiğinde ortam sesi ve hafif sinematik katman.
- Efektler hikâye olaylarına bağlı (zaman.json'daki cümle/sahne zamanları), rastgele değil; abartı yok.
- Anlatım asla bastırılmaz: konuşma fonun ≥ 12 dB üstünde, `miks.py` cümle bazında ölçer.

## 3. Teslim paketi (her video)
1. Final MP4 · 2. Ana başlık · 3. Alternatif başlıklar · 4. YouTube açıklaması · 5. SEO etiketleri + hashtagler ·
6. Sabit yorum · 7. Konu ve anlatım özeti · 8. Anlatıcı ve ses modeli · 9. Müzik ve efektler · 10. Kaynaklar ve lisans ·
11. Teknik QC raporu · 12. Kapak görseli.
- Metinler İngilizce; her birinin Türkçe anlamı pakette yanında.
- Dosya: `videolar/<klasör>/YAYIN_PAKETI.md`; MP4'ler depoya girmez (sha256 kaydı).

## 4. Durumlar ve bildirim
| Durum | Ölçüt |
|---|---|
| Üretimde | Senaryo/görsel/ses/render sürüyor |
| Kontrolde | Render bitti, QC/lisans kontrolü sürüyor veya Emir onayı bekleniyor |
| Tamamlandı | Render + teknik QC geçti; dosyalar teslim edildi |
| **YAYINA HAZIR** | Render + ses + görüntü + altyazı + telif/lisans kontrollerinin **hepsi** geçti |

- Video tamamlanınca bildirim "NØVEX videon hazır!" ile başlar.
- Ardından sayılar ayrı ayrı verilir: tamamlanan / yayına hazır / üretimde / kontrolde / eksikleri olanlar (eksik listesiyle).
- Tek kaynak: `uretim_durumu.md`.

## 5. Değişmeyen kurallar
- Emir'in onayı olmadan yükleme veya zamanlama yok.
- Ücretli servis, kredi veya API yok.
- Çalışan özellik bozulmaz.
- Yapılmayan iş yapılmış gibi raporlanmaz.

## 6. Teslim dosyaları (Ana Operasyon Talimatı, 3 Kasım 2026)
Her videonun `teslim/` klasörü:
- `VIDEO.mp4` · `THUMBNAIL.jpg`
- `TITLE.txt` (ana başlık + 2 alternatif) · `DESCRIPTION.txt` · `TAGS.txt` · `HASHTAGS.txt`
- `SUBTITLES.srt` · `PINNED_COMMENT.txt` · `SOURCES.txt` · `QC_REPORT.txt`

Ayrıca `YAYIN_PAKETI.md`: yukarıdakilerin Türkçe açıklamalı özeti + konu/anlatım özeti, anlatıcı/model, müzik/efektler, lisans durumu.

Hazır bildirimi (yalnızca gerçekten tamamlanınca):

> NØVEX videon hazır!
> Video türü / Slot / Video dosyası / Kapak / Başlık / Açıklama / Etiketler / Altyazı: Hazır | Eksik
> Kalite kontrolü: Geçti | Sorun var
> Yayın paketin hazır. İnceleyip onaylayabilirsin.

- Bildirim kanalı: bu sohbet + `PushNotification` (Claude uygulaması açıkken ve uzaktan bağlantı varken telefona düşer).
  E-posta (Gmail bağlayıcısı) ancak Emir izin verirse.
- Zamanında bitmeyen video için hazır bildirimi gönderilmez; gecikme ve nedeni raporlanır.
- Kontrol edilmemiş bir öğe "geçti" sayılmaz; yapılamayan kontrol açıkça yazılır.

## 7. Yaratıcı evrim (Creative Evolution Directive, 3 Kasım 2026)
Her video kendi görsel yönünü alır; aynı grafik, arka plan, palet, geçiş, kompozisyon ve kamera şablonu tekrar tekrar kullanılmaz.

**Üretim öncesi** (`videolar/<klasör>/GORSEL_YON.md`):
1. Görsel konsept.
2. Konuya özel renk paleti.
3. Kamera dili, ışık, kompozisyon, geçiş stili.
4. Özgün sekans fırsatları.
5. `strateji/GORSEL_KAYIT.md`'de önceki videolarla tekrar kontrolü.

**Üretim sonrası:**
1. Önceki videolarla karşılaştırma.
2. Tekrarlayan desenler.
3. Özgünlük, görsel anlatım ve sinematik kalite değerlendirmesi.
4. `GORSEL_KAYIT.md`'ye ders/iyileştirme notu.

**Keşfedilecek diller:** tarihî rekonstrüksiyon, fotogerçekçi ortamlar, 2D/3D açıklayıcı grafik, bilimsel görselleştirme, animasyonlu harita, arşiv belgesel estetiği, deneysel tipografi, atmosferik çevre anlatımı, gelişmiş kamera ve geçişler.

**Marka:** Marka tanınırlığı lacivert/altın zorunluluğuyla değil; kalite, anlatım, tipografi ve tutarlı profesyonel standartla sağlanır.

**Sınırlar:**
- Doğruluk önce gelir.
- Yapay zekâ sahneleri gerçek belgesel görüntüsü gibi sunulmaz (ekranda/açıklamada belirtilir).
- Lisanssız varlık kullanılmaz.
- Ücret ve yayın onaya bağlıdır.

**ChatGPT ile:** Önceki yaratıcı kararlar `inceleme_chatgpt.md` ve `GORSEL_KAYIT.md` üzerinden karşılıklı sorgulanır.

## 8. Görsel, ses ve hikâye kalite standardı (Emir, 4 Kasım 2026 01:51)
Tam metin: `strateji/KALITE_STANDARDI_4KASIM.md`.

**Referans:** İlk "What If Turkey Were in America?" / Antarktika videolarının sinematik kalitesi. Tam ekran ışın izlemeli küre, kamera dalışı, partikül, parlayan çizgiler, kelime vurgulu altyazı.
- Yeni videolar bunun altına düşmez.
- **4 Kasım'da üretilen 4 Short (sahne_v1 düz slayt) bu standardın ALTINDADIR.** Bu yüzden onları "standarda uygun" saymıyorum.

**Görsel:**
- Her videoda baskın görsel 3D/sinematik olmalı:
  - `gezegen` sahnesi (Venüs/Mars/Ay/buz/gaz/Dünya dokulu ışın izlemeli küre)
  - `kure_v1` (Dünya)
  - partikül (`partikul`), ışık huzmesi (`isik_huzme`), parlama (`parlama`)
  - kamera itme ve kaydırma
- Harita yalnızca gerektiğinde kullanılır. Düz tipografi sahnesi yalnızca destek amaçlıdır.
- Kling, Higgsfield ve benzeri ücretli üretim araçları onaysız kullanılmaz. ChatGPT sahne promptlarını hazırlar; ücretli üretim Emir onayıyla yapılır.

**Anlatıcı:**
- **Ana anlatıcı (Emir kararı, 4 Kasım 2026): Kokoro-82M v0.19, ses `am_adam` → `ses_motoru: "kokoro:5"`, hız çarpanı 1.0.**
  5 erkek ses (Michael, George, Adam, Lewis, Norman) aynı metinle dinletildi; Emir 3 numarayı (Adam) seçti: "her videoda tekrar tekrar geliştiririz".
- Lisans: ağırlıklar Apache 2.0 (ticari kullanım serbest). ⚠️ Eğitim verisinin bir kısmı kapalı ticari TTS çıktısı (model kartı) — gri alan olarak not edilir; YouTube'da sentetik içerik beyanı işaretlenir.
- `ses/LISANS.txt` şablonu: `videolar/2026-11-04_0800_antikythera-mechanism/ses/LISANS.txt` (yayin_uygun: evet).
- Ses kimliği kilitli: başka sese geçiş yalnızca Emir onayıyla. Geliştirme her videoda `anlatim_performans.json` (hız, vurgu, duraklama, `soyle`) ile yapılır.
- Eski aday Piper `en_US-norman-medium` (`piper-norman`) yedek olarak kalır.
- Agresif gürültü azaltma, keskinleştirme ve aşırı sıkıştırma yapılmaz.

**Tipografi:** Kilit kelimeler `vurgu_kelimeler` ile altyazıda vurgu rengiyle gösterilir. Mobilde okunabilirlik kontrol edilir.

**QC'ye eklenen sorular:**
- İlk 2 saniye güçlü mü?
- Referans kaliteye yakın mı?
- Durağan sahne var mı?
- Harita fazla mı?
- Kamera hareketi yeterli mi?
- Anlatıcı robotik mi?
- Akış izleyiciyi sona kadar tutar mı?

## 9. Video sonu katılım sorusu (Emir, 4 Kasım 2026 01:53) — ZORUNLU
- Her video, izleyiciye **sırada neyi keşfetmemizi istediğini** soran doğal bir İngilizce soruyla biter: konu, gizem, yer, uygarlık, bilim sorusu ya da What If senaryosu.
- Soru videonun konusuyla ilgili olur ve her videoda farklı ifade edilir.
- Shorts'ta kısa ve doğrudan, uzun videoda daha düşündürücü olur.
- Ara sıra iki seçenek sunulur (ör. "Mars, or Mercury?").
- Soru kapanış anlatımına ve sinematik ekran tipografisine (`soru` sahnesi) entegre edilir; duygusal kapanışı zayıflatmaz.
- Jenerik "abone ol / yorum yap" kalıbı kullanılmaz.
