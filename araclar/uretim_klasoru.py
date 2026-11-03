"""Seçilen fikirlerden İngilizce üretim klasörleri oluşturur (mevcut klasörlerin üzerine yazmaz).

Kullanım:
  python3 araclar/uretim_klasoru.py <secim.json> --tarih 2026-11-05 [--slotlar 0800,1200,1600,2000]
secim.json: araclar/fikir_puanla.py --cikti çıktısı. Slotlar seçim sırasıyla (puan sırası) atanır; editör değiştirebilir.
Oluşan: videolar/<tarih>_<HHMM>_<id>/ → 01_brief.md (sablonlar/en/SHORT.md + ön bilgi), 02_sources.md, 05_narration_en.txt,
        06_package.md, qc/ . Var olan klasör atlanır.
"""
import argparse, json, os, re, sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("secim"); p.add_argument("--tarih", required=True)
    p.add_argument("--slotlar", default="0800,1200,1600,2000")
    a = p.parse_args(argv)
    secim = json.load(open(a.secim, encoding="utf-8"))["secilen"]
    slotlar = a.slotlar.split(",")
    sablon = open(os.path.join(KOK, "sablonlar", "en", "SHORT.md"), encoding="utf-8").read()
    olusan = []
    for s, slot in zip(secim, slotlar):
        ad = f"{a.tarih}_{slot}_{s['id']}"; d = os.path.join(KOK, "videolar", ad)
        if os.path.exists(d):
            print(f"atlandı (var): {ad}"); continue
        os.makedirs(os.path.join(d, "qc"))
        on = (sablon.replace("YYYY-MM-DD_HHMM_slug", ad).replace('"08:00 | 12:00 | 16:00 | 20:00"', f'"{slot[:2]}:{slot[2:]}"')
              .replace("category: A | B | C | D | E | F | G | H", f"category: {s['category']}")
              .replace("mode: REALITY | SPECULATION | FICTION", f"mode: {s['mode']}")
              .replace("score: 0 ", f"score: {s['total']} ").replace("# <Working title>", f"# {s['title']}"))
        on = re.sub(r"(## 1\. Topic, category, mode\n- Topic: )…", r"\1" + s["title"].replace("\\", "") + f"\n- Editor notes: {s.get('notes', '')}", on)
        open(os.path.join(d, "01_brief.md"), "w", encoding="utf-8").write(on)
        kaynak = "| # | Claim (as narrated) | Source | Type | Status |\n|---|---|---|---|---|\n" if s["mode"] != "FICTION" else "FICTION — no factual claims. Any real-world reference must still be sourced.\n"
        open(os.path.join(d, "02_sources.md"), "w", encoding="utf-8").write(f"# Sources — {s['title']}\n\n{kaynak}")
        open(os.path.join(d, "05_narration_en.txt"), "w", encoding="utf-8").write("# One sentence per line. *emphasis*. Lines starting with # are not read.\n")
        open(os.path.join(d, "06_package.md"), "w", encoding="utf-8").write(f"# Publishing package — {s['title']}\n\n## Title\n## Description\n## Hashtags\n## Pinned comment\n## Thumbnail\n")
        olusan.append(ad)
    for x in olusan: print("oluşturuldu:", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
