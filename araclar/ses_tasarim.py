"""Genel ses tasarımı (müzik + efekt), tamamen kodla sentez — dış örnek yok, lisans temiz.
Olaylar anlatıma bağlıdır (araclar/anlatim_ifade.py zaman.json): her cümle başı whoosh; vurgu_db ≥ 2 parçalarda riser + darbe;
'gizem'/'gerilim' cümlelerinde atmosfer; açılış ve kapanış imzası.
Kullanım: python3 araclar/ses_tasarim.py zaman.json cikti_klasoru/ [--ruh gizem|epik|merak|gerilim|hayranlik] [--kapanis 2.0] [--ortam okyanus|ruzgar|uzay|yok]
"""
import argparse, json, os
import numpy as np
from scipy.io import wavfile

SR = 48000
AKOR = {  # 4 akorlu döngü (Hz, kök oktav 3)
    "epik": [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0)],
    "gizem": [(146.83, 174.61, 220.0), (116.54, 138.59, 174.61), (98.0, 116.54, 146.83), (110.0, 138.59, 164.81)],
    "merak": [(164.81, 196.0, 246.94), (130.81, 164.81, 196.0), (196.0, 246.94, 293.66), (146.83, 185.0, 220.0)],
    "gerilim": [(130.81, 155.56, 196.0), (103.83, 130.81, 155.56), (87.31, 103.83, 130.81), (98.0, 123.47, 146.83)],
    "hayranlik": [(130.81, 164.81, 196.0), (174.61, 220.0, 261.63), (110.0, 130.81, 164.81), (196.0, 246.94, 293.66)],
}
DRONE = {"epik": 73.42, "gizem": 73.42, "merak": 82.41, "gerilim": 65.41, "hayranlik": 65.41}


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
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (fr / fc) ** 4)
    return np.fft.irfft(X, len(x))


def sweep(dur, f0, f1, rng):
    n = int(dur * SR); x = rng.standard_normal(n); X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR); fc = np.sqrt(f0 * f1)
    X *= np.exp(-((np.log(fr + 1) - np.log(fc)) ** 2) / 1.2); y = np.fft.irfft(X, n)
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.linspace(0, np.pi, n)) ** 2


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("zaman"); ap.add_argument("cikti")
    ap.add_argument("--ruh", default="merak"); ap.add_argument("--kapanis", type=float, default=2.0); ap.add_argument("--ortam", default="yok")
    a = ap.parse_args(); z = json.load(open(a.zaman)); rng = np.random.default_rng(7)
    T = z[-1]["son"] + a.kapanis; n = int(T * SR); t = np.arange(n) / SR
    # müzik
    m = 0.45 * np.sin(2 * np.pi * DRONE.get(a.ruh, 73.42) * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    L = T / 4
    for i, ch in enumerate(AKOR.get(a.ruh, AKOR["merak"])):
        s0 = int(i * L * SR); dur = L + 1.5; seg = sum(pad(f, dur, rng) for f in ch) / 3 * env(int(dur * SR), 1.5, 1.5)
        b = min(n, s0 + len(seg)); m[s0:b] += 0.9 * seg[: b - s0]
    if a.ruh in ("gerilim", "epik", "gizem"):
        m += np.sin(2 * np.pi * 55 * t) * np.exp(-((t % (0.85 if a.ruh == "gerilim" else 1.0)) * 6)) * 0.3 * np.clip((t - 6) / 4, 0, 1)
    m = lowpass(m, 2500) * env(n, 1.0, 2.0); m /= np.abs(m).max() + 1e-9
    mus = np.stack([m, np.roll(m, 240)], 1) * 0.7
    # efekt
    e = np.zeros((n, 2))
    def koy(sig, at, g, pan=0.0):
        s0 = int(max(0, at) * SR); b = min(n, s0 + len(sig))
        if b > s0: e[s0:b, 0] += g * (1 - pan) * sig[: b - s0]; e[s0:b, 1] += g * (1 + pan) * sig[: b - s0]
    tt = np.arange(int(1.6 * SR)) / SR
    darbe = np.sin(2 * np.pi * 48 * tt * (1 + 0.6 * np.exp(-tt * 8))) * np.exp(-tt * 3.0)
    k12 = int(1.2 * SR); koy(darbe[:k12] + 0.25 * np.sin(2 * np.pi * 880 * tt[:k12]) * np.exp(-tt[:k12] * 4), 0.0, 0.7)   # açılış imzası
    for k, c in enumerate(z[1:], 1): koy(sweep(0.7, 300, 3500, rng), c["bas"] - 0.55, 0.32, 0.3 if k % 2 else -0.3)  # geçiş whoosh
    for c in z:
        for p in c.get("parcalar", []):
            if p.get("vurgu_db", 0) >= 2.0:
                koy(sweep(1.1, 400, 6000, rng) * np.linspace(0.2, 1, int(1.1 * SR)) ** 2, p["bas"] - 1.1, 0.15); koy(darbe, p["bas"] - 0.02, 0.42)
        if any(w in c.get("duygu", "") for w in ("gizem", "gerilim")):
            d = c["son"] - c["bas"] + 1.0; n2 = int(d * SR)
            at = lowpass(rng.standard_normal(n2), 220) * env(n2, 0.4, 0.6); koy(at / (np.abs(at).max() + 1e-9), c["bas"] - 0.3, 0.18)
    if a.ortam != "yok" and len(z) > 2:
        a0, a1 = z[1]["bas"] - 0.5, z[-2]["son"] + 0.5; n3 = int((a1 - a0) * SR); t3 = np.arange(n3) / SR
        fc = {"okyanus": 700, "ruzgar": 1500, "uzay": 160}.get(a.ortam, 700)
        lfo = {"okyanus": 0.11, "ruzgar": 0.05, "uzay": 0.03}.get(a.ortam, 0.1)
        o = lowpass(rng.standard_normal(n3), fc) * (0.55 + 0.45 * np.sin(2 * np.pi * lfo * t3) ** 2) * env(n3, 1.5, 1.5)
        koy(o / (np.abs(o).max() + 1e-9), a0, 0.14)
    son = z[-1]["son"] + 0.05; koy(darbe, son, 0.6)
    n4 = int(1.8 * SR); t4 = np.arange(n4) / SR
    koy((np.sin(2 * np.pi * 587.3 * t4) + 0.6 * np.sin(2 * np.pi * 880 * t4)) * env(n4, 0.3, 1.2) * 0.3, son + 0.1, 0.5)
    e /= np.abs(e).max() + 1e-9
    os.makedirs(a.cikti, exist_ok=True)
    wavfile.write(os.path.join(a.cikti, "muzik.wav"), SR, (mus * 0.9 * 32767).astype(np.int16))
    wavfile.write(os.path.join(a.cikti, "efekt.wav"), SR, (e * 0.9 * 32767).astype(np.int16))
    print(f"ses tasarımı: {T:.2f} sn, ruh={a.ruh}, ortam={a.ortam}")


if __name__ == "__main__":
    main()
