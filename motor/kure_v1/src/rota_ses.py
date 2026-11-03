"""Rota Short'u için lisanssız müzik + efekt sentezi (tamamen kodla üretilir, dış örnek yok).
Kullanım: python3 src/rota_ses.py zaman.json cikti_klasoru/   → muzik.wav, efekt.wav (48 kHz stereo)
Müzik: D minör drone + yavaş akor pedi + alt nabız; sahne geçişlerinde 'whoosh', varışta darbe.
"""
import json, os, sys
import numpy as np
from scipy.io import wavfile

SR = 48000


def env(n, a, r):
    e = np.ones(n); a, r = int(a * SR), int(r * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e


def pad(f, dur, rng, det=0.003):
    t = np.arange(int(dur * SR)) / SR; s = np.zeros_like(t)
    for k, g in ((1, 1.0), (2, 0.35), (3, 0.18), (4, 0.08)):
        for d in (-det, 0, det):
            s += g * np.sin(2 * np.pi * f * k * (1 + d) * t + rng.uniform(0, 6.28))
    return s / 6


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    for i, v in enumerate(x): z = (1 - a) * v + a * z; y[i] = z
    return y


def noise_sweep(dur, f0, f1, rng):
    n = int(dur * SR); x = rng.standard_normal(n)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR); fc = np.sqrt(f0 * f1)
    X *= np.exp(-((np.log(fr + 1) - np.log(fc)) ** 2) / 1.2); y = np.fft.irfft(X, n)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y / (np.abs(y).max() + 1e-9) * e


def main(zaman, out):
    z = json.load(open(zaman)); T = z[-1]["son"] + 2.2; n = int(T * SR); rng = np.random.default_rng(7)  # 2.2 = rota.KAPANIS_SN
    t = np.arange(n) / SR
    # müzik: Dm → Bb → F → C (her ~11 sn), drone D2
    m = 0.5 * np.sin(2 * np.pi * 73.42 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    akor = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0)]
    L = T / 4
    for i, ch in enumerate(akor):
        a = int(i * L * SR); dur = L + 1.5; seg = sum(pad(f, dur, rng) for f in ch) / 3 * env(int(dur * SR), 1.5, 1.5)
        b = min(n, a + len(seg)); m[a:b] += 0.9 * seg[: b - a]
    puls = (np.sin(2 * np.pi * 55 * t) * np.exp(-((t % 1.0) * 6))) * 0.35 * np.clip((t - 12) / 4, 0, 1)
    m = m + puls
    m = lowpass(m, 2500) * env(n, 1.0, 2.5)
    # son: kapanışta yükselen beşli
    m[int((T - 6) * SR):] += 0.12 * pad(293.66, 6, rng)[: n - int((T - 6) * SR)] * np.linspace(0, 1, n - int((T - 6) * SR))
    m /= np.abs(m).max() + 1e-9
    mus = np.stack([m, np.roll(m, 240)], 1) * 0.7
    # efekt: sahne geçişlerinde whoosh, kanca/varış/soru anlarında alçak darbe
    e = np.zeros((n, 2))
    def koy(sig, at, g, pan=0.0):
        a = int(max(0, at) * SR); b = min(n, a + len(sig)); e[a:b, 0] += g * (1 - pan) * sig[: b - a]; e[a:b, 1] += g * (1 + pan) * sig[: b - a]
    for k, s in enumerate(z[1:], 1):
        koy(noise_sweep(0.7, 300, 3500, rng), s["bas"] - 0.55, 0.35, 0.3 if k % 2 else -0.3)
    tt = np.arange(int(1.6 * SR)) / SR
    darbe = (np.sin(2 * np.pi * 48 * tt * (1 + 0.6 * np.exp(-tt * 8))) * np.exp(-tt * 3.0))
    for at in (0.2, z[7]["bas"] + 0.3, z[10]["son"] + 0.05):
        koy(darbe, at, 0.8)
    e /= np.abs(e).max() + 1e-9
    os.makedirs(out, exist_ok=True)
    wavfile.write(os.path.join(out, "muzik.wav"), SR, (mus * 0.9 * 32767).astype(np.int16))
    wavfile.write(os.path.join(out, "efekt.wav"), SR, (e * 0.9 * 32767).astype(np.int16))
    print("tamam", round(T, 2), "sn")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
