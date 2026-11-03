"""05_seslendirme.txt → TTS/hizalama satırları: yorumları ve *vurgu* yıldızlarını atar."""
import sys
for l in open(sys.argv[1], encoding="utf-8"):
    l = l.strip()
    if l and not l.startswith("#"):
        print(l.replace("*", ""))
