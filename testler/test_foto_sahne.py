"""`foto` sahnesi: görsel hareket eder, AI görseline kapatılamaz etiket basılır, eksik dosya açık hata verir."""
import json, os, subprocess, sys, tempfile, unittest
import numpy as np, cv2

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAHNE = os.path.join(KOK, "motor/sahne_v1/sahne.py")
PALET = {"zemin0": "#000000", "zemin1": "#111111", "vurgu": "#ffb347", "metin": "#ffffff", "ikincil": "#aaaaaa", "kara": "#333333"}


def kur(d, koken="ai", dosya="g.jpg"):
    img = np.zeros((900, 1400, 3), np.uint8); img[:] = (120, 80, 40)
    for i in range(0, 1400, 70): cv2.line(img, (i, 0), (i + 300, 900), (200, 200, 200), 6)   # dokulu: hareket ölçülebilir
    cv2.imwrite(os.path.join(d, "g.jpg"), img)
    plan = {"dil": "modern", "doku": "yok", "kamera": "sabit", "kapanis_sn": 1, "palet": PALET,
            "sahneler": [{"cumle": 1, "tur": "foto", "dosya": dosya, "koken": koken, "kaynak": "test", "lisans": "test", "hareket": "sag"},
                         {"cumle": 2, "tur": "soru", "metin": "What should we test next?", "secenekler": []}]}
    json.dump(plan, open(os.path.join(d, "p.json"), "w"))
    json.dump([{"i": 1, "bas": 0, "son": 5, "metin": "a"}, {"i": 2, "bas": 5.2, "son": 7, "metin": "b"}], open(os.path.join(d, "z.json"), "w"))


def kare(d, t):
    out = os.path.join(d, f"k{t}.png")
    r = subprocess.run([sys.executable, SAHNE, "kare", os.path.join(d, "p.json"), os.path.join(d, "z.json"), str(t), out], capture_output=True, text=True)
    return r, (cv2.imread(out) if r.returncode == 0 else None)


class TestFoto(unittest.TestCase):
    def test_gorsel_hareket_eder(self):
        d = tempfile.mkdtemp(); kur(d)
        _, a = kare(d, 3.0); _, b = kare(d, 4.6)
        self.assertGreater(np.abs(a.astype(int) - b.astype(int)).mean(), 2.0)

    def test_ai_etiketi_basilir(self):
        d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp(); kur(d1, "ai"); kur(d2, "prosedurel")
        _, a = kare(d1, 3.0); _, b = kare(d2, 3.0)
        bant = slice(190, 226)   # etiket satırı (y≈208)
        self.assertGreater(np.abs(a[bant].astype(int) - b[bant].astype(int)).max(), 100)

    def test_eksik_dosya_acik_hata(self):
        d = tempfile.mkdtemp(); kur(d, dosya="yok.jpg")
        r, _ = kare(d, 1.0)
        self.assertNotEqual(r.returncode, 0); self.assertIn("foto bulunamadı", r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
