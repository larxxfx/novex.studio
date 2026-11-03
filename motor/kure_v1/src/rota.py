"""ROTA MODU — "The longest straight line you can sail" (EN Short). Yeni dosya: render.py'yi DEĞİŞTİRMEZ, yalnızca
çekirdeğini (Cam, render_globe, polyline_layers, glow_lines, dot, ring, Text, font, post) kütüphane olarak kullanır.

Kullanım:
  python3 src/rota.py kare <t> <cikti.png> --zaman zaman.json --srt altyazi.srt
  python3 src/rota.py video <cikti.mp4> --zaman zaman.json --srt altyazi.srt [--bas 0 --son 45]
zaman.json: anlatıcının cümle zamanları [{i, bas, son, metin}] (11 cümle). Sahneler cümlelere kilitlidir → ses değişirse görüntü uyar.
Gerekli: build/ (render.py ile aynı) + build/rota_okyanus.json (src/rota_geo.py).
"""
import argparse, json, math, os, re, subprocess, sys
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # noqa: E402  (mevcut motor; içeriği değiştirilmedi)

W, H, FPS = R.W, R.H, R.FPS
ROTA = json.load(open(os.path.join(R.B, "rota_okyanus.json")))
RLL = np.asarray(ROTA["nokta_10km"], float)          # 10 km aralıklı (lon, lat)
RKM = ROTA["uzunluk_km"]
KEY = ROTA["anahtar"]
SAGRES, QUANZHOU = (-8.94, 37.01), (118.59, 24.87)     # kara rotası uçları (yaklaşık; etiket kaynaktaki 11.241 km)
TURK = np.array([0.25, 0.86, 0.82], np.float32); WHITE = np.array([1.0, 1.0, 1.0], np.float32)
EL = R.ELECTRIC; GOLD = R.GOLD


def kara_rotasi(n=600):
    return np.array([[math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(np.clip(v[2], -1, 1)))]
                     for v in (R.slerp(R.xyz(*SAGRES), R.xyz(*QUANZHOU), s) for s in np.linspace(0, 1, n))])
KARA = kara_rotasi()


def ll3(lon, lat): return R.xyz(lon, lat)
def rota_on(frac): return RLL[: max(2, int(len(RLL) * R.clamp01(frac)))]
def km_index(km): return int(np.clip(km / RKM * (len(RLL) - 1), 0, len(RLL) - 1))


def kamera(target_ll, D, P=0.0, head=0.0, up=None):
    T = ll3(*target_ll)
    up = R.local_north(*target_ll) if up is None else up
    return R.Cam(T, up, D, P=P, head=head)


def isik(cam):
    return R.norm(cam.C * 1.0 + np.array([0.3, 0.2, 0.6]))


def cizgi(img, cam, ll, renk, w=5, glow=22, a=1.0):
    R.glow_lines(img, R.polyline_layers(cam, [ll], lift=1.002), renk, w, glow, a)


def etiket(tx, cam, ll, s, dy=-46, a=1.0, boyut=34, renk=(235, 244, 255)):
    xy, vis = cam.project(ll3(*ll)[None] * 1.002)
    if vis[0] and a > 0:
        tx.text((float(np.clip(xy[0][0], 220, 860)), float(np.clip(xy[0][1] + dy, 470, 1180))), s, R.font("InterDisplay-Bold.otf", boyut), renk, a)
    return xy[0] if vis[0] else None


def sayac(tx, km, a=1.0, y=300):
    tx.text((W / 2, y), f"{int(round(km)):,} km", R.font("InterDisplay-Black.otf", 104), (255, 255, 255), a)


