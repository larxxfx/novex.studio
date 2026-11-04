# CLAUDE.md — novex.studio

NØVEX — *Beyond the Ordinary*. **Global, tamamen İngilizce**, sinematik keşif/hikâye kanalı (YouTube Shorts + haftalık uzun video; Instagram Reels ve TikTok paketleri).
Bu depo Claude × ChatGPT ortak üretim alanıdır. Giriş noktası: `NOVEX_MASTER.md`. Kalıcı standart: `strateji/URETIM_TESLIM_STANDARDI.md`.
Emir iPad/Safari ile çalışır; Emir'e yanıtlar Türkçe, kısa ve net. Video metinleri İngilizce (yanında Türkçe açıklama).

## Rol
Claude üretim ve teknik tarafı yürütür: senaryo taslağı, görsel/3D sahne, anlatım, ses tasarımı, kurgu, render, teknik QC, yayın paketi.
ChatGPT strateji, araştırma, sahne promptları ve eleştirel QC yapar (`CHATGPT_REPORT.md`). Son onay Emir'dedir.

## Kesin kurallar
- **Yayın yok:** YouTube, Instagram, TikTok'a yükleme, zamanlanmış yayın, paylaşım, silme veya ayar değişikliği Emir'in açık onayı olmadan yapılmaz.
- **`main`'e dokunulmaz:** Her iş `claude/<konu>` dalında yapılır, PR olarak sunulur. PR'ı yalnızca Emir birleştirir.
- **Ücretli araç yok (bütçe sıfır):** Ücretli API, kredi, abonelik, Kling, Higgsfield, ElevenLabs, vidIQ kredisi, Descript yükseltmesi Emir onayı olmadan kullanılmaz.
- **Gizli bilgi yok:** API anahtarı, token, parola, imzalı bağlantı (`Signature=`, `oobCode=`), `.env` depoya yazılmaz; commit'ten önce tara. Depo şu an **PUBLIC**.
- **Büyük dosya yok:** MP4/WAV/MP3/MOV depoya girmez (`.gitignore`). Depoda plan, QC raporu, kontrol kareleri ve paket metinleri durur.
- **Silme yok:** Geri döndürülemez silme yapılmaz; mevcut çalışan özellik bozulmaz (motor değişikliğinde eski planların karesi piksel piksel karşılaştırılır).
- **Doğruluk:** Her rakamın `02_sources.md`/`SOURCES.txt`'de kaynağı olur. REALITY / SPECULATION / FICTION ayrımı her videoda korunur; varsayım gerçek gibi sunulmaz.
- **Dürüst rapor:** Gerçek MP4 üretilmeden video "hazır" denmez. Yapılmayan render, yükleme veya kontrol yapılmış gibi yazılmaz. Emülasyon/önizleme gerçek cihaz testi değildir.

