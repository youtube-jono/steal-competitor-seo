"""Build the dashboard: one column, one row per item, a column per rival.

Usage:
    python3 code/build_dashboard.py output/<their-domain>
    python3 code/build_dashboard.py output/<their-domain> --stage=1     (writes dashboard-step1.html)

Sections fill in step by step: 1 Semrush (pages, keywords, links), 2 listings and
profile, 3 AI search. Later sections show a placeholder until their prompt has run.
data.json "stage" sets the step; without it the step is guessed from the saved data.

Handles 1 to 4 rivals (data.json "rivals"). Numbers come from raw/ and
5-ai/runs/; judgment calls come from data.json. Per-rival Semrush and sitemap
files are raw/semrush-top-pages-<domain>.csv and raw/sitemap-<domain>.json; the
first rival may use the plain raw/semrush-top-pages.csv and raw/sitemap.json.
Writes dashboard.html in the same folder.
"""

import csv
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlparse

sys.path.insert(0, str(Path(__file__).parent))
from tally_ai import clean_url, domain_of, load_runs  # noqa: E402

SHOW = 5
# Which prompt fills which section. Sections past the current step show a placeholder,
# so the dashboard fills in as viewers work through the prompts.
STEPS = {"pages": 1, "keywords": 1, "links": 1, "gbp": 2, "listings": 2, "ai": 3}
STEP_NAMES = {1: "the Semrush prompt", 2: "the listings and profile prompt", 3: "the AI search prompt"}
ENGINES = {"chatgpt": "ChatGPT", "claude": "Claude", "perplexity": "Perplexity", "gemini": "Gemini"}
# Checked with the dataviz validator on #faf9f5: blue, terracotta, aqua, yellow pass in
# this order with labels and 2px gaps. Rivals take terracotta, aqua, yellow, violet; you are blue.
RIVAL_COLOURS = ["#c96442", "#1baf7a", "#eda100", "#4a3aa7"]
YOU, OTHER = "#2a78d6", "#cfcdc4"
TYPE_COLOURS = {"home": "#2a78d6", "service": "#c96442", "city": "#1baf7a", "blog": "#eda100", "other": "#cfcdc4"}
TYPE_LABELS = {"home": "Homepage", "service": "Service", "city": "City", "blog": "Blog", "other": "Other"}
STAR = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M12 2 L13.4 10.6 L22 12 L13.4 13.4 L12 22 L10.6 13.4 L2 12 L10.6 10.6 Z"/></svg>'


def e(value):
    return html.escape(str(value), quote=True)


def num(value):
    return f"{float(value):,.0f}"


def read_csv(path):
    if not path.is_file():
        return [], []
    rows = list(csv.reader(path.open(), delimiter=";"))
    return (rows[0], rows[1:]) if rows else ([], [])


def short(domain):
    return domain.removeprefix("www.").split(".")[0]


UTILITY = ("about", "contact", "career", "privacy", "terms", "review", "testimonial", "faq", "gallery", "book", "thank", "coupon", "financing", "employment", "sitemap", "cart", "login")
QUESTION_STARTS = ("how-", "what-", "why-", "when-", "can-", "is-", "are-", "do-", "does-", "should-", "best-", "types-", "guide", "tips-", "signs-", "understanding-")


def page_type(url, types):
    """data.json page_types folders first, then a guess any plumber's site fits."""
    path = urlparse(url).path or "/"
    if path == "/":
        return "home"
    for prefix, kind in types.items():
        if path.rstrip("/") == prefix.rstrip("/"):
            return "other"
        if path.startswith(prefix):
            return kind
    slug = path.strip("/").split("/")[-1].lower()
    full = path.lower()
    if any(w in full for w in ("/blog", "/news", "/article", "/post")) or slug.startswith(QUESTION_STARTS) or "-vs-" in slug:
        return "blog"
    if any(w in full for w in ("service-area", "/areas", "/locations", "/location/")) or re.match(r"(plumbers?|plumbing)-[a-z-]+$", slug) or re.search(r"-(plumbers?|plumbing)$", slug):
        return "city"
    if any(w in slug for w in UTILITY) or not slug:
        return "other"
    return "service"


