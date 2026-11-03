"""V3: render.py sahnelerini seslendirmeye göre kurulmuş zaman çizelgesiyle (parça parça doğrusal
zaman eşlemesi) yeniden render eder. Animasyonlar ve altyazılar cümle sürelerine orantılı uzar.
Kullanım: python3 render_v3.py zaman_cizelgesi.json <sahne_no 1..6> out.mp4
"""
import json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # noqa: E402

tl = json.load(open(sys.argv[1], encoding="utf-8"))
OLD, NEW = np.array(tl["old_knots"]), np.array(tl["new_knots"])
DUR = tl["duration"]
def to_old(t_new): return float(np.interp(t_new, NEW, OLD))
def to_new(t_old): return float(np.interp(t_old, OLD, NEW))

# ---- altyazı: her kelime, seslendirmede söylendiği anda belirir (Glow-TTS harf sürelerinden) ----
WORD_LEAD = 0.06   # kelime, sesten bir tık önce görünsün
_segs = tl["segments"]
_word_t = []       # her altyazı satırı için, ekrandaki kelime başına ESKİ zamanda görünme anı
for (a, b, lines, hl), sg in zip(R.CAPS, _segs):
    cap_words = [w for l in lines for w in l.split()]
    on = sg["word_onsets"]
    if len(cap_words) == len(on):
        idx = list(range(len(on)))
    else:   # "1.200" = "bin iki yüz": ekrandaki rakam ilk sözcükle, sonrakiler kendi sözcükleriyle
        spoken = sg["text"].replace(",", "").split()
        idx, j = [], 0
        for w in cap_words:
            if any(ch.isdigit() for ch in w):
                idx.append(j); j += 3 if w == "1.200" else 2
            else:
                while j < len(spoken) and spoken[j].strip(".:?!").lower() != w.strip(".:?!,").lower(): j += 1
                idx.append(min(j, len(on) - 1)); j += 1
    _word_t.append([to_old(max(0.0, on[i] - WORD_LEAD)) for i in idx])

def captions_sync(tx, t):
    for (a, b, lines, hl), wt in zip(R.CAPS, _word_t):
        if not (a - 0.01 <= t < b): continue
        fin = 1 - R.seg(t, b - 0.14, b - 0.01) if b < 29.9 else 1.0
        size = 68
        while size > 50 and max(R.font("Inter-Black.otf", size).getlength(l) for l in lines) > R.SAFE_W: size -= 2
        f = R.font("Inter-Black.otf", size); sp = f.getlength(" ")
        y0 = 1300 - (len(lines) - 1) * 44; k = 0
        for li, line in enumerate(lines):
            ws = line.split(); widths = [f.getlength(w) for w in ws]
            x = R.W / 2 - (sum(widths) + sp * (len(ws) - 1)) / 2; y = y0 + li * 88
            for w, ww in zip(ws, widths):
                tw = max(a, wt[k])
                dur = max(0.08, to_old(to_new(tw) + 0.16) - tw)       # ~0,16 sn (gerçek zaman) belirme
                ap = R.ease_out(R.seg(t, tw, tw + dur)) * fin
                dy = (1 - R.ease_out(R.seg(t, tw, tw + dur * 1.25))) * 16
                colr = (255, 255, 255)
                if w in hl:
                    colr = R.to_rgb255(R.RED * 0.9 + 0.1) if (w in R.WARN and a >= 20) else R.to_rgb255(R.ELECTRIC * 0.85 + 0.15)
                tx.text((x, y + dy), w, f, colr, ap, anchor="ls")
                x += ww + sp; k += 1

R.captions = captions_sync

# sahne sınırları yeni zamanda, kare sınırına yuvarlanmış
bounds_old = [0.0, 3.0, 8.0, 14.0, 20.0, 26.0, 30.0]
bounds = [round(to_new(b) * R.FPS) for b in bounds_old]
bounds[-1] = int(np.ceil(DUR * R.FPS))

if __name__ == "__main__":
    k = int(sys.argv[2]); out = sys.argv[3]
    f0, f1 = bounds[k - 1], bounds[k]
    tmp = out[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{R.W}x{R.H}", "-r", str(R.FPS), "-i", "-",
                          "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-color_range", "tv", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                          "-pix_fmt", "yuv420p", "-r", str(R.FPS), "-movflags", "+faststart", tmp],
                         stdin=subprocess.PIPE)
    prev = None
    for fi in range(f0, f1):
        t_old = min(to_old(fi / R.FPS), 29.999)
        im = R.frame(t_old, prev); prev = im
        p.stdin.write(R.to_u8(im).tobytes())
        if (fi - f0) % 30 == 0: print(f"s{k}", fi, f1, flush=True)
    p.stdin.close(); rc = p.wait()
    if rc == 0: os.replace(tmp, out)
    sys.exit(rc)
