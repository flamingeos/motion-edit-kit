"""Sound effects: few and exact, every sound has something moving on screen at that moment.

The cue table is the plan's SFX list. Each cue names WHEN (a graphic's entrance/expand, or a moment inside a clip
in that clip's own media time, so it follows the pacing holds), WHICH sound, and HOW FAR UNDER THE VOICE.
build.py calls emit(rows, root, plan) and gets:
  <audio> tags          for the Studio preview (index.html)
  build/sfx.json        the same cues for the export mix (mix.py keeps the original voice untouched)
  build/sfx.md          the cue sheet for review

Placement: the sound's loudest moment lands one frame after the picture's hit (light before sound), entrances on
the fastest frame of their ease. Level: "under" = dB below the voice's median momentary loudness (measured on the
plan's VOICE unless the plan sets VOICE_LOUDNESS); each prepared file's own momentary max is measured, so levels
are comparable.
Sounds: Mixkit (free licence), downloaded by setup.sh from the links in ../sounds.txt; the kit ships no sound
files. Clip moments come from the clips' own animation script (the presentation HTML), which runs in media time.
"""

import json
import os
import re
import subprocess
from pathlib import Path

import numpy as np

from common import FPS, voice_loudness

F = 1 / FPS
DEFAULT_LIBRARY = Path.home() / ".motion-edit-kit/sounds"

# key: (library file, start, length, fade-out) — trims keep only the part that matches the motion.
# A new library file also needs its line (path + source link) in ../sounds.txt, so setup.sh can fetch it.
SOUNDS = {
    "air-quick":  ("transition/air-woosh-quick.mp3", 0, 1.2, 0.4),     # Quick air woosh
    "swoosh":     ("transition/swoosh-quick.mp3", 0, None, 0),         # Fast small sweep transition
    "sweep":      ("transition/sweep-short.mp3", 0, None, 0),          # Short transition sweep
    "zoom-soft":  ("transition/transition-soft.mp3", 0, None, 0),      # Air zoom vacuum
    "zoom-air":   ("camera/zoom-air-fast.mp3", 0, None, 0),            # Fast air zoom
    "whip":       ("transition/wind-swoosh-short.mp3", 0, 0.8, 0.3),   # Short wind swoosh
    "whoosh":     ("transition/whoosh-fast.mp3", 0, None, 0),          # Fast whoosh transition
    "deep":       ("transition/air-woosh-deep.mp3", 0, 2.4, 0.8),      # Deep air woosh
    "swirl":      ("transition/whoosh-swirl.mp3", 1.25, 1.1, 0.2),     # Swirling whoosh (its rising end only)
    "marker":     ("text/marker-pen-line.mp3", 0, 0.6, 0.2),           # Pen marker line (underline)
    "strike":     ("text/marker-pen-line.mp3", 0, 0.3, 0.1),           # Pen marker line, short (strike-through)
    "typing":     ("text/typewriter-digital.mp3", 0, 1.5, 0.05),       # Digital typing
    "stamp":      ("impact/hit-blow.mp3", 0, None, 0),                 # Blow hit (a stamp lands)
    "thump":      ("impact/bass-hit-short.mp3", 0, None, 0),           # Short bass hit
    "notify":     ("ui/ui-message-pop.mp3", 0, 0.4, 0.1),              # Message pop alert
    "click":      ("ui/ui-select-click.mp3", 0, 0.3, 0.1),             # Select click
    "select":     ("ui/ui-option-select.mp3", 0, 0.6, 0.2),            # Interface option select
    "pop":        ("ui/ui-popup-dry.mp3", 0, None, 0),                 # Dry pop up notification alert
    "confirm":    ("ui/ui-confirm-tone.mp3", 0, 0.7, 0.2),             # Confirmation tone
    "toggle":     ("ui/switch-light.mp3", 0, None, 0),                 # Light switch
    "chime":      ("ui/chime-crystal.mp3", 0, 1.2, 0.5),               # Crystal chime
    "counter":    ("data/data-compute.mp3", 0, 2.4, 0.5),              # Number counting up
    "downer":     ("film/cassette-stretch.mp3", 0.15, 1.9, 0.5),       # Tape slowing down (something drops)
    "shutter":    ("camera/camera-lens-shutter.mp3", 0, 0.6, 0.2),     # Lens shutter
    "confetti":   ("light/sparkle-poof-hit.mp3", 0, 1.6, 0.6),         # Magic sparkle poof hit
    "shimmer":    ("light/shimmer-sparkle-sweep.mp3", 0, None, 0),     # Sweeping sparkle presentation intro
    "sparkle":    ("light/sparkle-touch.mp3", 0, 1.4, 0.6),            # Magic sparkle touch
    "riser":      ("light/light-sweep-magic.mp3", 0, 1.8, 0.05),       # Magical light sweep (rising half only)
    "boom":       ("impact/impact-deep-whoosh.mp3", 0, 2.5, 0.8),      # Cinematic whoosh deep impact
}

