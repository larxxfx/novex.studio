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
| T-20261104-01 | 08:00 Short "Antikythera" üret (hat testi) | Claude | P0 | tamam | 04.11 00:10 | c383c96; QC 10/10; teslim edildi |
| T-20261104-02 | 12:00 Short "Lake Nyos" üret | Claude | P0 | tamam | 04.11 | c383c96; QC 10/10; teslim edildi |
| T-20261104-03 | 16:00 Short "Venus" üret | Claude | P0 | tamam | 04.11 | c383c96; QC 10/10; teslim edildi |
| T-20261104-04 | 20:00 Short "What if Gibraltar closed" üret | Claude | P0 | tamam | 04.11 | c383c96; QC 10/10; teslim edildi |
| T-20261104-05 | PR #2 + 4 Short.un senaryo, hook, kaynak ve SEO incelemesi (`paket.json`, `02_sources.md`, `anlatim_performans.json`) | ChatGPT | P0 | açık | 04.11 | sonucu `CHATGPT_REPORT.md`'ye |
| T-20261104-06 | 5 Kasım 4 Short konusu + kaynaklı senaryo (aynı klasör şablonu) | ChatGPT | P0 | açık | 04.11 | `videolar/2026-11-05_HHMM_<slug>/` |
| T-20261104-07 | Haftalık uzun video (Pazar 8 Kas 19:00) senaryosu + bölümler; aday `plan/en/longform_2026-11-08_voyager.md` | ChatGPT | P1 | açık | 04.11 | |
| T-20261104-08 | Uzun video render hattı (8–12 dk, `short_uret.py` 16:9 / bölüm desteği) | Claude | P1 | açık | 04.11 | |
| T-20261104-09 | Piper sesini dinle; onay ya da ret | Emir | P0 | açık | 04.11 | `ses/LISANS.txt` → `yayin_uygun` |
| T-20261104-10 | Depoyu Private yap (GitHub → Settings → Danger zone) | Emir | P0 | açık | 04.11 | 4 Kas 09:05 hâlâ PUBLIC; `strateji/DEPO_GUVENLIK_2026-11-04.md` |
| T-20261104-11 | YouTube kanalını vidIQ'da yetkilendir | Emir | P1 | açık | 04.11 | `vidiq_user_channels` boş |
| T-20261104-12 | Claude ↔ ChatGPT canlı mesajlaşma (Cloudflare) | Claude | P2 | engelli | 04.11 | Claude ortamı workers.dev erişemiyor; strateji/CANLI_ILETISIM_MIMARISI.md |
| T-20261104-13 | Telaffuz düzeltmesi (en iyi 3 seçim + fonetik yazım), 4 Short sesini yeniden üret | Claude | P1 | tamam | 04.11 | `cikti/anlatim/secim.json` |
| T-20261104-14 | Venus Short v2: Norman erkek ses + 3D gezegen sahnesi + katılım sorusu (Mars/Mercury) | Claude | P0 | tamam | 04.11 02:30 | `videolar/2026-11-04_1600_venus-day-longer-than-year/cikti/qc_rapor.md` (teknik 10/10) |
| T-20261104-15 | Norman sesini (en_US-norman-medium) dinle; onay ya da ret | Emir | P0 | açık | 04.11 | 4 videonun MP3'ü sohbette; lisans: LibriVox kamu malı + MIT; `ses/LISANS.txt` |
| T-20261104-16 | Diğer 3 Short'u yeni kalite standardına taşı (3D sahne, erkek ses, katılım sonu) | Claude | P1 | tamam | 04.11 10:45 | 4/4 gerçek MP4, teslim_dogrula çıkış 0, 9/9 somut görsel; `QUALITY_CONTROL.md`, `videolar/*/REFERANS_QC.md` |
| T-20261104-17 | Kalite standardı + katılım sorusu kalıcı belgelere (CLAUDE.md, NOVEX_MASTER, standart §10, referans kaydı) | Claude | P0 | tamam | 04.11 09:00 | `CLAUDE.md`, `strateji/GORSEL_REFERANS.md`, `d6fddc5` |
| T-20261104-18 | Teslim doğrulayıcı (MP4/kapak/SRT/paket/katılım/3D/lisans) + testler | Claude | P0 | tamam | 04.11 09:00 | `araclar/teslim_dogrula.py`, `testler/test_teslim_dogrula.py` 12/12 |
| T-20261104-19 | 5 zamanlanmış görevi yeni standarda güncelle; çalışma kanıtı | Claude | P0 | tamam | 04.11 09:02 | 08:00 çalıştı → `596d53e` (eski stil); talimatlar 09:02'de güncellendi |
| T-20261104-20 | Depo PUBLIC güvenlik kontrolü | Claude | P0 | tamam | 04.11 09:05 | `strateji/DEPO_GUVENLIK_2026-11-04.md` (anahtar yok, e-posta çıkarıldı) |
| T-20261104-22 | "What If Turkey Were in America?" MP4'ünü sohbete ekle (referans kaydı) | Emir | P2 | tamam | 04.11 10:52 | SHA-256 8850c1d6…; `strateji/referans/turkey_america_*.jpg` |
| T-20261104-23 | Uzun video hattı (16:9, bölümler, uzun QC) | Claude | P1 | açık | 04.11 | N-06; haftalık görev Cmt 10:13'te önce hattı kuracak |
| T-20261104-24 | Kalıcı kalite yükseltmesi: `foto` sahnesi (2.5D parallax, köken etiketi) + somut görsel/gelişim hedefi/tekrarsız soru denetimi + NARRATION/görsel kaynak paketi | Claude | P0 | tamam | 04.11 10:45 | `testler/test_foto_sahne.py` 3/3, `test_teslim_dogrula.py` 18/18; `strateji/GORSEL_URETIM_SISTEMI.md` |
| T-20261104-25 | Her video için sahne görsel promptları (`gorsel_promptlari.md`) + kamu malı fotoğraf önerileri | ChatGPT | P1 | açık | 04.11 | `CHATGPT_REPORT.md` istek bölümü |
| T-20261104-26 | Kamu malı fotoğraf/görselleri sohbete ekle (Wikimedia/NASA bu ortamdan erişilemiyor) veya ücretli görsel üretimine onay ver | Emir | P1 | açık | 04.11 | `strateji/GORSEL_URETIM_SISTEMI.md` §3 |
| T-20261104-27 | Dünya yakın planı: parlayan kıyı/sınır çizgisi ve daha keskin doku (N-16) | Claude | P2 | açık | 04.11 | Nyos/Gibraltar REFERANS_QC eksikleri |
| T-20261104-28 | Referans analizi + imza öğeleri motora (ülke vurgusu/taşıma, yorum rozeti, kapanış kartı) | Claude | P0 | tamam | 04.11 11:20 | `strateji/GORSEL_REFERANS.md`, `testler/test_bolge_bitis.py` 3/3 |
| T-20261104-29 | NASA Blue Marble gündüz + bulut + gece ışıkları dokularını sohbete ekle | Emir | P0 | açık | 04.11 | N-19 |
| T-20261104-30 | Doku gelince 4 Short'u ülke vurgusu + kapanış kartı + gerçekçi Dünya ile yeniden render | Claude | P1 | açık | 04.11 | T-20261104-29'a bağlı |
