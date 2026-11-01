"""Cut the speaker out for the panels/cards they stand in front of.

For each entry in the plan's CUTOUTS ({clip id: (first frame, last frame[, options])}): a frame-exact segment of
the footage (frame 0 of the segment = footage frame <first>), matted with `hyperframes remove-background`.
build.py starts the cutout at <first>/FPS, so it lines up with the footage under it to the frame.
Existing cutouts are kept; pass --force to redo them, or clip ids to do only those.
Run: python cutouts.py <project> [02 04 …] [--force]
"""

import subprocess
import sys

from common import FPS, load_plan


def main(project, *args):
    root, plan = load_plan(project)
    force = "--force" in args
    only = [a for a in args if a != "--force"]
    cut_dir = root / "assets/cut"
    cut_dir.mkdir(parents=True, exist_ok=True)
    for cid, (first, last, *_opts) in plan.CUTOUTS.items():
        out = cut_dir / f"cut{cid}.webm"
        if (only and cid not in only) or (out.exists() and not force):
            continue
        seg = cut_dir / f"seg{cid}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(root / plan.FOOTAGE), "-vf",
                        f"select=between(n\\,{first}\\,{last}),setpts=N/{FPS}/TB", "-an", "-c:v", "libx264", "-crf", "12",
                        "-pix_fmt", "yuv420p", "-r", str(FPS), str(seg)], check=True)
        print(f"{cid}: matting frames {first}–{last} ({(last - first + 1) / FPS:.1f}s)…", flush=True)
        subprocess.run(["npx", "--yes", "hyperframes@latest", "remove-background", str(seg), "-o", str(out),
                        "--quality", "best"], check=True)
    for p in sorted(cut_dir.glob("cut*.webm")):
        print(f"  {p.name}  {p.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["."]))
