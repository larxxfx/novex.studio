/** Karakter örneğinin etkin kimliği: sahnede `ad` varsa o, yoksa karakter `id`'si.
 * Motor (SpriteCharacter.ad), render kaydı (olaylar.json → kareler[].ad, olaylar[].karakter) ve testler aynı kuralı kullanır;
 * Python karşılığı: araclar/karakter_render.py → etkin_kimlik(). */
export const etkinKimlik = (k) => (k.ad ? String(k.ad) : String(k.id));

/** Sahnedeki karakterlerin etkin kimlikleri (sırayla); aynı kimlik iki kez geçerse hata. */
export function kimlikleriDogrula(karakterler) {
  const gorulen = new Set();
  for (const k of karakterler) {
    const ad = etkinKimlik(k);
    if (gorulen.has(ad)) throw new Error(`aynı etkin kimlik iki kez: "${ad}" (karakterlere farklı "ad" verin)`);
    gorulen.add(ad);
  }
  return [...gorulen];
}
