"""Export mix: the original voice, untouched, plus the sound-effect cues from build/sfx.json.

HyperFrames' own render re-levels the voice, so the export takes the picture from the render and builds the sound
here: voice at unity + each cue at its start with its gain, summed (no normalisation). Prints the loudness
before/after and the peak, and checks the voice did not shift in time (should print 0.0 ms).
Run: python mix.py <project> <render.mp4> <out.mp4>
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

from common import duration, load_plan


def loudness(path):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr.split("Summary:")[-1]
    return float(re.search(r"I:\s*(-?[\d.]+)", log).group(1)), float(re.search(r"Peak:\s*(-?[\d.]+)", log).group(1))


def pcm(path, seconds=40):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-t", str(seconds), "-vn", "-ac", "1", "-ar", "8000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def main(project, video, out):
    root, plan = load_plan(project)
    voice = Path(plan.VOICE).expanduser()
    cues = json.loads((root / "build/sfx.json").read_text())
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-i", str(voice)]
    chains, labels = [], ["[1:a]"]
    for i, c in enumerate(cues):
        cmd += ["-i", str(root / c["src"])]
        ms = round(c["start"] * 1000)
        chains.append(f"[{i + 2}:a]volume={c['volume']},adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    # the voice is padded with silence to the picture's length (the last graphic may hold past the last word)
    chains.insert(0, f"[1:a]apad=whole_dur={duration(video):.3f}[voice]")
    labels[0] = "[voice]"
    graph = ";".join(chains) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0[a]"
    cmd += ["-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ar", "44100", "-movflags", "+faststart", out]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True)

    vi, vp = loudness(voice)
    mi, mp = loudness(out)
    a, b = pcm(voice), pcm(out)
    lag = int(np.argmax(np.correlate(b[8000:16000 * 2], a[8000 + 400:16000 * 2 - 400], "valid"))) - 400
    print(f"voice only: {vi} LUFS, peak {vp} dBTP")
    print(f"with sfx:   {mi} LUFS, peak {mp} dBTP  ({len(cues)} cues)")
    print(f"voice offset after encode: {lag / 8:.1f} ms")


if __name__ == "__main__":
    main(*sys.argv[1:4])
