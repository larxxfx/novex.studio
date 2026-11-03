// Karakter motoru birim testleri. Çalıştırma: node motor/karakter/testler/motor.test.mjs (Node 22, bağımlılık yok)
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { manifestiDogrula, ManifestHatasi } from "../src/characters/CharacterManifest.js";
import { animasyonKaresi, zamandakiKare, anahtarDeger } from "../src/animation/AnimationTimeline.js";
import { CharacterLoader, EksikVarlikHatasi } from "../src/characters/CharacterLoader.js";
import { CharacterManager } from "../src/characters/CharacterManager.js";
import { SceneRenderer } from "../src/scene/SceneRenderer.js";
import { CameraController } from "../src/scene/CameraController.js";
import { etkinKimlik, kimlikleriDogrula } from "../src/characters/kimlik.js";

const KOK = new URL("../karakterler/explorer/", import.meta.url);
const gercek = JSON.parse(readFileSync(new URL("manifest.json", KOK), "utf8"));
let gecti = 0;
const test = async (ad, f) => { await f(); gecti++; console.log("✓", ad); };

// sahte tuval bağlamı: çizim çağrılarını kaydeder
function sahteCtx() {
  const kayit = [];
  const ctx = new Proxy({}, { get: (_, k) => (k === "kayit" ? kayit : (...a) => kayit.push([k, ...a])), set: () => true });
  return ctx;
}
const sahteYukleyici = (eksik = new Set()) => new CharacterLoader({
  jsonYukle: async () => structuredClone(gercek),
  gorselYukle: async (u) => { if ([...eksik].some((e) => u.endsWith(e))) throw new EksikVarlikHatasi(`yok: ${u}`); return { width: 182, height: 275, url: u }; },
});

