"""LangGraph: Scout agent (scrape->fetch->retrieve->score) -> conditional -> Outreach agent (draft)."""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from agent import rag, records, scrape
from agent.draft import draft_outreach
from agent.score import score_paper


class State(TypedDict, total=False):
    max_papers: int
    scraped: list[dict]
    papers: list[dict]
    chunks: dict       # paper id -> retrieved chunks
    scores: dict       # paper id -> Score dict
    drafts: dict       # paper id -> draft text


# ---- Scout agent nodes ----
def scrape_node(state: State) -> dict:
    items = [p for p in scrape.scrape_listing() if scrape.looks_relevant(p)]
    return {"scraped": items}


def fetch_node(state: State) -> dict:
    """arXiv API: official metadata for scraped ids + recent keyword-search hits, merged by id."""
    n = state["max_papers"]
    by_id = {p["id"]: p for p in state.get("scraped", [])}
    for p in records.fetch_by_ids(list(by_id)):          # API record wins (clean authors/date)
        by_id[p["id"]] = {**by_id[p["id"]], **p} if p["id"] in by_id else p
    for p in records.search_recent(n):
        by_id.setdefault(p["id"], p)
    return {"papers": list(by_id.values())[:n]}


def retrieve_node(state: State) -> dict:
    col = rag.build_index()
    return {"chunks": {p["id"]: rag.retrieve(col, p["title"] + "\n" + p["abstract"]) for p in state["papers"]}}


def score_node(state: State) -> dict:
    return {"scores": {p["id"]: score_paper(p, state["chunks"][p["id"]]) for p in state["papers"]}}


def route(state: State) -> str:
    return "outreach" if any(s["relevant"] for s in state["scores"].values()) else END


# ---- Outreach agent node ----
def draft_node(state: State) -> dict:
    drafts = {}
    for p in state["papers"]:
        s = state["scores"][p["id"]]
        if s["relevant"]:
            drafts[p["id"]] = draft_outreach(p, s, state["chunks"][p["id"]])
    return {"drafts": drafts}


def build_scout():
    g = StateGraph(State)
    for name, fn in [("scrape", scrape_node), ("fetch", fetch_node), ("retrieve", retrieve_node), ("score", score_node)]:
        g.add_node(name, fn)
    g.set_entry_point("scrape")
    g.add_edge("scrape", "fetch"); g.add_edge("fetch", "retrieve"); g.add_edge("retrieve", "score")
    g.add_edge("score", END)
    return g.compile()


def build_outreach():
    g = StateGraph(State)
    g.add_node("draft", draft_node)
    g.set_entry_point("draft"); g.add_edge("draft", END)
    return g.compile()


def build_graph():
    g = StateGraph(State)
    g.add_node("scout", build_scout())
    g.add_node("outreach", build_outreach())
    g.set_entry_point("scout")
    g.add_conditional_edges("scout", route, {"outreach": "outreach", END: END})
    g.add_edge("outreach", END)
    return g.compile()
