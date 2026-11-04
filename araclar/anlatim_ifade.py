"""İfadeli anlatım: cümleyi parçalara bölüp her parçaya ayrı hız, ses yüksekliği, perde ve duraklama verir (yerel, ücretsiz TTS).
Duygu/vurgu kontrolü olmayan modellerde (VITS/Piper, Matcha, Kokoro) vurgu ve tonlama bu parçalı "performans" ile kurulur.

Kullanım:  python3 araclar/anlatim_ifade.py performans.json motor cikti_klasoru/ [hiz_carpani]
  motor: piper-ljspeech | matcha-ljspeech | kokoro:<sid>
performans.json:
{"bas_sessizlik": 0.3,
 "cumleler": [
   {"duygu": "merak", "sonra": 0.55,
    "parcalar": [{"metin": "This line runs thirty-two thousand kilometers,", "hiz": 0.92},
                 {"metin": "and never touches land.", "hiz": 1.12, "kazanc_db": 2.0, "perde": -0.5, "once": 0.25}]}]}
  soyle: (isteğe bağlı) telaffuz için fonetik yazım, ör. "Kamchatka" → "Kam-chat-ka"; altyazıda metin kullanılır
  hiz: >1 yavaş (length_scale) · kazanc_db: vurgu · perde: yarım ton (rubberband, formant korunur) · once/sonra: duraklama (sn)
Çıktı: anlatim.wav (48 kHz mono), zaman.json [{i, metin, bas, son, duygu, parcalar:[{metin, bas, son, vurgu_db}]}] (altyazı + sahne zamanlaması için), parcalar/.
"""
import json, os, subprocess, sys

C = os.path.expanduser("~/.novex_cache")
S = f"{C}/sherpa-onnx-v1.12.15-linux-x64-shared"
ENV = dict(os.environ, LD_LIBRARY_PATH=f"{S}/lib")
MOTOR = {
    "piper-ljspeech": lambda d: [f"--vits-model={d}/en_US-ljspeech-high.onnx", f"--vits-tokens={d}/tokens.txt",
                                 f"--vits-data-dir={d}/espeak-ng-data"],
    "matcha-ljspeech": lambda d: [f"--matcha-acoustic-model={d}/matcha-icefall-en_US-ljspeech/model-steps-3.onnx",
                                  f"--matcha-vocoder={d}/vocos-22khz-univ.onnx", f"--matcha-tokens={d}/matcha-icefall-en_US-ljspeech/tokens.txt",
                                  f"--matcha-data-dir={d}/matcha-icefall-en_US-ljspeech/espeak-ng-data"],
}
DIZIN = {"piper-ljspeech": f"{C}/dl_piper/vits-piper-en_US-ljspeech-high", "matcha-ljspeech": f"{C}/dl_matcha",
         "kokoro": "/home/claude/tts_eval/dl/kokoro-en-v0_19"}
SR = 48000


def run(a, **k): return subprocess.run(a, check=True, capture_output=True, **k)