# ---------- marks ----------

def bar(value, top, colour, tip=""):
    width = 0 if not top or not value else max(2.0, 100 * float(value) / float(top))
    return f'<span class="bar" title="{e(tip)}"><i style="width:{width:.1f}%;background:{colour}"></i></span>'


def stack(parts, unit=""):
    total = sum(v for _, v, _ in parts) or 1
    return '<span class="stack">' + "".join(
        f'<i style="width:{100 * v / total:.2f}%;background:{c}" title="{e(l)}: {v:,.0f}{unit}"></i>' for l, v, c in parts if v) + "</span>"


def legend(items):
    return '<div class="legend">' + "".join(f'<span><b style="background:{c}"></b>{e(l)}</span>' for l, c in items) + "</div>"


def dot(colour, on=True, tip=""):
    return f'<i class="dot{"" if on else " off"}" style="{f"background:{colour}" if on else ""}" title="{e(tip)}"></i>'


EXT_ICON = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>'


def ext(url, label=""):
    """Text plus a small open-in-new-tab icon. No url, no icon."""
    if not url:
        return label
    return f'{label}<a class="ext" href="{e(url)}" target="_blank" rel="noreferrer" title="Open {e(url)}">{EXT_ICON}</a>'


def action_link(text, link, subject=""):
    """One click: an email opens the user's mail app with a subject filled in, a form opens in a new tab."""
    if not link:
        return f"<i>{e(text)}</i>"
    if link.startswith("mailto:"):
        href = link + (f"?subject={subject}" if subject else "")
        return f'<a href="{e(href)}" title="{e(link[7:])}">{e(text)} · {e(link[7:])}</a>'
    return f'<a href="{e(link)}" target="_blank" rel="noreferrer">{e(text)}</a>'


def more(rows, show=SHOW):
    if len(rows) <= show:
        return "".join(rows)
    return "".join(rows[:show]) + f'<details><summary>Show all {len(rows)}</summary>{"".join(rows[show:])}</details>'


def section(title, count, body, foot="", head=""):
    count_html = f'<span class="n">{e(count)}</span>' if count != "" else ""
    foot_html = f'<div class="foot">{foot}</div>' if foot else ""
    return f'<section class="card"><h2>{e(title)}{count_html}</h2>{head}{body}{foot_html}</section>'


def placeholder(title, step):
    return (f'<section class="card wait"><h2>{e(title)}<span class="n">step {step}</span></h2>'
            f'<p>Fills in when you run {e(STEP_NAMES[step])}.</p></section>')


def current_step(data, runs):
    """data.json "stage" wins; otherwise guess from what has been saved."""
    if "stage" in data:
        return int(data["stage"])
    if runs:
        return 3
    if data.get("citations") and data.get("gbp"):
        return 2
    return 1


def row(cells, cols):
    return f'<div class="r" style="grid-template-columns:{cols}">' + "".join(f"<span>{c}</span>" for c in cells) + "</div>"


# ---------- data ----------

def rival_files(raw, rivals):
    out = []
    for i, rv in enumerate(rivals):
        d = rv["domain"]
        pages_file = raw / f"semrush-top-pages-{d}.csv"
        site_file = raw / f"sitemap-{d}.json"
        if i == 0 and not pages_file.is_file():
            pages_file = raw / "semrush-top-pages.csv"
        if i == 0 and not site_file.is_file():
            site_file = raw / "sitemap.json"
        pages = read_csv(pages_file)[1]
        sitemap = json.loads(site_file.read_text()) if site_file.is_file() else {"pages": []}
        out.append({**rv, "colour": RIVAL_COLOURS[i % len(RIVAL_COLOURS)], "pages": pages, "sitemap": sitemap["pages"]})
    return out


# ---------- sections ----------

