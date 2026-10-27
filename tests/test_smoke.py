from pathlib import Path

import pytest
from pydantic import ValidationError

from agent import rag, scrape
from agent.graph import build_graph
from agent.score import Score


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
