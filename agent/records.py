"""arXiv API integration: keyword search + lookup by id -> plain dict records."""
import re
import urllib.parse

import feedparser

API = "http://export.arxiv.org/api/query"
QUERY = (
    "(cat:cs.CL OR cat:cs.LG) AND (abs:refusal OR abs:jailbreak OR abs:\"safety alignment\" "
    "OR abs:\"activation patching\" OR abs:\"mechanistic interpretability\" OR abs:\"safety fine-tuning\")"
)


def _record(e) -> dict:
    return {
        "id": re.sub(r"v\d+$", "", e.id.rsplit("/abs/", 1)[-1]),
        "title": " ".join(e.title.split()),
        "authors": [a.name for a in e.get("authors", [])],
        "abstract": " ".join(e.summary.split()),
        "url": e.id,
        "published": e.get("published", ""),
    }


def _query(**params) -> list[dict]:
    feed = feedparser.parse(f"{API}?{urllib.parse.urlencode(params)}")
    return [_record(e) for e in feed.entries]


def search_recent(max_results: int = 15) -> list[dict]:
    return _query(search_query=QUERY, sortBy="submittedDate", sortOrder="descending", max_results=max_results)


def fetch_by_ids(ids: list[str]) -> list[dict]:
    return _query(id_list=",".join(ids), max_results=len(ids)) if ids else []
