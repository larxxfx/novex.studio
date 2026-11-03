"""NØVEX fikir puanlama, çeşitlilik ve tekrar kontrolü (strateji: strateji/EDITORIAL_STRATEGY.md §6).

Kullanım:
  python3 araclar/fikir_puanla.py <adaylar.json> [--secim 4] [--kayit konu_kaydi.csv] [--cikti secim.json] [--kaydet]

adaylar.json: [{ "id", "title", "category" (A–H), "mode" (REALITY|SPECULATION|FICTION), "whatif": bool,
                 "keywords": [...], "scores": {hook, global_appeal, curiosity, retention, comments, visual,
                 research, originality}  (her biri 0–10, editör değerlendirmesi), "notes" }]
"repetition" puanı elle verilmez: konu kaydına benzerlikten otomatik hesaplanır.

Kurallar (kategoriler.json → diversity): en az 6 aday; en az 1 What If adayı; günlük 4 seçim; bir kategoriden en fazla 2;
teknoloji (F) en fazla 2; güçlü bir What If (≥ 60) varsa seçime girer. Reddedilir: < 55 puan, REALITY'de araştırma < 5,
son 30 günde yayınlanmış bir konuya ≥ 0,5 benzerlik.
Puanlar karar desteğidir; viral performans tahmini değildir.
"""
import argparse, csv, datetime as dt, json, os, re, sys
from difflib import SequenceMatcher

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AYAR = json.load(open(os.path.join(KOK, "strateji", "kategoriler.json"), encoding="utf-8"))
W = AYAR["scoring_weights"]; D = AYAR["diversity"]


def norm(s):
    return re.sub(r"[^a-z0-9ğüşıöç ]", " ", s.lower())


def benzerlik(aday, satir):
    k1, k2 = set(aday.get("keywords", [])), set(filter(None, satir["keywords"].split(";")))
    jacc = len(k1 & k2) / len(k1 | k2) if k1 and k2 else 0.0
    baslik = SequenceMatcher(None, norm(aday["title"]), norm(satir["title"])).ratio()
    return round(max(jacc, 0.8 * baslik), 3)


def kaydi_oku(yol):
    return list(csv.DictReader(open(yol, encoding="utf-8"))) if os.path.exists(yol) else []


def degerlendir(aday, kayit, bugun):
    s = aday["scores"]
    eksik = [k for k in W if k != "repetition" and k not in s]
    if eksik:
        raise ValueError(f"{aday['id']}: eksik puan {eksik}")
    en_yakin, sim = None, 0.0
    for r in kayit:
        if r.get("slug") == aday["id"]:
            continue
        b = benzerlik(aday, r)
        if b > sim:
            en_yakin, sim = r, b
    tekrar = round(10 * (1 - sim), 1)  # 10 = hiç benzemiyor
    toplam = sum(W[k] * s[k] / 10 for k in W if k != "repetition") + W["repetition"] * tekrar / 10
    neden = []
    if toplam < 55: neden.append("zayıf (< 55)")
    if aday["mode"] == "REALITY" and s["research"] < 5: neden.append("REALITY ama araştırma güvenilirliği < 5")
    if en_yakin and sim >= 0.5 and en_yakin["status"] in ("published", "ready"):
        gun = (bugun - dt.date.fromisoformat(en_yakin["date"])).days
        if gun <= 30: neden.append(f"son {gun} günde yayınlanan/hazır konuya çok benzer: '{en_yakin['title']}' ({sim})")
    uyari = f"önerilmiş benzer konu: '{en_yakin['title']}' ({sim})" if en_yakin and sim >= 0.5 and not neden else ""
    return {**aday, "repetition": tekrar, "benzer": en_yakin["slug"] if en_yakin else None, "benzerlik": sim,
            "total": round(toplam, 1), "reddet": neden, "uyari": uyari}


def sec(degerli, n):
    adaylar = sorted([d for d in degerli if not d["reddet"]], key=lambda d: -d["total"])
    secilen, kat = [], {}
    def uygun(d):
        if kat.get(d["category"], 0) >= D["max_per_category"]: return False
        if d["category"] == "F" and kat.get("F", 0) >= D["max_tech_selected"]: return False
        return True
    whatif = next((d for d in adaylar if (d.get("whatif") or d["category"] == "G") and d["total"] >= 60), None)
    if whatif:
        secilen.append(whatif); kat[whatif["category"]] = 1
    for d in adaylar:
        if len(secilen) >= n: break
        if d in secilen or not uygun(d): continue
        secilen.append(d); kat[d["category"]] = kat.get(d["category"], 0) + 1
    return sorted(secilen, key=lambda d: -d["total"])


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("adaylar"); p.add_argument("--secim", type=int, default=D["daily_shorts"])
    p.add_argument("--kayit", default=os.path.join(KOK, "konu_kaydi.csv")); p.add_argument("--cikti")
    p.add_argument("--kaydet", action="store_true", help="seçilenleri konu kaydına 'proposed' olarak ekle")
    p.add_argument("--tarih", default=dt.date.today().isoformat())
    a = p.parse_args(argv)
    adaylar = json.load(open(a.adaylar, encoding="utf-8"))
    sorun = []
    if len(adaylar) < D["min_candidates"]: sorun.append(f"en az {D['min_candidates']} aday gerekli ({len(adaylar)})")
    if sum(1 for x in adaylar if x.get("whatif") or x["category"] == "G") < D["min_whatif_candidates"]: sorun.append("What If adayı yok")
    bugun = dt.date.fromisoformat(a.tarih)
    kayit = kaydi_oku(a.kayit)
    degerli = [degerlendir(x, kayit, bugun) for x in adaylar]
    secilen = sec(degerli, a.secim)
    print("| # | id | kat | mod | puan | tekrar | durum |\n|---|---|---|---|---|---|---|")
    for i, d in enumerate(sorted(degerli, key=lambda d: -d["total"]), 1):
        durum = "SEÇİLDİ" if d in secilen else ("RED: " + "; ".join(d["reddet"]) if d["reddet"] else "yedek")
        if d["uyari"]: durum += f" · ⚠️ {d['uyari']}"
        print(f"| {i} | {d['id']} | {d['category']} | {d['mode']} | {d['total']} | {d['repetition']} | {durum} |")
    for s in sorun: print("SORUN:", s)
    if len(secilen) < a.secim: print(f"SORUN: yalnızca {len(secilen)} uygun aday — zayıf fikir zorla seçilmedi")
    if a.cikti:
        json.dump({"tarih": a.tarih, "secilen": secilen, "tum": degerli, "sorunlar": sorun}, open(a.cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.kaydet:
        with open(a.kayit, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            for d in secilen:
                w.writerow([a.tarih, "proposed", d["title"], d["id"], d["category"], d["mode"], ";".join(d.get("keywords", []))])
    return 0 if not sorun and len(secilen) == a.secim else 1


if __name__ == "__main__":
    sys.exit(main())
