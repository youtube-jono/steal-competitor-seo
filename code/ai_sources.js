// Paste into the browser's JavaScript tool once an AI answer has finished.
// Works on ChatGPT, Claude, Perplexity and Gemini. Returns the latest answer's
// text and every outside link on the page (tracking tags stripped, the AI's
// own links dropped). Open the sources panel first if the AI hides them.
(() => {
  const OWN = ['chatgpt.com', 'openai.com', 'claude.ai', 'anthropic.com', 'perplexity.ai',
    'gemini.google.com', 'google.com/search', 'accounts.google.com', 'support.google.com',
    'policies.google.com', 'gstatic.com', 'googleusercontent.com'];
  const ANSWER = [
    '[data-message-author-role="assistant"]',   // ChatGPT
    '.font-claude-response, [data-is-streaming]', // Claude
    '[id^="markdown-content"], .prose',          // Perplexity
    'message-content, model-response',           // Gemini
  ];

  let answer = '';
  for (const sel of ANSWER) {
    const nodes = document.querySelectorAll(sel);
    if (nodes.length) { answer = nodes[nodes.length - 1].innerText; break; }
  }
  if (!answer) answer = (document.querySelector('main') || document.body).innerText.slice(-6000);

  const clean = href => {
    try {
      const u = new URL(href);
      [...u.searchParams.keys()].filter(k => k.startsWith('utm_') || k === 'ref' || k === 'srsltid')
        .forEach(k => u.searchParams.delete(k));
      u.hash = '';
      return u.toString().replace(/\?$/, '');
    } catch (e) { return null; }
  };
  const links = [...new Set([...document.querySelectorAll('a[href^="http"]')]
    .map(a => clean(a.href))
    .filter(h => h && !OWN.some(d => h.includes(d))))];

  return {
    engine: location.hostname,
    still_writing: !!document.querySelector('[data-testid="stop-button"], button[aria-label*="Stop"]'),
    answer_length: answer.length,
    answer: answer.slice(0, 4000),
    links,
  };
})()
