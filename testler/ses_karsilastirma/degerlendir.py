"""NØVEX ses adayı değerlendirme + test MP4 (1080×1920, 30 FPS).

Kullanım:
  python3 testler/ses_karsilastirma/degerlendir.py <ses.(wav|mp3|m4a|flac)> <metin.txt> <etiket> <cikti_klasoru>
  ör.: ... google_chirp3.wav metin_yusuf.txt "Google Chirp3-HD <ses-adı> · YUSUF" out/google_yusuf

Ölçümler (nesnel; kulak testinin yerini tutmaz):
  - Ham ses: süre, LUFS, true peak, gürültü tabanı, kırpılma  (araclar/ses_isle.py stats)
  - İşlenmiş ses (−16 LUFS): cümle hizalama + Whisper-medium CER (araclar/hizala.py --whisper)
  - Perde: medyan F0 (Hz) ve p5–p95 aralığı (yarım ton) → tonlama canlılığı / monotonluk
  - Hız: hece/sn (konuşma süresi üzerinden), cümle arası duraklama ort./min/maks
Çıktı: rapor.json, rapor.md, test.mp4 (marka zemini + cümle altyazısı + etiket), qc_rapor.md.
Bu araç hiçbir ağ servisine bağlanmaz.
"""
import json, os, re, subprocess, sys
import numpy as np

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(KOK, "araclar"))
import ses_isle, hizala  # noqa: E402

FONT = "Inter"


def run(a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-1500:])
    return r


def f0_olc(wav):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    n, hop = 640, 160
    f0 = []
    for i in range(0, len(x) - n, hop):
        fr = x[i:i + n] - x[i:i + n].mean()
        if np.sqrt((fr ** 2).mean()) < 0.02: continue
        ac = np.correlate(fr, fr, "full")[n - 1:]
        lo, hi = 16000 // 400, 16000 // 65
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.45 * ac[0]: f0.append(16000 / k)
    f0 = np.array(f0)
    if len(f0) < 20: return None
    p5, p50, p95 = np.percentile(f0, [5, 50, 95])
    return {"medyan_hz": round(float(p50), 1), "aralik_yarimton_p5_p95": round(float(12 * np.log2(p95 / p5)), 1)}


def ass_zaman(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_yaz(path, etiket, cumleler, dur):
    stil = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"Style: Alt,{FONT},62,&H00FFFFFF,&H00FFFFFF,&H00301408,&H64000000,-1,0,0,0,100,100,0,0,1,4,0,2,140,140,470,1\n"
            f"Style: Etiket,{FONT},40,&H00D9C24A,&H00FFFFFF,&H00301408,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,8,140,140,260,1\n"
            f"Style: Marka,{FONT},54,&H00FFFFFF,&H00FFFFFF,&H00301408,&H00000000,-1,0,0,0,100,100,10,0,1,0,0,8,140,140,170,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = [f"Dialogue: 0,{ass_zaman(0)},{ass_zaman(dur)},Marka,,0,0,0,,NØVEX",
          f"Dialogue: 0,{ass_zaman(0)},{ass_zaman(dur)},Etiket,,0,0,0,,SES TESTİ · {etiket}"]
    for c in cumleler:
        a, b = c["konusma"]
        ev.append(f"Dialogue: 1,{ass_zaman(max(0, a - 0.05))},{ass_zaman(b + 0.15)},Alt,,0,0,0,,{c['metin']}")
    open(path, "w", encoding="utf-8").write(stil + "\n".join(ev) + "\n")


