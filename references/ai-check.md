# What AI says - ask like a buyer, steal the sources

When a buyer asks ChatGPT "who's the best plumber in Austin?", the answer names a few businesses and cites a few pages. Those pages are where the AI learned who to recommend. Get onto them and you get into the answer.

## The questions - discovery only

This part steals the sources the AIs use to pick a business, so every question is a discovery question: someone who doesn't know a business yet, asking who to hire. Trust, brand and named-competitor questions are brand-building, not stealing, and stay out.

It's a grid: the user's top services times their places, with two modifiers.

- **Services:** ranked by "[service] [city]" searches in one Semrush batch lookup (`phrase_these`). Keep every one with 50+ searches a month, top 3 first. The rivals' keywords (already pulled) are a check for services the user forgot.
- **Places:** the city, then the neighbourhoods with search volume (from the keyword list).

For each service and place:
1. Who's the best [service] in [place]?
2. How much does [service] cost in [place]?
3. Who can I call for an emergency [service] in [place] right now? Only for trades with emergency searches (plumbers, locksmiths, HVAC), not landscaping.

"Best" covers reviews and ratings too: the AIs rank "best" by stars and review counts, so a reviews question returns the same sources. Keep questions short: the keyword plus one modifier. The modifier changes the sources; extra wording doesn't.

Stop when it saturates: run a batch, then a new batch of other services, places or phrasings. When a batch turns up no new sources, stop. That usually happens fast.

Write `5-ai/questions.md` and show it before the run starts.

## The run

Start with ONE question: the biggest buyer question (usually "Who's the best [service] in [city]?"), 4 AIs x 3 chats = 12 chats, about 5 minutes. Run all 10 only when the user asks.


Every question, in all four, 3 times each, a fresh chat every time. 10 questions x 4 AIs x 3 runs = 120 chats. AI answers change from chat to chat, so one run proves nothing. Three shows what keeps coming back.

All in Claude in Chrome, the user's own logged-in browser. Run the four AIs at the same time: one tab each, send the question in all four, wait once (about 30 seconds), then collect from each tab. Use a private or temporary chat where the AI offers one, so memory and past chats don't bend the answer.

- **ChatGPT:** open `https://chatgpt.com/?temporary-chat=true`, type the question, send. Its sources are small citation pills, not links. Click a pill, then click each source in the popover: it opens in a new tab, so read that tab's address and close it. Place cards with photos and addresses come from Google Maps: note "Google Maps listings".
- **Claude:** open `https://claude.ai/new`, check web search is on in the tools menu, type, send. For "best plumber" questions it often answers from Google Maps ("Found 9 places"): note "Google Maps listings".
- **Perplexity:** open `https://www.perplexity.ai/search?q=<the question, URL-encoded>`. It runs on load, even logged out (the answer sits behind the sign-up box). Its sources are normal links.
- **Gemini:** open `https://gemini.google.com/app`, start a temporary chat if the menu offers one, type, send.

Wait until the answer stops growing (the stop button is gone, or the text length is the same two checks running). Then:

1. Open the sources panel if the AI hides sources behind a button (ChatGPT "Sources", Perplexity "Sources" tab, Gemini "Sources and related content").
2. Paste `code/ai_sources.js` into the JavaScript tool. It returns the answer text and every outside link on the page.
3. Read the answer. List every business it names, in the order named.
4. Save the run straight away as `5-ai/runs/<engine>-q<NN>-r<N>.json`:

```
{
  "engine": "chatgpt",
  "question_id": "01",
  "question": "Who's the best plumber in Austin?",
  "run": 1,
  "date": "2026-10-23",
  "named": ["Acme Plumbing", "Blue Water Plumbing", "Mr. Rooter"],
  "competitor_named": true,
  "you_named": false,
  "sources": ["https://www.homestars.com/...", "https://www.reddit.com/r/Austin/..."],
  "source_notes": ["Google Maps listings", "Site name - page title, when no address was available"],
  "answer_excerpt": "first 400 characters of the answer"
}
```

Before each chat, check whether its file already exists. If it does, skip it. A stopped run picks up where it left off.

If an AI asks the user to log in, hits a usage limit or shows a captcha, stop that AI, say which one, and carry on with the others.

## The tally

```
python3 code/tally_ai.py output/<their-domain>
```

It prints and saves `5-ai/tally.md`: how often each business is named by each AI, and every cited domain with how many chats cited it and which AIs. Domains the user already has (their own site, listings found in Part 3) are marked.

## Checking each source

Take every cited page the user is not on, most-cited first. Up to 40 pages. For each one, `firecrawl_scrape` it and answer:

- **Is the competitor named on it?** Search the page for their name, domain and phone. Say yes or no, and quote the line if yes. A source that doesn't name them still matters, but less.
- **Is the user named on it?** Same check.
- **What kind of page is it?**
  - Best-of list ("10 best plumbers in Austin") - ask to be added
  - Directory or review site - goes to the citations list
  - News or magazine story - pitch the writer
  - Blog that takes guest posts - pitch an article
  - Forum or Reddit thread - nothing to send. The user can answer real questions there as themselves, never as a fake customer.
  - A competitor's own site - nothing to get. Note which page AI quotes.
- **Who to contact and how.** Fastest route: `firecrawl_search` `"<domain> contact email"` (snippets often show the address), then `firecrawl_scrape` the contact page with the `query` format asking for the exact email or form URL. Put it in `data.json` as `link` (`mailto:` for an email) so the dashboard turns it into one click. In this order: the author's byline email, the page's contact link, `/contact`, `/about`, `/advertise`. For guest posts, `firecrawl_search` with `site:<domain> "write for us" OR "guest post" OR "contribute"`. Keep the exact email or form URL and where it was found. Never guess an address and never send anything.

## File shape - 5-ai/sources.md

Every number comes from `5-ai/tally.md`. Never round up, never fill a gap.

```
# What AI says about <service> in <city>

<N> chats. <Competitor> named in <N> (<N>%). <You> named in <N>.

ChatGPT names <Competitor> in <N> of 30. Claude <N> of 30. Perplexity <N> of 30. Gemini <N> of 30.

## Get on these (<N>)

### <domain/path> - directory, cited in <N> chats (<which AIs>)
Names <Competitor>: yes - "<the line that names them>"
How to get on it: <add-your-business page>

### <domain/path> - best-of list, cited in <N> chats (<which AIs>)
Names <Competitor>: yes - listed <position>
Contact: <email or form, and where it was found>
Ask: to be reviewed for the next update

## Already there (<N>)

## Nothing to send (<N>)
<domain/path> - forum thread, cited in <N> chats. Answer real questions there as yourself.
```
