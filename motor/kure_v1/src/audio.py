"""NØVEX Antarktika — müzik + ses efekti sentezi (lisans gerektirmez, tamamen kodla üretilir).
Kullanım: python3 audio.py out.wav
Zaman çizelgesi render.py sahneleriyle aynıdır (30,0 sn).
"""
import sys, wave
import numpy as np

SR, DUR = 48000, 30.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

def env(a, b, atk=0.05, rel=0.3):
    """a..b arası yumuşak açılıp kapanan zarf."""
    e = np.clip((t - a) / atk, 0, 1) * np.clip((b - t) / rel, 0, 1)
    return e * e * (3 - 2 * e)

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)):  # tek kutuplu; kısa sinyallerde yeterli
        s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def lp_fft(x, fc, slope=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** slope), len(x))

def bp_fft(x, f0, q):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + ((f - f0) / (f0 / q)) ** 2), len(x))

def note(f): return 440 * 2 ** ((f - 69) / 12)

L = np.zeros(N); R = np.zeros(N)
def add(sig, gain=1.0, pan=0.0, at=0.0):
    i = int(at * SR); n = min(len(sig), N - i)
    L[i:i + n] += sig[:n] * gain * np.sqrt(0.5 * (1 - pan))
    R[i:i + n] += sig[:n] * gain * np.sqrt(0.5 * (1 + pan))

# ---------- 1. Drone / pad (D minör, karanlık) ----------
chords = [  # (başla, bitir, midi notalar)
    (0.0, 8.0, [38, 50, 53, 57]),     # Dm
    (8.0, 14.0, [34, 46, 50, 53]),    # Bb
    (14.0, 20.0, [36, 48, 52, 55]),   # C
    (20.0, 26.0, [38, 50, 53, 56]),   # Ddim renkli gerilim
    (26.0, 30.0, [38, 50, 57, 62]),   # D5 açık final
]
for a, b, ns in chords:
    e = env(a - 0.15, b + 0.6, 0.6, 0.9)
    for k, m in enumerate(ns):
        f = note(m)
        for det, pan in ((-0.12, -0.6), (0.12, 0.6)):
            ph = 2 * np.pi * (f + det) * t
            w = np.sin(ph) + 0.35 * np.sin(2 * ph + 0.3) + 0.15 * np.sin(3 * ph)
            add(w * e * (0.05 if k == 0 else 0.028), 1.0, pan)
# yavaş filtre süpürmesi hissi için yüksek frekanslı "buz" parıltısı
shimmer = rng.standard_normal(N)
shimmer = bp_fft(shimmer, 6500, 3) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t))
add(shimmer * 0.010 * env(0, 30, 2, 2), 1.0, 0.3)

# ---------- 2. Nabız (gerilim tamburu), 8 sn'den sonra yükselir ----------
bpm = 96; beat = 60 / bpm
for k in range(int(30 / beat)):
    bt = k * beat
    if bt < 3.0 or bt > 28.3: continue
    if 26.0 <= bt < 28.3 and k % 2: continue
    gain = 0.30 + 0.35 * min(1, max(0, (bt - 8) / 12))
    n = int(0.45 * SR); tt = np.arange(n) / SR
    f = 52 * np.exp(-tt * 9) + 38
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    add(kick * gain, 1.0, 0.0, bt)
    if bt >= 14.0 and k % 2 == 1:  # 14 sn'den sonra ince hi-hat
        n2 = int(0.06 * SR); hh = bp_fft(rng.standard_normal(n2), 9000, 2) * np.exp(-np.arange(n2) / SR * 60)
        add(hh * 0.08, 1.0, 0.4, bt)

