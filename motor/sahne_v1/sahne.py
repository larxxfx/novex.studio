"""sahne_v1 — konudan bağımsız 2D sinematik sahne motoru (9:16). Her video kendi palet/tipografi/doku/kamera dilini seçer.
Sahneler anlatıcının cümle zamanlarına kilitlenir (zaman.json, araclar/anlatim_ifade.py çıktısı).

Kullanım:
  python3 motor/sahne_v1/sahne.py kare  <plan.json> <zaman.json> <t> <out.png> [--srt altyazi.srt] [--kapak]
  python3 motor/sahne_v1/sahne.py video <plan.json> <zaman.json> <out.mp4> [--srt altyazi.srt] [--bas s] [--son s]

plan.json (her video için ayrı; GORSEL_YON.md'de gerekçesi yazılır):
{ "dil": "arsiv|modern|daktilo",
  "palet": {"zemin0":"#1b140c","zemin1":"#3a2a16","vurgu":"#e0a84b","metin":"#f3e6cc","ikincil":"#9c8a6a","kara":"#5a4630","deniz":"#20180f"},
  "doku": "kagit|gren|yildiz|yok", "kamera": "itme|kaydirma|sabit", "kapanis_sn": 2.0,
  "kapak": {"ust": "…", "ana": "…", "zemin_sahne": 0},
  "sahneler": [ {"cumle": 1, "tur": "<tür>", ...parametreler} ] }   # her sahne verilen cümlenin başlangıcında başlar
Türler:
  baslik    {ust, ana, alt}                         kelime kelime yükselen başlık
  sayi      {bas, son, birim, etiket, ondalik}       sayaç
  harita    {bolge:[lon0,lat0,lon1,lat1], noktalar:[[lon,lat,"etiket"]], cizgi:[[lon,lat],...], yay:true, baslik}
  zaman     {olaylar:[["2560 BC","Great Pyramid"],...], baslik}   zaman çizelgesi
  karsilastir {ogeler:[["Label", 120], ...], birim, baslik}       büyüyen çubuklar
  alinti    {metin, kaynak}                          belge/alıntı kartı
  liste     {baslik, maddeler:[...]}                 sırayla beliren maddeler
  soru      {metin, secenekler:["YES","NO"]}         kapanış katılım sorusu
"""
import argparse, json, math, os, re, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
KOK = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.abspath(os.path.join(KOK, "..", ".."))
FONT = {
    "modern": {"agir": "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", "kalin": "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
               "orta": "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf", "ince": "/usr/share/fonts/opentype/inter/InterDisplay-Light.otf"},
    "arsiv": {"agir": "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf", "kalin": "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf",
              "orta": "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf", "ince": "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"},
    "daktilo": {"agir": "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", "kalin": "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
                "orta": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", "ince": "/usr/share/fonts/truetype/liberation/LiberationMono-Italic.ttf"},
}
_FC = {}
def font(dil, agirlik, boyut):
    k = (dil, agirlik, boyut)
    if k not in _FC: _FC[k] = ImageFont.truetype(FONT.get(dil, FONT["modern"])[agirlik], boyut)
    return _FC[k]

def renk(h, a=255):
    h = h.lstrip("#"); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

def cl(x): return max(0.0, min(1.0, x))
def seg(t, a, b): return cl((t - a) / max(b - a, 1e-6))
def ease(x): x = cl(x); return x * x * (3 - 2 * x)
def eout(x): x = cl(x); return 1 - (1 - x) ** 3

# ---------- dünya haritası (Natural Earth 50m, kure_v1 varlıklarından) ----------
_DUNYA = None
def dunya():
    global _DUNYA
    if _DUNYA is None:
        g = json.load(open(os.path.join(DEPO, "motor/kure_v1/data/ne/geojson/ne_50m_admin_0_countries.geojson")))
        polys = []
        for f in g["features"]:
            geo = f["geometry"]; cs = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
            for p in cs:
                a_ = np.asarray(p[0], float)
                if np.ptp(a_[:, 0]) > 180:          # 180. meridyeni geçen çokgen (Rusya, Fiji, Antarktika): aç ve iki kopya çiz
                    b_ = a_.copy(); b_[b_[:, 0] < 0, 0] += 360; polys += [b_, b_ - [360, 0]]
                else: polys.append(a_)
        _DUNYA = polys
    return _DUNYA

# ---------- arka plan katmanları ----------
_ZEMIN = {}
def zemin(plan):
    k = json.dumps(plan["palet"]) + plan.get("doku", "")
    if k in _ZEMIN: return _ZEMIN[k]
    p = plan["palet"]; rng = np.random.default_rng(11)
    y = np.linspace(0, 1, H)[:, None, None]
    z0 = np.array(renk(p["zemin0"])[:3], np.float32); z1 = np.array(renk(p["zemin1"])[:3], np.float32)
    img = (z0 * (1 - y) + z1 * y) * np.ones((1, W, 1), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2)
    img *= (1.15 - 0.75 * r[..., None] ** 1.6)
    d = plan.get("doku", "gren")
    if d == "kagit":
        n = cv2.GaussianBlur(rng.standard_normal((H // 4, W // 4)).astype(np.float32), (0, 0), 2.5)
        n = cv2.resize(n, (W, H)); img *= (1 + 0.06 * n[..., None])
        lif = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.8)
        img += 6 * lif[..., None]
    elif d == "yildiz":
        for _ in range(900):
            x, yv = rng.integers(0, W), rng.integers(0, H); b = rng.uniform(60, 230) * rng.uniform(0.2, 1) ** 2
            cv2.circle(img, (int(x), int(yv)), 1 if b < 150 else 2, (b, b, b), -1)
    _ZEMIN[k] = np.clip(img, 0, 255).astype(np.float32)
    return _ZEMIN[k]

def gren(img, t, plan):
    if plan.get("doku", "gren") == "yok": return img
    rng = np.random.default_rng(int(t * FPS) + 3)
    n = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    return img + cv2.resize(n, (W, H), interpolation=cv2.INTER_NEAREST)[..., None] * (5.0 if plan.get("doku") == "kagit" else 3.5)

# ---------- metin yardımcıları ----------
def satirla(metin, f, maks):
    out, cur = [], ""
    for k in metin.split():
        d = (cur + " " + k).strip()
        if f.getlength(d) <= maks or not cur: cur = d
        else: out.append(cur); cur = k
    return out + ([cur] if cur else [])

def yazi(dr, xy, s, f, fill, a=1.0, anchor="mm", golge=True):
    if a <= 0.01: return
    c = fill[:3] + (int(fill[3] * a) if len(fill) > 3 else int(255 * a),)
    if golge: dr.text((xy[0] + 3, xy[1] + 4), s, font=f, fill=(0, 0, 0, int(140 * a)), anchor=anchor)
    dr.text(xy, s, font=f, fill=c, anchor=anchor)

# ---------- sahne çizicileri: (katman RGBA, dr, plan, s, u (0..1 sahne ilerlemesi), ts (sahne içi sn)) ----------
def c_baslik(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]
    if s.get("ust"): yazi(dr, (W / 2, 560), s["ust"].upper(), font(dil, "orta", 40), renk(p["vurgu"]), ease(seg(ts, 0.1, 0.5)))
    f = font(dil, "agir", s.get("boyut", 112)); sat = satirla(s["ana"], f, 860); y0 = 760 - (len(sat) - 1) * 60
    kel_i = 0
    for i, sa in enumerate(sat):
        xs = W / 2 - f.getlength(sa) / 2; x = xs
        for k in sa.split():
            a = ease(seg(ts, 0.25 + kel_i * 0.12, 0.6 + kel_i * 0.12)); dy = (1 - a) * 40
            yazi(dr, (x, y0 + i * 124 + dy), k, f, renk(p["metin"]), a, anchor="lm"); x += f.getlength(k + " "); kel_i += 1
    if s.get("alt"): yazi(dr, (W / 2, y0 + len(sat) * 124 + 40), s["alt"], font(dil, "ince", 44), renk(p["ikincil"]), ease(seg(ts, 1.0, 1.5)))

def c_sayi(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]
    v = s["bas"] + (s["son"] - s["bas"]) * eout(seg(ts, 0.2, max(1.0, s.get("sure", 2.2))))
    od = s.get("ondalik", 0); txt = f"{v:,.{od}f}"
    f = font(dil, "agir", 190 if len(txt) < 7 else 150)
    yazi(dr, (W / 2, 760), txt, f, renk(p["vurgu"]), ease(seg(ts, 0.0, 0.3)))
    if s.get("birim"): yazi(dr, (W / 2, 900), s["birim"], font(dil, "kalin", 64), renk(p["metin"]), ease(seg(ts, 0.3, 0.6)))
    if s.get("etiket"):
        for i, sa in enumerate(satirla(s["etiket"], font(dil, "orta", 46), 800)):
            yazi(dr, (W / 2, 1010 + i * 58), sa, font(dil, "orta", 46), renk(p["ikincil"]), ease(seg(ts, 0.6, 1.0)))
    gen = 520 * ease(seg(ts, 0.1, 0.8)); dr.rectangle((W / 2 - gen / 2, 640, W / 2 + gen / 2, 646), fill=renk(p["vurgu"], 160))

def harita_proj(bolge):
    lon0, lat0, lon1, lat1 = bolge
    kx = 940 / (lon1 - lon0); ky = 940 / (lat1 - lat0); k = min(kx, ky * 1.0)
    cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    return lambda lon, lat: (W / 2 + (lon - cx) * k, 820 - (lat - cy) * k * 1.15)

def gc(a, b, n=120):
    def v(lon, lat): lo, la = math.radians(lon), math.radians(lat); return np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
    A, B = v(*a), v(*b); om = math.acos(np.clip(A @ B, -1, 1)) or 1e-9; out = []
    for t in np.linspace(0, 1, n):
        P = (math.sin((1 - t) * om) * A + math.sin(t * om) * B) / math.sin(om)
        out.append((math.degrees(math.atan2(P[1], P[0])), math.degrees(math.asin(P[2]))))
    return out

def c_harita(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]
    hedef = s.get("bolge", [-180, -60, 180, 80]); bas = s.get("bas_bolge", [-180, -60, 180, 80])
    z = ease(seg(ts, 0.0, 1.6)) if s.get("yakinlas", True) else 1.0
    b = [bas[i] + (hedef[i] - bas[i]) * z for i in range(4)]; pr = harita_proj(b)
    kara = renk(p.get("kara", p["ikincil"]), 235); kenar = renk(p["metin"], 70)
    if p.get("deniz"): dr.rectangle((0, 0, W, H), fill=renk(p["deniz"], 120))
    for poly in dunya():
        if poly[:, 0].max() < b[0] - 20 or poly[:, 0].min() > b[2] + 20 or poly[:, 1].max() < b[1] - 20 or poly[:, 1].min() > b[3] + 20: continue
        pts = [pr(x, y) for x, y in poly[:: max(1, len(poly) // 400)]]
        if len(pts) > 2: dr.polygon(pts, fill=kara, outline=kenar)
    if s.get("cizgi"):
        yol = s["cizgi"]
        if s.get("yay"): yol = sum((gc(yol[i], yol[i + 1]) for i in range(len(yol) - 1)), [])
        n = max(2, int(len(yol) * ease(seg(ts, 0.9, 0.9 + s.get("cizim_sn", 2.0)))))
        pts = [pr(x, y) for x, y in yol[:n]]
        for gw, ga in ((18, 40), (9, 90), (4, 255)): dr.line(pts, fill=renk(p["vurgu"], ga), width=gw, joint="curve")
    for i, (lon, lat, et) in enumerate(s.get("noktalar", [])):
        a = ease(seg(ts, 0.8 + i * 0.35, 1.2 + i * 0.35)); x, y = pr(lon, lat)
        if a <= 0: continue
        r = 10 + 30 * ((ts * 0.8 + i * 0.3) % 1); dr.ellipse((x - r, y - r, x + r, y + r), outline=renk(p["vurgu"], int(200 * (1 - (r - 10) / 30) * a)), width=3)
        dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=renk(p["vurgu"], int(255 * a)))
        if et: yazi(dr, (min(max(x, 260), 820), y - 46), et.upper(), font(dil, "kalin", 34), renk(p["metin"]), a)
    if s.get("baslik"): yazi(dr, (W / 2, 330), s["baslik"].upper(), font(dil, "kalin", 50), renk(p["vurgu"]), ease(seg(ts, 0.2, 0.6)))

def c_zaman(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]; ol = s["olaylar"]; n = len(ol)
    x0, x1, y = 300, 780, 820   # etiket genişliği 300 → merkezler 300–780 ise metin x 150–930 (güvenli alan 140–940)
    dr.line((x0, y, x0 + (x1 - x0) * ease(seg(ts, 0.1, 1.0)), y), fill=renk(p["ikincil"], 220), width=4)
    for i, (yil, et) in enumerate(ol):
        x = x0 + (x1 - x0) * (i / max(n - 1, 1)); a = ease(seg(ts, 0.4 + i * 0.45, 0.8 + i * 0.45))
        if a <= 0: continue
        dr.ellipse((x - 12, y - 12, x + 12, y + 12), fill=renk(p["vurgu"], int(255 * a)))
        ust = i % 2 == 0
        yazi(dr, (x, y - 70 if ust else y + 70), str(yil), font(dil, "agir", 50), renk(p["vurgu"]), a)
        sats = satirla(et, font(dil, "orta", 34), 300)
        for j, sa in enumerate(sats):   # üstteki etiket yukarı doğru büyür ama satır sırası korunur
            yazi(dr, (x, (y - 130 - (len(sats) - 1 - j) * 40) if ust else (y + 130 + j * 40)), sa, font(dil, "orta", 34), renk(p["metin"]), a)
    if s.get("baslik"): yazi(dr, (W / 2, 420), s["baslik"].upper(), font(dil, "kalin", 50), renk(p["vurgu"]), ease(seg(ts, 0.1, 0.5)))

def c_karsilastir(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]; og = s["ogeler"]; mx = max(v for _, v in og)
    for i, (et, v) in enumerate(og):
        y = 560 + i * 210; a = ease(seg(ts, 0.2 + i * 0.4, 0.5 + i * 0.4)); gen = 760 * (v / mx) * eout(seg(ts, 0.3 + i * 0.4, 1.3 + i * 0.4))
        yazi(dr, (160, y), et, font(dil, "kalin", 46), renk(p["metin"]), a, anchor="lm")
        dr.rectangle((160, y + 40, 160 + gen, y + 110), fill=renk(p["vurgu"] if i == len(og) - 1 else p["ikincil"], int(235 * a)))
        if gen > 10: yazi(dr, (min(170 + gen + 20, 900), y + 75), f"{v:,} {s.get('birim', '')}".strip(), font(dil, "kalin", 42), renk(p["metin"]), a, anchor="lm" if gen < 600 else "rm")
    if s.get("baslik"): yazi(dr, (W / 2, 420), s["baslik"].upper(), font(dil, "kalin", 50), renk(p["vurgu"]), ease(seg(ts, 0.1, 0.5)))

def c_alinti(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]; a = ease(seg(ts, 0.1, 0.6))
    dr.rounded_rectangle((120, 520, 960, 1160), 18, fill=renk(p["zemin1"], int(200 * a)), outline=renk(p["vurgu"], int(200 * a)), width=3)
    yazi(dr, (180, 600), "“", font(dil, "agir", 140), renk(p["vurgu"]), a, anchor="lm", golge=False)
    f = font(dil, "orta", 54)
    for i, sa in enumerate(satirla(s["metin"], f, 700)):
        yazi(dr, (W / 2, 700 + i * 70), sa, f, renk(p["metin"]), ease(seg(ts, 0.3 + i * 0.15, 0.7 + i * 0.15)), golge=False)
    if s.get("kaynak"): yazi(dr, (W / 2, 1100), "— " + s["kaynak"], font(dil, "ince", 38), renk(p["ikincil"]), ease(seg(ts, 0.9, 1.3)), golge=False)

def c_liste(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]
    if s.get("baslik"): yazi(dr, (W / 2, 470), s["baslik"].upper(), font(dil, "kalin", 52), renk(p["vurgu"]), ease(seg(ts, 0.1, 0.5)))
    for i, m in enumerate(s["maddeler"]):
        a = ease(seg(ts, 0.4 + i * 0.5, 0.8 + i * 0.5)); y = 620 + i * 130
        dr.rectangle((150, y - 8, 162, y + 8), fill=renk(p["vurgu"], int(255 * a)))
        yazi(dr, (200 + (1 - a) * 40, y), m, font(dil, "kalin", 52), renk(p["metin"]), a, anchor="lm")

def c_soru(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]; a = ease(seg(ts, 0.1, 0.5))
    f = font(dil, "agir", 72); sat = satirla(s["metin"], f, 860)
    for i, sa in enumerate(sat): yazi(dr, (W / 2, 620 + i * 90), sa, f, renk(p["metin"]), ease(seg(ts, 0.1 + i * 0.15, 0.5 + i * 0.15)))
    sec = s.get("secenekler", []); y = 640 + len(sat) * 90 + 60
    for i, o in enumerate(sec):
        b = ease(seg(ts, 0.7 + i * 0.25, 1.0 + i * 0.25)); x = W / 2 + (i - (len(sec) - 1) / 2) * 340
        dr.rounded_rectangle((x - 140, y - 55, x + 140, y + 55), 28, outline=renk(p["vurgu"], int(255 * b)), width=4, fill=renk(p["zemin1"], int(150 * b)))
        yazi(dr, (x, y), o, font(dil, "agir", 58), renk(p["vurgu"]), b, golge=False)
    yazi(dr, (W / 2, 1180), "NØVEX", font("modern", "agir", 64), renk(p["metin"]), ease(seg(ts, 1.4, 2.0)))

CIZ = {"baslik": c_baslik, "sayi": c_sayi, "harita": c_harita, "zaman": c_zaman, "karsilastir": c_karsilastir,
       "alinti": c_alinti, "liste": c_liste, "soru": c_soru}

# ---------- zamanlama ----------
def sahne_araliklari(plan, z):
    bas = {c["i"]: c["bas"] for c in z}; son_t = z[-1]["son"] + plan.get("kapanis_sn", 2.0)
    s = sorted(plan["sahneler"], key=lambda x: x["cumle"]); out = []
    for i, sc in enumerate(s):
        a = 0.0 if i == 0 else bas[sc["cumle"]] - 0.25
        b = (bas[s[i + 1]["cumle"]] - 0.25) if i + 1 < len(s) else son_t
        out.append((a, b, sc))
    return out, son_t

def srt_oku(yol):
    if not yol: return []
    out = []
    for b in re.split(r"\n\s*\n", open(yol, encoding="utf-8").read().strip()):
        l = b.strip().splitlines()
        def sn(x): h, m, s_ = x.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s_)
        a, c = l[1].split(" --> "); out.append((sn(a), sn(c), " ".join(l[2:])))
    return out

GECIS = 0.3
def tek_sahne(plan, sc, t, a, b):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(L)
    CIZ[sc["tur"]](L, dr, plan, sc, cl((t - a) / (b - a)), t - a)
    arr = np.asarray(L).astype(np.float32)
    # kamera: yavaş itme / kaydırma (sahne başına yön değişir)
    k = plan.get("kamera", "itme"); u = cl((t - a) / max(b - a, 1e-6))
    if k != "sabit":
        sc_ = 1.0 + (0.05 * u if k == "itme" else 0.03); dx = (18 * (u - 0.5) * (1 if hash(sc["tur"]) % 2 else -1)) if k == "kaydirma" else 0
        M = np.float32([[sc_, 0, (1 - sc_) * W / 2 + dx], [0, sc_, (1 - sc_) * H * 0.45]])
        arr = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR)
    return arr

def kare(plan, z, caps, t, ara=None, kapak=False):
    ara = ara or sahne_araliklari(plan, z)[0]
    img = zemin(plan).copy()
    idx = next((i for i, (a, b, _) in enumerate(ara) if t < b), len(ara) - 1)
    a, b, sc = ara[idx]; lay = tek_sahne(plan, sc, t, a, b)
    if idx + 1 < len(ara) and t > b - GECIS:
        w = ease((t - (b - GECIS)) / (2 * GECIS)); a2, b2, sc2 = ara[idx + 1]; lay = lay * (1 - w) + tek_sahne(plan, sc2, t, a2, b2) * w
    elif idx > 0 and t < a + GECIS:
        w = ease((t - (a - GECIS)) / (2 * GECIS)); a0, b0, sc0 = ara[idx - 1]; lay = tek_sahne(plan, sc0, t, a0, b0) * (1 - w) + lay * w
    al = lay[..., 3:4] / 255.0; img = img * (1 - al) + lay[..., :3] * al
    # altyazı: alt bant (y 1250–1480), güvenli alan içinde
    if caps and not kapak:
        S = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(S); f = font(plan["dil"] if plan["dil"] != "daktilo" else "modern", "kalin", 50)
        for c0, c1, m in caps:
            if c0 - 0.05 <= t < c1 + 0.12:
                aa = ease(seg(t, c0 - 0.05, c0 + 0.12)) * (1 - seg(t, c1, c1 + 0.12))
                for i, sa in enumerate(satirla(m, f, 780)):
                    yazi(d, (W / 2, 1300 + i * 64), sa, f, (255, 255, 255, 255), aa)
        s_ = np.asarray(S).astype(np.float32); sal = s_[..., 3:4] / 255
        yy = np.arange(H, dtype=np.float32)[:, None, None]; scr = np.exp(-((yy - 1340) / 200) ** 2) * 0.45
        img = img * (1 - scr); img = img * (1 - sal) + s_[..., :3] * sal
    if t < 2.4 and not kapak:
        T = Image.new("RGBA", (W, H), (0, 0, 0, 0)); yazi(ImageDraw.Draw(T), (W / 2, 175), "NØVEX", font("modern", "orta", 30), renk(plan["palet"]["metin"]), ease(seg(t, 0.1, 0.4)) * (1 - seg(t, 2.0, 2.4)), golge=False)
        tt = np.asarray(T).astype(np.float32); img = img * (1 - tt[..., 3:4] / 255) + tt[..., :3] * tt[..., 3:4] / 255
    img = gren(img, t, plan)
    son = ara[-1][1]
    if not kapak: img *= (1 - ease(seg(t, son - 0.6, son))) * ease(seg(t, 0.0, 0.35)) if t < 0.35 else (1 - ease(seg(t, son - 0.6, son)))
    return np.clip(img, 0, 255).astype(np.uint8)

def kapak_ciz(plan, z, out):
    ara, _ = sahne_araliklari(plan, z); k = plan.get("kapak", {})
    i = k.get("zemin_sahne", 0); a, b, sc = ara[i]
    img = kare(plan, z, [], a + min(2.5, (b - a) * 0.8), ara, kapak=True).astype(np.float32) * 0.55
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); p = plan["palet"]
    if k.get("ust"): yazi(d, (W / 2, 520), k["ust"].upper(), font(plan["dil"], "kalin", 64), renk(p["vurgu"]), 1)
    f = font(plan["dil"], "agir", 150)
    for j, sa in enumerate(satirla(k.get("ana", ""), f, 900)): yazi(d, (W / 2, 700 + j * 165), sa, f, renk(p["metin"]), 1)
    yazi(d, (W / 2, 1420), "NØVEX", font("modern", "agir", 56), renk(p["metin"]), 0.9)
    l = np.asarray(L).astype(np.float32); img = img * (1 - l[..., 3:4] / 255) + l[..., :3] * l[..., 3:4] / 255
    cv2.imwrite(out, cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mod"); ap.add_argument("plan"); ap.add_argument("zaman"); ap.add_argument("args", nargs="*")
    ap.add_argument("--srt"); ap.add_argument("--bas", type=float, default=0.0); ap.add_argument("--son", type=float); ap.add_argument("--kapak", action="store_true")
    a = ap.parse_args(); plan = json.load(open(a.plan, encoding="utf-8")); z = json.load(open(a.zaman, encoding="utf-8"))
    caps = srt_oku(a.srt); ara, toplam = sahne_araliklari(plan, z)
    if a.mod == "kapak": kapak_ciz(plan, z, a.args[0]); return
    if a.mod == "kare":
        cv2.imwrite(a.args[1], cv2.cvtColor(kare(plan, z, caps, float(a.args[0]), ara), cv2.COLOR_RGB2BGR)); return
    out = a.args[0]; f0 = round(a.bas * FPS); f1 = round((a.son if a.son is not None else toplam) * FPS); tmp = out[:-4] + ".part.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                           "-color_trc", "bt709", "-color_range", "tv", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-r", str(FPS), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        pr.stdin.write(kare(plan, z, caps, fi / FPS, ara).tobytes())
        if (fi - f0) % 90 == 0: print("kare", fi, "/", f1, flush=True)
    pr.stdin.close(); rc = pr.wait()
    if rc == 0: os.replace(tmp, out)
    sys.exit(rc)

if __name__ == "__main__":
    main()
