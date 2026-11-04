# NØVEX görsel kalite referansı (Emir, 4 Kasım 2026)

**Ana referans:** İlk NØVEX videosu *"What If Turkey Were in America?"* (Türkçe adıyla "Türkiye, Amerika'nın Yerinde Olsaydı?").
Aynı motorla (`motor/kure_v1`) üretilen ikinci video *"Türkiye Antarktika'da Olsaydı?"* da referans kalitededir.

> **Dürüst not:** Referans videonun MP4 dosyası bu depoda **yok** (`motor/kure_v1/OKUBENI.md`: "İlk video bu klasöre dahil değil").
> Depoda onu üreten motor ve Antarktika videosunun kaynak kodu var. Aşağıdaki kontrol kareleri `kure_v1` ile
> **yeniden render edilmiş Antarktika kareleridir**, ilk videonun kendisi değildir. Emir ilk videonun MP4'ünü
> gönderirse SHA-256'sı ve kareleri buraya eklenir.

## Kontrol kareleri (`strateji/referans/`)
| Kare | Ne gösteriyor |
|---|---|
| `kure_v1_antarktika_t1.5.jpg` | Tam ekran ışın izlemeli küre, atmosfer kenarı, gece tarafı, kelime vurgulu altyazı |
| `kure_v1_antarktika_t10.0.jpg` | Yörüngeden yüzeye dalış, kar/parçacık fırtınası, büyük sayaç (−50 °C), kaynaklı bilgi kutusu |
| `kure_v1_antarktika_t22.0.jpg` | Yakın plan buz dokusu, parlayan sınır çizgileri, ek harita kartı, vurgu renkli sonuç cümlesi |

Üretim: `cd motor/kure_v1 && python3 src/render.py frame <t> out.png` (motor değiştirilmedi).

## Referansı referans yapan özellikler (her yeni video bunlarla karşılaştırılır)
1. **Gerçek bir 3D nesne ekranı doldurur** (küre, gezegen, dişli…); düz renk zemin üstünde yalnız yazı yok.
2. **Kamera hareket eder:** yörüngeden dalış, itme, takip. Durağan sahne en fazla ~3 sn.
3. **Işık ve atmosfer:** atmosfer halesi, gece/gündüz geçişi, parlama, parçacık (kar, toz, kor).
4. **Parlayan çizgiler ve işaretler** konuyu coğrafyaya bağlar (sınır, rota, nokta + nabız halkası).
5. **Büyük sayaç + kısa bağlam etiketi**; rakam animasyonla gelir.
6. **Kelime vurgulu altyazı**, mobil güvenli alanda.
7. **Akış:** her sahne bir soru açar, sonraki sahne cevaplar; kapanış güçlü.

## Karşılaştırma yöntemi (QC'de)
- Yeni videodan ~12 kare (`ffmpeg -ss <t>`) + yukarıdaki 3 referans kare yan yana incelenir.
- Sorular: 3D nesne var mı · kamera hareketi var mı · ışık/atmosfer var mı · harita/yazı ağırlığı fazla mı · ilk 2 sn güçlü mü.
- Sonuç `QUALITY_CONTROL.md`'ye "referansa göre" satırı olarak yazılır; eksikler açıkça belirtilir.
