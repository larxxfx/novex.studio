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

## 2026-11-04 02:30 · Venus Short v2 (yeni kalite standardı)
- Ses: Piper `en_US-norman-medium` (erkek, LibriVox kamu malı + MIT). Emir onayı bekliyor (T-20261104-15).
- Görsel: `sahne_v1` içinde yeni `gezegen` sahnesi (ışın izlemeli küre, prosedürel doku, atmosfer, dönüş), partikül, ışık huzmesi, parlama, vurgu kelimeli altyazı.
- Kapanış: "Which planet should NØVEX explore next? Mars or Mercury?" (anlatım + ekran yazısı).
- QC: teknik 10/10, −13.9 LUFS, TP −1.6, konuşma/fon ≥ 15.5 dB, telaffuz WER %1,0. Lisans: GEÇMEDİ (onay yok) → yayına hazır DEĞİL.
- Düzeltilen: MERCURY kutu taşması, gezegen üstü etiket kontrastı, kapakta çift yazı. Eski 3 Short'un kapakları byte-aynı (regresyon yok).
- Referansla fark: kure_v1 (Antarktika) kamera dalışları ve parlak kıta hatları burada yok; gezegen dokusu prosedürel ve yumuşak. Sonraki adım: Dünya konulu Short'larda kure_v1 / `dunya` dokusu.

## 2026-11-04 10:50 · Kalite standardı kalıcı + 4 Short yeni standartta + kalite yükseltmesi (dal `claude/kalite-standardi`)
**Tamamlanan (kanıtlı)**
- Kalıcı kurallar: `CLAUDE.md` (eskimiş Türkçe/Yusuf-Zeynep/main'e commit kuralları güncellendi), `NOVEX_MASTER.md`, `strateji/URETIM_TESLIM_STANDARDI.md` §10–11, `strateji/GORSEL_REFERANS.md` (+3 kontrol karesi), `strateji/GORSEL_URETIM_SISTEMI.md`, `strateji/SUREKLI_GELISIM.md`, `strateji/haftalik/2026-W45.md`.
- Motor: `gezegen` Dünya'ya dalış (`hedef/hedef_bas/dalis`), nabızlı işaret, parlayan hat, dişliler, kurumuş Akdeniz (`dunya_kuru`), Dünya dokusu boylam hatası düzeltildi (180° kayma: kamera Pasifik'e dalıyordu), uzun seçenekler alt alta; **yeni `foto` sahnesi** (2.5D parallax, Ken Burns, sis; AI görseline kapatılamaz etiket). Eski planlar piksel piksel aynı (Venüs, Nyos fark 0).
- Hata düzeltmeleri: kamera yönü `hash()` → belirlenimli (paralel parçalarda sıçrama); Whisper sabit geçici dosyası (eşzamanlı üretimde yanlış çekim seçimi) ×2; Venüs `LISANS.txt` yanlış sesi (ljspeech) gösteriyordu → Norman.
- `araclar/teslim_dogrula.py`: MP4/kapak/SRT/paket/katılım sorusu/3D oranı/ses-lisans tutarlılığı/**somut görsel**/foto kaynak-lisans-köken/**gelişim hedefi**/**tekrarsız kapanış sorusu**. Paket: `NARRATION.txt` + SOURCES `VISUALS`.
- 4 Short (gerçek MP4, Norman, 9/9 somut 3D sahne, konuya özel "next" sorusu): teslim_dogrula çıkış 0; teknik QC 10/10; kareler referansla incelendi (`videolar/*/REFERANS_QC.md`).
- Zamanlanmış görevler: 08:00 görevi 05:47'de gerçekten çalıştı (`596d53e`, eski stil yeniden render) → 5 görevin talimatı 09:02'de yeni standarda güncellendi.
- Depo güvenliği: PUBLIC; 34 commit'te anahtar yok; kişisel e-posta güncel dosyalardan çıkarıldı (`strateji/DEPO_GUVENLIK_2026-11-04.md`).
- Testler: `python3 -m unittest discover -s testler` → **36/36 OK**; `kuyruk_dogrula` OK.

**Yayına hazır video: YOK** — Norman sesi Emir onayı bekliyor (`yayin_uygun: hayir`).
**Engeller:** gerçek/arşiv görsel kaynaklarına erişim yok (N-17); uzun video hattı yok (N-06); depo public (N-09); Instagram/TikTok/R2/vidIQ kanal yetkisi yok.
**Geri dönüş:** `claude/kalite-standardi` birleştirilmezse `claude/uretim-hatti` (`596d53e`) olduğu gibi kalır; motor değişikliği geri alınacaksa `2b8ee07`.

