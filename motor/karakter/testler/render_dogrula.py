"""Render edilmiş karakter videosunun doğrulaması (gerçek MP4 üzerinde).
Kullanım: python3 motor/karakter/testler/render_dogrula.py <cikti_klasoru>   (karakter_render.py çıktısı)

Kontroller:
  1. MP4 özellikleri (1080×1920, 30/1, kare sayısı = olaylar.json'daki kare sayısı)
  2. Siyah kare yok; hareket bölümünde donmuş kare yok (ardışık kare farkı > eşik)
  3. Kare kaydı: idle → run → jump → idle sırası ve jump'ın next=idle ile bitmesi
  4. Ses-görüntü senkronu: her ses olayının MP4 sesindeki başlangıcı, olayın karesine ±1 kare (33 ms) içinde
"""
import json, subprocess, sys
import numpy as np

d = sys.argv[1]
v = f"{d}/video.mp4"
olay = json.load(open(f"{d}/olaylar.json"))
fps = olay["fps"]
sonuc = []
def k(ad, ok, ayr=""): sonuc.append(ok); print(("✓" if ok else "✗"), ad, ayr)

pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-of", "json", v], capture_output=True, text=True).stdout)
vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
k("1080×1920 · 30/1", (vs["width"], vs["height"], vs["r_frame_rate"]) == (1080, 1920, "30/1"))
k("kare sayısı kayıtla aynı", int(vs["nb_read_frames"]) == olay["kare_sayisi"], f'{vs["nb_read_frames"]} / {olay["kare_sayisi"]}')

w, h = 270, 480
ham = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
kareler = np.frombuffer(ham, np.uint8).reshape(-1, h, w).astype(np.int16)
k("siyah kare yok", int((kareler.mean((1, 2)) < 8).sum()) == 0)
fark = np.abs(np.diff(kareler, axis=0)).mean((1, 2))
anim = [next((x["anim"] for x in kr if x["ad"] == "kasif_on"), None) for kr in olay["kareler"]]
hareketli = [i for i in range(1, len(anim)) if anim[i] in ("run", "jump")]
donuk = [i for i in hareketli if fark[i - 1] < 0.05]
k("hareket bölümünde donmuş kare yok", not donuk, f"donuk: {len(donuk)}/{len(hareketli)}")

sira = [a for i, a in enumerate(anim) if i == 0 or a != anim[i - 1]]
k("animasyon sırası idle→run→jump→idle", sira == ["idle", "run", "jump", "idle"], str(sira))

sr = 48000
def oku(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                                        capture_output=True).stdout, np.float32)
def sapmalar(x):
    # başlangıç: 2 ms pencere enerjisi, olaydan önceki 30 ms'lik yerel tabanın üstüne çıktığı ilk an
    pen = sr // 500; e = np.sqrt(np.convolve(x ** 2, np.ones(pen) / pen, "same")); r = []
    for o in olay["olaylar"]:
        if o["karakter"] != "kasif_on": continue
        i0 = int((o["t"] - 0.02) * sr); seg = e[i0:i0 + int(0.12 * sr)]
        taban = np.median(e[max(0, i0 - int(0.03 * sr)):i0]) if i0 > 0 else 0.0
        r.append((i0 + int(np.argmax(seg > taban + 0.3 * (seg.max() - taban)))) / sr - o["t"])
    return np.array(r) * 1000
for ad, f in (("kaynak efekt.wav", f"{d}/efekt.wav"), ("MP4 (AAC)", v)):
    s_ = sapmalar(oku(f))
    k(f"ses olayları ±1 kare (33 ms) içinde — {ad}", len(s_) > 0 and np.abs(s_).max() <= 1000 / fps,
      f"{len(s_)} olay · en büyük |sapma| {np.abs(s_).max():.1f} ms · ortalama {s_.mean():+.1f} ms")
print(f"\n{sum(sonuc)}/{len(sonuc)} kontrol geçti")
sys.exit(0 if all(sonuc) else 1)
