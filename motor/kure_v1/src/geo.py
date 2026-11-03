"""Coğrafi hazırlık: Natural Earth (kamu malı) verisinden
- Türkiye'yi küre üzerinde KATI DÖNDÜRME ile (şekil ve alan birebir korunur) Ankara = Güney Kutbu olacak şekilde taşır
- Antarktika kara / buz sahanlığı maskesini kutup projeksiyonunda rasterleştirir
- en yakın denize uzaklıkları hesaplar
Çıktı: build/geo.json, build/polar_class.npy
"""
import json, math, os, sys
import numpy as np, cv2
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NE = os.path.join(ROOT, "data", "ne", "geojson")
OUT = os.path.join(ROOT, "build"); os.makedirs(OUT, exist_ok=True)

def load(name):
    return json.load(open(os.path.join(NE, name), encoding="utf-8"))["features"]

def rings_of(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [ [np.array(r, dtype=np.float64) for r in poly] for poly in polys ]

def xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)], -1)

def lonlat(v):
    return np.degrees(np.arctan2(v[..., 1], v[..., 0])), np.degrees(np.arcsin(np.clip(v[..., 2], -1, 1)))

def frame_at(lon, lat):
    u = xyz(lon, lat); lo, la = math.radians(lon), math.radians(lat)
    n = np.array([-math.sin(la)*math.cos(lo), -math.sin(la)*math.sin(lo), math.cos(la)])
    e = np.cross(n, u)
    return u, n, e

countries10 = load("ne_10m_admin_0_countries.geojson")
def country(name):
    for f in countries10:
        if f["properties"]["ADMIN"] == name: return rings_of(f["geometry"])
    raise SystemExit(name)
TR = country("Turkey"); AQ = country("Antarctica")
SHELVES = [r for f in load("ne_10m_antarctic_ice_shelves_polys.geojson") for r in rings_of(f["geometry"])]

ANKARA = (32.8597, 39.9334)
CITIES = {"İstanbul": (28.9784, 41.0082), "Ankara": ANKARA, "İzmir": (27.1428, 38.4237),
          "Antalya": (30.7133, 36.8969), "Trabzon": (39.7168, 41.0027), "Van": (43.3832, 38.5012)}

# --- kutup rasteri (azimutal eşit-uzaklık, merkez = Güney Kutbu) ---
RDEG = 32.0; N = 6400; PPD = N / 2 / RDEG          # piksel/derece (yay)
KM_PER_PX = 6371.0 * math.radians(1) / PPD
def polar_px(lon, lat):
    rho = (90 + lat) * PPD; t = np.radians(lon)
    return np.stack([N/2 + rho*np.sin(t), N/2 - rho*np.cos(t)], -1)

def raster(polys, val, img):
    for poly in polys:
        for k, r in enumerate(poly):
            # kutbu kapatan kenarları (-90) olduğu gibi bırak: AE'de merkez noktasına gider
            pts = np.round(polar_px(r[:, 0], r[:, 1]) * 4).astype(np.int32)
            cv2.fillPoly(img, [pts], val if k == 0 else 0, lineType=cv2.LINE_8, shift=2)

