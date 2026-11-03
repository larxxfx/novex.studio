#!/usr/bin/env bash
# Sahneleri birleştir, sesi ekle, doğrula. Video yeniden kodlanmaz.
set -e; cd "$(dirname "$0")/out"
printf "file 'scenes/%s.mp4'\n" s1 s2 s3 s4 s5 s6 > concat.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i concat.txt -c copy video_sessiz.mp4
ffmpeg -hide_banner -loglevel error -y -i video_sessiz.mp4 -i muzik_efekt.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart novex_antarktika.part.mp4
mv novex_antarktika.part.mp4 novex_antarktika.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration -show_entries format=duration -of compact novex_antarktika.mp4
