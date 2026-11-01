#!/bin/bash
# One-time setup for the motion-edit kit on a Mac with Apple silicon. Safe to run again: it only adds what is missing.
#   - ffmpeg, Node and Python 3.10–3.14: uses the ones already installed, else installs them with Homebrew
#   - Python packages for the edit-video engine (Whisper, the word aligner) in ~/.motion-edit-kit/venv
#   - the sound effects, downloaded from Mixkit into ~/.motion-edit-kit/sounds (the kit ships none: skills/edit-video/sounds.txt)
#   - the presentation renderer (playwright-core) and a check for Google Chrome
#   - HyperFrames (fetched once by npx, then cached)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
KIT="$HOME/.motion-edit-kit"
mkdir -p "$KIT"

if [ "$(uname -m)" != "arm64" ]; then
  echo "This kit needs a Mac with Apple silicon (M1 or newer): PyTorch, which runs Whisper, no longer supports Intel Macs."
  exit 1
fi
brew_install() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is needed to install $1: https://brew.sh — install it, then run this again."
    exit 1
  fi
  brew install "$1"
}
command -v ffmpeg >/dev/null 2>&1 || brew_install ffmpeg
command -v npx >/dev/null 2>&1 || brew_install node

echo "→ Python packages"
if [ ! -x "$KIT/venv/bin/python" ]; then
  PYTHON=""
  for c in python3.12 python3.13 python3.11 python3.14 python3; do   # Apple's own python3 (3.9) is too old
    if command -v "$c" >/dev/null 2>&1 &&
       "$c" -c 'import sys; sys.exit(not (3, 10) <= sys.version_info[:2] <= (3, 14))' 2>/dev/null; then
      PYTHON="$(command -v "$c")"
      break
    fi
  done
  if [ -z "$PYTHON" ]; then
    brew_install python@3.12
    PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
  fi
  "$PYTHON" -m venv "$KIT/venv"
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
