# novex.studio — NØVEX · Claude × ChatGPT ortak üretim deposu

Depo: `github.com/larxxfx/novex.studio` (özel)

**NØVEX · Beyond the Ordinary.** Türkçe, sinematik, belgesel tarzı dikey kısa videolar
(YouTube Shorts · TikTok · Instagram Reels).

Bu depo, iki yapay zekânın ve kanal sahibinin **aynı dosyalar üzerinden** çalıştığı tek doğruluk
kaynağıdır. Claude ile ChatGPT arasında doğrudan bir bağlantı yoktur; bağlantı bu depodur.

## Kim, neyi, nereden yapar?

| Taraf | Rol | Depoya erişim | iPad'de nereden |
|---|---|---|---|
| **Emir** (sahip) | Onay, yayın, Descript sesini iPad'den sohbete aktarma (yedek: kendi sesi) | Tam | GitHub uygulaması / Safari / Descript |
| **Yusuf / Zeynep** | Kalıcı ana anlatıcılar (Descript AI Speech) — lisans doğrulanana kadar yayına uygun değil | — | `marka/SESLENDIRME.md` |
| **Claude** | Senaryo taslağı, görsel/video üretimi, ses işleme ve hizalama, kurgu, ses tasarımı, render, teknik QC | Okuma + yazma (doğrudan commit) | Claude uygulaması |
| **ChatGPT** | Fikir karşılaştırma, kaynak doğrulama, senaryo/tutma eleştirisi, başlık stratejisi, son QC | **Okuma**: GitHub bağlayıcısı · **Yazma**: yalnızca Codex üzerinden PR | ChatGPT uygulaması |

ChatGPT'nin GitHub bağlayıcısı **salt okunur**dur. ChatGPT'nin depoya yazması için Codex (Plus ve
üstü, MFA gerekli) kullanılır; Codex yoksa ChatGPT'nin raporu Emir tarafından
`videolar/<video>/inceleme_chatgpt.md` dosyasına yapıştırılır.

## Klasörler

```
marka/            Marka kimliği, ses profili (voice.md), tipografi ve renk kodları
plan/             Haftalık/günlük içerik planları, fikir havuzu
videolar/         Her video için bir klasör (01_brief … 06_paket, qc/, kapak/) — bkz. videolar/README.md
seriler/          son-sinyal/: bible, karakter kartları, süreklilik kaydı, bölüm takibi, uzun film
sablonlar/        Video klasörüne kopyalanan boş dosya şablonları
inceleme/         Haftalık genel değerlendirmeler, performans notları
araclar/          QC betiği, yerel TTS, render yardımcıları
yayin_kaydi.csv   Yayınlanan her içerik (tekrar kontrolünün temeli)
GUNLUK.md         Kim ne yaptı — her oturum sonunda bir satır
CALISMA_DUZENI.md İş akışı, durumlar, dosya adları, inceleme kuralları
```

## Büyük dosyalar

MP4 ve WAV dosyaları **depoya konmaz** (GitHub tek dosyada 100 MB sınırı; depo şişer).
Depoda video başına yalnızca: senaryo, kaynaklar, sahne planı, kontrol kareleri (`qc/*.jpg`),
QC raporu ve dosya özeti (SHA-256, süre, boyut) durur. Final MP4 Claude sohbetinden indirilir.
ChatGPT videoyu izleyemez; kontrol karelerini ve QC raporunu inceler.
