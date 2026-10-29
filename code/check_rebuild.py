"""Gate for a rebuilt page: is it really new, or a reworded copy?

Usage:
    python3 code/check_rebuild.py output/<their-domain>/raw/page-<slug>.md output/<their-domain>/rebuilds/<slug>.md
    python3 code/check_rebuild.py THEIRS.md YOURS.md --forbid "Acme Plumbing" --forbid 512-555-0199

Splits both pages into 5-word phrases and counts how many of the rebuild's
phrases also appear on their page. Only the page below the first --- line is
checked, so the notes at the top can name their URL. FAQ questions (lines ending in "?") are
allowed to match - they are what buyers ask. Answers are not.

Fails (exit 1) when:
  - more than 5% of the rebuild's phrases are on their page, or
  - their domain, business name or phone shows up in the rebuild.
Their domain is read from the path (output/<their-domain>/...) when it can be.
"""

import argparse
import re
import sys
from pathlib import Path

PHRASE_WIDTH = 5
MAX_SHARED = 0.05
SHOW_SHARED = 12


def words(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)          # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)       # links -> text
    text = re.sub(r"https?://\S+", " ", text)
    return re.findall(r"[a-z0-9$']+", text.lower())


def phrases(text):
    w = words(text)
    return {" ".join(w[i:i + PHRASE_WIDTH]) for i in range(len(w) - PHRASE_WIDTH + 1)}


def answer_lines(text):
    """The rebuild minus FAQ questions and markdown furniture."""
    keep = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("#>*- ").strip()
        if not stripped or stripped.endswith("?"):
            continue
        keep.append(stripped)
    return "\n".join(keep)


def page_body(text):
    """Rebuild files open with notes, then a --- line, then the page. Check the page only."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


def domain_from_path(path):
    parts = Path(path).resolve().parts
    if "output" in parts:
        i = parts.index("output")
        if i + 1 < len(parts) and "." in parts[i + 1]:
            return parts[i + 1]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("theirs")
    parser.add_argument("yours")
    parser.add_argument("--forbid", action="append", default=[], help="text that must never appear (name, phone)")
    args = parser.parse_args()

    for path in (args.theirs, args.yours):
        if not Path(path).is_file():
            print(f"Missing file: {path}")
            return 2

    theirs = Path(args.theirs).read_text(errors="replace")
    yours = page_body(Path(args.yours).read_text(errors="replace"))

    forbid = list(args.forbid)
    domain = domain_from_path(args.theirs)
    if domain:
        forbid.append(domain.removeprefix("www.").split(".")[0])

    their_phrases = phrases(theirs)
    your_phrases = phrases(answer_lines(yours))
    if not your_phrases:
        print("The rebuild has no text to check.")
        return 2

    shared = sorted(your_phrases & their_phrases)
    share = len(shared) / len(your_phrases)
    lowered = yours.lower()
    leaks = [term for term in forbid if term and term.lower() in lowered]

    print(f"Rebuild phrases: {len(your_phrases)}")
    print(f"Also on their page: {len(shared)} ({share:.1%}) - limit {MAX_SHARED:.0%}")
    for phrase in shared[:SHOW_SHARED]:
        print(f"  shared: \"{phrase}\"")
    for term in leaks:
        print(f"  LEAK: \"{term}\" appears in the rebuild")

    passed = share <= MAX_SHARED and not leaks
    print("PASS" if passed else "FAIL - rewrite the shared lines and run again")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
