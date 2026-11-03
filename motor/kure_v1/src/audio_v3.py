"""NØVEX Antarktika V3 — müzik ve efektler, seslendirme zaman çizelgesine göre, AYRI katmanlar halinde.
Tamamen kodla sentezlenir (lisans gerektirmez).
Kullanım: python3 audio_v3.py zaman_cizelgesi.json <cikti_dizini>
Çıktı: muzik.wav, efekt.wav (48 kHz stereo, float → 24-bit)
"""
import json, os, sys, wave
import numpy as np

tl = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = sys.argv[2]
OLD, NEW = np.array(tl["old_knots"]), np.array(tl["new_knots"])
def W(t_old): return float(np.interp(t_old, OLD, NEW))   # eski olay zamanı -> yeni zaman

SR = 48000
DUR = tl["duration"]
N = int(np.ceil(SR * DUR))
t = np.arange(N) / SR
rng = np.random.default_rng(7)


def env(a, b, atk=0.05, rel=0.3):
    e = np.clip((t - a) / atk, 0, 1) * np.clip((b - t) / rel, 0, 1)
    return e * e * (3 - 2 * e)

def lp_fft(x, fc, slope=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** slope), len(x))

def hp_fft(x, fc, slope=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (1 - 1 / (1 + (f / fc) ** slope)), len(x))

def bp_fft(x, f0, q):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + ((f - f0) / (f0 / q)) ** 2), len(x))

def note(m): return 440 * 2 ** ((m - 69) / 12)

class Bus:
    def __init__(self): self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, sig, gain=1.0, pan=0.0, at=0.0):
        i = int(at * SR)
        if i >= N: return
        n = min(len(sig), N - i)
        self.L[i:i + n] += sig[:n] * gain * np.sqrt(0.5 * (1 - pan))
        self.R[i:i + n] += sig[:n] * gain * np.sqrt(0.5 * (1 + pan))

mus, sfx = Bus(), Bus()

# ---------------- MÜZİK: karanlık pad (eski akor sınırları yeni zamana eşlenir) ----------------
chords = [(0.0, 8.0, [38, 50, 53, 57]), (8.0, 14.0, [34, 46, 50, 53]), (14.0, 20.0, [36, 48, 52, 55]),
          (20.0, 26.0, [38, 50, 53, 56]), (26.0, 30.0, [38, 50, 57, 62])]
for a, b, ns in chords:
    A, B = W(a), (DUR if b >= 30 else W(b))
    e = env(A - 0.15, B + 0.6, 0.6, 0.9 if b < 30 else 0.4)
    for k, m in enumerate(ns):
        f = note(m)
        for det, pan in ((-0.12, -0.6), (0.12, 0.6)):
            ph = 2 * np.pi * (f + det) * t
            w = np.sin(ph) + 0.35 * np.sin(2 * ph + 0.3) + 0.15 * np.sin(3 * ph)
            mus.add(w * e * (0.05 if k == 0 else 0.028), 1.0, pan)
shimmer = bp_fft(rng.standard_normal(N), 6500, 3) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t))
mus.add(shimmer * 0.010 * env(0, DUR, 2, 1.5), 1.0, 0.3)

# nabız: sabit tempo (96 BPM) yeni zamanda; 8. sn sonrası (eski) yükselir
beat = 60 / 96
for k in range(int(DUR / beat) + 1):
    bt = k * beat
    if bt < W(3.0) or bt > W(28.3): continue
    if W(26.0) <= bt and k % 2: continue
    prog = min(1, max(0, (bt - W(8.0)) / (W(20.0) - W(8.0))))
    n = int(0.45 * SR); tt = np.arange(n) / SR
    f = 52 * np.exp(-tt * 9) + 38
    mus.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * (0.30 + 0.35 * prog), 1.0, 0.0, bt)
    if bt >= W(14.0) and k % 2 == 1:
        n2 = int(0.06 * SR)
        mus.add(bp_fft(rng.standard_normal(n2), 9000, 2) * np.exp(-np.arange(n2) / SR * 60) * 0.08, 1.0, 0.4, bt)

# ---------------- EFEKTLER ----------------
def whoosh(at, dur, gain, up=True, pan=0.0):
    n = int(dur * SR); tt = np.linspace(0, 1, n); x = rng.standard_normal(n)
    fc = (300 + 5000 * tt ** 2) if up else (5000 - 4700 * tt ** 0.5)
    y = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        y[i:i + blk] = bp_fft(x[i:i + blk], fc[min(i + blk // 2, n - 1)], 1.5)
    sfx.add(y * np.sin(np.pi * tt) ** 1.5 * gain, 1.0, pan, at)

def impact(at, gain=1.0):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 5) + 30) / SR) * np.exp(-tt * 2.2)
    noise = lp_fft(rng.standard_normal(n), 900) * np.exp(-tt * 9) * 0.6
    sfx.add((boom + noise) * gain, 1.0, 0.0, at)

