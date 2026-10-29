# Steal Competitor SEO

One command: `/steal theirsite.com yoursite.com`. It takes a local competitor apart in five parts - their pages, keywords, listings, backlinks, and what AI tools say about them. Then it builds the best pages onto your site, and writes a hit list and a dashboard to `output/<theirsite>/`.

The steps are in `.claude/skills/steal/SKILL.md`. The rules for each part are in `references/`. Read them before running.

## Rules

- Semrush spends the user's credits. Four calls per competitor, exactly as `references/semrush.md` lists. Check `output/<theirsite>/raw/` before every call and never buy the same report twice.
- Never copy a competitor's words. Rebuilt pages pass `code/check_rebuild.py` before anyone sees them.
- Never invent a number, review, price or credential. Use a `[YOUR ...]` placeholder.
- Never send an email, form or message. Find the contact, the user sends.
- Never solve or get around a captcha. Stop and ask.
- Never deploy, push or publish the user's site. New pages stay local until the user fills the amber slots and says go.
- Browser work runs in Claude in Chrome. Pages are read with the Firecrawl MCP.
- Output files are plain blocks, no tables, no filler. Shapes in `references/output-format.md`.

## Files

- `.claude/skills/steal/SKILL.md` - the `/steal` command
- `references/` - setup, the Semrush calls, and the rules for each part
- `code/sitemap.py` - every page in a site's sitemap, free
- `code/google_results.js` - reads a Google results page
- `code/ai_sources.js` - reads an AI answer and its sources
- `code/tally_ai.py` - counts who the AIs name and which sites they cite
- `code/check_rebuild.py` - fails a rebuilt page that is too close to the original
- `code/build_dashboard.py` - builds `output/<theirsite>/dashboard.html` from the run, one screen
- `code/build_compare.py` - their pages vs yours, side by side
- `code/gbp_categories.py` - every Google Business Profile category a business uses
- `templates/nextjs/` - the amber fill-in slot and the page schema helper, dropped into a Next.js site
