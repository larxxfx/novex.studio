# kure_v1 — mevcut davranış (rota modu eklenmeden önce belgelendi, 3 Kasım 2026)

## render.py (değiştirilmedi)
- **İçe aktarıldığında** `build/geo.json`, dünya/kutup/gökyüzü dokularını (mip piramidiyle) yükler; `build/` yoksa çöker.
- **Genel çekirdek** (her video kullanabilir): `Cam(target, up, D, P, head, fov)` küre kamerası; `render_globe(cam, sun, …)` ışın izlemeli küre
  (atmosfer, gece, sis, aurora); `polyline_layers` + `glow_lines` parlayan çizgi; `dot`, `ring`, `fill_poly`; `Text` (Pillow katmanı, gölge, yuvarlak kutu);
  `post` (hareket bulanıklığı, gren, vinyet); `slerp`, `great_circle`, `local_north`, `ease*`, `seg`.
- **Antarktika'ya özel** (modül düzeyinde): `CITIES`, `TM_OUTER` (taşınmış Türkiye), `CRACKS`, `CONVOY`, Türkçe `CAPS`, `frame(t)` içindeki 6 sahne, `SCENES`.
- CLI: `render.py frame <t> out.png`, `render.py scene sN out.mp4` (ffmpeg rawvideo → libx264, bt709).

## Koruma testi
Depodaki kopya ile özgün çalışma kopyası `/home/claude/novex-antarktika` aynı kareyi üretir: t = 1.5, 10.0, 22.0 sn'de **en büyük piksel farkı 0**.

## Rota modu (yeni dosyalar; render.py'ye dokunmaz)
| Dosya | Görev |
|---|---|
| `src/rota_geo.py` | Sonmiani → Karaginsky uzun büyük daire yayı; NE 10 m kara maskesiyle kara testi → `build/rota_okyanus.json` |
| `src/rota.py` | 11 sahne; sahneler anlatıcının cümle zamanlarına (`zaman.json`) kilitli; İngilizce ekran metni + yakılmış altyazı |
| `src/rota_ses.py` | Kodla sentezlenen lisanssız müzik + efekt (dış örnek yok) |

Ölçüm (`rota_geo.py`): yay 32.090 km (kaynak 32.089,7 km), karaya değen nokta 0 (uçlarda 15 km tampon), en yakın kıyı 2,3 km (Kamçatka ucunda, çözünürlük sınırında).
Bilinen görsel kusur: S6'da Antarktika kutup dokusu eğik açıda benekli görünüyor (motorun kutup dokusu; render.py değiştirilmedi).
