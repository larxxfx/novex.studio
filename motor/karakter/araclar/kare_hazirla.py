"""Karakter kitindeki PNG karelerini üretime hazırlar (kaynak kite dokunmaz; yeni klasöre yazar).

Kullanım:
  python3 motor/karakter/araclar/kare_hazirla.py <kit_klasoru> <karakter_id> <cikti_klasoru>
  ör.: ... motor/karakter/kaynak/explorer_kit_v1 explorer motor/karakter/karakterler/explorer

Adımlar (her kare için):
 1. Kare, kitin referans sayfasında (source_reference.*) şablon eşleştirme ile bulunur → sayfadaki gerçek konumu.
 2. Parşömen kalıntıları silinir: otomatik kural (kalinti.py) + kit için elle işaretlenmiş bölgeler (EL_ILE).
 3. Hizalama: her animasyon satırının zemin çizgisi = o satırdaki karelerin en alt noktası (en büyük y).
    Kareler zemine göre dikey ofsetini korur (zıplama yüksekliği geri gelir); yatay çapa = gövde (üst %40) ağırlık merkezi.
 4. Tüm kareler aynı boyutlu tuvale yerleştirilir; çapa noktası tuvalde sabittir (alt-orta) → titreme olmaz.
 5. manifest.json (şema v2) + qc/kalite_raporu.json + qc/kontrol_sayfasi.png yazılır.
"""
import glob, json, os, sys
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from kalinti import kalinti_maskesi  # noqa: E402

ANIMASYONLAR = ["idle", "run", "jump"]
# Görsel incelemeyle işaretlenen kalıntı bölgeleri (kare koordinatı x0,y0,x1,y1; yalnızca açık renkli pikseller silinir).
# explorer_kit_v1: bekleme karelerinde ip halkası ile bacak arasındaki parşömen dilimi.
EL_ILE = {f"idle/frame_0{i}.png": [(24, 130, 40, 185)] for i in range(1, 7)}
# Otomatik kuralın yanlış seçtiği yerler (korunur): idle 4'te elde tutulan haritanın köşesi.
KORU = {"idle/frame_04.png": [(70, 120, 110, 200)]}


def acik_piksel(im):
    L = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2LAB).astype(int)
    return (L[..., 0] > 178) & (L[..., 1] <= 136)


