"""araclar/teslim_dogrula.py testleri: küçük ama gerçek bir MP4 ile sahte teslim klasörü kurar, her kuralın yakalandığını doğrular."""
import json, os, shutil, subprocess, sys, tempfile, time, unittest

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "araclar"))
import teslim_dogrula as td  # noqa: E402

_MP4 = None


def ornek_mp4():
    """2 sn'lik 1080×1920 H.264 High + AAC 48 kHz (bir kez üretilir)."""
    global _MP4
    if _MP4: return _MP4
    _MP4 = os.path.join(tempfile.mkdtemp(), "v.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=20",
                    "-f", "lavfi", "-i", "sine=f=440:r=48000:d=20", "-c:v", "libx264", "-profile:v", "high", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:a", "aac", "-ar", "48000", "-shortest", _MP4], check=True)
    return _MP4


def klasor_kur(d, **deg):
    os.makedirs(os.path.join(d, "cikti"), exist_ok=True); os.makedirs(os.path.join(d, "teslim"), exist_ok=True); os.makedirs(os.path.join(d, "ses"), exist_ok=True)
    w = lambda ad, s: open(os.path.join(d, ad), "w", encoding="utf-8").write(s if isinstance(s, str) else json.dumps(s))
    son = deg.get("son", "And which planet should we explore next: Mars, or Mercury?")
    w("uretim.json", {"ses_motoru": deg.get("motor", "piper-norman")})
    w("anlatim_performans.json", {"cumleler": [{"parcalar": [{"metin": "Venus spins backwards."}]}, {"parcalar": [{"metin": son}]}]})
    sh = deg.get("sahneler", [{"cumle": 1, "tur": "gezegen"}, {"cumle": 2, "tur": "soru"}])
    w("sahne_plani.json", {"sahneler": sh, "vurgu_kelimeler": ["Venus"]})
    w("ses/LISANS.txt", deg.get("lisans", "motor: piper en_US-norman-medium\nemir_ses_onayi: bekliyor\nyayin_uygun: hayir\n"))
    for ad in td.PAKET: w("teslim/" + ad, "x")
    w("teslim/PINNED_COMMENT.txt", deg.get("pinned", "Mars or Mercury — which should NØVEX explore next?"))
    w("teslim/SUBTITLES.srt", f"1\n00:00:00,000 --> 00:00:01,000\nVenus spins backwards.\n\n2\n00:00:01,100 --> 00:00:01,900\n{son}\n")
    w("cikti/durum.json", {"asamalar": {s: {"durum": "tamam", **({"teknik": "10/10"} if s == "qc" else {})} for s in td.ASAMALAR}})
    time.sleep(0.01)
    shutil.copy(ornek_mp4(), os.path.join(d, "cikti/VIDEO.mp4"))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=1080x1920", "-frames:v", "1",
                    os.path.join(d, "teslim/THUMBNAIL.jpg")], check=True)


class TestTeslimDogrula(unittest.TestCase):
    def setUp(self): self.d = tempfile.mkdtemp()
    def tearDown(self): shutil.rmtree(self.d, ignore_errors=True)

    def test_saglam_klasor_hatasiz_ama_onaysiz_yayina_hazir_degil(self):
        klasor_kur(self.d); r = td.dogrula(self.d)
        self.assertEqual(r["hatalar"], []); self.assertFalse(r["bilgi"]["yayina_hazir"])

    def test_lisans_evet_ise_yayina_hazir(self):
        klasor_kur(self.d, lisans="motor: piper en_US-norman-medium\nemir_ses_onayi: evet\nyayin_uygun: evet\n")
        self.assertTrue(td.dogrula(self.d)["bilgi"]["yayina_hazir"])

    def test_not_satirindaki_evet_sayilmaz(self):
        klasor_kur(self.d, lisans="motor: piper en_US-norman-medium\nyayin_uygun: hayir\nnot: onaydan sonra yayin_uygun: evet yazılır\n")
        self.assertFalse(td.dogrula(self.d)["bilgi"]["yayina_hazir"])

    def test_mp4_yoksa_hata(self):
        klasor_kur(self.d); os.remove(os.path.join(self.d, "cikti/VIDEO.mp4"))
        self.assertTrue(any("gerçek MP4" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_plan_mp4ten_yeniyse_hata(self):
        klasor_kur(self.d); p = os.path.join(self.d, "sahne_plani.json"); t = time.time() + 30; os.utime(p, (t, t))
        self.assertTrue(any("ESKİ" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_katilim_sorusu_zorunlu(self):
        klasor_kur(self.d, son="Could you survive a day on Venus?")
        self.assertTrue(any("sırada ne" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_jenerik_abone_ol_yasak(self):
        klasor_kur(self.d, son="Subscribe for more and tell us what we should explore next?")
        self.assertTrue(td.dogrula(self.d)["hatalar"])
        klasor_kur(self.d, pinned="Like and subscribe!")
        self.assertTrue(any("sabitlenmiş" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_soru_sahnesi_zorunlu(self):
        klasor_kur(self.d, sahneler=[{"cumle": 1, "tur": "gezegen"}, {"cumle": 2, "tur": "gezegen"}])
        self.assertTrue(any("`soru`" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_duz_slayt_videosu_reddedilir(self):
        klasor_kur(self.d, sahneler=[{"cumle": 1, "tur": "baslik"}, {"cumle": 1, "tur": "harita"}, {"cumle": 1, "tur": "harita"},
                                     {"cumle": 1, "tur": "harita"}, {"cumle": 2, "tur": "soru"}])
        h = td.dogrula(self.d)["hatalar"]
        self.assertTrue(any("düz slayt" in x for x in h)); self.assertTrue(any("harita sahnesi fazla" in x for x in h))

    def test_lisans_baska_sesi_kaydediyorsa_hata(self):
        klasor_kur(self.d, lisans="motor: piper en_US-ljspeech-high\nyayin_uygun: hayir\n")
        self.assertTrue(any("başka bir sesi" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_eksik_paket_dosyasi(self):
        klasor_kur(self.d); os.remove(os.path.join(self.d, "teslim/TIKTOK.txt"))
        self.assertTrue(any("TIKTOK" in h for h in td.dogrula(self.d)["hatalar"]))

    def test_bozuk_cozunurluk(self):
        klasor_kur(self.d)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", ornek_mp4(), "-vf", "scale=720:1280", "-c:v", "libx264", "-profile:v", "high",
                        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-c:a", "copy", os.path.join(self.d, "cikti/VIDEO.mp4")], check=True)
        self.assertTrue(any("çözünürlük" in h for h in td.dogrula(self.d)["hatalar"]))


if __name__ == "__main__":
    unittest.main()
