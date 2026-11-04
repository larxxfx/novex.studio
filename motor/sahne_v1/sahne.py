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
  soru      {metin, secenekler:["MARS","MERCURY"]}   ZORUNLU kapanış: "sırada ne?" sorusu (uzun seçenekler otomatik alt alta)
  gezegen   3D ışın izlemeli küre (yeni standartta baskın sahne türü):
            doku: venus|mars|ay|buz|gaz|dunya|dunya_kuru (Akdeniz tuz çölü)|yok (küre yok; yalnız dişli/yazı)
            merkez [x,y], yaricap [r0,r1] (zum), donus °/sn, egim °, isik [x,y,z], atmosfer hex
            hedef [lon,lat] (o nokta ekran ortasına döner), hedef_bas [lon,lat] (kamera oradan kayar), dalis 0..1 (üstel zum = dalış)
            isaretler [[lon,lat,"etiket","#renk","ust|alt"]] (parlayan nabızlı nokta), cizgi [[lon,lat],...] + cizgi_renk/cizgi_bas/cizgi_sure
            disliler [[x,y,r,dis,yon]] + disli_renk/disli_hiz/disli_guc (dönen dişliler)
            yazılar: ust, ana, boyut, sayi {bas,son,birim,etiket,sure}, karsi [[et,deger],[et,deger]], ok "saat", kontur (okunurluk)
Plan düzeyi sinematik katmanlar: partikul {tur: toz|kar|kor|yildiz_akisi, yogunluk, renk, guc}, isik_huzme {aci, renk, guc},
  parlama true/false, vurgu_kelimeler [...] (altyazıda vurgu rengi). Örnekler: videolar/2026-11-04_*/sahne_plani.json.
