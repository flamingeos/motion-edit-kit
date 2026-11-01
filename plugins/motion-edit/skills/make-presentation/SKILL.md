---
name: make-presentation
description: Turn a talking-head video's script or transcript (VSL, YouTube video, course lesson, any long or short talk) into an animated HTML motion-graphics presentation, then render every scene to its own MP4 clip with a cue sheet so a human or AI video editor can cut them in as B-roll. Use when the user pastes a video transcript or script and asks for motion graphics, animated slides, overlays, B-roll graphics, "visuals for my video", or "make this more visual", for any client or brand. Hands off to the edit-video skill.
---

# Make the presentation (motion graphics)

Turn a spoken script into full-screen animated graphics that cut in over a talking-head video. Each idea in the script gets its own short scene. Every scene is rendered frame by frame to a smooth MP4. The editor gets the clips plus a cue sheet saying exactly where each one goes.

The finished package for each video has three parts:
1. `<client>-<video>.html`: the live presentation, with one scene per beat, keyboard-driven.
2. `graphics-<video>/NN-slug.mp4`: one 1920×1080, 30 fps, silent clip per scene.
3. `graphics-<video>/EDITOR-CUE-SHEET.md`: which clip goes where, and what it shows.

Files in this skill:
- `templates/presentation-template.html`: the engine and example scenes. Copy it, then replace the scenes.
- `templates/EDITOR-CUE-SHEET.md`: cue-sheet format.
- `scripts/render.js`: deterministic frame-by-frame renderer (Playwright + ffmpeg).
- `scripts/contact-sheet.sh`: tiles the last frame of every clip into one image for review.
- `scripts/package.json`: renderer dependency (`playwright-core`).

---

## 1. Intake (ask only for what's missing)

Collect these before building:
- **Script or transcript**, ideally with timestamps or section headers. Timestamps go straight into the cue sheet.
- **A frame from the talking-head footage.** It decides the contrast. Dark footage gets light graphics, and vice versa.
- **Brand:** the name shown in the corner, 2–3 accent colours, and any reference design, page or deck they like. If they share a reference URL, open it and copy its fonts, colours and type sizes. A design the user hands you beats your own taste.
- **Screenshots of their product, form, page or app** if the script talks about them, for example "just below this video you'll find…". These get **rebuilt in HTML**, not pasted. See §3.
- **Numbers and claims** used on screen (prices, client counts, revenue, dates). Use only what the script says. Anything you have to invent (gift names, sample messages, example prices) must be listed to the user at the end as a placeholder.

Work in a fresh folder (when the full-edit skill runs you, use `<project>/presentation/`). When the client has several videos, keep one HTML file and one `graphics-<video>/` folder per video, all with the same look.

If the video is already edited and transcribed (full-edit / edit-video `prep.py`), use `<project>/transcript/footage.srt` as the script: it has the real timestamps, so the cue sheet times are exact.

## 2. Storyboard

- Split the script into **beats**, one idea each. A scene lasts **6–10 s** (`data-dur`).
- Typical counts: a 3–4 minute video gets about 20 scenes, a 1–2 minute video gets 10–14. Shorter scripts get fewer, cleaner scenes. Don't pad.
- For each beat, choose **one visual metaphor** that shows the idea instead of restating it. Proven patterns:
  - Problem → bar or meter dropping into the red, price counting down, chart line falling
  - Myth → chain of cards that collapses, then a "No funciona así"-style stamp
  - Confusion → giant "?" with floating question chips
  - "X ≠ Y" → two cards with a ≠ drawn between them
  - Comparison → two cards, one faded with ✗ and one highlighted with ✓
  - Process → horizontal timeline whose nodes light up in order
  - Credibility → name reveal plus counter cards (150+, 6 cifras…)
  - Search or visibility → a fake search box typing a query, with "you" missing from the results
  - Social proof gap → follower counter vs. bookings at 0
  - Offer or modules → grid of icon cards
  - Gift or bonus → gift box opening
  - Community → "Tú" in the centre, connected to a ring of avatars
  - Channel or messaging → phone mockup with messages arriving one by one
  - Event or date → calendar with the date getting clicked, a live-class mockup, a "save the date" pill
  - Recap → checklist that ticks off
  - CTA → button that a cursor clicks (with ripple), plus a bouncing arrow pointing down
  - "Not A, it's B" reframe → line 1 with its last word struck through, then line 2 big
- Plan the text for every scene: **one short headline (2–7 words) plus at most one subtitle line.** See §4.

## 3. Build the HTML

