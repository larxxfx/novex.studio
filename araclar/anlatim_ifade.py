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
    else:
        a = MOTOR[motor](DIZIN[motor]) + [f"--{'vits' if motor.startswith('piper') else 'matcha'}-length-scale={hiz}"]
        if motor.startswith("piper"): a += ["--vits-noise-scale=0.72", "--vits-noise-scale-w=0.85"]   # biraz daha canlı prozodi
    run([f"{S}/bin/sherpa-onnx-offline-tts", *a, "--num-threads=2", f"--output-filename={out}", metin], env=ENV)


def sessizlik(sn, out):
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{max(sn, 0.001):.3f}", "-c:a", "pcm_s24le", out])


def isle(ham, kazanc, perde, out):
    """48 kHz'e çevir, uç sessizliği kırp (parça birleşimleri doğal olsun), kazanç ve perde uygula, 8 ms yumuşak giriş/çıkış."""
    f = [f"aresample={SR}", "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02",
         "areverse", "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06", "areverse"]
    if abs(perde) > 0.01: f.append(f"rubberband=pitch={2 ** (perde / 12):.5f}:formant=preserved")
    if abs(kazanc) > 0.01: f.append(f"volume={kazanc}dB")
    f += ["afade=t=in:d=0.008", "areverse", "afade=t=in:d=0.02", "areverse"]
    run(["ffmpeg", "-v", "error", "-y", "-i", ham, "-af", ",".join(f), "-ac", "1", "-c:a", "pcm_s24le", out])


def main(perf_yol, motor, cikti, carpan="1.0"):
    carpan = float(carpan)   # tüm parçaların hızına uygulanan genel çarpan (<1 hızlı)
    p = json.load(open(perf_yol, encoding="utf-8")); pd = os.path.join(cikti, "parcalar"); os.makedirs(pd, exist_ok=True)
    liste, zaman, t, n = [], [], 0.0, 0
    def ekle_sessiz(sn):
        nonlocal t, n
        if sn <= 0: return
        f = f"{pd}/s{n:03d}.wav"; sessizlik(sn, f); liste.append(f); t += sn; n += 1
    ekle_sessiz(p.get("bas_sessizlik", 0.3))
    for ci, c in enumerate(p["cumleler"], 1):
        bas = None; pz = []
        for pi, pr in enumerate(c["parcalar"]):
            ekle_sessiz(pr.get("once", 0.0) if pi else 0.0)
            ham = f"{pd}/h{ci:02d}_{pi}.wav"; son = f"{pd}/p{ci:02d}_{pi}.wav"
            sentezle(motor, pr["metin"], round(pr.get("hiz", 1.0) * carpan, 3), ham)
            isle(ham, pr.get("kazanc_db", 0.0), pr.get("perde", 0.0), son)
            bas = t if bas is None else bas
            d = sure(son); pz.append({"metin": pr["metin"], "bas": round(t, 3), "son": round(t + d, 3), "vurgu_db": pr.get("kazanc_db", 0.0)})
            liste.append(son); t += d
        zaman.append({"i": ci, "metin": " ".join(x["metin"] for x in c["parcalar"]), "bas": round(bas, 3), "son": round(t, 3),
                      "duygu": c.get("duygu", ""), "parcalar": pz})
        ekle_sessiz(c.get("sonra", 0.45))
    lst = f"{pd}/liste.txt"; open(lst, "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f in liste))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s24le", os.path.join(cikti, "anlatim.wav")])
    json.dump(zaman, open(os.path.join(cikti, "zaman.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{motor}: {len(zaman)} cümle, {t:.2f} sn → {cikti}/anlatim.wav")


if __name__ == "__main__":
    main(*sys.argv[1:5])
