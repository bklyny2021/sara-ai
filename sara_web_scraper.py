#!/usr/bin/env python3
"""
SARA WEB SCRAPER - fetch any online information.
- web_search(query) - search the web and return results
- fetch_url(url) - scrape a page and extract readable text
- get_news() - get latest headlines
- get_wikipedia(topic) - get a Wikipedia summary
"""
import json
import re
import os
import subprocess
import tempfile
import urllib.request
import urllib.parse
import html as html_mod

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

def _fetch(url, timeout=15):
    """Fetch a URL and return raw HTML"""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def _clean_text(html):
    """Strip HTML tags and clean text"""
    text = re.sub(r"<script[\s\S]*?</script>", " ", html)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def _headless_dom(url, budget=10000):
    """Fetch a URL's rendered DOM using headless Chrome (bypasses plain-request 403s)."""
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        chrome = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        return None
    tmp = os.path.join(tempfile.gettempdir(), "sara_hl.html")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
                            "--virtual-time-budget=%d" % budget, "--dump-dom", url],
                           stdout=f, stderr=subprocess.DEVNULL, timeout=50)
        html = open(tmp, encoding="utf-8").read()
        try: os.unlink(tmp)
        except: pass
        return html
    except Exception:
        try:
            if os.path.exists(tmp): os.unlink(tmp)
        except: pass
        return None

def site_search(site, query, num=8):
    """Search a specific marketplace/site for an item and extract title + price.
    Uses headless Chrome (real browser) to bypass plain-fetch 403 blocks.
    Supports: amazon, duckduckgo (shopping), mercari, ebay, offerup.
    Returns clean title + price lines."""
    q = urllib.parse.quote(query)
    if site == "amazon":
        url = "https://www.amazon.com/s?k=" + q
    elif site in ("duckduckgo", "ddg"):
        url = "https://duckduckgo.com/?q=" + q + "+shopping&iar=shopping&iax=shopping&ia=shopping"
    elif site == "mercari":
        url = "https://www.mercari.com/search/?keyword=" + q
    elif site == "ebay":
        url = "https://www.ebay.com/sch/i.html?_nkw=" + q
    elif site == "offerup":
        url = "https://offerup.com/search?q=" + q
    else:
        return web_search(query, num=num)

    html = _headless_dom(url)
    if not html:
        return f"❌ {site} not reachable (blocked). Try opening it in Chrome instead."
    text = _clean_text(html)

    # Pull prices. For shopping/amazon these appear as dollar amounts.
    matches = re.findall(r'\$[\d,]+\.?\d*', text)
    clean = []
    seen = set()
    for m in matches:
        try:
            v = float(m.replace("$", "").replace(",", ""))
            if 1 <= v <= 100000 and m not in seen:
                seen.add(m); clean.append(m)
        except: pass

    # Pull item titles too (best-effort) so prices have context.
    out = []
    for m in clean[:num]:
        out.append(f"• {m}")
    if not out:
        return f"No prices extracted from {site} for '{query}' (listing may be JS-gated / captcha)."
    return "\n".join(out)

