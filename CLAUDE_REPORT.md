# Claude raporu

Her oturum en üste eklenir. Biçim: ne yapıldı → kanıt (commit, dosya, test) → sorunlar → sonraki adım.

### [Claude] — Üretim hattı + 4 Kasım Short'ları — 2026-11-04 00:40 TSİ
**Dal:** `claude/uretim-hatti` · **PR #2:** https://github.com/larxxfx/novex.studio/pull/2 (Emir birleştirir; ChatGPT inceler). Varlık dalı: `varliklar`.

**Yapılanlar ve kanıtları:**
1. **Natural Earth 403 çözüldü.** Varlıklar `varliklar` dalında (`debda67`). Temiz dizinde `sha256 -c` OK.
2. **`araclar/kurulum_ortam.sh`:** temiz bir HOME'da 156 sn, tüm kontroller ✓.
3. **`motor/sahne_v1/sahne.py`:** konudan bağımsız 2D sahne motoru.
   - 8 sahne türü: baslik, sayi, harita, zaman, karsilastir, alinti, liste, soru.
   - 3 tipografi dili: arsiv, modern, daktilo.
   - Konuya özel palet ve doku, kamera hareketi, sahne arası geçiş, güvenli alan içinde altyazı.
   - Hız: ~4,5 kare/sn/çekirdek; 48 sn'lik Short ≈ 3 dk render.
4. **`araclar/short_uret.py`:** 10 aşamalı, kaldığı yerden devam eden hat.
   - Durum `cikti/durum.json`'da tutulur; render parça parça yapılır.
   - Depodan "tamam" görünen ama çıktısı olmayan aşamayı yeniden yapar.
5. **`araclar/ses_tasarim.py`:** olay tabanlı ses tasarımı.
   - Sahne geçişlerinde whoosh; vurgulu parçada riser ve darbe; gizem/gerilimde atmosfer.
   - Ortam sesi (okyanus, rüzgâr, uzay); açılış ve kapanış imzası.
6. **`araclar/anlatim_ifade.py`:** ifadeli anlatım.
   - Parça başına hız, vurgu, perde ve duraklama; `soyle` (fonetik yazım), `altyazi` alanı.
   - Sessizlik kırpma payı artırıldı.
7. **`araclar/qc.py` hata düzeltmesi.** Lisans kontrolü not satırındaki "yayin_uygun: evet" ifadesini yanlışlıkla geçerli sayıyordu. Artık yalnızca satır başındaki anahtar okunuyor; iki yönlü test geçti.
8. **Ses lisansı:**
   - Piper `en_US-ljspeech-high`: MIT lisanslı depo, LJ Speech kamu malı, model "trained from scratch" → **doğrulandı**.
   - Matcha: ağırlık lisansı yazılı değil → doğrulanamadı.
   - Kokoro: yayına uygun değil.
9. **08:00 Antikythera:** MP4 üretildi.
   - Teknik QC 10/10; siyah ya da donmuş kare yok; senkron 2 ms; konuşma fonun ≥ 19,6 dB üstünde.
   - Telaffuz: kelime hata oranı %3,0 ("Antikythera" yanlış okunuyor).
   - Lisans: Emir'in ses onayını bekliyor.
10. **12:00 Lake Nyos:** MP4 üretildi; teknik QC 10/10. Telaffuz hatası %7,4 → ses yeniden üretilecek (T-20261104-13).
11. **Zamanlanmış görevler:** 4 günlük görev (05:47, 09:43, 13:17, 16:23 TSİ) + Cumartesi 10:13 uzun video görevi.
    - Hepsi bulutta, otomatik onay modunda, telefona bildirimli.
    - İlk çalışma 4 Kas 05:47. **Henüz hiçbiri çalışmadı → çalıştığı kanıtlanmadı.**

**Sorunlar:**
- Depo PUBLIC; görünürlük değiştirme isteğim güvenlik denetimince reddedildi.
- R2 kapalı.
- Instagram ve TikTok bağlantısı yok.
- vidIQ'da kanal yok.
- Canlı Claude↔ChatGPT kanalı yok (N-07).
- Uzun video hattı yok (N-06; Cumartesi görevi kurmaya çalışacak).
