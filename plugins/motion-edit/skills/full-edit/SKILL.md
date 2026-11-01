---
name: full-edit
description: The whole workflow for one talking video, start to finish — transcribe the edited video, make the motion-graphics presentation from its words, render the clips, edit them onto the video with speaker cutouts, transitions and sound effects, and export. Use when the user hands over an edited video and asks for "the full edit", "make the graphics and edit it", or names this workflow.
---

# Full edit: presentation → edit → export

Two skills in a row, with a stop for the user's approval after each: **make-presentation** builds and renders
the graphics from the video's own words, **edit-video** puts them on the video. Run either one alone when the user
only needs that half (they already have graphics, or only want the slides).

Paths: the plugin root is two folders above this skill. `ENGINE` = `<plugin root>/skills/edit-video/engine`,
`PY` = `~/.motion-edit-kit/venv/bin/python`. If `PY` is missing, run `bash <plugin root>/setup.sh` once.

## 0. Intake (ask only for what's missing)

- The **edited video** (cuts and colour done) and the spoken **language**.
- The **speaker's name** and the **brand**: name, 2–3 colours, any reference page or deck they like.
- Screenshots of anything the speaker points at (a form, a page, an app).
- Where the project folder lives and where approved files go (default: `projects/<name>/` and `Final-approved-exports/`).

## 1. Prep and transcript

Follow edit-video step 1 without `--graphics`:
```bash
$PY $ENGINE/prep.py <project> --video "<edited.mp4>" --lang <xx> --title "<Client – video>"
```
Read `transcript/footage.txt`, fix misheard names. `transcript/footage.srt` is the script for the presentation,
with real timestamps.

## 2. Presentation

Follow the make-presentation skill in `<project>/presentation/`, using `transcript/footage.srt` as the script and
`assets/frame.png` as the footage frame. Render the clips to `<project>/presentation/graphics-<video>/` with the cue
sheet.

**Stop:** show the user the contact sheet, the scene list (one line each) and any placeholder content you
invented. Fix and re-render only the scenes they change. Continue when they approve.

## 3. Edit

```bash
$PY $ENGINE/prep.py <project> --graphics <project>/presentation/graphics-<video>
```
Then edit-video steps 2–8. The presentation HTML is in `<project>/presentation/`: read clip moments from it.

**Stop:** send the export and the review sheets (`build/edl.md`, `build/sfx.md`). Each round of feedback is a new
version (v2, v3 …).

## 4. Approval

Only on the user's approval: copy the export to the final folder, confirm it is identical (`cmp`), and tell them
the file name, length and size.
