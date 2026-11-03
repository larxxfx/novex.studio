#!/usr/bin/env bash
# Ses araçlarını (sherpa-onnx, Whisper-medium, taslak Piper sesleri) ~/.novex_cache altına kurar.
# Yalnızca GitHub sürüm indirmeleri kullanılır. Var olanları yeniden indirmez.
set -e
C="$HOME/.novex_cache"; mkdir -p "$C"; cd "$C"
B=https://github.com/k2-fsa/sherpa-onnx/releases/download
get(){ local p=$1 d=$(basename "$1" .tar.bz2); [ -d "$d" ] && { echo "var: $d"; return; }; curl -sL --max-time 900 -o "$d.tar.bz2" "$B/$p" && tar xjf "$d.tar.bz2" && rm "$d.tar.bz2" && echo "kuruldu: $d"; }
get v1.12.15/sherpa-onnx-v1.12.15-linux-x64-shared.tar.bz2
get asr-models/sherpa-onnx-whisper-medium.tar.bz2
get tts-models/vits-piper-tr_TR-fettah-medium.tar.bz2      # YALNIZCA TASLAK (lisans: marka/SESLENDIRME.md)
get tts-models/vits-piper-tr_TR-fahrettin-medium.tar.bz2   # YALNIZCA TASLAK
echo "tamam: $C"
