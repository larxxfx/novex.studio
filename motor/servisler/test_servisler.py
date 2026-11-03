"""Adaptör ve karar motoru testleri. Çalıştırma (depo kökünde): python3 -m unittest motor/servisler/test_servisler.py -v
Ağ kullanmaz; hiçbir gerçek API çağrısı yapılmaz."""
import unittest
from motor.servisler.temel import Is, Yapilandirilmadi, HarcamaKilidi, EntegrasyonYok, GeciciHata, ServisHatasi, Sonuc
from motor.servisler.adaptorler import KlingAdaptor, tum_adaptorler
from motor.servisler.karar import karar_ver

MEVCUT = ["idle", "run", "jump"]


class Adaptorler(unittest.TestCase):
    def test_anahtarsiz_yapilandirilmadi(self):
        with self.assertRaises(Yapilandirilmadi):
            KlingAdaptor(ortam={}).uret(Is(tur="image_to_video", sure_sn=5))

    def test_harcama_kilidi_onaysiz(self):
        with self.assertRaises(HarcamaKilidi):
            KlingAdaptor(ortam={"KLING_API_KEY": "x"}).uret(Is(tur="image_to_video", sure_sn=5))

    def test_harcama_kilidi_sinir(self):
        o = {"KLING_API_KEY": "x", "NOVEX_HARCAMA_ONAYI": "evet", "NOVEX_IS_BASINA_MAKS_USD": "0.10"}
        with self.assertRaises(HarcamaKilidi):
            KlingAdaptor(ortam=o).uret(Is(tur="image_to_video", sure_sn=5))  # ~$0.375 > $0.10

    def test_dogrulanmamis_entegrasyon_sahte_basari_donmez(self):
        o = {"KLING_API_KEY": "x", "NOVEX_HARCAMA_ONAYI": "evet", "NOVEX_IS_BASINA_MAKS_USD": "1"}
        with self.assertRaises(EntegrasyonYok):
            KlingAdaptor(ortam=o).uret(Is(tur="image_to_video", sure_sn=5))

    def test_yeniden_deneme_ustel_bekleme(self):
        bekle = []
        class Gecici(KlingAdaptor):
            n = 0
            def _gonder(self, is_, anahtar):
                Gecici.n += 1
                if Gecici.n < 3: raise GeciciHata("429")
                return Sonuc("tamam", ["a.mp4"], 0.3, self.ad)
        o = {"KLING_API_KEY": "x", "NOVEX_HARCAMA_ONAYI": "evet", "NOVEX_IS_BASINA_MAKS_USD": "1"}
        r = Gecici(ortam=o, bekleme=bekle.append).uret(Is(tur="image_to_video", sure_sn=5))
        self.assertEqual(r.durum, "tamam"); self.assertEqual(bekle, [2.0, 4.0])
        class Hep(KlingAdaptor):
            def _gonder(self, is_, anahtar): raise GeciciHata("503")
        with self.assertRaises(ServisHatasi):
            Hep(ortam=o, bekleme=lambda s: None).uret(Is(tur="image_to_video", sure_sn=5))

    def test_anahtar_repr_da_gizli(self):
        self.assertNotIn("gizli123", repr(KlingAdaptor(ortam={"KLING_API_KEY": "gizli123"})))


class Karar(unittest.TestCase):
    def test_basit_sahne_yerel_ve_ucretsiz(self):
        r = karar_ver({"hareketler": ["idle", "run"], "mevcut_hareketler": MEVCUT, "kamera": "takip", "sure_sn": 5}, tum_adaptorler(ortam={}))
        self.assertEqual((r["yontem"], r["tahmini_usd"]), ("yerel", 0.0))

    def test_eksik_hareket_servis_yoksa_yerel_yedek_ve_uyari(self):
        r = karar_ver({"hareketler": ["wave"], "mevcut_hareketler": MEVCUT, "kamera": "sabit", "sure_sn": 4, "tekrar_kullanim": 5},
                      tum_adaptorler(ortam={}))
        self.assertEqual(r["yontem"], "yerel_yedek"); self.assertEqual(r["hareket_yerine"], {"wave": "idle"})
        self.assertTrue(any("yeni_kare" in u for u in r["uyari"]))

    def test_eksik_hareket_tekrar_kullanilacaksa_kare_uretimi_tercih(self):
        r = karar_ver({"hareketler": ["wave"], "mevcut_hareketler": MEVCUT, "kamera": "sabit", "sure_sn": 4, "tekrar_kullanim": 5},
                      tum_adaptorler(ortam={"OPENAI_API_KEY": "x", "KLING_API_KEY": "y"}))
        self.assertEqual(r["yontem"], "yeni_kare"); self.assertTrue(r["onay_gerekli"])

    def test_sinematik_kamera_higgsfield_onerilir(self):
        r = karar_ver({"hareketler": ["idle"], "mevcut_hareketler": MEVCUT, "kamera": "orbit", "sure_sn": 5},
                      tum_adaptorler(ortam={"HIGGSFIELD_API_KEY": "x"}))
        self.assertEqual(r["yontem"], "higgsfield")

    def test_karmasik_beden_kling(self):
        r = karar_ver({"hareketler": ["idle"], "mevcut_hareketler": MEVCUT, "kamera": "sabit", "karmasik_beden": True, "sure_sn": 5},
                      tum_adaptorler(ortam={"KLING_API_KEY": "x"}))
        self.assertEqual(r["yontem"], "kling"); self.assertAlmostEqual(r["tahmini_usd"], 0.375)


if __name__ == "__main__":
    unittest.main()
