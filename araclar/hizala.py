"""Seslendirme kaydını metne hizalar: cümle ve kelime zamanları + Whisper ile okuma doğrulaması.

Kullanım:
  python3 araclar/hizala.py ses.wav metin.txt 07_ses_zamanlama.json [--whisper]
metin.txt: her satır bir cümle (05_seslendirme.txt'nin yorum olmayan satırları).

Yöntem:
1. Sessizlikler bulunur (−38 dB, ≥ 0,22 sn); konuşma parçaları en kısa aralıklardan birleştirilerek
   cümle sayısına indirilir (her cümle sonunda doğal bir duraklama varsayılır).
2. Kelime başlangıçları, cümle içinde hece sayısına göre dağıtılır (noktalama duraklarına pay bırakılır).
   Yaklaşıktır; altyazı kelime belirişi için yeterlidir.
3. --whisper: her cümle parçası Whisper-medium ile çözülüp metinle karşılaştırılır (CER).
   CER > %8 olan cümle "yeniden kayıt / telaffuz kontrolü" diye işaretlenir.
"""
import json, os, re, subprocess, sys, tempfile

CACHE = os.path.expanduser("~/.novex_cache")
SHERPA = os.path.join(CACHE, "sherpa-onnx-v1.12.15-linux-x64-shared")
WHISPER = os.path.join(CACHE, "sherpa-onnx-whisper-medium")
VOWELS = "aeıioöuüâîûAEIİOÖUÜ"


def sessizlikler(path, db=-38, d=0.22):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={db}dB:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", o)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout)
    return list(zip(st, en + [dur] * (len(st) - len(en)))), dur


def parcalar(path):
    sil, dur = sessizlikler(path)
    segs, t = [], 0.0
    for a, b in sil:
        if a - t > 0.08: segs.append([t, a])
        t = b
    if dur - t > 0.08: segs.append([t, dur])
    return segs


def heceler(w): return max(1, sum(1 for c in w if c in VOWELS) + (1 if re.search(r"\d", w) else 0))


BIR = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
ON = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def yaziyla(n):
    if n == 0: return "sıfır"
    def uc(x):
        y, r = divmod(x, 100); o, b = divmod(r, 10)
        return " ".join(w for w in [("" if y == 1 else BIR[y]) + (" yüz" if y else ""), ON[o], BIR[b]] if w).strip()
    parts = []
    for val, ad in ((10**9, "milyar"), (10**6, "milyon"), (1000, "bin")):
        q, n = divmod(n, val)
        if q: parts.append(("" if (q == 1 and ad == "bin") else uc(q) + " ") + ad)
    if n: parts.append(uc(n))
    return " ".join(parts).replace("  ", " ").strip()


def sayilari_yaz(s):
    s = re.sub(r"(\d{1,3}(?:\.\d{3})+|\d+)", lambda m: " " + yaziyla(int(m.group(1).replace(".", ""))) + " ", s)
    return re.sub(r"\bkm\b", "kilometre", s)


def norm(s):
    s = sayilari_yaz(s)
    s = s.replace("İ", "i").replace("I", "ı").lower()
    return " ".join(re.sub(r"[^\wçğıöşüâîû ]", " ", s).split())


def cer(a, b):
    a, b = norm(a), norm(b); d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[-1] / max(1, len(a))


def whisper(path, a, b):
    with tempfile.TemporaryDirectory() as td:
        seg = os.path.join(td, "s.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", path, "-ar", "16000",
                        "-ac", "1", seg], check=True)
        env = dict(os.environ, LD_LIBRARY_PATH=os.path.join(SHERPA, "lib"))
        o = subprocess.run([os.path.join(SHERPA, "bin", "sherpa-onnx-offline"),
                            f"--whisper-encoder={WHISPER}/medium-encoder.int8.onnx",
                            f"--whisper-decoder={WHISPER}/medium-decoder.int8.onnx",
                            f"--tokens={WHISPER}/medium-tokens.txt", "--whisper-language=tr",
                            "--whisper-task=transcribe", "--num-threads=2", seg], capture_output=True, text=True, env=env)
        m = re.search(r'"text": "(.*?)"', o.stdout + o.stderr)
        return m.group(1).strip() if m else ""


def main(wav, metin, out, use_whisper=False):
    cumleler = [l.strip().replace("*", "") for l in open(metin, encoding="utf-8") if l.strip() and not l.startswith("#")]
    raw = parcalar(wav)
    uyari = []
    N, M = len(cumleler), len(raw)
    if M >= N:
        # Her cümleye ardışık parçalar atanır; maliyet = (gerçek süre − hece oranlı beklenen süre)²
        hec = [sum(heceler(w) for w in c.split()) for c in cumleler]
        konusma = sum(b - a for a, b in raw); beklenen = [konusma * h / sum(hec) for h in hec]
        INF = float("inf"); dp = [[INF] * (M + 1) for _ in range(N + 1)]; geri = [[0] * (M + 1) for _ in range(N + 1)]
        dp[0][0] = 0
        for i in range(1, N + 1):
            for j in range(i, M - (N - i) + 1):
                for k in range(i - 1, j):
                    if dp[i - 1][k] == INF: continue
                    sure = sum(b - a for a, b in raw[k:j])
                    c = dp[i - 1][k] + (sure - beklenen[i - 1]) ** 2
                    if c < dp[i][j]: dp[i][j], geri[i][j] = c, k
        segs, j = [], M
        for i in range(N, 0, -1):
            k = geri[i][j]; segs.append([raw[k][0], raw[j - 1][1]]); j = k
        segs.reverse()
    else:
        segs = raw
    if len(segs) < len(cumleler):
        uyari.append(f"Konuşma parçası ({len(segs)}) cümle sayısından ({len(cumleler)}) az: cümleler arasında duraklama yok. "
                     "Kayıtta her cümleden sonra yarım saniye durulmalı.")
    sonuc = []
    for k, (c, (a, b)) in enumerate(zip(cumleler, segs), 1):
        kel = c.split(); w = [heceler(x) + (0.6 if x[-1] in ",;:" else 0) for x in kel]
        tot = sum(w); t = a; on = []
        for x, wi in zip(kel, w):
            on.append(round(t, 3)); t += (b - a) * wi / tot
        rec = {"i": k, "metin": c, "konusma": [round(a, 3), round(b, 3)], "kelime_baslangic": on}
        if use_whisper:
            h = whisper(wav, max(0, a - 0.25), b + 0.2); rec["whisper"] = h; rec["cer"] = round(cer(c, h), 3)
            if rec["cer"] > 0.08: uyari.append(f"Cümle {k}: okuma/telaffuz kontrolü (CER {rec['cer']:.0%}) → «{h}»")
        sonuc.append(rec)
    json.dump({"ses": os.path.basename(wav), "cumleler": sonuc, "uyarilar": uyari},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in sonuc:
        print(f"{r['i']:2d} {r['konusma'][0]:6.2f}-{r['konusma'][1]:6.2f}  {('CER %.0f%% ' % (100 * r['cer'])) if 'cer' in r else ''}{r['metin']}")
    for u in uyari: print("UYARI:", u)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(a[0], a[1], a[2], "--whisper" in sys.argv)