"""
import argparse, json, math, os, re, subprocess, sys, zlib
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
def eio3(x): x = cl(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

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

def yazi(dr, xy, s, f, fill, a=1.0, anchor="mm", golge=True, kontur=0):
    if a <= 0.01: return
    c = fill[:3] + (int(fill[3] * a) if len(fill) > 3 else int(255 * a),)
    if golge: dr.text((xy[0] + 3, xy[1] + 4), s, font=f, fill=(0, 0, 0, int(140 * a)), anchor=anchor)
    if kontur: dr.text(xy, s, font=f, fill=c, anchor=anchor, stroke_width=kontur, stroke_fill=(0, 0, 0, int(200 * a)))
    else: dr.text(xy, s, font=f, fill=c, anchor=anchor)

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
    fo0 = font(dil, "agir", 58); logo_y = 1180
    if sec and max(dr.textlength(o, font=fo0) for o in sec) > 300:   # uzun seçenek: tam genişlikte alt alta
        for i, o in enumerate(sec):
            b = ease(seg(ts, 0.7 + i * 0.25, 1.0 + i * 0.25)); yy = y + i * 135; yg = min(390, (dr.textlength(o, font=fo0) + 80) / 2)
            dr.rounded_rectangle((W / 2 - yg, yy - 55, W / 2 + yg, yy + 55), 28, outline=renk(p["vurgu"], int(255 * b)), width=4, fill=renk(p["zemin1"], int(150 * b)))
            yazi(dr, (W / 2, yy), o, fo0, renk(p["vurgu"]), b, golge=False)
        logo_y = max(1180, yy + 150); sec = []
    for i, o in enumerate(sec):
        b = ease(seg(ts, 0.7 + i * 0.25, 1.0 + i * 0.25)); x = W / 2 + (i - (len(sec) - 1) / 2) * 380
        fo = font(dil, "agir", 58); yg = max(140, (dr.textlength(o, font=fo) + 70) / 2)   # kutu yazıya göre genişler (MERCURY taşmasın)
        if len(sec) > 1: yg = min(yg, 185)
        if dr.textlength(o, font=fo) > 2 * yg - 50: fo = font(dil, "agir", 48)
        dr.rounded_rectangle((x - yg, y - 55, x + yg, y + 55), 28, outline=renk(p["vurgu"], int(255 * b)), width=4, fill=renk(p["zemin1"], int(150 * b)))
        yazi(dr, (x, y), o, fo, renk(p["vurgu"]), b, golge=False)
    yazi(dr, (W / 2, logo_y), "NØVEX", font("modern", "agir", 64), renk(p["metin"]), ease(seg(ts, 1.4, 2.0)))


# ---------- 3D gezegen (ışın izlemeli küre, prosedürel/gerçek doku) ----------
_DOKU = {}
def fbm(h, w, oktav, seed, yatay=1.0):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); a = 1.0; t = 0
    for o in range(oktav):
        gh, gw = max(2, int(4 * 2 ** o)), max(2, int(4 * 2 ** o * yatay))
        n = rng.standard_normal((gh, gw)).astype(np.float32)
        out += a * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC); t += a; a *= 0.55
    out /= t
    m = np.abs(np.linspace(-1, 1, w, dtype=np.float32))[None, :]          # yatayda döşenebilir: yarım kaydırılmış kopyayla harmanla (dikiş yok)
    out = out * (1 - m) + np.roll(out, w // 2, axis=1) * m
    return (out - out.min()) / (out.max() - out.min() + 1e-9)

def gezegen_dokusu(tur):
    if tur in _DOKU: return _DOKU[tur]
    H_, W_ = 1024, 2048
    if tur == "dunya_kuru":   # Mesiniyen tuzluluk krizi: Akdeniz havzası tuz çölü (Karadeniz ve Atlantik hariç)
        d = gezegen_dokusu("dunya")[0].copy(); th, tw = d.shape[:2]
        lon = (np.arange(tw) / tw * 360 - 180)[None, :]; lat = (90 - np.arange(th) / th * 180)[:, None]
        r_, g_, b_ = d[..., 0], d[..., 1], d[..., 2]
        su = (b_ - r_ > 0.065) & (r_ < 0.14)   # ölçüm: deniz ~(3,10,26), kara ~(33–49, 37–57, 38–60) /255
        hav = (lon > -5.4) & (lon < 36.5) & (lat > 30.0) & (lat < 46.0) & ~((lon > 26.8) & (lat > 40.6)) & ~((lon < 2.5) & (lat > 41.5))   # Karadeniz ve Biskay (Atlantik) hariç
        m = (su & hav).astype(np.float32); m = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]
        n = cv2.resize(fbm(512, 1024, 6, 55), (tw, th))[..., None]
        tuz = np.array([0.86, 0.82, 0.72], np.float32) * (0.75 + 0.35 * n) + np.array([0.0, -0.05, -0.12], np.float32) * (n > 0.6)
        _DOKU[tur] = (d * (1 - m) + tuz * m, None); return _DOKU[tur]
    if tur == "dunya":
        im = cv2.imread(os.path.join(DEPO, "motor/kure_v1/build/world_tex.jpg"))
        d = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), (4096, 2048), interpolation=cv2.INTER_AREA).astype(np.float32) / 255; bulut = None   # dalış için 4096'lık
    else:
        renkler = {"venus": ((0.55, 0.36, 0.16), (0.98, 0.86, 0.58)), "mars": ((0.35, 0.12, 0.06), (0.85, 0.45, 0.25)),
                   "ay": ((0.25, 0.25, 0.26), (0.78, 0.77, 0.74)), "buz": ((0.55, 0.68, 0.80), (0.95, 0.98, 1.0)),
                   "gaz": ((0.55, 0.40, 0.28), (0.95, 0.90, 0.80))}[tur]
        n = fbm(H_, W_, 7, {"venus": 3, "mars": 5, "ay": 7, "buz": 9, "gaz": 11}[tur], yatay=3.0 if tur in ("venus", "gaz") else 1.0)
        if tur in ("venus", "gaz"):  # enlem bantları
            y = np.linspace(0, 1, H_)[:, None]; n = 0.6 * n + 0.4 * (0.5 + 0.5 * np.sin(y * np.pi * 9 + 2.5 * fbm(H_, W_, 3, 21)))
        if tur == "ay": n = n * 0.7 + 0.3 * (fbm(H_, W_, 7, 31) > 0.62)
        c0, c1 = np.array(renkler[0], np.float32), np.array(renkler[1], np.float32)
        d = c0 + (c1 - c0) * n[..., None]
        bulut = fbm(H_, W_, 5, 41, yatay=4.0) if tur == "venus" else None
    _DOKU[tur] = (d, bulut); return _DOKU[tur]

def gz_param(s, ts, u):
    """Küre kamerası: merkez, yarıçap (zum), eğim ve dönüş. `hedef` [lon, lat] verilirse o nokta ekranın ortasına döner;
    `hedef_bas` verilirse kamera ondan hedefe kayar (yarıçap büyümesiyle birlikte = dalış)."""
    cx, cy = s.get("merkez", [W / 2, 820]); r0, r1 = s.get("yaricap", [380, 520])
    e = ease(u) if not s.get("dalis") else eio3(seg(u, 0.0, s["dalis"]))
    R = r0 * (r1 / r0) ** e if s.get("dalis") else r0 + (r1 - r0) * e   # dalışta üstel zum: sabit hız hissi
    if s.get("hedef"):
        lo, la = s["hedef"]; lb, ab = s.get("hedef_bas", s["hedef"]); k = e
        lon_c = lb + (lo - lb) * k; lat_c = ab + (la - ab) * k
        return cx, cy, R, math.radians(-lat_c), math.radians(lon_c + s.get("donus", 0) * ts)
    return cx, cy, R, math.radians(s.get("egim", 12)), math.radians(s.get("donus", 4) * ts + s.get("lon0", 0))

def gz_izdusum(s, ts, u, lon, lat):
    """lon/lat (°) → ekran (x, y, görünür mü). gezegen_katman'daki eşlemenin tersi."""
    cx, cy, R, eg, rot = gz_param(s, ts, u)
    lr = math.radians(lon) - rot; ar = math.radians(lat)
    X = math.cos(ar) * math.sin(lr); Yt = math.sin(ar); Zt = math.cos(ar) * math.cos(lr)
    Y = Yt * math.cos(eg) + Zt * math.sin(eg); Z = -Yt * math.sin(eg) + Zt * math.cos(eg)
    return cx + X * R, cy - Y * R, Z > 0.02

