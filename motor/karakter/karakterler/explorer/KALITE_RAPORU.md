# Explorer kiti — kalite raporu (explorer_kit_v1, 3 Kasım 2026)

**Sonuç: test ve prototip için kullanılabilir; yayın kalitesinde ana karakter olarak HAZIR DEĞİL.**

## Bulunan sorunlar ve yapılanlar

| # | Sorun | Etki | Durum |
|---|---|---|---|
| 1 | Parşömen kalıntısı: bekleme 1–6'da ip ile bacak arası, koşu 2 ve 4'te bacak arası krem dilimler | Arka planda açık renkli lekeler | ✅ Silindi (449 px; otomatik kural + elle işaretli bölge, `araclar/kare_hazirla.py`). Koşu 2'de 1–2 px'lik iz kalabilir |
| 2 | Kare boyutları farklı (107–168 × 210–262 px), çapa yok | Koşuda yatay titreme | ✅ Ortak 182×275 tuval; çapa = ayak tabanı, gövde merkezine hizalı |
| 3 | Zıplama yüksekliği kırpmada kaybolmuş | Zıplama yerinde çömelme gibi görünür | ✅ Referans sayfasından geri kazanıldı (kare 3: 27 px, kare 4: 67 px) |
| 4 | **Çözünürlük çok düşük** (karakter ~190–250 px boy) | 1080×1920'de 3× büyütme → pikselli görünüm | ⚠️ Çözülemez. Geçici: tam sayı ölçek + yumuşatmasız çizim (piksel sanatı görünümü). Kalıcı: yüksek çözünürlüklü yeniden üretim |
| 5 | İkili alfa (yarı saydam kenar yok) | Tırtıklı kenar | ⚠️ Piksel sanatı ölçeklemede kabul edilebilir; yumuşak stil için yeniden üretim gerekir |
| 6 | Kare numaraları eksik: referansta koşu 1,2,3,4,**7,8**; zıplama 1,2,3,**6,7,8** | Koşu döngüsünde ve zıplamada hareket atlıyor | ⚠️ Kaynakta yok; ara kareler üretilmeli |
| 7 | Stil: tanımdaki "el çizimi hikâye kitabı" değil, piksel sanatı/chibi oranlar | Marka kimliğiyle uyum kararı gerekir | ❓ Emir'in kararı |
| 8 | Kaynak/lisans: referans sayfası "Evelyn — Explorer" başlıklı; kim/neyle üretildiği belirtilmemiş | Ticari kullanım hakkı belirsiz | ❓ `LISANS.md` |

## Kontroller
- 18 karenin tamamı RGBA, kenara değen kare yok, referans sayfasıyla birebir eşleşme (hata 0).
- Görsel kontrol sayfası: `qc/kontrol_sayfasi.png` · ayrıntı: `qc/kalite_raporu.json`.
