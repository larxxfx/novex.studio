/**
 * Karakter kayıt defteri: tanımlar (yüklenmiş manifest + kareler) ve sahnedeki örnekler.
 * Motor belirli bir karaktere bağlı değildir; yeni karakter = yeni klasör + manifest.
 */
import { etkinKimlik } from "./kimlik.js";
import { SpriteCharacter } from "../animation/SpriteCharacter.js";

export class CharacterManager {
  constructor(loader) {
    this.loader = loader;
    this.tanimlar = new Map(); // id → { manifest, kareler }
  }

  async kaydet(id, kokUrl) {
    const t = await this.loader.yukle(kokUrl);
    this.tanimlar.set(id, t);
    return t;
  }

  tanim(id) {
    const t = this.tanimlar.get(id);
    if (!t) throw new Error(`karakter kayıtlı değil: ${id}`);
    return t;
  }

  sil(id) { return this.tanimlar.delete(id); }
  liste() { return [...this.tanimlar.keys()]; }

  /** Sahne için yeni örnek (aynı karakterden birden fazla örnek olabilir). */
  ornek(id, ayarlar = {}) {
    return new SpriteCharacter({ tanim: this.tanim(id), ...ayarlar, ad: etkinKimlik({ id, ad: ayarlar.ad }) });
  }
}
