# NØVEX — Master (giriş noktası)

NØVEX — Beyond the Ordinary. Global, tamamen İngilizce. **Kalıcı hedef (Emir, 3 Kas 2026):**
- **Günde 4 özgün Short:** 08:00 · 12:00 · 16:00 · 20:00 Europe/Istanbul
- **Haftada 1 uzun video:** 8–12 dk, Pazar 19:00

Bu dosya kuralları tekrar etmez; doğru belgeye yönlendirir.

| Konu | Belge |
|---|---|
| Kalıcı üretim/teslim standardı, durum tanımları, yaratıcı evrim | `strateji/URETIM_TESLIM_STANDARDI.md` |
| Ana operasyon talimatı (Emir) / ChatGPT master talimatı | `strateji/ANA_OPERASYON_TALIMATI.md` · `strateji/CHATGPT_MASTER_DIRECTIVE.md` |
| Editoryal strateji, kategoriler, REALITY/SPECULATION/FICTION | `strateji/EDITORIAL_STRATEGY.md`, `strateji/kategoriler.json` |
| **Görsel kalite referansı** (What If Turkey Were in America? / kure_v1) | `strateji/GORSEL_REFERANS.md` · `strateji/KALITE_STANDARDI_4KASIM.md` |
| **Görsel üretim sistemi** (somut görsel zorunlu, foto/AI/arşiv ayrımı, ChatGPT prompt akışı, erişilebilen araçlar) | `strateji/GORSEL_URETIM_SISTEMI.md` |
| **Sürekli gelişim** (gelişim hedefi, haftalık değerlendirme) | `strateji/SUREKLI_GELISIM.md` · `strateji/haftalik/` |
| Görsel tekrar kaydı | `strateji/GORSEL_KAYIT.md` |
| Ses lisansı araştırması | `marka/SES_LISANS_ARASTIRMASI_EN.md` |
| Çalışma düzeni ve inceleme biçimi | `CALISMA_DUZENI.md` · `CHATGPT_TALIMATLARI.md` |
| Ortak görevler / raporlar | `TASK_QUEUE.md` · `CLAUDE_REPORT.md` · `CHATGPT_REPORT.md` |
| Üretim kaydı / QC / sıradakiler / erişim | `PRODUCTION_LOG.md` · `QUALITY_CONTROL.md` · `NEXT_ACTIONS.md` · `TOOL_ACCESS_STATUS.md` |
| Günlük | `GUNLUK.md` |

## Üretim hattı (tek komut)

```
bash araclar/kurulum_ortam.sh                       # temiz oturum: varlıklar + Piper + Whisper (~3 dk)
python3 araclar/short_uret.py videolar/<klasör>     # ses → telaffuz → altyazı → render → ses tasarımı → miks → birleştir → QC → kapak → paket
```

- **Klasör girdileri:** `uretim.json`, `anlatim_performans.json`, `sahne_plani.json`, `paket.json`, `02_sources.md`, `ses/LISANS.txt`, `GORSEL_YON.md`.
- **Örnekler (yeni standart):** `videolar/2026-11-04_1600_venus-day-longer-than-year/` (gezegen), `videolar/2026-11-04_2000_what-if-gibraltar-closed/` (Dünya'ya dalış + kurumuş deniz), `videolar/2026-11-04_0800_antikythera-mechanism/` (dişliler + Ay).
- **Teslim doğrulama:** `python3 araclar/teslim_dogrula.py videolar/<klasör>`.

## Değişmez sınırlar
- Emir'in açık onayı olmadan hiçbir platformda yükleme, yayın ya da zamanlama yok.
- Ücretli servis veya kredi yok.
- Gizli bilgi depoya girmez.
- `main`'e doğrudan değişiklik yok.
- Yapılmayan iş yapılmış gibi raporlanmaz; gerçek MP4 yoksa video hazır değildir.
- **Her video**, konuya özel doğal bir İngilizce "sırada neyi keşfedelim?" sorusuyla biter (anlatım + ekran). Jenerik abone ol çağrısı yok.
- **Resmî ses: "Adam" (Kokoro am_adam, `kokoro:5`)**; Norman ve diğer anlatıcılar yasak. Ayrıntı: `marka/SES_RESMI_ADAM.md`.
- Baskın görsel 3D/sinematik; `soru` kartı dışında her sahnede somut görsel varlık; düz slayt veya yalnız harita videosu yok.
- Gerçek / arşiv / AI görselleri ayrılır, kaynak ve lisans kaydedilir; AI görseli gerçek gibi sunulmaz.
- Her videoda bir `gelisim_hedefi`; kapanış soruları tekrar etmez (teslim_dogrula).

## Hatlar
- **Shorts hattı** (9:16, 30–60 sn): `araclar/short_uret.py` → günde 4.
- **Uzun belgesel hattı** (16:9, 8–12 dk): ayrı hat, henüz kurulmadı (N-06) → haftada 1, Pazar 19:00.
- Teslim edilmiş slot yeniden üretilmez; gerçek MP4 olmadan "hazır" denmez; yayın, ücretli harcama ve PR birleştirme Emir onayıyla.
