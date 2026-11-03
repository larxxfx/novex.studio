"""Ses / müzik / efekt katmanlarını ayrı seviyelerle miksler; görüntüye dokunmaz.

Kullanım:  python3 araclar/miks.py miks.json
miks.json örneği:
{
  "ses": "ses/ses.wav", "muzik": "ses/muzik.wav", "efekt": "ses/efekt.wav",
  "ses_db": 0, "muzik_db": -4, "efekt_db": -5,
  "ducking_muzik": {"esik": 0.02, "oran": 10}, "ducking_efekt": {"esik": 0.015, "oran": 5},
  "hedef_lufs": -14, "true_peak": -1.5,
  "zamanlama": "07_ses_zamanlama.json",            # konuşma/fon oranı raporu için (isteğe bağlı)
  "cikti": "ses/miks.wav"
}
Seviye değiştirmek için yalnızca bu dosya düzenlenip betik yeniden çalıştırılır.
"""
import json, os, re, subprocess, sys


def run(a): return subprocess.run(a, capture_output=True, text=True)


def lufs(path, a=None, b=None):
    args = ["ffmpeg", "-hide_banner"] + (["-ss", str(a), "-to", str(b)] if a is not None else []) + \
           ["-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"]
    s = run(args).stderr.split("Summary:")[-1]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", s); p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", s)
    return (float(i.group(1)) if i else None), (float(p.group(1)) if p else None)


def main(cfg_path):
    base = os.path.dirname(os.path.abspath(cfg_path)); c = json.load(open(cfg_path, encoding="utf-8"))
    P = lambda k: os.path.join(base, c[k])
    dm, de = c.get("ducking_muzik", {"esik": 0.02, "oran": 10}), c.get("ducking_efekt", {"esik": 0.015, "oran": 5})
    graph = (f"[0:a]aformat=channel_layouts=stereo,volume={c.get('ses_db', 0)}dB,asplit=3[v][s1][s2];"
             f"[1:a]aformat=channel_layouts=stereo,volume={c.get('muzik_db', -4)}dB[m];"
             f"[m][s1]sidechaincompress=threshold={dm['esik']}:ratio={dm['oran']}:attack=15:release=350:makeup=1[md];"
             f"[2:a]aformat=channel_layouts=stereo,volume={c.get('efekt_db', -5)}dB[e];"
             f"[e][s2]sidechaincompress=threshold={de['esik']}:ratio={de['oran']}:attack=8:release=300[ed];"
             f"[v][md][ed]amix=inputs=3:normalize=0:duration=longest")
    pre = P("cikti") + ".premiks.wav"
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", P("ses"), "-i", P("muzik"), "-i", P("efekt"),
             "-filter_complex", graph, "-ar", "48000", "-c:a", "pcm_s24le", pre])
    if r.returncode: sys.exit(r.stderr[-800:])
    I, TP = c.get("hedef_lufs", -14), c.get("true_peak", -1.5)
    m = run(["ffmpeg", "-hide_banner", "-i", pre, "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json", "-f", "null", "-"]).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,"
          "alimiter=limit=0.84:attack=2:release=60:level=false,aresample=48000")
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", pre, "-af", ln, "-c:a", "pcm_s24le", P("cikti")])
    if r.returncode: sys.exit(r.stderr[-800:])
    os.remove(pre)
    rapor = {"lufs_tp": lufs(P("cikti")), "ayarlar": {k: c[k] for k in c if k.endswith("_db")}}
    if c.get("zamanlama") and os.path.exists(P("zamanlama")):          # konuşma / fon oranı
        bed = P("cikti") + ".fon.wav"
        g2 = graph.replace("volume=%sdB,asplit=3[v]" % c.get('ses_db', 0), "volume=%sdB,asplit=3[v0]" % c.get('ses_db', 0)) \
                  .replace("[v][md][ed]amix", "[v0]volume=0[v];[v][md][ed]amix")
        run(["ffmpeg", "-hide_banner", "-y", "-i", P("ses"), "-i", P("muzik"), "-i", P("efekt"), "-filter_complex", g2,
             "-ar", "48000", "-c:a", "pcm_s24le", bed])
        z = json.load(open(P("zamanlama"), encoding="utf-8"))
        satir = []
        for s in z.get("cumleler", z.get("segments", [])):
            a, b = s.get("konusma", s.get("speech"))
            v, _ = lufs(P("ses"), a, b); f, _ = lufs(bed, a, b)
            if v is not None and f is not None: satir.append({"cumle": s.get("i"), "ses_fon_farki_db": round(v - f, 1)})
        os.remove(bed); rapor["ses_fon"] = satir
        rapor["uyarilar"] = [f"Cümle {x['cumle']}: konuşma fona çok yakın ({x['ses_fon_farki_db']} dB < 12)"
                             for x in satir if x["ses_fon_farki_db"] < 12]
    json.dump(rapor, open(P("cikti") + ".rapor.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(rapor, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
