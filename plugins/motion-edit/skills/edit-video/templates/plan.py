"""Plan for one video: everything that changes from video to video. The engine scripts read this file.

Fill it in this order: CUES (run cues.py) → LOOK + PANEL (from assets/frame.png and a test snapshot) → EDL →
CUTOUTS (run cutouts.py) → SFX (run build.py). Times are seconds in the edited video; quote the transcript's
word times next to each EDL row so the next person can see why a graphic lands where it does.
"""

TITLE = "__TITLE__"
SPEAKER = "the speaker"            # their first name reads better in the review sheets
FOOTAGE = "assets/footage.mp4"     # the edited video, re-encoded to 30 fps by prep.py
VOICE = "__VOICE__"                # the edited video as delivered: its sound goes into the export untouched
TRANSCRIPT = "transcript/footage-aligned.json"
FOOTAGE_DURATION = __DURATION__
TOTAL = __TOTAL__                  # the last graphic may hold ~0.5–1 s past the last word: raise this to allow it
MEDIA_START = 2 / 30               # frames 0–1 of every rendered clip carry leftovers from the recorder: skip them
VOICE_LOUDNESS = None              # None = measured from VOICE (median momentary LUFS of the speech)

# What shows behind the speaker when they reframe left for a panel, and where their face is.
# wall / wallLight / wallDark: the wall colour at the frame's right edge, a bit lighter, a bit darker (pick them
# from assets/frame.png). face: the point the speaker zooms around (between the eyes). mask: the cutout is
# hidden left of mask[0] and fully shown from mask[1] — set it just inside the speaker's body edge that faces
# the panel, so only that side sits in front of the card. card: the graphics' own background colour.
LOOK = {"wall": "#474d50", "wallLight": "#4f5558", "wallDark": "#2e3335", "plateAt": "70% 55%",
        "face": [950, 420], "mask": [960, 1080], "card": "#f4efe9"}

# Panels and cards: lay = [x, y, scale] of the graphic (scale 0.56 = a big centred card on the right), shift =
# how far the speaker moves left (px) so they stand beside it. Rows can override with their own "lay"/"shift".
PANEL = {"lay": [790, 238, 0.56], "shift": -440}

# (clip id, first words of its line, last words of its line) — as said in the transcript.
CUES = [
    # ("01", "first few words", "last few words"),
]

# id, mode, enter, start, exit-start, exit, extra.
#   mode:  full | right | card | right2full
#   enter: zoom | slow-zoom | whip | push | iris | slide | pop     (slide/pop for right/card)
#   exit:  fade | fade-to | pop-to | slide-out | pop-out | cover | end
#   extra: "segs": [[out, media], …]  pace a clip to the words: from second <out> play the clip from its media
#                                     time <media>, holding the previous part's last frame until then.
#                                     A single [[start, m]] just starts the clip m seconds in.
#          "irisAt": [x, y]           where an iris opens from (the centre of the panel it replaces)
#          "expandAt": t, "zoomExpand": True   right2full: the panel grows to full screen at t
EDL = [
    # ("01", "full", "zoom", 0.42, 4.45, "fade-to", {}),
    # ("02", "right", "slide", 4.72, 12.40, "cover", {}),
]

# Speaker cutouts for panels/cards: {clip id: (first footage frame, last footage frame[, {"fadeOut": t, "fadeFrames": 5}])}.
# Cover the whole time the card is on screen; for right2full, fade the cutout out at expandAt.
CUTOUTS = {
    # "02": (140, 390),
}

# Sound cues: (when, sound, dB under the voice, what is on screen).
#   when: "07:enter" | "10:expand" | "06@1.75" (a moment inside clip 06, in the clip file's own time)
#   a trailing "<" puts the sound's END there (riser into the boom), ">" its START.
SFX = [
    # ("01:enter", "air-quick", 12, "01 title zooms in"),
]

# Extra or changed sounds: key → (file in the sound library, start, length or None, fade-out).
SOUNDS = {}
