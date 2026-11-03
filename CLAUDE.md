# CLAUDE.md — novex.studio

Bu depo NØVEX'in (Türkçe, sinematik, belgesel tarzı dikey video kanalı) Claude × ChatGPT ortak üretim alanıdır.
Önce `README.md` ve `CALISMA_DUZENI.md` dosyalarını izle; bu dosya yalnızca Claude'a özgü kuralları özetler.

## Rol
Claude üretim ve teknik tarafı yürütür: senaryo taslağı, ElevenLabs seslendirme/görsel/video, kurgu, ses tasarımı,
render, teknik QC ve yayın paketi. ChatGPT eleştirir ve doğrular (`inceleme_chatgpt.md`). Son onay Emir'dedir.

## Kesin kurallar
- **Yayın yok:** YouTube, TikTok, Instagram'a yükleme, paylaşım, silme veya değiştirme Emir'in açık onayı olmadan yapılmaz.
- **Gizli bilgi yok:** API anahtarı, token, parola, imzalı bağlantı (`Signature=`, `oobCode=`) depoya yazılmaz. Commit'ten önce tara.
- **Büyük dosya yok:** MP4/WAV/MP3/MOV depoya girmez (`.gitignore`). Depoda QC raporu, kontrol kareleri ve SHA-256 durur.
- **Doğruluk:** Her rakamın `02_kaynaklar.md`'de kaynağı olur; doğrulanmamış iddia ⚠️ ile işaretlenir; varsayım gerçek gibi sunulmaz.
- **Kredi:** ElevenLabs'te uzun/çoklu video üretiminden önce `estimate_only` ile fiyat alınır ve Emir'e sorulur. Başarısız üretim yeniden denenmeden önce Emir'e bildirilir.
- **Dürüst rapor:** Yapılmayan render, yükleme veya kontrol yapılmış gibi yazılmaz.

## Teknik standart (kısa)
1080×1920 · 30 FPS · H.264 High · yuv420p · Rec.709 etiketli · AAC 48 kHz · −14 LUFS · true peak ≤ −1 dBTP ·
metinler x 140–940, y < 1520 · konuşma fonun ≥ 12 dB üstünde · siyah/donuk kare yok. Kontrol: `python3 araclar/qc.py <video.mp4>`.

## Commit
- Doğrudan `main`; küçük ve ayrık commit'ler; mesaj biçimi `[claude] <video veya alan>: <ne>`.
- Her oturum sonunda `GUNLUK.md`'ye bir satır.
- ChatGPT/Codex dalları (`chatgpt/...`) Claude tarafından birleştirilmez; Emir birleştirir.