RAW = {}


def raw_dir_sitemap(data):
    f = RAW.get("dir")
    if not f:
        return None
    path = f / f'sitemap-{data["you"]["domain"]}.json'
    return json.loads(path.read_text())["pages"] if path.is_file() else None


def strip(data, rivals, gap, runs, step=3):
    you = data["you"]
    named = sum(1 for r in runs if any(any(rv["name"].lower() in n.lower() for rv in rivals) for n in r.get("named", [])))
    cells = [
        (f'{min(len(rv["sitemap"]) for rv in rivals)}-{max(len(rv["sitemap"]) for rv in rivals)} <small>vs {you.get("pages", 0)}</small>' if len(rivals) > 1 else f'{len(rivals[0]["sitemap"])} <small>vs {you.get("pages", 0)}</small>', "Pages, rivals vs you"),
        (len(top20_keywords(RAW["dir"], rivals)) or len(gap[1]), "Keywords they rank top 20 for"),
        (f'{sum(1 for c in data["citations"] if c.get("tier") != "skip")} <small>vs {you.get("listings", 0)}</small>' if step >= 2 else "-", "Listings worth getting vs yours"),
        (len(data["backlinks"]["win"]), "Links to win"),
        (f"{named}/{len(runs)} <small>vs {sum(1 for r in runs if r.get('you_named'))}</small>" if runs and step >= 3 else "-", "AI answers naming rivals vs you"),
    ]
    rivals_line = "".join(f'<span><b style="background:{rv["colour"]}"></b>{ext("https://" + rv["domain"], e(rv["name"]))}</span>' for rv in rivals) + f'<span><b style="background:{YOU}"></b>{e(you["name"])}</span>'
    return ('<div class="strip">' + "".join(f'<div><div class="v">{v}</div><div class="k">{e(k)}</div></div>' for v, k in cells) + "</div>"
            + f'<div class="legend top">{rivals_line}</div>')


def traffic_section(data, rivals):
    types = data.get("page_types", {})
    order = ["home", "service", "city", "blog", "other"]
    rows = []
    blog_note = ""
    for rv in rivals:
        publish = Counter(page_type(p["url"], types) for p in rv["sitemap"])
        share = Counter()
        for r in rv["pages"]:
            share[page_type(r[0], types)] += float(r[3])
        rows.append(row([e(rv["name"]), stack([(TYPE_LABELS[t], publish[t], TYPE_COLOURS[t]) for t in order], " pages"),
                         stack([(TYPE_LABELS[t], share[t], TYPE_COLOURS[t]) for t in order], "%")], "170px 1fr 1fr"))
        if not blog_note and publish["blog"]:
            blog_note = f'{rv["name"]}: {publish["blog"]} blog posts bring {share["blog"]:.0f}% of the traffic.'
    you_site = raw_dir_sitemap(data)
    if you_site is not None:
        mine = Counter(page_type(p["url"], types) for p in you_site)
        rows.append(row([f'<strong>{e(data["you"]["name"])}</strong>', stack([(TYPE_LABELS[t], mine[t] or (1 if t == "home" and you_site else 0), TYPE_COLOURS[t]) for t in order], " pages"),
                         f'<i>{len(you_site)} pages, no ranking traffic yet</i>'], "170px 1fr 1fr"))
    head = row(["", "<em>What they publish</em>", "<em>Where the traffic lands (Semrush est.)</em>"], "170px 1fr 1fr")
    return section("Pages vs traffic", "", head + "".join(rows), blog_note,
                   legend([(TYPE_LABELS[t], TYPE_COLOURS[t]) for t in order]))


