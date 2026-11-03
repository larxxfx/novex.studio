"""araclar/fikir_puanla.py testleri. Çalıştırma: python3 -m unittest testler/test_fikir_puanla.py -v"""
import csv, json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "araclar"))
import fikir_puanla as fp

def aday(id_, kat, mod="REALITY", p=8, kw=None, whatif=False, research=None):
    s = {k: p for k in fp.W if k != "repetition"}
    if research is not None: s["research"] = research
    return {"id": id_, "title": id_.replace("-", " "), "category": kat, "mode": mod, "whatif": whatif, "keywords": kw or [id_], "scores": s}

class Test(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.kayit = os.path.join(self.d, "k.csv")
        with open(self.kayit, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["date", "status", "title", "slug", "category", "mode", "keywords"])
            w.writerow(["2026-11-01", "published", "Turkey in Antarctica", "turkey-in-antarctica", "G", "SPECULATION", "turkey;antarctica;what-if"])
    def run_(self, adaylar, *ek):
        y = os.path.join(self.d, "a.json"); json.dump(adaylar, open(y, "w")); c = os.path.join(self.d, "c.json")
        rc = fp.main([y, "--kayit", self.kayit, "--cikti", c, "--tarih", "2026-11-03", *ek]); return rc, json.load(open(c))

    def test_puan_100_uzerinden(self):
        r = fp.degerlendir(aday("x", "A", p=10), [], fp.dt.date(2026, 11, 3)); self.assertEqual(r["total"], 100.0)
        r = fp.degerlendir(aday("x", "A", p=0), [], fp.dt.date(2026, 11, 3)); self.assertEqual(r["total"], 7.0)  # yalnız tekrar puanı
    def test_cesitlilik_kategori_ve_teknoloji_siniri(self):
        ad = [aday(f"t{i}", "F", p=9, kw=[f"k{i}"]) for i in range(4)] + [aday("h", "A", p=7), aday("w", "G", "SPECULATION", 7, whatif=True)]
        rc, o = self.run_(ad); kats = [s["category"] for s in o["secilen"]]
        self.assertEqual(rc, 0); self.assertLessEqual(kats.count("F"), 2); self.assertIn("G", kats)
    def test_az_aday_ve_whatif_yok_sorun(self):
        rc, o = self.run_([aday(f"a{i}", "ABCDE"[i]) for i in range(5)])
        self.assertEqual(rc, 1); self.assertTrue(any("6 aday" in s for s in o["sorunlar"])); self.assertIn("What If adayı yok", o["sorunlar"])
    def test_yakin_tarihli_yayinla_tekrar_reddedilir(self):
        ad = [aday("turkey-antarctica-again", "G", "SPECULATION", 9, kw=["turkey", "antarctica", "what-if"], whatif=True)] + \
             [aday(f"o{i}", "ABCDE"[i], kw=[f"z{i}"]) for i in range(5)]
        rc, o = self.run_(ad); r = next(x for x in o["tum"] if x["id"] == "turkey-antarctica-again")
        self.assertTrue(any("çok benzer" in n for n in r["reddet"]))
    def test_reality_zayif_arastirma_reddedilir(self):
        r = fp.degerlendir(aday("x", "D", research=3), [], fp.dt.date(2026, 11, 3)); self.assertTrue(r["reddet"])
    def test_zayif_fikir_zorla_secilmez(self):
        ad = [aday(f"a{i}", "ABCDEF"[i], p=3, kw=[f"q{i}"]) for i in range(6)]; ad[5]["whatif"] = True
        rc, o = self.run_(ad); self.assertEqual(o["secilen"], []); self.assertEqual(rc, 1)

if __name__ == "__main__":
    unittest.main()
