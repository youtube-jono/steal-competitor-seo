# Semrush - the four calls

Four calls per competitor. About 4,800 API units in total. Every result is saved to `output/<their-domain>/raw/` straight away, as the CSV Semrush returns. If the file already exists, read it and skip the call.

Each call goes through the Semrush connector first: `get_report_schema` once if you need it, then `execute_report`. Note the `usage.api_units` from each response in `raw/semrush-spend.md`.

If the connector isn't there, or answers `no_api_units` or `no_subscription`, run the same report with the API key instead:

```
python3 code/semrush_fallback.py <report> '<params as JSON>' --out output/<their-domain>/raw/<file>.csv
```

Same report names, same params, same CSV. It reads `SEMRUSH_API_KEY` from `.env`. If neither works, stop and tell the user.

Several competitors? Batch them: one keyword gap and one backlink gap can hold up to 4 rivals plus you, so each extra competitor only adds its own top-pages call (about 200 units).

Want two weeks free? Semrush trial: https://www.semrush.com/partner/jonocatliffseo_7401436/?irclickid=UodwPVRilxyZWxsygXUph16GUkr03ZTt3xLWws0&irgwc=1&afsrc=1

---

## Call 1 - top pages (about 200 units)

What it is in Semrush: Organic Research > Pages.

report: `resource_organic_unique`
params:
- target: their domain
- database: from `inputs.md`
- display_limit: 20
- display_sort: `traffic_desc`

Saves to: `raw/semrush-top-pages.csv`

---

## Call 2 - keyword gap (about 2,400 units)

What it is in Semrush: Keyword Gap, the Missing tab. Keywords every rival ranks for and you don't.

report: `domain_domains`
params:
- database: from `inputs.md`
- domains, in this order:
  - `{"sign": "*", "type": "organic", "domain": "<rival 1>"}`
  - `{"sign": "*", "type": "organic", "domain": "<rival 2>"}`
  - `{"sign": "-", "type": "organic", "domain": "<your domain>"}`
- display_sort: `volume_desc`
- display_limit: 30
- export_columns: `keyword, position_domain_1, position_domain_2, position_domain_3, volume, keyword_difficulty, cpc`

Only one rival? Use just the first and last lines. That gives the Untapped list instead.

Saves to: `raw/semrush-keyword-gap.csv`

This is the most expensive call: 80 units a row. Never raise the limit without asking.

---

## Call 3 - backlink gap (about 1,600 units)

What it is in Semrush: Backlink Gap.

report: `backlinks_matrix`
params:
- targets: `[<rival 1>, <rival 2>, <your domain>]`
- target_types: `["root_domain", "root_domain", "root_domain"]`
- display_sort: `matchesnum_desc` (sites linking to both rivals first)
- display_limit: 40

Saves to: `raw/semrush-backlink-gap.csv`

Expect most rows to be junk. That is normal. `references/backlinks.md` sorts them.

---

## Call 4 - service demand (about 10 units a keyword)

What it is in Semrush: Keyword Overview, in bulk.

report: `phrase_these`
params:
- phrase: every "[service] [city]" for the user's services, separated by semicolons, e.g. `drain cleaning austin;emergency plumber austin;toilet repair austin`
- database: from `inputs.md`
- export_columns: `keyword, volume, intent`

Saves to: `raw/semrush-service-demand.csv`. The top 3 by volume fill the AI questions. The Questions tab is skipped: for local services it returns mostly "how to become a plumber" and 0-volume questions.

---

## What is never called

- No domain overview, no competitor discovery report. Google finds the competitor for free.
- No separate commercial-keywords report. The keyword gap is already their commercial keywords.
- No per-domain backlink lists. Firecrawl search finds the linking page for free.
