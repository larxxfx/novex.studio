"""Karakter sahnesini MP4'e render eder (NØVEX standardı: 1080×1920, 30 FPS, H.264 High, yuv420p, Rec.709, AAC 48 kHz, −14 LUFS).

Kullanım:
  python3 motor/karakter/araclar/karakter_render.py <sahne.json> <cikti_klasoru> [--ses anlatim.wav] [--sessiz-efekt]

Nasıl çalışır:
  1. motor/karakter klasörü 127.0.0.1'de geçici bir HTTP sunucusuyla sunulur (ES modülleri için).
  2. Başsız Chromium (Playwright) render/sahne.html'i açar; her kare için NOVEX.kare(t) çağrılır → canvas PNG → ffmpeg.
     Zaman, kare numarasından hesaplanır (t = i · 1000 / fps); requestAnimationFrame kullanılmaz → deterministik.
  3. Ses efektleri, render edilen karelerin animasyon durumundan üretilir (koşu adımı, sıçrama, iniş) → görüntüyle aynı zaman ekseni.
  4. --ses verilirse anlatım eklenir; efekt/ambiyans anlatımın altında kısılır (sidechain). İki geçişli loudnorm → −14 LUFS.
  5. araclar/qc.py ile teknik kontrol.
Çıktı: video.mp4, video_sessiz.mp4, efekt.wav, olaylar.json (kare→animasyon kaydı + ses olayları), qc_rapor.md, kontrol kareleri.
"""
import argparse, base64, functools, http.server, json, os, subprocess, sys, threading, time
import numpy as np

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))          # motor/karakter
DEPO = os.path.abspath(os.path.join(KOK, "..", ".."))
SR = 48000


def sunucu_baslat():
    class Sessiz(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Sessiz, directory=KOK)
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def ffmpeg_video(yol, fps, w, h):
    return subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "png", "-framerate", str(fps), "-i", "-",
        "-vf", f"scale={w}:{h}:flags=neighbor:out_color_matrix=bt709:out_range=tv,format=yuv420p",
        "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", str(fps),
        "-movflags", "+faststart", yol], stdin=subprocess.PIPE)


# --- ses efektleri (sentez; dış kaynak/lisans gerektirmez) ---
def zarf(n, atak, dusus):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(atak, 1e-4)) * np.exp(-t / dusus)


def adim(r):
    n = int(0.12 * SR); g = r.standard_normal(n)
    g = np.convolve(g, np.ones(18) / 18, "same")                     # yumuşak toprak sesi
    return 0.55 * g * zarf(n, 0.002, 0.03) + 0.35 * np.sin(2 * np.pi * 85 * np.arange(n) / SR) * zarf(n, 0.001, 0.025)


def sicrama(r):
    n = int(0.35 * SR); t = np.arange(n) / SR
    g = np.convolve(r.standard_normal(n), np.ones(6) / 6, "same")
    return 0.35 * g * np.sin(np.pi * t / t[-1]) ** 2


def inis(r):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return 0.9 * np.sin(2 * np.pi * (70 - 30 * t / t[-1]) * t) * zarf(n, 0.002, 0.06) + 0.4 * adim(r)[:n] if n <= len(adim(r)) else \
        0.9 * np.sin(2 * np.pi * (70 - 30 * t / t[-1]) * t) * zarf(n, 0.002, 0.06)


def ambiyans(n):
    t = np.arange(n) / SR
    return 0.05 * (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 0.4 * np.sin(2 * np.pi * 0.1 * t))
                   + 0.4 * np.sin(2 * np.pi * 110 * t)) * np.minimum(1, t / 1.5) * np.minimum(1, (t[-1] - t) / 1.5)


def etkin_kimlik(k):
    """Motorla aynı kural (src/characters/kimlik.js): ad varsa ad, yoksa id."""
    return str(k["ad"]) if k.get("ad") else str(k["id"])


def sahne_kimlikleri(sahne):
    """Sahnedeki TÜM karakterlerin etkin kimlikleri, sahne sırasıyla; tekrar eden kimlik hata."""
    ids = [etkin_kimlik(k) for k in sahne["karakterler"]]
    tekrar = sorted({x for x in ids if ids.count(x) > 1})
    if tekrar: sys.exit(f"aynı etkin kimlik iki kez: {tekrar} (karakterlere farklı \"ad\" verin)")
    return ids


def ses_olaylari(kayit, fps, ad):
    """Kare kaydından ses olayları: run 0/3. kare = ayak teması, jump 2. kare = kalkış, jump→idle = iniş."""
    olay, onceki = [], None
    for i, kare in enumerate(kayit):
        d = next((x for x in kare if x["ad"] == ad), None)
        if not d: onceki = None; continue
        anahtar = (d["anim"], d["index"])
        if anahtar != onceki:
            t = i / fps
            if d["anim"] == "run" and d["index"] in (0, 3): olay.append({"t": round(t, 4), "tur": "adim", "kare": i})
            if d["anim"] == "jump" and d["index"] == 2: olay.append({"t": round(t, 4), "tur": "sicrama", "kare": i})
            if onceki and onceki[0] == "jump" and d["anim"] != "jump": olay.append({"t": round(t, 4), "tur": "inis", "kare": i})
        onceki = anahtar
    return olay


