#!/bin/bash
# One-time setup for the motion-edit kit on a Mac. Safe to run again: it only adds what is missing.
#   - ffmpeg, Node, Python 3.12 (Homebrew)
#   - Python packages for the edit-video engine (Whisper, the word aligner) in ~/.motion-edit-kit/venv
#   - the sound effects, downloaded from Mixkit into ~/.motion-edit-kit/sounds (the kit ships none: skills/edit-video/sounds.txt)
#   - the presentation renderer (playwright-core) and a check for Google Chrome
#   - HyperFrames (fetched once by npx, then cached)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
KIT="$HOME/.motion-edit-kit"
mkdir -p "$KIT"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is needed first: https://brew.sh — install it, then run this again."
  exit 1
fi
for pkg in ffmpeg node python@3.12; do
  brew list --formula "$pkg" >/dev/null 2>&1 || brew install "$pkg"
done

echo "→ Python packages"
if [ ! -x "$KIT/venv/bin/python" ]; then
  "$(brew --prefix python@3.12)/bin/python3.12" -m venv "$KIT/venv"
fi
"$KIT/venv/bin/pip" install --quiet --upgrade pip
"$KIT/venv/bin/pip" install --quiet -r "$HERE/requirements.txt"

echo "→ Sound effects (from Mixkit)"
grep -v '^#' "$HERE/skills/edit-video/sounds.txt" | while read -r file url; do
  [ -s "$KIT/sounds/$file" ] && continue
  mkdir -p "$KIT/sounds/$(dirname "$file")"
  curl -fsSL "$url" -o "$KIT/sounds/$file"
done

echo "→ Presentation renderer"
(cd "$HERE/skills/make-presentation/scripts" && npm install --silent)
CHROME="${CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || echo "! Google Chrome not found: install it, or set CHROME_PATH (the presentation renderer needs it)"

echo "→ HyperFrames"
npx --yes hyperframes@latest --help >/dev/null

echo
echo "Done. Engine Python: $KIT/venv/bin/python"