def riser(at, dur, gain):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(200 * 2 ** (tt / dur * 2.5)) / SR) * (tt / dur) ** 2
    nz = bp_fft(rng.standard_normal(n), 3000, 1) * (tt / dur) ** 3
    sfx.add((s * 0.5 + nz) * gain, 1.0, 0.0, at)

def tick(at, gain=0.25, f=2400):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    sfx.add(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 180) * gain, 1.0, 0.0, at)

def crack(at, gain=0.6, pan=0.0):
    """buz çatlaması: seyrek kırılma tıkırtıları + düşük gövde"""
    n = int(0.9 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) * (rng.random(n) < 0.02 * np.exp(-tt * 4) + 0.001)
    x = lp_fft(x, 4000) * np.exp(-tt * 3)
    sfx.add((x * 3 + np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 6) * 0.4) * gain, 1.0, pan, at)

def ice_shimmer(at, dur, gain, pan=0.0):
    """buz kristali parıltısı: yüksek, yumuşak çan tonları"""
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for f in (2093, 2637, 3136, 3951):
        st = int(rng.random() * 0.3 * SR)
        y[st:] += np.sin(2 * np.pi * f * tt[:n - st]) * np.exp(-tt[:n - st] * 5)
    sfx.add(y / 4 * gain, 1.0, pan, at)

# kanca: ilk karede vurgu + uzaydan dalış
impact(0.0, 0.30)
whoosh(0.0, W(2.9), 0.75, up=True)
riser(W(1.4), W(3.0) - W(1.4), 0.28)
impact(W(3.0), 0.6)                                   # Ankara = Güney Kutbu
ice_shimmer(W(3.1), 1.4, 0.35, 0.2)
for i, x in enumerate((5.65, 6.05, 6.4, 6.7, 7.0)): tick(W(x), 0.22, 1800 + 200 * i)   # şehir pinleri
whoosh(W(7.6), 0.8, 0.35, up=False, pan=-0.3)
impact(W(8.0), 0.6)                                   # −50 °C
for i in range(20): tick(W(8.05) + i * 0.045, 0.10, 3200)
# kar fırtınası: rüzgâr (eski 8–14 sn)
wind = bp_fft(rng.standard_normal(N), 450, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t) * np.sin(2 * np.pi * 0.11 * t + 1))
sfx.add(wind * 0.9 * env(W(8.0), W(14.0), 0.6, 0.8), 1.0, -0.2)
sfx.add(np.roll(wind, 7000) * 0.9 * env(W(8.0), W(14.0), 0.6, 0.8), 1.0, 0.2)
crack(W(10.9), 0.55, -0.4); crack(W(11.7), 0.45, 0.5); crack(W(12.5), 0.5, 0.0)
# hafif rüzgâr yatağı videonun geri kalanında (buz kıtası atmosferi)
air = lp_fft(rng.standard_normal(N), 700)
sfx.add(air * 0.10 * env(W(14.0) - 0.5, DUR, 1.0, 1.0), 1.0, 0.0)
whoosh(W(13.6), 0.8, 0.35, up=False, pan=0.3)
for x in (14.45, 14.85, 15.25): tick(W(x), 0.35, 900)         # TARIM/ORMAN/MERA ✕
whoosh(W(16.3), W(19.3) - W(16.3), 0.22, up=True, pan=-0.5)    # ikmal hattı
riser(W(18.6), W(20.0) - W(18.6), 0.22)
impact(W(20.0), 0.6)                                  # asıl şok
crack(W(20.15), 0.5, 0.3)
for x in (21.2, 21.5, 21.8): tick(W(x), 0.2, 1500)            # 3 deniz
whoosh(W(23.0), W(25.6) - W(23.0), 0.25, up=True, pan=0.4)     # mesafe çizgisi
riser(W(24.7), W(26.0) - W(24.7), 0.2)
whoosh(W(26.0), W(28.4) - W(26.0), 0.45, up=False)             # kamera uzaya
impact(W(28.55), 0.55)                                # NØVEX logo
ice_shimmer(W(28.6), 1.6, 0.3, -0.2)


def write(bus, name):
    x = np.stack([bus.L, bus.R], 1)
    x *= np.clip(np.minimum(t / 0.01, (DUR - t) / 0.5), 0, 1)[:, None]
    x = np.stack([hp_fft(x[:, 0], 30), hp_fft(x[:, 1], 30)], 1)   # sesaltı/DC temizliği
    pk = np.abs(x).max(); x = x / pk * 0.5 if pk > 0 else x
    i24 = (np.clip(x, -1, 1) * 8388607).astype(np.int32)
    b = i24.astype("<i4").tobytes(); b = b"".join(b[i:i + 3] for i in range(0, len(b), 4))
    with wave.open(os.path.join(OUT, name), "wb") as f:
        f.setnchannels(2); f.setsampwidth(3); f.setframerate(SR); f.writeframes(b)

write(mus, "muzik.wav"); write(sfx, "efekt.wav")
print("ok", DUR)
