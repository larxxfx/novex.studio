# Sıradaki işler ve engeller (Claude günceller; ChatGPT ekleyebilir)

| ID | İş | Sorumlu | Süre | Kabul testi | Durum |
|---|---|---|---|---|---|
| N-01 | Natural Earth 403 | Claude | — | Temiz dizinde `varliklar` dalı + `sha256 -c` OK | ÇÖZÜLDÜ (3 Kas, `debda67`) |
| N-02 | Temiz oturum kurulumu | Claude | — | `araclar/kurulum_ortam.sh` boş HOME'da 156 sn, KURULUM TAMAM | ÇÖZÜLDÜ |
| N-03 | Tek görsel stile bağımlılık | Claude | — | `motor/sahne_v1` (8 sahne türü, 3 tipografi dili, konuya özel palet) + 08:00 MP4 | ÇÖZÜLDÜ (ilk sürüm) |
| N-04 | Render kesintiye dayanıklılık | Claude | — | `short_uret.py` aşama/parça kaydı; biten parça atlanır | ÇÖZÜLDÜ (kod); kesinti testi: yapılacak |
| N-05 | Zamanlanmış görevler (4/gün + Pazar) | Claude | 30 dk | Görev listesinde 5 kayıt + ilk çalışmanın MP4 kanıtı | DEVAM |
| N-06 | Uzun video hattı (8–12 dk, 16:9) | Claude | 1–2 gün | 8 dk test MP4 + bölümler | AÇIK |
| N-07 | Claude ↔ ChatGPT canlı mesajlaşma (Cloudflare Worker + Durable Objects + WebSocket, mock adaptörler) | Claude | 1–2 gün | Mock testlerle 7 senaryo (mesaj, cevap, kopma/yeniden teslim, kuyruk, tekrar engeli, yetkisiz erişim) | ENGELLİ: Claude ortamı *.workers.dev'e erişemiyor (curl 000, 4 Kas). Ayrıntı: strateji/CANLI_ILETISIM_MIMARISI.md. Çalışan alternatif: GitHub kuyruğu + kuyruk_dogrula.py + Actions (success). Not: Queues ve DO artık ücretsiz planda. |
| N-08 | Instagram / TikTok hesap bağlantısı | Emir | — | vidIQ Instagram listesi dolu; TikTok bağlayıcısı | ENGELLİ (hesap bağlantısı yok) |
| N-09 | Depo Private | Emir | 1 dk | `private=true` | ENGELLİ (Claude'un isteği güvenlik denetimince reddedildi) |
| N-10 | Ses onayı (Piper) | Emir | 5 dk | `ses/LISANS.txt` `yayin_uygun: evet` | BEKLİYOR |
| N-11 | MP4 harici depolama (R2) | Emir | — | R2 panelden etkin + minimum yetkili token GitHub Secret'ta | ENGELLİ (R2 kapalı; şimdilik teslim sohbetten) |
| N-12 | Telaffuz kararsızlığı (Piper rastlantısal) | Claude | — | Cümle başına 3 deneme + Whisper ile en iyi seçim (`anlatim_ifade.py`); Nyos WER %7,4 → %1,9 | ÇÖZÜLDÜ |