def main(src, metin, etiket, out):
    os.makedirs(out, exist_ok=True)
    ses_isle.main(src, out)                        # out/ses.wav + ses_rapor.json
    wav = os.path.join(out, "ses.wav")
    zam = os.path.join(out, "zamanlama.json")
    hizala.main(wav, metin, zam, True)
    z = json.load(open(zam, encoding="utf-8"))
    sr = json.load(open(os.path.join(out, "ses_rapor.json"), encoding="utf-8"))
    cs = z["cumleler"]
    konusma = sum(b - a for a, b in (c["konusma"] for c in cs))
    hece = sum(hizala.heceler(w) for c in cs for w in hizala.sayilari_yaz(c["metin"]).split())
    durak = [cs[i + 1]["konusma"][0] - cs[i]["konusma"][1] for i in range(len(cs) - 1)]
    tum = " ".join(c["metin"] for c in cs); tum_h = " ".join(c.get("whisper", "") for c in cs)
    rap = {"etiket": etiket, "girdi": os.path.basename(src), "ham": sr["girdi_olcum"], "islenmis": sr["cikti_olcum"],
           "cer_genel": round(hizala.cer(tum, tum_h), 4),
           "cer_en_kotu_cumle": max(((c.get("cer", 0), c["i"]) for c in cs)),
           "hiz_hece_sn": round(hece / konusma, 2) if konusma else None,
           "durak_sn": {"ort": round(float(np.mean(durak)), 2), "min": round(min(durak), 2), "maks": round(max(durak), 2)} if durak else None,
           "perde": f0_olc(wav), "uyarilar": z["uyarilar"] + sr["uyarilar"]}
    dur = sr["cikti_olcum"]["sure_sn"] + 0.6
    ass = os.path.join(out, "altyazi.ass"); ass_yaz(ass, etiket, cs, dur)
    mp4 = os.path.join(out, "test.mp4")
    vf = ("format=yuv420p,"
          f"ass={ass}:fontsdir=/usr/share/fonts/opentype/inter,"
          "scale=out_color_matrix=bt709:out_range=tv,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709")
    run(["ffmpeg", "-hide_banner", "-y",
         "-f", "lavfi", "-i", f"gradients=s=1080x1920:r=30:c0=0x08122B:c1=0x0B2A4A:x0=540:y0=0:x1=540:y1=1920:d={dur}",
         "-i", wav, "-filter_complex",
         f"[0:v]{vf}[v];[1:a]apad=pad_dur=0.6,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", "-r", "30",
         "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", mp4])
    subprocess.run([sys.executable, os.path.join(KOK, "araclar", "qc.py"), mp4, os.path.join(out, "qc_rapor.md")],
                   capture_output=True, text=True)
    json.dump(rap, open(os.path.join(out, "rapor.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    p = rap["perde"] or {}
    md = [f"# Ses testi — {etiket}", "", f"Girdi: `{rap['girdi']}`", "",
          "| Ölçüm | Değer |", "|---|---|",
          f"| Süre (ham) | {rap['ham']['sure_sn']} sn |",
          f"| Ham LUFS / true peak | {rap['ham']['lufs']} / {rap['ham']['true_peak_dbtp']} dBTP |",
          f"| Ham gürültü tabanı | {rap['ham']['gurultu_tabani_db']} dB |",
          f"| Whisper CER (genel) | %{100 * rap['cer_genel']:.1f} |",
          f"| En kötü cümle | #{rap['cer_en_kotu_cumle'][1]} — CER %{100 * rap['cer_en_kotu_cumle'][0]:.0f} |",
          f"| Hız | {rap['hiz_hece_sn']} hece/sn |",
          f"| Cümle arası duraklama | {rap['durak_sn']} |",
          f"| Medyan perde | {p.get('medyan_hz')} Hz |",
          f"| Perde aralığı (p5–p95) | {p.get('aralik_yarimton_p5_p95')} yarım ton |", "",
          "## Cümleler", "", "| # | Metin | Whisper | CER |", "|---|---|---|---|"]
    md += [f"| {c['i']} | {c['metin']} | {c.get('whisper', '')} | %{100 * c.get('cer', 0):.0f} |" for c in cs]
    md += ["", "## Uyarılar", ""] + [f"- {u}" for u in rap["uyarilar"]] + ([] if rap["uyarilar"] else ["- yok"])
    md += ["", "Kulak testi (Emir): doğallık · vurgu · duygu · marka uyumu → `KARSILASTIRMA.md` tablosuna."]
    open(os.path.join(out, "rapor.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    if len(sys.argv) != 5: sys.exit(__doc__)
    main(*sys.argv[1:])
