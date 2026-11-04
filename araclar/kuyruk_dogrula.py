"""TASK_QUEUE.md doğrulayıcı — Claude ve ChatGPT'nin ortak kuyruğundaki çakışmaları yakalar.
Kurallar: ID biçimi T-YYYYMMDD-NN ve benzersiz; Sahip ∈ {Claude, ChatGPT, Emir}; Durum geçerli; 'tamam' için Sonuç/kanıt boş olamaz;
aynı görev metni iki açık satırda olamaz (tekrar engeli); 'devam' durumunda Sahip zorunlu.
Kullanım: python3 araclar/kuyruk_dogrula.py [TASK_QUEUE.md]   → 0: temiz, 1: hata (satır numarasıyla)
"""
import re, sys, unicodedata

DURUM = {"açık", "devam", "inceleme", "tamam", "engelli", "iptal"}
SAHIP = {"Claude", "ChatGPT", "Emir"}
IDRE = re.compile(r"^T-\d{8}-\d{2}$")


def satirlar(metin):
    out = []
    for no, l in enumerate(metin.splitlines(), 1):
        if not l.startswith("| T-"): continue
        h = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(h) < 7: out.append((no, None, f"sütun sayısı {len(h)} < 7")); continue
        out.append((no, dict(zip(["id", "gorev", "sahip", "oncelik", "durum", "tarih", "sonuc"], h[:7])), None))
    return out


def dogrula(metin):
    hatalar, gorulen, aktif = [], {}, {}
    for no, s, e in satirlar(metin):
        if e: hatalar.append(f"satır {no}: {e}"); continue
        if not IDRE.match(s["id"]): hatalar.append(f"satır {no}: geçersiz ID '{s['id']}'")
        if s["id"] in gorulen: hatalar.append(f"satır {no}: ID {s['id']} tekrar (ilk: satır {gorulen[s['id']]})")
        gorulen.setdefault(s["id"], no)
        if s["sahip"] not in SAHIP: hatalar.append(f"satır {no}: sahip '{s['sahip']}' geçersiz")
        if s["durum"] not in DURUM: hatalar.append(f"satır {no}: durum '{s['durum']}' geçersiz")
        if s["durum"] == "tamam" and len(s["sonuc"]) < 3: hatalar.append(f"satır {no}: 'tamam' ama kanıt yok")
        anahtar = "".join(c for c in unicodedata.normalize("NFKD", s["gorev"].casefold()) if not unicodedata.combining(c))
        anahtar = re.sub(r"\W+", " ", anahtar).strip()   # Türkçe İ/ı ve noktalama farkı tekrarı gizlemesin
        if s["durum"] in ("açık", "devam", "inceleme"):
            if anahtar in aktif: hatalar.append(f"satır {no}: aynı görev zaten açık (satır {aktif[anahtar]})")
            aktif.setdefault(anahtar, no)
    return hatalar


if __name__ == "__main__":
    yol = sys.argv[1] if len(sys.argv) > 1 else "TASK_QUEUE.md"
    h = dogrula(open(yol, encoding="utf-8").read())
    print("\n".join(h) if h else f"✓ {yol}: {len(satirlar(open(yol, encoding='utf-8').read()))} görev, çakışma yok")
    sys.exit(1 if h else 0)
