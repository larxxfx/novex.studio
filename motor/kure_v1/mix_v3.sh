#!/usr/bin/env bash
# V3 miks: seslendirme (işlenmiş) + müzik (konuşmada otomatik kısılır) + efekt  ->  -14 LUFS / ≤ -1 dBTP
# Kullanım: ./mix_v3.sh   (girdiler out/v3/ içinde)
set -e; cd "$(dirname "$0")/out/v3"

# 1) seslendirme: 48 kHz, gürültü/uğultu temizliği, sıcaklık + netlik EQ, kompresör, de-esser
ffmpeg -hide_banner -loglevel error -y -i seslendirme_22k.wav -af "\
aresample=48000:resampler=soxr,\
highpass=f=75:poles=2,lowpass=f=11000,\
equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=120:t=q:w=1.0:g=1.5,\
acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=3dB,\
deesser=i=0.4:m=0.5:f=0.5,\
aformat=channel_layouts=stereo" -c:a pcm_s24le ses_islenmis.wav

# 2) premiks: müzik ses tarafından kısılır (ducking), efektler hafif kısılır
ffmpeg -hide_banner -loglevel error -y -i ses_islenmis.wav -i muzik.wav -i efekt.wav -filter_complex "\
[0:a]asplit=3[v][sc1][sc2];\
[1:a]volume=-4dB[m];[m][sc1]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350:makeup=1[md];\
[2:a]volume=-5dB[e];[e][sc2]sidechaincompress=threshold=0.015:ratio=5:attack=8:release=300[ed];\
[v]volume=0dB[vv];[vv][md][ed]amix=inputs=3:normalize=0:duration=longest" -c:a pcm_s24le premiks.wav

# 3) iki geçişli doğrusal loudness: -14 LUFS, true peak -1.5 dBTP (güvenlik payı)
J=$(ffmpeg -hide_banner -i premiks.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -loglevel error -y -i premiks.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.84:attack=2:release=60:level=false,aresample=48000" -c:a pcm_s24le miks_final.wav
echo "miks tamam"
