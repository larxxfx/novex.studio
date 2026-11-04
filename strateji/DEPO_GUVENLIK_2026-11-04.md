# Depo güvenlik kontrolü — 4 Kasım 2026 09:05 (Claude)

| Kontrol | Sonuç | Kanıt |
|---|---|---|
| Görünürlük | **PUBLIC** (`private: false`) | `gh api repos/larxxfx/novex.studio` → `visibility: public` |
| Çatallama / izlenme | 0 fork; son 14 günde 0 görüntülenme | `…/forks` → 0; `…/traffic/views` → count 0 |
| Gizli anahtar (tüm dallar, 34 commit) | **Bulunmadı** | API anahtarı, GitHub/AWS/Google/Slack token, JWT, `sb_secret_`, özel anahtar, imzalı URL, parola kalıpları; eşleşmeler yalnız kural metinleri |
| `.env` / kimlik dosyası (tüm geçmiş) | **Yok** | dosya adı taraması: `.env`, `.dev.vars`, `credentials`, `*.pem`, `*.key` |
| Kişisel veri | **Vardı → güncel dosyalardan çıkarıldı** | vidIQ hesap e-postası `TOOL_ACCESS_STATUS.md` ve `strateji/MASTER_STATUS_2026-11-03.md`'de açıktı; bu dalda silindi. **Geçmiş commit'lerde duruyor.** |
| Büyük/medya dosyası | Yok (MP4/WAV/MP3 `.gitignore`) | yalnız kontrol kareleri ve kapak JPG'leri |

## Risk
1. Geçmişteki e-posta adresi herkese açık okunabilir (spam/hedefli kimlik avı riski).
2. Senaryolar, konu planı (`videolar/2026-11-0x_*`), SON SİNYAL dizi fikirleri, marka ve strateji belgeleri herkes tarafından kopyalanabilir; yayından önce içerik "çalınabilir".
3. İş akışı ve araç listesi (`TOOL_ACCESS_STATUS.md`) hangi hesapların bağlı olduğunu gösteriyor.
Anahtar sızıntısı olmadığı için **acil kimlik bilgisi değiştirme gerekmiyor**.

## Çözüm (Emir yapmalı — Claude'un görünürlük değiştirme isteği güvenlik denetimince engellendi)
GitHub → larxxfx/novex.studio → Settings → General → en altta *Danger Zone* → **Change repository visibility → Make private**.
Private olunca: GitHub Actions dakikaları özel depo kotasından düşer (ücretsiz planda ayda 2.000 dk); ChatGPT/Claude bağlayıcıları erişimi korur.
Geçmişteki e-postayı tamamen silmek geçmişi yeniden yazmayı gerektirir (geri döndürülemez) — Private yapmak bunun yerine yeterlidir.
