/**
 * Kamera: anahtar karelerle kaydırma (x, y = bakılan nokta) ve yakınlaştırma (zoom). Deterministik.
 * keys: [{t, x, y, zoom, ease?}] — x/y sahne koordinatı (1080×1920 tuvalde merkez 540, 960).
 */
import { anahtarDeger } from "../animation/AnimationTimeline.js";

export class CameraController {
  constructor(keys = [], { genislik = 1080, yukseklik = 1920 } = {}) {
    this.keys = keys; this.w = genislik; this.h = yukseklik;
  }

  durum(tMs) {
    return {
      x: anahtarDeger(this.keys, tMs, "x", this.w / 2),
      y: anahtarDeger(this.keys, tMs, "y", this.h / 2),
      zoom: anahtarDeger(this.keys, tMs, "zoom", 1),
    };
  }

  /** Dünya katmanları çizilmeden önce çağrılır; parallax: 0 = sabit (gökyüzü), 1 = tam kamera hareketi. */
  uygula(ctx, tMs, parallax = 1) {
    const c = this.durum(tMs);
    const zoom = 1 + (c.zoom - 1) * parallax;
    ctx.translate(this.w / 2, this.h / 2);
    ctx.scale(zoom, zoom);
    ctx.translate(-(this.w / 2 + (c.x - this.w / 2) * parallax), -(this.h / 2 + (c.y - this.h / 2) * parallax));
  }
}
