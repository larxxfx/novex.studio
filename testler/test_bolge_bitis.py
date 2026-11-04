"""Referans videonun imza öğeleri: ülke vurgusu/taşıma (kuzey yukarıda, gerçek boyut) ve kapanış kartı."""
import importlib.util, json, os, subprocess, sys, tempfile, unittest
import numpy as np, cv2

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAHNE = os.path.join(KOK, "motor/sahne_v1/sahne.py")
spec = importlib.util.spec_from_file_location("sahne", SAHNE); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)


class TestBolge(unittest.TestCase):
    def test_tasima_yonu_ve_boyutu_korur(self):
        h = S.ulke_halkalari("Turkey"); t = S.bolge_tasi(h, [-98, 40])
        a, b = np.concatenate(h), np.concatenate(t)
        self.assertAlmostEqual(np.ptp(a[:, 1]), np.ptp(b[:, 1]), delta=0.5)      # enlem genişliği aynı → dönmedi
        self.assertLess(abs(np.ptp(b[:, 0]) - np.ptp(a[:, 0])), 1.5)            # boylam genişliği ~aynı (benzer enlem)
        self.assertLess(abs(b[:, 0].mean() + 98), 1.0); self.assertLess(abs(b[:, 1].mean() - 40), 1.5)

    def test_bilinmeyen_ulke_acik_hata(self):
        with self.assertRaises(SystemExit): S.ulke_halkalari("Atlantis")

    def test_ulke_kirmizi_cizilir_ve_bitis_karti(self):
        d = tempfile.mkdtemp()
        plan = {"dil": "modern", "doku": "yok", "kamera": "sabit", "kapanis_sn": 3.0,
                "palet": {"zemin0": "#000000", "zemin1": "#111111", "vurgu": "#ffc23d", "metin": "#ffffff", "ikincil": "#aaaaaa", "kara": "#333333"},
                "sahneler": [{"cumle": 1, "tur": "gezegen", "doku": "dunya", "merkez": [540, 1000], "yaricap": [1400, 1400], "hedef": [35, 39],
                              "bolge": [{"ulke": "Turkey", "renk": "#ff0000", "dolgu": 0.8, "bas": 0.0}]},
                             {"cumle": 2, "tur": "soru", "metin": "Which country should we move next?", "secenekler": [], "bitis_karti": True}]}
        json.dump(plan, open(os.path.join(d, "p.json"), "w"))
        json.dump([{"i": 1, "bas": 0, "son": 3, "metin": "a"}, {"i": 2, "bas": 3.2, "son": 5, "metin": "b"}], open(os.path.join(d, "z.json"), "w"))
        def kare(t):
            out = os.path.join(d, f"{t}.png"); subprocess.run([sys.executable, SAHNE, "kare", *[os.path.join(d, x) for x in ("p.json", "z.json")], str(t), out], check=True, capture_output=True)
            return cv2.imread(out)
        a = kare(2.0); merkez = a[950:1050, 490:590].reshape(-1, 3).mean(0)     # BGR: kırmızı baskın
        self.assertGreater(merkez[2], merkez[1] + 40)
        son = kare(7.6)                                                            # son kart: soru metni görünmez, logo görünür
        self.assertLess(son[300:700].mean(), 25); self.assertGreater(son[780:900].max(), 150)


if __name__ == "__main__":
    unittest.main()
