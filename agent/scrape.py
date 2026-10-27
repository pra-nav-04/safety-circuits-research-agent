"""Playwright node: scrape the arXiv 'new submissions' listing page."""
import re
from html import unescape

from playwright.sync_api import sync_playwright

LISTING_URL = "https://arxiv.org/list/cs.CL/new"
# Words that make a listing entry worth looking at (keeps the LLM bill small).
KEYWORDS = ("safety", "refus", "jailbreak", "harm", "align", "interpretab", "attention head", "circuit", "red team", "guardrail")


def _text(s: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", s)).split())


def parse_listing(html: str) -> list[dict]:
    """Pure function (testable on a saved fixture): listing HTML -> [{id,title,authors,abstract,url}]."""
    out = []
    for dt, dd in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", html, re.S):
        m = re.search(r'href="/abs/([^"]+)"', dt)
        title = re.search(r'list-title[^>]*>\s*<span class="descriptor">Title:</span>(.*?)</div>', dd, re.S)
        authors = re.search(r'list-authors">(.*?)</div>', dd, re.S)
        abstract = re.search(r'<p class="mathjax">(.*?)</p>', dd, re.S)
        if not (m and title):
            continue
        out.append({
            "id": m.group(1),
            "title": _text(title.group(1)),
            "authors": [a.strip() for a in _text(authors.group(1)).replace("Authors:", "").split(",")] if authors else [],
            "abstract": _text(abstract.group(1)) if abstract else "",
            "url": f"https://arxiv.org/abs/{m.group(1)}",
        })
    return out


def scrape_listing(url: str = LISTING_URL) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html = page.content()
        browser.close()
    return parse_listing(html)


def looks_relevant(paper: dict) -> bool:
    text = (paper["title"] + " " + paper["abstract"]).lower()
    return any(k in text for k in KEYWORDS)