def pages_section(data, rivals):
    types = data.get("page_types", {})
    floors = {"service": float(data.get("min_service_visits", 0)), "blog": float(data.get("min_blog_visits", 0))}
    keep = [(rv, r) for rv in rivals for r in rv["pages"]
            if page_type(r[0], types) in floors and float(r[2]) >= floors[page_type(r[0], types)]]
    keep.sort(key=lambda x: -float(x[1][2]))
    top = max((float(r[2]) for _, r in keep), default=1)
    multi = len(rivals) > 1
    cols = "1fr 70px 160px 50px 50px" if multi else "1fr 70px 160px 50px 50px"
    rows = [row([ext(r[0], e(urlparse(r[0]).path)), f'<em>{TYPE_LABELS[page_type(r[0], types)].lower()}</em>',
                 bar(r[2], top, rv["colour"], f'{rv["name"]}: {num(r[2])} visits a month'), num(r[2]), f"{e(r[1])} kw"], cols)
            for rv, r in keep]
    insight = ""
    for rv in rivals:
        blogs = sum(1 for p in rv["sitemap"] if page_type(p["url"], types) == "blog")
        home = sum(float(r[3]) for r in rv["pages"] if page_type(r[0], types) == "home")
        if blogs:
            insight = f' {rv["name"]}: {blogs} blog posts; the homepage alone brings {home:.0f}% of their traffic.'
            break
    return section("Their top service + blog pages", f'{len(keep)} · service {floors["service"]:.0f}+, blog {floors["blog"]:.0f}+ visits/mo', more(rows), f"Visits a month, Semrush estimate. Bar colour = rival.{e(insight)}")


INTENT = {"0": "C", "1": "I", "2": "N", "3": "T"}
INTENT_TIP = {"C": "Commercial: comparing options", "I": "Informational: wants an answer", "N": "Navigational: looking for a brand", "T": "Transactional: ready to hire"}


def top20_keywords(raw, rivals):
    """Keywords any rival ranks top 20 for (raw/semrush-top20-<domain>.csv), merged, brand searches dropped."""
    merged = {}
    brands = [w for rv in rivals for w in re.findall(r"[a-z]{4,}", rv["name"].lower()) if w not in ("plumbing", "plumber", "drains", "service")]
    brands += ["roto", "rooter", "mr rooter"]
    for rv in rivals:
        head, rows = read_csv(raw / f'semrush-top20-{rv["domain"]}.csv')
        for r in rows:
            kw, pos, vol, url, intents = r[0], int(r[1]), int(r[2]), r[3], r[4]
            if any(b in kw for b in brands) or intents.strip() == "2":
                continue
            item = merged.setdefault(kw, {"vol": vol, "intent": set(), "pos": {}, "url": {}})
            item["intent"] |= {INTENT[i] for i in intents.split(",") if i in INTENT}
            if pos < item["pos"].get(rv["domain"], 999):
                item["pos"][rv["domain"]], item["url"][rv["domain"]] = pos, url
    return sorted(merged.items(), key=lambda kv: -kv[1]["vol"])


def keywords_section(data, rivals, gap):
    raw = RAW["dir"]
    items = top20_keywords(raw, rivals)
    if not items:
        return ""
    top = max(v["vol"] for _, v in items)
    cols = "1fr 52px 110px 56px " + " ".join("40px" for _ in rivals) + " 36px"
    head = row(["", "<em>intent</em>", "", "<em>vol</em>"] + [f'<em title="{e(rv["name"])}">{e(short(rv["domain"])[:2])}</em>' for rv in rivals] + ["<em>you</em>"], cols)
    rows = []
    for kw, v in items:
        tags = "".join(f'<b class="it it-{t}" title="{e(INTENT_TIP[t])}">{t}</b>' for t in sorted(v["intent"], key="CTIN".index))
        positions = []
        for rv in rivals:
            pos = v["pos"].get(rv["domain"])
            positions.append(f'<a href="{e(v["url"][rv["domain"]])}" target="_blank" rel="noreferrer" style="color:{rv["colour"]}" title="Their ranking page">#{pos}</a>' if pos else "<i>-</i>")
        rows.append(row([ext("https://www.google.com/search?q=" + kw.replace(" ", "+") + "&gl=ca", e(kw)), tags,
                         bar(v["vol"], top, rivals[0]["colour"], f'{v["vol"]:,} searches a month'), f'{v["vol"]:,}'] + positions + ["<i>-</i>"], cols))
    counts = Counter(t for _, v in items for t in v["intent"])
    foot = (f'Searches a month. Only keywords a rival ranks top 20 for; brand searches dropped. Click a position to open their ranking page. '
            f'C commercial {counts["C"]} · T transactional {counts["T"]} · I informational {counts["I"]}')
    return section("Keywords they rank top 20 for, you don't", len(items), head + more(rows, 10), foot)