# ---------- 3. Efektler ----------
def whoosh(at, dur, gain, up=True, pan=0.0):
    n = int(dur * SR); tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    fc = (300 + 5000 * tt ** 2) if up else (5000 - 4700 * tt ** 0.5)
    # zamanla değişen filtre: bloklar halinde
    y = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        seg = x[i:i + blk]; c = fc[min(i + blk // 2, n - 1)]
        y[i:i + blk] = bp_fft(seg, c, 1.5)
    shape = np.sin(np.pi * tt) ** 1.5
    add(y * shape * gain, 1.0, pan, at)

def impact(at, gain=1.0):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 5) + 30) / SR) * np.exp(-tt * 2.2)
    noise = lp_fft(rng.standard_normal(n), 900) * np.exp(-tt * 9) * 0.6
    add((boom + noise) * gain, 1.0, 0.0, at)

def riser(at, dur, gain):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 200 * 2 ** (tt / dur * 2.5)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / dur) ** 2
    nz = bp_fft(rng.standard_normal(n), 3000, 1) * (tt / dur) ** 3
    add((s * 0.5 + nz) * gain, 1.0, 0.0, at)

def tick(at, gain=0.25, f=2400):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    add(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 180) * gain, 1.0, 0.0, at)

def crack(at, gain=0.6, pan=0.0):
    n = int(0.9 * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n) * (rng.random(n) < 0.02 * np.exp(-tt * 4) + 0.001)
    x = lp_fft(x, 4000) * np.exp(-tt * 3)
    body = np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 6) * 0.4
    add((x * 3 + body) * gain, 1.0, pan, at)

# S1 kanca: uzaydan dalış
whoosh(0.0, 2.9, 1.6, up=True)
impact(0.0, 0.45)                      # ilk karede vurgu
riser(1.4, 1.6, 0.45)
impact(3.0, 0.6)                       # Ankara = Güney Kutbu
for i, tt_ in enumerate((5.65, 6.05, 6.4, 6.7, 7.0)): tick(tt_, 0.22, 1800 + 200 * i)  # şehir pinleri
whoosh(7.6, 0.8, 0.35, up=False, pan=-0.3)
impact(8.0, 0.6)                       # −50 °C
for i in range(20): tick(8.05 + i * 0.045, 0.10, 3200)   # sayaç
# kar fırtınası: rüzgâr 8–14
wind = rng.standard_normal(N)
wind = bp_fft(wind, 450, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t) * np.sin(2 * np.pi * 0.11 * t + 1))
add(wind * 0.9 * env(8.0, 14.0, 0.6, 0.8), 1.0, -0.2)
add(np.roll(wind, 7000) * 0.9 * env(8.0, 14.0, 0.6, 0.8), 1.0, 0.2)
crack(10.9, 0.55, -0.4); crack(11.7, 0.45, 0.5); crack(12.5, 0.5, 0.0)
whoosh(13.6, 0.8, 0.35, up=False, pan=0.3)
for tt_ in (14.45, 14.85, 15.25): tick(tt_, 0.35, 900)    # TARIM/ORMAN/MERA ✕
whoosh(16.3, 3.0, 0.22, up=True, pan=-0.5)               # uçak hattı
riser(18.6, 1.4, 0.22)
impact(20.0, 0.6)                     # Asıl şok
for tt_ in (21.2, 21.5, 21.8): tick(tt_, 0.2, 1500)     # 3 deniz
whoosh(23.0, 2.6, 0.25, up=True, pan=0.4)               # mesafe çizgisi
riser(24.7, 1.3, 0.2)
whoosh(26.0, 2.4, 0.45, up=False)     # kamera uzaya çekiliyor
impact(28.55, 0.55)                   # NØVEX logo

# ---------- Miks ----------
mix = np.stack([L, R], 1)
mix *= np.clip(np.minimum(t / 0.05, (DUR - t) / 0.6), 0, 1)[:, None]   # tık önleme + son kuyruk
# yumuşak limiter
peak = np.max(np.abs(mix)); mix = np.tanh(mix / peak * 1.4) / np.tanh(1.4) * 0.89
out = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print("ok", sys.argv[1])
