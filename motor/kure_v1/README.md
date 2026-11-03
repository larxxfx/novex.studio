# kure_v1 — ilk NØVEX videolarının küre/harita render motoru (arşiv + yeniden kullanım)

"Türkiye Antarktika'da Olsaydı?" (3 Kasım 2026) bu kodla üretildi. Kod daha önce yalnızca Claude'un geçici çalışma ortamında
duruyordu; kaybolmaması için 3 Kasım 2026'da depoya alındı. **Davranışı değiştirilmedi.**

| Dosya | Görev |
|---|---|
| `src/geo.py` | Natural Earth sınırları → küre üzerinde ülke taşıma, mesafe/alan hesapları (`build/geo.json`) |
| `src/tex.py` | Prosedürel dünya, kutup buzu ve gökyüzü dokuları (`build/*.png|jpg`) |
| `src/render.py`, `render_v3.py` | Sahne render'ı (numpy + OpenCV + Pillow), kelime düzeyinde altyazı |
| `src/audio*.py`, `narration.py` | Sentez müzik/efekt, anlatım yerleşimi |
| `src/extras.py` | SRT + kapak |
| `*.sh`, `qc.py` | Birleştirme, miks, QC |
| `senaryo.md`, `OKUBENI.md` | Antarktika videosunun senaryosu, kaynakları ve çalışma notları |

## Yeniden kurulum
Depoya alınmayanlar (büyük/yeniden üretilebilir): `data/ne/geojson/` ve `build/`.
1. Natural Earth (kamu malı) GeoJSON'ları `data/ne/geojson/` altına:
   `ne_10m_admin_0_countries`, `ne_10m_antarctic_ice_shelves_polys`, `ne_50m_admin_0_countries`,
   `ne_50m_antarctic_ice_shelves_polys`, `ne_50m_populated_places_simple` (kaynak: github.com/nvkelso/natural-earth-vector).
2. `python3 src/geo.py && python3 src/tex.py all` → `build/`
3. `OKUBENI.md`'deki render komutları.

Not: Kod Antarktika videosuna özel sahne zamanlamaları içerir; yeni videolar için genelleştirme sonraki iştir.
