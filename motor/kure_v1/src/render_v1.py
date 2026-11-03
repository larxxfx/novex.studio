"""NØVEX — Türkiye Antarktika'da olsaydı. 3B ışın-küre render motoru + sahne zaman çizelgesi.
Kullanım:
  python3 render.py frame 4.5 out.jpg        # tek kare
  python3 render.py scene s2 out.mp4          # bir sahneyi kodla
"""
import json, math, os, sys, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "build")
W, H, FPS = 1080, 1920, 30
SCENES = {"s1": (0.0, 3.0), "s2": (3.0, 8.0), "s3": (8.0, 14.0), "s4": (14.0, 20.0), "s5": (20.0, 26.0), "s6": (26.0, 30.0)}

# ---------------- veriler ----------------
GEO = json.load(open(os.path.join(B, "geo.json"), encoding="utf-8"))
def _load(name):
    im = cv2.imread(os.path.join(B, name), cv2.IMREAD_COLOR)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
POLAR = [_load("polar_tex.png")]
while POLAR[-1].shape[0] > 400: POLAR.append(cv2.pyrDown(POLAR[-1]))
WORLD = [_load("world_tex.jpg")]
while WORLD[-1].shape[0] > 400: WORLD.append(cv2.pyrDown(WORLD[-1]))
SKY = _load("sky_tex.png")
RDEG = GEO["polar"]["RDEG"]
POLAR_KM = 6371 * math.radians(1) / (POLAR[0].shape[0] / 2 / RDEG)
WORLD_KM = 6371 * math.radians(360 / WORLD[0].shape[1])

FONTS = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FONTS + name, size)
    return _fc[k]

ELECTRIC = np.array([0.20, 0.62, 1.00], np.float32)
RED = np.array([1.00, 0.24, 0.24], np.float32)
GOLD = np.array([1.00, 0.78, 0.35], np.float32)

# ---------------- matematik ----------------
def xyz(lon, lat, r=1.0):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1) * np.asarray(r)[..., None] if np.ndim(r) else \
        np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1) * r

def norm(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def lerp(a, b, t): return a + (b - a) * t
def clamp01(x): return max(0.0, min(1.0, x))
def ease(t): t = clamp01(t); return t * t * (3 - 2 * t)
def ease_io3(t): t = clamp01(t); return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def ease_out(t): t = clamp01(t); return 1 - (1 - t) ** 3
def seg(t, a, b): return clamp01((t - a) / (b - a))
def slerp(a, b, t):
    a, b = norm(np.asarray(a, float)), norm(np.asarray(b, float))
    om = math.acos(max(-1, min(1, float(np.dot(a, b)))))
    if om < 1e-6: return a
    return (math.sin((1 - t) * om) * a + math.sin(t * om) * b) / math.sin(om)

U0 = np.array([1.0, 0.0, 0.0])
def local_north(lon, lat):
    lo, la = math.radians(lon), math.radians(lat)
    return np.array([-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)])

class Cam:
    def __init__(self, target, up_t, D, P, head=0.0, fov=40.0, w=W, h=H):
        n = norm(np.asarray(target, float)); up_t = norm(up_t - np.dot(up_t, n) * n)
        hr = math.radians(head); e = np.cross(up_t, n)
        up_t = up_t * math.cos(hr) + e * math.sin(hr)
        p = math.radians(P)
        self.T = n
        self.C = n + D * (math.cos(p) * n - math.sin(p) * up_t)
        self.f = norm(n - self.C)
        uh = norm(up_t * math.cos(p) + n * math.sin(p))
        self.r = norm(np.cross(self.f, uh)); self.u = np.cross(self.r, self.f)
        self.w, self.h = w, h
        self.F = (h / 2) / math.tan(math.radians(fov) / 2)

    def project(self, P):
        P = np.asarray(P, float); v = P - self.C
        z = v @ self.f
        x = (v @ self.r) / np.maximum(z, 1e-6) * self.F + self.w / 2
        y = -(v @ self.u) / np.maximum(z, 1e-6) * self.F + self.h / 2
        Pn = P / np.linalg.norm(P, axis=-1, keepdims=True)
        vis = (z > 1e-4) & (np.sum(Pn * v, -1) < 0)
        return np.stack([x, y], -1), vis

# ekran ışınları (boyut başına önbellek)
_rays = {}
def screen_grid(w, h):
    if (w, h) not in _rays:
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        _rays[(w, h)] = (xs - w / 2 + 0.5, -(ys - h / 2 + 0.5))
    return _rays[(w, h)]

