"""Playwright node: scrape the arXiv 'new submissions' listing page."""
import re
from html import unescape

from playwright.sync_api import sync_playwright

LISTING_URL = "https://arxiv.org/list/cs.CL/new"
BLOG_URL = "https://alignment.anthropic.com/"
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


def _get_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html = page.content()
        browser.close()
    return html


def scrape_listing(url: str = LISTING_URL) -> list[dict]:
    return parse_listing(_get_html(url))


def parse_blog(html: str, base_url: str = BLOG_URL) -> list[dict]:
    """Pure: lab-blog index HTML -> records. No arXiv id or authors, so id is 'blog:<slug>'."""
    out = []
    for href, body in re.findall(r'<a href="([^"]+)" class="(?:note|paper)">(.*?)</a>', html, re.S):
        title = re.search(r"<h3>(.*?)</h3>", body, re.S)
        desc = re.search(r'class="description">(.*?)</div>', body, re.S)
        if not title:
            continue
        out.append({
            "id": "blog:" + href.strip("/").replace("/", "-"),
            "title": _text(title.group(1)),
            "authors": [],
            "abstract": _text(desc.group(1)) if desc else "",
            "url": base_url.rstrip("/") + "/" + href,
            "published": "",
        })
    return out


def scrape_blog(url: str = BLOG_URL) -> list[dict]:
    return parse_blog(_get_html(url), url)


def looks_relevant(paper: dict) -> bool:
    text = (paper["title"] + " " + paper["abstract"]).lower()
    return any(k in text for k in KEYWORDS)
