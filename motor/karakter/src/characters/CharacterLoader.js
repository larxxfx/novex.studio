/**
 * Karakter yükleyici: manifest + tüm kareleri önceden yükler, URL bazında önbellekler.
 * Görsel yükleme fonksiyonu enjekte edilebilir (tarayıcıda Image, testte sahte yükleyici).
 */
import { manifestiDogrula } from "./CharacterManifest.js";

export class EksikVarlikHatasi extends Error {}

export function tarayiciGorselYukle(url) {
  return new Promise((ok, hata) => {
    const img = new Image();
    img.decoding = "async";
    img.onload = () => ok(img);
    img.onerror = () => hata(new EksikVarlikHatasi(`görsel yüklenemedi: ${url}`));
    img.src = url;
  });
}

export class CharacterLoader {
  constructor({ gorselYukle = tarayiciGorselYukle, jsonYukle = (u) => fetch(u).then((r) => {
    if (!r.ok) throw new EksikVarlikHatasi(`manifest yok: ${u} (${r.status})`);
    return r.json();
  }) } = {}) {
    this.gorselYukle = gorselYukle;
    this.jsonYukle = jsonYukle;
    this.onbellek = new Map(); // url → Promise<görsel>
  }

  gorsel(url) {
    if (!this.onbellek.has(url)) {
      const p = this.gorselYukle(url).catch((e) => { this.onbellek.delete(url); throw e; });
      this.onbellek.set(url, p);
    }
    return this.onbellek.get(url);
  }

  /** kokUrl: karakter klasörü (sonu / ile). Dönüş: { manifest, kareler: Map<yol, görsel> } */
  async yukle(kokUrl) {
    const manifest = manifestiDogrula(await this.jsonYukle(new URL("manifest.json", kokUrl).href));
    const yollar = Object.values(manifest.animations).flatMap((a) => a.frames);
    const kareler = new Map();
    const sonuc = await Promise.allSettled(yollar.map(async (y) => kareler.set(y, await this.gorsel(new URL(y, kokUrl).href))));
    const eksik = sonuc.filter((s) => s.status === "rejected");
    if (eksik.length) throw new EksikVarlikHatasi(`${manifest.characterId}: ${eksik.length} kare yüklenemedi — ${eksik[0].reason.message}`);
    return { manifest, kareler, kokUrl };
  }
}
