"""Every Google Business Profile category a business uses, not just the primary one.

Usage:
    python3 code/gbp_categories.py "Acme Plumbing 100 Main St Austin" "Blue Water Plumbing Austin"

Google Maps shows only the primary category on screen, but the place data it
loads holds the full list. This opens Maps in headless Chromium, catches that
data and prints the category list for each search. Free, no API key.
Search with the business name plus street or city so Maps lands on one place.
"""

import json
import re
import sys

from playwright.sync_api import sync_playwright

WAIT_MS = 9000
TRADE_WORDS = ("plumb", "drain", "contractor", "heating", "sewer", "electric", "roof", "hvac", "clean", "repair", "service")


def categories(query):
    responses = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-CA")
        page.set_default_timeout(45000)
        page.on("response", lambda r: responses.append(r) if ("tbm=map" in r.url or "/maps/preview/place" in r.url) else None)
        page.goto("https://www.google.com/maps/search/" + query.replace(" ", "+") + "?hl=en", wait_until="domcontentloaded")
        page.wait_for_timeout(WAIT_MS)
        bodies = []
        for r in responses:
            try:
                bodies.append(r.text())
            except Exception:
                pass
        browser.close()
    for body in bodies:
        for m in re.finditer(r'\[((?:"[A-Z][^"\[\]]{2,45}",?){1,15})\]', body):
            items = re.findall(r'"([^"]+)"', m.group(1))
            if items and any(w in items[0].lower() for w in TRADE_WORDS):
                return items
    return []


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for query in sys.argv[1:]:
        found = categories(query)
        print(f"{query} => {json.dumps(found) if found else 'not found - try the exact business name and street'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
