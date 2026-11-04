# NØVEX görsel kalite referansı (Emir, 4 Kasım 2026)

**Ana referans:** İlk NØVEX videosu *"What If Turkey Were in America?"* (Türkçe: "Türkiye, Amerika'nın Yerinde Olsaydı?").
Emir 4 Kas 10:52'de sohbete ekledi; bu kayıt o dosyadan yapıldı.

| Bilgi | Değer |
|---|---|
| Dosya | `62ab0770-…bb2.mov` (Emir'in kopyası; MOV depoya girmez — CLAUDE.md büyük dosya kuralı) |
| SHA-256 | `8850c1d6f8a68b46120623bd5e7bf6162c14a1e5bb505cf812407572a411a76b` |
| Teknik | 720×1280 (bu kopya; muhtemelen indirilmiş/kaydedilmiş), HEVC Main, 30 fps, bt709, AAC 44,1 kHz stereo, 35,6 sn, ~2,5 Mb/sn |
| Ses | −20,0 LUFS entegre, tepe −8,9 dBFS (bu kopyada); Türkçe anlatım |
| Tempo | Sert kesme yok; sürekli kamera hareketi + yumuşak geçişler; ~6 görsel bölüm (geçişler ≈ 8,5 · 13,0 · 14,4 · 19,6 sn) |

## Kontrol kareleri (`strateji/referans/turkey_america_t*.jpg`, 405×720)
0,5 · 3 · 8 · 10 · 14 · 16 · 18 · 20 · 22 · 26 · 31 · 35 sn. Eski Antarktika kareleri (`kure_v1_antarktika_*.jpg`) ikincil referans olarak duruyor.

## Referansı referans yapan özellikler
1. **Gerçek uydu görünümlü, canlı Dünya:** bulutlar, kar, kabartma, mavi okyanus; gece tarafında şehir ışıkları. Uzayda tam küre ile açılış, kıtaya dalış.
2. **Ülke vurgusu:** kırmızı yarı saydam dolgu + parlayan sınır + bayrak simgesi + aralıklı büyük harf etiket (TÜRKİYE, KANADA, MEKSİKA). Türkiye'nin ABD'nin yerine "taşınması" videonun imza anı.
3. **Alçak açılı 3D arazi uçuşları:** Pasifik kıyısı (Monterey), Büyük Ovalar (Denver); ufuk pusu, kabartma, ışık. Konuyu "yer" olarak hissettiriyor.
4. **Canlandırma sahnesi:** petrol kuyuları + gün batımı silueti, köşede **"CANLANDIRMA"** etiketi (gerçek görüntü değil, açıkça belirtilmiş).
5. **Stratejik parlayan yaylar** (Avrupa/Atlantik'e camgöbeği hatlar).
6. **Tipografi:** kalın, sıkışık büyük harf başlık; renkli anahtar kelimeler (kırmızı TÜRKİYE, beyaz metin, sarı OLSAYDI/SÜPER GÜÇLERİNDEN); üst etiket "— PASİFİK KIYISI —" geniş harf aralığıyla; altyazı kalın, anahtar kelime sarı.
7. **Final:** "SEN NE DÜŞÜNÜYORSUN?" + kırmızı "YORUMLARA YAZ" rozeti, ardından tam ekran **NØVEX** kartı + "YA ÖYLE OLSAYDI?" sloganı.

## 4 Kasım Short'ları (v3/v4) referansa göre — dürüst karşılaştırma
| Özellik | Referans | Bizim 4 Short | Durum |
|---|---|---|---|
| Dünya dokusu | Gerçek uydu mozaiği, bulut, şehir ışıkları | `world_tex.jpg`: Natural Earth sınırlarından **prosedürel**, gri-lacivert, biyom/bulut yok | **En büyük açık.** Kamu malı NASA Blue Marble (+ bulut + gece ışıkları) dokusu gerekiyor; bu ortam NASA'ya erişemiyor → Emir eklemeli (N-19) |
| Ülke vurgusu / taşıma | Kırmızı dolgu + parlayan sınır, Türkiye→ABD | Yoktu | **Motora eklendi** (`bolge`, `tasi`; kuzey yukarıda, gerçek boyut) — videolarda henüz kullanılmadı |
| Arazi uçuşu | Alçak açı, kabartma, ufuk | Yok | Yükseklik verisi (SRTM/ETOPO, kamu malı) gerekiyor; erişim yok (N-20) |
| Canlandırma / foto | "CANLANDIRMA" etiketli illüstrasyon | `foto` sahnesi hazır, köken etiketi var; görsel varlık yok | Görsel kaynağı bekleniyor (N-17) |
| Parlayan hatlar | Stratejik yaylar | Gibraltar sel hattı ✅ | Var |
| Dalış / kamera | Sürekli | Dalış + zum ✅ | Var; yakın planda doku bulanık |
| Tipografi | Büyük harf, kalın, çok renkli vurgu | Başlıklar karışık harf, tek renk | Geliştirilecek (başlıkta renkli anahtar kelime) |
| Final | Soru + yorum rozeti + NØVEX kartı | Soru ✅; rozet ve kart yoktu | **Motora eklendi** (`yorum_rozeti`, `bitis_karti`) |
| Süre / tempo | 35,6 sn | 46–51 sn | Daha sıkı senaryo hedeflenmeli |

Kısaca: **4 Short referansın altında kalıyor**; ana sebep gerçekçi Dünya dokusu, arazi uçuşları ve gerçek görsel varlıkların eksikliği. Motor tarafındaki imza öğeleri (ülke vurgusu/taşıma, yorum rozeti, kapanış kartı) eklendi ve test edildi.

## Karşılaştırma yöntemi (her QC'de)
- Yeni videodan ~12 kare + `turkey_america_*` kareleri yan yana; yukarıdaki 7 özellik tek tek işaretlenir.
- Sonuç her videonun `REFERANS_QC.md`'sine ve `QUALITY_CONTROL.md`'ye yazılır; eksikler açıkça belirtilir.
- Referansın sahneleri/renkleri kopyalanmaz: her konu kendi paletini ve görsel kimliğini taşır; kopyalanan şey **kalite seviyesi**.