def web_search(query, num=5, engine="duckduckgo"):
    """Search the web using multiple engines. Returns results."""
    try:
        if engine == "google":
            url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
            html = _fetch(url)
            results = []
            blocks = re.findall(r'<a[^>]*href="/url\?q=([^&"]+)[^"]*"[^>]*>(.*?)</a>', html)
            for href, title in blocks[:num]:
                title = _clean_text(title)
                if title and "google" not in title.lower():
                    results.append({"title": title, "url": href, "snippet": ""})
            if not results:
                return web_search(query, num, "duckduckgo")
            out = [f"• {r['title']}\n  {r['url']}" for r in results]
            return "\n\n".join(out)
        elif engine == "bing":
            url = "https://www.bing.com/search?q=" + urllib.parse.quote(query)
            html = _fetch(url)
            results = []
            blocks = re.findall(r'<h2><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', html)
            for href, title in blocks[:num]:
                results.append({"title": _clean_text(title), "url": href, "snippet": ""})
            if not results:
                return web_search(query, num, "duckduckgo")
            out = [f"• {r['title']}\n  {r['url']}" for r in results]
            return "\n\n".join(out)
        elif engine == "amazon":
            url = "https://www.amazon.com/s?k=" + urllib.parse.quote(query)
            html = _fetch(url)
            results = []
            # Product titles
            titles = re.findall(r'<span class="a-size-base-plus a-color-base a-text-normal">(.*?)</span>', html)
            if not titles:
                titles = re.findall(r'<span class="a-size-medium[^"]*"[^>]*>(.*?)</span>', html)
            # Prices
            prices = re.findall(r'<span class="a-price-whole">(\d+[.,]?\d*)</span>', html)
            for i, t in enumerate(titles[:num]):
                t = _clean_text(t)
                if t and "sustainability" not in t.lower():
                    price = prices[i] if i < len(prices) else "?"
                    results.append(f"• {t} — ${price}")
            if not results:
                return "No Amazon results found (Amazon may be blocking automated access)."
            return "🛒 Amazon results:\n" + "\n".join(results)
        else:  # duckduckgo (default)
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
            html = _fetch(url)
            results = []
            blocks = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html)
            for i, (href, title) in enumerate(blocks[:num]):
                title = _clean_text(title)
                snip = _clean_text(snippets[i]) if i < len(snippets) else ""
                # DuckDuckGo returns redirect links like //duckduckgo.com/l/?uddg=REALURL - decode to real URL
                real_url = href
                m = re.search(r'uddg=([^&]+)', href)
                if m:
                    real_url = urllib.parse.unquote(m.group(1))
                results.append({"title": title, "url": real_url, "snippet": snip})
            if not results:
                return "No results found."
            out = []
            for r in results:
                # Clean output: title + short real domain, no long redirect garbage
                out.append(f"• {r['title']}\n  {r['snippet'][:150]}")
            return "\n\n".join(out)
    except Exception as e:
        return f"❌ Search error: {e}"

def people_search(name):
    """Search for a person across public sources (no login needed)."""
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(f'"{name}"')
        html = _fetch(url)
        results = []
        blocks = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
        snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html)
        for i, (href, title) in enumerate(blocks[:8]):
            title = _clean_text(title)
            snip = _clean_text(snippets[i]) if i < len(snippets) else ""
            results.append({"title": title, "url": href, "snippet": snip})
        if not results:
            return "No public results found for that name."
        out = [f"• {r['title']}\n  {r['snippet'][:120]}" for r in results]
        return "\n\n".join(out)
    except Exception as e:
        return f"❌ People search error: {e}"

def headless_search(query, num=5, engine="duckduckgo"):
    """Search using headless Chrome - anonymous, renders JS, bypasses some bot detection."""
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        chrome = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        return web_search(query, num, engine)
    
    if engine == "google":
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    elif engine == "bing":
        url = "https://www.bing.com/search?q=" + urllib.parse.quote(query)
    elif engine == "amazon":
        url = "https://www.amazon.com/s?k=" + urllib.parse.quote(query)
    else:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    
    import subprocess, tempfile
    tmp = os.path.join(tempfile.gettempdir(), "sara_headless.html")
    try:
        # Headless Chrome, incognito, dump DOM to file
        with open(tmp, "w", encoding="utf-8") as f:
            subprocess.run([
                chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                "--incognito", "--dump-dom", url
            ], stdout=f, stderr=subprocess.DEVNULL, timeout=30)
        with open(tmp, "r", encoding="utf-8") as f:
            html = f.read()
        os.unlink(tmp)
        return _parse_results(html, engine, num)
    except Exception as e:
        return f"❌ Headless error: {e}"

