# Steal Competitor SEO

Pull a local competitor's SEO apart with Claude Code, then build their best pages onto your site.

```
git clone https://github.com/youtube-jono/steal-competitor-seo.git
cd steal-competitor-seo
claude
/steal theirsite.com yoursite.com
```

Or one part at a time: `/steal pages`, `/steal keywords`, `/steal listings`, `/steal backlinks`, `/steal ai`, `/steal build`.

## What you get

1. **Their pages** - every page they publish, the few that bring the traffic, and the best one rebuilt for you. Same sections, your words.
2. **Their keywords** - the searches that find them and never find you, sorted onto the page that should rank.
3. **Their listings** - every directory carrying their phone number that you're not on, with the page to add yourself.
4. **Their backlinks** - the links a business like yours can actually win, and how they got each one.
5. **What AI says** - 10 buyer questions asked in ChatGPT, Claude, Perplexity and Gemini, three times each. Every site the AIs cite, checked for your competitor's name, with who to contact to get on it.
6. **Built for you** - the rebuilt pages go straight onto your site, in your site's design, with schema and the sitemap done. Anything only you know (prices, reviews, licence, photos) shows as an amber box to fill in.

All of it lands in `output/<theirsite>/`: a one-screen `dashboard.html`, `compare.html` (their pages vs yours), `listings-pack.md` and `outreach.md`.

## What it needs

- **Claude Code**
- **Semrush**, through the claude.ai connector. Four calls per competitor, about 4,800 API units, each saved so it never pays twice.
- **Firecrawl MCP** to read pages. Free tier is enough.
- **Claude in Chrome**, logged in to ChatGPT, Claude, Perplexity and Gemini.

Setup for all three: `references/setup.md`.

## What it never does

- Copy their pages. Rebuilds keep the structure and nothing else, and a checker fails any page that shares more than 5% of its phrases.
- Invent proof. Prices, reviews and years stay as `[YOUR PRICE]` until you fill them in.
- Contact anyone. It finds the email or form. You send.
- Deploy your site. New pages stay local until you fill the amber boxes and say go.
- Get around a captcha. If Google asks, you solve it.

Everything I teach publicly is free. The rest of the SEO blueprint lives in the community: https://www.skool.com/automatable-free
