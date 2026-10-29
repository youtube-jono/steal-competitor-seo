# Output files

Everything for one competitor lives in `output/<their-domain>/`. Plain blocks, short lines, no tables, no intros. A person should be able to act on any file without reading another.

```
output/<their-domain>/
  inputs.md            you, them, the database
  raw/                 everything bought or scraped, never re-bought
  1-pages.md
  rebuilds/<slug>.md
  2-keywords.md
  3-citations.md
  4-backlinks.md
  have.txt             your domain + directories you're already on
  5-ai/questions.md
  5-ai/runs/*.json
  5-ai/tally.md
  5-ai/sources.md
  listings-pack.md     your details to paste + every add-your-business link
  outreach.md          one short email per link target, you send
  data.json            the calls made, for the dashboard
  dashboard.html       one screen, built by code/build_dashboard.py
  compare.html         their pages vs yours, built by code/build_compare.py
```

Every Semrush number is labelled an estimate the first time it appears in a file.

---

## inputs.md

```
# Inputs

You: Dave's Plumbing · davesplumbing.com · (512) 555-0142 · Austin · plumber
Them: Acme Plumbing · acmeplumbing.com · 512-555-0199
Second rival (gap reports only): bluewaterplumbing.com
Semrush database: us
```

---

## 1-pages.md

```
# Their pages

They publish <N> pages (sitemap). Semrush estimates <N> visits a month. The top <N> pages bring <N>%.

## The pages that earn

1. / - homepage - <traffic> visits (<share>%) - not rebuilt
2. /service-areas/round-rock-plumbers-contractors/ - city page - <traffic> visits (<share>%), <N> keywords
...

## What they publish
<N> blog posts · <N> city pages · <N> service pages · <N> other

## Rebuild these
1. <url> - <why: traffic, keywords, you don't have it>
2. ...
3. ...

## Page 1 structure: <url>
Title: ...
H1: ...
Sections in order:
- H2 ...
- H2 ...
Proof: ...
Prices: ...
FAQ: <N> questions
Call to action: ...
```

---

## 2-keywords.md

Group by the page that should rank. Each keyword on its own line.

```
# Their keywords - <N> searches both rivals rank for and you don't

Volumes are Semrush estimates for <country>.

## Drain cleaning page (rebuild 1)
drain cleaning - 12,100 a month - them #35, rival #63
drain cleaning austin - 1,600 a month - them #8, rival #29

## Homepage
plumber austin - 3,600 a month - them #4, rival #14

## New page: Cedar Park
plumber cedar park - 1,900 a month - them #24, rival #21
```

---

## 3-citations.md

```
# Their listings - on <N> directories you're not

## Get listed (<N>)

### Angi
Their listing: <url>
Add yours: <url found live>
Free

## Already there (<N>)

## Checked, not theirs
<url> - same name, different phone (Dallas)
```

---


## data.json

Judgments only. Every count, volume, position and traffic number on the dashboard is read from `raw/` and `5-ai/runs/`, never typed here. Shape:

```
{
  "date": "YYYY-MM-DD", "database": "us",
  "you":  {"name", "domain", "phone", "city", "service", "pages": <your sitemap count>, "listings": <directories you're on>},
  "them": {"name", "domain", "phone", "address"},
  "rival2": {"name", "domain"},
  "page_types": {"/blog/": "blog", "/service-areas/": "city", "/plumbing/": "service"},
  "rebuilds": [{"url", "name", "keyword", "file", "gate", "page", "slots"}],
  "keyword_groups": [{"page", "kind", "note", "keywords": [exact keywords from the gap CSV]}],
  "site_preview": "http://localhost:3000",
  "citations": [{"site", "status": "Theirs" | "Check", "detail": "a few words", "add": "add-your-business URL or null"}],
  "citation_notes": ["one line at most"],
  "backlinks": {"win": [{"domain", "what": "a few words"}], "directory": [...], "check": [...], "dead": [...], "skip": {"Group name": [...]}},
  "rivals": [{"name", "domain"}],   up to 4; per-rival files are raw/semrush-top-pages-<domain>.csv and raw/sitemap-<domain>.json
  "ai_question": "the question asked",
  "ai_sources": [{"site", "match": ["domains or source names it covers"], "type", "names_them", "action", "link"}],
  "gbp": {"them": {"name", "rating", "reviews", "categories"}, "you": {"name", "categories"}, "leaders": [{"name", "categories"}], "note"}
}
```

`page_types` maps a URL folder to service, city or blog. Anything unmatched is "other". The homepage is always "homepage".