def listings_section(data, rivals):
    cols = "1fr " + " ".join("16px" for _ in rivals) + " 16px 70px 220px"
    head_row = row([""] + [f'<em title="{e(rv["name"])}">{e(short(rv["domain"])[:2])}</em>' for rv in rivals] + ["<em>you</em>", "", ""], cols)
    rows = []
    rank = {"core": 0, "worth": 1, "skip": 2}
    for c in sorted(data["citations"], key=lambda c: (rank.get(c.get("tier", "worth"), 1), -len(c.get("rivals", [rivals[0]["domain"]])))):
        on = set(c.get("rivals", [rivals[0]["domain"]]))
        marks = [dot(rv["colour"], rv["domain"] in on, rv["name"]) for rv in rivals]
        tier = c.get("tier", "worth")
        tag = {"core": '<b class="ok">core</b>', "worth": '<b class="mid">worth it</b>', "skip": '<b class="chk">skip</b>'}[tier]
        link = (f'<a href="{e(c["add"])}" target="_blank" rel="noreferrer">Add</a>' if c.get("add")
                else f'<i title="{e(c.get("note", ""))}">{e(c.get("note", "no form"))}</i>')
        rows.append(row([ext(c.get("url"), e(c["site"]))] + marks + [dot(YOU, False, "you")] + [tag, link], cols))
    notes = " ".join(e(n) for n in data.get("citation_notes", []))
    keep = sum(1 for c in data["citations"] if c.get("tier") != "skip")
    return section("Listings to get", f'{keep} worth it · you have {data["you"].get("listings", 0)}', head_row + more(rows, keep), notes)


def links_section(data, rivals, links):
    head, rows_ = links
    lookup = {r[0]: r for r in rows_}
    bl = data["backlinks"]
    junk = sum(len(v) for v in bl["skip"].values()) + len(bl.get("dead", []))
    funnel = (row(["", stack([("Win", len(bl["win"]), "#c96442"), ("Directories", len(bl["directory"]), "#2a78d6"),
                              ("Unclear", len(bl["check"]), "#eda100"), ("Junk or dead", junk, OTHER)])], "1fr")
              + legend([(f'Win {len(bl["win"])}', "#c96442"), (f'Directories {len(bl["directory"])}', "#2a78d6"),
                        (f'Unclear {len(bl["check"])}', "#eda100"), (f"Junk or dead {junk}", OTHER)]))
    rows = []
    cols = "170px 1fr " + " ".join("16px" for _ in rivals) + " 50px 320px"
    for w in bl["win"]:
        found = lookup.get(w["domain"])
        on = set(w.get("rivals", []))
        if found and not on:
            on = {h for h, v in zip(head[4:], found[4:]) if v not in ("", "0")}
        auth = found[1] if found else None
        rows.append(row([ext(w.get("url") or "https://" + w["domain"], e(w["domain"])), e(w["what"])] + [dot(rv["colour"], rv["domain"] in on, rv["name"]) for rv in rivals] + [f"AS {e(auth)}" if auth else "", action_link(w.get("action", ""), w.get("link"), quote(f'{data["you"].get("city", "")} {data["you"].get("service", "")}'.strip()))], cols))
    return section("Links to win", len(bl["win"]), funnel + "".join(rows), (f'Top {len(rows_)} of about {sum(v for k, v in data.get("backlink_totals", {}).items() if k != data["you"]["domain"]):,} sites linking to the rivals, sorted by authority' if data.get("backlink_totals") else f"{len(rows_)} sites link to the rivals and not to you"))


