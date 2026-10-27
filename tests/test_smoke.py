from pathlib import Path

import pytest
from pydantic import ValidationError

from agent import rag, scrape
from agent.graph import build_graph
from agent.score import Score, validate_score


def test_parser_on_fixture():
    papers = scrape.parse_listing((Path(__file__).parent / "fixtures/arxiv_cs_cl_new.html").read_text())
    assert len(papers) == 3 and all(p["id"] and p["title"] and p["abstract"] for p in papers)


def test_score_schema_validates():
    Score(relevant=True, matched_hypothesis="H3", reason="x")
    with pytest.raises(ValidationError):
        Score(relevant=True, matched_hypothesis="H99", reason="x")


def test_graph_compiles():
    assert build_graph() is not None


def test_retriever_returns_chunks(tmp_path):
    col = rag.build_index(tmp_path / "db")
    hits = rag.retrieve(col, "attention heads causing refusal ablation", k=3)
    assert len(hits) == 3 and all(h["text"] for h in hits)


def test_parse_blog_on_fixture():
    posts = scrape.parse_blog((Path(__file__).parent / "fixtures/alignment_blog.html").read_text())
    assert len(posts) == 3 and all(p["id"].startswith("blog:") and p["title"] and p["abstract"] for p in posts)


PAPER = {"title": "Circuits shift", "abstract": "Attention heads shift during training and the circuit reorganizes."}
CHUNKS = [{"source": "f", "text": "The dominant refusal head moved from mid-network to layer 0."}]
GOOD = {"relevant": True, "matched_hypothesis": "H4", "reason": "x",
        "abstract_quote": "Attention heads shift during training", "evidence_quote": "moved from mid-network to layer 0"}


def test_validate_accepts_grounded():
    assert validate_score(PAPER, CHUNKS, GOOD)["validation"] == "ok"


def test_validate_rejects_fabricated_evidence():
    out = validate_score(PAPER, CHUNKS, {**GOOD, "evidence_quote": "we plan a cross-lingual extension"})
    assert out["relevant"] is False and "evidence_quote" in out["validation"]


def test_validate_rejects_misquoted_abstract():
    out = validate_score(PAPER, CHUNKS, {**GOOD, "abstract_quote": "jailbreaks transfer across seeds"})
    assert out["relevant"] is False and "abstract_quote" in out["validation"]
