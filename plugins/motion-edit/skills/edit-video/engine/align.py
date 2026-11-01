"""Re-time a Whisper transcript to the audio with forced alignment (torchaudio MMS_FA).

Whisper's word timestamps drift by up to ~0.35s (usually early), which makes one-word
captions feel off-pace. This keeps Whisper's words and replaces their start/end with
frame-accurate times from a CTC forced aligner.

Usage: .venv/bin/python tools/align.py MEDIA WORDS.json [--out ALIGNED.json]
WORDS.json is the Remotion Caption-format file written by tools/transcribe.py.
"""

import argparse
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import numpy as np
import torch
from torchaudio.pipelines import MMS_FA

SR = 16000


def load_audio(path: str) -> torch.Tensor:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return torch.from_numpy(np.frombuffer(raw, np.float32).copy()).unsqueeze(0)


def normalize(word: str) -> str:
    """Lowercase a-z and apostrophes only, which is what the MMS aligner's dictionary covers."""
    w = unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z']", "", w)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("media")
    p.add_argument("words")
    p.add_argument("--out")
    args = p.parse_args()

    words = json.loads(Path(args.words).read_text())
    norm = [normalize(w["text"]) for w in words]
    keep = [i for i, n in enumerate(norm) if n]

    wave = load_audio(args.media)
    model = MMS_FA.get_model()
    with torch.inference_mode():
        emission, _ = model(wave)
    spans = MMS_FA.get_aligner()(emission[0], MMS_FA.get_tokenizer()([norm[i] for i in keep]))
    sec_per_frame = wave.size(1) / emission.size(1) / SR

    moved = []
    for i, span in zip(keep, spans):
        start = round(span[0].start * sec_per_frame * 1000)
        end = round(span[-1].end * sec_per_frame * 1000)
        moved.append(start - words[i]["startMs"])
        words[i].update(startMs=start, endMs=end, timestampMs=(start + end) // 2)

    out = Path(args.out) if args.out else Path(args.words).with_name(Path(args.words).stem + "-aligned.json")
    out.write_text(json.dumps(words, indent=2))
    m = np.array(moved)
    print(f"aligned {len(keep)} words -> {out} · shift mean {m.mean():+.0f}ms, max {np.abs(m).max():.0f}ms")


if __name__ == "__main__":
    main()