def gbp_section(data, rivals):
    g = data.get("gbp")
    if not g:
        return ""
    by_domain = {x["domain"]: x for x in g.get("rivals", [])}
    have = [(rv, by_domain[rv["domain"]]) for rv in rivals if rv["domain"] in by_domain]
    mine = set(g["you"]["categories"])
    usage = Counter(c for _, x in have for c in x["categories"])
    cols = "1fr " + " ".join("22px" for _ in have) + " 22px 60px"
    head = row(["<em>Category</em>"] + [f'<em title="{e(rv["name"])}">{e(short(rv["domain"])[:2])}</em>' for rv, _ in have] + ["<em>you</em>", "<em>used by</em>"], cols)
    rows = [row([e(cat)] + [dot(rv["colour"], cat in x["categories"], rv["name"]) for rv, x in have] + [dot(YOU, cat in mine, "you"), f"{n} of {len(have)}"], cols)
            for cat, n in sorted(usage.items(), key=lambda kv: (-kv[1], kv[0]))]
    reviews = " · ".join(f'{rv["name"]} {x["rating"]}★ ({x["reviews"]})' for rv, x in have)
    return section("Google Business Profile categories", "most used first", head + more(rows, 6), f'Reviews: {e(reviews)}. {e(g.get("note", ""))}')


def ai_section(data, rivals, runs):
    if not runs:
        return section("What AI says", "not run yet", "", "")
    named = Counter()
    for r in runs:
        for n in {x.strip() for x in r.get("named", [])}:
            named[n] += 1
    names_rows = []
    for n, k in named.most_common(6):
        is_rival = next((rv for rv in rivals if rv["name"].lower() in n.lower()), None)
        names_rows.append(row([e(n), bar(k, len(runs), is_rival["colour"] if is_rival else OTHER, f"named in {k} of {len(runs)} chats"), f"{k}/{len(runs)}"], "260px 1fr 44px"))
    for rv in rivals:
        if not any(rv["name"].lower() in n.lower() for n in named):
            names_rows.insert(0, row([f'<strong>{e(rv["name"])}</strong>', bar(0, 1, rv["colour"]), f"0/{len(runs)}"], "260px 1fr 44px"))
    # sources: count chats per catalogued source
    def chats_for(match):
        c = 0
        for r in runs:
            pool = {domain_of(clean_url(u)) for u in r.get("sources", []) if clean_url(u)} | {n.strip() for n in r.get("source_notes", [])}
            if any(m in pool or any(m in p for p in pool) for m in match):
                c += 1
        return c
    catalogue = data.get("ai_sources", [])
    scored = sorted(((chats_for(s["match"]), s) for s in catalogue), key=lambda x: -x[0])
    top = max((c for c, _ in scored), default=1)
    src_rows = []
    for c, s in scored:
        action = action_link(s["action"], s.get("link"), "Adding%20us%20to%20your%20list")
        flag = ' <b class="ok">names them</b>' if s.get("names_them") else ""
        src_rows.append(row([ext(s.get("url"), e(s["site"])) + flag, f'<em>{e(s["type"])}</em>', bar(c, top, "#5e5d59", f"cited in {c} of {len(runs)} chats"), f"{c}", action], "220px 120px 80px 24px 1fr"))
    q = f'"{e(data.get("ai_question", ""))}" · ' if data.get("ai_question") else ""
    body = ('<div class="sub">Who the AIs recommend</div>' + "".join(names_rows)
            + '<div class="sub">What they cite, and what to do</div>' + more(src_rows, 14))
    per = Counter(r["engine"] for r in runs)
    return section("What AI says", f'{len(runs)} chats', body, f'{q}{", ".join(f"{ENGINES.get(k, k)} {v}" for k, v in sorted(per.items()))}')


STAGE_OVERRIDE = {}

