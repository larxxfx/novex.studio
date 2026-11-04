"""PRODUCTION_LOG.md ve QUALITY_CONTROL.md'yi videolar/*/cikti/durum.json'lardan yeniden üretir (elle tutulan kayıt değil; tek kaynak durum.json).
Kullanım: python3 araclar/kayit_guncelle.py [--teslim <klasör_adı> ...]   (--teslim: sohbete gerçekten gönderilen videoları işaretler → teslim/TESLIM.txt)
"""
import datetime, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import teslim_dogrula  # noqa: E402  (yayına hazır kararı tek yerde: teslim_dogrula)

DEPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def oku(k):
    d = json.load(open(f"{k}/cikti/durum.json")); u = json.load(open(f"{k}/uretim.json"))
    p = json.load(open(f"{k}/paket.json")) if os.path.exists(f"{k}/paket.json") else {}
    lis = open(f"{k}/ses/LISANS.txt").read() if os.path.exists(f"{k}/ses/LISANS.txt") else ""
    t = f"{k}/teslim/TESLIM.txt"; teslim = open(t).read().strip() if os.path.exists(t) else ""
    return d, u, p, lis, teslim


def main():
    if "--teslim" in sys.argv:
        for ad in sys.argv[sys.argv.index("--teslim") + 1:]:
            open(f"{DEPO}/videolar/{ad}/teslim/TESLIM.txt", "w").write(f"teslim edildi {datetime.datetime.now().isoformat(timespec='minutes')} (sohbet: önizleme MP4 + paket)\n")
    pl = ["# Üretim kaydı (otomatik: `python3 araclar/kayit_guncelle.py`; kaynak `videolar/*/cikti/durum.json`)", "",
          "| Tarih | Slot | Klasör | Başlık | Aşama | MP4 | Teslim |", "|---|---|---|---|---|---|---|"]
    ql = ["# Kalite kontrol özeti (otomatik; ayrıntı `videolar/<klasör>/teslim/QC_REPORT.txt`)", "",
          "| Klasör | Teknik | Siyah/Donuk | Senkron | Ses/fon min | LUFS/TP | Telaffuz WER | Ses lisansı | Yayına hazır |", "|---|---|---|---|---|---|---|---|---|"]
    tds = []
    for k in sorted(glob.glob(f"{DEPO}/videolar/*/cikti/durum.json")):
        k = os.path.dirname(os.path.dirname(k)); ad = os.path.basename(k)
        try: d, u, p, lis, teslim = oku(k)
        except Exception as e: pl.append(f"| ? | ? | {ad} | okunamadı: {e} | | | |"); continue
        A = d["asamalar"]; son = next((a for a in reversed(["ses", "telaffuz", "altyazi", "render", "ses_tasarim", "miks", "birlestir", "qc", "kapak", "paket"]) if a in A), "—")
        mp4 = f"{A['birlestir']['mb']} MB" if "birlestir" in A else "yok"
        pl.append(f"| {u.get('tarih')} | {u.get('slot')} | `{ad}` | {p.get('baslik', '')} | {son} | {mp4} | {'teslim edildi' if teslim else '—'} |")
        q = A.get("qc", {}); m = A.get("miks", {}); t = A.get("telaffuz", {})
        lis_ok = any(l.strip() == "yayin_uygun: evet" for l in lis.splitlines())
        td = teslim_dogrula.dogrula(k); tds.append(td)
        hazir = "EVET" if td["bilgi"].get("yayina_hazir") else "HAYIR"
        if q: ql.append(f"| `{ad}` | {q.get('teknik')} | {q.get('siyah')}/{q.get('donuk')} | {q.get('senkron_ms')} ms | {m.get('ses_fon_min')} dB | {m.get('lufs_tp')} | "
                        f"{t.get('wer')}% | {'onaylı' if lis_ok else 'Emir onayı bekliyor'} | {hazir} |")
    ql += ["", "## Teslim doğrulama (`python3 araclar/teslim_dogrula.py`)", "",
           "MP4 + kapak + SRT + paket + zorunlu katılım sorusu + 3D sahne oranı + ses/lisans tutarlılığı. MP4'ü bu makinede olmayan klasör ❌ görünür (MP4 git dışıdır).", "",
           teslim_dogrula.md(tds)]
    for td in tds:
        r = os.path.join(td["klasor"], "REFERANS_QC.md")
        if os.path.exists(r): ql += ["", f"## Referansa göre: `{os.path.basename(td['klasor'])}`", "", open(r, encoding="utf-8").read().strip()]
    ql += ["", "Not: siyah=1 değerleri videonun ilk 0,2 sn'lik bilinçli siyahtan açılışıdır (blackdetect eşiği). İnsan dinleme/izleme kontrolü Emir'dedir."]
    open(f"{DEPO}/PRODUCTION_LOG.md", "w").write("\n".join(pl) + "\n"); open(f"{DEPO}/QUALITY_CONTROL.md", "w").write("\n".join(ql) + "\n")
    print("\n".join(pl[4:])); print(); print("\n".join(ql[4:]))


if __name__ == "__main__":
    main()