def sure(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


def sentezle(motor, metin, hiz, out):
    if motor.startswith("kokoro"):
        d = DIZIN["kokoro"]; sid = motor.split(":")[1]
        a = [f"--kokoro-model={d}/model.onnx", f"--kokoro-voices={d}/voices.bin", f"--kokoro-tokens={d}/tokens.txt",
             f"--kokoro-data-dir={d}/espeak-ng-data", f"--sid={sid}", f"--kokoro-length-scale={hiz}"]
    elif motor.startswith("piper-") and motor not in MOTOR:   # herhangi bir Piper sesi: piper-<ad> → ~/.novex_cache/dl_*/vits-piper-*-<ad>-*/
        import glob as _g
        d = (_g.glob(f"{C}/dl_*/vits-piper-*-{motor[6:]}-*") or [None])[0]
        if not d: raise SystemExit(f"Piper sesi bulunamadı: {motor} (kurulum_ortam.sh)")
        a = [f"--vits-model={_g.glob(d + '/*.onnx')[0]}", f"--vits-tokens={d}/tokens.txt", f"--vits-data-dir={d}/espeak-ng-data",
             f"--vits-length-scale={hiz}", "--vits-noise-scale=0.667", "--vits-noise-scale-w=0.8"]
    else:
        a = MOTOR[motor](DIZIN[motor]) + [f"--{'vits' if motor.startswith('piper') else 'matcha'}-length-scale={hiz}"]
        if motor.startswith("piper"): a += ["--vits-noise-scale=0.667", "--vits-noise-scale-w=0.8"]   # varsayılan: yüksek değişkenlik ilk sesleri bozuyordu (4 Kas telaffuz testi)
    run([f"{S}/bin/sherpa-onnx-offline-tts", *a, "--num-threads=2", f"--output-filename={out}", metin], env=ENV)


def sessizlik(sn, out):
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{max(sn, 0.001):.3f}", "-c:a", "pcm_s24le", out])


def isle(ham, kazanc, perde, out):
    """48 kHz'e çevir, uç sessizliği kırp (parça birleşimleri doğal olsun), kazanç ve perde uygula, 8 ms yumuşak giriş/çıkış."""
    f = [f"aresample={SR}", "silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.09",
         "areverse", "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06", "areverse"]
    if abs(perde) > 0.01: f.append(f"rubberband=pitch={2 ** (perde / 12):.5f}:formant=preserved")
    if abs(kazanc) > 0.01: f.append(f"volume={kazanc}dB")
    f += ["afade=t=in:d=0.008", "areverse", "afade=t=in:d=0.02", "areverse"]
    run(["ffmpeg", "-v", "error", "-y", "-i", ham, "-af", ",".join(f), "-ac", "1", "-c:a", "pcm_s24le", out])


def whisper_wer(wav, metin):
    """Cümle wav'ını Whisper small.en ile yazıya çevirip WER döndürür (yoksa None)."""
    W = f"{C}/sherpa-onnx-whisper-small.en"
    if not os.path.exists(f"{W}/small.en-encoder.int8.onnx"): return None, ""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from short_uret import nrm, wer
    import tempfile as _tf   # her çağrıya ayrı dosya: eşzamanlı üretimler birbirinin sesini değerlendirmesin (4 Kas hatası)
    fd, gecici = _tf.mkstemp(suffix=".wav", prefix="secim_"); os.close(fd)
    try:
        run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-ar", "16000", "-ac", "1", gecici])
        o = subprocess.run([f"{S}/bin/sherpa-onnx-offline", f"--whisper-encoder={W}/small.en-encoder.int8.onnx", f"--whisper-decoder={W}/small.en-decoder.int8.onnx",
                            f"--tokens={W}/small.en-tokens.txt", "--num-threads=2", gecici], capture_output=True, text=True, env=ENV)
    finally:
        os.remove(gecici)
    import re as _re
    h = (_re.findall(r'"text":\s*"(.*?)"', o.stdout + o.stderr) or [""])[-1].strip()
    return wer(nrm(metin), nrm(h)), h


def main(perf_yol, motor, cikti, carpan="1.0", sec="3"):
    """sec: cümle başına en çok kaç deneme (Piper/Matcha rastlantısal; en düşük WER'li deneme seçilir, WER=0 bulununca durur)."""
    carpan, sec = float(carpan), int(sec)
    p = json.load(open(perf_yol, encoding="utf-8")); pd = os.path.join(cikti, "parcalar"); os.makedirs(pd, exist_ok=True)
    liste, zaman, t, n, secim = [], [], 0.0, 0, []
    def sessiz_dosya(sn):
        nonlocal n
        f = f"{pd}/s{n:03d}.wav"; sessizlik(sn, f); n += 1; return f
    if p.get("bas_sessizlik", 0.3) > 0:
        f = sessiz_dosya(p.get("bas_sessizlik", 0.3)); liste.append(f); t += sure(f)
    for ci, c in enumerate(p["cumleler"], 1):
        metin = " ".join(x["metin"] for x in c["parcalar"]); en_iyi = None
        for deneme in range(max(1, sec)):
            dosyalar = []   # (dosya, parça_indeksi veya None=sessizlik)
            for pi, pr in enumerate(c["parcalar"]):
                if pi and pr.get("once", 0.0) > 0: dosyalar.append((sessiz_dosya(pr["once"]), None))
                ham = f"{pd}/h{ci:02d}_{pi}_{deneme}.wav"; son = f"{pd}/p{ci:02d}_{pi}_{deneme}.wav"
                sentezle(motor, pr.get("soyle", pr["metin"]), round(pr.get("hiz", 1.0) * carpan, 3), ham)   # soyle: yalnız TTS'e giden fonetik yazım
                isle(ham, pr.get("kazanc_db", 0.0), pr.get("perde", 0.0), son); dosyalar.append((son, pi))
            cw = f"{pd}/c{ci:02d}_{deneme}.wav"; l = f"{pd}/c{ci:02d}_{deneme}.txt"
            open(l, "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f, _ in dosyalar))
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", l, "-c:a", "pcm_s24le", cw])
            w, duyulan = whisper_wer(cw, metin) if sec > 1 else (None, "")
            if en_iyi is None or (w is not None and w < en_iyi[0]): en_iyi = (w if w is not None else 0.0, dosyalar, deneme, duyulan)
            if w is None or w == 0: break
        w, dosyalar, deneme, duyulan = en_iyi
        secim.append({"i": ci, "deneme": deneme + 1, "wer": round(100 * w, 1), "duyulan": duyulan})
        bas = t; pz = []
        for f, pi in dosyalar:
            d = sure(f)
            if pi is not None:
                pr = c["parcalar"][pi]; pz.append({"metin": pr["metin"], "bas": round(t, 3), "son": round(t + d, 3), "vurgu_db": pr.get("kazanc_db", 0.0)})
            liste.append(f); t += d
        zaman.append({"i": ci, "metin": metin, "bas": round(bas, 3), "son": round(t, 3),
                      "duygu": c.get("duygu", ""), "altyazi": c.get("altyazi", metin), "parcalar": pz})
        if c.get("sonra", 0.45) > 0:
            f = sessiz_dosya(c.get("sonra", 0.45)); liste.append(f); t += sure(f)
    lst = f"{pd}/liste.txt"; open(lst, "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f in liste))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s24le", os.path.join(cikti, "anlatim.wav")])
    json.dump(zaman, open(os.path.join(cikti, "zaman.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(secim, open(os.path.join(cikti, "secim.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{motor}: {len(zaman)} cümle, {t:.2f} sn, deneme {sum(x['deneme'] for x in secim)} → {cikti}/anlatim.wav")


if __name__ == "__main__":
    main(*sys.argv[1:6])
