"""SON SİNYAL karakter efekt ön ayarını uygular. Kullanım: python3 araclar/karakter_ses.py girdi.wav cikti.wav <ön_ayar>"""
import json, os, subprocess, sys
P = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "seriler/son-sinyal/ses/ses_profilleri.json"), encoding="utf-8"))
src, dst, ad = sys.argv[1:4]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", P[ad]["ffmpeg_af"], "-c:a", "pcm_s24le", dst], check=True)
print("ok", ad, dst)
