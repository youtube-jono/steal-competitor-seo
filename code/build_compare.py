"""Side-by-side: their page vs your rebuilt page, one row per topic.

Usage:
    python3 code/build_compare.py output/<their-domain>

Reads the rebuilds in data.json ("url" = their page path, "page" = yours) and
"site_preview" (where your site runs, e.g. http://localhost:3000). Screenshots
both pages above the fold with headless Chromium, adds the page's target keyword
from the cached keyword gap ("keyword" in each rebuild), and writes compare.html
plus the images in shots/.
"""

import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1280, "height": 800}

def e(value):
    return html.escape(str(value), quote=True)


def shoot(page, url, path):
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.add_style_tag(content="nextjs-portal { display:none !important; }")  # hide the Next.js dev badge
    page.wait_for_timeout(800)
    page.screenshot(path=str(path))


def keyword_line(rb, gap):
    """One line from the cached keyword gap: the keyword this page targets."""
    row = gap.get(rb.get("keyword", ""))
    if not row:
        return ""
    return f'<p class="kw">{e(row[0])} · {float(row[4]):,.0f} searches a month · they rank #{e(row[1])}, you don\'t rank</p>'


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    folder = Path(sys.argv[1])
    data = json.loads((folder / "data.json").read_text())
    base_them = f'https://www.{data["them"]["domain"].removeprefix("www.")}'
    preview = data.get("site_preview", "").rstrip("/")
    if not preview:
        print("data.json needs \"site_preview\" - where your site runs, e.g. http://localhost:3000")
        return 1
    shots = folder / "shots"
    shots.mkdir(exist_ok=True)
    gap = {}
    gap_file = folder / "raw" / "semrush-keyword-gap.csv"
    if gap_file.is_file():
        gap = {r.split(";")[0]: r.split(";") for r in gap_file.read_text().splitlines()[1:]}
    blocks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT)
        for i, rb in enumerate([r for r in data.get("rebuilds", []) if r.get("page")], 1):
            shoot(page, base_them + rb["url"], shots / f"{i}-theirs.png")
            shoot(page, preview + rb["page"], shots / f"{i}-yours.png")
            print(f'{rb["name"]}: both screenshots saved')
            blocks.append(f"""<section><h2>{e(rb["name"])}</h2>{keyword_line(rb, gap)}
<div class="pair"><figure><figcaption>Theirs · {e(rb["url"])}</figcaption><img src="shots/{i}-theirs.png" alt="Their page"></figure>
<figure><figcaption>Yours · {e(rb["page"])}</figcaption><img src="shots/{i}-yours.png" alt="Your rebuilt page"></figure></div>
</section>""")
        browser.close()
    out = folder / "compare.html"
    out.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Their page vs yours</title><style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#f5f4ed; color:#141413; font:13px/1.4 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif; }}
.wrap {{ max-width:1280px; margin:0 auto; padding:20px 24px 32px; }}
h1 {{ font:500 26px/1.1 "Tiempos Text",Georgia,serif; margin-bottom:14px; }}
section {{ background:#faf9f5; border:1px solid #ece9df; border-radius:12px; padding:14px; margin-bottom:14px; }}
h2 {{ font:500 17px/1.2 "Tiempos Text",Georgia,serif; margin-bottom:10px; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
figure {{ min-width:0; }} img {{ width:100%; border:1px solid #ece9df; border-radius:8px; display:block; }}
figcaption {{ font:11px ui-monospace,Menlo,monospace; color:#87867f; margin-bottom:6px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.kw {{ font:12px ui-monospace,Menlo,monospace; color:#c96442; margin:-4px 0 10px; }}
@media (max-width:860px) {{ .pair {{ grid-template-columns:1fr; }} .wrap {{ padding:16px; }} }}
</style></head><body><div class="wrap"><h1>{e(data["them"]["name"])}'s pages vs yours</h1>{"".join(blocks)}</div></body></html>""")
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