def duz_harita(t_rel, frac):
    """Eşdikdörtgen düz harita + rota (S3)."""
    tex = R.WORLD[1] if len(R.WORLD) > 1 else R.WORLD[0]
    mw, mh = W, W // 2; top = 650
    m = cv2.resize(tex, (mw, mh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255 * 0.85
    img = np.zeros((H, W, 3), np.float32); img[:] = (0.01, 0.025, 0.07)
    img[top:top + mh] = m
    ll = rota_on(frac); x = (ll[:, 0] + 180) / 360 * mw; y = top + (90 - ll[:, 1]) / 180 * mh
    kes = np.where(np.abs(np.diff(ll[:, 0])) > 180)[0] + 1
    paths = [np.stack([a, b], -1) for a, b in zip(np.split(x, kes), np.split(y, kes)) if len(a) > 1]
    R.glow_lines(img, paths, WHITE, 5, 16, 1.0)
    return img


def sahne_zamanlari(z):
    b = [s["bas"] for s in z]
    return {"s1": (0.0, b[1] - 0.2), "s2": (b[1] - 0.2, b[2] - 0.2), "s3": (b[2] - 0.2, b[3] - 0.2), "s4": (b[3] - 0.2, b[4] - 0.2),
            "s5": (b[4] - 0.2, b[5] - 0.2), "s6": (b[5] - 0.2, b[6] - 0.2), "s7": (b[6] - 0.2, b[7] - 0.2), "s8": (b[7] - 0.2, b[8] - 0.2),
            "s9": (b[8] - 0.2, b[9] - 0.2), "s10": (b[9] - 0.2, b[10] - 0.2), "s11": (b[10] - 0.2, z[-1]["son"] + 0.9)}


def srt_oku(yol):
    blok = re.split(r"\n\s*\n", open(yol, encoding="utf-8").read().strip()); out = []
    def sn(x): h, m, s = x.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
    for b in blok:
        l = b.strip().splitlines(); a, c = l[1].split(" --> "); out.append((sn(a), sn(c), " ".join(l[2:])))
    return out


def satirla(metin, f, maks=760):
    kel, sat, cur = metin.split(), [], ""
    for k in kel:
        d = (cur + " " + k).strip()
        if f.getlength(d) <= maks: cur = d
        else: sat.append(cur); cur = k
    return sat + [cur]


def altyazi(tx, t, caps):
    f = R.font("InterDisplay-Bold.otf", 50)
    for a, b, metin in caps:
        if a - 0.05 <= t < b + 0.12:
            al = R.ease(R.seg(t, a - 0.05, a + 0.12)) * (1 - R.seg(t, b, b + 0.12))
            for k, s in enumerate(satirla(metin, f)):
                tx.text((W / 2, 1300 + k * 64), s, f, (255, 255, 255), al)


def kare(t, Z, caps, prev=None):
    S = Z["sahne"]; tx = R.Text(); mb = 0.0
    def ic(ad): a, b = S[ad]; return a <= t < b
    def lt(ad): return t - S[ad][0]
    def ln(ad): a, b = S[ad]; return R.clamp01((t - a) / (b - a))
    if ic("s1"):                                    # kanca: çizgi küre üzerinde koşar, sayaç
        u = ln("s1"); cam = kamera((lerp(20, 60, u), lerp(-5, 5, u)), lerp(3.6, 3.1, u), P=0)
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t)
        f = R.ease_io3(R.seg(t, 0.25, S["s1"][1] - 0.4))
        cizgi(img, cam, rota_on(f), WHITE, 5, 26)
        sayac(tx, RKM * f, R.ease(R.seg(t, 0.1, 0.4)))
        tx.text((W / 2, 400), "NO LAND", R.font("InterDisplay-Bold.otf", 52), (120, 230, 220), R.ease(R.seg(t, 2.4, 2.8)))
    elif ic("s2"):                                  # Sonmiani, batıya çıkış
        u = ln("s2"); cam = kamera((lerp(66.0, 62.0, u), 24.5), lerp(0.55, 0.42, u), P=lerp(30, 45, u), head=-15)
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t, fog=0.2)
        cizgi(img, cam, RLL[: max(2, int(R.ease(u) * 90))], WHITE, 6, 22)
        xy = etiket(tx, cam, ROTA["bas"], "SONMIANI, PAKISTAN", -60, R.ease(R.seg(u, 0.05, 0.25)))
        if xy is not None:
            R.dot(img, xy, 9, R.RED, 14, 1.0); R.ring(img, xy, 18 + 50 * ((t * 0.9) % 1), R.RED, 3, 0.8 * (1 - (t * 0.9) % 1))
    elif ic("s3"):                                  # düz harita: S-eğrisi
        img = duz_harita(lt("s3"), R.ease_io3(R.seg(ln("s3"), 0.0, 0.85)))
        tx.text((W / 2, 520), "ON A FLAT MAP", R.font("InterDisplay-Bold.otf", 48), (150, 190, 255), R.ease(R.seg(ln("s3"), 0.05, 0.25)))
    elif ic("s4"):                                  # kürede tek düz çizgi: kamera rota düzleminde
        u = ln("s4")
        mid = RLL[len(RLL) // 2]; nrm = np.cross(ll3(*RLL[0]), ll3(*mid)); nrm /= np.linalg.norm(nrm)
        hedef = ll3(*RLL[int(len(RLL) * 0.74)])
        cam = R.Cam(hedef, nrm, lerp(3.4, 3.0, u), P=0, head=lerp(25, 0, R.ease_io3(R.seg(u, 0, 0.6))))
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t)
        cizgi(img, cam, RLL, WHITE, 6, 28)
        tx.text((W / 2, 520), "ON A GLOBE: ONE STRAIGHT LINE", R.font("InterDisplay-Bold.otf", 44), (120, 230, 220), R.ease(R.seg(u, 0.35, 0.55)))
    elif ic("s5") or ic("s6"):                      # boğazlar
        ad = "s5" if ic("s5") else "s6"; u = ln(ad); k = KEY["mozambik" if ad == "s5" else "drake"]
        i0 = km_index(k["km"]); a = RLL[max(0, i0 - 60)]; b = RLL[min(len(RLL) - 1, i0 + 60)]
        hedef = R.slerp(ll3(*a), ll3(*b), lerp(0.2, 0.8, u))
        lon, lat = math.degrees(math.atan2(hedef[1], hedef[0])), math.degrees(math.asin(hedef[2]))
        cam = kamera((lon, lat), 0.75 if ad == "s5" else 1.05, P=35 if ad == "s5" else 15, head=(70 if ad == "s5" else -100))
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t, fog=0.15)
        cizgi(img, cam, RLL[: i0 + int(lerp(-40, 60, u))], WHITE, 6, 24)
        if ad == "s5":
            etiket(tx, cam, (33.0, -15.0), "AFRICA", 0, R.ease(R.seg(u, 0.1, 0.3)), 40)
            etiket(tx, cam, (46.8, -19.5), "MADAGASCAR", 0, R.ease(R.seg(u, 0.2, 0.4)), 36)
        else:
            etiket(tx, cam, (-69.0, -53.5), "SOUTH AMERICA", 0, R.ease(R.seg(u, 0.1, 0.3)), 36)
            etiket(tx, cam, (-62.0, -64.5), "ANTARCTICA", 0, R.ease(R.seg(u, 0.2, 0.4)), 36)
        sayac(tx, k["km"] + lerp(-400, 600, u), 0.9, 300)
    elif ic("s7"):                                  # Pasifik: hızlı uçuş + sayaç
        u = R.ease_io3(ln("s7")); i0 = km_index(KEY["drake"]["km"] + 700); i1 = km_index(RKM - 2500)
        i = int(lerp(i0, i1, u)); lon, lat = RLL[i]
        cam = kamera((lon, lat), 1.1, P=25, head=-30)
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t, fog=0.1)
        cizgi(img, cam, RLL[: i + 1], WHITE, 6, 24)
        sayac(tx, i / (len(RLL) - 1) * RKM, 1.0); mb = 0.25
        tx.text((W / 2, 400), "PACIFIC OCEAN", R.font("InterDisplay-Bold.otf", 44), (150, 190, 255), R.ease(R.seg(u, 0.1, 0.3)))
    elif ic("s8"):                                  # Kamçatka varış
        u = ln("s8"); cam = kamera((lerp(168, 163.5, R.ease(u)), lerp(55, 58.2, R.ease(u))), lerp(0.9, 0.45, R.ease_io3(u)), P=40, head=-20)
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t, fog=0.2)
        cizgi(img, cam, RLL, WHITE, 6, 24)
        xy = etiket(tx, cam, ROTA["son"], "KAMCHATKA, RUSSIA", -60, R.ease(R.seg(u, 0.3, 0.5)))
        if xy is not None:
            pa = R.ease_out(R.seg(u, 0.25, 0.45)); R.dot(img, xy, 10 * pa, GOLD, 16, pa)
        sayac(tx, RKM, 1.0)
    elif ic("s9"):                                  # kaynak kartı
        u = ln("s9"); cam = kamera((lerp(140, 100, u), 10), lerp(2.2, 3.4, R.ease_io3(u)), P=0)
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t)
        cizgi(img, cam, RLL, WHITE, 5, 24)
        a = R.ease(R.seg(u, 0.1, 0.3))
        tx.rrect((140, 280, 940, 470), 22, (6, 14, 34, 215), a, (60, 150, 255, 230), 3)
        tx.text((W / 2, 335), "Confirmed in 2018", R.font("InterDisplay-Bold.otf", 46), (255, 255, 255), a, shadow=False)
        tx.text((W / 2, 400), "Chabukswar & Mukherjee · arXiv:1804.07389", R.font("InterDisplay-SemiBold.otf", 28), (170, 200, 255), a, shadow=False)
    elif ic("s10"):                                 # kara rotası
        u = ln("s10"); cam = kamera((lerp(20, 60, u), 38), lerp(2.0, 1.8, u), P=10)
        img, _, _ = R.render_globe(cam, isik(cam), 1.0, 0, t)
        f = R.ease_io3(R.seg(u, 0.1, 0.8)); cizgi(img, cam, KARA[: max(2, int(len(KARA) * f))], TURK, 7, 26)
        etiket(tx, cam, SAGRES, "PORTUGAL", 46, R.ease(R.seg(u, 0.05, 0.2)), 32)
        etiket(tx, cam, QUANZHOU, "CHINA", 46, R.ease(R.seg(u, 0.75, 0.9)), 32)
        tx.text((W / 2, 300), "11,241 km", R.font("InterDisplay-Black.otf", 104), (120, 230, 220), R.ease(R.seg(u, 0.55, 0.75)))
        tx.text((W / 2, 400), "ON LAND", R.font("InterDisplay-Bold.otf", 48), (120, 230, 220), R.ease(R.seg(u, 0.6, 0.8)))
    else:                                           # soru + kapanış
        u = ln("s11"); cam = kamera((lerp(100, 120, u), 0), 3.2, P=0)
        img, _, _ = R.render_globe(cam, isik(cam), 0.8, 0.2, t)
        cizgi(img, cam, RLL, WHITE, 4, 18, 0.8)
        a = R.ease(R.seg(u, 0.05, 0.2))
        tx.rrect((140, 300, 940, 520), 26, (6, 14, 34, 220), a, (60, 150, 255, 230), 3)
        tx.text((W / 2, 370), "Could a ship sail it", R.font("InterDisplay-Bold.otf", 50), (255, 255, 255), a, shadow=False)
        tx.text((W / 2, 440), "non-stop?", R.font("InterDisplay-Bold.otf", 50), (255, 255, 255), a, shadow=False)
        tx.text((W / 2, 610), "YES  or  NO?", R.font("InterDisplay-Black.otf", 76), (120, 230, 220), R.ease(R.seg(u, 0.25, 0.4)))
        tx.text((W / 2, 1150), "NØVEX", R.font("InterDisplay-Black.otf", 70), (255, 255, 255), R.ease(R.seg(u, 0.6, 0.8)))
    if t < 2.6:
        tx.text((W / 2, 175), "NØVEX", R.font("InterDisplay-SemiBold.otf", 30), (150, 190, 255), R.ease(R.seg(t, 0.1, 0.4)) * (1 - R.seg(t, 2.2, 2.6)), shadow=False)
    if R.SCRIM is None:
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        R.SCRIM = (np.exp(-((yy - 1330) / 220) ** 2) * 0.55).astype(np.float32)
    img = img * (1 - R.SCRIM) + np.array([0.0, 0.01, 0.04], np.float32) * R.SCRIM
    altyazi(tx, t, caps)
    img = tx.composite(img)
    return R.post(img, t, prev, mb if prev is not None else 0)


