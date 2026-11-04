import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "araclar"))
from kuyruk_dogrula import dogrula

BAS = "| ID | Görev | Sahip | Öncelik | Durum | Tarih | Sonuç |\n|---|---|---|---|---|---|---|\n"
def s(id_, gorev="İş A", sahip="Claude", durum="açık", sonuc=""): return f"| {id_} | {gorev} | {sahip} | P1 | {durum} | 04.11 | {sonuc} |\n"


class Test(unittest.TestCase):
    def test_temiz(self): self.assertEqual(dogrula(BAS + s("T-20261104-01") + s("T-20261104-02", "İş B", "ChatGPT")), [])
    def test_tekrar_id(self): self.assertTrue(any("tekrar" in h for h in dogrula(BAS + s("T-20261104-01") + s("T-20261104-01", "İş B"))))
    def test_tekrar_gorev(self): self.assertTrue(any("zaten açık" in h for h in dogrula(BAS + s("T-20261104-01") + s("T-20261104-02", "iş a!"))))
    def test_tamam_kanitsiz(self): self.assertTrue(any("kanıt" in h for h in dogrula(BAS + s("T-20261104-01", durum="tamam"))))
    def test_tamam_kanitli(self): self.assertEqual(dogrula(BAS + s("T-20261104-01", durum="tamam", sonuc="ef29d3e")), [])
    def test_gecersiz_sahip_durum_id(self):
        h = dogrula(BAS + s("T-1", sahip="Bot", durum="bitti"))
        self.assertEqual(len(h), 3)
    def test_kapali_tekrar_serbest(self): self.assertEqual(dogrula(BAS + s("T-20261104-01", durum="iptal") + s("T-20261104-02")), [])
    def test_gercek_kuyruk(self):
        yol = os.path.join(os.path.dirname(__file__), "..", "TASK_QUEUE.md")
        self.assertEqual(dogrula(open(yol, encoding="utf-8").read()), [])


if __name__ == "__main__":
    unittest.main()
