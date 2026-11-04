"""NØVEX Short üretim hattı — tek komut, kaldığı yerden devam eder (her aşama cikti/durum.json'a yazılır; render parçaları tek tek).
Kullanım:  python3 araclar/short_uret.py videolar/<klasör> [--paralel 2] [--parca 4] [--yeniden <aşama>]
Klasör girdileri (ChatGPT/Claude hazırlar): uretim.json, anlatim_performans.json, sahne_plani.json, paket.json, 02_sources.md
Aşamalar: ses → telaffuz → altyazi → render → ses_tasarim → miks → birlestir → qc → kapak → paket
Çıktılar: cikti/ (büyük dosyalar, git dışı) · teslim/ (VIDEO.mp4 hariç metinler + kapak + QC; depoya girer)
"""
import argparse, datetime, glob, hashlib, json, os, re, subprocess, sys, time

DEPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
C = os.path.expanduser("~/.novex_cache")
SH = f"{C}/sherpa-onnx-v1.12.15-linux-x64-shared"
WH = f"{C}/sherpa-onnx-whisper-small.en"
ASAMALAR = ["ses", "telaffuz", "altyazi", "render", "ses_tasarim", "miks", "birlestir", "qc", "kapak", "paket"]
FPS = 30


def run(a, **k):
    r = subprocess.run(a, capture_output=True, text=True, **k)
    if r.returncode: raise RuntimeError(f"komut başarısız: {' '.join(map(str, a[:4]))}…\n{r.stderr[-1500:]}")
    return r


def sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def sure(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).stdout)