# ---------------- küre render ----------------
def render_globe(cam, sun_dir, sun_int=1.0, night=0.0, t=0.0, fog=0.0, aurora=0.0, star_gain=1.0):
    w, h = cam.w, cam.h
    sx, sy = screen_grid(w, h)
    d = (cam.f[None, None, :].astype(np.float32) + (sx / cam.F)[..., None] * cam.r.astype(np.float32)
         + (sy / cam.F)[..., None] * cam.u.astype(np.float32))
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    C = cam.C.astype(np.float32)
    b = d @ C; c = float(C @ C) - 1.0
    disc = b * b - c
    hit = disc > 0
    tt = np.where(hit, -b - np.sqrt(np.maximum(disc, 0)), 0).astype(np.float32)
    hit &= tt > 0
    p = C + d * tt[..., None]
    lon = np.degrees(np.arctan2(p[..., 1], p[..., 0])); lat = np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1)))
    # mip seviyesi: merkez piksel ayak izi
    tc = float(tt[h // 2, w // 2]) if hit[h // 2, w // 2] else float(np.linalg.norm(C))
    foot_km = tc / cam.F * 6371 * 1.15
    out = np.zeros((h, w, 3), np.float32)
    # dünya dokusu
    lw = int(np.clip(math.floor(math.log2(max(foot_km / WORLD_KM, 1e-3))), 0, len(WORLD) - 1))
    tw = WORLD[lw]; Hw, Ww = tw.shape[:2]
    mx = ((lon + 180) / 360 * Ww - 0.5).astype(np.float32); my = ((90 - lat) / 180 * Hw - 0.5).astype(np.float32)
    col = cv2.remap(tw, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP).astype(np.float32) / 255
    # kutup dokusu
    pm = lat < -56.5
    if pm.any():
        lp = int(np.clip(math.floor(math.log2(max(foot_km / POLAR_KM, 1e-3))), 0, len(POLAR) - 1))
        tp = POLAR[lp]; Np = tp.shape[0]; ppd = Np / 2 / RDEG
        rho = (90 + lat) * ppd; lr = np.radians(lon)
        px = (Np / 2 + rho * np.sin(lr) - 0.5).astype(np.float32); py = (Np / 2 - rho * np.cos(lr) - 0.5).astype(np.float32)
        pc = cv2.remap(tp, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32) / 255
        wpol = np.clip((-56.5 - lat) / 2.5, 0, 1)[..., None]
        col = col * (1 - wpol) + pc * wpol
    # aydınlatma
    n = p
    ndl = n @ np.asarray(sun_dir, np.float32)
    diff = np.clip(ndl * 1.9 + 0.30, 0, 1.15)
    amb = np.array([0.20, 0.27, 0.42], np.float32) * (1 - 0.55 * night) + np.array([0.02, 0.04, 0.10], np.float32) * night
    sunc = np.array([1.02, 0.98, 0.93], np.float32) * sun_int
    lit = col * (amb + sunc * diff[..., None]) * 0.74
    mu = np.clip(-(d * n).sum(-1), 0, 1)
    rim = (1 - mu) ** 3
    atm = np.array([0.30, 0.55, 1.0], np.float32)
    lit = lit + atm * (rim * (0.55 * (1 - night) + 0.12) * np.clip(diff + 0.25, 0, 1))[..., None]
    if fog > 0:
        fz = 1 - np.exp(-tt * fog)
        fogc = np.array([0.62, 0.74, 0.90], np.float32) * (1 - night) * sun_int + np.array([0.03, 0.05, 0.11], np.float32) * night
        lit = lit * (1 - fz[..., None]) + fogc * fz[..., None]
    out[hit] = lit[hit]
    # gökyüzü: yıldız + atmosfer halesi + aurora
    sky = ~hit
    if sky.any():
        slon = np.degrees(np.arctan2(d[..., 1], d[..., 0])); slat = np.degrees(np.arcsin(np.clip(d[..., 2], -1, 1)))
        Hs, Ws = SKY.shape[:2]
        st = cv2.remap(SKY, ((slon + 180) / 360 * Ws).astype(np.float32), ((90 - slat) / 180 * Hs).astype(np.float32),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP).astype(np.float32) / 255
        bmin = np.where(b < 0, np.sqrt(np.maximum(c + 1 - b * b, 0)), math.sqrt(c + 1))
        alt = bmin - 1.0
        halo = np.exp(-np.maximum(alt, 0) / 0.016) * (bmin >= 1)
        sk = st * star_gain + atm * (halo * (0.85 * (1 - night) + 0.25))[..., None]
        if aurora > 0:
            az = np.arctan2(d @ cam.r.astype(np.float32), d @ cam.f.astype(np.float32))
            curtain = 0.5 + 0.5 * np.sin(az * 9 + t * 0.9 + 2.0 * np.sin(az * 3.1 - t * 0.4))
            curtain *= 0.5 + 0.5 * np.sin(az * 23 - t * 1.7)
            band = np.exp(-((alt - 0.030) / 0.013) ** 2) * (alt > 0.002)
            ac = np.array([0.18, 0.95, 0.85], np.float32) * 0.55 + np.array([0.25, 0.45, 1.0], np.float32) * 0.45
            sk = sk + ac * (aurora * band * curtain * 0.75)[..., None]
        out[sky] = sk[sky]
    return out, hit, tt

# ---------------- çizim yardımcıları ----------------
def to_pts(xy):
    return np.round(xy * 16).astype(np.int32).reshape(-1, 1, 2)

def polyline_layers(cam, lonlat_list, closed=False, lift=1.0):
    """lon/lat çoklu çizgileri ekrana; görünmeyen parçaları böler."""
    out = []
    for ll in lonlat_list:
        ll = np.asarray(ll, float)
        P = xyz(ll[:, 0], ll[:, 1]) * lift
        xy, vis = cam.project(P)
        if closed: xy = np.vstack([xy, xy[:1]]); vis = np.append(vis, vis[0])
        start = None
        for i in range(len(vis) + 1):
            v = vis[i] if i < len(vis) else False
            if v and start is None: start = i
            if not v and start is not None:
                if i - start >= 2: out.append(xy[start:i])
                start = None
    return out

def partial(path, frac):
    """kümülatif uzunluğa göre çizginin ilk frac kısmı"""
    if frac >= 1: return path
    dl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    L = dl[-1] * frac
    k = int(np.searchsorted(dl, L))
    if k <= 0: return path[:1]
    a = (L - dl[k - 1]) / max(dl[k] - dl[k - 1], 1e-9)
    return np.vstack([path[:k], path[k - 1] + (path[k] - path[k - 1]) * a])

def glow_lines(img, paths, color, width, glow, alpha=1.0, under=True):
    if not paths or alpha <= 0: return
    h, w = img.shape[:2]
    if under and width >= 2:
        dk = np.zeros((h, w), np.float32)
        for pth in paths:
            if len(pth) >= 2: cv2.polylines(dk, [to_pts(pth)], False, 1.0, int(round(width)) + 7, cv2.LINE_AA, 4)
        dk = cv2.GaussianBlur(dk, (0, 0), 3) * 0.55 * alpha
        img[:] = img * (1 - dk[..., None]) + np.array([0.01, 0.03, 0.09], np.float32) * dk[..., None]
    lay = np.zeros((h, w), np.float32)
    for pth in paths:
        if len(pth) >= 2: cv2.polylines(lay, [to_pts(pth)], False, 1.0, max(1, int(round(width))), cv2.LINE_AA, 4)
    if glow > 0:
        s = cv2.resize(lay, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        g = cv2.resize(cv2.GaussianBlur(s, (0, 0), glow / 4), (w, h), interpolation=cv2.INTER_LINEAR)
        img += (color * 0.9)[None, None, :] * (g * 2.2 * alpha)[..., None]
    a = np.clip(lay * alpha, 0, 1)[..., None]
    img[:] = img * (1 - a) + (color * 0.35 + 0.65)[None, None, :] * a if width < 4 else img * (1 - a) + color[None, None, :] * a

def fill_poly(img, paths, color, alpha):
    if alpha <= 0: return
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.float32)
    cv2.fillPoly(m, [to_pts(p) for p in paths if len(p) >= 3], 1.0, cv2.LINE_AA, 4)
    a = (m * alpha)[..., None]
    img[:] = img * (1 - a) + color[None, None, :] * a

def dot(img, xy, r, color, glow=18, alpha=1.0):
    h, w = img.shape[:2]
    lay = np.zeros((h, w), np.float32)
    cv2.circle(lay, (int(xy[0] * 16), int(xy[1] * 16)), int(r * 16), 1.0, -1, cv2.LINE_AA, 4)
    g = cv2.GaussianBlur(lay, (0, 0), glow)
    img += color[None, None, :] * (g * 3.0 * alpha)[..., None]
    a = (lay * alpha)[..., None]; img[:] = img * (1 - a) + (color * 0.3 + 0.7) * a

def ring(img, xy, r, color, th=3, alpha=1.0):
    if alpha <= 0 or r <= 0: return
    h, w = img.shape[:2]
    lay = np.zeros((h, w), np.float32)
    cv2.circle(lay, (int(xy[0] * 16), int(xy[1] * 16)), int(r * 16), 1.0, max(1, int(th)), cv2.LINE_AA, 4)
    a = (lay * alpha)[..., None]; img[:] = img * (1 - a) + color * a

def great_circle(a_ll, b_ll, n=120, arc=0.0):
    A, Bv = xyz(*a_ll), xyz(*b_ll)
    pts = []
    for s in np.linspace(0, 1, n):
        v = slerp(A, Bv, s); pts.append(v * (1 + arc * math.sin(math.pi * s)))
    return np.array(pts)

def path3d(cam, P):
    xy, vis = cam.project(P)
    return [xy[vis]] if vis.sum() >= 2 else []

# ---------------- metin katmanı ----------------
class Text:
    def __init__(self):
        self.im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
        self.used = False
    def text(self, xy, s, f, fill=(255, 255, 255), a=1.0, anchor="mm", shadow=True, spacing=0):
        if a <= 0.01: return
        self.used = True
        al = int(255 * clamp01(a))
        if shadow:
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
            sd.text((xy[0], xy[1] + 4), s, font=f, fill=(0, 4, 14, int(al * 0.85)), anchor=anchor)
            from PIL import ImageFilter
            sh = sh.filter(ImageFilter.GaussianBlur(9))
            self.im.alpha_composite(sh)
        self.d.text(xy, s, font=f, fill=tuple(fill) + (al,), anchor=anchor)
    def rrect(self, box, r, fill, a=1.0, outline=None, width=2):
        if a <= 0.01: return
        self.used = True
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle(box, r, fill=tuple(fill[:3]) + (int(fill[3] * a),),
                             outline=(tuple(outline[:3]) + (int(outline[3] * a),)) if outline else None, width=width)
        self.im.alpha_composite(ov)
    def cross(self, c, r, fill, a=1.0, width=9):
        if a <= 0.01: return
        self.used = True
        col = tuple(fill) + (int(255 * clamp01(a)),); x, y = c
        self.d.line((x - r, y - r, x + r, y + r), fill=col, width=width)
        self.d.line((x - r, y + r, x + r, y - r), fill=col, width=width)
    def composite(self, img):
        if not self.used: return img
        arr = np.asarray(self.im).astype(np.float32) / 255
        a = arr[..., 3:4]
        return img * (1 - a) + arr[..., :3] * a

def to_rgb255(c): return tuple(int(round(v * 255)) for v in c)

# Altyazılar: (başla, bitir, satırlar, vurgulu kelimeler)
CAPS = [
    (0.10, 2.95, ["Türkiye'yi alıp", "dünyanın en soğuk", "kıtasına bıraktık."], {"en", "soğuk"}),
    (3.00, 5.30, ["Ankara, tam", "Güney Kutbu'nda."], {"Güney", "Kutbu'nda."}),
    (5.30, 7.95, ["İstanbul da, Van da", "buzun üstünde."], {"buzun"}),
    (8.00, 10.80, ["Kutupta yıllık ortalama", "eksi 50 derece."], {"eksi", "50"}),
    (10.80, 13.95, ["Güneş, altı ay", "boyunca hiç doğmaz."], {"altı", "ay"}),
    (14.00, 16.20, ["Açık havada", "tarım olmazdı."], {"tarım"}),
    (16.20, 19.95, ["Yakıt da ekmek de uçakla", "ya da haftalar süren", "konvoylarla gelirdi."], {"uçakla", "konvoylarla"}),
    (20.00, 23.00, ["Asıl şok: üç tarafı deniz olan", "Türkiye'nin tek bir", "kıyısı kalmazdı."], {"kıyısı", "kalmazdı."}),
    (23.00, 25.95, ["Ankara'dan en yakın denize", "1.200 kilometreden fazla."], {"1.200", "kilometreden"}),
    (26.00, 28.40, ["Bir ülkenin kaderini yalnızca", "insanlar değil,", "coğrafya da yazar."], {"coğrafya"}),
    (28.40, 30.00, ["Sen bu ülkede", "ilk neyi kurardın?"], {"neyi", "kurardın?"}),
]
WARN = {"kalmazdı.", "kıyısı"}

def captions(tx, t):
    for (a, b, lines, hl) in CAPS:
        if not (a - 0.01 <= t < b + 0.12): continue
        words = [w for l in lines for w in l.split()]
        nw = len(words); rev = a + (b - a) * 0.62
        fin = 1 - seg(t, b - 0.02, b + 0.12) if b < 29.9 else 1.0
        f = font("Inter-Black.otf", 68)
        sp = f.getlength(" ")
        y0 = 1300 - (len(lines) - 1) * 44
        k = 0
        for li, line in enumerate(lines):
            ws = line.split(); widths = [f.getlength(w) for w in ws]
            tot = sum(widths) + sp * (len(ws) - 1); x = W / 2 - tot / 2; y = y0 + li * 88
            for w, ww in zip(ws, widths):
                tw = a + (rev - a) * (k / max(1, nw - 1)) - 0.05
                ap = ease_out(seg(t, tw, tw + 0.16)) * fin
                dy = (1 - ease_out(seg(t, tw, tw + 0.2))) * 16
                colr = (255, 255, 255)
                if w in hl: colr = to_rgb255(RED * 0.9 + 0.1) if (w in WARN and a >= 20) else to_rgb255(ELECTRIC * 0.85 + 0.15)
                tx.text((x, y + dy), w, f, colr, ap, anchor="ls")
                x += ww + sp; k += 1

# ---------------- sahne verileri ----------------
TM = GEO["turkey_moved"]
TM_OUTER = [np.array(p[0]) for p in TM]
TM_MAIN = max(TM_OUTER, key=len)
CITIES = GEO["cities"]
_cent = norm(np.mean(np.concatenate([xyz(p[:, 0], p[:, 1]) for p in TM_OUTER]), 0))
POLE = np.array([0, 0, -1.0])
TR_CENTER = _cent
COAST = (GEO["nearest_coast"]["lon"], GEO["nearest_coast"]["lat"])
MCMURDO = (166.67, -77.85)
CONVOY = [(166.67, -77.85), (172.0, -79.6), (-178.0, -81.6), (-165.0, -83.6), (-150.0, -85.3), (-147.0, -86.6), (-120.0, -88.4), (0, -90)]
REAL_TR = np.array(GEO["turkey_real_main"]); REAL_FLAG = np.array(GEO["turkey_real_coastflag"])

def densify(ll, step=0.4):
    out = []
    for a, b in zip(ll[:-1], ll[1:]):
        A, Bv = xyz(*a), xyz(*b); n = max(2, int(math.degrees(math.acos(np.clip(A @ Bv, -1, 1))) / step))
        for s in np.linspace(0, 1, n, endpoint=False): out.append(slerp(A, Bv, s))
    out.append(xyz(*ll[-1])); return np.array(out)
CONVOY3 = densify(CONVOY)

def make_cracks(seed=3):
    rng = np.random.default_rng(seed); cracks = []
    def walk(lon, lat, ang, n, depth):
        pts = [(lon, lat)]; v = xyz(lon, lat)
        for i in range(n):
            ang += rng.normal(0, 0.35)
            nn = local_north(*pts[-1]) if pts[-1][1] > -89.99 else U0
            e = np.cross(nn, norm(v)); stepv = (nn * math.cos(ang) + e * math.sin(ang)) * 0.0028
            v = norm(v + stepv); pts.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(v[2]))))
            if depth < 2 and rng.random() < 0.07: walk(*pts[-1], ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.1), n // 2, depth + 1)
        cracks.append(np.array(pts))
    a_lon, a_lat = CITIES["Ankara"]["moved"]
    for k in range(7):
        walk(a_lon, a_lat + 0.02, k / 7 * 2 * math.pi + rng.normal(0, 0.2), 90, 0)
    return cracks
