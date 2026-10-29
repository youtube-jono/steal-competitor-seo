---
name: steal
description: Pull a local competitor's SEO apart and turn it into real pages on your site - their best pages (rebuilt in your words and built into your site), the keywords they rank for that you don't, their directory listings, the backlinks you can win, and the sites AI tools cite when buyers ask who to hire. Use when someone runs /steal or asks to steal, copy, reverse-engineer or out-rank a competitor's SEO.
argument-hint: "their-site.com your-site.com, or one part: pages | keywords | listings | backlinks | ai | build"
---

# /steal

One competitor in, real pages and one hit list out. Six parts, in this order:

1. Their pages - the few that bring the traffic, rebuilt for you
2. Their keywords - the searches that find them and never find you
3. Their listings - every directory that carries their phone number
4. Their backlinks - the links a business like yours can actually win
5. What AI says - who ChatGPT, Claude, Perplexity and Gemini recommend, and the sites they cite
6. Build it - the rebuilt pages go onto the user's own site, ready to fill in and launch

Read every file in `references/` before starting. They hold the exact calls, the rules and the file shapes. This file is the order of work.

## One part at a time

`/steal their-site.com your-site.com` runs all six parts in order. A part name runs just that part:

- `/steal pages` - Part 1
- `/steal keywords` - Part 2
- `/steal listings` - Part 3
- `/steal backlinks` - Part 4
- `/steal ai` - Part 5
- `/steal build` - Part 6

A single part reads `output/<their-domain>/inputs.md` from the last run. If there is none, do Step 0 first. If a part needs another part's output (Part 5 needs the keyword gap, Part 6 needs the rebuilds), check `raw/` and the part files. Run the missing part only if its data isn't there, and say so. After any part, update `data.json`, set its `"stage"` (1 after pages, keywords and links; 2 after listings and the profile; 3 after the AI search) and rebuild the dashboard. Sections past the current stage show a placeholder, so the dashboard fills in as the user goes.

## Hard rules

- **Semrush: connector first, API key second.** If the claude.ai connector is missing or out of units, `code/semrush_fallback.py` runs the same report with `SEMRUSH_API_KEY` from `.env`.
- **Semrush costs credits. Four calls per competitor, no more.** The exact calls and row caps are in `references/semrush.md`. Every result is saved to `output/<their-domain>/raw/` the moment it lands. Before any Semrush call, check `raw/` - if the file is there, read it and do not call again. Never re-run a report to "refresh" it unless the user asks.
- **Rebuild, never copy.** Same page type, same sections in the same order. Every word, photo, price and review is the user's own. `python3 code/check_rebuild.py` must pass before a rebuilt page is shown. Google shows the original and skips the copy.
- **Never invent proof.** Prices, review counts, years in business, licences, guarantees: if the user has not given it, write `[YOUR PRICE]`, `[YOUR REVIEW COUNT]` and so on. A placeholder is honest. A made-up number is not.
- **Semrush traffic is an estimate.** Use it to rank what to build first. Never quote it as the competitor's real numbers.
- **Never contact anyone.** This skill finds the email address or form. The user sends every message.
- **Browser work runs in Claude in Chrome**, the user's own logged-in browser. If it is not connected, stop and say so: the extension is at https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn . If Google shows a captcha, stop and ask the user to solve it, then carry on. Never try to get around one.
- **Pages are read with the Firecrawl MCP** (`firecrawl_scrape`, `firecrawl_map`, `firecrawl_search`). Setup is in `references/setup.md`.
- **Never deploy, push or publish** the user's site. Part 6 builds pages locally. Going live is the user's call.
- Output files follow `references/output-format.md`: plain blocks, no tables, no filler.

## Step 0 - inputs (2 minutes)

Make `output/<their-domain>/` and write `inputs.md` with:

- **You:** business name, website, phone exactly as listed, city, main service.
- **Them:** the competitor's website. If the user did not name one, Google `[main service] [city]` in Chrome and take the top organic result that is a real local business (skip directories, franchises and lead-gen sites). Take the next one down as the second rival - it only feeds the two gap reports.
- **Their phone and business name**, read off their homepage with Firecrawl.
- **Semrush database:** `us`, `ca`, `uk`, `au` and so on, by the business's country.

Ask only for what you cannot find. Then run the five parts without stopping, unless a hard rule says stop.

## Part 1 - their pages

