---
name: edit-video
description: Put finished motion-graphic clips onto an edited talking-head video — full-screen takeovers, side panels and floating cards with the speaker cut out in front of them, smooth transitions, a few sound effects tied to what moves, and the original voice untouched. Use when the user hands over an edited video (VSL, YouTube video, course lesson, any long-form talk) plus a folder of graphic clips with a cue sheet (from the make-presentation skill or anywhere) and asks to "edit it", "put the graphics in", or "do it like last time".
---

# Edit the video (graphics on the talking head)

The speaker's edited video stays the base: their picture and their voice, untouched. Each graphic clip comes in at
the line it belongs to, as a full-screen takeover or as a panel/card the speaker reframes beside and stands in front
of. Every beat inside a graphic lands on the word that names it. A handful of sounds mark what moves; there is no
music. The result is rendered with HyperFrames and the voice is mixed back in at its original level.

**This has been proven on wide (16:9, 1920×1080) videos.** A tall (9:16) video needs tall graphics and a first
trial run to set its layouts: say so before starting one, and treat the first as a test.

## Tools and paths

- `ENGINE` = this skill's folder + `/engine`. `PLAN` template: this skill's folder + `/templates/plan.py`.
- `PY` = `~/.motion-edit-kit/venv/bin/python`. If it is missing, run `bash <plugin root>/setup.sh` once (the plugin
  root is two folders above this skill). It installs ffmpeg, Whisper, the aligner and the sound library.
- HyperFrames: `npx --yes hyperframes@latest …` (check, snapshot, render, remove-background).
- Every engine script takes the project folder first. Everything that changes per video is in `<project>/plan.py`;
  never edit the engine for one video.

## What you need from the user

1. The **edited video**: cuts and colour correction done (CapCut or anything else). Its sound is the final voice.
2. The **graphics folder**: `NN-slug.mp4` clips (1920×1080, 30 fps, silent) and `EDITOR-CUE-SHEET.md` (which line
   each clip goes with).
3. The **presentation HTML**, if there is one. Moments inside a clip (a click, a counter, an item ticking) are read
   from each scene's builder there, so sounds and pacing land on them.
4. The language, the speaker's name, and where finished files go. Ask only for what is missing.

## Workflow

Copy this into the task list:

```
- [ ] 1. Prep the project (footage, words, graphics, plan)
- [ ] 2. Fix the transcript, then CUES → cues.py
- [ ] 3. Set LOOK + PANEL from the footage
- [ ] 4. Write the EDL (layouts, transitions, pacing)
- [ ] 5. Cutouts for panels/cards
- [ ] 6. Sound cues
- [ ] 7. Build, check, snapshot every transition, fix
- [ ] 8. Render, mix, verify, show the user
- [ ] 9. On approval only: copy to the final folder
```

### 1. Prep

```bash
$PY $ENGINE/prep.py <project> --video "<edited.mp4>" --graphics "<clips folder>" --lang <en|es|…> --title "<Client – video>"
```
It makes the 30 fps footage copy, the transcript (`transcript/footage.txt/.srt`, word times in
`footage-aligned.json`), copies the clips, starts `plan.py` and saves `assets/frame.png`. Safe to re-run.
Licence note: the word aligner's model is CC-BY-NC 4.0 (non-commercial). For paid work the user may want
`--no-align` (Whisper's own word times, up to ~0.35 s off; check timings on the snapshots more carefully).

### 2. Words and cues

Read `transcript/footage.txt`. Fix misheard names and brand words in `footage-aligned.json` (text only, keep the
times). Then fill `CUES` with, per clip, the first and last few words of its line from the cue sheet, and run
`$PY $ENGINE/cues.py <project>`. It prints each line's start, end and the gap before it.

### 3. Look and panel

Open `assets/frame.png`.
- `LOOK.wall` / `wallLight` / `wallDark`: the wall colour at the frame's right edge (what shows when the speaker
  moves left), a little lighter and a little darker. Sample it:
  `ffmpeg -v error -i assets/frame.png -vf "crop=40:300:1860:300,scale=1:1" -f rawvideo -pix_fmt rgb24 - | xxd -p`
- `LOOK.face`: the point between the speaker's eyes (zooms push in around it).
- `PANEL.shift`: how far left the speaker moves for a panel (start at −360 to −440 so they land around x ≈ 500).
  `PANEL.lay` [790, 238, 0.56] is a big centred card on the right; keep it unless it covers the speaker.
- `LOOK.mask`: where the cutout starts showing, just inside the speaker's body edge that faces the card.
Check these on the first panel's snapshot in step 7 and adjust.

### 4. The EDL (the edit itself)

One row per clip: `(id, mode, enter, start, exit-start, exit, extra)`. Quote the word times next to each row.

