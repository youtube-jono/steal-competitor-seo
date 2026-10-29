"""Count what the AI runs said: who gets named, and which sites get cited.

Usage:
    python3 code/tally_ai.py output/<their-domain>

Reads every 5-ai/runs/*.json (shape in references/ai-check.md) and writes
5-ai/tally.md. Domains listed in have.txt (one per line - the user's own site
and the directories they are already on) are marked as already there.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

ENGINE_NAMES = {"chatgpt": "ChatGPT", "claude": "Claude", "perplexity": "Perplexity", "gemini": "Gemini"}
TOP_BUSINESSES = 12
TOP_URLS_PER_DOMAIN = 3


def domain_of(url):
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def clean_url(url):
    """One spelling per page: no www, no tracking tags, no trailing slash."""
    parts = urlparse(url.strip())
    if not parts.netloc:
        return ""
    host = parts.netloc.lower().removeprefix("www.")
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query)
                       if not k.startswith("utm_") and k not in ("ref", "srsltid")])
    return urlunparse(("https", host, parts.path.rstrip("/"), "", query, ""))


def chats(n):
    return f"{n} chat" if n == 1 else f"{n} chats"


def load_runs(runs_dir):
    runs, bad = [], []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            run = json.loads(path.read_text())
        except json.JSONDecodeError:
            bad.append(path.name)
            continue
        if not isinstance(run, dict) or "engine" not in run or "sources" not in run:
            bad.append(path.name)
            continue
        runs.append(run)
    return runs, bad


def load_have(folder):
    path = folder / "have.txt"
    if not path.is_file():
        return set()
    lines = [line.strip().lower() for line in path.read_text().splitlines()]
    return {domain_of(l) if "://" in l else l.removeprefix("www.") for l in lines if l and not l.startswith("#")}


def pct(part, whole):
    return f"{part / whole:.0%}" if whole else "0%"


def tally(runs, have):
    per_engine = Counter(r["engine"] for r in runs)
    comp_by_engine = Counter(r["engine"] for r in runs if r.get("competitor_named"))
    you_by_engine = Counter(r["engine"] for r in runs if r.get("you_named"))
    named = Counter()
    for r in runs:
        for name in {n.strip() for n in r.get("named", []) if n.strip()}:
            named[name] += 1

    domain_chats = Counter()
    domain_engines = defaultdict(set)
    domain_urls = defaultdict(Counter)
    for r in runs:
        seen = set()
        for url in {clean_url(u) for u in r.get("sources", [])}:
            d = domain_of(url)
            if not d:
                continue
            domain_urls[d][url] += 1
            domain_engines[d].add(r["engine"])
            seen.add(d)
        for d in seen:
            domain_chats[d] += 1

    total = len(runs)
    lines = [f"# AI tally - {total} chats", ""]
    lines += ["## Who gets named", ""]
    comp_total = sum(comp_by_engine.values())
    you_total = sum(you_by_engine.values())
    lines.append(f"Competitor: named in {comp_total} of {total} chats ({pct(comp_total, total)})")
    lines.append(f"You: named in {you_total} of {total} chats ({pct(you_total, total)})")
    for engine, count in sorted(per_engine.items()):
        label = ENGINE_NAMES.get(engine, engine)
        lines.append(f"{label}: competitor {comp_by_engine[engine]} of {count}, you {you_by_engine[engine]} of {count}")
    lines += ["", "Every business named, most often first:"]
    for name, count in named.most_common(TOP_BUSINESSES):
        lines.append(f"- {name}: {chats(count)}")

    lines += ["", f"## Cited sites ({len(domain_chats)} domains)", ""]
    for d, count in domain_chats.most_common():
        engines = ", ".join(sorted(ENGINE_NAMES.get(e, e) for e in domain_engines[d]))
        mark = " - already there" if d in have else ""
        lines.append(f"### {d} - {chats(count)} ({engines}){mark}")
        for url, n in domain_urls[d].most_common(TOP_URLS_PER_DOMAIN):
            lines.append(f"{url} ({n})")
        lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    folder = Path(sys.argv[1])
    runs_dir = folder / "5-ai" / "runs"
    if not runs_dir.is_dir():
        print(f"No runs yet: {runs_dir} does not exist.")
        return 1
    runs, bad = load_runs(runs_dir)
    for name in bad:
        print(f"Skipped unreadable run file: {name}")
    if not runs:
        print("No usable runs to count.")
        return 1
    report = tally(runs, load_have(folder))
    out = folder / "5-ai" / "tally.md"
    out.write_text(report + "\n")
    print(report)
    print(f"\nSaved {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