CSS = """
* { box-sizing:border-box; margin:0; padding:0; }
:root { --canvas:#f5f4ed; --ivory:#faf9f5; --sand:#e8e6dc; --ink:#141413; --body:#5e5d59; --muted:#87867f; --hair:#ece9df;
  --terra:#c96442; --coral:#d97757; --good:#3d7a4a; --good-bg:rgba(61,122,74,.09); --warn:#9a7410; --warn-bg:rgba(212,160,23,.12); }
body { background:var(--canvas); color:var(--ink); font:13px/1.4 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif; -webkit-font-smoothing:antialiased; }
.n, em, small, .strip .k, summary, .foot, .sub, .meta { font-family:"JetBrains Mono",ui-monospace,Menlo,monospace; }
.wrap { max-width:1000px; margin:0 auto; padding:20px 24px 32px; }
header { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:12px; }
header .mark { color:var(--terra); align-self:center; }
header h1 { font:500 26px/1.1 "Tiempos Text",Georgia,serif; letter-spacing:-.4px; }
.meta { color:var(--muted); font-size:12px; }
.strip { display:grid; grid-template-columns:repeat(5,1fr); background:var(--ivory); border:1px solid var(--hair); border-radius:12px; }
.strip > div { padding:10px 14px; border-right:1px solid var(--hair); } .strip > div:last-child { border-right:0; }
.strip .v { font:500 21px/1.1 "Tiempos Text",Georgia,serif; } .strip .v small { font-size:12px; color:var(--muted); }
.strip .k { font-size:9.5px; text-transform:uppercase; letter-spacing:1.1px; color:#6e6d66; margin-top:3px; }
.card { background:var(--ivory); border:1px solid var(--hair); border-radius:12px; padding:12px 16px; margin-top:12px; }
.card h2 { font:500 15px/1.2 "Tiempos Text",Georgia,serif; display:flex; align-items:baseline; gap:8px; margin-bottom:6px; }
.n { font-size:10.5px; color:var(--coral); text-transform:uppercase; letter-spacing:1px; }
.r { display:grid; gap:12px; align-items:center; padding:4px 0; border-top:1px solid var(--hair); min-height:26px; }
.r > span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; min-width:0; }
.r > span:nth-child(n+3) { text-align:right; }
em { font-style:normal; font-size:10px; color:var(--muted); } small { font-size:10.5px; color:var(--muted); }
a { color:var(--terra); text-decoration:none; font-weight:500; } a:hover { text-decoration:underline; }
a.ext { display:inline-flex; vertical-align:-1px; margin-left:6px; color:var(--muted); padding:2px; border-radius:4px; }
a.ext:hover { color:var(--terra); background:var(--sand); text-decoration:none; }
i { font-style:normal; color:var(--muted); font-size:11px; }
b { font-weight:500; font-size:10px; text-transform:uppercase; letter-spacing:.6px; padding:1px 6px; border-radius:99px; }
b.it { padding:1px 5px; margin-right:2px; font-size:9.5px; } .it-C { color:#9a4a2e; background:rgba(201,100,66,.12); } .it-T { color:#2a5ea8; background:rgba(42,120,214,.12); } .it-I { color:#6e6d66; background:var(--sand); } .it-N { color:#6e6d66; background:var(--sand); }
b.ok { color:var(--good); background:var(--good-bg); } b.mid { color:#2a5ea8; background:rgba(42,120,214,.09); } b.chk { color:var(--warn); background:var(--warn-bg); }
.bar { display:block; height:8px; background:var(--sand); border-radius:4px; overflow:hidden; } .bar i { display:block; height:100%; border-radius:4px; }
.stack { display:flex; gap:2px; height:12px; border-radius:4px; overflow:hidden; } .stack i { display:block; height:100%; }
.legend { display:flex; flex-wrap:wrap; gap:3px 14px; font-size:11.5px; color:var(--body); margin:2px 0 6px; }
.legend b { display:inline-block; width:9px; height:9px; border-radius:2px; margin-right:5px; padding:0; vertical-align:-1px; }
.legend.top { margin:8px 2px 0; }
.dot { display:block; width:11px; height:11px; border-radius:50%; margin-left:auto; } .dot.off { border:1.5px dashed var(--muted); }
.chip { display:inline-block; margin:1px 4px 1px 0; padding:1px 7px; border:1px solid var(--hair); border-radius:99px; background:#fff; color:var(--body); }
details summary { cursor:pointer; font-size:10.5px; color:var(--terra); padding:5px 0 1px; list-style:none; }
details summary::before { content:"+ "; } details[open] summary::before { content:"- "; }
.foot { font-size:10.5px; color:var(--muted); margin-top:6px; }
.sub { font-size:10px; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin:8px 0 2px; }
.files { margin-top:12px; font-size:12px; }
.card.wait { border-style:dashed; background:transparent; } .card.wait p { color:var(--muted); font-size:12.5px; } .files a { margin-right:14px; }
@media (max-width:760px) { .strip { grid-template-columns:repeat(2,1fr); } .wrap { padding:16px; }
  .r { grid-template-columns:1fr auto !important; } .r > span:nth-child(n+3):not(:last-child) { display:none; } }
"""


