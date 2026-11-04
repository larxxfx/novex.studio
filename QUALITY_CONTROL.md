# Kalite kontrol özeti (otomatik; ayrıntı `videolar/<klasör>/teslim/QC_REPORT.txt`)

| Klasör | Teknik | Siyah/Donuk | Senkron | Ses/fon min | LUFS/TP | Telaffuz WER | Ses lisansı | Yayına hazır |
|---|---|---|---|---|---|---|---|---|
| `2026-11-04_0800_antikythera-mechanism` | 10/10 | 0/0 | 2.0 ms | 16.1 dB | [-13.9, -1.7] | 5.4% | Emir onayı bekliyor | HAYIR |
| `2026-11-04_1200_lake-nyos` | 10/10 | 0/0 | 2.0 ms | 17.0 dB | [-13.9, -1.6] | 5.0% | Emir onayı bekliyor | HAYIR |
| `2026-11-04_1600_venus-day-longer-than-year` | 10/10 | 0/0 | 2.0 ms | 15.5 dB | [-13.8, -1.6] | 1.0% | Emir onayı bekliyor | HAYIR |
| `2026-11-04_2000_what-if-gibraltar-closed` | 10/10 | 0/0 | 2.0 ms | 14.7 dB | [-13.9, -1.7] | 4.3% | Emir onayı bekliyor | HAYIR |

## Teslim doğrulama (`python3 araclar/teslim_dogrula.py`)

MP4 + kapak + SRT + paket + zorunlu katılım sorusu + 3D sahne oranı + ses/lisans tutarlılığı. MP4'ü bu makinede olmayan klasör ❌ görünür (MP4 git dışıdır).

| Video | MP4 | Süre | Kapak | SRT | Paket+katılım | 3D sahne | Ses | Teknik QC | Durum |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-04_0800_antikythera-mechanism | 196.0 MB · `10c817637ca4` | 49.1 sn | 1080×1920 | 10 satır | ✅ | 9/9 3D, harita 0 | piper-norman (Emir: bekliyor) | 10/10 | ⏳ onay bekliyor |
| 2026-11-04_1200_lake-nyos | 146.7 MB · `e80950d2c8b9` | 51.0 sn | 1080×1920 | 10 satır | ✅ | 9/9 3D, harita 0 | piper-norman (Emir: bekliyor) | 10/10 | ⏳ onay bekliyor |
| 2026-11-04_1600_venus-day-longer-than-year | 127.6 MB · `958de103d0c3` | 46.67 sn | 1080×1920 | 10 satır | ✅ | 9/9 3D, harita 0 | piper-norman (Emir: bekliyor) | 10/10 | ⏳ onay bekliyor |
| 2026-11-04_2000_what-if-gibraltar-closed | 135.4 MB · `51d5ab666478` | 47.8 sn | 1080×1920 | 10 satır | ✅ | 9/9 3D, harita 0 | piper-norman (Emir: bekliyor) | 10/10 | ⏳ onay bekliyor |

## Referansa göre: `2026-11-04_0800_antikythera-mechanism`

Kontrol: gerçek MP4'ten 12 kare (0,5–46,5 sn) `strateji/referans/` kareleriyle yan yana, 4 Kas ~11:00 (v4).

| Soru | Cevap |
|---|---|
| İlk 2 sn güçlü mü? | İyi: Atlantik'ten Ege'ye dönen küre, "1901 · Aegean Sea", 2. saniyede başlık ve nabızlı enkaz işareti. |
| Referansa yakın mı? | Kısmen-yakın: Dünya'ya dalış, atmosfer, nabızlı işaret ✅; nesne bölümünde 3D model yok, dişliler 2D çizim (dönen, parlayan). Ay sahneleri 3D ✅. |
| Durağan sahne | Yok; dişliler sahneye göre farklı hızda döner, küreler döner/zumlar. Dişli sahnesi 5 kez kullanıldı: çeşitlilik orta. |
| Harita fazla mı? | 2D harita yok. |
| Kamera hareketi | Üstel dalış + itme. |
| Anlatıcı | Norman; "1901" artık doğru. Whisper sapmaları: "gears"→"years", "shipwreck"→"chipric", "Antikythera" (Whisper hiç yazamıyor). **Emir dinlemeli.** |
| Mobil okunurluk | v3'te dişliler altyazıya giriyordu → yukarı alındı; uzun seçeneklerde logo sorunun üstüne alındı. |
| Kapanış sorusu | "So was it one of a kind, or the only one that survived? And which lost technology should we uncover next: Damascus steel, or Roman concrete?" + ekranda DAMASCUS STEEL / ROMAN CONCRETE ✅ |

## Referansa göre: `2026-11-04_1200_lake-nyos`

Kontrol: gerçek MP4'ten 14 kare (0,4–50 sn) `strateji/referans/` kareleriyle yan yana, 4 Kas ~10:40 (v4).

