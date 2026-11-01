# Motion Edit Kit

Turns an edited talking video into a polished motion-graphics edit, inside Claude Code.

1. **make-presentation**: builds animated graphics from the video's own words and renders each one as a clip.
2. **edit-video**: puts those clips on the video as full-screen takeovers, side panels and floating cards. The
   speaker is cut out in front of the cards, and a few sound effects mark what moves. The original voice stays untouched.
3. **full-edit**: runs both in order and stops for your approval after each one.

Works for VSLs, YouTube videos, course lessons and any other talking video.

## What you need

- A Mac with Apple silicon (M1 or newer), with [Claude Code](https://code.claude.com) and Google Chrome.
  [Homebrew](https://brew.sh) is only needed if the Mac is missing ffmpeg, Node or Python.
- A GitHub account with access to this repository (it's private): accept the invite email from GitHub.
- Your video, already cut and colour-corrected (CapCut or any editor).

## Install

**1. Sign in to GitHub on your Mac** (one time), so Claude Code can download a private repository. In Terminal:

```
brew install gh
gh auth login
gh auth setup-git
echo 'export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1' >> ~/.zshrc
```

**2. Install the kit.** Open a new Terminal window and run:

```
claude plugin marketplace add flamingeos/motion-edit-kit
claude plugin install motion-edit@motion-edit-kit
```

**3. Run the setup.** Start Claude Code and ask it to "run the motion-edit setup". This runs
`plugins/motion-edit/setup.sh` once, which installs Whisper, the renderer and the sound effects (about 5 minutes).
The first transcription also downloads Whisper's model once (about 1.6 GB).

## Updates

New versions arrive when you run `claude plugin marketplace update motion-edit-kit` and then
`claude plugin update motion-edit@motion-edit-kit`. Restart Claude Code afterwards.

## Use

| Type | When |
|---|---|
| `/motion-edit:full-edit` | You have an edited video and want everything: graphics + edit + export |
| `/motion-edit:make-presentation` | You only want the animated graphics |
| `/motion-edit:edit-video` | You already have graphic clips and a cue sheet |

Claude asks for anything it's missing: the video, the brand colours, the speaker's name and the language.
It shows you the graphics before editing, and the finished edit before exporting.

## What's inside

```
plugins/motion-edit/
  setup.sh                     one-time install
  skills/make-presentation/    the graphics recipe, slide template and renderer
  skills/edit-video/           the editing recipe, its engine (Python + HyperFrames) and the plan template
  skills/full-edit/            the start-to-finish recipe
```

Each video gets its own project folder with a `plan.py`. That file holds every timing, layout and sound for
that video, so the engine itself never changes.

## Good to know

- **Tested on wide (16:9) videos.** Tall (9:16) videos need tall graphics and a first test run.
- **Sound effects are not included.** Setup downloads them straight from Mixkit (free to use in videos).
- **The word-timing model is non-commercial** (CC-BY-NC 4.0). For paid work, edit-video can skip it
  (`prep.py --no-align`). See [CREDITS.md](CREDITS.md).
