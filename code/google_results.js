// Paste into the browser's JavaScript tool on a Google results page.
// Returns every organic result on the page: title, site, link, snippet,
// plus whether Google is showing a captcha and whether a next page exists.
(() => {
  const results = [...document.querySelectorAll('a h3')].map(h => {
    const a = h.closest('a');
    const box = a.closest('[data-hveid], .g, .MjjYud') || a.parentElement;
    const cite = box.querySelector('cite');
    let link = a.href;
    try {
      const u = new URL(link);
      const target = u.searchParams.get('url') || u.searchParams.get('q');
      if (u.hostname.includes('google') && target && target.startsWith('http')) link = target;
    } catch (e) {}
    const site = cite ? cite.innerText.split(' › ')[0].trim() : '';
    const snippet = (box.querySelector('[data-sncf], .VwiC3b') || {}).innerText || '';
    return { title: h.innerText.trim(), site, link, snippet: snippet.slice(0, 240) };
  });
  return {
    captcha: location.pathname.startsWith('/sorry') || !!document.querySelector('#captcha-form, iframe[src*="recaptcha"]'),
    next: !!document.querySelector('#pnnext, a[aria-label="Next page"]'),
    count: results.length,
    results,
  };
})()