| Soru | Cevap |
|---|---|
| İlk 2 sn güçlü mü? | İyi: turkuaz atmosferli küre Afrika'ya döner; 2. saniyede başlık + "Lake Nyos" nabız işareti. |
| Referansa yakın mı? | Kısmen: dalış, atmosfer, gece paleti, işaret ✅. Yakın planda kara gri/bulanık ve bulut benzeri lekeli (doku sınırı, N-16); kure_v1'in parlayan kıyı çizgileri yok. |
| Durağan sahne | Yakın plan sahneleri (2–8) aynı bölgede: zum farklı ama görüntü benzer → çeşitlilik zayıf. |
| Harita / grafik | Yok. v3'teki yoğunluk çubuğu ve zaman çizelgesi (yalnız grafik) Dünya yakın planı + sayaç/karşılaştırma ile değiştirildi (Emir 10:16 kuralı). |
| Kamera hareketi | Dalış + yavaş zum; Monoun'a kayma. |
| Anlatıcı | Norman; "Cameroon" artık doğru ("hills of Cameroon"). Whisper sapmaları: "exhaled"→"excelled", "Nyos"→"Neos", "Monoun"→"Monand". **Emir dinlemeli.** |
| Mobil okunurluk | Etiketler altyazı bandının üstünde (v3'te çakışıyordu). "HEAVIER THAN AIR" başlığı karşılaştırma etiketlerine yakın. |
| Gelişim hedefi tuttu mu? | Evet: düz harita/grafik sahnesi kalmadı (teslim_dogrula 9/9 somut görsel); kanca ülke adı netleşti. |
| Kapanış sorusu | "Would you live beside a lake that can breathe? And which deadly place on Earth should we explore next?" + ekranda soru ✅ |
| Eksik | Gerçek göl/fıskiye fotoğrafı yok (erişim yok); Emir kamu malı fotoğraf eklerse `foto` sahnesi olarak eklenebilir. |

## Referansa göre: `2026-11-04_1600_venus-day-longer-than-year`

Kontrol: 12 kare (0,5–46 sn) `strateji/referans/` kareleriyle yan yana, 4 Kas 02:14 ve 02:23 (düzeltme sonrası).

| Soru | Cevap |
|---|---|
| İlk 2 sn güçlü mü? | Orta-iyi: küçük gezegen hızla büyüyor, başlık 0,5 sn'de henüz soluk; 2. saniyede tam okunur. |
| Referansa yakın mı? | Kısmen. Tam ekran 3D küre, atmosfer halesi, parçacık, ışık huzmesi, vurgu altyazı ✅. Kamera dalışı, parlayan çizgi ve gerçek doku yok (Venüs dokusu prosedürel ve yumuşak). |
| Durağan sahne | Yok; küre her sahnede döner/zumlar. Ancak 8 sahnenin hepsi aynı küre: görsel çeşitlilik düşük. |
| Harita fazla mı? | Harita yok. |
| Kamera hareketi | Yavaş itme + küre zumu; dalış yok. |
| Anlatıcı robotik mi? | Norman: doğal sayılır, hafif sentetik tını; WER %1,0. **Emir dinlemedi.** |
| Mobil okunurluk | Düzeltildi (MERCURY kutusu, 465 °C etiketi konturlu). |
| Akış | Sayaç → karşılaştırma → ters dönüş oku → 465 °C → soru: her sahne yeni bir şaşkınlık açıyor. |
| Kapanış sorusu | "Could you survive a single day on Venus? And which planet should we explore next: Mars, or Mercury?" + ekranda MARS / MERCURY ✅ |

## Referansa göre: `2026-11-04_2000_what-if-gibraltar-closed`

Kontrol: gerçek MP4'ten 16 kare (0,4–46 sn) `strateji/referans/` kareleriyle yan yana, 4 Kas ~10:45.

| Soru | Cevap |
|---|---|
| İlk 2 sn güçlü mü? | İyi: tam küre + "What if…" sorusu; 2,5 sn'de boğaz işareti ve başlık. |
| Referansa yakın mı? | Yakın: aynı Dünya dokusu, atmosfer kenarı, yörüngeden boğaza dalış, nabızlı işaret, parlayan sel hattı, kelime vurgulu altyazı ✅. Eksik: kure_v1'deki parlayan kıyı/sınır çizgileri; yakın planda kara gri ve yumuşak (N-16). |
| Durağan sahne | Yok: dalış, hedefler arası kayma, zum, çizilen hat. |
| Harita fazla mı? | 2D harita yok; 9/9 sahne 3D küre. |
| Kamera hareketi | Dalış + Akdeniz'e kayma + hafif itme. |
| En güçlü an | Akdeniz'in tuz çölüne dönüşmesi (`dunya_kuru`) ve Atlantik'ten akan mavi sel hattı. |
| Anlatıcı | Norman; Whisper sapmaları: "desert"→"digit" (bir turda doğru), "Malacca"→"Molacal". **Emir dinlemeli.** |
| Mobil okunurluk | Etiketler altyazı bandının üstünde (merkez y 1000 düzeltmesi); daktilo yazı küçük etiketlerde ince. |
| Doğruluk | "Up to 1 meter" ekranda kaynakla uyumlu (0,5–1 m/yıl); "as little as two years" korunarak. |
| Kapanış sorusu | "Would you walk across the dry Mediterranean? And which strait should we close next: the Bosphorus Strait, or the Strait of Malacca?" + ekranda BOSPHORUS / MALACCA ✅ |

Not: siyah=1 değerleri videonun ilk 0,2 sn'lik bilinçli siyahtan açılışıdır (blackdetect eşiği). İnsan dinleme/izleme kontrolü Emir'dedir.
