/**
 * Sahne JSON'u → SceneRenderer. Hem canlı önizleme (onizleme.html) hem MP4 render'ı (render/sahne.html) bunu kullanır.
 *
 * Sahne JSON (örnek: sahneler/ornek_kasif.json):
 * { sure_ms, fps, genislik, yukseklik,
 *   arkaplan: { tur: "novex_gece", zemin_y },
 *   karakterler: [{ id, kok, ad?, klipler, hareket, yon?, z?, giris?, cikis? }],
 *   kamera: [{t, x, y, zoom}],
 *   yazilar: [{ t0, t1, metin, y? }]   // ekran yazısı (güvenli alan: x 140–940, y < 1520)
 * }
 */
import { CharacterLoader } from "../characters/CharacterLoader.js";
import { CharacterManager } from "../characters/CharacterManager.js";
import { SceneRenderer } from "./SceneRenderer.js";

const RENK = { gece0: "#08122B", gece1: "#0B2A4A", turkuaz: "#3FD0C9", elektrik: "#2E8BFF", krem: "#F2EAD8" };

function rastgele(tohum) { // deterministik (mulberry32)
  return () => { tohum |= 0; tohum = (tohum + 0x6d2b79f5) | 0; let t = Math.imul(tohum ^ (tohum >>> 15), 1 | tohum);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

export function novexGeceKatmanlari({ genislik: W = 1080, yukseklik: H = 1920, zemin_y: Z = 1500 } = {}) {
  const r = rastgele(317); const yildiz = Array.from({ length: 140 }, () => [r() * W * 1.4 - W * 0.2, r() * Z * 0.75, r() * 1.6 + 0.4, r()]);
  const tepe = (tohum, taban, genlik) => { const q = rastgele(tohum); return Array.from({ length: 13 }, (_, i) => [i * W * 0.15 - W * 0.4, taban - q() * genlik]); };
  const daglar = [tepe(11, Z - 120, 260), tepe(23, Z - 40, 160)];
  return [
    { tur: "arkaplan", parallax: 0, ciz(ctx) {
      const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, RENK.gece0); g.addColorStop(0.75, RENK.gece1); g.addColorStop(1, "#123A57");
      ctx.fillStyle = g; ctx.fillRect(-W, -H, W * 3, H * 3); } },
    { tur: "arkaplan", parallax: 0.15, ciz(ctx, t) {
      for (const [x, y, s, f] of yildiz) { ctx.globalAlpha = 0.45 + 0.4 * Math.sin(t / 900 + f * 6.28); ctx.fillStyle = RENK.krem; ctx.fillRect(x, y, s, s); }
      ctx.globalAlpha = 1; } },
    ...daglar.map((pts, i) => ({ tur: "arkaplan", parallax: 0.35 + i * 0.3, ciz(ctx) {
      ctx.fillStyle = i ? "#0E3350" : "#0C2742"; ctx.beginPath(); ctx.moveTo(-W, H);
      for (const [x, y] of pts) ctx.lineTo(x, y); ctx.lineTo(W * 2, H); ctx.closePath(); ctx.fill(); } })),
    { tur: "arkaplan", parallax: 1, ciz(ctx) {
      const g = ctx.createLinearGradient(0, Z, 0, H); g.addColorStop(0, "#1B4A4A"); g.addColorStop(1, "#0A1E2C");
      ctx.fillStyle = g; ctx.fillRect(-W, Z, W * 3, H);
      ctx.fillStyle = RENK.turkuaz; ctx.globalAlpha = 0.55; ctx.fillRect(-W, Z - 2, W * 3, 3); ctx.globalAlpha = 1; } },
  ];
}

export function yaziKatmani(yazilar = []) {
  return { tur: "onplan", ciz(ctx, t, sahne) {
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.font = "700 46px Inter, 'Helvetica Neue', Arial, sans-serif"; ctx.fillStyle = RENK.krem;
    ctx.fillText("N Ø V E X", sahne.w / 2, 170);
    for (const y of yazilar) {
      if (t < y.t0 || t >= y.t1) continue;
      const a = Math.min(1, (t - y.t0) / 200, (y.t1 - t) / 200);
      ctx.globalAlpha = a; ctx.font = `700 ${y.boyut || 56}px Inter, 'Helvetica Neue', Arial, sans-serif`;
      ctx.lineWidth = 10; ctx.strokeStyle = "rgba(8,18,43,0.85)"; ctx.strokeText(y.metin, sahne.w / 2, y.y || 380);
      ctx.fillStyle = y.renk || RENK.krem; ctx.fillText(y.metin, sahne.w / 2, y.y || 380); ctx.globalAlpha = 1;
    }
  } };
}

/** sahneJson + temel URL → { sahne: SceneRenderer, sure_ms, fps } (tüm kareler önceden yüklenmiş) */
export async function sahneKur(sahneJson, temelUrl, { loader = new CharacterLoader() } = {}) {
  const W = sahneJson.genislik || 1080, H = sahneJson.yukseklik || 1920;
  const yonetici = new CharacterManager(loader);
  for (const id of new Set(sahneJson.karakterler.map((k) => k.id))) {
    const kok = sahneJson.karakterler.find((k) => k.id === id).kok;
    await yonetici.kaydet(id, new URL(kok, temelUrl).href);
  }
  const arka = sahneJson.arkaplan?.tur === "novex_gece" ? novexGeceKatmanlari({ genislik: W, yukseklik: H, zemin_y: sahneJson.arkaplan.zemin_y }) : [];
  const sahne = new SceneRenderer({ genislik: W, yukseklik: H, kamera: sahneJson.kamera || [],
    katmanlar: [...arka, { tur: "karakterler", parallax: 1 }, yaziKatmani(sahneJson.yazilar)] });
  for (const k of sahneJson.karakterler) sahne.ekle(yonetici.ornek(k.id, k));
  return { sahne, yonetici, sure_ms: sahneJson.sure_ms, fps: sahneJson.fps || 30 };
}