def main(kit, kid, out):
    kaynak = os.path.join(kit, "assets", kid if os.path.isdir(os.path.join(kit, "assets", kid)) else "explorer")
    ref_yol = next(iter(glob.glob(os.path.join(kaynak, "source_reference.*"))), None)
    ref = cv2.imread(ref_yol) if ref_yol else None
    kareler, rapor = {}, {"kit": os.path.basename(os.path.normpath(kit)), "kareler": {}, "uyarilar": []}
    for a in ANIMASYONLAR:
        for f in sorted(glob.glob(os.path.join(kaynak, a, "frame_*.png"))):
            rel = os.path.relpath(f, kaynak)
            im = cv2.imread(f, cv2.IMREAD_UNCHANGED)
            if im is None or im.shape[2] != 4:
                rapor["uyarilar"].append(f"{rel}: okunamadı veya alfa kanalı yok"); continue
            al = im[..., 3] > 8
            rm = kalinti_maskesi(im)
            for (x0, y0, x1, y1) in KORU.get(rel, []):
                rm[y0:y1, x0:x1] = False
            for (x0, y0, x1, y1) in EL_ILE.get(rel, []):
                bolge = np.zeros_like(al); bolge[y0:y1, x0:x1] = True
                rm |= bolge & al & acik_piksel(im)
            temiz = im.copy(); temiz[rm, 3] = 0
            ys, xs = np.nonzero(temiz[..., 3] > 8)
            ust = ys < ys.min() + 0.4 * (ys.max() - ys.min())
            x_min, y_min = xs.min(), ys.min()
            konum = None
            if ref is not None:
                res = cv2.matchTemplate(ref, im[..., :3], cv2.TM_SQDIFF, mask=(al * 255).astype(np.uint8))
                mn, _, loc, _ = cv2.minMaxLoc(res)
                konum = (int(loc[0]), int(loc[1]), round(float(mn) / al.sum(), 2))
            kirp = temiz[y_min:ys.max() + 1, x_min:xs.max() + 1]  # içerik kutusuna kırp
            kareler[rel] = dict(im=kirp, alt=int(ys.max() - y_min), cx=float(xs[ust].mean() - x_min),
                                konum=(konum[0] + int(x_min), konum[1] + int(y_min), konum[2]) if konum else None)
            rapor["kareler"][rel] = {
                "boyut": [int(im.shape[1]), int(im.shape[0])], "silinen_kalinti_px": int(rm.sum()),
                "yari_saydam_px": int(((im[..., 3] > 8) & (im[..., 3] < 247)).sum()),
                "kenara_degiyor": bool(al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any()),
                "referans_eslesme": konum}
    if not kareler:
        sys.exit("kare bulunamadı")
    # zemin ofseti (referans sayfasından): satırdaki en alt nokta = zemin
    for a in ANIMASYONLAR:
        ks = [k for k in kareler if k.startswith(a + "/")]
        if ref is not None and all(kareler[k]["konum"] for k in ks):
            zemin = max(kareler[k]["konum"][1] + kareler[k]["alt"] for k in ks)
            for k in ks:
                kareler[k]["yukseklik"] = zemin - (kareler[k]["konum"][1] + kareler[k]["alt"])
        else:
            for k in ks: kareler[k]["yukseklik"] = 0
            rapor["uyarilar"].append(f"{a}: referans eşleşmesi yok → zıplama yüksekliği bilinmiyor (0 alındı)")
    sol = max(k["cx"] for k in kareler.values()); sag = max(k["im"].shape[1] - k["cx"] for k in kareler.values())
    ust = max(k["alt"] + k["yukseklik"] for k in kareler.values())
    PAD = 4
    W = int(np.ceil(max(sol, sag))) * 2 + 2 * PAD; H = int(ust) + 1 + 2 * PAD
    cax, cay = W // 2, H - PAD  # çapa: alt-orta (ayakların zemine bastığı nokta)
    manifest = {"schema": 2, "characterId": kid, "displayName": "NØVEX Explorer",
                "canvas": {"width": W, "height": H, "anchor": {"x": cax, "y": cay}},
                "render": {"pixelArt": True, "note": "Düşük çözünürlüklü kaynak: tam sayı katlarla, yumuşatmasız ölçekle."},
                "source": {"kit": rapor["kit"], "license": "BEKLİYOR — kaynak/izin bilgisi Emir'den (LISANS.md)"},
                "animations": {}}
    fps = {"idle": 5, "run": 10, "jump": 8}; loop = {"idle": True, "run": True, "jump": False}
    for a in ANIMASYONLAR:
        os.makedirs(os.path.join(out, a), exist_ok=True)
        frames = []
        for k in sorted(x for x in kareler if x.startswith(a + "/")):
            d = kareler[k]; t = np.zeros((H, W, 4), np.uint8)
            x0 = int(round(cax - d["cx"])); y0 = int(cay - d["yukseklik"] - d["alt"])
            h, w = d["im"].shape[:2]
            t[y0:y0 + h, x0:x0 + w] = d["im"]
            cv2.imwrite(os.path.join(out, k), t)
            frames.append(k); rapor["kareler"][k]["zemin_ustu_px"] = int(d["yukseklik"])
        manifest["animations"][a] = {"frames": frames, "fps": fps[a], "loop": loop[a]}
    manifest["animations"]["jump"]["next"] = "idle"
    for gelecek in ["walk", "talk", "point", "lookLeft", "lookRight", "wave", "sit", "stand", "crouch",
                    "interact", "surprise", "think", "explain"]:
        manifest.setdefault("planned", []).append(gelecek)
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # kontrol sayfası: her kare tuvalde, zemin çizgisi ve çapa işaretli, 2x
    os.makedirs(os.path.join(out, "qc"), exist_ok=True)
    satirlar = []
    for a in ANIMASYONLAR:
        hucre = []
        for k in manifest["animations"][a]["frames"]:
            t = cv2.imread(os.path.join(out, k), cv2.IMREAD_UNCHANGED)
            v = np.zeros((H, W, 3), np.uint8); v[:] = (70, 35, 15)
            m = t[..., 3] > 8; v[m] = t[..., :3][m]
            cv2.line(v, (0, cay), (W, cay), (0, 200, 255), 1); cv2.circle(v, (cax, cay), 2, (0, 0, 255), -1)
            hucre.append(cv2.resize(v, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
        satirlar.append(np.hstack(hucre))
    cv2.imwrite(os.path.join(out, "qc", "kontrol_sayfasi.png"), np.vstack(satirlar))
    json.dump(rapor, open(os.path.join(out, "qc", "kalite_raporu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"tuval {W}x{H}, çapa ({cax},{cay}); kare: {len(kareler)}; silinen kalıntı px: "
          f"{sum(r['silinen_kalinti_px'] for r in rapor['kareler'].values())}; uyarı: {len(rapor['uyarilar'])}")


if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
