#!/usr/bin/env python3
"""NØVEX teslim doğrulayıcı: bir video klasörünün gerçekten teslim edilebilir olup olmadığını denetler.

Kullanım:
  python3 araclar/teslim_dogrula.py videolar/<klasör> [videolar/<klasör> ...] [--json] [--md rapor.md]

Denetimler (hata = teslim edilemez; uyarı = bakılmalı; yayına hazır = hata yok + lisans 'evet'):
  1. MP4      cikti/VIDEO.mp4 var; 1080×1920, 30 fps, H.264 High, yuv420p, bt709, AAC 48 kHz; süre; SHA-256;
              plan ve anlatım dosyalarından YENİ (eski plandan kalma MP4 yakalanır); durum.json'da tüm aşamalar 'tamam'.
  2. Kapak    teslim/THUMBNAIL.jpg geçerli görüntü, 9:16, ≥ 1080×1920.
  3. Altyazı  teslim/SUBTITLES.srt ayrıştırılır; zamanlar sıralı; son satır video süresini aşmaz.
  4. Paket    TITLE, DESCRIPTION, TAGS, HASHTAGS, PINNED_COMMENT, SOURCES (görsel kaynak/lisans dahil), YOUTUBE, INSTAGRAM_REELS,
              TIKTOK, QC_REPORT, NARRATION (tam seslendirme metni) boş değil.
  5. Katılım  son anlatım cümlesi + son altyazı "next" içeren bir soru; sahne planı `soru` sahnesiyle biter;
              sabitlenmiş yorum soru içerir; jenerik "subscribe / like and" kalıbı yok (CLAUDE.md, zorunlu kural).
  6. Görsel   sahnelerin en az yarısı 3D/sinematik (`gezegen`); harita en fazla 2 sahne; `vurgu_kelimeler` var.
  7. Ses      uretim.json ses_motoru ile ses/LISANS.txt motoru aynı model; `yayin_uygun: evet` değilse yayına hazır değil.
  8. Somut görsel (Emir, 4 Kas 10:16)  `soru` dışındaki HER sahnede somut görsel varlık: `foto` (dosya + koken + kaynak + lisans)
              veya `gezegen` (doku ya da disliler). Yalnız yazı/sayaç/harita/grafik sahnesi = hata.
  9. Gelişim  uretim.json `gelisim_hedefi` (bu videonun önceki videolara göre somut gelişim hedefi) dolu.
 10. Tekrar   kapanış sorusu başka bir videonun kapanış sorusuyla aynı değil.
"""
import hashlib, json, os, re, subprocess, sys

PAKET = ["TITLE.txt", "DESCRIPTION.txt", "TAGS.txt", "HASHTAGS.txt", "PINNED_COMMENT.txt", "SOURCES.txt",
         "YOUTUBE.txt", "INSTAGRAM_REELS.txt", "TIKTOK.txt", "QC_REPORT.txt", "NARRATION.txt"]
ASAMALAR = ["ses", "telaffuz", "altyazi", "render", "ses_tasarim", "miks", "birlestir", "qc", "kapak", "paket"]
JENERIK = re.compile(r"\b(subscribe|smash (the )?like|like and (comment|share)|hit the bell)\b", re.I)
SINEMATIK = {"gezegen", "foto"}   # 3D/sinematik/görsel sahne türleri (sahne_v1)
KOKENLER = {"fotograf", "arsiv", "ai", "prosedurel"}


def somut_mu(s):
    """Sahnede somut bir görsel varlık var mı (yalnız yazı/sayaç/harita/grafik değil)?"""
    if s.get("tur") == "foto": return bool(s.get("dosya"))
    if s.get("tur") == "gezegen": return s.get("doku", "venus") != "yok" or bool(s.get("disliler"))
    return False


def kapanis_metni(perf):
    son = perf["cumleler"][-1]; return son.get("altyazi") or " ".join(p["metin"] for p in son["parcalar"])


def nrm_soru(t): return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def ffprobe(yol):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", yol],
                       capture_output=True, text=True)
    if r.returncode: return None
    return json.loads(r.stdout)


def srt_oku(yol):
    def sn(t):
        h, m, s = t.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
    out = []
    for blok in re.split(r"\n\s*\n", open(yol, encoding="utf-8").read().strip()):
        sat = blok.strip().splitlines()
        if len(sat) < 3 or "-->" not in sat[1]: raise ValueError(f"bozuk SRT bloğu: {blok[:40]!r}")
        a, b = [x.strip() for x in sat[1].split("-->")]
        out.append((sn(a), sn(b), " ".join(sat[2:])))
    return out


