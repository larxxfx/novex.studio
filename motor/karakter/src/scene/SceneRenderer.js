/**
 * Sahne çizici: katmanlar (arka plan → karakterler z sırasıyla → ön plan/arayüz) + kamera.
 * renderFrame(ctx, tMs) tamamen deterministiktir; canlı önizleme ve MP4 render'ı aynı fonksiyonu kullanır.
 *
 * katman: { tur: "arkaplan"|"karakterler"|"onplan", parallax?: 0..1, ciz?: (ctx, tMs, sahne) => void }
 */
import { CameraController } from "./CameraController.js";

export class SceneRenderer {
  constructor({ genislik = 1080, yukseklik = 1920, kamera = [], katmanlar = [], karakterler = [] } = {}) {
    this.w = genislik; this.h = yukseklik;
    this.kamera = new CameraController(kamera, { genislik, yukseklik });
    this.katmanlar = katmanlar;
    this.karakterler = karakterler;
  }

  ekle(karakter) { this.karakterler.push(karakter); return karakter; }
  cikar(karakter) { this.karakterler = this.karakterler.filter((k) => k !== karakter); }

  renderFrame(ctx, tMs) {
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, this.w, this.h);
    const cizilen = [];
    for (const katman of this.katmanlar) {
      ctx.save();
      if (katman.tur !== "onplan") this.kamera.uygula(ctx, tMs, katman.parallax ?? 1);
      if (katman.tur === "karakterler") {
        for (const k of [...this.karakterler].sort((a, b) => a.z - b.z)) {
          const d = k.draw(ctx, tMs);
          if (d) cizilen.push({ ad: k.ad, ...d });
        }
      } else if (katman.ciz) {
        katman.ciz(ctx, tMs, this);
      }
      ctx.restore();
    }
    ctx.restore();
    return cizilen; // test ve ses senkronu için: bu karede hangi karakter hangi karede
  }
}
