"""NØVEX teknik kalite kontrolü. Kullanım: python3 qc.py video.mp4 [rapor.md] [--lisans ses/LISANS.txt]
NØVEX standardını denetler ve kontrol karesi sayfası üretir (video_qc.jpg)."""
import json, subprocess, sys, re, os

v = sys.argv[1]
def run(*a): return subprocess.run(a, capture_output=True, text=True)
pr = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", v).stdout)
vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
a = au[0] if au else {}
dur = float(pr["format"]["duration"])
dec = run("ffmpeg", "-v", "error", "-i", v, "-f", "null", "-").stderr.strip()
lufs = None
if au:
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", run("ffmpeg", "-hide_banner", "-i", v, "-af", "ebur128", "-f", "null", "-").stderr.split("Summary:")[-1])
    lufs = float(m.group(1)) if m else None

checks = [
    ("Çözünürlük 1080×1920", f'{vs["width"]}×{vs["height"]}', vs["width"] == 1080 and vs["height"] == 1920),
    ("Kare hızı 30", vs["r_frame_rate"], vs["r_frame_rate"] == "30/1"),
    ("Video codec H.264", f'{vs["codec_name"]} {vs.get("profile", "")}', vs["codec_name"] == "h264"),
    ("Piksel formatı yuv420p", vs["pix_fmt"], vs["pix_fmt"] == "yuv420p"),
    ("Rec.709 / SDR", f'{vs.get("color_primaries", "?")}/{vs.get("color_transfer", "?")}/{vs.get("color_space", "?")}',
     vs.get("color_primaries") == "bt709" and vs.get("color_transfer") == "bt709" and vs.get("color_space") == "bt709"),
    ("Ses AAC 48 kHz", f'{a.get("codec_name", "yok")} {a.get("sample_rate", "")}', a.get("codec_name") == "aac" and a.get("sample_rate") == "48000"),
    ("Süre (Shorts ≤ 60 sn)", f"{dur:.3f} sn", 0 < dur <= 60),
    ("Kare sayısı", vs.get("nb_frames", "?"), True),
    ("Tam çözümleme", "hata yok" if not dec else dec[:120], not dec),
    ("Ses yüksekliği ≈ −14 LUFS", f"{lufs} LUFS" if lufs is not None else "yok", lufs is not None and -16 <= lufs <= -12),
]
# Ses lisansı: --lisans <ses/LISANS.txt> verilirse yayın uygunluğu da denetlenir
if "--lisans" in sys.argv:
    lp = sys.argv[sys.argv.index("--lisans") + 1]
    lt = open(lp, encoding="utf-8").read() if os.path.exists(lp) else ""
    kaynak = (re.search(r"kaynak:\s*(.+)", lt) or [None, "yok"])[1].strip()
    ok_lic = bool(re.search(r"yayin_uygun:\s*evet", lt))
    checks.append(("Ses lisansı yayına uygun", kaynak, ok_lic))
lines = ["| Kontrol | Değer | Sonuç |", "|---|---|---|"] + [f"| {n} | {val} | {'✅' if ok else '❌'} |" for n, val, ok in checks]
report = "\n".join(lines)
print(report)

# kontrol kareleri: başlangıç, orta, son + her 3 sn
qc = os.path.splitext(v)[0] + "_qc.jpg"
ts = [0.2] + [x for x in range(3, int(dur), 3)] + [max(0, dur - 0.3)]
run("ffmpeg", "-y", "-v", "error", "-i", v, "-vf",
    f"select='{'+'.join(f'between(t,{t},{t}+0.034)' for t in ts)}',scale=216:384,tile={len(ts)}x1",
    "-frames:v", "1", "-fps_mode", "vfr", qc)
rap = [a for a in sys.argv[2:] if a.endswith(".md")]
if rap: open(rap[0], "w", encoding="utf-8").write(report + "\n")
sys.exit(0 if all(ok for _, _, ok in checks) else 1)
