"""NØVEX Antarktika — seslendirme üretimi (ücretsiz, yerel: Coqui Türkçe Glow-TTS + HiFiGAN, NumPy).
Her cümle, videodaki altyazı aralığına sığacak hızda üretilir ve o altyazının başlangıcına yerleştirilir.
Kullanım: python3 narration.py <cikti_dizini>
"""
import json, os, sys, wave
import numpy as np

sys.path.insert(0, "/home/claude/numtts")
import numtts  # noqa: E402

M = "/home/claude/tts_dl/m/"
SR = 22050
# (altyazı başlangıç, altyazı bitiş, okunacak metin — sayılar yazıyla)
LINES = [
    (0.10, 2.95, "Türkiye'yi alıp, dünyanın en soğuk kıtasına bıraktık."),
    (3.00, 5.30, "Ankara, tam Güney Kutbu'nda."),
    (5.30, 7.95, "İstanbul da, Van da, buzun üstünde."),
    (8.00, 10.80, "Kutupta yıllık ortalama, eksi elli derece."),
    (10.80, 13.95, "Güneş, altı ay boyunca hiç doğmaz."),
    (14.00, 16.20, "Açık havada tarım olmazdı."),
    (16.20, 19.95, "Yakıt da ekmek de, uçakla ya da haftalar süren konvoylarla gelirdi."),
    (20.00, 23.00, "Asıl şok: üç tarafı deniz olan Türkiye'nin, tek bir kıyısı kalmazdı."),
    (23.00, 25.95, "Ankara'dan en yakın denize, bin iki yüz kilometreden fazla."),
    (26.00, 28.40, "Bir ülkenin kaderini yalnızca insanlar değil, coğrafya da yazar."),
    (28.40, 29.90, "Sen bu ülkede ilk neyi kurardın?"),
]
LEAD = 0.06          # konuşma altyazının ilk kelimesinden hemen sonra başlasın
TAIL_GAP = 0.12      # bir sonraki altyazıya bırakılan boşluk
LS_MIN, LS_MAX = 0.80, 1.05   # hız sınırları (length_scale): çok hızlı/yavaş olmasın


def trim(w, thr=0.012, keep=0.03, with_offset=False):
    e = np.convolve(np.abs(w), np.ones(256) / 256, "same")
    idx = np.where(e > thr)[0]
    if not len(idx):
        return (w, 0) if with_offset else w
    a = max(0, idx[0] - int(keep * SR)); b = min(len(w), idx[-1] + int(keep * SR))
    return (w[a:b], a) if with_offset else w[a:b]


def word_onsets(tts, text, ls, trim_off):
    """Her kelimenin, kırpılmış ses içindeki başlangıç saniyesi (Glow-TTS harf sürelerinden)."""
    ids, _, wc = tts.durations(text, ls)
    chars = [tts.tok.vocab[i] for i in ids]
    hop = 256 / SR
    t = np.concatenate([[0], np.cumsum(wc)]) * hop - trim_off / SR
    on, prev_space = [], True
    for k, ch in enumerate(chars):
        if ch != " " and prev_space:
            on.append(max(0.0, float(t[k])))
        prev_space = ch == " "
    return on


def synth(tts, voc, text, ls):
    mel, _ = tts.mel(text, ls)
    return trim(voc(mel))


LS = 0.93            # tüm cümlelerde aynı, doğal hız (×1.075)
GAP_AFTER = 0.18     # cümle sonu nefes payı


