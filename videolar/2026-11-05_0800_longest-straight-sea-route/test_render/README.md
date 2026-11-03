# Test render — 3 Kasım 2026 (YAYINA UYGUN DEĞİL)
- Dosya (depoda değil): `NOVEX_ocean_route_TEST_sarah.mp4` sha256 `341c5f7a5ef0f2837e497880b54971252b9d871e8be170aef88416226fd4ce3a` (170 MB, crf 17);
  önizleme `NOVEX_ocean_route_TEST_sarah_preview.mp4` sha256 `9c851d8d70543abd32efc4618719834492a9e376658a6f4c3e9a75733739b4fe` (62 MB, crf 21). İkisi de qc.py: 10/11 ✅, lisans ❌.
- Anlatıcı: Kokoro v0.19 af_sarah (yerel, ücretsiz) — **test amaçlı seçildi, final anlatıcı Emir'in onayında.** Michael için yeniden render ~25 dk.
- Görüntü: `motor/kure_v1/src/rota.py` · ses: `rota_ses.py` (kodla sentez) + `araclar/miks.py` (bu klasördeki miks.json).
- Ölçüm: −14,0 LUFS, true peak −1,8 dBTP; konuşma/fon farkı 17,6–25,3 dB (tümü ≥ 12); siyah/donuk kare yok; 43,46 sn, 1301 kare.
- Aynı metin karşılaştırması (`ses_karsilastirma_michael_sarah.json`, Whisper medium): Michael WER %1,8 (cümle 4 "and it's" → "in its"), 2,67 kel/sn, F0 121 Hz; Sarah WER %0, 2,77 kel/sn, F0 188 Hz.
- Bilinen kusurlar: S6/S7'de Antarktika kutup dokusu benekli; son 0,48 sn kapanış kartı sesin bitişinde kesiliyor; S4 başında çizgi henüz düzleşmemiş (kamera dönüşü).
