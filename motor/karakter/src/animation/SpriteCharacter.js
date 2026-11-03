/**
 * Sahnedeki bir karakter örneği. Durumsuz çizim: draw(ctx, tMs) yalnızca t'ye bağlıdır.
 *
 * ayarlar:
 *   klipler:  [{anim, start, speed?}]              animasyon zaman çizelgesi (ms)
 *   hareket:  [{t, x, y, olcek?, ease?}]           sahne koordinatında konum (çapa noktası) + ölçek anahtar kareleri
 *   yon:      [{t, yon: 1|-1}]                      1 = sağa bakar (kaynak çizim), -1 = aynalı
 *   giris/cikis: ms                                  sahnede görünür olduğu aralık
 *   z:        katman sırası (büyük = önde)
 */
import { zamandakiKare, anahtarDeger } from "./AnimationTimeline.js";

export class SpriteCharacter {
  constructor({ tanim, klipler = [{ anim: "idle", start: 0 }], hareket = [{ t: 0, x: 540, y: 1500, olcek: 3 }],
                yon = [{ t: 0, yon: 1 }], giris = 0, cikis = Infinity, z = 0, ad = "" }) {
    this.tanim = tanim; this.klipler = klipler; this.hareket = hareket; this.yon = yon;
    this.giris = giris; this.cikis = cikis; this.z = z; this.ad = ad || tanim.manifest.characterId;
  }

  gorunur(tMs) { return tMs >= this.giris && tMs < this.cikis; }

  durum(tMs) {
    const m = this.tanim.manifest;
    const k = zamandakiKare(m, this.klipler, tMs);
    let olcek = anahtarDeger(this.hareket, tMs, "olcek", 1);
    if (m.render.pixelArt) olcek = Math.max(1, Math.round(olcek)); // piksel sanatı: tam sayı ölçek
    const yonListesi = this.yon.filter((y) => y.t <= tMs).sort((a, b) => a.t - b.t);
    return { ...k, x: anahtarDeger(this.hareket, tMs, "x"), y: anahtarDeger(this.hareket, tMs, "y"), olcek,
             yon: yonListesi.length ? yonListesi[yonListesi.length - 1].yon : 1 };
  }

  draw(ctx, tMs) {
    if (!this.gorunur(tMs)) return null;
    const d = this.durum(tMs);
    const img = this.tanim.kareler.get(d.yol);
    if (!img) throw new Error(`${this.ad}: kare önbellekte yok: ${d.yol}`);
    const m = this.tanim.manifest;
    const ax = m.canvas ? m.canvas.anchor.x : img.width / 2;
    const ay = m.canvas ? m.canvas.anchor.y : img.height;
    ctx.save();
    ctx.imageSmoothingEnabled = !m.render.pixelArt;
    ctx.translate(Math.round(d.x), Math.round(d.y));
    ctx.scale(d.olcek * d.yon, d.olcek);
    ctx.drawImage(img, -ax, -ay);
    ctx.restore();
    return d;
  }
}
