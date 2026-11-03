#!/usr/bin/env bash
cd "$(dirname "$0")"; mkdir -p ${OD:-out/v3/scenes} logs
run(){ for k in "$@"; do python3 src/render_v3.py ${TL:-out/v3/zaman_cizelgesi.json} $k ${OD:-out/v3/scenes}/s$k.mp4 > logs/v3_s$k.log 2>&1 || echo "HATA s$k"; done; }
run 3 1 6 & run 4 5 2 & wait; echo BITTI
