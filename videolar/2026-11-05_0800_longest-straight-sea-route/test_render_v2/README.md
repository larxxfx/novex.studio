# Test render v2 — 3 Kasım 2026 (YAYINA UYGUN DEĞİL) — v1'in yerini alır
- Master (depoda değil): `NOVEX_ocean_route_v2_sarah.mp4` sha256 `4600e987f341eb3ba4dbe5c5fb5248fe5ecdb108dfe02023dfb20621bc7de1cf` (177 MB, crf 17)
- Önizleme: `NOVEX_ocean_route_v2_sarah_preview.mp4` sha256 `383fd8e5de5fdaba4a22299ecadb309259b781994837e0129f5d8cabd6ad5e13` (65 MB, crf 21)
- qc.py (her iki dosya, bu render üzerinde çalıştırıldı): 10/11 ✅ · **lisans ❌** (Kokoro; bkz. `marka/SES_LISANS_ARASTIRMASI_EN.md`)
- 45,23 sn, 1357 kare; ses 45,23 sn (önce: video 43,46'da sesle kesiliyordu). −13,9 LUFS, true peak −1,7 dBTP.
- Konuşma/fon farkı (11 cümle): 17,7–27,3 dB (tümü ≥ 12). blackdetect / freezedetect: bulgu yok.

## v1 → v2 düzeltmeleri (yalnız `src/rota.py`, `src/rota_ses.py`; `render.py` değişmedi)
1. **Antarktika beneği:** render_globe kutup mip seviyesini ekran merkezinden seçiyordu → eğik açıda 4800 px doku aliasing.
   Rota modunda 2 seviye kaba + Gauss/bilateral yumuşatılmış kutup piramidi (POLAR_KM uyarlandı).
2. **S4 eğri çizgi:** kamera artık rota düzleminde sabit (head=0, P=0) → çizgi ilk kareden itibaren düz; yalnız uzaklaşma.
3. **Erken bitiş:** kapanış anlatımdan sonra 2,2 sn tutuluyor, son 0,6 sn siyaha iniş; müzik/ses aynı uzunlukta; mux'ta `-shortest` yok.
4. **Süreklilik:** her sahne sınırında ±0,30 sn çapraz geçiş; km sayacı tek değer olarak sahneler arasında akıyor (çift sayaç yok).

## Kalan görsel konular
- Antarktika artık beneksiz ama Drake/Pasifik geçişinde parlak beyaz büyük kütle olarak görünüyor (dokunun kendisi).
- S10'da "11,241 km" yazısı kürenin üst kenarındaki buzla üst üste geliyor.
- Kamçatka etiketi S8'in başında soluk (bilinçli giriş animasyonu, ilk kareler).
