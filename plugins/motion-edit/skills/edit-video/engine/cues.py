"""Find each graphic's spoken line in the forced-aligned transcript → build/cues.json.

The plan's CUES list gives, per clip, the first and last few words of its line (as said, any accents/punctuation).
Prints each line's start/end and the gap before it — the raw timing the EDL is built on.
Run: python cues.py <project>
"""

import json
import re
import sys
import unicodedata

from common import load_plan

norm = lambda s: re.sub(r"[^a-z0-9']", "", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode())


def main(project):
    root, plan = load_plan(project)
    w = json.loads((root / plan.TRANSCRIPT).read_text())
    W = [norm(x["text"]) for x in w]

    def find(phrase, after=0):
        p = [norm(t) for t in phrase.split()]
        for i in range(after, len(W) - len(p) + 1):
            if W[i:i + len(p)] == p:
                return i
        raise SystemExit(f"not found: {phrase!r} after word {after} — check the words in transcript/*.txt")

    out, k = [], 0
    for cid, a, b in plan.CUES:
        i = find(a, k)
        j = find(b, i) + len(b.split()) - 1
        k = j
        out.append({"id": cid, "start": w[i]["startMs"] / 1000, "end": w[j]["endMs"] / 1000,
                    "first": " ".join(x["text"].strip() for x in w[i:i + 6]), "last": w[j]["text"].strip()})
    (root / "build").mkdir(exist_ok=True)
    (root / "build/cues.json").write_text(json.dumps(out, indent=1))
    prev = 0
    for c in out:
        print(f"{c['id']}  {c['start']:7.2f} → {c['end']:7.2f}  ({c['end'] - c['start']:5.2f}s)  gap {c['start'] - prev:5.2f}  [{c['first']} … {c['last']}]")
        prev = c["end"]


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