def gezegen_katman(s, ts, u):
    """RGBA float katman (W×H×4, 0..255): küre + atmosfer halesi. s: tur, merkez[x,y], yaricap[r0,r1], donus (°/sn), isik[x,y,z], atmosfer hex, egim (°),
    hedef/hedef_bas/dalis (Dünya'ya dalış)."""
    d, bulut = gezegen_dokusu(s.get("doku", "venus"))
    cx, cy, R, eg, rot = gz_param(s, ts, u)
    pad = int(R * 0.35); x0, x1 = int(max(0, cx - R - pad)), int(min(W, cx + R + pad)); y0, y1 = int(max(0, cy - R - pad)), int(min(H, cy + R + pad))
    out = np.zeros((H, W, 4), np.float32)
    if x1 <= x0 or y1 <= y0: return out
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); X = (xx - cx) / R; Y = (cy - yy) / R; r2 = X * X + Y * Y; ic = r2 <= 1
    Z = np.sqrt(np.clip(1 - r2, 0, 1))
    Yt = Y * math.cos(eg) - Z * math.sin(eg); Zt = Y * math.sin(eg) + Z * math.cos(eg)
    lon = np.arctan2(X, Zt) + rot; lat = np.arcsin(np.clip(Yt, -1, 1))
    if s.get("doku", "venus").startswith("dunya"): lon = lon + np.pi   # eşdikdörtgen Dünya dokusunun sol kenarı 180°B
    th, tw = d.shape[:2]; mx = ((lon / (2 * np.pi)) % 1.0 * tw).astype(np.float32); my = ((0.5 - lat / np.pi) * th).astype(np.float32)
    col = cv2.remap(d, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    if bulut is not None:
        mxb = (((lon + 0.6 * ts * 0.05) / (2 * np.pi)) % 1.0 * tw).astype(np.float32)
        b = cv2.remap(bulut, mxb, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)[..., None]; col = col * (0.75 + 0.35 * b)
    L = np.array(s.get("isik", [-0.6, 0.35, 0.75]), np.float32); L /= np.linalg.norm(L)
    ndl = X * L[0] + Y * L[1] + Z * L[2]; dif = np.clip(ndl * 1.15 + 0.08, 0, 1.2)[..., None]
    atm = np.array(renk(s.get("atmosfer", "#ffb860"))[:3], np.float32) / 255
    kenar = (1 - Z) ** 2.5; lit = col * (0.06 + dif) + atm * (kenar * np.clip(ndl + 0.35, 0, 1))[..., None] * 0.9
    rgb = np.where(ic[..., None], lit, 0); a = ic.astype(np.float32)
    dist = np.sqrt(r2); hale = np.exp(-np.clip(dist - 1, 0, None) / 0.06) * (dist > 1) * np.clip(X * L[0] + Y * L[1] + 0.6, 0.15, 1.2)
    rgb = rgb + atm * hale[..., None] * 0.8; a = np.clip(a + hale * 0.8, 0, 1)
    out[y0:y1, x0:x1, :3] = np.clip(rgb, 0, 1.6) * 255; out[y0:y1, x0:x1, 3] = a * 255
    return out

def disli_ciz(dr, s, ts, p):
    """Birbirine geçen dönen dişliler (Antikythera). disliler: [[x, y, r, dis_sayisi, yon(+1/-1)], ...]; disli_renk hex."""
    cc = s.get("disli_renk", p["vurgu"]); a0 = ease(seg(ts, 0.0, 0.5)) * s.get("disli_guc", 1.0); hiz = s.get("disli_hiz", 12)
    for j, (x, y, r, n, yon) in enumerate(s["disliler"]):
        aci = math.radians(yon * hiz * ts * 60 / n); pts = []
        for k in range(n * 4):
            t_ = aci + k * math.pi / (n * 2); rr = r if (k % 4) in (1, 2) else r * (1 - 1.6 / n * 2.2)
            pts.append((x + rr * math.cos(t_), y + rr * math.sin(t_)))
        for gen, al in ((22, 30), (10, 70)): dr.line(pts + [pts[0]], fill=renk(cc, int(al * a0)), width=gen, joint="curve")
        dr.polygon(pts, fill=renk(p.get("zemin1", "#000000"), int(200 * a0)), outline=renk(cc, int(255 * a0)), width=4)
        ri = r * 0.72; dr.ellipse((x - ri, y - ri, x + ri, y + ri), outline=renk(cc, int(150 * a0)), width=3)
        for q in range(4 if r > 120 else 3):   # kollar
            t_ = aci + q * 2 * math.pi / (4 if r > 120 else 3)
            dr.line([(x + r * 0.14 * math.cos(t_), y + r * 0.14 * math.sin(t_)), (x + ri * math.cos(t_), y + ri * math.sin(t_))], fill=renk(cc, int(170 * a0)), width=max(4, int(r * 0.06)))
        rh = r * 0.12; dr.ellipse((x - rh, y - rh, x + rh, y + rh), outline=renk(cc, int(255 * a0)), width=4)

def c_gezegen(L, dr, plan, s, u, ts):
    dil, p = plan["dil"], plan["palet"]
    if s.get("cizgi"):   # küre üzerinde zamanla çizilen parlayan hat (kıyı, boğaz, rota)
        pts = s["cizgi"]; k = eout(seg(ts, s.get("cizgi_bas", 0.3), s.get("cizgi_bas", 0.3) + s.get("cizgi_sure", 1.4)))
        n = max(2, int(round(len(pts) * k))); xy = [gz_izdusum(s, ts, u, lo, la) for lo, la in pts[:n]]
        par = []; cur = []
        for x, y, g in xy:
            if g: cur.append((x, y))
            elif cur: par.append(cur); cur = []
        if cur: par.append(cur)
        cc = s.get("cizgi_renk", p["vurgu"])
        for q in par:
            if len(q) < 2: continue
            for gen, al in ((26, 40), (14, 90), (5, 255)): dr.line(q, fill=renk(cc, al), width=gen, joint="curve")
    for i, m in enumerate(s.get("isaretler", [])):   # parlayan, nabız atan nokta + etiket
        x, y, g = gz_izdusum(s, ts, u, m[0], m[1]); a = ease(seg(ts, 0.4 + i * 0.3, 0.9 + i * 0.3))
        if not g or a <= 0.01: continue
        cc = m[3] if len(m) > 3 else p["vurgu"]
        for rr, al in ((34, 40), (22, 80), (12, 255)): dr.ellipse((x - rr, y - rr, x + rr, y + rr), fill=renk(cc, int(al * a)))
        nb = (ts * 0.8 + i * 0.3) % 1.0; rr = 18 + 70 * nb
        dr.ellipse((x - rr, y - rr, x + rr, y + rr), outline=renk(cc, int(220 * a * (1 - nb))), width=4)
        if len(m) > 2 and m[2]:
            fe = font(dil, "kalin", 44); tw = dr.textlength(m[2], font=fe); lx = min(max(x, 160 + tw / 2), 920 - tw / 2)
            ly = (y + 80 if m[4] == "alt" else y - 80) if len(m) > 4 else (y - 80 if y > 420 else y + 80)
            yazi(dr, (lx, ly), m[2], fe, renk(p["metin"]), a, kontur=4)
    if s.get("disliler"): disli_ciz(dr, s, ts, p)
    kt = s.get("kontur", 0)   # parlak zemin (Dünya yakın plan) üstünde okunurluk
    if s.get("ust"): yazi(dr, (W / 2, 250), s["ust"].upper(), font(dil, "orta", 40), renk(p["vurgu"]), ease(seg(ts, 0.2, 0.6)), kontur=kt)
    if s.get("ana"):
        f = font(dil, "agir", s.get("boyut", 96))
        for i, sa in enumerate(satirla(s["ana"], f, 880)): yazi(dr, (W / 2, 330 + i * 106), sa, f, renk(p["metin"]), ease(seg(ts, 0.35 + i * 0.15, 0.8 + i * 0.15)), kontur=kt)
    if s.get("sayi"):
        z = s["sayi"]; v = z["bas"] + (z["son"] - z["bas"]) * eout(seg(ts, 0.3, z.get("sure", 2.0))); f = font(dil, "agir", 170)
        yazi(dr, (W / 2, 330), f"{v:,.0f}", f, renk(p["vurgu"]), ease(seg(ts, 0.1, 0.4)))
        if z.get("birim"): yazi(dr, (W / 2, 450), z["birim"], font(dil, "kalin", 58), renk(p["metin"]), ease(seg(ts, 0.4, 0.7)))
        if z.get("etiket"):   # gezegen üstünde okunur kalsın; güvenli alan için satıra böl
            fe = font(dil, "orta", 42)
            for j, sa in enumerate(satirla(z["etiket"], fe, 780)): yazi(dr, (W / 2, 520 + j * 52), sa, fe, renk(p["metin"]), ease(seg(ts, 0.6, 1.0)), kontur=4)
    if s.get("karsi"):   # iki değer karşılaştırması (ör. YIL 225 · GÜN 243)
        for i, (et, v) in enumerate(s["karsi"]):
            x = W / 2 + (i - 0.5) * 420; a = ease(seg(ts, 0.3 + i * 0.6, 0.7 + i * 0.6))
            yazi(dr, (x, 300), et.upper(), font(dil, "kalin", 40), renk(p["ikincil"]), a)
            yazi(dr, (x, 400), str(v), font(dil, "agir", 130), renk(p["vurgu"] if i else p["metin"]), a)
    if s.get("ok"):  # dönüş yönü oku (retrograd)
        a = ease(seg(ts, 0.6, 1.0)); cx, cy = s.get("merkez", [W / 2, 820]); R = s.get("yaricap", [380, 520])[1] + 60
        bas_a, son_a = (200, 340) if s["ok"] == "saat" else (340, 200)
        dr.arc((cx - R, cy - R, cx + R, cy + R), min(bas_a, son_a), max(bas_a, son_a), fill=renk(p["vurgu"], int(230 * a)), width=8)
        ang = math.radians(son_a); tip = (cx + R * math.cos(ang), cy + R * math.sin(ang)); dd = 1 if s["ok"] == "saat" else -1
        dr.polygon([tip, (tip[0] - 28 * dd, tip[1] - 22), (tip[0] - 6 * dd, tip[1] + 30)], fill=renk(p["vurgu"], int(255 * a)))

# ---------- sinematik katmanlar: partikül, ışık huzmesi, parlama ----------
_PART = {}
def partikul(img, t, plan):
    pk = plan.get("partikul")
    if not pk: return img
    n = pk.get("yogunluk", 160); tur = pk.get("tur", "toz")
    if tur not in _PART:
        rng = np.random.default_rng(77); _PART[tur] = (rng.uniform(0, W, n), rng.uniform(0, H, n), rng.uniform(0.3, 1, n), rng.uniform(0, 6.28, n))
    x, y, z, f = _PART[tur]; c = np.array(renk(pk.get("renk", plan["palet"]["metin"]))[:3], np.float32)
    hiz = {"toz": (8, -6), "kar": (-10, 60), "kor": (6, -45), "yildiz_akisi": (0, 120)}.get(tur, (8, -6))
    px = (x + hiz[0] * t * z + 14 * np.sin(t * 0.7 + f)) % W; py = (y + hiz[1] * t * z) % H
    lay = np.zeros((H // 2, W // 2), np.float32)
    for a_, b_, zz, ff in zip(px / 2, py / 2, z, f):
        cv2.circle(lay, (int(a_), int(b_)), 1 if zz < 0.7 else 2, float(0.35 + 0.65 * zz) * (0.6 + 0.4 * math.sin(t * 2 + ff)), -1, lineType=cv2.LINE_AA)
    lay = cv2.GaussianBlur(cv2.resize(lay, (W, H)), (0, 0), 1.2)
    return img + lay[..., None] * c * pk.get("guc", 0.55)

def isik_huzme(img, t, plan):
    ih = plan.get("isik_huzme")
    if not ih: return img
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32); ang = math.radians(ih.get("aci", 28) + 4 * math.sin(t * 0.15))
    k = (xx * math.cos(ang) + yy * math.sin(ang)) / 18.0
    m = (0.5 + 0.5 * np.sin(k + t * 0.3)) ** 6 * np.exp(-yy / (H / 4) * 1.6)
    m = cv2.resize(cv2.GaussianBlur(m, (0, 0), 3), (W, H))
    return img + m[..., None] * np.array(renk(ih.get("renk", plan["palet"]["vurgu"]))[:3], np.float32) * ih.get("guc", 0.18)

def parlama(img, plan):
    if not plan.get("parlama", False): return img   # varsayılan kapalı: eski planların görüntüsü değişmez
    k = cv2.resize(np.clip(img - 190, 0, None), (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    return img + cv2.resize(cv2.GaussianBlur(k, (0, 0), 6), (W, H)) * 0.55

CIZ = {"baslik": c_baslik, "sayi": c_sayi, "harita": c_harita, "zaman": c_zaman, "karsilastir": c_karsilastir,
       "alinti": c_alinti, "liste": c_liste, "soru": c_soru, "gezegen": c_gezegen}

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
    if sc["tur"] == "gezegen" and sc.get("doku") != "yok":   # 3D küre metnin altında; metin üstte
        g = gezegen_katman(sc, t - a, cl((t - a) / (b - a))); ta = arr[..., 3:4] / 255
        arr = np.concatenate([g[..., :3] * (1 - ta) + arr[..., :3] * ta, np.maximum(g[..., 3:4], arr[..., 3:4])], -1)
    # kamera: yavaş itme / kaydırma (sahne başına yön değişir)
    k = plan.get("kamera", "itme"); u = cl((t - a) / max(b - a, 1e-6))
    if k != "sabit":
        sc_ = 1.0 + (0.05 * u if k == "itme" else 0.03); dx = (18 * (u - 0.5) * (1 if zlib.crc32(sc["tur"].encode()) % 2 else -1)) if k == "kaydirma" else 0
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
    img = isik_huzme(img, t, plan); img = partikul(img, t, plan); img = parlama(img, plan)
    # altyazı: alt bant (y 1250–1480), güvenli alan içinde
    if caps and not kapak:
        S = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(S); f = font(plan["dil"] if plan["dil"] != "daktilo" else "modern", "kalin", 50)
        for c0, c1, m in caps:
            if c0 - 0.05 <= t < c1 + 0.12:
                aa = ease(seg(t, c0 - 0.05, c0 + 0.12)) * (1 - seg(t, c1, c1 + 0.12))
                vk = {w.lower() for w in plan.get("vurgu_kelimeler", [])}
                for i, sa in enumerate(satirla(m, f, 780)):
                    x = W / 2 - f.getlength(sa) / 2
                    for kel in sa.split():
                        cc = renk(plan["palet"]["vurgu"]) if kel.strip(".,?!:;'\"").lower() in vk else (255, 255, 255, 255)
                        yazi(d, (x, 1300 + i * 64), kel, f, cc, aa, anchor="lm"); x += f.getlength(kel + " ")
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
    if sc.get("tur") == "gezegen":   # gezegen sahnesinde yazılar küreyle aynı katmanda: kapak zemini için yazısız kopya
        ara = list(ara); ara[i] = (a, b, {kk: v for kk, v in sc.items() if kk not in ("ust", "ana", "sayi", "karsi", "ok")})
        img = kare(plan, z, [], a + min(2.5, (b - a) * 0.8), ara, kapak=True).astype(np.float32) * 0.75
    else:
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
