#!/usr/bin/env bash
# NØVEX temiz oturum kurulumu — her zamanlanmış üretim oturumunun ilk adımı. Tekrar çalıştırmak güvenli (var olanı atlar).
# Kullanım: bash araclar/kurulum_ortam.sh      (depo kökünden)
# İndirir: kure_v1 varlıkları (varliklar dalı), sherpa-onnx, Piper ljspeech (lisansı doğrulanmış EN ses),
#          Whisper small.en (telaffuz kontrolü). Gizli bilgi kullanmaz; ücretsiz ve herkese açık kaynaklar.
set -euo pipefail
DEPO="$(cd "$(dirname "$0")/.." && pwd)"; C="$HOME/.novex_cache"; mkdir -p "$C"
GH=https://github.com/k2-fsa/sherpa-onnx/releases/download
indir() {  # indir <url> <hedef_klasör_adı>
  local url="$1" ad="$2"
  if [ -d "$C/$ad" ]; then echo "✓ $ad (var)"; return; fi
  echo "↓ $ad"; local tmp; tmp="$(mktemp -d "$C/.dl.XXXX")"
  curl -fsSL --retry 3 -o "$tmp/a.tar.bz2" "$url"
  tar xjf "$tmp/a.tar.bz2" -C "$tmp" && rm "$tmp/a.tar.bz2"
  mv "$tmp/$ad" "$C/$ad" && rmdir "$tmp" 2>/dev/null || true
}
# 1) motor varlıkları (Natural Earth + build) — ayrı 'varliklar' dalından, sha256 doğrulamalı
if [ ! -f "$DEPO/motor/kure_v1/build/geo.json" ]; then
  echo "↓ kure_v1 varlıkları"; tmp="$(mktemp -d)"
  git -C "$tmp" init -q && git -C "$tmp" remote add origin "$(git -C "$DEPO" remote get-url origin)"
  git -C "$tmp" fetch -q --depth 1 origin varliklar && git -C "$tmp" checkout -q FETCH_HEAD
  (cd "$tmp" && sha256sum -c SHA256SUMS)
  tar xzf "$tmp/kure_v1_varliklar.tar.gz" -C "$DEPO/motor/kure_v1" && rm -rf "$tmp"
else echo "✓ kure_v1 varlıkları (var)"; fi
# 2) sherpa-onnx çalıştırıcıları
indir "$GH/v1.12.15/sherpa-onnx-v1.12.15-linux-x64-shared.tar.bz2" sherpa-onnx-v1.12.15-linux-x64-shared
# 3) EN anlatım sesi: Piper en_US-ljspeech-high (MIT + LJ Speech kamu malı) — anlatim_ifade.py 'piper-ljspeech'
mkdir -p "$C/dl_piper"; [ -d "$C/dl_piper/vits-piper-en_US-ljspeech-high" ] || { C0="$C"; C="$C/dl_piper"; indir "$GH/tts-models/vits-piper-en_US-ljspeech-high.tar.bz2" vits-piper-en_US-ljspeech-high; C="$C0"; }
# 3b) erkek anlatıcı adayı: Piper en_US-norman-medium (LibriVox kamu malı, sıfırdan eğitim; rhasspy/piper-voices MIT) — anlatim_ifade.py 'piper-norman'
mkdir -p "$C/dl_erkek"; [ -d "$C/dl_erkek/vits-piper-en_US-norman-medium" ] || { C0="$C"; C="$C/dl_erkek"; indir "$GH/tts-models/vits-piper-en_US-norman-medium.tar.bz2" vits-piper-en_US-norman-medium; C="$C0"; }
# 4) telaffuz kontrolü: Whisper small.en
indir "$GH/asr-models/sherpa-onnx-whisper-small.en.tar.bz2" sherpa-onnx-whisper-small.en
# 5) Python bağımlılıkları (sistemde olmalı; pip ağı kapalı olabilir)
python3 -c "import numpy, cv2, PIL, scipy" && echo "✓ python: numpy cv2 PIL scipy"
F="$(ffmpeg -hide_banner -filters 2>/dev/null || true)"; case "$F" in *rubberband*) echo "✓ ffmpeg (+rubberband)";; *) echo "⚠ ffmpeg rubberband yok (perde ayarı atlanır)";; esac
if [ -f /usr/share/fonts/opentype/inter/InterDisplay-Bold.otf ]; then echo "✓ Inter fontları"; else echo "⚠ Inter fontu yok"; fi
echo "KURULUM TAMAM"