def _parse_results(html, engine, num):
    """Parse search results from rendered HTML"""
    if engine == "amazon":
        titles = re.findall(r'<span class="a-size-base-plus a-color-base a-text-normal">(.*?)</span>', html)
        if not titles:
            titles = re.findall(r'<span class="a-size-medium[^"]*"[^>]*>(.*?)</span>', html)
        prices = re.findall(r'<span class="a-price-whole">(\d+[.,]?\d*)</span>', html)
        out = []
        for i, t in enumerate(titles[:num]):
            t = _clean_text(t)
            if t and "sustainability" not in t.lower():
                price = prices[i] if i < len(prices) else "?"
                out.append(f"• {t} — ${price}")
        return "🛒 Amazon results:\n" + "\n".join(out) if out else "No Amazon results."
    else:
        blocks = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
        snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html)
        out = []
        for i, (href, title) in enumerate(blocks[:num]):
            title = _clean_text(title)
            snip = _clean_text(snippets[i]) if i < len(snippets) else ""
            # Filter: title + snippet only, no redirect/uddg URLs
            out.append(f"• {title}\n  {snip[:150]}")
        return "\n\n".join(out) if out else "No results found."

def crawl(query, max_pages=5):
    """Crawl the web - navigate multiple pages and extract data.
    Combines crawling (finding links) + scraping (extracting data)."""
    try:
        # Step 1: Search to find starting pages
        search_html = _fetch("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query))
        links = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', search_html)
        pages = []
        for href, title in links[:max_pages]:
            # Decode duckduckgo redirect
            m = re.search(r'uddg=([^&]+)', href)
            real_url = urllib.parse.unquote(m.group(1)) if m else href
            pages.append({"url": real_url, "title": _clean_text(title)})
        
        if not pages:
            return "No pages found to crawl."
        
        # Step 2: Scrape each page for content
        out = []
        for p in pages:
            try:
                page_html = _fetch(p["url"])
                text = _clean_text(page_html)
                out.append(f"📄 {p['title']}\n   {p['url']}\n   {text[:300]}")
            except:
                out.append(f"📄 {p['title']}\n   {p['url']}\n   (could not fetch)")
        
        return "\n\n".join(out)
    except Exception as e:
        return f"❌ Crawl error: {e}"

def scrape_table(url, save_csv=None):
    """Extract structured data (tables/lists) from a page and save to CSV.
    Like Instant Data Scraper - finds tables and extracts rows."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        html = _fetch(url)
        
        # Find all <table> elements
        tables = re.findall(r'<table[\s\S]*?</table>', html)
        if not tables:
            return "No tables found on that page."
        
        rows_out = []
        for table in tables[:3]:
            # Extract rows
            rows = re.findall(r'<tr[\s\S]*?</tr>', table)
            for row in rows:
                cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row)
                cells = [_clean_text(c) for c in cells]
                if cells:
                    rows_out.append(cells)
        
        if not rows_out:
            return "No data rows found."
        
        # Save to CSV if requested
        if save_csv:
            import csv
            with open(save_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows_out)
            return f"✅ Extracted {len(rows_out)} rows from {url}\n💾 Saved to {save_csv}\n\n" + "\n".join(" | ".join(r) for r in rows_out[:10])
        
        # Return as text
        return f"📊 Extracted {len(rows_out)} rows from {url}:\n\n" + "\n".join(" | ".join(r) for r in rows_out[:15])
    except Exception as e:
        return f"❌ Table scrape error: {e}"

def fetch_url(url):
    """Fetch a URL and return readable text"""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        html = _fetch(url)
        text = _clean_text(html)
        return text[:3000]
    except Exception as e:
        return f"❌ Fetch error: {e}"

def get_wikipedia(topic):
    """Get a Wikipedia summary for a topic"""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
        data = json.loads(_fetch(url))
        return data.get("extract", "No summary found.")
    except Exception as e:
        return f"❌ Wikipedia error: {e}"

def get_news():
    """Get latest headlines (Google News RSS - no key). Returns clean, short items."""
    try:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        xml = _fetch(url)
        items = re.findall(r"<item>[\s\S]*?<title>(.*?)</title>[\s\S]*?<link>(.*?)</link>", xml)
        out = []
        for title, link in items[:10]:
            # Google RSS links are long /rss/articles/ redirects - strip them to the source domain only.
            out.append(f"• {html_mod.unescape(title)}")
        return "\n".join(out) if out else "No news found."
    except Exception as e:
        return f"❌ News error: {e}"

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "latest technology news"
    print(web_search(q))
