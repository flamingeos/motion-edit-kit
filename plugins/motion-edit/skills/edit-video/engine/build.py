"""Build the edit: the finished motion-graphic clips over the speaker's footage.

Full-screen takeovers, side panels and floating cards with the speaker cut out in front of them, minimal sound
effects tied to what moves (sfx.py, mixed over the untouched voice by mix.py). Reads the project's plan.py (EDL,
look, cutouts, sound cues) and build/cues.json (each clip's spoken line, from cues.py), validates every window
against the clip's real length, and writes:
  index.html      the HyperFrames composition (footage + graphic wrappers + one GSAP timeline)
  build/edl.md    the edit decision list (times, phrase, mode, transitions) for review
  build/sfx.*     the sound-effect cues

Run: python build.py <project>
"""

import json
import math
import subprocess
import sys

import sfx
from common import ENGINE, FPS, duration, load_plan

# Entrance / exit lengths in frames (the transitions in template.html use the same numbers).
ENTER_FRAMES = {"iris": 16, "zoom": 12, "slow-zoom": 18, "whip": 9, "push": 15, "pop": 13, "slide": 14}
EXIT_FRAMES = {"fade": 8, "fade-to": 8, "pop-to": 9, "slide-out": 14, "pop-out": 13, "cover": 0, "end": 0}
PANEL_MODES = ("right", "card", "right2full")   # the speaker reframes and stands in front of these

LABEL = {"iris": "Iris opens out of the panel", "zoom": "T2 Zoom takeover", "slow-zoom": "T2 Slow zoom", "whip": "T4 Whip pan",
         "push": "T1 Full-screen slide", "pop": "T3 Card pop-in", "slide": "T1 Slide & reframe",
         "fade": "Quick crossfade to {s}", "fade-to": "Crossfade to {s} (already reframed for the next graphic)",
         "pop-to": "Card pops away ({s} stays reframed for the next panel)", "slide-out": "Slide out + reframe back",
         "pop-out": "Card pop-out + reframe back", "cover": "Next graphic covers it", "end": "Holds to the end"}
MODE = {"full": "Full screen", "right": "Right-side panel", "card": "Floating card",
        "right2full": "Right panel → zoom to full screen (T1 → T5)"}

HOLD_FRAMES = 900   # every hold clip is 30 s of one frame; a piece uses as much of it as it needs


def hold_clip(root, cid, clip, frame):
    """A still of one clip frame as a 30 fps H.264 clip, built from the decoded YUV frame (no RGB round trip),
    so it renders with exactly the colours of the playing clip."""
    holds = root / "assets/gfx/holds"
    out = holds / f"{cid}-f{frame:03d}.mp4"
    if not out.exists():
        holds.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vf",
                        f"select=eq(n\\,{frame}),setpts=N/{FPS}/TB,loop=loop={HOLD_FRAMES}:size=1:start=0",
                        "-frames:v", str(HOLD_FRAMES), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                        "-pix_fmt", "yuv420p", "-g", str(FPS), "-an", str(out)], check=True)
    return f"assets/gfx/holds/{out.name}"


def pieces(root, cid, clip, segs, window_end, clip_frames):
    """Turn [out, media] anchors into play/hold pieces, in whole frames so they butt up exactly."""
    last = clip_frames - 2
    anchors = [(round(o * FPS), round(m * FPS)) for o, m in segs]
    end_f = round(window_end * FPS)
    out = []
    for k, (o, m) in enumerate(anchors):
        nxt_o, nxt_m = (anchors[k + 1] if k + 1 < len(anchors) else (end_f, None))
        play = (nxt_m - m) if nxt_m is not None else min(nxt_o - o, last - m)
        if play > nxt_o - o:
            raise SystemExit(f"{cid}: segment at {o / FPS:.2f}s needs {play} frames but only has {nxt_o - o}")
        if play > 0:
            out.append({"kind": "play", "start": o / FPS, "frames": play, "media": m / FPS})
        if o + play < nxt_o:
            frame = nxt_m if nxt_m is not None else last
            out.append({"kind": "hold", "start": (o + play) / FPS, "frames": nxt_o - (o + play),
                        "src": hold_clip(root, cid, clip, frame), "frame": frame})
    return out


