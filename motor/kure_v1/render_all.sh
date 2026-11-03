#!/usr/bin/env bash
cd "$(dirname "$0")"; mkdir -p "${OUTDIR:-out/scenes}"
run(){ for s in "$@"; do python3 src/render.py scene $s ${OUTDIR:-out/scenes}/$s.mp4 > logs/$s.log 2>&1 || echo "HATA $s"; done; }
run s3 s1 s6 & run s4 s5 s2 & wait; echo BITTI