def sha256(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for p in iter(lambda: f.read(1 << 20), b""): h.update(p)
    return h.hexdigest()


def katilim_sorusu_mu(metin):
    m = metin.strip()
    return m.endswith("?") and re.search(r"\bnext\b", m, re.I) is not None and not JENERIK.search(m)


def dogrula(klasor):
    H, U, B = [], [], {}   # hatalar, uyarılar, bilgiler
    j = lambda ad: os.path.join(klasor, ad)
    def oku_json(ad):
        try: return json.load(open(j(ad), encoding="utf-8"))
        except Exception as e: H.append(f"{ad} okunamadı: {e}"); return None
    uretim, plan, perf = oku_json("uretim.json"), oku_json("sahne_plani.json"), oku_json("anlatim_performans.json")

    # 1. MP4
    mp4 = j("cikti/VIDEO.mp4"); sure = None
    if not os.path.isfile(mp4):
        H.append("cikti/VIDEO.mp4 yok — gerçek MP4 üretilmemiş")
    else:
        pr = ffprobe(mp4)
        if not pr: H.append("VIDEO.mp4 ffprobe ile okunamadı")
        else:
            v = next((s for s in pr["streams"] if s["codec_type"] == "video"), None)
            a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
            sure = float(pr["format"]["duration"]); B["sure_sn"] = round(sure, 2); B["mb"] = round(os.path.getsize(mp4) / 1e6, 1)
            if not v: H.append("video akışı yok")
            else:
                fps = eval(v.get("r_frame_rate", "0/1"))   # "30/1"
                beklenen = {"çözünürlük": (f"{v.get('width')}×{v.get('height')}", "1080×1920"), "fps": (round(fps, 2), 30.0),
                            "codec": (v.get("codec_name"), "h264"), "profil": (v.get("profile"), "High"),
                            "piksel": (v.get("pix_fmt"), "yuv420p"), "renk": (v.get("color_space"), "bt709")}
                for k, (deger, bek) in beklenen.items():
                    if deger != bek: H.append(f"MP4 {k}: {deger} (beklenen {bek})")
            if not a: H.append("ses akışı yok")
            else:
                if a.get("codec_name") != "aac": H.append(f"ses codec {a.get('codec_name')} (beklenen aac)")
                if a.get("sample_rate") != "48000": H.append(f"ses örnekleme {a.get('sample_rate')} (beklenen 48000)")
            if not (15 <= sure <= 180): H.append(f"süre {sure:.1f} sn Shorts aralığında değil")
            B["sha256"] = sha256(mp4)
            mt = os.path.getmtime(mp4)
            for ad in ("sahne_plani.json", "anlatim_performans.json"):
                if os.path.isfile(j(ad)) and os.path.getmtime(j(ad)) > mt + 1:
                    H.append(f"VIDEO.mp4, {ad} dosyasından ESKİ — son plan render edilmemiş")
    durum = oku_json("cikti/durum.json") if os.path.isfile(j("cikti/durum.json")) else None
    if durum:
        eksik = [s for s in ASAMALAR if (durum.get("asamalar") or {}).get(s, {}).get("durum") != "tamam"]
        if eksik: H.append(f"durum.json tamamlanmamış aşamalar: {', '.join(eksik)}")
        qc = (durum.get("asamalar") or {}).get("qc", {})
        B["qc_teknik"] = qc.get("teknik"); B["telaffuz_wer"] = (durum.get("asamalar") or {}).get("telaffuz", {}).get("wer")
        if qc.get("teknik") and not str(qc["teknik"]).startswith("10/10"): H.append(f"teknik QC {qc['teknik']}")
    else:
        H.append("cikti/durum.json yok")

    # 2. Kapak
    kp = j("teslim/THUMBNAIL.jpg")
    if not os.path.isfile(kp): H.append("teslim/THUMBNAIL.jpg yok")
    else:
        pr = ffprobe(kp)
        if not pr: H.append("kapak okunamadı")
        else:
            s0 = pr["streams"][0]; w, h = s0.get("width", 0), s0.get("height", 0); B["kapak"] = f"{w}×{h}"
            if w < 1080 or h < 1920 or abs(w / h - 9 / 16) > 0.01: H.append(f"kapak {w}×{h} (beklenen 9:16, ≥1080×1920)")
            if os.path.isfile(mp4) and os.path.getmtime(kp) + 1 < os.path.getmtime(mp4): U.append("kapak MP4'ten eski")

    # 3. Altyazı
    son_altyazi = ""
    sp = j("teslim/SUBTITLES.srt")
    if not os.path.isfile(sp): H.append("teslim/SUBTITLES.srt yok")
    else:
        try:
            cues = srt_oku(sp); B["altyazi_satir"] = len(cues)
            if not cues: H.append("SRT boş")
            for (a1, b1, _), (a2, b2, _) in zip(cues, cues[1:]):
                if a2 < a1 or b1 > a2 + 0.05: H.append("SRT zamanları sıralı/çakışmasız değil"); break
            if any(b <= a for a, b, _ in cues): H.append("SRT'de süresi sıfır/negatif satır")
            if sure and cues and cues[-1][1] > sure + 0.3: H.append(f"son altyazı ({cues[-1][1]:.2f} sn) videodan uzun ({sure:.2f} sn)")
            son_altyazi = cues[-1][2] if cues else ""
        except Exception as e: H.append(f"SRT ayrıştırılamadı: {e}")

    # 4. Paket
    bos = [ad for ad in PAKET if not os.path.isfile(j("teslim/" + ad)) or not open(j("teslim/" + ad), encoding="utf-8").read().strip()]
    if bos: H.append(f"eksik/boş paket dosyası: {', '.join(bos)}")

    # 5. Katılım sorusu (zorunlu)
    if perf:
        son = perf["cumleler"][-1]; metin = son.get("altyazi") or " ".join(p["metin"] for p in son["parcalar"])
        B["kapanis"] = metin
        if not katilim_sorusu_mu(metin): H.append("son anlatım cümlesi 'sırada ne?' sorusu değil (\"next\" içeren soru olmalı)")
        if JENERIK.search(" ".join(p["metin"] for c in perf["cumleler"] for p in c["parcalar"])): H.append("anlatımda jenerik abone ol/beğen kalıbı")
    if son_altyazi and not katilim_sorusu_mu(son_altyazi): H.append("son altyazı katılım sorusu değil")
    if plan:
        sh = sorted(plan["sahneler"], key=lambda x: x["cumle"])
        if not sh or sh[-1].get("tur") != "soru": H.append("sahne planı ekranda `soru` sahnesiyle bitmiyor")
    pc = j("teslim/PINNED_COMMENT.txt")
    if os.path.isfile(pc):
        t = open(pc, encoding="utf-8").read()
        if "?" not in t: H.append("sabitlenmiş yorum soru içermiyor")
        if JENERIK.search(t): H.append("sabitlenmiş yorumda jenerik abone ol kalıbı")

    # 6. Görsel standart
    if plan:
        turler = [s.get("tur") for s in plan["sahneler"] if s.get("tur") != "soru"]
        sin = sum(t in SINEMATIK for t in turler); har = turler.count("harita")
        B["sahne"] = f"{sin}/{len(turler)} 3D, harita {har}"
        if turler and sin / len(turler) < 0.5: H.append(f"3D/sinematik sahne oranı düşük ({sin}/{len(turler)}) — düz slayt videosu")
        if har > 2: H.append(f"harita sahnesi fazla ({har})")
        if not plan.get("vurgu_kelimeler"): U.append("vurgu_kelimeler tanımlı değil")
        bos_sahne = [f"{s.get('cumle')}:{s.get('tur')}" for s in plan["sahneler"] if s.get("tur") != "soru" and not somut_mu(s)]
        if bos_sahne: H.append(f"somut görseli olmayan sahne (yalnız yazı/sayaç/harita/grafik): {', '.join(bos_sahne)}")
        for s in plan["sahneler"]:
            if s.get("tur") != "foto": continue
            eksik = [k for k in ("kaynak", "lisans") if not str(s.get(k, "")).strip()]
            if s.get("koken") not in KOKENLER: eksik.append("koken (fotograf|arsiv|ai|prosedurel)")
            if eksik: H.append(f"foto sahnesi {s.get('cumle')}: eksik {', '.join(eksik)}")
            if s.get("dosya") and not os.path.isfile(s["dosya"] if os.path.isabs(s["dosya"]) else j(s["dosya"])): H.append(f"foto dosyası yok: {s['dosya']}")
        B["gorsel_koken"] = sorted({s.get("koken") for s in plan["sahneler"] if s.get("tur") == "foto"}) or ["prosedurel 3D"]

    # 9. Gelişim hedefi
    if uretim is not None and not str(uretim.get("gelisim_hedefi", "")).strip():
        H.append("uretim.json `gelisim_hedefi` yok (her videoda önceki videolara göre somut bir gelişim hedefi)")

    # 10. Kapanış sorusu tekrar etmiyor
    if perf:
        bu = nrm_soru(kapanis_metni(perf)); kok = os.path.dirname(os.path.abspath(klasor.rstrip("/")))
        for diger in sorted(os.listdir(kok)) if os.path.isdir(kok) else []:
            yol = os.path.join(kok, diger, "anlatim_performans.json")
            if diger == os.path.basename(os.path.abspath(klasor.rstrip("/"))) or not os.path.isfile(yol): continue
            try:
                if nrm_soru(kapanis_metni(json.load(open(yol, encoding="utf-8")))) == bu: H.append(f"kapanış sorusu {diger} ile aynı"); break
            except Exception: pass

    # 7. Ses ve lisans
    lis = j("ses/LISANS.txt"); yayin_uygun = False
    if not os.path.isfile(lis): H.append("ses/LISANS.txt yok")
    else:
        t = open(lis, encoding="utf-8").read()
        yayin_uygun = re.search(r"^yayin_uygun:\s*evet\s*$", t, re.M) is not None
        B["emir_ses_onayi"] = (re.search(r"^emir_ses_onayi:\s*(\S+)", t, re.M) or [None, "?"])[1]
        motor = (uretim or {}).get("ses_motoru", "")
        ad = motor.split("-", 1)[1] if motor.startswith("piper-") else motor
        ilk = t.splitlines()[0] if t else ""
        if motor.startswith("kokoro:"):   # ör. kokoro:5 → LISANS ilk satırı "Kokoro … (sid 5)"
            ad = "" if ("kokoro" in ilk.lower() and f"sid {motor.split(':')[1]})" in ilk) else motor
        if ad and ad not in ilk: H.append(f"LISANS.txt başka bir sesi kaydediyor (uretim.json: {motor}; LISANS: {ilk[:60]})")
        B["ses_motoru"] = motor

    B["yayina_hazir"] = not H and yayin_uygun
    if not H and not yayin_uygun: B["neden_hazir_degil"] = "ses lisansı/Emir onayı bekliyor (yayin_uygun: hayir)"
    return {"klasor": klasor, "hatalar": H, "uyarilar": U, "bilgi": B}


def md(sonuclar):
    satir = ["| Video | MP4 | Süre | Kapak | SRT | Paket+katılım | 3D sahne | Ses | Teknik QC | Durum |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sonuclar:
        b = r["bilgi"]; ad = os.path.basename(r["klasor"].rstrip("/"))
        durum = "✅ yayına hazır" if b.get("yayina_hazir") else ("⏳ onay bekliyor" if not r["hatalar"] else "❌ " + "; ".join(r["hatalar"]))
        satir.append(f"| {ad} | {b.get('mb', '—')} MB · `{b.get('sha256', '')[:12]}` | {b.get('sure_sn', '—')} sn | {b.get('kapak', '—')} | "
                     f"{b.get('altyazi_satir', '—')} satır | {'✅' if not r['hatalar'] else '—'} | {b.get('sahne', '—')} | "
                     f"{b.get('ses_motoru', '—')} (Emir: {b.get('emir_ses_onayi', '?')}) | {b.get('qc_teknik', '—')} | {durum} |")
    return "\n".join(satir)


def main(argv):
    js = "--json" in argv; mdo = argv[argv.index("--md") + 1] if "--md" in argv else None
    yollar = [a for a in argv if not a.startswith("--") and a != mdo]
    if not yollar: print(__doc__); return 2
    sonuc = [dogrula(y) for y in yollar]
    if js: print(json.dumps(sonuc, ensure_ascii=False, indent=1))
    else:
        for r in sonuc:
            print(("✓ " if not r["hatalar"] else "✗ ") + r["klasor"])
            for h in r["hatalar"]: print("   HATA  ", h)
            for u in r["uyarilar"]: print("   uyarı ", u)
            print("   " + ", ".join(f"{k}={v}" for k, v in r["bilgi"].items() if k != "sha256"))
    if mdo: open(mdo, "w", encoding="utf-8").write(md(sonuc) + "\n")
    return 1 if any(r["hatalar"] for r in sonuc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
