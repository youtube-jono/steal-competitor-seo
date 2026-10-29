# Their listings - find every directory they're on

A citation is the business listed on another site with its name, address and phone. Google checks them against each other to trust the business is real. The competitor's list is a ready-made map of the directories that matter in their city and trade.

## The searches (Claude in Chrome, free)

Run each one on google.com with `&gl=<country>&hl=en&filter=0` on the end (`filter=0` shows the results Google would otherwise hide as similar). Page through with `&start=10`, `&start=20` until there is no next page. On every page, paste `code/google_results.js` into the JavaScript tool and keep what it returns in `raw/google-<search>.json`.

1. Their phone, in quotes, minus their own site: `"512-555-0199" -site:acmeplumbing.com`
2. The same phone with no dashes: `"5125550199" -site:acmeplumbing.com`
3. Their name in quotes plus the city, minus their own site: `"Acme Plumbing" Austin -site:acmeplumbing.com`

Google treats `(512) 555-0199`, `512-555-0199` and `512.555.0199` as the same search, so one dashed version covers all three. Google often serves only one or two pages for these searches. That is the whole result, not a block.

Google gets suspicious after about a dozen searches in a row. Wait a few seconds between pages. If the script returns `captcha: true` (Google's "unusual traffic" page), stop. Ask the user to solve it in their browser, then carry on from the same page.

Then run searches 1 and 3 for the user's own phone and name.

Businesses often use different phone numbers on different sites (Acme Plumbing uses three). That is why the name search matters most. To confirm a directory, `firecrawl_search` `"<their name>" <city> site:<directory>` and check the street address.

## What counts as a listing

Keep:
- Directories and review sites: Yelp, HomeStars, BBB, YellowPages, Houzz, Angi, Nextdoor, Thumbtack, 411, n49, Cylex, Hotfrog, city directories
- Trade bodies and local associations that list members
- Best-of lists that show the phone (these also go to Part 5)

Drop:
- Their own site, and any page on a domain they own
- Phone-lookup spam: random subdomains on `blob.core.windows.net`, `storage.googleapis.com`, `web.core.windows.net`, `s3-external`, odd TLDs (`.boats`, `.cfd`, `.monster`), titles like "Who called from..."
- Their social profiles (they have them, the user needs their own, nothing to learn)

## The same-name trap

A name search finds every business with that name. "Dave's Plumbing" turns up a Dallas company and a BBB profile for someone else. A name hit only counts when the listing shows the same phone or the same street address. If the Google snippet doesn't show it, `firecrawl_scrape` the listing and check. Same rule for the user's side: never count someone else's listing as theirs.

## The gap

Every directory the competitor is on and the user is not. For each one:
- Their listing URL (shows the category they picked and how many reviews they have there)
- Where a business adds itself. Find it with `firecrawl_search`: `<directory> add your business` or `<directory> claim listing`. Never guess the URL.
- Free or paid, if the add page says

Add any directory domains from the Part 4 backlink gap, marked "from their backlinks".

## The basics everyone needs

Whether or not the competitor has them, check the user is on these. Name and home domain only - find the add page live.

Everywhere: Google Business Profile (business.google.com), Bing Places (bingplaces.com), Apple Business Connect (businessconnect.apple.com), Yelp, BBB, Nextdoor, Foursquare, Houzz

Canada: YellowPages.ca, HomeStars, 411.ca, n49, Cylex Canada, Hotfrog Canada, TrustedPros

US: YellowPages.com, Angi, HomeAdvisor, Thumbtack, Manta, Superpages

## Google Business Profile categories

Google Maps shows only the primary category. `python3 code/gbp_categories.py "<name> <street or city>"` reads the full list from the place data. Run it for the competitor and the top 3 map-pack businesses. The user adds only categories for work they really do. Reviews can't be copied, so the profile part is categories only.

## Where to add yourself

`firecrawl_scrape` the directory's homepage with the `links` format and look for add, claim, submit, register or sign-up. If none, say "no add form found". Never guess the URL.

## Keep the details identical

Name, address and phone must match the user's Google Business Profile character for character on every listing. Pick one phone format and one way to write the street, and use it everywhere.
