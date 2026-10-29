# Build it - the rebuilds become real pages

A report tells you what to do. This part does it. Every rebuild that passed the gate becomes a page on the user's own site, in the site's own design, ready for the user to fill in their proof and go live.

Two or three pages per run: the rebuild picks from Part 1. Never more without asking.

## First, find out what the site is

Ask where the site's code lives if it isn't obvious. Then:

- **Next.js** (a `package.json` with `next`, an `app/` folder): build the pages in code. Most of this file.
- **WordPress**: create each page as a draft through the WordPress MCP (Novamira). Never publish. The user reviews the draft and fills the slots.
- **Anything else** (Wix, Squarespace, Webflow, Shopify): write each page as `output/<their-domain>/pages/<slug>.html`, plain and paste-ready, and say where in their builder it goes.

## Next.js: build with what the site already has

1. Read one existing service or content page and the components it imports. Build the new pages from those same components, in the same way. Never invent a section style, a colour or a font. The new pages should look like they were always there.
2. Copy `templates/nextjs/Slot.tsx` into the site's components folder if it has nothing like it, and `templates/nextjs/local-schema.ts` into `lib/`. Fix their two import paths to match the site.
3. One folder per page: `app/<slug>/page.tsx`. The slug is the rebuild's URL.
4. Put the copy in arrays at the top of the file (cards, steps, FAQs), then render. The words come from the gated rebuild file, line for line. Section headings may be new words, never theirs.
5. Every gap the user must fill is a slot written as `[[YOUR PRICE RANGE]]` and rendered with `fill()`. It shows up in amber on the page. Never fill one with a guess.
6. Metadata: the rebuild's title and meta description, and a canonical URL.
7. Schema: `localPageSchema()` - the service, the area and the FAQ. Answers that still hold a slot stay out of the schema until filled. Never add a rating or review count.
8. Add each page to the sitemap (`app/sitemap.ts` or wherever the site lists its pages).
9. Link the new pages to each other, and from the closest existing page if there is an obvious one.
10. If a shared component only takes plain text and a slot needs to sit inside it, widen its type from `string` to `React.ReactNode`. Show the user that diff. Never change how a shared component looks.

## Check before saying done

- `npx tsc --noEmit` passes
- The dev server serves every new page with a 200, and the sitemap lists them
- `python3 code/check_rebuild.py output/<their-domain>/raw/page-<slug>.md <site>/app/<slug>/page.tsx --forbid "<their name>" --forbid "<their phone>"` passes on the finished page, not just the draft
- A screenshot of each page, desktop and phone width, and no sideways scroll on the phone
- Count the slots on each page and list them for the user, so they know exactly what to fill

## Never

- Deploy, push or publish. The pages stay local until the user fills the slots and says go.
- Replace a slot with stock photos, an AI image or a made-up number.
- Touch pages the run didn't create, beyond the sitemap line and a widened type.

## The side-by-side

Add `"keyword"` (the gap keyword the page targets) to each rebuild in `data.json`, and `"site_preview"` (where the site runs locally). Then `python3 code/build_compare.py output/<their-domain>` writes `compare.html`: their page and yours, first screen, side by side, with the keyword, its volume and their rank.

## Then tell the user

Each page's local URL, how many slots it has, and the three slots that matter most (price, review count, licence). Add the pages to `data.json` under each rebuild as `"page": "/<slug>"` and `"slots": <count>` so the dashboard links to them.