cls = np.zeros((N, N), np.uint8)
raster(AQ, 1, cls)                                   # 1 = kara/buz (grounded+shelf)
shelf = np.zeros_like(cls); raster(SHELVES, 1, shelf)
cls[(shelf == 1) & (cls == 0)] = 2                   # 2 = yüzen buz sahanlığı (NE kara poligonunun dışında)
# Antarctica poligonu -90 kenarı ile kapanır; kutup çevresi doğru dolmuş mu?
assert cls[N//2, N//2] == 1, "kutup dolmadı"
np.save(os.path.join(OUT, "polar_class.npy"), cls)
# iki NE katmanı arasındaki ince boşluklar "deniz" sayılmasın: kapama + yalnızca açık okyanusa bağlı su
land = cv2.morphologyEx((cls > 0).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
lab, _ = ndimage.label(land == 0)
ocean = lab == lab[0, 0]
cls[(~ocean) & (cls == 0)] = 1   # veri katmanları arasındaki iç boşluklar = buz
np.save(os.path.join(OUT, "polar_class.npy"), cls)
dist_km = ndimage.distance_transform_edt(~ocean) * KM_PER_PX

# --- Türkiye'yi taşı: Ankara -> Güney Kutbu, yön açısı phi tarama ---
ua, na, ea = frame_at(*ANKARA)
def rotation(phi_deg):
    up = np.array([0, 0, -1.0]); p = math.radians(phi_deg)
    n_p = np.array([math.cos(p), math.sin(p), 0.0])  # Türkiye'nin "kuzeyi" phi boylamına bakar
    e_p = np.cross(n_p, up)
    return np.stack([up, n_p, e_p], 1) @ np.stack([ua, na, ea], 0)

def move(R, lon, lat):
    return lonlat(xyz(lon, lat) @ R.T)

def sample(lon, lat):
    px = np.round(polar_px(lon, lat)).astype(int)
    return cls[px[:, 1], px[:, 0]], dist_km[px[:, 1], px[:, 0]]

best = None
for phi in range(0, 360, 5):
    R = rotation(phi); c_all = []
    for poly in TR:
        lo, la = move(R, poly[0][:, 0], poly[0][:, 1]); c, d = sample(lo, la); c_all.append(c)
    c_all = np.concatenate(c_all)
    shelf_frac = float(np.mean(c_all == 2)); ocean_frac = float(np.mean(c_all == 0))
    score = ocean_frac * 10 + shelf_frac
    if best is None or score < best[0] - 1e-9 or (abs(score - best[0]) < 1e-9 and abs(phi - 0) < abs(best[1])):
        best = (score, phi, shelf_frac, ocean_frac)
print("en iyi yön:", best)
PHI = best[1]; R = rotation(PHI)

moved = []
border_d = []
for poly in TR:
    rr = []
    for r in poly:
        lo, la = move(R, r[:, 0], r[:, 1]); rr.append(np.stack([lo, la], 1).round(5).tolist())
        c, d = sample(lo, la); border_d.append(d)
    moved.append(rr)
border_d = np.concatenate(border_d)
cities = {}
for k, (lo, la) in CITIES.items():
    mlo, mla = move(R, np.array([lo]), np.array([la]))
    c, d = sample(mlo, mla)
    cities[k] = {"real": [lo, la], "moved": [float(mlo[0]), float(mla[0])], "cls": int(c[0]), "coast_km": float(d[0])}

# Türkiye alanı (gerçek) - küresel poligon alanı, kontrol için
def sph_area(ring):
    lo, la = np.radians(ring[:, 0]), np.radians(ring[:, 1])
    return abs(np.sum((lo[1:] - lo[:-1]) * (2 + np.sin(la[:-1]) + np.sin(la[1:]))) / 2) * 6371.0**2
tr_area = sum(sph_area(p[0]) - sum(sph_area(h) for h in p[1:]) for p in TR)
aq_area = float(np.sum(cls > 0)) * KM_PER_PX**2   # AE yakl.; kontrol amaçlı

# kutuptan en yakın kıyı noktası (çizgi animasyonu için)
oy, ox = np.nonzero(ocean)
dd = np.hypot(ox - N/2, oy - N/2); j = int(np.argmin(dd))
near_rho = dd[j] / PPD; near_lon = math.degrees(math.atan2(ox[j] - N/2, -(oy[j] - N/2)))

def simplify(rings, eps):
    out = []
    for poly in rings:
        r = poly[0]
        a = cv2.approxPolyDP((r * 1e4).astype(np.int32).reshape(-1, 1, 2), eps * 1e4, True).reshape(-1, 2) / 1e4
        if len(a) >= 3: out.append(a.round(4).tolist())
    return out

geo = {
    "phi": PHI, "shelf_frac": best[2], "ocean_frac": best[3],
    "turkey_moved": moved,
    "turkey_real": [[r.round(5).tolist() for r in poly] for poly in TR],
    "antarctica": simplify(AQ, 0.02),
    "cities": cities,
    "pole_coast_km": float(dist_km[N//2, N//2]),
    "nearest_coast": {"lon": near_lon, "lat": -90 + near_rho, "km": float(near_rho * 6371 * math.pi / 180)},
    "border_min_coast_km": float(border_d.min()), "border_max_coast_km": float(border_d.max()),
    "turkey_area_km2": tr_area, "antarctica_area_km2_approx": aq_area,
    "polar": {"N": N, "RDEG": RDEG},
}
# gerçek Türkiye: kıyı mı kara sınırı mı? (komşu ülke kenarına < ~1 km olan noktalar = kara sınırı)
from scipy.spatial import cKDTree
nb = []
for f in countries10:
    if f["properties"]["ADMIN"] in ("Greece", "Bulgaria", "Georgia", "Armenia", "Azerbaijan", "Iran", "Iraq", "Syria"):
        for poly in rings_of(f["geometry"]):
            for r in poly: nb.append(r)
tree = cKDTree(np.concatenate(nb))
main = max(TR, key=lambda p: len(p[0]))[0]
dd, _ = tree.query(main)
geo["turkey_real_main"] = main.round(5).tolist()
geo["turkey_real_coastflag"] = (dd > 0.01).astype(int).tolist()
print("kıyı oranı:", float(np.mean(dd > 0.01)))
json.dump(geo, open(os.path.join(OUT, "geo.json"), "w"), ensure_ascii=False)
print(json.dumps({k: v for k, v in geo.items() if k not in ("turkey_moved", "turkey_real", "antarctica")}, ensure_ascii=False, indent=1))