1. Copy `templates/presentation-template.html` to `<client>-<video>.html`.
2. Set the brand tokens in `:root`: `--bg`, `--ink`, `--wine`/`--rose`/`--cop` (accent gradient), `--grad`. Set the brand name in `.chrome .bl` and the fonts in the Google Fonts link.
3. Write one `<section class="scene" data-id="…" data-dur="…" data-tag="…" data-title="…">` per beat.
   - `data-tag`: the small label shown top-left (in the HTML only; renders hide it).
   - `data-title`: the scene name. It becomes the clip filename slug.
4. Write one builder per scene in `const B={ id(tl,$,q,s){…} }`. The helpers are documented in the template header: `rise`, `draw`, `count`, `typeText`, `fill`, `pop`, `bob`, `loop`, `choose`, `moveCursor`, `click`, `at`, `cardIn`.
   - Any `.title` (split words) and any `.sub` (fade-up at `data-t` seconds) animate automatically. Don't animate them again in the builder.
5. **Rebuilt UI.** When the script shows the client's real page, form or app, recreate it as HTML: same copy, options, step counter ("1 de 7"), progress bar and buttons. Drop the browser chrome. Then animate it: options get selected, a cursor clicks, Siguiente lights up, the progress bar fills. The `form()` helper in the template is the pattern.
6. Serve the folder locally, for example `python3 -m http.server 8791 --bind 127.0.0.1`, and open the page. Check that the port is free first (`lsof -iTCP:<port> -sTCP:LISTEN`). If something else is already listening, pick another port. Never stop the user's other servers.

## 4. Style rules (approved by the client, keep them)

**Look**
- **Light theme on dark footage.** Warm cream background (`#f4efe8`), white cards (`#fffdfa`) with a soft wide shadow, near-black ink. On dark talking-head footage this gives contrast and "volume". (Flip it only if the footage is light.)
- Background: two large radial-gradient blush/peach blobs drifting slowly, plus a faint dot grid. Use gradients, never `filter: blur`.
- **Type:** a bold, tight grotesk for headlines (Instrument Sans 600, letter-spacing −0.04em). An italic serif for the accent words (Instrument Serif italic, filled with the brand gradient). Uppercase mono for small labels (IBM Plex Mono, letter-spacing 0.16em).
- **One accent gradient** (for example wine → rose → copper) used for discs, fills, buttons and accent words. Red `#d23f3f` only means negative or loss, green `#2f9e6e` only means positive or done.
- Icons: simple 24×24 line icons in gradient discs or white cards. **No real brand logos.** Platform names (Instagram, Google, Zoom, WhatsApp) are fine as text.
- Chrome in the HTML: tag top-left, brand bottom-left, `NN / total` bottom-right. **Renders hide the chrome** (`nochrome`), so clips can sit anywhere in the edit.

**Text: the balance the client landed on**
- Too many words is wrong, because the speaker is already saying them.
- Zero words is also wrong ("I don't understand what I'm looking at").
- ✅ Every scene: **one short headline that names the idea**, at most **one subtitle sentence**, and **short labels** on the graphic itself (bar labels, card titles, chip text). Captions under cards: 3–7 words.
- Spanish or other non-English scripts: keep all on-screen text in the script's language and reuse the speaker's own words.

**Motion: "smooth and clean at all times"**
- Animate **only transform and opacity** (plus SVG stroke-dashoffset and colour tweens on small elements). No animated `filter: blur`, no animated `letter-spacing`, no animated `box-shadow`, no full-scene zoom or push.
- Easing: `power3.out` for entrances, `power2.inOut` / `sine.inOut` for moves and state changes, `back.out(1.2)` at most for pops. **Never** `bounce`, `elastic`, `expo.out`, `power4.in` slams, or quick x-shakes. They read as "pausing then snapping".
- Entrances: words rise from a mask (`rise`), cards slide up 120px and fade in, chips pop from scale 0.4. Stagger 0.05–0.2 s.
- **No CSS transitions or class toggles for visual state.** Everything (highlights, fills, colour changes) is a GSAP tween on the scene timeline, so the renderer can step it frame by frame.
- Ambient loops (gentle bobbing, pulsing rings, dashed lines flowing) are fine. Push them into `loops` so they're killed on scene change.
- Leave about 1 s of calm hold at the end of every scene (`data-dur` ≈ last tween end + 1).

## 5. Check before rendering

- Run every scene in the browser console and confirm there are no errors:
  `const e=[];scenes.forEach((s,i)=>{try{go(i);tl.progress(1)}catch(x){e.push(i+1+': '+x.message)}});e`
