"""List every page a site publishes, from its sitemap. Free - no Semrush credits.

Usage:
    python3 code/sitemap.py acmeplumbing.com
    python3 code/sitemap.py acmeplumbing.com --out output/acmeplumbing.com/raw/sitemap.json

Finds the sitemap through robots.txt (or the usual paths), follows sitemap
indexes, and groups the pages by the sitemap file they came from and by their
first folder. Prints a short summary. Exit code 2 means the site blocked the
fetch (Cloudflare and friends) - use Firecrawl's map tool instead.
"""

import argparse
import gzip
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from urllib.parse import urlparse

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
COMMON_PATHS = ["/sitemap_index.xml", "/sitemap.xml", "/wp-sitemap.xml", "/sitemap-index.xml"]
MAX_SITEMAPS = 60
TIMEOUT = 20


class Blocked(Exception):
    pass


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read()
    except urllib.error.HTTPError as err:
        if err.code in (401, 403, 429, 503):
            raise Blocked(f"{url} answered {err.code}")
        return None
    except (urllib.error.URLError, TimeoutError):
        return None
    if body[:2] == b"\x1f\x8b":
        body = gzip.decompress(body)
    text = body.decode("utf-8", errors="replace")
    if "Attention Required! | Cloudflare" in text or "cf-challenge" in text:
        raise Blocked(f"{url} is behind a bot check")
    return text


def base_urls(domain):
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    bare = domain[4:] if domain.startswith("www.") else domain
    return [f"https://{bare}", f"https://www.{bare}"]


def find_sitemaps(domain):
    for base in base_urls(domain):
        robots = fetch(base + "/robots.txt") or ""
        listed = [line.split(":", 1)[1].strip() for line in robots.splitlines()
                  if line.lower().startswith("sitemap:")]
        if listed:
            return listed
        for path in COMMON_PATHS:
            text = fetch(base + path)
            if text and ("<urlset" in text or "<sitemapindex" in text):
                return [base + path]
    return []


def local(tag):
    return tag.rsplit("}", 1)[-1]


def read_sitemap(url, seen, pages):
    if url in seen or len(seen) >= MAX_SITEMAPS:
        return
    seen.add(url)
    text = fetch(url)
    if not text:
        return
    try:
        root = ET.fromstring(text.strip().encode("utf-8"))
    except ET.ParseError:
        return
    source = urlparse(url).path.rsplit("/", 1)[-1] or url
    for node in root:
        loc = next((c.text.strip() for c in node if local(c.tag) == "loc" and c.text), None)
        if not loc:
            continue
        if local(root.tag) == "sitemapindex":
            read_sitemap(loc, seen, pages)
        else:
            lastmod = next((c.text.strip() for c in node if local(c.tag) == "lastmod" and c.text), "")
            pages.append({"url": loc, "sitemap": source, "lastmod": lastmod})


def first_folder(url):
    parts = [p for p in urlparse(url).path.split("/") if p]
    return parts[0] if len(parts) > 1 else "(top level)"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("domain")
    parser.add_argument("--out", help="write the full page list here as JSON")
    args = parser.parse_args()

    try:
        sitemaps = find_sitemaps(args.domain)
        if not sitemaps:
            print(f"No sitemap found for {args.domain}. Use Firecrawl's map tool instead.")
            return 1
        seen, pages = set(), []
        for sm in sitemaps:
            read_sitemap(sm, seen, pages)
    except Blocked as err:
        print(f"Blocked: {err}. Use Firecrawl's map tool instead.")
        return 2

    unique = list({p["url"]: p for p in pages}.values())
    by_sitemap = Counter(p["sitemap"] for p in unique)
    by_folder = Counter(first_folder(p["url"]) for p in unique)

    print(f"{args.domain}: {len(unique)} pages in {len(seen)} sitemap file(s)")
    print("By sitemap file:")
    for name, count in by_sitemap.most_common():
        print(f"  {name}: {count}")
    print("By first folder (top 12):")
    for name, count in by_folder.most_common(12):
        print(f"  /{name}/: {count}" if name != "(top level)" else f"  {name}: {count}")

    if args.out:
        with open(args.out, "w") as fh:
            json.dump({"domain": args.domain, "sitemaps": sorted(seen), "pages": unique}, fh, indent=1)
        print(f"Saved {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
