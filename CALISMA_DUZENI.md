# Çalışma düzeni

## 1. Bir videonun yolculuğu

| # | Durum (`01_brief.md` → `durum:`) | Sahip | Ne olur | Çıktı dosyası |
|---|---|---|---|---|
| 1 | `fikir` | Claude | 3–5 fikir, puan tablosu | `01_brief.md` |
| 2 | `fikir-inceleme` | ChatGPT | Kendi fikirleriyle karşılaştırır, seçimi onaylar ya da değiştirir | `inceleme_chatgpt.md` §1 |
| 3 | `kaynak` | Claude + ChatGPT | Her olgusal iddia birincil/kurumsal kaynakla eşleşir | `02_kaynaklar.md` |
| 4 | `senaryo` | Claude | Senaryo + zaman kodlu sahne planı + seslendirme metni | `03_senaryo.md`, `04_sahne_plani.md`, `05_seslendirme.txt` |
| 5 | `senaryo-inceleme` | ChatGPT | Kanca, tutma, doğruluk, dil | `inceleme_chatgpt.md` §2 |
| 6 | `ses` | Emir → Claude | Emir `05_seslendirme.txt`'yi iPad'de kaydeder, sohbete ekler; Claude `ses_isle.py` + `hizala.py --whisper` ile işler ve okuma hatalarını işaretler | `ses/LISANS.txt`, `07_ses_zamanlama.json` |
| 7 | `uretimde` | Claude | Görsel, animasyon, kurgu, müzik/efekt, altyazı, render | (MP4 depo dışı) |
| 8 | `qc` | Claude | Teknik QC + kontrol kareleri | `qc/qc_rapor.md`, `qc/*.jpg` |
| 9 | `son-inceleme` | ChatGPT | Kareler + metin + paket üzerinden son kontrol | `inceleme_chatgpt.md` §3 |
| 10 | `onay-bekliyor` | Emir | Yayın onayı | — |
| 11 | `yayinlandi` | Emir | Yükler, bağlantıyı `yayin_kaydi.csv`'ye ekler | `yayin_kaydi.csv` |

Bir adım "kırmızı" bulgu üretirse durum bir önceki sahibine geri döner.

## 2. Dosya ve dal adları

- Video klasörü: `videolar/2026-11-04_0800_en-uzun-duz-rota/`
- Claude doğrudan `main`'e yazar (küçük, ayrık commit'ler; mesaj: `[claude] <video>: <ne>`).
- ChatGPT (Codex) **her zaman dal + PR** açar: `chatgpt/<video>-<ne>`; Emir birleştirir.
- Kimse diğerinin dosyasını silmez; eleştiri `inceleme_*.md` dosyalarına yazılır.

## 3. İnceleme formatı (iki taraf için aynı)

```
### [ChatGPT|Claude] — <adım> — <tarih>
Karar: ONAY | DEĞİŞİKLİK İSTE | RED
Kırmızı (yayını engeller):
- <madde> — <kanıt/kaynak>
Sarı (düzeltilmeli):
- ...
Öneri (isteğe bağlı):
- ...
```

Kırmızı bulgu örnekleri: kaynaksız rakam, yanlış olgu, tekrar konu, telif riski, ilk 2 sn'de kanca yok.

## 4. Kalite çizgisi (NØVEX)

- 1080×1920, 30 FPS, H.264 + AAC 48 kHz, Rec.709, −14 LUFS (±1), true peak ≤ −1 dBTP.
- Altyazı ve metinler x 140–940 px, y < 1520 px (Shorts/TikTok/Reels arayüzü dışı).
- Siyah/donmuş kare yok; konuşma fonun ≥ 12 dB üstünde; kelime düzeyinde senkron.
- Görsel dil: gece mavisi/lacivert zemin, elektrik mavisi + turkuaz vurgu, kontrollü kırmızı/altın.
  Çocukça, aşırı renkli, slayt gösterisi yok. Canlandırma sahneleri "CANLANDIRMA" etiketi taşır.
- YouTube kapağı **1280×720** hazırlanır (kanalın kapak düzenleyicisi 16:9 kırpıyor);
  dikey 1080×1920 sürümü TikTok/Reels için.
- Her rakamın bir kaynağı vardır; varsayım senaryoları gerçek gibi sunulmaz.

## 5. Tekrar kontrolü

Yeni fikir, `yayin_kaydi.csv` ve `plan/` içindeki son 30 günün konularıyla karşılaştırılır:
aynı **konu**, aynı **kanca kalıbı** ("Türkiye X'te olsaydı") veya aynı **görsel düzen** aynı
hafta içinde tekrar edilmez.

## 6. Günlük

Her oturumun sonunda `GUNLUK.md`'ye bir satır: `2026-11-04 09:40 · Claude · 0800 videosu QC'den geçti`.

## 7. SON SİNYAL

Seri geneli `seriler/son-sinyal/` altında (bible, karakter kartları, süreklilik kaydı, bölüm takibi);
bölüm üretimleri `videolar/<tarih>_1700_son-sinyal-bNN/` klasörlerinde. Bible kilitlenmeden karakter görseli üretilmez.
Her bölüm sonunda `devamlilik/sureklilik_kaydi.csv` ve `bolumler/bolum_takip.csv` güncellenir.
