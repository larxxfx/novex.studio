"""Seslendirme kaydını yayın kalitesine getirir (kendi kaydımız veya taslak TTS).

Kullanım:  python3 araclar/ses_isle.py girdi.(m4a|wav|mp3) cikti_klasoru/
Çıktı:     ses.wav (48 kHz mono, 24-bit, −16 LUFS, true peak ≤ −1,5 dBTP) + ses_rapor.json

Zincir: 48 kHz mono → uğultu filtresi (80 Hz) → gürültü azaltma (afftdn) → de-esser →
kompresör (3:1) → iki geçişli doğrusal loudness. Konuşmanın hızına ve tonuna dokunulmaz.
"""
import json, os, re, subprocess, sys, hashlib


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def stats(path):
    """Tepe, gürültü tabanı, kırpılmış örnek, LUFS, süre."""
    a = run(["ffmpeg", "-hide_banner", "-i", path, "-af",
             "astats=measure_perchannel=none:measure_overall=Peak_level+Noise_floor+Peak_count,ebur128=peak=true",
             "-f", "null", "-"]).stderr
    num = lambda pat: (lambda m: float(m.group(1)) if m else None)(re.search(pat, a))
    summ = a.split("Summary:")[-1]
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout or 0)
    return {"sure_sn": round(dur, 3), "tepe_dbfs": num(r"Peak level dB:\s*(-?[\d.]+|-inf)"),
            "gurultu_tabani_db": num(r"Noise floor dB:\s*(-?[\d.]+)"),
            "tepe_ornek_sayisi": num(r"Peak count:\s*([\d.]+)"),
            "lufs": (lambda m: float(m.group(1)) if m else None)(re.search(r"I:\s+(-?[\d.]+) LUFS", summ)),
            "true_peak_dbtp": (lambda m: float(m.group(1)) if m else None)(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ))}


def main(src, outdir):
    os.makedirs(outdir, exist_ok=True)
    pre = os.path.join(outdir, "_on_isleme.wav")
    chain = ("aresample=48000:resampler=soxr,aformat=channel_layouts=mono,"
             "highpass=f=80:poles=2,lowpass=f=15000,"
             "afftdn=nr=12:nf=-50:tn=1,"
             "deesser=i=0.35:m=0.5:f=0.5,"
             "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2dB")
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", src, "-af", chain, "-c:a", "pcm_s24le", pre])
    if r.returncode: sys.exit(r.stderr[-800:])
    meas = run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                "-f", "null", "-"]).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    out = os.path.join(outdir, "ses.wav")
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,"
          "alimiter=limit=0.84:attack=2:release=50:level=false,aresample=48000")
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", pre, "-af", ln, "-c:a", "pcm_s24le", out])
    if r.returncode: sys.exit(r.stderr[-800:])
    os.remove(pre)
    rep = {"girdi": os.path.basename(src), "girdi_olcum": stats(src), "cikti_olcum": stats(out),
           "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest()}
    rep["uyarilar"] = []
    if (rep["girdi_olcum"]["tepe_ornek_sayisi"] or 0) > 20 and (rep["girdi_olcum"]["tepe_dbfs"] or -99) > -0.3:
        rep["uyarilar"].append("Girdi kırpılmış (clipping) olabilir: kayıt seviyesi düşürülüp yeniden kaydedilmeli.")
    if (rep["girdi_olcum"]["gurultu_tabani_db"] or -99) > -45:
        rep["uyarilar"].append("Gürültü tabanı yüksek (> −45 dB): daha sessiz bir odada kayıt önerilir.")
    json.dump(rep, open(os.path.join(outdir, "ses_rapor.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