def look_tokens(plan):
    """The template's look placeholders, from the plan's LOOK (wall colours behind the speaker, face point, cutout mask)."""
    L = plan.LOOK
    r, g, b = (int(L["wall"][i:i + 2], 16) for i in (1, 3, 5))
    return {"{{WALL}}": L["wall"], "{{WALL_LIGHT}}": L["wallLight"], "{{WALL_DARK}}": L["wallDark"],
            "{{WALL_CLEAR}}": f"rgba({r},{g},{b},0)", "{{PLATE_AT}}": L.get("plateAt", "70% 55%"),
            "{{FACE}}": f"{L['face'][0]}px {L['face'][1]}px", "{{MASK_FROM}}": str(L["mask"][0]),
            "{{MASK_TO}}": str(L["mask"][1]), "{{CARD}}": L.get("card", "#f4efe9")}


def main(project):
    root, plan = load_plan(project)
    media_start = plan.MEDIA_START
    total = plan.TOTAL
    speaker = getattr(plan, "SPEAKER", "the speaker")
    cue_rows = {c["id"]: c for c in json.loads((root / "build/cues.json").read_text())}
    clips = {p.name[:2]: p for p in sorted((root / "assets/gfx").glob("[0-9][0-9]-*.mp4"))}
    cutouts = getattr(plan, "CUTOUTS", {})

    rows, errors = [], []
    edl = plan.EDL
    for n, (cid, mode, enter, start, exit_at, exit_kind, extra) in enumerate(edl):
        clip = clips[cid]
        extra = dict(extra)
        if mode in PANEL_MODES and "lay" not in extra:
            extra.update(plan.PANEL)
        if cid in cutouts:
            # Cutouts (cutouts.py): segment frame 0 = footage frame <first>, so start = first / FPS, frame-exact.
            # A cutout off by one frame from the footage under it doubles the speaker's edges as they move.
            first, _last, *opts = cutouts[cid]
            extra["cutout"] = {"src": f"assets/cut/cut{cid}.webm", "start": first / FPS, **(opts[0] if opts else {})}
        usable = 1e9 if extra.get("segs") else duration(clip) - media_start   # paced clips hold frames
        if exit_kind == "cover":
            nxt = edl[n + 1]
            window_end = nxt[3] + ENTER_FRAMES[nxt[2]] / FPS + 1 / FPS   # stay until the next graphic is fully in
        else:
            # Leave before the clip runs out: pull the exit earlier if the line outlasts the clip.
            latest_exit = start + usable - EXIT_FRAMES[exit_kind] / FPS - 1 / FPS
            if exit_at > latest_exit:
                print(f"  {cid}: exit pulled from {exit_at:.2f} to {latest_exit:.2f} (clip ends)")
                exit_at = latest_exit
            window_end = exit_at + EXIT_FRAMES[exit_kind] / FPS
        window_end = min(window_end, total)
        if window_end - start > usable + 1e-6:
            errors.append(f"{cid}: window {window_end - start:.2f}s is longer than the clip ({usable:.2f}s)")
        row = {"id": cid, "src": f"assets/gfx/{clip.name}", "mode": mode, "enter": enter, "start": round(start, 3),
               "exitAt": round(exit_at, 3), "exit": exit_kind, "windowEnd": round(window_end, 3),
               "nextShift": None, **extra}
        if extra.get("segs"):
            assert abs(extra["segs"][0][0] - start) < 1e-6, f"{cid}: first seg must start at the row start"
            row["pieces"] = pieces(root, cid, clip, extra["segs"], window_end, round(duration(clip) * FPS))
        rows.append(row)
    if errors:
        raise SystemExit("\n".join(errors))

    # Where the speaker has to be when a graphic leaves straight into a card/panel: a full-screen fade-to snaps them
    # there while they are hidden; a pop-to card leaves them where they are (both panels use the same reframe).
    for a, b in zip(rows, rows[1:]):
        if a["exit"] in ("fade-to", "pop-to"):
            a["nextShift"] = b.get("shift", 0)
            b["shiftReady"] = True
            if a["exit"] == "pop-to":
                assert a.get("shift") == b.get("shift"), f"{a['id']}: pop-to needs the same reframe as {b['id']}"

    # A cutout must never sit on top of the previous graphic while that one is still on screen (a 3-frame glitch
    # otherwise): it only starts once the previous graphic has gone, and a card never arrives before that.
    for a, b in zip(rows, rows[1:]):
        if b.get("cutout") and a["windowEnd"] > b["cutout"]["start"]:
            b["cutout"]["from"] = a["windowEnd"]
            if b["start"] < a["windowEnd"] - 1e-6:
                raise SystemExit(f"{b['id']}: card arrives at {b['start']:.2f} while {a['id']} is on screen until {a['windowEnd']:.2f}")

    # ---- page ------------------------------------------------------------------------------------
    wrappers = []
    for i, r in enumerate(rows):
        dur = round(r["windowEnd"] - r["start"], 3)
        if r.get("pieces"):
            vids = "".join(
                f'        <video id="g{r["id"]}p{k}" class="clip" src="{p["src"] if p["kind"] == "hold" else r["src"]}" '
                f'data-start="{p["start"]:.4f}" data-duration="{p["frames"] / FPS:.4f}" '
                f'data-media-start="{0 if p["kind"] == "hold" else p["media"]:.4f}" data-track-index="{1 + i % 2}" muted playsinline></video>\n'
                for k, p in enumerate(r["pieces"]))
            wrappers.append(f'      <div id="w{r["id"]}" class="gw" style="z-index:{10 + i}">\n'
                            f'        <div id="gi{r["id"]}" class="gi" data-layout-allow-overflow>\n{vids}        </div>\n      </div>')
        else:
            wrappers.append(
                f'      <div id="w{r["id"]}" class="gw" style="z-index:{10 + i}">\n'
                f'        <video id="g{r["id"]}" class="clip" src="{r["src"]}" data-start="{r["start"]}" data-duration="{dur}"\n'
                f'          data-media-start="{media_start:.4f}" data-track-index="{1 + i % 2}" muted playsinline></video>\n'
                f'      </div>')
        if r.get("cutout"):   # same z as the card but later in the DOM: above this card, below the next graphic
            c = r["cutout"]
            f0 = round(c["start"] * FPS)   # every time below is a whole frame, so the layer never lands between frames
            assert abs(c["start"] * FPS - f0) < 1e-3, f"{r['id']}: cutout start {c['start']} is not on a frame"
            vis_f = max(math.ceil(c.get("from", r["start"]) * FPS - 1e-6), f0 + 1)
            end_f = math.floor(min(r["windowEnd"], c["start"] + duration(root / c["src"])) * FPS + 1e-6)
            assert end_f > vis_f, f"{r['id']}: cutout file ends before the card"
            vis, end = vis_f / FPS, end_f / FPS
            wrappers.append(
                f'      <div id="spkc{r["id"]}" class="spkc" style="z-index:{10 + i}">\n'
                f'        <video id="cut{r["id"]}" class="clip" src="{c["src"]}" data-start="{vis:.4f}" '
                f'data-duration="{round(end - vis, 3)}" data-media-start="{(vis_f - f0) / FPS + 0.0005:.4f}" data-track-index="3" '
                f'muted playsinline data-layout-allow-occlusion></video>\n      </div>')

    page = (ENGINE / "template.html").read_text()
    page = page.replace("<!--GRAPHICS-->", "\n".join(wrappers)).replace("/*EDL*/[]", json.dumps(rows))
    page = page.replace("<!--SFX-->", sfx.emit(rows, root, plan))
    page = page.replace("{{FOOTAGE}}", str(plan.FOOTAGE_DURATION)).replace("{{DURATION}}", str(total))
    page = page.replace("{{FOOTAGE_SRC}}", plan.FOOTAGE).replace("{{TITLE}}", plan.TITLE)
    for k, v in look_tokens(plan).items():
        page = page.replace(k, v)
    (root / "index.html").write_text(page)

    # ---- EDL for review -------------------------------------------------------------------------
    lines = [f"# {plan.TITLE} — edit decision list", "",
             "Times are in the final video (no cuts, so they match the edited footage).", "",
             "| # | In | Out | Phrase (start of the line) | Layout | Entrance | Exit |", "|---|---|---|---|---|---|---|"]
    fmt = lambda s: f"{int(s // 60)}:{s % 60:05.2f}"
    for r in rows:
        c = cue_rows[r["id"]]
        enter = LABEL[r["enter"]] + (f" → expands at {fmt(r['expandAt'])}" if r.get("expandAt") else "")
        if r.get("pieces") and len(r["pieces"]) > 1:
            enter += f"; paced to the words ({sum(p['kind'] == 'hold' for p in r['pieces'])} holds)"
        lines.append(f"| {r['id']} | {fmt(r['start'])} | {fmt(r['windowEnd'])} | “{c['first']} …” ({fmt(c['start'])}) | "
                     f"{MODE[r['mode']]} | {enter} | {LABEL[r['exit']].format(s=speaker)} |")
    (root / "build/edl.md").write_text("\n".join(lines) + "\n")
    print(f"index.html: {len(rows)} graphics · edl.md written")
    for r in rows:
        print(f"  {r['id']} {r['start']:7.2f} → {r['windowEnd']:7.2f}  {r['mode']:10s} {r['enter']:9s} {r['exit']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
