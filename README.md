# Motion Edit Kit

Give it a talking video you've already edited. It gives you back a finished video with animated graphics
that appear right when you say each idea. Sometimes the graphics fill the screen. Sometimes a card slides in
beside you, and you're cut out so you stand in front of it. Each move gets a soft sound effect, and your voice
stays exactly as you recorded it.

It works for sales videos (VSLs), YouTube videos, course lessons and any video of someone talking.

It runs inside **Claude Code**: you talk to Claude, and Claude does the work.

---

## Before you start

You need:

- [ ] **A Mac from 2020 or newer** (Apple M1 chip or later). Older Intel Macs can't run it.
- [ ] **Claude Code**, either the app or the Terminal version: [code.claude.com](https://code.claude.com)
- [ ] **Google Chrome**

---

## Install it: pick one way

### Way 1: Let Claude do it (easiest)

1. Open Claude Code.
2. Copy this whole message and send it to Claude:

   ```text
   Please install the Motion Edit Kit for me and do the complete setup. You have my permission to run
   the commands this needs.

   1. Install the kit:
      claude plugin marketplace add https://github.com/flamingeos/motion-edit-kit.git
      claude plugin install motion-edit@motion-edit-kit
   2. Run the kit's setup.sh from its install folder ("claude plugin list --json" shows it as installPath).
      If it asks for Homebrew, install Homebrew first, then run the setup again.
      Tell me when it's finished, and tell me if anything failed.
   ```

3. Claude asks before each step. Say **yes**.
4. When Claude says it's done, **close Claude Code and open it again**, so it loads the kit.

### Way 2: Do it yourself in Terminal

Open the **Terminal** app. Paste each line, press Enter, and wait for it to finish before the next one.

**Step 1. Install the kit.**

```bash
claude plugin marketplace add https://github.com/flamingeos/motion-edit-kit.git
```

```bash
claude plugin install motion-edit@motion-edit-kit
```

**Step 2. Run the setup.** This installs the tools the kit uses. It takes about 1–5 minutes.

```bash
bash "$(ls -d ~/.claude/plugins/cache/motion-edit-kit/motion-edit/*/ | sort -V | tail -1)setup.sh"
```
It should end with `Done.` (This line finds the newest installed version of the kit and runs its setup.)
If it says Homebrew is needed, install it from [brew.sh](https://brew.sh) and run the line again.

**Step 3.** Open Claude Code (or restart it if it was open).

---

## Make your first video

1. **Edit your video first** in CapCut or any editor: the cuts and the colour.
2. In Claude Code, type **`/motion-edit:full-edit`** and tell Claude where your video is.
3. Claude asks a few questions: your name, your brand colours and the language you speak.
4. Claude writes down every word you say, then makes the animated graphics from your words.
   **It shows you the graphics. Approve them or ask for changes.**
5. Claude puts the graphics on your video, with the cutout and the sound effects.
   **It shows you the finished video. Approve it or ask for changes.**
6. When you approve, Claude saves the final file.

The first video takes longer, because the tool that writes down your words downloads once (about 1.6 GB).

### Other commands

| Type this | When |
|---|---|
| `/motion-edit:full-edit` | You want everything: graphics + edit + final video |
| `/motion-edit:make-presentation` | You only want the animated graphics |
| `/motion-edit:edit-video` | You already have graphic clips and want them put on your video |

---

## Get updates

- **Way 1:** tell Claude: *"Update the Motion Edit Kit and run its setup again."*
- **Way 2:** in Terminal, run these three commands, then restart Claude Code:

```bash
claude plugin marketplace update motion-edit-kit
```
```bash
claude plugin update motion-edit@motion-edit-kit
```
```bash
bash "$(ls -d ~/.claude/plugins/cache/motion-edit-kit/motion-edit/*/ | sort -V | tail -1)setup.sh"
```

---

## If something goes wrong

| What you see | What to do |
|---|---|
| `claude: command not found` | Install the Terminal version of Claude Code: [code.claude.com](https://code.claude.com) |
| `Failed to clone marketplace` | Check your internet connection and that the link is typed exactly as above |
| `This kit needs a Mac with Apple silicon` | The Mac is too old (Intel). Use a 2020-or-newer Mac |
| `Google Chrome not found` | Install Google Chrome, then run the setup again |
| `/motion-edit:...` commands don't show up | Close Claude Code completely and open it again |
| Anything else | Tell Claude what happened and paste the error. Running the setup again is always safe |

---

## Good to know

- **Tested on wide (16:9) videos.** Tall (9:16) videos need tall graphics and a test run first.
- **Sound effects aren't inside the kit.** The setup downloads them straight from Mixkit (free to use in videos).
- **The tool that times each word has a non-commercial licence** (CC-BY-NC 4.0). For paid client work, you
  can ask Claude to skip it ("use --no-align"); the timing is then a little less exact. See [CREDITS.md](CREDITS.md).

### What's inside

```
plugins/motion-edit/
  setup.sh                     the one-time setup
  skills/make-presentation/    how to make the graphics (template + renderer)
  skills/edit-video/           how to edit (the engine + a plan template for each video)
  skills/full-edit/            the whole thing, start to finish
```

---

## Licence

Made by Juwany. Free to use, change and share under the [MIT licence](LICENSE): keep the copyright notice
when you share it. The outside tools it downloads have their own licences, listed in [CREDITS.md](CREDITS.md).