def build(folder):
    data = json.loads((folder / "data.json").read_text())
    raw = folder / "raw"
    RAW["dir"] = raw
    rivals = rival_files(raw, data.get("rivals") or [data["them"]])
    gap = read_csv(raw / "semrush-keyword-gap.csv")
    links = read_csv(raw / "semrush-backlink-gap.csv")
    runs = load_runs(folder / "5-ai" / "runs")[0] if (folder / "5-ai" / "runs").is_dir() else []
    you = data["you"]
    files = [f for f in ("compare.html", "listings-pack.md", "outreach.md") if (folder / f).is_file()]
    if (STAGE_OVERRIDE.get("step") or current_step(data, runs)) < 3:
        files = [f for f in files if f == "compare.html"]
    files_html = '<div class="files">' + "".join(f'<a href="{e(f)}" target="_blank" rel="noreferrer">{e(f)}</a>' for f in files) + "</div>" if files else ""
    names = " · ".join(rv["name"] for rv in rivals)
    step = STAGE_OVERRIDE.get("step") or current_step(data, runs)
    plan = [("pages", "Their top service + blog pages", lambda: pages_section(data, rivals)),
            ("keywords", "Keywords they rank top 20 for, you don't", lambda: keywords_section(data, rivals, gap)),
            ("links", "Links to win", lambda: links_section(data, rivals, links)),
            ("gbp", "Google Business Profile categories", lambda: gbp_section(data, rivals)),
            ("listings", "Listings to get", lambda: listings_section(data, rivals)),
            ("ai", "What AI says", lambda: ai_section(data, rivals, runs))]
    parts = [make() if STEPS[key] <= step else placeholder(title, STEPS[key]) for key, title, make in plan]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Steal {e(names)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="wrap">
<header><span class="mark">{STAR}</span><h1>{e(names)} <span style="color:var(--muted)">vs</span> {e(you["name"])}</h1>
<span class="meta">{e(you.get("city", ""))} · {e(data["date"])}</span></header>
{strip(data, rivals, gap, runs, step)}
{"".join(p for p in parts if p)}
{files_html}
</div></body></html>"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--stage")]
    for a in sys.argv[1:]:
        if a.startswith("--stage="):
            STAGE_OVERRIDE["step"] = int(a.split("=", 1)[1])
    if len(args) != 1:
        print(__doc__)
        return 2
    folder = Path(args[0])
    if not (folder / "data.json").is_file():
        print(f"No data.json in {folder}. /steal writes it at the end of each part.")
        return 1
    out = folder / (f'dashboard-step{STAGE_OVERRIDE["step"]}.html' if STAGE_OVERRIDE.get("step") else "dashboard.html")
    out.write_text(build(folder))
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
