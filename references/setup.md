# Setup - three connections, once

## 1. Semrush (parts 1, 2, 4 and the questions in 5)

claude.ai > Settings > Connectors > Semrush > Connect, and sign in to your Semrush account.

Backup: copy `.env.example` to `.env` and paste your Semrush API key (Semrush > Subscription info > API units). `/steal` uses the connector first and switches to the key only if the connector is out of units or not connected.

Every call spends Semrush API units from your account. `/steal` makes four calls per competitor, about 4,800 units, and saves every result so it never pays twice.

No Semrush yet? Two weeks free: https://www.semrush.com/partner/jonocatliffseo_7401436/?irclickid=UodwPVRilxyZWxsygXUph16GUkr03ZTt3xLWws0&irgwc=1&afsrc=1

## 2. Firecrawl (reads pages, including ones behind bot checks)

1. Make a free account at firecrawl.dev and copy your API key (starts `fc-`).
2. In a terminal, in this folder:

```
claude mcp add firecrawl -e FIRECRAWL_API_KEY=fc-YOUR-KEY -- npx -y firecrawl-mcp
```

3. Restart Claude Code. `/mcp` should list `firecrawl` as connected.

A full run reads roughly 60 to 100 pages, one credit each.

## 3. Claude in Chrome (Google searches and the four AIs)

1. Install the extension: https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn
2. Open the Claude side panel in Chrome and sign in with the same account as Claude Code.
3. In that Chrome, log in to ChatGPT, Claude, Perplexity and Gemini. Free accounts work. Paid accounts hit fewer limits on a 120-chat run.

`/steal` drives your real browser, so you can watch it work. Leave the tab alone while it runs. If Google shows a captcha, solve it yourself and tell Claude to carry on.
