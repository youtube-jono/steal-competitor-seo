# Their backlinks - keep the ones you can win

The backlink gap returns every site that links to the rivals and not to you. Most of it is junk. The job is a short list of real links a local business can get, and how the competitor got each one.

## Sort every domain into one of three

**Win it** - a real organisation that would link to the user too:
- Suppliers and manufacturers with a "where to buy" or "find an installer" page
- Trade associations and licensing bodies with member lists
- Chambers of commerce and business improvement areas
- Local sports teams, schools, charities and events (sponsor pages)
- Local news, radio and community sites (stories, best-of lists, sponsor spots)
- Partner businesses in nearby trades: realtors, property managers, renovators, organisers
- Community forums and Q&A where a real answer can carry a link (RedFlagDeals, Reddit, local Facebook groups excluded)

**Directory** - a business listing site. Move it to `3-citations.md`, marked "from their backlinks". Examples: bbb.org, yelp, yellowpages, canadianbusinessdirectory.ca, fyple, marketlister, bestprosintown, mappca, cylex, hotfrog. Media sites often run one too: two "local radio" links turned out to be a radio station's business directory. Check the linking page before calling it a sponsorship.

**Skip** - nothing a real business should chase:
- Site-info and stat scrapers: sitelike, urlm, datagemba, websiteinformer, statshow
- Web directories from the 2000s: odp.org, viesearch, linkcentre, seekon, weboworld
- Article farms and self-publish platforms: articleted, vocal.media (note it, but it is a link anyone can make)
- Odd TLDs and nonsense names: `.top`, `.sbs`, `.cloud`, `.monster`, `.forum` with no real community
- Sites in another language or country with nothing to do with the trade
- Other competitors in the same trade (a link from a rival is not on offer)
- Big platforms where the link is a profile or search result: yahoo.com, google.com, linkedin.com

When unsure, `firecrawl_scrape` the domain's homepage. If it isn't a real organisation with a real audience, skip it.

## For every Win it domain

1. Find the page that links to them: `firecrawl_search` with `site:<domain> <their brand name>`, then `site:<domain> <their domain>`.
2. Scrape it and say how they got the link, in one line: sponsored the team, supplier lists them as an installer, member of the association, a radio ad page, a guest article, a forum answer.
3. Find who to contact: the page's own contact link, then `/contact`, `/about`, `/advertise`, `/sponsorship`. An email address beats a form. Never send anything.

Rank Win it by: links to both rivals first, then by authority score, then by how easy the ask is (sponsor or member beats press).

## File shape

```
## Win it (6)

### <domain> - <what it is>, links to both rivals
How they got it: <one line, read off the linking page>
Their link: <the page that links to them>
Contact: <email or form, and the page it came from>
Authority: <domain_ascore from the gap report>
```