1. `python3 code/sitemap.py <their-domain> --out output/<their-domain>/raw/sitemap.json` - every page they publish, free. If it exits 2 (blocked), use `firecrawl_map` instead.
2. Semrush call 1: top pages (`references/semrush.md`).
3. Put the two together: "They publish N pages. These 6 bring X% of the traffic." Name each page's type: service page, city page, blog post, homepage.
4. Pick the 3 best pages to rebuild: highest traffic that is a service or city page the user does not have yet. The homepage is never a rebuild target.
5. Scrape those 3 with `firecrawl_scrape` (markdown). Save to `raw/page-<slug>.md`. Write each page's structure map as `references/pages.md` describes.
6. Write `1-pages.md`.
7. Rebuild the top pick into `rebuilds/<slug>.md` following `references/pages.md`. Run `python3 code/check_rebuild.py raw/page-<slug>.md rebuilds/<slug>.md --forbid "<their name>" --forbid "<their phone>"`. Rewrite until it passes. Offer to rebuild the other two.

## Part 2 - their keywords

1. Semrush call 2: keyword gap (`references/semrush.md`). Keywords both rivals rank for, that the user does not rank for at all.
2. Sort every keyword onto a page: one of the rebuilds, a page the user already has (check their sitemap with `code/sitemap.py`), or a new page to build.
3. Write `2-keywords.md`.

## Part 3 - their listings

Follow `references/citations.md`:

1. In Chrome, Google their phone in quotes, minus their own site. Every page of results. Run `code/google_results.js` on each page.
2. Google their business name in quotes plus the city, minus their own site. Every page.
3. Keep listings only. Drop phone-lookup spam and their own social pages. A name-search hit counts only if the listing shows their phone or street address - check with `firecrawl_scrape` when the snippet doesn't show it.
4. Run the same two searches for the user's phone and name. Same check: a same-name business elsewhere is not the user.
5. The gap is every directory they are on and the user is not. For each one, the listing URL and the page where a business adds itself.
6. Google Business Profile: `python3 code/gbp_categories.py "<their name> <street or city>"` for them and the top 3 map-pack businesses. Maps shows only the primary category; this reads the full list.
7. Write `3-citations.md` and `listings-pack.md` (the user's exact details to paste, the categories to add, and every add-your-business link). Directory domains found in Part 4 get added here too.
8. Write `have.txt`: the user's own domain and every directory they are already on, one domain per line. Part 5 uses it.

## Part 4 - their backlinks

1. Semrush call 3: backlink gap (`references/semrush.md`).
2. Sort every domain into Win it, Directory (moves to `3-citations.md`) or Skip, using `references/backlinks.md`.
3. For each Win it domain, find the page that links to them with `firecrawl_search` (`site:<domain> <their brand>`) and say how they got it: sponsor, supplier, member, partner, press, forum post.
4. Write `4-backlinks.md` and `outreach.md`: one short ready-to-send email per target, to the exact address found. The user sends them.

## Part 5 - what AI says

Follow `references/ai-check.md`:

1. Semrush call 4: questions for `[main service] [city]`.
2. Rank the user's services by "[service] [city]" searches, then build the grid in `references/ai-check.md`: top services times places, asked as "best", plus a cost and (for emergency trades) an urgency version. Discovery only. Write `5-ai/questions.md` and show it before the run.
3. Ask the questions in ChatGPT, Claude, Perplexity and Gemini at the same time (one tab each), 3 fresh chats per AI, starting with the top "best" question. Keep adding batches until one finds no new sources. Each chat is saved to `5-ai/runs/` as it finishes, so a stopped run picks up where it left off.
4. `python3 code/tally_ai.py output/<their-domain>` - which sites get cited, how often, and how often each business is named.
5. Every cited page the user is not on: `firecrawl_scrape` it. Is the competitor named on it? What kind of page is it (best-of list, directory, news, forum, blog that takes guest posts)? Who do you contact, and how?
6. Write `5-ai/sources.md`.

## Part 6 - build it

Follow `references/build.md`:

1. Find out what the site runs on and where its code lives.
2. Build each gated rebuild as a real page on the site, in the site's own design. Gaps only the user can fill show as amber slots.
3. Add the pages to the sitemap, link them to each other, and add the service and FAQ schema.
4. Type-check, load every page, screenshot desktop and phone, and run the gate on the finished page.
5. `python3 code/build_compare.py output/<their-domain>` - their page and yours side by side, first screen, with the target keyword. Needs `site_preview` and each rebuild's `keyword` in `data.json`.
6. Never deploy. The pages stay local until the user fills the slots and says go.

## Finish

1. Write `data.json`: the calls made along the way (rebuild picks, keyword groups, listings, backlink sort, hit list). Shape in `references/output-format.md`. Numbers never go in it - the dashboard reads those from `raw/` and `5-ai/runs/`.
2. `python3 code/build_dashboard.py output/<their-domain>` - writes `dashboard.html`, one screen: a stat strip and six short lists. No prose on it.
3. Reply with the five headline numbers, one line each, and the full path to `dashboard.html`.
