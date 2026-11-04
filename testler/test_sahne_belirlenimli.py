"""sahne_v1 aynı kareyi her işlemde aynı üretmeli (4 Kas hatası: kamera kayma yönü Python hash() ile seçiliyordu;
paralel render parçaları farklı PYTHONHASHSEED aldığı için sahne ortasında yön sıçrıyordu)."""
import json, os, subprocess, sys, tempfile, unittest

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAHNE = os.environ.get('SAHNE_PY', os.path.join(KOK, 'motor/sahne_v1/sahne.py'))


class TestBelirlenimli(unittest.TestCase):
    def test_kaydirma_kamerasi_hashseedden_bagimsiz(self):
        d = tempfile.mkdtemp()
        plan = {"dil": "modern", "doku": "yok", "kamera": "kaydirma", "kapanis_sn": 1.0,
                "palet": {"zemin0": "#000000", "zemin1": "#101010", "vurgu": "#ffaa00", "metin": "#ffffff", "ikincil": "#888888", "kara": "#333333"},
                "sahneler": [{"cumle": 1, "tur": "baslik", "ust": "TEST", "ana": "Same frame", "alt": "every time"},
                             {"cumle": 2, "tur": "soru", "metin": "Which test should we run next?", "secenekler": ["A", "B"]}]}
        zaman = [{"i": 1, "bas": 0.0, "son": 2.0, "metin": "a"}, {"i": 2, "bas": 2.2, "son": 4.0, "metin": "b"}]
        pj, zj = os.path.join(d, "p.json"), os.path.join(d, "z.json")
        json.dump(plan, open(pj, "w")); json.dump(zaman, open(zj, "w"))
        cikti = []
        for tohum in ("1", "2", "3"):
            out = os.path.join(d, f"k{tohum}.png")
            subprocess.run([sys.executable, SAHNE, "kare", pj, zj, "1.3", out], check=True, capture_output=True,
                           env=dict(os.environ, PYTHONHASHSEED=tohum))
            cikti.append(open(out, "rb").read())
        self.assertEqual(cikti[0], cikti[1]); self.assertEqual(cikti[1], cikti[2])


if __name__ == "__main__":
    unittest.main()
