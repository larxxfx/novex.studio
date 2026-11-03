/**
 * Deterministik, zaman kodlu animasyon seçimi. requestAnimationFrame'e bağlı değildir:
 * aynı t (ms) her zaman aynı kareyi verir → MP4 render'ı kare kare tekrarlanabilir.
 *
 * Klip listesi (bir karakter örneği için):
 *   [{ anim: "idle", start: 0 }, { anim: "run", start: 2000, speed: 1 }, { anim: "jump", start: 5500 }]
 * Bir klip bir sonraki klibin start'ına kadar sürer. Döngüsüz animasyon bitince son karede kalır
 * ya da manifestteki `next` animasyonuna geçer (ör. jump → idle).
 */

export function kareSuresiMs(anim, speed = 1) {
  return 1000 / (anim.fps * speed);
}

/** Tek bir animasyonda, animasyonun başlangıcından itibaren geçen süre için kare indeksi ve bitti bilgisi. */
export function animasyonKaresi(anim, gecenMs, speed = 1) {
  const n = anim.frames.length;
  if (gecenMs < 0) return { index: 0, bitti: false };
  const k = Math.floor(gecenMs / kareSuresiMs(anim, speed) + 1e-9);
  if (anim.loop) return { index: k % n, bitti: false };
  return k >= n ? { index: n - 1, bitti: true, bitisMs: n * kareSuresiMs(anim, speed) } : { index: k, bitti: false };
}

/** Klip listesi + manifest → t anında {anim, index}. */
export function zamandakiKare(manifest, klipler, tMs) {
  if (!klipler.length) throw new Error("klip listesi boş");
  const sirali = [...klipler].sort((a, b) => a.start - b.start);
  let aktif = sirali[0];
  for (const k of sirali) if (k.start <= tMs) aktif = k;
  let animAd = aktif.anim;
  let anim = manifest.animations[animAd];
  if (!anim) throw new Error(`${manifest.characterId}: "${animAd}" animasyonu yok (planlanan hareketler henüz çizilmedi)`);
  let gecen = tMs - aktif.start;
  const speed = aktif.speed || 1;
  let r = animasyonKaresi(anim, gecen, speed);
  // döngüsüz animasyon bitti ve next tanımlıysa ona geç (zincir derinliği sınırlı)
  for (let derinlik = 0; r.bitti && anim.next && derinlik < 4; derinlik++) {
    gecen -= r.bitisMs;
    animAd = anim.next; anim = manifest.animations[animAd];
    r = animasyonKaresi(anim, gecen, speed);
  }
  return { anim: animAd, index: r.index, yol: anim.frames[r.index] };
}

/** Anahtar kare enterpolasyonu (konum, ölçek, kamera için). keys: [{t, ...sayılar}], kolaylaştırma: "linear"|"inOut" */
export function anahtarDeger(keys, tMs, alan, varsayilan = 0) {
  const k = keys.filter((x) => alan in x).sort((a, b) => a.t - b.t);
  if (!k.length) return varsayilan;
  if (tMs <= k[0].t) return k[0][alan];
  if (tMs >= k[k.length - 1].t) return k[k.length - 1][alan];
  for (let i = 0; i < k.length - 1; i++) {
    const a = k[i], b = k[i + 1];
    if (tMs >= a.t && tMs <= b.t) {
      let u = (tMs - a.t) / (b.t - a.t || 1);
      if ((b.ease || "inOut") === "inOut") u = u * u * (3 - 2 * u);
      return a[alan] + (b[alan] - a[alan]) * u;
    }
  }
  return varsayilan;
}