## 2026-11-04 11:20 · Gerçek referans video kaydedildi ve analiz edildi
- "What If Turkey Were in America?" (Emir'in MOV'u): SHA-256 `8850c1d6…a76b`, 720×1280 HEVC, 35,6 sn; 12 kontrol karesi `strateji/referans/turkey_america_*.jpg`; özellik analizi + 4 Short ile dürüst karşılaştırma `strateji/GORSEL_REFERANS.md`.
- Sonuç: 4 Short referansın **altında** — en büyük fark gerçekçi uydu Dünya dokusu (bizimki prosedürel gri), arazi uçuşları ve gerçek görsel varlıklar.
- Motora eklenenler (eski planlar piksel piksel aynı, fark 0): `bolge` ülke vurgusu (Natural Earth, parlayan sınır + dolgu), `tasi` What If taşıma (kuzey yukarıda, gerçek boyut; ilk sürümdeki 90° dönme hatası düzeltildi), `yorum_rozeti`, `bitis_karti`. Testler: `test_bolge_bitis.py` 3/3.
- Engel: NASA Blue Marble dokusu bu ortamdan indirilemiyor → Emir eklemeli (N-19).

## 2026-11-09 19:10 · Claude → ChatGPT: DURUM ANALİZİ ve ÜRETİM DURAKLATMASI
**Emir'in kararı (9 Kas 19:05): NØVEX video üretimi tamamen DURAKLATILDI. Emir yeni bir talimat verene kadar hiçbir video işi başlatılmayacak (senaryo, render, ses, paket dahil). Lütfen sen de yeni video görevi açma; yeni konular Emir'le konuşulacak.**

### 4–9 Kasım'da gerçekte ne oldu (kanıtlı)
| Konu | Durum | Kanıt |
|---|---|---|
| Resmî ses | **"Adam" = Kokoro v0.19 am_adam (`kokoro:5`, hız 1.0)**. Emir 4 Kas'ta seçti; Norman ve diğer sesler yasak. Referans MP3 ile ölçüm: perde 129/130 Hz, en yakın aday. | `14a3243` (bu dal), `marka/SESLENDIRME.md`; ayrıntılı ölçüm `claude/yedek-2026-11-04-adam` dalında `marka/SES_RESMI_ADAM.md` |
| 08:00 Antikythera (Adam sesi) | Gerçek MP4 üretildi, teknik QC 10/10, Emir'e gönderildi (4 Kas 11:30) | MP4 git dışı; plan `videolar/2026-11-04_0800_antikythera-mechanism` |
| 12:00 Lake Nyos (Adam sesi) | Gerçek MP4 üretildi (4 Kas 11:44), QC 10/10, telaffuz WER %2,5 — **Emir'e gönderilmedi** | Yalnız Claude'un çalışma alanında |
| 16:00 Venüs | Adam sesi üretildi, **render yarıda kaldı** (yalnız Norman sesli eski MP4 var — kullanılamaz) | — |
| 20:00 Cebelitarık | Adam sesiyle **hiç üretilmedi** (eski Norman sesli MP4 — kullanılamaz) | — |
| 5–9 Kas zamanlanmış görevler | **Hiçbiri üretmedi.** Hepsi tetiklendi ama ~6 sn'de "usage limit reached" hatasıyla düştü (son: 9 Kas 05:47 / 09:44 / 13:18 / 16:30; haftalık görev 7 Kas). Depoya 4 Kas 08:08'den beri commit yok. | Görev çalışma kayıtları: `ROUTINE_RUN_FAILURE_REASON_USAGE_LIMIT_REACHED` |
| Uzun video (Pazar 8 Kas) | Üretilmedi (görev kullanım sınırına takıldı; uzun video hattı zaten kurulmamıştı) | — |
| PR'lar | #2 (`claude/uretim-hatti`→main) ve #3 (`claude/kalite-standardi`→`claude/uretim-hatti`) açık, birleştirilmedi | GitHub |
| Depo | Hâlâ **PUBLIC** | `gh api` 9 Kas |

### Yarım kalan / tutarsız noktalar (karar Emir'de, kimse kendiliğinden düzeltmesin)
1. **İki paralel Claude oturumu** 4 Kas'ta aynı kararı uyguladı: `14a3243` (uzak dalda) ve `452b9bb` (çakıştığı için itilemedi → `claude/yedek-2026-11-04-adam` dalında saklandı; Adam ölçüm kaydı, GOREV_SHORT/UZUN talimat dosyaları, 4 Short'a ülke sınırı vurgusu + yorum rozeti + NØVEX kapanış kartı). Birleştirilmedi.
2. Ses lisans kaydı iki oturumda farklı: `14a3243` → `yayin_uygun: evet`; `452b9bb` → `hayir` (Kokoro eğitim verisindeki gri alan; Emir'in açık risk kabulü bekleniyor).
3. Zamanlanmış görevler hâlâ **etkin**; 12:00 görevinin talimatı hâlâ Norman sesini yazıyor (diğer üçü ve haftalık görev Kokoro'ya güncellenmiş). Emir'e duraklatma soruldu, yanıt bekleniyor.

### ChatGPT'den istenen
- Yeni video, senaryo veya sahne promptu görevi **açma**. TASK_QUEUE'daki açık video görevlerini "beklemede" say.
- Bu raporu okuduğunu `CHATGPT_REPORT.md`'ye kısa bir satırla yaz; Emir'in yeni konusu gelince ondan devam ederiz.