def plan(out):
    """V3: her cümle aynı hızda üretilir; video zaman çizelgesi sese göre yeniden kurulur."""
    os.makedirs(out, exist_ok=True)
    tts = numtts.GlowTTS(M + "tts_models--tr--common-voice--glow-tts")
    voc = numtts.HiFiGAN(M + "vocoder_models--tr--common-voice--hifigan")
    old_knots, new_knots, segs = [0.0], [0.0], []
    t_new = 0.0; prev_old = 0.0
    waves = []
    for i, (a, b, text) in enumerate(LINES):
        mel, _ = tts.mel(text, LS)
        w, off = trim(voc(mel), with_offset=True); waves.append(w)
        onsets = word_onsets(tts, text, LS, off)
        d = len(w) / SR
        t_new += (a - prev_old)                   # altyazılar arası boşluk aynen korunur
        A = t_new
        need = LEAD + d + (GAP_AFTER if i < len(LINES) - 1 else 0.55)   # son cümleden sonra logo payı
        B = A + max(b - a, need)
        old_knots += [a, b]; new_knots += [A, B]
        segs.append({"i": i + 1, "text": text, "old": [a, b], "new": [round(A, 4), round(B, 4)],
                     "speech": [round(A + LEAD, 4), round(A + LEAD + d, 4)], "dur": round(d, 3),
                     "word_onsets": [round(A + LEAD + o, 4) for o in onsets]})
        t_new = B; prev_old = b
    end_new = t_new + (30.0 - prev_old)
    old_knots.append(30.0); new_knots.append(end_new)
    T = int(np.ceil(end_new * SR))
    total = np.zeros(T, np.float32)
    for sg, w in zip(segs, waves):
        i0 = int(sg["speech"][0] * SR)
        fade = np.ones(len(w), np.float32); n = int(0.008 * SR)
        fade[:n] = np.linspace(0, 1, n); fade[-n:] = np.linspace(1, 0, n)
        total[i0:i0 + len(w)] += w * fade
    with wave.open(os.path.join(out, "seslendirme_22k.wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(total, -1, 1) * 32767).astype(np.int16).tobytes())
    tl = {"length_scale": LS, "duration": round(end_new, 4), "old_knots": old_knots,
          "new_knots": [round(x, 4) for x in new_knots], "segments": segs}
    json.dump(tl, open(os.path.join(out, "zaman_cizelgesi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for sg in segs:
        print(f"{sg['i']:2d} yeni {sg['new'][0]:6.2f}-{sg['new'][1]:6.2f}  konuşma {sg['speech'][0]:6.2f}-{sg['speech'][1]:6.2f} ({sg['dur']:.2f}s)  {sg['text']}")
    print("toplam süre:", round(end_new, 2), "sn")


def main(out):
    os.makedirs(out, exist_ok=True)
    tts = numtts.GlowTTS(M + "tts_models--tr--common-voice--glow-tts")
    voc = numtts.HiFiGAN(M + "vocoder_models--tr--common-voice--hifigan")
    total = np.zeros(int(30.0 * SR), np.float32)
    report = []
    for i, (a, b, text) in enumerate(LINES):
        slot = (b - a) - LEAD - (TAIL_GAP if i < len(LINES) - 1 else 0)
        w = synth(tts, voc, text, 1.0)
        nat = len(w) / SR
        ls = float(np.clip(slot / nat * 0.98, LS_MIN, LS_MAX)) if nat > slot else 1.0
        if ls != 1.0:
            w = synth(tts, voc, text, ls)
        dur = len(w) / SR
        st = a + LEAD
        i0 = int(st * SR); i1 = min(len(total), i0 + len(w))
        fade = np.ones(len(w), np.float32); n = int(0.008 * SR)
        fade[:n] = np.linspace(0, 1, n); fade[-n:] = np.linspace(1, 0, n)
        total[i0:i1] += (w * fade)[:i1 - i0]
        ok = st + dur <= b - (TAIL_GAP if i < len(LINES) - 1 else 0) + 1e-3
        report.append({"i": i + 1, "text": text, "start": round(st, 3), "end": round(st + dur, 3),
                       "slot_end": b, "natural_s": round(nat, 2), "length_scale": round(ls, 3), "fits": bool(ok)})
        print(f"{i+1:2d} {st:5.2f}-{st+dur:5.2f} (slot ≤{b:5.2f})  doğal {nat:4.2f}s  hız×{1/ls:4.2f}  {'OK' if ok else 'TAŞIYOR'}  {text}")
    total = np.clip(total, -1, 1)
    with wave.open(os.path.join(out, "seslendirme_22k.wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((total * 32767).astype(np.int16).tobytes())
    json.dump(report, open(os.path.join(out, "seslendirme_zamanlar.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    plan(sys.argv[1]) if len(sys.argv) > 2 and sys.argv[2] == "--plan" else main(sys.argv[1])