**Modes**
- `full`: the graphic takes over the screen. For big ideas, lists, numbers, the payoff, the close.
- `right`: a panel slides in on the right; the speaker moves left and stands in front of its edge (cutout).
- `card`: a floating card pops in beside the speaker (cutout). For a quick point or a moment that is personal.
- `right2full`: a panel that grows to full screen at `expandAt` (the speaker's cutout fades out first).

**Entrances**: `zoom` (default takeover), `slow-zoom` (the closing line), `whip` (an energetic turn), `push` (a
full-screen graphic slides over), `iris` (opens out of the panel before it: `irisAt` = that panel's centre),
`slide` (panels), `pop` (cards).
**Exits**: `fade` (quick crossfade back), `fade-to` (crossfade, already reframed for the panel that follows),
`pop-to` (card shrinks away, speaker stays reframed for the next panel), `slide-out` / `pop-out` (and the speaker
moves back), `cover` (the next graphic comes in on top), `end` (holds to the end).

**The style that was approved**
- Mix the layouts: full-screen takeovers alternate with panels/cards that have the speaker in front. Avoid the
  same mode and entrance three times in a row.
- A graphic comes in on its line's first strong word (0.1–0.3 s before it is fine), never long before.
- Leave the speaker alone sometimes: an intro look, a laugh, a personal aside, a pause before the payoff.
- Pace clips to the words with `segs`: when an animation beat (an item, a tick, a click) would land early, hold
  the frame before it and restart on the word. A clip that should start part-way in gets a single `[[start, m]]`.
- One payoff: the single most important moment gets the riser + boom (step 6). Build up to it.
- The last graphic may hold ~0.5–1 s past the last word: raise `TOTAL`.

### 5. Cutouts

For every `right`/`card`/`right2full` row add `CUTOUTS[id] = (first frame, last frame)` in footage frames
(seconds × 30) covering the whole time the panel is on screen, then:
```bash
$PY $ENGINE/cutouts.py <project>
```
Frame-exact matters: a cutout one frame off doubles the speaker's edges as they move. For `right2full`, add
`{"fadeOut": <expandAt>, "fadeFrames": 5}` so the face never ghosts through the growing panel.

### 6. Sounds

Fill `SFX` with `(when, sound, dB under the voice, what is on screen)`:
- Every entrance gets one transition sound (`air-quick`, `swoosh`, `sweep`, `zoom-soft`, `zoom-air`, `whip`,
  `whoosh`, `deep` for the slow close). Moments inside clips: `click`, `select`, `pop`, `notify`, `strike`,
  `thump`, `chime`, `sparkle`, `confetti`, `shimmer`, `counter`, `typing`.
- Nothing plays unless something moves at that moment. About one sound per action; never stack two within 0.25 s.
- Levels: entrances 12–13 dB under the voice, small UI moments 14–16, the boom ~6.
- The payoff: `"NN@t<"` riser ending on the hit, then the `boom` 1 frame later. Once per video.
- `"NN@t"` is the clip file's own time (read it from the presentation builder or a frame grab). The engine
  follows the pacing holds and puts each sound's loudest point 1 frame after the picture's hit.
- No music.

### 7. Build and check

```bash
$PY $ENGINE/build.py <project>
cd <project> && npx --yes hyperframes@latest check
npx --yes hyperframes@latest snapshot --at <t1>,<t2>,… --no-end --output <project>/snaps
```
Snapshot every entrance and exit (start + 2 frames, middle, end) and every panel with a cutout. Look at them:
the cutout's edge sits cleanly in front of the card, no face showing through a growing panel, nothing cut off,
the panel doesn't cover the speaker's face. Fix the plan and rebuild. `build/edl.md` and `build/sfx.md` are the
review sheets.

### 8. Render, mix, verify

```bash
npx --yes hyperframes@latest render --fps 30 --quality delivery --output renders/v1.mp4
$PY $ENGINE/mix.py <project> renders/v1.mp4 "<exports>/<Client – video> v1.mp4"
ffmpeg -v info -i "<export>" -vf blackdetect=d=0.05:pix_th=0.05 -an -f null - 2>&1 | grep -c black_start   # want 0
```
`mix.py` must print `voice offset after encode: 0.0 ms`, and the loudness should barely move from the voice-only
number. Send the user the export and the two review sheets. Version names: v1, v2, … for each round of feedback.

### 9. Approval

Only when the user approves, copy the export to their final folder and confirm the copy is identical (`cmp`).

## Pitfalls already hit (don't repeat them)

| Symptom | Cause | Fix |
|---|---|---|
| Speaker's edges look "wavey / glitchy" on a panel | Cutout one frame off the footage | Frame-exact CUTOUTS; never hand-tweak cutout starts |
| A 3-frame flash of the speaker over the previous graphic | Cutout started before that graphic left | The engine delays it; never let a card arrive before the previous graphic is gone |
| Face ghosts through a panel growing to full screen | Cutout still visible during the expand | `fadeOut` at `expandAt`, `fadeFrames` 5 |
| Stray bar / previous scene on a clip's first frame | Recorder leftovers in frames 0–1 | `MEDIA_START = 2 / 30` (keep it) |
| Check fails: something runs past the end | A long sound or hold beyond `TOTAL` | Trim the sound (`SOUNDS` length) or raise `TOTAL` |
| `ENTER[...] is not a function` | Entrance name not in the template | Use only the entrances listed above |
| "cue table out of order" | SFX rows not in hit-time order | Order SFX by when they hit |
| Voice quieter in the HyperFrames render | Its render re-levels audio | Always export through `mix.py` |
