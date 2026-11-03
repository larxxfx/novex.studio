#!/usr/bin/env bash
# Kullanım: ./mix_voice.sh assets/seslendirme.mp3  -> out/novex_antarktika_sesli.mp4
set -e; cd "$(dirname "$0")"; V="$1"; [ -f "$V" ] || { echo "ses dosyası yok: $V"; exit 1; }
ffmpeg -hide_banner -loglevel error -y -i out/video_sessiz.mp4 -i out/muzik_efekt.wav -i "$V" -filter_complex \
 "[2:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5,asplit[v][sc];\
  [1:a]volume=-6dB[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];\
  [md][v]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -t 30 -movflags +faststart out/novex_antarktika_sesli.part.mp4
mv out/novex_antarktika_sesli.part.mp4 out/novex_antarktika_sesli.mp4 && echo "ok: out/novex_antarktika_sesli.mp4"
