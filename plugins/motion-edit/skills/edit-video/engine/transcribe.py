"""Transcribe a video/audio file with OpenAI Whisper.

Writes next to the output base path:
  <base>.json  word-level captions in Remotion's Caption format
  <base>.srt   phrase-level subtitles for FFmpeg / CapCut / uploads
  <base>.txt   plain transcript

Usage: .venv/bin/python tools/transcribe.py INPUT [--out BASE] [--model small] [--lang en]
"""

import argparse
import json
from pathlib import Path

import whisper


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--out", help="output base path without extension (default: next to input)")
    p.add_argument("--model", default="small", help="tiny, base, small, medium, large, turbo")
    p.add_argument("--lang", default=None, help="language code, e.g. en or es (default: auto-detect)")
    args = p.parse_args()

    src = Path(args.input)
    base = Path(args.out) if args.out else src.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)

    model = whisper.load_model(args.model)
    result = model.transcribe(str(src), language=args.lang, word_timestamps=True, fp16=False)

    captions = []
    srt_lines = []
    for i, seg in enumerate(result["segments"], 1):
        srt_lines += [str(i), f"{srt_time(seg['start'])} --> {srt_time(seg['end'])}", seg["text"].strip(), ""]
        for w in seg.get("words", []):
            captions.append({
                "text": w["word"],
                "startMs": round(w["start"] * 1000),
                "endMs": round(w["end"] * 1000),
                "timestampMs": round((w["start"] + w["end"]) / 2 * 1000),
                "confidence": round(w.get("probability", 1.0), 3),
            })

    base.with_suffix(".json").write_text(json.dumps(captions, indent=2))
    base.with_suffix(".srt").write_text("\n".join(srt_lines))
    base.with_suffix(".txt").write_text(result["text"].strip() + "\n")
    print(f"language={result['language']} words={len(captions)} -> {base}.json/.srt/.txt")


if __name__ == "__main__":
    main()
