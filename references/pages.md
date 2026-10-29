# Their pages - pick, map, rebuild

## Picking the pages

The sitemap says how many pages they have. Semrush says which ones earn. On a local site, a handful of pages bring most of the traffic. Say that out loud in `1-pages.md`: "331 pages. The top 6 bring 82%."

Page types, read from the URL and the page:
- Homepage - never rebuilt. It ranks on the whole site's strength, not its layout.
- Service page - one service, one city. `/drain-cleaning-austin/`
- City page - every service, one area. `/service-areas/round-rock-plumbers/`
- Blog post - answers a question. `/blog/why-is-my-water-heater-leaking/`

Rebuild order: service pages first, then city pages for areas the user actually serves, then blog posts. Skip any page the user already has a real version of.

## The structure map

For each scraped page, write down what is there and in what order. This is what gets copied. Nothing else does.

- Title tag and H1
- Every H2 and H3, in order
- Word count (context only, never a target)
- What sits above the fold: phone, button, reviews badge, price, photo
- Proof on the page: review quotes, review count, years, licences, guarantees, before-and-after photos
- Prices or price ranges, and where they sit
- FAQ: how many questions, and the questions themselves
- Internal links: which other pages it links to
- Schema types, if Firecrawl returns them (LocalBusiness, FAQPage, Service)
- The call to action and how many times it repeats

## Rebuilding

The rebuilt page has the same skeleton: same page type, same sections, same order, same kinds of proof in the same spots. Everything inside the skeleton is new.

- Every sentence is written fresh. Never reword theirs line by line.
- Their FAQ questions are fair game, because they are what buyers ask. The answers are the user's own.
- Their proof becomes a slot for the user's proof: `[YOUR REVIEW COUNT]`, `[YOUR PRICE FOR THIS JOB]`, `[PHOTO: your van at a real job]`.
- The user's city and areas, the user's phone, the user's business name. Never theirs.
- Fix what theirs gets wrong: no price when buyers search for prices, no FAQ, a wall of text, the phone buried.

Then run the gate:

```
python3 code/check_rebuild.py output/<their-domain>/raw/page-<slug>.md output/<their-domain>/rebuilds/<slug>.md
```

It fails if more than 5% of the rebuild's 5-word phrases appear on their page, or if the competitor's name, phone or domain shows up. Rewrite the flagged lines and run it again. A page is only shown once it passes.

## Rebuild file shape

```
# Drain cleaning in Austin - rebuilt from acmeplumbing.com/drain-cleaning-austin/

Their page: <traffic> visits a month (Semrush estimate), <N> keywords.
Gate: <share>% shared phrases - pass.

Title: Drain Cleaning Austin | Price Up Front | Dave's Plumbing
Meta description: ...
URL: /drain-cleaning-austin/

---

(the page, top to bottom, in markdown)
```