await test("gerçek manifest geçerli (şema 2, 3 animasyon, ortak tuval)", () => {
  const m = manifestiDogrula(gercek);
  assert.equal(m.schema, 2); assert.deepEqual(Object.keys(m.animations), ["idle", "run", "jump"]);
  assert.ok(m.canvas.width > 0 && m.canvas.anchor.y > 0); assert.equal(m.render.pixelArt, true);
  assert.ok(m.planned.includes("walk") && !m.planned.includes("run"));
});
await test("bozuk manifest reddedilir", () => {
  assert.throws(() => manifestiDogrula({}), ManifestHatasi);
  assert.throws(() => manifestiDogrula({ characterId: "x", animations: { a: { frames: [], fps: 5 } } }), ManifestHatasi);
  assert.throws(() => manifestiDogrula({ characterId: "x", animations: { a: { frames: ["1"], fps: 0 } } }), ManifestHatasi);
  assert.throws(() => manifestiDogrula({ characterId: "x", animations: { a: { frames: ["1"], fps: 5, next: "yok" } } }), ManifestHatasi);
});
await test("idle döngüsü: 5 fps, 6 kare → 1,2 sn'de başa döner", () => {
  const a = gercek.animations.idle;
  assert.equal(animasyonKaresi(a, 0).index, 0); assert.equal(animasyonKaresi(a, 199).index, 0);
  assert.equal(animasyonKaresi(a, 200).index, 1); assert.equal(animasyonKaresi(a, 1199).index, 5);
  assert.equal(animasyonKaresi(a, 1200).index, 0);
});
await test("run döngüsü: 10 fps sırayla oynar, speed çarpanı çalışır", () => {
  const a = gercek.animations.run;
  assert.deepEqual([0, 100, 200, 300, 400, 500, 600].map((t) => animasyonKaresi(a, t).index), [0, 1, 2, 3, 4, 5, 0]);
  assert.equal(animasyonKaresi(a, 100, 2).index, 2);
});
await test("jump döngüsüz: son karede biter, next=idle'a geçer", () => {
  const m = manifestiDogrula(gercek); const kl = [{ anim: "jump", start: 1000 }];
  assert.equal(zamandakiKare(m, kl, 1000).index, 0);
  assert.equal(zamandakiKare(m, kl, 1749).anim, "jump"); assert.equal(zamandakiKare(m, kl, 1749).index, 5);
  const sonra = zamandakiKare(m, kl, 1750); assert.equal(sonra.anim, "idle"); assert.equal(sonra.index, 0);
  const m2 = structuredClone(m); delete m2.animations.jump.next;
  assert.equal(zamandakiKare(m2, kl, 5000).index, 5); // next yoksa son karede kalır
});
await test("geçişler: klip sınırında animasyon değişir, ilk kareden başlar", () => {
  const m = manifestiDogrula(gercek); const kl = [{ anim: "idle", start: 0 }, { anim: "run", start: 2000 }];
  assert.equal(zamandakiKare(m, kl, 1999).anim, "idle");
  const r = zamandakiKare(m, kl, 2000); assert.equal(r.anim, "run"); assert.equal(r.index, 0);
});
await test("planlanan ama çizilmemiş hareket açık hata verir", () => {
  const m = manifestiDogrula(gercek);
  assert.throws(() => zamandakiKare(m, [{ anim: "walk", start: 0 }], 10), /walk.*yok/);
});
await test("deterministik: aynı t → aynı sonuç (1000 rastgele t)", () => {
  const m = manifestiDogrula(gercek); const kl = [{ anim: "idle", start: 0 }, { anim: "run", start: 2000 }, { anim: "jump", start: 5600 }];
  for (let i = 0; i < 1000; i++) { const t = Math.random() * 9000; assert.deepEqual(zamandakiKare(m, kl, t), zamandakiKare(m, kl, t)); }
});
await test("anahtar kare enterpolasyonu (linear / inOut / sınırlar)", () => {
  const k = [{ t: 0, x: 0 }, { t: 100, x: 100, ease: "linear" }];
  assert.equal(anahtarDeger(k, -5, "x"), 0); assert.equal(anahtarDeger(k, 50, "x"), 50); assert.equal(anahtarDeger(k, 500, "x"), 100);
  assert.equal(anahtarDeger([{ t: 0, x: 0 }, { t: 100, x: 100 }], 25, "x"), 15.625);
  assert.equal(anahtarDeger([], 5, "x", 7), 7);
});
await test("yükleyici: tüm kareleri önceden yükler ve önbellekler", async () => {
  const L = sahteYukleyici(); const t = await L.yukle(KOK.href);
  assert.equal(t.kareler.size, 18); assert.equal(L.onbellek.size, 18);
  await L.yukle(KOK.href); assert.equal(L.onbellek.size, 18);
});
await test("eksik kare açık hatayla durur", async () => {
  await assert.rejects(sahteYukleyici(new Set(["run/frame_03.png"])).yukle(KOK.href), (e) => e instanceof EksikVarlikHatasi && /1 kare/.test(e.message));
});
await test("çoklu karakter: z sırasıyla çizilir, giriş/çıkış ve aynalama uygulanır", async () => {
  const y = new CharacterManager(sahteYukleyici()); await y.kaydet("explorer", KOK.href);
  const s = new SceneRenderer({ katmanlar: [{ tur: "karakterler" }] });
  s.ekle(y.ornek("explorer", { ad: "on", z: 2, hareket: [{ t: 0, x: 300, y: 1500, olcek: 3.4 }] }));
  s.ekle(y.ornek("explorer", { ad: "arka", z: 1, giris: 500, yon: [{ t: 0, yon: -1 }], hareket: [{ t: 0, x: 800, y: 1400, olcek: 2 }] }));
  assert.deepEqual(s.renderFrame(sahteCtx(), 0).map((d) => d.ad), ["on"]);
  const c = sahteCtx(); const d = s.renderFrame(c, 600);
  assert.deepEqual(d.map((x) => x.ad), ["arka", "on"]);
  assert.equal(d[1].olcek, 3); // piksel sanatı → tam sayı ölçek
  assert.ok(c.kayit.some(([k, sx]) => k === "scale" && sx === -2)); // arka plandaki aynalı
  s.cikar(s.karakterler[0]); assert.equal(s.karakterler.length, 1);
});
await test("etkin kimlik: ad varsa ad, yoksa id; karışık sahnede hepsi ayrı; tekrar hata", async () => {
  assert.equal(etkinKimlik({ id: "explorer", ad: "kasif_on" }), "kasif_on");
  assert.equal(etkinKimlik({ id: "explorer" }), "explorer");
  assert.deepEqual(kimlikleriDogrula([{ id: "explorer", ad: "kasif_on" }, { id: "robot" }, { id: "explorer", ad: "kasif_arka" }]),
    ["kasif_on", "robot", "kasif_arka"]);
  assert.throws(() => kimlikleriDogrula([{ id: "explorer" }, { id: "explorer" }]), /aynı etkin kimlik/);
  const y = new CharacterManager(sahteYukleyici()); await y.kaydet("explorer", KOK.href);
  assert.equal(y.ornek("explorer", {}).ad, "explorer"); // motor da id'ye düşer (manifest characterId'ye değil)
  assert.equal(y.ornek("explorer", { ad: "kasif_on" }).ad, "kasif_on");
  const sahne = JSON.parse(readFileSync(new URL("../sahneler/ornek_kasif.json", import.meta.url)));
  assert.equal(etkinKimlik(sahne.karakterler[0]), "kasif_on"); // örnek sahnenin ana karakteri
});
await test("karakter farklı sahnelere eklenebilir (aynı tanım, bağımsız örnekler)", async () => {
  const y = new CharacterManager(sahteYukleyici()); await y.kaydet("explorer", KOK.href);
  const a = new SceneRenderer({ katmanlar: [{ tur: "karakterler" }] }), b = new SceneRenderer({ katmanlar: [{ tur: "karakterler" }] });
  a.ekle(y.ornek("explorer", { klipler: [{ anim: "run", start: 0 }] })); b.ekle(y.ornek("explorer", { klipler: [{ anim: "jump", start: 0 }] }));
  assert.equal(a.renderFrame(sahteCtx(), 250)[0].anim, "run"); assert.equal(b.renderFrame(sahteCtx(), 250)[0].anim, "jump");
  assert.throws(() => y.tanim("yok"), /kayıtlı değil/);
});
await test("kamera: kaydırma ve yakınlaştırma enterpolasyonu", () => {
  const k = new CameraController([{ t: 0, x: 540, y: 960, zoom: 1 }, { t: 1000, x: 640, y: 960, zoom: 1.2, ease: "linear" }]);
  assert.deepEqual(k.durum(500), { x: 590, y: 960, zoom: 1.1 });
});

console.log(`\n${gecti} test geçti`);