- To parse-check the script: extract the `<script>` body and run `node --check`.
- Preview-pane screenshots are unreliable: hidden panes throttle animation and screenshots lag one frame behind. **Judge layout from the rendered frames** (§6–7). Use the pane only for a quick look.
- After editing the HTML, reload with a cache-buster (`?v=N`). Otherwise the browser keeps serving the old file.

## 6. Render every scene to MP4

```bash
cd scripts && [ -d node_modules ] || npm install   # first use, and again after each kit update (new folder)
node render.js "http://localhost:8765/<client>-<video>.html?v=1" "../graphics-<video>" 30
# only some scenes (1-based):
node render.js "<url>" "<outDir>" 30 4,11
```
- It uses the installed **Google Chrome** (`/Applications/Google Chrome.app/...`, so edit `executablePath` on other machines). It loads the page with `?render=1`, pauses GSAP's global timeline and steps it `1/30 s` per frame. Each frame is a 1920×1080 screenshot piped into ffmpeg (`libx264 -crf 14 -preset slow -pix_fmt yuv420p`). The result is perfectly smooth whatever the machine's speed.
- Speed is about 1 minute per 8 s clip. For more than 10 scenes, run two processes in parallel on halves of the list in the background.
- Output filenames are `NN-<slug of data-title>.mp4` with accents stripped.

## 7. Review the renders, fix, re-render only what changed

```bash
bash scripts/contact-sheet.sh "graphics-<video>" review.png
```
Look at the sheet, and also at a mid-animation frame for scenes with a cursor or a sequence:
`ffmpeg -ss 3.5 -i clip.mp4 -frames:v 1 mid.png`.
Check for overlaps, text clipped by other shapes, empty or cramped space, and labels that can't be read on their background. Fix the HTML, then re-render only those scene numbers.

## 8. Cue sheet and delivery

Write `graphics-<video>/EDITOR-CUE-SHEET.md` from `templates/EDITOR-CUE-SHEET.md`. Use one row per clip: file, approximate time, the **speaker's exact line** that triggers the cut, and what the graphic shows. Keep the placement rules at the top.

**The editor (human or AI) needs:**
- the `graphics-<video>/` folder: MP4s plus the cue sheet. This is the actual hand-off: the edit-video skill copies it with `prep.py --graphics`.
- the HTML too: edit-video times sounds and pacing to the moments inside each clip, and reads them from each scene's builder (media time = builder time).
- optionally the HTML, for previewing or tweaking a scene live (keys: ←/→ scene, R replay, A autoplay, C hide frame, H hide UI, F fullscreen, `#N` in the URL jumps to a scene).

**Tell the user at the end:**
- where each folder is
- the scene list (one line each)
- any **placeholder** content you invented that they should replace (gift names, sample messages, example prices)
- which scenes you re-rendered after fixes, and anything you could not check

---

## Pitfalls we already hit (don't repeat them)

| Symptom | Cause | Fix |
|---|---|---|
| Two strokes of a "≠" or a horizontal line invisible | SVG gradient stroke (`objectBoundingBox`) on a zero-height line | Use a solid stroke colour, or a `userSpaceOnUse` gradient |
| Headline never appears | The same `.wi` words animated twice (`.title` auto-anim plus a builder `rise`). The second `from` starts from the hidden state | Animate `.title` / `.sub` only through the automatic intro |
| Two `from` tweens on one element end at the wrong scale | The first `from` renders immediately, so the second records the wrong end value | One `from` per property per element. Use `fromTo` when stacking |
| Cursor misses its target | Position measured after a `from` tween already moved the card | Measure positions with `at()` **before** adding the card's entrance tweens |
| Gradient text vanishes | Brand gradient (dark wine) used as text colour on a dark mockup screen | Use a light tint such as `#f0b7a6` on dark surfaces |
| Gift lids or overlays cover the title or labels | Lids animated upward into other elements | Lift and fade lids out (`y:-170, opacity:0`) or move them sideways |
| Laggy playback | Animated blur filters, big blurred background elements, full-scene scale, backdrop-filter | Gradient backgrounds, transform and opacity only, no backdrop-filter |
| "Pauses then snaps" | `expo.out` long tails, bounce or elastic, slams, shakes, CSS transitions out of sync | See the motion rules in §4 |
| First frame of a scene jumps | Timeline started before layout settled | Live mode: `tl.pause()` then play after two `requestAnimationFrame`s (already in the template). Render mode skips this |
| Edits not showing | Browser cache | Add `?v=N` to the URL |
| Counter text flickers or jitters | Proportional digits | Use `font-variant-numeric: tabular-nums` on numbers |
