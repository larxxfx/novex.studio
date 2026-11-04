"""Büyük daire rotası + "karaya değiyor mu?" testi (Natural Earth 10 m). Yeni dosya; mevcut motoru değiştirmez.

Kullanım: python3 src/rota_geo.py  → build/rota_okyanus.json (rota noktaları, uzunluk, kara testi)
Uç noktalar (Chabukswar & Mukherjee 2018, arXiv:1804.07389): Sonmiani 25°16′30″K 66°40′0″D → Karaginsky 58°37′K 162°14′D.
Yön: Pakistan'dan BATIYA (büyük daire üzerinde uzun yay ≈ 32.090 km).
"""
import json, math, os
import numpy as np, cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NE = os.path.join(ROOT, "data", "ne", "geojson"); B = os.path.join(ROOT, "build")
R_KM = 6371.0088
A_LL = (66 + 40 / 60, 25 + 16.5 / 60)        # (lon, lat)
B_LL = (162 + 14 / 60, 58 + 37 / 60)
RES = 0.02                                    # derece/piksel (≈ 2,2 km ekvatorda)


def xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def uzun_yay(a_ll, b_ll, adim_km=1.0):
    """a→b büyük dairesinin UZUN yayı (kısa yayın tamamlayıcısı)."""
    A, Bv = xyz(*a_ll), xyz(*b_ll)
    om = math.acos(float(np.clip(A @ Bv, -1, 1)))      # kısa yay açısı
    uzun = 2 * math.pi - om
    n = int(uzun * R_KM / adim_km) + 1
    # kısa yay A→B yönünün tersine giden yay: A'dan -(B yönü) tarafına
    e = Bv - (A @ Bv) * A; e /= np.linalg.norm(e)        # A'daki kısa yay teğeti
    th = -np.linspace(0, uzun, n)                         # ters yön
    P = np.cos(th)[:, None] * A + np.sin(th)[:, None] * e
    lon = np.degrees(np.arctan2(P[:, 1], P[:, 0])); lat = np.degrees(np.arcsin(np.clip(P[:, 2], -1, 1)))
    return np.stack([lon, lat], -1), uzun * R_KM


def kara_maskesi():
    W, H = int(360 / RES), int(180 / RES)
    m = np.zeros((H, W), np.uint8)
    for f in json.load(open(os.path.join(NE, "ne_10m_admin_0_countries.geojson"), encoding="utf-8"))["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for k, ring in enumerate(poly):
                r = np.asarray(ring, float)
                pts = np.stack([(r[:, 0] + 180) / RES, (90 - r[:, 1]) / RES], -1)
                cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 0 if k else 1, cv2.LINE_8, 4)
    return m


def main():
    rota, km = uzun_yay(A_LL, B_LL)
    m = kara_maskesi()
    H, W = m.shape
    px = np.clip(((rota[:, 0] + 180) / RES).astype(int), 0, W - 1); py = np.clip(((90 - rota[:, 1]) / RES).astype(int), 0, H - 1)
    kara = m[py, px].astype(bool)
    s_km = np.arange(len(rota)) * (km / (len(rota) - 1))
    tampon = 15.0                                            # uç noktalar kıyıda: ilk/son 15 km hariç
    ic = (s_km > tampon) & (s_km < km - tampon)
    dokunus = s_km[ic & kara]
    # kıyıya en yakın geçiş (iç kısımda): uzaklık dönüşümü (piksel → km, enleme göre)
    dist = cv2.distanceTransform((1 - m).astype(np.uint8), cv2.DIST_L2, 5)
    d_km = dist[py, px] * RES * 111.32 * np.cos(np.radians(rota[:, 1])).clip(0.2, 1)
    ici = np.where(ic)[0]; j = ici[np.argmin(d_km[ici])]
    # anahtar noktalar (sahne kamerası için): Mozambik Kanalı, Drake, Pasifik ortası
    def en_yakin(lon, lat):
        d = np.hypot((rota[:, 0] - lon) * np.cos(np.radians(lat)), rota[:, 1] - lat); i = int(np.argmin(d))
        return {"lon": round(float(rota[i, 0]), 3), "lat": round(float(rota[i, 1]), 3), "km": round(float(s_km[i]), 1)}
    sonuc = {"bas": A_LL, "son": B_LL, "uzunluk_km": round(km, 1), "kaynak_km": 32089.7,
             "kara_testi": {"cozunurluk_derece": RES, "uc_tamponu_km": tampon, "karaya_degen_nokta": int(len(dokunus)),
                            "ilk_temaslar_km": [round(float(x), 1) for x in dokunus[:10]],
                            "en_yakin_kiyi_km": round(float(d_km[j]), 1), "en_yakin_kiyi_konum": [round(float(rota[j, 0]), 2), round(float(rota[j, 1]), 2)]},
             "anahtar": {"mozambik": en_yakin(41.5, -18.5), "drake": en_yakin(-66.0, -57.5), "pasifik": en_yakin(-150.0, 0.0)},
             "nokta_10km": rota[::10].round(4).tolist()}
    json.dump(sonuc, open(os.path.join(B, "rota_okyanus.json"), "w"))
    print(json.dumps({k: v for k, v in sonuc.items() if k != "nokta_10km"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