# ---------- metin normalleştirme (telaffuz kontrolü için) ----------
BIR = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
ON = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def sayi_yazi(n):
    if n < 20: return BIR[n]
    if n < 100: return ON[n // 10] + ("" if n % 10 == 0 else " " + BIR[n % 10])
    if n < 1000: return BIR[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + sayi_yazi(n % 100))
    for b, ad in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= b: return sayi_yazi(n // b) + " " + ad + ("" if n % b == 0 else " " + sayi_yazi(n % b))
def nrm(s):
    s = s.lower().replace("-", " ")
    s = re.sub(r"\b(1[0-9]|20)(\d\d)\b", lambda m: sayi_yazi(int(m.group(1))) + " " + (sayi_yazi(int(m.group(2))) if m.group(2) != "00" else "hundred"), s)  # yıllar
    s = re.sub(r"\d[\d,]*", lambda m: sayi_yazi(int(m.group(0).replace(",", ""))) if m.group(0).replace(",", "").isdigit() else m.group(0), s)
    s = re.sub(r"[^a-z' ]", " ", s).replace(" and ", " ")
    return [w for w in s.split() if w not in ("and", "the", "a")]
def wer(r, h):
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(len(r), 1)


class Uretim:
    def __init__(self, k, paralel, parca):
        self.k = os.path.abspath(k); self.c = os.path.join(self.k, "cikti"); self.t = os.path.join(self.k, "teslim")
        os.makedirs(self.c, exist_ok=True); os.makedirs(self.t, exist_ok=True)
        self.u = json.load(open(os.path.join(self.k, "uretim.json"), encoding="utf-8"))
        self.dy = os.path.join(self.c, "durum.json")
        self.d = json.load(open(self.dy)) if os.path.exists(self.dy) else {"asamalar": {}, "hatalar": []}
        self.paralel, self.parca = paralel, parca
        # durum.json depodan gelebilir ama büyük dosyalar git dışıdır: "tamam" aşamanın çıktısı yoksa o ve sonrası yeniden yapılır
        kanit = {"ses": f"{self.c}/anlatim/zaman.json", "render": f"{self.c}/parcalar.txt", "ses_tasarim": f"{self.c}/ses/muzik.wav",
                 "miks": f"{self.c}/ses/miks.wav", "birlestir": f"{self.c}/VIDEO.mp4"}
        for a in ASAMALAR:
            if self.bitti(a) and a in kanit and not os.path.exists(kanit[a]):
                print(f"! {a} 'tamam' görünüyor ama çıktısı yok → {a} ve sonrası yeniden", flush=True)
                for b in ASAMALAR[ASAMALAR.index(a):]: self.d["asamalar"].pop(b, None)
                self.kaydet(); break

    def kaydet(self): json.dump(self.d, open(self.dy, "w"), indent=1, ensure_ascii=False)
    def bitti(self, a): return self.d["asamalar"].get(a, {}).get("durum") == "tamam"
    def isaret(self, a, **bilgi):
        self.d["asamalar"][a] = {"durum": "tamam", "zaman": datetime.datetime.now().isoformat(timespec="seconds"), **bilgi}; self.kaydet()
        print(f"✓ {a} {bilgi if bilgi else ''}", flush=True)

    # 1) anlatım
    def ses(self):
        out = os.path.join(self.c, "anlatim")
        run([sys.executable, f"{DEPO}/araclar/anlatim_ifade.py", f"{self.k}/anlatim_performans.json", self.u.get("ses_motoru", "piper-ljspeech"), out,
             str(self.u.get("hiz_carpani", 1.0))])
        run([sys.executable, f"{DEPO}/araclar/ses_isle.py", f"{out}/anlatim.wav", f"{self.c}/ses/"])
        z = json.load(open(f"{out}/zaman.json")); self.isaret("ses", sure=round(z[-1]["son"], 2), cumle=len(z))

    # 2) telaffuz (Whisper small.en, cümle başına)
    def telaffuz(self):
        z = json.load(open(f"{self.c}/anlatim/zaman.json")); wav = f"{self.c}/anlatim/anlatim.wav"; env = dict(os.environ, LD_LIBRARY_PATH=f"{SH}/lib")
        sat, R, Hh = [], [], []
        for s in z:
            run(["ffmpeg", "-v", "error", "-y", "-ss", str(max(0, s["bas"] - 0.1)), "-to", str(s["son"] + 0.15), "-i", wav, "-ar", "16000", "-ac", "1", f"{self.c}/_tlf.wav"])   # klasöre özel: eşzamanlı üretimler çakışmasın
            o = subprocess.run([f"{SH}/bin/sherpa-onnx-offline", f"--whisper-encoder={WH}/small.en-encoder.int8.onnx",
                                f"--whisper-decoder={WH}/small.en-decoder.int8.onnx", f"--tokens={WH}/small.en-tokens.txt", "--num-threads=2", f"{self.c}/_tlf.wav"],
                               capture_output=True, text=True, env=env)
            h = (re.findall(r'"text":\s*"(.*?)"', o.stdout + o.stderr) or [""])[-1].strip()
            r_, h_ = nrm(s["metin"]), nrm(h); R += r_; Hh += h_; w = wer(r_, h_)
            sat.append({"i": s["i"], "metin": s["metin"], "duyulan": h, "wer": round(100 * w, 1)})
        top = round(100 * wer(R, Hh), 1)
        json.dump({"wer_toplam": top, "cumleler": sat}, open(f"{self.c}/telaffuz.json", "w"), indent=1, ensure_ascii=False)
        self.isaret("telaffuz", wer=top, sorunlu=[x["i"] for x in sat if x["wer"] > 0])

    # 3) altyazı
    def altyazi(self):
        z = json.load(open(f"{self.c}/anlatim/zaman.json"))
        def tc(x): return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round((x % 1) * 1000)) % 1000:03d}"
        srt = "\n".join(f"{o['i']}\n{tc(o['bas'])} --> {tc(o['son'])}\n{o.get('altyazi', o['metin'])}\n" for o in z)
        open(f"{self.t}/SUBTITLES.srt", "w", encoding="utf-8").write(srt); self.isaret("altyazi", satir=len(z))

    # 4) render (parçalı, devam edebilir)
    def render(self):
        plan = f"{self.k}/sahne_plani.json"; z = f"{self.c}/anlatim/zaman.json"; srt = f"{self.t}/SUBTITLES.srt"
        zz = json.load(open(z)); T = zz[-1]["son"] + json.load(open(plan)).get("kapanis_sn", 2.0); N = round(T * FPS)
        sinir = [round(N * i / self.parca) / FPS for i in range(self.parca + 1)]
        isler = [(i, sinir[i], sinir[i + 1], f"{self.c}/parca_{i:02d}.mp4") for i in range(self.parca)]
        bekleyen = [x for x in isler if not os.path.exists(x[3])]
        calisan = []
        while bekleyen or calisan:
            while bekleyen and len(calisan) < self.paralel:
                i, a, b, f = bekleyen.pop(0)
                p = subprocess.Popen([sys.executable, f"{DEPO}/motor/sahne_v1/sahne.py", "video", plan, z, f, "--srt", srt, "--bas", str(a), "--son", str(b)],
                                     stdout=open(f"{self.c}/parca_{i:02d}.log", "w"), stderr=subprocess.STDOUT); calisan.append((p, i, a, b, f))
            time.sleep(2)
            for x in list(calisan):
                if x[0].poll() is not None:
                    calisan.remove(x)
                    if x[0].returncode != 0:
                        self.d["hatalar"].append(f"render parça {x[1]} rc={x[0].returncode}"); self.kaydet()
                        raise RuntimeError(f"render parça {x[1]} başarısız — tekrar çalıştırınca yalnız bu parça yeniden üretilir")
        open(f"{self.c}/parcalar.txt", "w").write("".join(f"file '{x[3]}'\n" for x in isler))
        self.isaret("render", sure=round(T, 3), kare=N, parca=self.parca)

    # 5) ses tasarımı
    def ses_tasarim(self):
        run([sys.executable, f"{DEPO}/araclar/ses_tasarim.py", f"{self.c}/anlatim/zaman.json", f"{self.c}/ses",
             "--ruh", self.u.get("ruh", "merak"), "--ortam", self.u.get("ortam", "yok"), "--kapanis", str(json.load(open(f"{self.k}/sahne_plani.json")).get("kapanis_sn", 2.0))])
        self.isaret("ses_tasarim", ruh=self.u.get("ruh"), ortam=self.u.get("ortam"))

    # 6) miks (konuşma/fon ≥ 12 dB ölçümüyle)
    def miks(self):
        s = f"{self.c}/ses"; T = self.d["asamalar"]["render"]["sure"]; z = json.load(open(f"{self.c}/anlatim/zaman.json"))
        run(["ffmpeg", "-v", "error", "-y", "-i", f"{s}/ses.wav", "-af", f"apad=whole_dur={T}", "-c:a", "pcm_s24le", f"{s}/ses_p.wav"]); os.replace(f"{s}/ses_p.wav", f"{s}/ses.wav")
        json.dump({"cumleler": [{"i": c["i"], "konusma": [c["bas"], c["son"]]} for c in z]}, open(f"{s}/zamanlama.json", "w"))
        json.dump({"ses": "ses.wav", "muzik": "muzik.wav", "efekt": "efekt.wav", "ses_db": 0, "muzik_db": self.u.get("muzik_db", -9), "efekt_db": self.u.get("efekt_db", -8),
                   "ducking_muzik": {"esik": 0.02, "oran": 10}, "ducking_efekt": {"esik": 0.015, "oran": 5}, "hedef_lufs": -14, "true_peak": -1.5,
                   "zamanlama": "zamanlama.json", "cikti": "miks.wav"}, open(f"{s}/miks.json", "w"))
        run([sys.executable, f"{DEPO}/araclar/miks.py", f"{s}/miks.json"]); r = json.load(open(f"{s}/miks.wav.rapor.json"))
        self.isaret("miks", lufs_tp=r["lufs_tp"], ses_fon_min=min(x["ses_fon_farki_db"] for x in r["ses_fon"]), uyarilar=r.get("uyarilar", []))

    # 7) birleştir (sesten kısa kesmez: süre = video kare sayısı)
    def birlestir(self):
        N = self.d["asamalar"]["render"]["kare"]; D = f"{N / FPS:.3f}"; v = f"{self.c}/VIDEO.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{self.c}/parcalar.txt", "-i", f"{self.c}/ses/miks.wav", "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", D, "-movflags", "+faststart", v])
        self.isaret("birlestir", dosya=v, mb=round(os.path.getsize(v) / 1e6, 1))

    # 8) QC
    def qc(self):
        import numpy as np
        v = f"{self.c}/VIDEO.mp4"; lis = f"{self.k}/ses/LISANS.txt"
        q = subprocess.run([sys.executable, f"{DEPO}/araclar/qc.py", v, f"{self.c}/qc_rapor.md"] + (["--lisans", lis] if os.path.exists(lis) else []), capture_output=True, text=True).stdout
        bd = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-vf", "blackdetect=d=0.2:pix_th=0.05,freezedetect=n=0.001:d=0.8", "-an", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
        siyah = len(re.findall("black_start", bd)); donuk = len(re.findall("freeze_start", bd))
        def oku(f): return np.frombuffer(run(["ffmpeg", "-v", "error", "-i", f, "-t", "12", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], text=False).stdout if False else
                                         subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-t", "12", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
        a, b = oku(v), oku(f"{self.c}/ses/ses.wav"); n = min(len(a), len(b)); A = np.fft.rfft(a[:n], 2 * n); B = np.fft.rfft(b[:n], 2 * n)
        cc = np.fft.irfft(A * np.conj(B)); k = int(np.argmax(cc)); k = k if k < n else k - 2 * n; kayma = round(k / 8 * 1, 1)
        teknik = [l for l in q.splitlines() if l.startswith("|") and ("✅" in l or "❌" in l) and "lisans" not in l.lower()]
        gecen = sum("✅" in l for l in teknik)
        lis_ok = any("lisans" in l.lower() and "✅" in l for l in q.splitlines())
        self.isaret("qc", teknik=f"{gecen}/{len(teknik)}", siyah=siyah, donuk=donuk, senkron_ms=kayma, lisans="geçti" if lis_ok else "GEÇMEDİ",
                    tablo=q.strip().splitlines()[-14:])

    def kapak(self):
        run([sys.executable, f"{DEPO}/motor/sahne_v1/sahne.py", "kapak", f"{self.k}/sahne_plani.json", f"{self.c}/anlatim/zaman.json", f"{self.t}/THUMBNAIL.jpg"])
        self.isaret("kapak", dosya="teslim/THUMBNAIL.jpg")

    # 10) yayın paketi (YouTube + Instagram + TikTok) + QC raporu
    def paket(self):
        p = json.load(open(f"{self.k}/paket.json", encoding="utf-8")); t = self.t; A = self.d["asamalar"]
        open(f"{t}/TITLE.txt", "w").write(f"MAIN: {p['baslik']}\n" + "".join(f"ALT {i+1}: {x}\n" for i, x in enumerate(p.get("alternatif", []))))
        open(f"{t}/DESCRIPTION.txt", "w").write(p["aciklama"].strip() + "\n\n" + " ".join(p["hashtag"]) + "\n")
        open(f"{t}/TAGS.txt", "w").write(", ".join(p["etiketler"]) + "\n"); open(f"{t}/HASHTAGS.txt", "w").write(" ".join(p["hashtag"]) + "\n")
        open(f"{t}/PINNED_COMMENT.txt", "w").write(p["sabit_yorum"].strip() + "\n")
        plan = json.load(open(f"{self.k}/sahne_plani.json", encoding="utf-8"))
        KOKEN_EN = {"fotograf": "Photograph", "arsiv": "Archive image", "ai": "AI-generated illustration (not a real photograph)", "prosedurel": "Procedural render"}
        gorseller = [f"- Scene {s_['cumle']}: {KOKEN_EN.get(s_.get('koken'), s_.get('koken'))} — {s_.get('kaynak', '?')} — license: {s_.get('lisans', '?')}\n"
                     for s_ in plan["sahneler"] if s_.get("tur") == "foto"]
        gorsel_blok = "\nVISUALS\n" + ("".join(gorseller) if gorseller else "") + \
            "- All other scenes: original 3D renders made in code (sahne_v1; Earth texture from Natural Earth, public domain). No stock footage.\n"
        open(f"{t}/SOURCES.txt", "w").write("".join(f"{i+1}. {s}\n" for i, s in enumerate(p["kaynaklar"])) + f"\nMode: {p.get('mod','REALITY')}\nFull claim list: 02_sources.md\n" + gorsel_blok)
        perf = json.load(open(f"{self.k}/anlatim_performans.json", encoding="utf-8"))   # tam seslendirme metni (TTS'e giden fonetik yazım değil, okunan metin)
        open(f"{t}/NARRATION.txt", "w").write("".join(f"{i+1}. [{c.get('duygu', '')}] " + " ".join(p_['metin'] for p_ in c["parcalar"]) + "\n" for i, c in enumerate(perf["cumleler"])))
        ig, tk = p["instagram"], p["tiktok"]
        open(f"{t}/INSTAGRAM_REELS.txt", "w").write(f"COVER TEXT: {ig['kapak']}\nCAPTION:\n{ig['aciklama'].strip()}\n\n{' '.join(ig['hashtag'])}\n\nNOTE: upload the clean VIDEO.mp4 (no watermark); choose cover frame with the text above.\n")
        open(f"{t}/TIKTOK.txt", "w").write(f"ON-SCREEN TITLE: {tk['kapak']}\nCAPTION:\n{tk['aciklama'].strip()} {' '.join(tk['hashtag'])}\n\nNOTE: upload the clean VIDEO.mp4 (no watermark).\n")
        open(f"{t}/YOUTUBE.txt", "w").write(f"TITLE: {p['baslik']}\n\nDESCRIPTION:\n{open(f'{t}/DESCRIPTION.txt').read()}\nTAGS: {', '.join(p['etiketler'])}\n\nPINNED COMMENT:\n{p['sabit_yorum']}\n")
        tl = subprocess.run([sys.executable, os.path.expanduser("~/.claude/skills/yt-package/title.py"), "--title", p["baslik"], "--thumb", p.get("kapak_metni", "")],
                            capture_output=True, text=True).stdout if os.path.exists(os.path.expanduser("~/.claude/skills/yt-package/title.py")) else "(yt-package/title.py bu oturumda yok)"
        v = f"{self.c}/VIDEO.mp4"; tlf = json.load(open(f"{self.c}/telaffuz.json")); q = A["qc"]; m = A["miks"]
        rap = [f"NØVEX QC REPORT — {p['baslik']}", f"Slot: {self.u.get('tarih')} {self.u.get('slot')} (Europe/Istanbul) · rendered {A['birlestir']['zaman']}",
               f"VIDEO.mp4 {A['birlestir']['mb']} MB sha256 {sha(v)}", "",
               f"VIDEO   technical checks {q['teknik']} · black segments {q['siyah']} · frozen segments {q['donuk']} · {A['render']['kare']} frames / {A['render']['sure']} s",
               f"AUDIO   loudness/true peak {m['lufs_tp']} · min speech-over-background {m['ses_fon_min']} dB (need >= 12) · warnings {m['uyarilar']}",
               f"SYNC    narration vs MP4 offset {q['senkron_ms']} ms",
               f"VOICE   {self.u.get('ses_motoru')} · Whisper small.en WER {tlf['wer_toplam']}% · flagged sentences {[x['i'] for x in tlf['cumleler'] if x['wer'] > 0]}",
               *[f"        s{x['i']}: heard \"{x['duyulan']}\"" for x in tlf["cumleler"] if x["wer"] > 0],
               f"SUBS    SUBTITLES.srt, {A['altyazi']['satir']} cues, timing from synthesis (exact); burned-in inside safe area",
               f"LICENCE voice: {q['lisans']} (see ses/LISANS.txt) · visuals: own code + Natural Earth (public domain) · fonts: OFL/Apache · music/SFX: own synthesis",
               "HUMAN   listening/viewing by Emir: PENDING (Claude cannot listen)", "", "TITLE LINT (yt-package/title.py):", tl.strip(), "",
               "qc.py table:", *q["tablo"]]
        open(f"{t}/QC_REPORT.txt", "w").write("\n".join(rap) + "\n")
        self.isaret("paket", dosyalar=sorted(os.listdir(t)))

    def calistir(self, yeniden=None):
        if yeniden:
            i = ASAMALAR.index(yeniden)
            for a in ASAMALAR[i:]: self.d["asamalar"].pop(a, None)
            if yeniden in ("ses", "render"): [os.remove(f) for f in glob.glob(f"{self.c}/parca_*.mp4")]
            self.kaydet()
        for a in ASAMALAR:
            if self.bitti(a): print(f"· {a} (önceden tamam)"); continue
            try: getattr(self, a)()
            except Exception as e:
                self.d["hatalar"].append(f"{a}: {str(e)[:400]}"); self.kaydet(); print(f"✗ {a}: {e}", file=sys.stderr); sys.exit(1)
        print("ÜRETİM TAMAM →", self.c)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("klasor"); ap.add_argument("--paralel", type=int, default=2); ap.add_argument("--parca", type=int, default=4)
    ap.add_argument("--yeniden", choices=ASAMALAR); a = ap.parse_args()
    Uretim(a.klasor, a.paralel, a.parca).calistir(a.yeniden)
