# Sürekli gelişim mekanizması (Emir, 4 Kasım 2026 — kalıcı)

## Her yeni videodan ÖNCE (zamanlanmış görevler dahil)
1. Son 4 videonun `videolar/<v>/REFERANS_QC.md`, `QUALITY_CONTROL.md` ve `strateji/GORSEL_KAYIT.md` "Ders" sütununu oku.
2. Emir'in son geri bildirimlerini oku (`CHATGPT_REPORT.md`, `TASK_QUEUE.md`, sohbet).
3. `uretim.json` → `"gelisim_hedefi"`: bu videoda önceki videolara göre **ölçülebilir/görülebilir tek bir somut gelişim** (ör. "kıyı çizgilerine parlayan hat", "ilk 1 sn'de dalış başlasın"). Boşsa `teslim_dogrula` hata verir.

## Her videodan SONRA
- `REFERANS_QC.md`: 12+ kare referansla yan yana; QC soruları + gelişim hedefi tuttu mu (evet/hayır + kanıt karesi).
- `GORSEL_KAYIT.md`: görsel dil, palet, kamera, tekrarlanmaması gereken, ders.
- `PRODUCTION_LOG.md` / `QUALITY_CONTROL.md`: `python3 araclar/kayit_guncelle.py`.

## Haftalık kalite değerlendirmesi (Pazar, uzun video görevinden sonra)
Değerlendirilen 8 eksen (1–5, kanıtla): görsel etki ve sahne çeşitliliği · ilk saniyeler · ses doğallığı · hikâye akışı · kamera/animasyon · müzik/efekt · tipografi/renk · final ve yorum potansiyeli.
Dosya: `strateji/haftalik/<YYYY-WW>.md`. **Gerçek performans verisi (izlenme, retention) yoksa uydurulmaz**; "veri yok" yazılır. Kanal vidIQ'da yetkilendirilince ücretsiz okuma araçlarıyla eklenir.
