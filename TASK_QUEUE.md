# NØVEX — Ortak görev kuyruğu (ChatGPT ↔ Claude)

**İletişim gerçek zamanlı DEĞİL.**
- İki taraf bu dosyayı GitHub üzerinden okur ve günceller.
- Claude'un kontrol aralığı yalnızca zamanlanmış görevlerin çalıştığı saatlerdir (bkz. `TOOL_ACCESS_STATUS.md`).
- ChatGPT'nin kontrol aralığı ChatGPT tarafında tanımlanır ve burada doğrulanmamıştır.
- Canlı mesajlaşma altyapısı (Cloudflare Worker) henüz kurulmadı: `NEXT_ACTIONS.md` N-07.

## Kurallar
- Her görevin bir kimliği var: `T-YYYYMMDD-NN`.
- Bir göreve başlayan, `Sahip` alanına kendini yazar ve `Durum`'u `devam` yapar. Başkasının `devam`daki görevine dokunulmaz.
- Durumlar:
  - `açık`
  - `devam`
  - `inceleme` (karşı tarafın kontrolü bekleniyor)
  - `tamam` (test kanıtıyla)
  - `engelli` (neden yazılır)
  - `iptal`
- `Sonuç` alanına commit SHA, dosya yolu veya test sonucu yazılır. Kanıt yoksa `tamam` yapılmaz.
- Değişiklikler yalnızca `claude/*` veya `chatgpt/*` dallarında yapılır. `main`'i Emir birleştirir.
- Yayın, yükleme, zamanlama ve ücretli işlem yalnızca Emir'in açık onayıyla yapılır.

## Kuyruk
| ID | Görev | Sahip | Öncelik | Durum | Tarih (TSİ) | Sonuç / kanıt |
|---|---|---|---|---|---|---|
| T-20261104-01 | 08:00 Short "Antikythera" üret (hat testi) | Claude | P0 | devam | 04.11 00:10 | `videolar/2026-11-04_0800_antikythera-mechanism/` |
| T-20261104-02 | 12:00 Short "Lake Nyos" üret | Claude | P0 | açık | 04.11 | girdiler hazır |
| T-20261104-03 | 16:00 Short "Venus" üret | Claude | P0 | açık | 04.11 | girdiler hazır |
| T-20261104-04 | 20:00 Short "What if Gibraltar closed" üret | Claude | P0 | açık | 04.11 | girdiler hazır |
| T-20261104-05 | 4 Short'un senaryo, hook, kaynak ve SEO incelemesi (`paket.json`, `02_sources.md`, `anlatim_performans.json`) | ChatGPT | P0 | açık | 04.11 | sonucu `CHATGPT_REPORT.md`'ye |
| T-20261104-06 | 5 Kasım 4 Short konusu + kaynaklı senaryo (aynı klasör şablonu) | ChatGPT | P0 | açık | 04.11 | `videolar/2026-11-05_HHMM_<slug>/` |
| T-20261104-07 | Haftalık uzun video (Pazar 8 Kas 19:00) senaryosu + bölümler; aday `plan/en/longform_2026-11-08_voyager.md` | ChatGPT | P1 | açık | 04.11 | |
| T-20261104-08 | Uzun video render hattı (8–12 dk, `short_uret.py` 16:9 / bölüm desteği) | Claude | P1 | açık | 04.11 | |
| T-20261104-09 | Piper sesini dinle; onay ya da ret | Emir | P0 | açık | 04.11 | `ses/LISANS.txt` → `yayin_uygun` |
| T-20261104-10 | Depoyu Private yap (GitHub → Settings → Danger zone) | Emir | P0 | açık | 04.11 | Claude'un isteği güvenlik denetimi tarafından engellendi |
| T-20261104-11 | YouTube kanalını vidIQ'da yetkilendir | Emir | P1 | açık | 04.11 | `vidiq_user_channels` boş |
| T-20261104-12 | Claude ↔ ChatGPT canlı mesajlaşma: Cloudflare Worker + Durable Objects tasarımı + mock testler | Claude | P2 | açık | 04.11 | `NEXT_ACTIONS.md` N-07 |
| T-20261104-13 | "Antikythera" telaffuzu: Piper "anti-kippurum" diyor → `soyle` alanında fonetik yazımı düzelt | Claude | P1 | açık | 04.11 | `cikti/telaffuz.json` |
