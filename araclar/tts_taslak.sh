#!/usr/bin/env bash
# TASLAK seslendirme (zamanlama/animatik için). YAYINLANAMAZ — lisans: marka/SESLENDIRME.md
# Kullanım: araclar/tts_taslak.sh videolar/<video>/05_seslendirme.txt videolar/<video>/ses [fettah|fahrettin]
set -e
TXT="$1"; OUT="$2"; V="${3:-fettah}"; C="$HOME/.novex_cache"
D="$C/vits-piper-tr_TR-$V-medium"; S="$C/sherpa-onnx-v1.12.15-linux-x64-shared"
[ -d "$D" ] || { echo "Önce: bash araclar/kurulum.sh"; exit 1; }
mkdir -p "$OUT"; export LD_LIBRARY_PATH="$S/lib"
TMP=$(mktemp -d); i=0; : > "$TMP/list.txt"
python3 -I "$(dirname "$0")/metin_hazirla.py" "$TXT" | while IFS= read -r line; do
  i=$((i+1)); "$S/bin/sherpa-onnx-offline-tts" --vits-model="$D/tr_TR-$V-medium.onnx" --vits-tokens="$D/tokens.txt" \
    --vits-data-dir="$D/espeak-ng-data" --vits-length-scale=1.05 --vits-noise-scale=0.5 --vits-noise-scale-w=0.5 --num-threads=2 --output-filename="$TMP/$i.wav" "$line" >/dev/null 2>&1
  ffmpeg -v error -y -f lavfi -i anullsrc=r=22050:cl=mono -t 0.45 "$TMP/p$i.wav"
  printf "file '%s'\nfile '%s'\n" "$TMP/$i.wav" "$TMP/p$i.wav" >> "$TMP/list.txt"
done
ffmpeg -v error -y -f concat -safe 0 -i "$TMP/list.txt" -c:a pcm_s16le "$OUT/taslak_tts_$V.wav"
printf "kaynak: TASLAK-piper-%s\nlisans: veri CC0 beyanı doğrulanamadı; lessac (yalnızca araştırma) türevi\nyayin_uygun: hayir\n" "$V" > "$OUT/LISANS.txt"
rm -rf "$TMP"; echo "TASLAK hazır: $OUT/taslak_tts_$V.wav  (yayin_uygun: hayir)"
