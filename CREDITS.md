# Credits and licences

The kit is the recipes, templates and engine scripts. Everything below is installed or downloaded on the user's
own machine by `setup.sh`, by `npx`, or on first use. None of it is bundled.

| What | Used for | Licence | Notes |
|---|---|---|---|
| [HyperFrames](https://hyperframes.heygen.com) (HeyGen) | Renders the edit; speaker cutouts (`remove-background`) | Apache-2.0 | Run with `npx hyperframes@latest` |
| [GSAP](https://gsap.com) | Animation in the presentation and the edit | GreenSock "no charge" standard licence | Loaded from a CDN inside the pages |
| [OpenAI Whisper](https://github.com/openai/whisper) | Transcription | MIT | |
| [PyTorch / torchaudio](https://pytorch.org) | Runs Whisper and the aligner | BSD-3-Clause | |
| MMS forced-alignment model (Meta, via torchaudio `MMS_FA`) | Exact word timings | **CC-BY-NC 4.0 (non-commercial)** | Downloaded by torchaudio on first use. Skip it with `prep.py --no-align` |
| [Playwright](https://playwright.dev) (`playwright-core`) | Records each slide frame by frame | Apache-2.0 | |
| [FFmpeg](https://ffmpeg.org) | All video and audio processing | LGPL / GPL | Installed with Homebrew |
| Sound effects ([Mixkit](https://mixkit.co)) | Transitions, clicks, the payoff hit | Mixkit Sound Effects Free License | Downloaded from Mixkit by `setup.sh`. The list is in `plugins/motion-edit/skills/edit-video/sounds.txt`. Free to use in videos; the files may not be resold or shared on their own |
| Google Fonts (Instrument Sans, Instrument Serif, IBM Plex Mono) | Presentation type | SIL Open Font License | Loaded from Google Fonts |

The sound sources were traced with the help of the [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)
project (Apache-2.0).
