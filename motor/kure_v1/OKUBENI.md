# NØVEX — Türkiye Antarktika'da Olsaydı? (Shorts #2)

İlk video ("Türkiye, Amerika'nın Yerinde Olsaydı?") bu klasöre dahil değil ve ona dokunulmadı.

## Teslim dosyaları (`out/`)
| Dosya | Ne |
|---|---|
| `novex_antarktika.mp4` | Final video: 1080×1920, 30 FPS, H.264 + AAC, 30,0 sn, altyazılar görüntüye gömülü |
| `kapak.jpg` | 1080×1920 kapak |
| `altyazi_tr.srt` | YouTube'a ayrıca yüklenebilir Türkçe altyazı |
| `muzik_efekt.wav` | Müzik + efekt sesi (−14 LUFS). Seslendirme gelince miks için ayrı tutuldu |
| `scenes/s1..s6.mp4` | Sahne dosyaları |

Senaryo, zaman kodlu sahne planı ve kaynaklar: `senaryo.md`.

## Seslendirme durumu
Bu video için bir seslendirme kaydı verilmedi; yeni yapay ses de üretilmedi. Video şu an müzik,
efekt ve kelime kelime açılan altyazılarla çalışıyor. Seslendirme eklemek için:

1. `senaryo.md` içindeki metni, tablodaki zamanlara uyacak hızda kaydet (ElevenLabs "Adam" vb.).
   Toplam ~95 kelime / 30 sn ≈ dakikada 190 kelime; hızlı ama Shorts için olağan.
2. Kaydı `assets/seslendirme.mp3` olarak koy ve:
   ```bash
   ./mix_voice.sh assets/seslendirme.mp3
   ```
   Müzik konuşma sırasında otomatik kısılır (sidechain), video yeniden kodlanmaz.
   Kaydın süresi 30 sn'den belirgin farklıysa altyazı zamanlarını (`src/render.py` → `CAPS`)
   kayda göre güncelleyip yalnızca ilgili sahneleri yeniden render et.

## Yeniden render
```bash
python3 src/render.py frame 4.0 test.jpg          # tek kare kontrol
./render_all.sh                                   # 6 sahne, 2 paralel işlem
python3 src/audio.py out/muzik_efekt_raw.wav      # müzik + efekt sentezi
./assemble.sh                                     # birleştir + ses + doğrula
python3 src/extras.py                             # SRT + kapak (KAPAK_T=saniye ile kare seç)
```
Gerekenler: Python 3 (numpy, opencv-python, Pillow), FFmpeg, Inter fontu.

## Lisanslar
- Harita: Natural Earth (kamu malı).
- Doku/görüntü: kodla üretildi (Natural Earth verisinden prosedürel buz dokusu).
- Müzik ve efektler: `src/audio.py` ile sentezlendi; üçüncü taraf ses yok.
- Font: Inter (SIL Open Font License).

## Sınırlar (açıkça)
- Gerçek hava çekimi/stok video kullanılmadı: ortamda lisanslı görüntü indirme imkânı yok.
  Tüm sahneler 3B küre render motoruyla gerçek coğrafi veriden üretildi.
- Blender/Remotion kullanılmadı; render Python (numpy + OpenCV) + FFmpeg ile yapıldı.

## Sürümler
- **V1** `out/novex_antarktika.mp4` — ilk teslim (renk etiketi yok, 5 altyazı satırı sağ buton alanına taşıyor).
- **V2** `out/v2/novex_antarktika_V2.mp4` — Rec.709 dönüşüm + etiket; altyazılar x 140–940 güvenli alanda;
  altyazı geçişleri üst üste binmiyor. QC: `out/v2/qc_rapor.md`. Kapak: `out/kapak_v2.jpg`.
  Yeniden render: `OUTDIR=out/v2/scenes ./render_all.sh`, kontrol: `python3 qc.py <video.mp4>`.
- **FINAL (V3)** `out/v3b/NOVEX_Antarktika_FINAL.mp4` — 36,8 sn, Türkçe erkek seslendirme (yerel, ücretsiz:
  Coqui tr Glow-TTS + tr HiFiGAN, MIT; PyTorch'suz NumPy çıkarımı `~/numtts`). Görüntü seslendirmeye göre
  yeniden zamanlandı (`src/render_v3.py`), altyazılar kelime kelime sese kilitli. Müzik/efekt ayrı katman
  (`src/audio_v3.py`), konuşmada otomatik kısılır (`mix_v3.sh`), −14 LUFS / −1,5 dBTP.
  Sıra: `python3 src/narration.py out/v3b --plan` → `TL=out/v3b/zaman_cizelgesi.json OD=out/v3b/scenes ./render_v3_all.sh`
  → `python3 src/audio_v3.py out/v3b/zaman_cizelgesi.json out/v3` → `./mix_v3.sh` → birleştir → `python3 qc.py`.
