#!/usr/bin/env python3
"""
SARA BROWSER AGENT - lets Sara take control of a real browser (like Ada).
Uses Playwright (Chromium) to navigate, search, click, type, and read pages.
100% local - no cloud model needed. Sara's model just decides which action to call.
"""
import os
import time
import re
from playwright.sync_api import sync_playwright

class SaraBrowser:
    def __init__(self):
        self._pw = None
        self._browser = None
        self._page = None
        self._started = False

    def _ensure_started(self):
        """Lazily start the browser on first use."""
        if self._started and self._page:
            return
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        self._page = self._browser.new_page()
        self._started = True

    def navigate(self, url):
        """Open a URL in the browser."""
        self._ensure_started()
        if not url.startswith("http"):
            url = "https://" + url
        self._page.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(1)
        return f"Opened {self._page.url}"

    def search(self, query):
        """Search the web and return top results.
        Uses the plain-HTTP scraper (which works) instead of the browser,
        because search engines show CAPTCHAs to automated browsers."""
        try:
            import sara_web_scraper as ws
            return ws.web_search(query, num=5)
        except Exception as e:
            return f"Search error: {e}"

    def click(self, text):
        """Click an element by its visible text."""
        self._ensure_started()
        try:
            self._page.get_by_text(text, exact=False).first.click(timeout=10000)
            time.sleep(1)
            return f"Clicked '{text}'. Now at {self._page.url}"
        except Exception as e:
            return f"Could not click '{text}': {e}"

    def type_text(self, text, press_enter=False):
        """Type text into the focused/active field."""
        self._ensure_started()
        try:
            self._page.keyboard.type(text)
            if press_enter:
                self._page.keyboard.press("Enter")
                time.sleep(1)
            return f"Typed '{text}'"
        except Exception as e:
            return f"Could not type: {e}"

    def read_page(self):
        """Read the current page's visible text content."""
        self._ensure_started()
        try:
            text = self._page.inner_text("body")
            text = re.sub(r"\s+", " ", text).strip()
            return text[:2000]
        except Exception as e:
            return f"Could not read page: {e}"

    def screenshot(self, path=None):
        """Take a screenshot of the current page."""
        self._ensure_started()
        if not path:
            path = os.path.join("C:/Users/bklyn/SARA3-2026", "sara_browser_shot.png")
        try:
            self._page.screenshot(path=path)
            return f"Screenshot saved to {path}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def close(self):
        """Close the browser."""
        try:
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
            self._started = False
            return "Browser closed."
        except Exception as e:
            return f"Close error: {e}"

# Singleton so Sara keeps one browser session across calls
_browser = SaraBrowser()

def run(action, *args):
    """Main entry point for Sara's tool. action = navigate|search|click|type|read|screenshot|close"""
    try:
        if action == "navigate":
            return _browser.navigate(args[0] if args else "")
        if action == "search":
            return _browser.search(args[0] if args else "")
        if action == "click":
            return _browser.click(args[0] if args else "")
        if action == "type":
            return _browser.type_text(args[0] if args else "", press_enter=(len(args) > 1 and args[1]))
        if action == "read":
            return _browser.read_page()
        if action == "screenshot":
            return _browser.screenshot(args[0] if args else None)
        if action == "close":
            return _browser.close()
        return "Unknown browser action. Use: navigate, search, click, type, read, screenshot, close"
    except Exception as e:
        return f"Browser error: {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(run(sys.argv[1], *sys.argv[2:]))
    else:
        print("Usage: python sara_browser.py <action> [args]")
