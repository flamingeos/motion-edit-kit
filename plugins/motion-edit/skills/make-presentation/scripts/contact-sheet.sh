#!/usr/bin/env bash
# Tile the last frame of every clip in a folder into one review image.
# usage: bash contact-sheet.sh <videosDir> <out.png> [columns]
set -euo pipefail
DIR="$1"; OUT="$2"; COLS="${3:-4}"
TMP="$(mktemp -d)"
n=0
for f in "$DIR"/*.mp4; do
  n=$((n+1))
  ffmpeg -v error -y -sseof -0.3 -i "$f" -frames:v 1 -vf "scale=480:-1" "$TMP/$(printf '%03d' $n).png"
done
ROWS=$(( (n + COLS - 1) / COLS ))
ffmpeg -v error -y -pattern_type glob -i "$TMP/*.png" -vf "tile=${COLS}x${ROWS}:color=white" -frames:v 1 "$OUT"
rm -rf "$TMP"
echo "wrote $OUT ($n clips)"