CRACKS = make_cracks()

rng_p = np.random.default_rng(11)
NP = 1300
PART = {"x": rng_p.random(NP) * 1.4 - 0.2, "y": rng_p.random(NP), "z": rng_p.random(NP) ** 1.6, "ph": rng_p.random(NP)}
GRAIN = [np.random.default_rng(i).normal(0, 1, (H // 2, W // 2)).astype(np.float32) for i in range(6)]
VIG = None
SCRIM = None

def blizzard(img, t, inten, night):
    if inten <= 0: return
    lay = np.zeros((H, W), np.float32); big = np.zeros((H // 2, W // 2), np.float32)
    vx, vy = -1.9, 1.05
    for i in range(NP):
        z = PART["z"][i]; spd = 0.25 + 1.6 * z
        x = ((PART["x"][i] + vx * spd * t * 0.18) % 1.4 - 0.2) * W
        y = ((PART["y"][i] + vy * spd * t * 0.18 + PART["ph"][i]) % 1.0) * H
        L = 6 + 46 * z
        if z > 0.82:
            cv2.circle(big, (int(x / 2), int(y / 2)), int(2 + 5 * z), 0.35, -1, cv2.LINE_AA)
        else:
            cv2.line(lay, (int(x * 4), int(y * 4)), (int((x - vx * L) * 4), int((y - vy * L * 0.55) * 4)),
                     0.25 + 0.6 * z, 1 + int(z * 2.4), cv2.LINE_AA, 2)
    big = cv2.resize(cv2.GaussianBlur(big, (0, 0), 3), (W, H))
    a = np.clip((lay + big) * inten, 0, 1)[..., None]
    col = np.array([0.92, 0.95, 1.0], np.float32) * (1 - 0.55 * night) + np.array([0.35, 0.45, 0.65], np.float32) * 0.55 * night
    img[:] = img * (1 - a * 0.85) + col * a * 0.85
    # rüzgârla taşınan yüzey karı (sis tabakası)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    haze = np.clip((yy - 0.25) / 0.75, 0, 1) * 0.22 * inten
    img[:] = img * (1 - haze[..., None]) + col * haze[..., None]

def post(img, t, mblur_prev=None, k=0.0):
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2
        VIG = np.clip(1 - 0.42 * r2, 0.35, 1)[..., None]
    br = np.maximum(img - 0.78, 0)
    s = cv2.resize(br, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(s, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR)
    img = img + bl * 0.55
    img = img * VIG
    img = img * 0.95 + np.array([0.004, 0.012, 0.032], np.float32)
    img = img / (1 + np.maximum(img - 0.85, 0) * 0.9)        # yumuşak tepe sıkıştırma
    g = cv2.resize(GRAIN[int(t * FPS) % len(GRAIN)], (W, H), interpolation=cv2.INTER_NEAREST)
    img = img + g[..., None] * 0.012
    if mblur_prev is not None and k > 0: img = img * (1 - k) + mblur_prev * k
    return np.clip(img, 0, 1)

def sun_vec(az_deg, elev):
    a = math.radians(az_deg); return norm(np.array([math.cos(a), math.sin(a), -elev]))

# ---------------- zaman çizelgesi ----------------
def frame(t, prev=None):
    tx = Text(); mb = 0.0
    a_ll = CITIES["Ankara"]["moved"]; A3 = xyz(*a_ll)
    if t < 3.0:                                         # S1 KANCA: uzaydan dalış
        s = ease_io3(t / 3.0)
        lat = lerp(-18, -90, s); lon = lerp(48, 0, s)
        target = xyz(lon, lat); up = local_north(lon, lat) if lat > -89.999 else U0
        D = math.exp(lerp(math.log(5.6), math.log(1.30), ease_io3(seg(t, 0.15, 3.0))))
        cam = Cam(target, up, D, P=lerp(8, 0, s), head=lerp(-18, 0, s))
        img, hit, tt = render_globe(cam, sun_vec(30, 0.45), 1.0, 0, t)
        f = ease_io3(seg(t, 1.55, 2.85))
        if f > 0:
            paths = polyline_layers(cam, TM_OUTER, closed=True)
            fill_poly(img, paths, ELECTRIC * 0.55, 0.30 * ease(seg(t, 2.3, 2.95)))
            glow_lines(img, [partial(p, f) for p in paths], ELECTRIC, 3, 26, 1.0)
        mb = 0.35 * (1 - seg(t, 2.4, 3.0))
        tx.text((W / 2, 250), "NØVEX · DÜŞÜNCE DENEYİ", font("InterDisplay-SemiBold.otf", 30), (150, 190, 255), ease(seg(t, 0.2, 0.6)) * (1 - seg(t, 2.6, 2.95)), shadow=False)
    elif t < 8.0:                                       # S2 İLK ŞOK
        lt = t - 3.0; s = ease_io3(lt / 5.0)
        target = slerp(POLE, TR_CENTER, 0.55 * ease(seg(lt, 0, 2.5)))
        cam = Cam(target, U0, lerp(1.30, 0.80, ease_io3(seg(lt, 0, 3.0))), P=lerp(0, 50, ease_io3(seg(lt, 0, 3.2))), head=lerp(0, 16, s))
        img, hit, tt = render_globe(cam, sun_vec(30, 0.45), 1.0, 0, t, fog=0.15)
        paths = polyline_layers(cam, TM_OUTER, closed=True)
        fill_poly(img, paths, ELECTRIC * 0.55, 0.30)
        glow_lines(img, paths, ELECTRIC, 3, 26, 1.0)
        # kutup / Ankara
        xyA, visA = cam.project(A3[None])
        if visA[0]:
            pa = ease_out(seg(lt, 0.2, 0.6))
            dot(img, xyA[0], 9 * pa, RED, 14, pa)
            ring(img, xyA[0], 18 + 60 * ((lt * 0.8) % 1), RED, 3, 0.8 * (1 - (lt * 0.8) % 1) * pa)
            tx.text((xyA[0][0], xyA[0][1] - 52), "ANKARA", font("InterDisplay-Bold.otf", 40), (255, 255, 255), pa)
            bx, by = xyA[0][0], xyA[0][1] + 56
            tx.rrect((bx - 150, by - 22, bx + 150, by + 22), 14, (40, 6, 10, 215), pa, (255, 90, 90, 230), 2)
            tx.text((bx, by), "GÜNEY KUTBU · 90°G", font("InterDisplay-Bold.otf", 26), (255, 215, 215), pa, shadow=False)
        for nm, t0 in (("İstanbul", 2.35), ("Van", 2.75), ("İzmir", 3.1), ("Antalya", 3.4), ("Trabzon", 3.7)):
            xy, vis = cam.project(xyz(*CITIES[nm]["moved"])[None])
            if vis[0]:
                pa = ease_out(seg(lt, t0, t0 + 0.3))
                dot(img, xy[0], 6 * pa, ELECTRIC, 10, pa)
                tx.text((xy[0][0], xy[0][1] - 34), nm.upper() if nm != "İzmir" else "İZMİR", font("InterDisplay-Bold.otf", 30), (235, 244, 255), pa)
        qa = ease_out(seg(lt, 3.6, 3.95))
        tx.rrect((150, 300, 930, 420), 22, (6, 14, 34, 200), qa, (60, 150, 255, 230), 3)
        tx.text((W / 2, 361), "Hâlâ aynı ülke mi?", font("InterDisplay-Bold.otf", 54), (255, 255, 255), qa, shadow=False)
    elif t < 14.0:                                      # S3 İKLİM: kutup gecesi + fırtına
        lt = t - 8.0
        night = ease(seg(lt, 1.6, 4.2))
        target = slerp(POLE, TR_CENTER, 0.15)
        cam = Cam(target, U0, lerp(0.36, 0.27, ease_io3(lt / 6)), P=lerp(70, 77, ease(lt / 6)), head=lerp(196, 214, lt / 6))
        sun = sun_vec(lerp(210, 250, lt / 6), lerp(0.30, -0.05, ease(seg(lt, 0.8, 4.2))))
        img, hit, tt = render_globe(cam, sun, lerp(1.0, 0.10, night), night, t, fog=lerp(0.8, 1.6, night),
                                    aurora=ease(seg(lt, 3.2, 5.0)), star_gain=1.0 + 1.5 * night)
        paths = polyline_layers(cam, TM_OUTER, closed=True)
        glow_lines(img, paths, ELECTRIC, 3, 22, 0.85)
        cf = ease(seg(lt, 3.4, 6.0))
        if cf > 0:
            cp = []
            for c in CRACKS:
                for p in polyline_layers(cam, [c]): cp.append(partial(p, cf))
            glow_lines(img, cp, np.array([0.35, 0.75, 1.0], np.float32), 2, 10, 0.9)
        blizzard(img, t, 0.55 + 0.45 * math.sin(math.pi * seg(lt, 0, 6)), night)
        # sıcaklık
        ta = ease_out(seg(lt, 0.2, 0.6)) * (1 - seg(lt, 5.75, 6.0))
        tv = lerp(-20, -50, ease_io3(seg(lt, 0.3, 2.2)))
        tx.text((W / 2, 400), f"−{abs(round(tv))}°C", font("InterDisplay-Black.otf", 190), (255, 255, 255), ta)
        tx.text((W / 2, 520), "YILLIK ORTALAMA · GÜNEY KUTBU", font("InterDisplay-SemiBold.otf", 30), (170, 205, 255), ta)
        ra = ease_out(seg(lt, 1.6, 2.0)) * (1 - seg(lt, 5.75, 6.0))
        tx.rrect((170, 580, 910, 650), 18, (60, 10, 14, 170), ra, (255, 70, 70, 220), 2)
        tx.text((W / 2, 615), "En düşük ölçüm: −89,2°C · Vostok, 1983", font("Inter-SemiBold.otf", 30), (255, 225, 225), ra, shadow=False)
        na = ease_out(seg(lt, 2.9, 3.3)) * (1 - seg(lt, 5.75, 6.0))
        tx.text((W / 2, 720), "KUTUP GECESİ ≈ 6 AY", font("InterDisplay-Bold.otf", 36), (200, 225, 255), na)
    elif t < 20.0:                                      # S4 EKONOMİ / İKMAL
        lt = t - 14.0
        tgt = slerp(POLE, xyz(178.0, -82.5), lerp(0.18, 0.55, ease_io3(seg(lt, 1.6, 4.0))))
        cam = Cam(tgt, U0, lerp(0.95, 1.18, ease_io3(seg(lt, 1.4, 4.2))), P=lerp(30, 24, ease(lt / 6)), head=lerp(-6, 4, lt / 6))
        img, hit, tt = render_globe(cam, sun_vec(80, 0.42), 0.85, 0.15, t, fog=0.12)
        paths = polyline_layers(cam, TM_OUTER, closed=True)
        fill_poly(img, paths, ELECTRIC * 0.5, 0.22)
        glow_lines(img, paths, ELECTRIC, 3, 22, 1.0)
        xyA, visA = cam.project(A3[None])
        if visA[0]: dot(img, xyA[0], 8, RED, 12, 1.0)
        # ✕ listesi
        for i, (lab, t0) in enumerate((("TARIM", 0.25), ("ORMAN", 0.65), ("MERA", 1.05))):
            a = ease_out(seg(lt, t0, t0 + 0.25)) * (1 - seg(lt, 2.0, 2.35)); y = 330 + i * 92
            tx.rrect((250, y - 38, 830, y + 38), 16, (6, 14, 34, 190), a, (90, 120, 170, 160), 2)
            tx.text((420, y), lab, font("InterDisplay-Bold.otf", 46), (235, 242, 255), a, shadow=False)
            sa = ease_out(seg(lt, t0 + 0.2, t0 + 0.42)) * a
            tx.cross((700, y), 20 * (0.6 + 0.4 * sa), to_rgb255(RED), sa)
        # ikmal hatları
        ra = seg(lt, 2.2, 5.3)
        if ra > 0:
            air = great_circle(MCMURDO, a_ll, 140, arc=0.045)
            ap = path3d(cam, air)
            glow_lines(img, [partial(p, ease_io3(ra)) for p in ap], GOLD, 3, 18, 1.0)
            gp = path3d(cam, CONVOY3 * 1.0004)
            gf = ease_io3(seg(lt, 2.6, 5.6))
            if gp:
                g = partial(gp[0], gf)
                dl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(g, axis=0), axis=1))]
                dash = [g[(dl >= s0) & (dl < s0 + 18)] for s0 in np.arange(0, dl[-1], 30)]
                glow_lines(img, [d for d in dash if len(d) >= 2], np.array([0.85, 0.92, 1.0], np.float32), 3, 10, 0.95)
            if ap and ease_io3(ra) < 1:
                q = partial(ap[0], ease_io3(ra))[-1]; dot(img, q, 7, GOLD, 12, 1.0)
            xyM, visM = cam.project(xyz(*MCMURDO)[None])
            if visM[0]:
                dot(img, xyM[0], 7, np.array([0.9, 0.95, 1.0], np.float32), 10, ease(seg(lt, 2.2, 2.6)))
                tx.text((xyM[0][0], xyM[0][1] + 44), "ROSS DENİZİ KIYISI", font("InterDisplay-SemiBold.otf", 26), (210, 225, 250), ease(seg(lt, 2.3, 2.7)))
            la = ease_out(seg(lt, 3.3, 3.7))
            tx.rrect((90, 300, 520, 370), 16, (40, 28, 6, 190), la, (255, 200, 90, 220), 2)
            tx.text((305, 335), "UÇAK · saatler", font("Inter-Bold.otf", 32), (255, 228, 170), la, shadow=False)
            lb = ease_out(seg(lt, 4.0, 4.4))
            tx.rrect((90, 390, 690, 460), 16, (8, 16, 36, 190), lb, (200, 220, 255, 200), 2)
            tx.text((390, 425), "KAR PALETLİ KONVOY · haftalar", font("Inter-Bold.otf", 32), (225, 236, 255), lb, shadow=False)
    elif t < 26.0:                                      # S5 BEKLENMEYEN GERÇEK
        lt = t - 20.0
        mv = ease_io3(seg(lt, 3.0, 5.6))
        tgt = slerp(POLE, xyz(*COAST), lerp(0.12, 0.5, mv))
        cam = Cam(tgt, U0, lerp(1.05, 1.55, mv), P=lerp(14, 8, lt / 6), head=lerp(178, 178, lt / 6))
        img, hit, tt = render_globe(cam, sun_vec(60, 0.42), 0.85, 0.1, t, fog=0.1)
        paths = polyline_layers(cam, TM_OUTER, closed=True)
        warn = ease(seg(lt, 1.8, 2.3))
        pulse = 0.5 + 0.5 * math.sin(lt * 9)
        bc = ELECTRIC * (1 - warn) + RED * warn
        fill_poly(img, paths, bc * 0.5, 0.22 + 0.06 * pulse * warn)
        glow_lines(img, paths, bc, 3 + 2 * warn, 22 + 12 * pulse * warn, 1.0)
        xyA, visA = cam.project(A3[None])
        if visA[0]: dot(img, xyA[0], 8, RED, 12, 1.0)
        # Ankara -> en yakın deniz
        df = ease_io3(seg(lt, 3.0, 5.4))
        if df > 0:
            line = great_circle(a_ll, COAST, 160)
            lp = path3d(cam, line * 1.0006)
            glow_lines(img, [partial(p, df) for p in lp], np.array([0.95, 0.97, 1.0], np.float32), 3, 14, 1.0)
            if lp:
                q = partial(lp[0], df)[-1]
                km = int(round(1200 * df / 10) * 10)
                lab = f"{km:,}".replace(",", ".") + " km" if df < 1 else "1.200+ km"
                tx.text((q[0], q[1] - 46), lab, font("InterDisplay-Black.otf", 54), (255, 255, 255), 1.0)
                if df >= 1:
                    ring(img, q, 16 + 40 * ((lt * 0.9) % 1), np.array([0.6, 0.85, 1.0], np.float32), 3, 0.8 * (1 - (lt * 0.9) % 1))
                    tx.text((q[0], q[1] + 44), "EN YAKIN DENİZ", font("InterDisplay-SemiBold.otf", 26), (190, 220, 255), 1.0)
        ka = ease_out(seg(lt, 2.0, 2.4))
        tx.rrect((220, 300, 860, 420), 22, (50, 6, 10, 200), ka, (255, 70, 70, 240), 3)
        tx.text((W / 2, 361), "KIYI: 0 km", font("InterDisplay-Black.otf", 66), (255, 255, 255), ka, shadow=False)
        sa = ease_out(seg(lt, 4.4, 4.8))
        tx.text((W / 2, 470), "Sınırdan bile en yakın deniz ≈ 800 km", font("Inter-SemiBold.otf", 31), (225, 232, 250), sa)
        # bugünkü Türkiye ek penceresi
        ia = ease_out(seg(lt, 0.05, 0.4)) * (1 - ease(seg(lt, 1.8, 2.15)))
        if ia > 0:
            iw, ih = 880, 560
            icam = Cam(xyz(35.0, 39.0), local_north(35.0, 39.0), 0.52, 0, 0, 40, iw, ih)
            inset, _, _ = render_globe(icam, sun_vec(-60, -0.9) * np.array([1, 1, -1]), 1.0, 0, t)
            pts, vis = icam.project(xyz(REAL_TR[:, 0], REAL_TR[:, 1]))
            land = [pts[np.r_[i, i + 1]] for i in range(len(pts) - 1) if REAL_FLAG[i] == 0 and REAL_FLAG[i + 1] == 0]
            coast = [pts[np.r_[i, i + 1]] for i in range(len(pts) - 1) if REAL_FLAG[i] == 1 or REAL_FLAG[i + 1] == 1]
            fill_poly(inset, [pts], ELECTRIC * 0.5, 0.25)
            glow_lines(inset, land, np.array([0.7, 0.75, 0.85], np.float32), 2, 0, 0.9)
            glow_lines(inset, coast, ELECTRIC, 4, 16, ease(seg(lt, 0.3, 0.9)))
            inset = np.clip(inset, 0, 1)
            x0, y0 = (W - iw) // 2, 560 + int((1 - ia) * 40)
            region = img[y0:y0 + ih, x0:x0 + iw]
            img[y0:y0 + ih, x0:x0 + iw] = region * (1 - ia) + inset * ia
            tx.rrect((x0 - 3, y0 - 3, x0 + iw + 3, y0 + ih + 3), 26, (0, 0, 0, 0), ia, (90, 170, 255, 255), 3)
            tx.text((x0 + 30, y0 + 40), "BUGÜN", font("InterDisplay-Black.otf", 34), (255, 255, 255), ia, anchor="lm")
            sl = ease(seg(lt, 0.5, 0.9)) * ia
            for nm, ll in (("KARADENİZ", (35.0, 42.6)), ("EGE", (25.4, 38.6)), ("AKDENİZ", (31.5, 35.1))):
                q, v = icam.project(xyz(*ll)[None])
                tx.text((x0 + q[0][0], y0 + q[0][1]), nm, font("InterDisplay-Bold.otf", 28), (150, 205, 255), sl)
            tx.text((x0 + iw - 30, y0 + 40), "3 DENİZ", font("InterDisplay-Black.otf", 34), to_rgb255(ELECTRIC * 0.8 + 0.2), sl, anchor="rm")
    else:                                               # S6 FİNAL
        lt = t - 26.0; s = ease_io3(seg(lt, 0, 3.6))
        tgt = slerp(slerp(POLE, xyz(*COAST), 0.5), POLE, s)
        D = math.exp(lerp(math.log(1.55), math.log(4.6), s))
        cam = Cam(tgt, U0, D, P=lerp(8, 0, s), head=lerp(178, 160, s))
        img, hit, tt = render_globe(cam, sun_vec(60, 0.42), 1.0, 0, t)
        paths = polyline_layers(cam, TM_OUTER, closed=True)
        fill_poly(img, paths, ELECTRIC * 0.6, 0.35)
        glow_lines(img, paths, ELECTRIC, 3, 20, 1.0)
        ca = ease_out(seg(lt, 0.8, 1.2)) * (1 - seg(lt, 2.3, 2.6))
        tx.rrect((170, 300, 910, 420), 22, (6, 14, 34, 200), ca, (60, 150, 255, 230), 3)
        tx.text((W / 2, 361), "Antarktika ≈ 18 Türkiye", font("InterDisplay-Bold.otf", 54), (255, 255, 255), ca, shadow=False)
        la = ease_out(seg(lt, 2.55, 3.1))
        tx.text((W / 2, 360), "NØVEX", font("InterDisplay-Black.otf", 132), (255, 255, 255), la)
        tx.text((W / 2, 450), "COĞRAFYA · TARİH · YA ŞÖYLE OLSAYDI?", font("InterDisplay-SemiBold.otf", 26), (150, 190, 255), la * ease(seg(lt, 2.8, 3.3)))
        mb = 0.15
    global SCRIM
    if SCRIM is None:
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        SCRIM = (np.exp(-((yy - 1270) / 230) ** 2) * 0.55).astype(np.float32)
        TOPS = None
    img = img * (1 - SCRIM) + np.array([0.0, 0.01, 0.04], np.float32) * SCRIM
    captions(tx, t)
    img = tx.composite(img)
    out = post(img, t, prev, mb if prev is not None else 0)
    return out

def to_u8(img): return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "frame":
        t = float(sys.argv[2]); im = frame(t)
        cv2.imwrite(sys.argv[3], cv2.cvtColor(to_u8(im), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    elif mode == "scene":
        name, out = sys.argv[2], sys.argv[3]
        a, b = SCENES[name]; f0, f1 = round(a * FPS), round(b * FPS)
        tmp = out[:-4] + ".part.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                              "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        prev = None
        for fi in range(f0, f1):
            im = frame(fi / FPS, prev); prev = im
            p.stdin.write(to_u8(im).tobytes())
            if (fi - f0) % 30 == 0: print(name, fi, flush=True)
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.replace(tmp, out)
        sys.exit(rc)
