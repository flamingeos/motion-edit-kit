"""Set up (or top up) a project folder for one video. Safe to run again: it only does what is missing.

  1. footage   the edited video, re-encoded to 30 fps H.264 → assets/footage.mp4 (the sound stays on the original:
               the export mix uses the file you pass as --video untouched)
  2. graphics  the finished clips (NN-slug.mp4) + EDITOR-CUE-SHEET.md → assets/gfx/
  3. words     Whisper transcript + forced alignment → transcript/footage.{txt,srt,json}, footage-aligned.json
  4. plan.py   started from templates/plan.py with the footage's numbers filled in
  5. a frame of the footage (assets/frame.png) to read the speaker's position and wall colour from

Run: python prep.py <project> --video EDITED.mp4 [--graphics CLIPS_FOLDER] [--lang es] [--title "Client – video"] [--no-align]
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from common import ENGINE, FPS, duration, voice_loudness


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--video", help="the edited video (cuts + colour done); its sound is used untouched")
    ap.add_argument("--graphics", help="folder with NN-slug.mp4 clips and EDITOR-CUE-SHEET.md")
    ap.add_argument("--lang", help="spoken language (en, es, …); Whisper guesses if left out")
    ap.add_argument("--title", help="name used in the review sheets")
    ap.add_argument("--model", default="turbo", help="Whisper model (turbo is fast and accurate)")
    ap.add_argument("--no-align", action="store_true",
                    help="keep Whisper's own word times (up to ~0.35 s off) instead of the MMS aligner, whose model is "
                         "licensed CC-BY-NC 4.0 (non-commercial)")
    a = ap.parse_args()

    root = Path(a.project).expanduser().resolve()
    for d in ("assets/gfx", "assets/cut", "transcript", "build", "renders"):
        (root / d).mkdir(parents=True, exist_ok=True)
    footage = root / "assets/footage.mp4"
    video = Path(a.video).expanduser().resolve() if a.video else None

    if video and not footage.exists():
        print("1. footage → assets/footage.mp4")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-r", FPS, "-c:v", "libx264", "-preset", "medium",
             "-crf", "15", "-g", FPS, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
             "-movflags", "+faststart", footage])

    if a.graphics:
        src = Path(a.graphics).expanduser()
        clips = sorted(src.glob("[0-9][0-9]-*.mp4"))
        if not clips:
            raise SystemExit(f"no NN-slug.mp4 clips in {src}")
        for p in clips + [q for q in [src / "EDITOR-CUE-SHEET.md"] if q.exists()]:
            shutil.copy2(p, root / "assets/gfx" / p.name)
        print(f"2. graphics → assets/gfx ({len(clips)} clips)")

    words = root / "transcript/footage.json"
    aligned = root / "transcript/footage-aligned.json"
    if footage.exists() and not aligned.exists():
        print("3. transcribing + aligning the words …", flush=True)
        if not words.exists():
            run([sys.executable, ENGINE / "transcribe.py", footage, "--out", root / "transcript/footage", "--model", a.model]
                + (["--lang", a.lang] if a.lang else []))
        if a.no_align:
            shutil.copy2(words, aligned)
        else:
            run([sys.executable, ENGINE / "align.py", footage, words, "--out", aligned])

    if not (root / "hyperframes.json").exists():
        (root / "hyperframes.json").write_text(json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}}, indent=2) + "\n")
        (root / "meta.json").write_text(json.dumps({"id": root.name, "name": root.name}, indent=2) + "\n")

    if footage.exists():
        dur = round(duration(footage), 3)
        if not (root / "plan.py").exists():
            plan = (ENGINE.parent / "templates/plan.py").read_text()
            plan = (plan.replace("__TITLE__", a.title or root.name).replace("__VOICE__", str(video or footage))
                    .replace("__DURATION__", f"{dur}").replace("__TOTAL__", f"{dur:.2f}"))
            (root / "plan.py").write_text(plan)
            print("4. plan.py started — fill in CUES, EDL, CUTOUTS, SFX")
        frame = root / "assets/frame.png"
        if not frame.exists():
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur / 2:.2f}", "-i", footage, "-frames:v", "1", frame])
        print(f"\nfootage: {dur:.2f}s · voice {voice_loudness(video or footage)} LUFS · frame: assets/frame.png")
    for p in sorted((root / "assets/gfx").glob("[0-9][0-9]-*.mp4")):
        print(f"  {p.name:48s} {duration(p):5.2f}s")


if __name__ == "__main__":
    main()