ONSET = {"click", "select", "pop", "toggle"}   # aligned by their attack, not their loudest point

# Fastest frame of each entrance (template.html eases): out-eases peak early, in-out eases at the middle.
ENTER_PEAK_F = {"zoom": 4, "slow-zoom": 6, "whip": 5, "push": 7, "pop": 4, "slide": 3, "iris": 8}   # pop: 2-frame delay + 2


def library(plan):
    return Path(getattr(plan, "SOUND_LIBRARY", None) or os.environ.get("MOTION_EDIT_SOUNDS") or DEFAULT_LIBRARY).expanduser()


def prepare(key, sounds, lib, out_dir):
    src, ss, length, fade = sounds[key]
    out = out_dir / f"{key}.wav"
    if not out.exists():
        if not (lib / src).exists():
            raise SystemExit(f"sfx: {lib / src} not found — run setup.sh (it downloads the sounds in sounds.txt)")
        out_dir.mkdir(parents=True, exist_ok=True)
        af = []
        if fade:
            dur = length if length else float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(lib / src)],
                capture_output=True, text=True).stdout) - ss
            af.append(f"afade=t=out:st={dur - fade:.3f}:d={fade}")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", str(lib / src)]
        if length:
            cmd += ["-t", str(length)]
        cmd += (["-af", ",".join(af)] if af else []) + ["-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(out)]
        subprocess.run(cmd, check=True)
    return out


def measure(path, onset=False):
    """(duration, hit time, momentary-loudness max in LUFS). The hit is the loudest 20 ms — or, for clicks, where the
    attack first reaches half of it (a click's peak trails its attack, and an early click reads as out of sync)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    n = 882
    rms = [np.sqrt(np.mean(a[i:i + n] ** 2)) for i in range(0, len(a) - n, n // 2)]
    hit = int(np.argmax(np.array(rms) >= max(rms) / 2)) if onset else int(np.argmax(rms))
    peak = hit * (n // 2) / 44100 + n / 2 / 44100
    log = subprocess.run(["ffmpeg", "-hide_banner", "-v", "verbose", "-i", str(path), "-af",
                          "apad=pad_dur=0.5,ebur128=framelog=verbose", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = max(float(x) for x in re.findall(r"M:\s*(-?[\d.]+)", log))
    return len(a) / 44100, peak, m


def emit(rows, root, plan):
    R = {r["id"]: r for r in rows}
    media_start = plan.MEDIA_START
    sounds = {**SOUNDS, **getattr(plan, "SOUNDS", {})}
    onset = ONSET | set(getattr(plan, "ONSET", ()))
    lib, out_dir = library(plan), root / "assets/sfx"
    voice_m = getattr(plan, "VOICE_LOUDNESS", None)
    if voice_m is None:
        voice_m = voice_loudness(Path(plan.VOICE).expanduser())

    def media(cid, m):
        r = R[cid]
        if not r.get("pieces"):
            return r["start"] + m - media_start
        for p in r["pieces"]:
            if p["kind"] == "play" and p["media"] - 1e-6 <= m < p["media"] + p["frames"] / FPS:
                return p["start"] + m - p["media"]
        raise SystemExit(f"sfx: {cid}@{m} falls in a held (frozen) part of the clip")

    def when(spec):
        cid, rest = spec[:2], spec[2:].rstrip("<>")
        r = R[cid]
        if rest.startswith("@"):
            return media(cid, float(rest[1:]))
        kind = rest[1:]
        if kind == "enter":
            return r["start"] + ENTER_PEAK_F[r["enter"]] * F
        if kind == "expand":
            return r["expandAt"] + 9 * F
        raise SystemExit(f"sfx: unknown anchor {spec}")

    cues, info = [], {}
    for n, (spec, key, under, what) in enumerate(plan.SFX, 1):
        path = prepare(key, sounds, lib, out_dir)
        info.setdefault(key, measure(path, onset=key in onset))
        dur, peak, m = info[key]
        t = when(spec)
        r = R[spec[:2]]
        if not r["start"] - 1e-6 <= t <= r["windowEnd"] + 1e-6:
            raise SystemExit(f"sfx: {spec} at {t:.2f}s is outside its graphic ({r['start']:.2f}–{r['windowEnd']:.2f})")
        start = t - dur if spec.endswith("<") else t if spec.endswith(">") else t + F - peak
        if start < 0:
            raise SystemExit(f"sfx: {spec} {key} would start before 0")
        gain_db = voice_m - under - m
        cues.append({"id": f"sfx{n:02d}", "at": round(t, 3), "start": round(start, 3), "duration": round(dur, 3),
                     "src": f"assets/sfx/{key}.wav", "sound": key, "under": under, "gainDb": round(gain_db, 2),
                     "volume": round(10 ** (gain_db / 20), 4), "what": what, "file": sounds[key][0]})
    for a, b in zip(cues, cues[1:]):
        if b["at"] < a["at"]:   # by hit time: a slow whoosh may start before the click just ahead of it
            raise SystemExit(f"sfx: cue table out of order at {b['what']}")
        if b["at"] - a["at"] < 0.25 and not (a["sound"] == "riser" or b["sound"] == "riser"):
            print(f"  sfx: {a['what']} and {b['what']} are only {b['at'] - a['at']:.2f}s apart")
    if cues and max(c["volume"] for c in cues) > 3.98:
        raise SystemExit("sfx: a cue needs more than +12 dB — pick a louder file")
    if any(c["start"] + c["duration"] > plan.TOTAL + 1e-6 for c in cues):
        raise SystemExit("sfx: a sound runs past the end of the video — trim it (SOUNDS length) or raise TOTAL")

    (root / "build").mkdir(exist_ok=True)
    (root / "build/sfx.json").write_text(json.dumps(cues, indent=1))
    fmt = lambda s: f"{int(s // 60)}:{s % 60:05.2f}"
    lines = [f"# {plan.TITLE} — sound effects cue sheet", "",
             f"{len(cues)} sounds. Time = where the sound hits. Level = how far under the voice (dB; bigger = quieter).", "",
             "| # | Time | What happens on screen | Sound | Level |", "|---|---|---|---|---|"]
    for c in cues:
        lines.append(f"| {c['id'][3:]} | {fmt(c['at'])} | {c['what'][3:]} | {c['sound']} | −{c['under']} dB |")
    (root / "build/sfx.md").write_text("\n".join(lines) + "\n")
    lanes = []   # Studio lanes: each cue on the first lane that is free when it starts (no overlapping sounds on one lane)
    for c in cues:
        k = next((i for i, end in enumerate(lanes) if end <= c["start"]), len(lanes))
        lanes[k:k + 1] = [c["start"] + c["duration"]]
        c["lane"] = 20 + k
    tags = [f'      <audio id="{c["id"]}" class="clip" src="{c["src"]}" data-start="{c["start"]:.3f}" '
            f'data-duration="{c["duration"]:.3f}" data-volume="{c["volume"]:.4f}" data-track-index="{c["lane"]}" '
            f'data-audio-group="sfx"></audio>' for c in cues]
    print(f"sfx: {len(cues)} cues (voice {voice_m} LUFS) · sfx.json + sfx.md written")
    return "\n".join(tags)
