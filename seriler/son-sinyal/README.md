# SON SİNYAL — proje klasörü

Kurgusal, yapay zekâ destekli haftalık dikey dizi. **Gerçek olay veya haber gibi sunulmaz**;
her bölümde "KURGU" etiketi ve açıklamada "kurgusal dizi" ibaresi bulunur.

| Klasör / dosya | Ne için |
|---|---|
| `SERIES_BIBLE.md` | Evren, salgın kuralları, karakterler, 7 bölüm, kurallar — **tek doğruluk kaynağı** |
| `karakterler/` | Her karakter için kimlik kartı (değişmez görünüm + referans görsel kimlikleri + ses) |
| `referans-gorseller/` | Onaylı karakter/mekân referanslarının **kimlik listesi** (görseller ElevenLabs akışında; büyük dosya depoya girmez) |
| `mekanlar/` | Mekân kartları (ışık, saat, hasar durumu) |
| `stil/STIL.md` | Renk, ışık, kamera, ses tasarımı kuralları |
| `promptlar/` | Onaylı üretim promptları (görsel/video/ses) — her bölüm aynı tabanı kullanır |
| `devamlilik/` | Bölüm bölüm süreklilik kaydı: kıyafet, yara, eşya, saat, hava, kim nerede |
| `bolumler/bolum_takip.csv` | 7 bölümün durum, tarih, klasör, cliffhanger ve açık soru takibi |
| `uzun-film/` | Haftalık uzun YouTube filmi kurgu planı |

Bölüm üretim klasörleri `videolar/<tarih>_1700_son-sinyal-bNN/` altında; bu klasör seri genelini tutar.

## Süreklilik kuralı (kısa)
1. Bir karakterin görünüşü yalnızca `karakterler/<ad>.md` güncellenerek değişir (sebebi bölüm olayıdır).
2. Her yeni görsel/video üretimi, o karakterin **onaylı referans kimliklerini** referans görsel olarak kullanır.
3. Bölüm bitince `devamlilik/sureklilik_kaydi.csv`'ye son durum satırları eklenir; sonraki bölüm buradan başlar.
4. ChatGPT her bölümün §3 son incelemesinde süreklilik tablosuyla kareleri karşılaştırır.
