"""Dokular: kutup buz dokusu (AE projeksiyon), dünya dokusu (equirect), yıldız gökyüzü.
Tamamen prosedürel + Natural Earth maskeleri. Çıktı: build/*.png"""
import json, math, os
import numpy as np, cv2
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "build"); NE = os.path.join(ROOT, "data", "ne", "geojson")
rng = np.random.default_rng(7)

def noise(shape, cell, rng=rng):
    h, w = shape
    g = rng.standard_normal((max(2, h // cell + 2), max(2, w // cell + 2))).astype(np.float32)
    return cv2.resize(g, (w + 2 * cell, h + 2 * cell), interpolation=cv2.INTER_CUBIC)[cell:cell + h, cell:cell + w]

def fbm(shape, cells, amps):
    out = np.zeros(shape, np.float32)
    for c, a in zip(cells, amps): out += a * noise(shape, c)
    return out

# ---------------- kutup dokusu ----------------
import sys
PART = sys.argv[1] if len(sys.argv) > 1 else "all"
if PART in ("polar", "all"):
  cls0 = np.load(os.path.join(B, "polar_class.npy"))
  N = 4800; cls = cv2.resize(cls0, (N, N), interpolation=cv2.INTER_NEAREST); del cls0
  land = cls == 1; shelf = cls == 2; ocean = cls == 0
  d_coast = ndimage.distance_transform_edt(~ocean).astype(np.float32) * (6400/4800)      # px, karada
  d_land = ndimage.distance_transform_edt(ocean).astype(np.float32) * (6400/4800)       # px, denizde
  coastal = np.exp(-d_coast / 160.0)

  # rüzgâr izleri (sastrugi): tek yönde uzayan, düşük genlikli; kutupta tekillik yok
  sa = cv2.resize(rng.standard_normal((N // 5, N // 90)).astype(np.float32), (N, N), interpolation=cv2.INTER_CUBIC)
  sa += 0.6 * cv2.resize(rng.standard_normal((N // 2, N // 30)).astype(np.float32), (N, N), interpolation=cv2.INTER_CUBIC)
  M = cv2.getRotationMatrix2D((N / 2, N / 2), 28, 1.0)
  streak = cv2.warpAffine(sa, M, (N, N), borderMode=cv2.BORDER_REFLECT); del sa
  h = fbm((N, N), [900, 320, 110, 36, 12], [1.0, 0.5, 0.25, 0.10, 0.035])
  h += 0.015 * streak
  h *= (0.35 + 1.4 * coastal)                       # iç plato düz, kıyı engebeli
  ridge = 1 - np.abs(fbm((N, N), [60, 20], [1.0, 0.5]))
  crev = 0.6 * np.clip((ridge - 0.95) / 0.05, 0, 1) * np.clip(coastal * 1.6 - 0.15, 0, 1)
  h[shelf] = 0.03 * streak[shelf] + 0.12 * h[shelf]
  gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) * 3.0
  gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) * 3.0
  L = np.array([-0.55, -0.6, 0.58]); L /= np.linalg.norm(L)
  shade = (L[2] - L[0] * gx - L[1] * gy) / np.sqrt(1 + gx * gx + gy * gy)
  shade = np.clip(shade / L[2], 0, 1.6)
  del gx, gy, ridge

  lit = np.array([246, 250, 255], np.float32) / 255; shd = np.array([128, 162, 205], np.float32) / 255
  t = np.clip((shade - 0.15) / 1.1, 0, 1)[..., None] ** 0.8
  ice = shd * (1 - t) + lit * t
  ice *= (0.975 + 0.025 * np.clip(streak, -2, 2)[..., None] / 2)
  blue_ice = np.array([90, 140, 200], np.float32) / 255
  ice = ice * (1 - 0.75 * crev[..., None]) + blue_ice * 0.35 * crev[..., None]
  shelf_col = np.array([205, 222, 242], np.float32) / 255 * (0.94 + 0.06 * np.clip(streak, -2, 2) / 2)[..., None]
  # okyanus + deniz buzu
  oc = np.array([7, 18, 40], np.float32) / 255
  deep = np.array([3, 9, 24], np.float32) / 255
  wo = np.clip(d_land / 900.0, 0, 1)[..., None]
  ocean_col = oc * (1 - wo) + deep * wo
  floes = (fbm((N, N), [14, 5, 2], [1, 0.6, 0.3]) > 0.35 + d_land / 160.0)
  pack = np.clip(1 - d_land / 200.0, 0, 1) * floes * 0.7
  ocean_col = ocean_col * (1 - pack[..., None] * 0.8) + np.array([200, 215, 235], np.float32) / 255 * pack[..., None] * 0.8

  tex = np.where(land[..., None], ice, np.where(shelf[..., None], shelf_col, ocean_col))
  # kıyı/sahanlık uçlarında ince açık şerit (buz cephesi)
  front = (d_coast > 0) & (d_coast < 3)
  tex[front] = tex[front] * 0.6 + 0.4
  cv2.imwrite(os.path.join(B, "polar_tex.png"), cv2.cvtColor((np.clip(tex, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
  del tex, ice, h, shade, streak, crev, ocean_col
  print("polar_tex ok")

# ---------------- dünya dokusu (equirect) ----------------
if PART not in ("world", "all"): raise SystemExit
W, H = 6144, 3072
feats = json.load(open(os.path.join(NE, "ne_50m_admin_0_countries.geojson"), encoding="utf-8"))["features"]
mask = np.zeros((H, W), np.uint8)
def eq(c): return np.stack([(c[:, 0] + 180) / 360 * W, (90 - c[:, 1]) / 180 * H], 1)
for f in feats:
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    v = 2 if f["properties"]["ADMIN"] in ("Antarctica", "Greenland") else 1
    for poly in polys:
        for k, ring in enumerate(poly):
            cv2.fillPoly(mask, [np.round(eq(np.array(ring)) * 4).astype(np.int32)], v if k == 0 else 0, cv2.LINE_8, 2)
dl = ndimage.distance_transform_edt(mask == 0).astype(np.float32) * (8192/6144)
n2 = fbm((H, W), [300, 80, 20, 6], [1, 0.5, 0.25, 0.12])
landc = np.array([58, 66, 70], np.float32) / 255 * (0.85 + 0.12 * n2)[..., None]
landc += (np.array([40, 34, 22], np.float32) / 255 * np.clip(noise((H, W), 400), 0, 1)[..., None] * 0.5)
icec = np.array([225, 235, 248], np.float32) / 255 * (0.94 + 0.04 * n2)[..., None]
wo = np.clip(dl / 45.0, 0, 1)[..., None] ** 0.6
oceanc = (np.array([9, 26, 54], np.float32) / 255) * (1 - wo) + (np.array([4, 12, 30], np.float32) / 255) * wo
oceanc *= (0.92 + 0.06 * n2)[..., None]
lat = (90 - (np.arange(H) + 0.5) / H * 180)[:, None]
greenland_ice = (mask == 2) & (lat > 0)
world = np.where(mask[..., None] == 1, landc, oceanc)
world[mask == 2] = icec[mask == 2]
cv2.imwrite(os.path.join(B, "world_tex.jpg"), cv2.cvtColor((np.clip(world, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
            [cv2.IMWRITE_JPEG_QUALITY, 94])
del world, landc, oceanc, icec, n2, dl
print("world_tex ok")

# ---------------- yıldızlar ----------------
if PART != 'all' and PART != 'sky' and PART != 'world': raise SystemExit
SW, SH = 4096, 2048
sky = np.zeros((SH, SW, 3), np.float32)
band = np.exp(-((np.arange(SH)[:, None] - SH * 0.42 - 180 * np.sin(np.arange(SW)[None, :] / SW * 2 * np.pi)) / 160) ** 2)
sky += (band * 0.05 * (0.6 + 0.4 * np.clip(noise((SH, SW), 50), -1, 1)))[..., None] * np.array([0.5, 0.7, 1.0])
n = 9000
ys = rng.integers(0, SH, n); xs = rng.integers(0, SW, n)
b = rng.power(6, n) ** 4 * 0.9 + 0.05
col = np.stack([0.85 + 0.15 * rng.random(n), 0.9 + 0.1 * rng.random(n), np.ones(n)], 1)
for y, x, bb, c in zip(ys, xs, b, col):
    sky[y, x] += c * bb
    if bb > 0.7: cv2.circle(sky, (int(x), int(y)), 1, (c * bb * 0.5).tolist(), -1, cv2.LINE_AA)
cv2.imwrite(os.path.join(B, "sky_tex.png"), cv2.cvtColor((np.clip(sky, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
print("sky ok")