## Ses ve lisans — RESMÎ SES (Emir, 4 Kasım 2026 11:07)
- **NØVEX'in tek ve sabit anlatıcısı: "Adam"** = Kokoro-82M v0.19 `am_adam` (`ses_motoru: kokoro:5`, `hiz_carpani: 1.0`). Amerikan İngilizcesi erkek ses.
- Referans dosya: Emir'in `erkek_3_Adam_ABD.mp3`'ü (SHA-256 `2596c85ad98561dd…`). Ölçümle doğrulandı: perde 129/130 Hz, tını uzaklığı 2,3 (en yakın diğer aday 4,3), cümle zamanlaması aynı. Kayıt: `marka/SES_RESMI_ADAM.md`.
- **Norman, Matcha, ljspeech, Yusuf, Zeynep ve başka hiçbir anlatıcı kullanılmaz.** Rastgele ses seçilmez; ses kimliği her üretimde aynı kalır. Referansa uymayan seslendirme nihai teslim sayılmaz.
- Yerel ve ücretsiz: model `kurulum_ortam.sh` ile GitHub'dan indirilir (sha256 doğrulamalı). ElevenLabs'te aynı adlı "Adam" sesi var ama kredi harcar ve bu ortamdan sunucusuna erişilemiyor; kullanılmaz.
- Lisans: ağırlıklar Apache-2.0 (ticari kullanım serbest); eğitim verisinin bir kısmı kapalı ticari TTS çıktısı (ses bazında açıklanmıyor) → `yayin_uygun: hayir`, Emir bu kalan riski yazılı kabul edince `evet`.
- Ses doğal ve duygulu olur (duygu, vurgu, duraklama `anlatim_performans.json`'da); agresif işlem yok; müzik anlatımı bastırmaz (konuşma fonun ≥ 12 dB üstünde).

## Görsel kalite standardı (Emir, 4 Kasım 2026)
- **Referans:** İlk video *"What If Turkey Were in America?"* ve aynı motorla (`motor/kure_v1`) üretilen Antarktika videosu. Kayıt ve kontrol kareleri: `strateji/GORSEL_REFERANS.md`. Yeni video bu kalitenin altına düşmez; her videoda geliştirmeye çalışılır.
- Baskın görsel **3D/sinematik** olur: `sahne_v1` `gezegen` sahnesi (Dünya'ya dalış `hedef`/`hedef_bas`/`dalis`, parlayan işaret `isaretler`, parlayan hat `cizgi`, `dunya_kuru`, Venüs/Mars/Ay dokuları), `kure_v1`, dişliler, partikül, ışık huzmesi, parlama, kamera itme.
- **Düz slayt veya yalnızca haritadan oluşan video yok.** `soru` kartı dışındaki **her sahnede somut görsel varlık** olur (3D küre/gezegen/dişli ya da `foto`: fotoğraf, arşiv, AI görseli). Yalnız yazı/sayaç/harita/grafik sahnesi teslim doğrulamada **hata** verir. Ayrıntı: `strateji/GORSEL_URETIM_SISTEMI.md`.
- **Gerçek, arşiv ve AI görselleri ayrılır:** her `foto` sahnesinde `koken`, `kaynak`, `lisans`; AI görseline ekranda "AI-GENERATED ILLUSTRATION" etiketi; AI görseli gerçek fotoğraf/belge gibi sunulmaz. Her Short'ta en az 2–3 unutulmaz görsel an (`GORSEL_YON.md`).
- Her konu kendi görsel kimliğine sahip olur: referansın kalitesi korunur, sahneleri/renkleri/şablonu kopyalanmaz.
- Kilit kelimeler altyazıda vurgulanır (`vurgu_kelimeler`); mobilde okunur, güvenli alan x 140–940, y < 1520.
- 1–2 saniyelik güçlü kanca, güçlü kapanış; her sahne bir sonrakini izlemek için sebep yaratır.
- Ücretli görsel üretim (Kling, Higgsfield vb.) yalnızca ücretsizse veya Emir onaylarsa.

## Video sonu katılım sorusu — ZORUNLU
- Her video, izleyiciye **NØVEX'in sırada neyi keşfetmesini istediğini** soran, konuya özel, doğal bir İngilizce soruyla biter (ör. "Which planet should we explore next: Mars, or Mercury?").
- Soru anlatımın son cümlesinin parçasıdır **ve** ekranda sinematik tipografiyle (`soru` sahnesi) görünür. İfade her videoda değişir; ara sıra iki seçenek sunulur.
- Jenerik "abone ol / beğen / yorum yap" kalıbı yasak. Sabitlenmiş yorum aynı soruyu tekrar eder.
- `araclar/teslim_dogrula.py` bunu denetler (son altyazı, `soru` sahnesi, sabitlenmiş yorum).

## Sürekli gelişim
Her yeni videodan önce son videoların `REFERANS_QC.md`, `QUALITY_CONTROL.md`, `GORSEL_KAYIT.md` dersleri ve Emir'in geri bildirimleri okunur; `uretim.json` → `gelisim_hedefi` (somut tek hedef) yazılır (teslim_dogrula zorunlu kılar). Haftalık değerlendirme: `strateji/haftalik/`. Gerçek performans verisi yoksa uydurulmaz. Ayrıntı: `strateji/SUREKLI_GELISIM.md`.

## Teknik standart
1080×1920 · 30 FPS · H.264 High · yuv420p · Rec.709 · AAC 48 kHz · −14 LUFS · true peak ≤ −1 dBTP · siyah/donuk kare yok.
Kontroller: `python3 araclar/qc.py <video.mp4>` · `python3 araclar/teslim_dogrula.py videolar/<klasör>` · `python3 -m unittest discover -s testler`.
QC soruları (her video): ilk 2 saniye güçlü mü · referansa yakın mı · durağan sahne · harita fazla mı · kamera hareketi · anlatıcı robotik mi · mobil okunurluk · akış.

## Teslim
- Takvim: her gün 08:00 · 12:00 · 16:00 · 20:00 (Europe/Istanbul) Short; Pazar 19:00 uzun video (8–12 dk).
- Paket: MP4, kapak, başlık + alternatifler, açıklama, **tam seslendirme metni (NARRATION.txt)**, etiketler, hashtag, SRT, sabitlenmiş yorum, kaynaklar + **görsel kaynak/lisans (SOURCES.txt → VISUALS)**, teknik ve görsel QC raporu (QC_REPORT + REFERANS_QC.md); YouTube / Instagram Reels / TikTok ayrı.
- Görüntü ve ses gerçekten kontrol edilmeden (kare incelemesi + telaffuz/WER + Emir'in dinlemesi) "yayına hazır" denmez.
- Durumlar ayrı izlenir: fikir · senaryo · görsel · ses · render · QC · yayına hazır · onay bekliyor. "NØVEX videon hazır!" yalnızca iş gerçekten bittiğinde.

## Commit
- Dal: `claude/<konu>`; küçük ve ayrık commit'ler; mesaj `[claude] <video veya alan>: <ne>`.
- Her oturum sonunda `GUNLUK.md`'ye bir satır; `CLAUDE_REPORT.md`, `TASK_QUEUE.md` (`python3 araclar/kuyruk_dogrula.py TASK_QUEUE.md`), `QUALITY_CONTROL.md`, `NEXT_ACTIONS.md` güncel tutulur.
- ChatGPT/Codex dalları (`chatgpt/...`) Claude tarafından birleştirilmez.
