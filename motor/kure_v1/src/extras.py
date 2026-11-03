"""SRT altyazı + kapak görseli. Kullanım: python3 extras.py"""
import os, sys, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from PIL import Image, ImageDraw
OUT = os.path.join(R.ROOT, "out")
def ts(x): ms = int(round(x * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
with open(os.path.join(OUT, "altyazi_tr.srt"), "w", encoding="utf-8") as f:
    for i, (a, b, lines, _) in enumerate(R.CAPS, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(min(b, 30.0))}\n{' '.join(lines)}\n\n")
# kapak: altyazısız kare + başlık
R.captions = lambda tx, t: None
im = R.to_u8(R.frame(float(os.environ.get("KAPAK_T", "4.6"))))
img = Image.fromarray(im).convert("RGBA")
ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
for y in range(0, 760):  # üstte okunabilirlik için koyu geçiş
    d.line((0, y, R.W, y), fill=(2, 6, 18, int(235 * (1 - y / 760) ** 1.3)))
img.alpha_composite(ov); d = ImageDraw.Draw(img)
def ctext(y, s, size, fill, name="InterDisplay-Black.otf"):
    f = R.font(name, size); d.text((R.W / 2, y), s, font=f, fill=fill, anchor="mm", stroke_width=5, stroke_fill=(3, 10, 28))
ctext(150, "NØVEX", 58, (150, 195, 255, 255))
ctext(300, "TÜRKİYE", 150, (255, 255, 255, 255))
ctext(440, "ANTARKTİKA'DA", 122, (70, 165, 255, 255))
ctext(570, "OLSAYDI?", 150, (255, 255, 255, 255))
img.convert("RGB").save(os.path.join(OUT, "kapak.jpg"), quality=92)
print("ok")