def lerp(a, b, u): return a + (b - a) * u


def main():
    p = argparse.ArgumentParser(); p.add_argument("mod"); p.add_argument("args", nargs="+")
    p.add_argument("--zaman", required=True); p.add_argument("--srt", required=True)
    p.add_argument("--bas", type=float, default=0.0); p.add_argument("--son", type=float, default=None)
    a = p.parse_args()
    z = json.load(open(a.zaman)); Z = {"sahne": sahne_zamanlari(z)}; caps = srt_oku(a.srt)
    sure = Z["sahne"]["s11"][1]
    if a.mod == "kare":
        im = kare(float(a.args[0]), Z, caps); cv2.imwrite(a.args[1], cv2.cvtColor(R.to_u8(im), cv2.COLOR_RGB2BGR)); return
    out = a.args[0]; f0 = round(a.bas * FPS); f1 = round((a.son if a.son is not None else sure) * FPS)
    tmp = out[:-4] + ".part.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                           "-color_trc", "bt709", "-color_range", "tv", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-r", str(FPS), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    prev = None
    for fi in range(f0, f1):
        im = kare(fi / FPS, Z, caps, prev); prev = im
        pr.stdin.write(R.to_u8(im).tobytes())
        if (fi - f0) % 60 == 0: print("kare", fi, "/", f1, flush=True)
    pr.stdin.close(); rc = pr.wait()
    if rc == 0: os.replace(tmp, out)
    sys.exit(rc)


if __name__ == "__main__":
    main()
