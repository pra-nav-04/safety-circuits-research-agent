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
        "abstract_quote": "Attention heads shift during training", "evidence_quote": "moved from mid-network to layer 0", "strength": 5}


def test_validate_accepts_grounded():
    assert validate_score(PAPER, CHUNKS, GOOD)["validation"] == "ok"


def test_validate_rejects_fabricated_evidence():
    out = validate_score(PAPER, CHUNKS, {**GOOD, "evidence_quote": "we plan a cross-lingual extension"})
    assert out["relevant"] is False and "evidence_quote" in out["validation"]


def test_validate_rejects_misquoted_abstract():
    out = validate_score(PAPER, CHUNKS, {**GOOD, "abstract_quote": "jailbreaks transfer across seeds"})
    assert out["relevant"] is False and "abstract_quote" in out["validation"]


def test_validate_rejects_thin_match():
    out = validate_score(PAPER, CHUNKS, {**GOOD, "strength": 2})
    assert out["relevant"] is False and "weak match" in out["validation"]


def test_fuzzy_accepts_near_quote_strict_does_not():
    near = {**GOOD, "evidence_quote": "so the dominant refusal head moved from mid network to layer 0"}
    assert validate_score(PAPER, CHUNKS, near)["validation"] == "ok"
    assert validate_score(PAPER, CHUNKS, near, fuzzy=False)["relevant"] is False


def test_fuzzy_still_rejects_fabrication():
    out = validate_score(PAPER, CHUNKS, {**GOOD, "evidence_quote": "we plan a cross-lingual extension of the circuit"})
    assert out["relevant"] is False


def test_fetch_skips_seen_ids(monkeypatch):
    from agent import graph, records
    monkeypatch.setattr(records, "fetch_by_ids", lambda ids: [])
    monkeypatch.setattr(records, "search_recent", lambda n: [])
    scraped = [{"id": "a", "title": "t", "abstract": "x", "authors": []}, {"id": "b", "title": "t", "abstract": "x", "authors": []}]
    out = graph.fetch_node({"max_papers": 5, "scraped": scraped, "seen": ["a"]})
    assert [p["id"] for p in out["papers"]] == ["b"]


def test_lock_blocks_second_run(tmp_path):
    from agent import ops
    lock = tmp_path / "run.lock"
    assert ops.acquire_lock(lock) is True
    assert ops.acquire_lock(lock) is False
    ops.release_lock(lock)
    assert ops.acquire_lock(lock) is True


def test_health_check_fails_on_closed_port(monkeypatch):
    from agent import ops
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setenv("VLLM_API_KEY", "x")
    ok, msg = ops.health_check(timeout=2)
    assert ok is False and "unreachable" in msg


def test_digest_lists_relevant_paper():
    from agent import ops
    papers = [{"id": "a", "title": "Heads shift", "url": "http://x"}, {"id": "b", "title": "Other", "url": "http://y"}]
    scores = {"a": {"relevant": True, "matched_hypothesis": "H4", "reason": "r", "abstract_quote": "q1", "evidence_quote": "q2"},
              "b": {"relevant": False, "matched_hypothesis": "none", "reason": "r"}}
    md = ops.digest(papers, scores, {"a": "draft"}, "run1")
    assert "Heads shift" in md and "Other" not in md and "Needs human review" in md


def test_bootstrap_ci_and_kappa():
    from agent import eval as ev
    gold = {str(i): i % 2 == 0 for i in range(20)}
    perfect = [dict(gold)]
    lo_hi = ev.bootstrap(perfect, gold, n=200)
    assert all(lo == 1.0 and hi == 1.0 for lo, hi in lo_hi)          # perfect predictor: CI collapses to 1
    assert ev.kappa(gold, gold) == 1.0
    assert ev.kappa(gold, {k: not v for k, v in gold.items()}) < 0


def test_validate_node_skipped_when_flag_false():
    from agent import graph
    out = graph.validate_node({"papers": [], "chunks": {}, "scores": {"a": {"relevant": True, "matched_hypothesis": "H4", "reason": "x"}}})
    assert out["scores"]["a"]["relevant"] is True and out["scores"]["a"]["validation"] == "off"


def test_wide_prompt_differs_and_formats():
    from agent import score
    assert score.PROMPT_WIDE != score.PROMPT_NARROW and "would want to read" in score.PROMPT_WIDE
    score.PROMPT_WIDE.format(hyps="h", chunks="c", title="t", abstract="a")