def wav_yaz(yol, x):
    x = np.clip(x, -1, 1); st = np.repeat(x[:, None], 2, 1)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", yol], input=st.astype(np.float32).tobytes(), check=True)


def loudnorm_iki_gecis(girdi_args, filtre, cikti_args):
    olc = subprocess.run(["ffmpeg", "-hide_banner", *girdi_args, "-filter_complex", filtre + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(olc[olc.rindex("{"):olc.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample={SR}")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *girdi_args, "-filter_complex", filtre + "," + ln + "[a]",
                    *cikti_args], check=True)


def main():
    p = argparse.ArgumentParser(); p.add_argument("sahne"); p.add_argument("cikti")
    p.add_argument("--ses", help="anlatım ses dosyası (isteğe bağlı)"); p.add_argument("--sessiz-efekt", action="store_true")
    a = p.parse_args()
    os.makedirs(a.cikti, exist_ok=True)
    sahne = json.load(open(a.sahne, encoding="utf-8"))
    fps, W, H = sahne.get("fps", 30), sahne.get("genislik", 1080), sahne.get("yukseklik", 1920)
    N = round(sahne["sure_ms"] * fps / 1000)
    from playwright.sync_api import sync_playwright
    srv = sunucu_baslat(); port = srv.server_address[1]
    sessiz = os.path.join(a.cikti, "video_sessiz.mp4"); kayit = []; t0 = time.time(); hatalar = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(); s = b.new_page(viewport={"width": W, "height": H})
        s.on("pageerror", lambda e: hatalar.append(str(e))); s.on("console", lambda m: m.type == "error" and hatalar.append(m.text))
        s.goto(f"http://127.0.0.1:{port}/render/sahne.html"); s.wait_for_function("window.NOVEX_HAZIR === true", timeout=20000)
        bilgi = s.evaluate("(j) => NOVEX.hazirla(j)", sahne)
        if hatalar: sys.exit("sahne hazırlanamadı: " + hatalar[0])
        ff = ffmpeg_video(sessiz, fps, W, H)
        for i in range(N):
            kayit.append(s.evaluate("(t) => NOVEX.kare(t)", i * 1000 / fps))
            ff.stdin.write(base64.b64decode(s.evaluate("NOVEX.png()").split(",", 1)[1]))
        ff.stdin.close(); ff.wait(); b.close()
    srv.shutdown()
    if hatalar: sys.exit("render sırasında hata: " + hatalar[0])
    if ff.returncode: sys.exit("ffmpeg video hatası")
    sure = N / fps
    print(f"render: {N} kare, {time.time() - t0:.1f} sn ({bilgi})")
    # ses
    r = np.random.default_rng(7); efekt = np.zeros(int(sure * SR) + SR); olaylar = []
    kimlikler = sahne_kimlikleri(sahne)
    kayitta = {x["ad"] for kr in kayit for x in kr}
    if kayitta - set(kimlikler): sys.exit(f"render kaydında sahnede olmayan kimlik: {sorted(kayitta - set(kimlikler))}")
    for k in kimlikler:
        olaylar += [dict(o, karakter=k) for o in ses_olaylari(kayit, fps, k)]
    if not a.sessiz_efekt:
        uret = {"adim": adim, "sicrama": sicrama, "inis": inis}
        for o in olaylar:
            x = uret[o["tur"]](r) * (0.6 if o["karakter"].endswith("arka") else 1.0)
            i0 = int(o["t"] * SR); efekt[i0:i0 + len(x)] += x[: len(efekt) - i0]
    efekt = efekt[: int(sure * SR)] + ambiyans(int(sure * SR))
    efekt_yol = os.path.join(a.cikti, "efekt.wav"); wav_yaz(efekt_yol, efekt * 0.8)
    son = os.path.join(a.cikti, "video.mp4")
    cikti_args = ["-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", f"{sure:.3f}",
                  "-movflags", "+faststart", son]
    if a.ses:
        loudnorm_iki_gecis(["-i", sessiz, "-i", efekt_yol, "-i", a.ses],
                           "[2:a]aresample=48000,asplit[v][sc];[1:a][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[d];"
                           "[v][d]amix=inputs=2:normalize=0,apad", cikti_args)
    else:
        loudnorm_iki_gecis(["-i", sessiz, "-i", efekt_yol], "[1:a]anull", cikti_args)
    json.dump({"fps": fps, "kare_sayisi": N, "karakterler": kimlikler, "ana_karakter": kimlikler[0], "olaylar": olaylar, "kareler": kayit}, open(os.path.join(a.cikti, "olaylar.json"), "w"), ensure_ascii=False)
    qc = subprocess.run([sys.executable, os.path.join(DEPO, "araclar", "qc.py"), son, os.path.join(a.cikti, "qc_rapor.md")], capture_output=True, text=True)
    print(qc.stdout[-1500:] or qc.stderr[-800:])
    print(f"ses olayı: {len(olaylar)} · çıktı: {son}")


if __name__ == "__main__":
    main()
