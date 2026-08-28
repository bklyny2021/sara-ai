#!/usr/bin/env python3
"""
SARA PEOPLE FINDER - find people across public sources.
Searches public records, social media, and web for a person.
Uses free, no-login sources (DuckDuckGo, public directories).

Note: Facebook/Instagram/TikTok/X require login to search directly.
Sara searches public web results for those platforms instead.
"""
import json
import re
import urllib.request
import urllib.parse
import html as html_mod

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

def _fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def _clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_mod.unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def _ddg_search(query, num=10):
    """Search DuckDuckGo and return results"""
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    html = _fetch(url)
    blocks = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
    snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html)
    results = []
    for i, (href, title) in enumerate(blocks[:num]):
        m = re.search(r'uddg=([^&]+)', href)
        real = urllib.parse.unquote(m.group(1)) if m else href
        snip = _clean(snippets[i]) if i < len(snippets) else ""
        results.append({"title": _clean(title), "url": real, "snippet": snip})
    return results

def find_person(name, location=None):
    """Find a person by name (and optional location)"""
    out = []
    out.append(f"🔎 People search for: {name}" + (f" in {location}" if location else ""))
    out.append("")
    
    # 1. General web search
    q = f'"{name}"'
    if location:
        q += f" {location}"
    try:
        results = _ddg_search(q, 8)
        out.append("🌐 Web results:")
        for r in results:
            out.append(f"  • {r['title']}\n    {r['url']}\n    {r['snippet'][:120]}")
    except Exception as e:
        out.append(f"  (web search error: {e})")
    
    # 2. Social media specific searches
    out.append("")
    out.append("📱 Social media:")
    platforms = {
        "Facebook": f'"{name}" site:facebook.com',
        "Instagram": f'"{name}" site:instagram.com',
        "TikTok": f'"{name}" site:tiktok.com',
        "X/Twitter": f'"{name}" site:x.com OR site:twitter.com',
        "LinkedIn": f'"{name}" site:linkedin.com',
    }
    for platform, q in platforms.items():
        try:
            results = _ddg_search(q, 2)
            if results:
                out.append(f"  {platform}:")
                for r in results[:2]:
                    out.append(f"    • {r['title']}\n      {r['url']}")
            else:
                out.append(f"  {platform}: no public results")
        except:
            out.append(f"  {platform}: search error")
    
    return "\n".join(out)

def find_phone(name, location=None):
    """Search for a person's phone/contact info"""
    q = f'"{name}" phone contact'
    if location:
        q += f" {location}"
    try:
        results = _ddg_search(q, 6)
        out = [f"📞 Contact search for {name}:"]
        for r in results:
            out.append(f"  • {r['title']}\n    {r['url']}\n    {r['snippet'][:120]}")
        return "\n".join(out)
    except Exception as e:
        return f"❌ Contact search error: {e}"

def find_inmate(name, location=None):
    """Search public inmate/jail/prison databases for a person.
    Covers NYC jails, NY state prisons, and federal prisons."""
    out = []
    out.append(f"⛓️ Inmate search for: {name}")
    out.append("")
    
    # NYC Department of Corrections (Rikers + city jails)
    out.append("🏙️ NYC DOC (Rikers & city jails):")
    try:
        q = f'"{name}" site:nyc.gov inmate OR "department of corrections"'
        if location:
            q += f" {location}"
        results = _ddg_search(q, 3)
        for r in results:
            out.append(f"  • {r['title']}\n    {r['url']}\n    {r['snippet'][:100]}")
        if not results:
            out.append("  No NYC DOC results found")
    except Exception as e:
        out.append(f"  (error: {e})")
    
    # NY State Department of Corrections (DOCCS - upstate prisons)
    out.append("")
    out.append("🏛️ NY State DOCCS (upstate prisons):")
    try:
        q = f'"{name}" site:doccs.ny.gov OR "new york state" inmate lookup'
        results = _ddg_search(q, 3)
        for r in results:
            out.append(f"  • {r['title']}\n    {r['url']}\n    {r['snippet'][:100]}")
        if not results:
            out.append("  No NY DOCCS results found")
    except Exception as e:
        out.append(f"  (error: {e})")
    
    # Federal Bureau of Prisons (BOP)
    out.append("")
    out.append("🇺🇸 Federal BOP (federal prisons):")
    try:
        q = f'"{name}" site:bop.gov inmate locator'
        results = _ddg_search(q, 3)
        for r in results:
            out.append(f"  • {r['title']}\n    {r['url']}\n    {r['snippet'][:100]}")
        if not results:
            out.append("  No federal BOP results found")
    except Exception as e:
        out.append(f"  (error: {e})")
    
    # General inmate search
    out.append("")
    out.append("🔍 General inmate databases:")
    try:
        q = f'"{name}" inmate locator OR "inmate search" OR "prisoner search"'
        if location:
            q += f" {location}"
        results = _ddg_search(q, 5)
        for r in results:
            out.append(f"  • {r['title']}\n    {r['url']}\n    {r['snippet'][:100]}")
    except Exception as e:
        out.append(f"  (error: {e})")
    
    return "\n".join(out)

if __name__ == "__main__":
    import sys
    name = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "John Smith"
    print(find_person(name))
