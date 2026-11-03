/**
 * Karakter manifesti (şema v2) doğrulama ve normalleştirme. Saf modül: DOM'a bağımlı değil (Node testleri çalışır).
 *
 * Şema v2:
 * {
 *   schema: 2, characterId, displayName,
 *   canvas: { width, height, anchor: { x, y } },   // tüm karelerin ortak tuvali; çapa = ayakların zemine bastığı nokta
 *   render: { pixelArt: bool },                      // true: tam sayı ölçek + yumuşatmasız çizim
 *   animations: { <ad>: { frames: [yol], fps, loop, next? } },
 *   planned: [ad]                                    // henüz karesi olmayan hareketler (motor bunları "yok" sayar)
 * }
 * Şema v1 (kit prototipi: anchor/canvas yok) otomatik v2'ye çevrilir; çapa olarak kare tabanının ortası kullanılır.
 */
export const BILINEN_HAREKETLER = [
  "idle", "walk", "run", "jump", "talk", "point", "lookLeft", "lookRight", "wave",
  "sit", "stand", "crouch", "interact", "surprise", "think", "explain",
];

export class ManifestHatasi extends Error {}

export function manifestiDogrula(ham) {
  if (!ham || typeof ham !== "object") throw new ManifestHatasi("manifest nesne değil");
  const m = structuredClone(ham);
  if (!m.characterId) throw new ManifestHatasi("characterId eksik");
  if (!m.animations || !Object.keys(m.animations).length) throw new ManifestHatasi(`${m.characterId}: animasyon yok`);
  m.schema = m.schema || 1;
  m.render = { pixelArt: false, ...(m.render || {}) };
  for (const [ad, a] of Object.entries(m.animations)) {
    if (!Array.isArray(a.frames) || !a.frames.length) throw new ManifestHatasi(`${m.characterId}.${ad}: kare listesi boş`);
    if (!(a.fps > 0 && a.fps <= 60)) throw new ManifestHatasi(`${m.characterId}.${ad}: fps 0–60 aralığında olmalı`);
    a.loop = a.loop !== false;
    if (a.next && !m.animations[a.next]) throw new ManifestHatasi(`${m.characterId}.${ad}: next="${a.next}" tanımlı değil`);
  }
  if (m.schema >= 2) {
    const c = m.canvas;
    if (!c || !(c.width > 0) || !(c.height > 0) || !c.anchor) throw new ManifestHatasi(`${m.characterId}: canvas/anchor eksik`);
  }
  m.planned = (m.planned || []).filter((p) => !m.animations[p]);
  return m;
}

/** Bir animasyonun bu karakterde gerçekten karesi var mı? (planned olanlar yok sayılır) */
export function animasyonVarMi(m, ad) {
  return Boolean(m.animations[ad]);
}
