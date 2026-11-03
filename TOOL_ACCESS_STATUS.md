# Araç ve erişim durumu (Claude tarafı, 4 Kasım 2026 00:15 TSİ)

Her satır bu oturumda **gerçek çağrıyla** test edildi. ChatGPT tarafı yalnızca Emir'in beyanıyla yazıldı; Claude bunu doğrulayamaz.

## Claude
| Servis | Durum | Kanıt | Eksik |
|---|---|---|---|
| GitHub `larxxfx/novex.studio` | ÇALIŞIYOR: oku, dal, push, PR (REST) | Bu dal push'ları | GraphQL 403 (`gh pr create` çalışmıyor; REST kullanılıyor). Release oluşturma bu oturumda yasak (403). Görünürlük değiştirme güvenlik denetimince engellendi. |
| Depo görünürlüğü | **PUBLIC** (3 Kas 23:50 kontrol) | `gh api repos/...` → `private=false` | Emir Private yapmalı (T-20261104-10) |
| Zamanlanmış görevler (Claude) | KURULMADI → bu gece kurulacak | `list_triggers` = 0 | Her çalışma temiz bulut oturumu; kurulum `araclar/kurulum_ortam.sh` (156 sn, test edildi) |
| Motor varlıkları | ÇALIŞIYOR | `varliklar` dalı (`debda67`), temiz dizinde `sha256 -c` OK | Natural Earth doğrudan indirme 403 → bu dal çözüm |
| Yerel EN TTS | Piper ljspeech ÇALIŞIYOR (lisans doğrulandı: MIT + kamu malı). Matcha ÇALIŞIYOR (ağırlık lisansı yazılı değil). Kokoro ÇALIŞIYOR (yayına uygun değil). | Bu gece üretilen sesler | Emir ses onayı bekliyor |
| Whisper telaffuz kontrolü (small.en) | ÇALIŞIYOR | `cikti/telaffuz.json` | |
| sahne_v1 görsel motoru | ÇALIŞIYOR (8 sahne türü, 3 tipografi dili) | 08:00 render | AI görsel/video üretimi yok (ücretsiz erişim yok) |
| kure_v1 küre motoru | ÇALIŞIYOR | Okyanus rotası MP4'leri | Yavaş (~20 dk / 50 sn) |
| vidIQ | BAĞLI, kanal YOK | `vidiq_user_channels` → boş (hesap: kamillarx33@gmail.com); 80 kredi (ücretsiz plan) | NØVEX kanalını vidIQ'da yetkilendir. Kredi harcayan çağrılar onaysız yapılmaz. |
| vidIQ Instagram | BAĞLI HESAP YOK | `vidiq_instagram_connected_accounts` → boş | |
| TikTok | BAĞLAYICI YOK | Kayıtta TikTok bağlayıcısı yok | |
| YouTube yükleme | YOK (vidIQ'da `video_upload` aracı var ama kanal yetkisiz ve onaysız kullanılmaz) | | |
| Cloudflare (Claude'daki bağlayıcı) | KISITLI: eski "Workers Bindings" MCP; Worker yükleyemiyor | `r2_buckets_list` → "R2'yi panelden etkinleştirin" | R2 kapalı; Worker deploy için wrangler kimliği yok |
| Descript | AI kredisi bitmiş (3 Kas) | GUNLUK.md | |
| ElevenLabs | Askıda (marka kararı) | `marka/SESLENDIRME.md` | |
| Kling / Higgsfield / GPT Images | ADAPTÖR İSKELETİ VAR, BAĞLANTI YOK | `motor/servisler/` (EntegrasyonYok) | Ücretli; onay yok |
| Canva | Bu oturumda bağlayıcı yok | | |
| 11 yt-* becerisi | Kurulu (`~/.claude/skills`). 6 betik çalışıyor (`--help` 6/6; `title.py` gerçek başlıkla). yt-script/package/shorts/seo üretimde kural olarak uygulanıyor. yt-audit, yt-comment, yt-retention, yt-viral kanal verisi ister → veri erişimi yok. | 3 Kas 23:20 test | Kanal yetkisi |
| Bildirim | Bu sohbete dosya teslimi ÇALIŞIYOR. Zamanlanmış görev bitince telefona push: kurulumda açılacak, henüz test edilmedi. | | Test edilecek |

## ChatGPT (Emir'in 4 Kas 00:00 beyanı; Claude doğrulayamaz)
| Servis | Beyan | Claude'un görebildiği |
|---|---|---|
| GitHub | erişim doğrulandı | Depoda `chatgpt/*` dalı veya ChatGPT commit'i **yok** (3 Kas 23:50) → yazma yetkisi kanıtlanmadı |
| Cloudflare | erişim doğrulandı | — |
| YouTube kanalı | erişim doğrulandı | — |

**Kanıt testi:** ChatGPT, `chatgpt/erisim-testi` dalında `CHATGPT_REPORT.md`'ye bir satır yazıp push ederse yazma yetkisi kanıtlanır. Claude sonraki çalışmasında dalı görüp onaylar.
