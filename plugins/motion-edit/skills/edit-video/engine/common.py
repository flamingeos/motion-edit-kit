"""Shared by every engine script: load a video's plan.py and probe media.

Every script takes the project folder as its first argument; everything that changes from video to video lives in
that folder's plan.py (see templates/plan.py), so the engine itself never needs editing.
"""

import importlib.util
import re
import subprocess
from pathlib import Path

import numpy as np

FPS = 30    # the composition, the footage (prep.py re-encodes it to 30) and the graphic clips all run at 30 fps
ENGINE = Path(__file__).resolve().parent


def load_plan(project):
    root = Path(project).expanduser().resolve()
    spec = importlib.util.spec_from_file_location("plan", root / "plan.py")
    if spec is None or not (root / "plan.py").exists():
        raise SystemExit(f"no plan.py in {root} (start one with prep.py)")
    plan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plan)
    return root, plan


def duration(path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def voice_loudness(path) -> float:
    """Median momentary loudness of the speech (LUFS): the reference every sound-effect level is set against.
    Frames under -40 LUFS (pauses, room tone) are left out."""
    log = subprocess.run(["ffmpeg", "-hide_banner", "-v", "verbose", "-i", str(path), "-vn", "-af", "ebur128=framelog=verbose",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    m = np.array([float(x) for x in re.findall(r"M:\s*(-?[\d.]+)", log)])
    return round(float(np.median(m[m > -40])), 1)
