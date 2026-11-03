import sys, os, cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
ts = [float(x) for x in sys.argv[2:]]; out = sys.argv[1]
ims = [cv2.cvtColor(render.to_u8(render.frame(t)), cv2.COLOR_RGB2BGR) for t in ts]
for t, im in zip(ts, ims): cv2.imwrite(os.path.join(os.path.dirname(out), f"full_{t:05.2f}.jpg"), im, [cv2.IMWRITE_JPEG_QUALITY, 92])
small = [cv2.resize(im, (360, 640), interpolation=cv2.INTER_AREA) for im in ims]
cv2.imwrite(out, np.hstack(small))
