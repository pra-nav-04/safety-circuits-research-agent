"""Score node: match a paper to open hypotheses + pre-qualify, grounded in retrieved chunks."""
import re
from typing import Literal

from pydantic import BaseModel, ValidationError

from agent.llm import get_llm
from agent.rag import OPEN_HYPOTHESES

HypKey = Literal["H3", "H3b", "H4", "F1", "F2", "F3", "EXT", "none"]


class Score(BaseModel):
    relevant: bool
    matched_hypothesis: HypKey
    reason: str
    evidence_quote: str = ""   # verbatim from the retrieved project excerpts
    abstract_quote: str = ""   # verbatim from the paper title/abstract


PROMPT = """You pre-qualify new arXiv papers for a research project on attention heads that cause
small instruct LLMs to refuse harmful prompts.

Open hypotheses / directions (key: description):
{hyps}

Excerpts retrieved from the project's own paper and findings:
{chunks}

New paper:
Title: {title}
Abstract: {abstract}

Decide if the paper bears directly on ONE open hypothesis. Rules:
- relevant=true only if the abstract itself supports the link; do not guess.
- matched_hypothesis is one key above, or "none" when relevant=false.
- Only use the descriptions above; do not invent project plans (e.g. do not claim the project studies languages, topics or methods not listed).
- evidence_quote: one sentence copied VERBATIM from the "Excerpts retrieved" section above that supports the match. A quote copied from the hypothesis list is INVALID and the verdict will be rejected; if no excerpt sentence supports the match, set relevant=false.
- abstract_quote: one sentence copied VERBATIM from the paper abstract that supports the match.
  Both quotes must be empty when relevant=false.
- reason: 1-2 sentences citing what in the abstract and what in the excerpts connect."""


def score_paper(paper: dict, chunks: list[dict], llm=None) -> dict:
    """Never raises: parse/validation/API failures become relevant=False with an error note."""
    llm = (llm or get_llm(0)).with_structured_output(Score)
    prompt = PROMPT.format(
        hyps="\n".join(f"{k}: {v}" for k, v in OPEN_HYPOTHESES.items()),
        chunks="\n---\n".join(c["text"] for c in chunks),
        title=paper["title"], abstract=paper["abstract"],
    )
    try:
        s = llm.invoke(prompt)
        if s is None:
            raise ValueError("model returned no structured output")
        if s.relevant and s.matched_hypothesis == "none":  # contradictory -> reject
            raise ValueError("relevant=true but matched_hypothesis=none")
        return s.model_dump()
    except (ValidationError, ValueError, Exception) as e:  # noqa: BLE001 - keep the run alive
        return {"relevant": False, "matched_hypothesis": "none", "reason": "scoring failed", "error": str(e)[:200]}


def _norm(t: str) -> str:
    """Lowercase, drop markdown/punctuation so '**bold**' and plain quotes compare equal."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t.lower()).split())


def validate_score(paper: dict, chunks: list[dict], score: dict) -> dict:
    """Grounding check, no LLM: a 'relevant' verdict must quote real text from both sides."""
    if not score["relevant"]:
        return {**score, "validation": "skipped (not relevant)"}
    source = _norm(paper["title"] + " " + paper["abstract"])
    corpus = _norm(" ".join(c["text"] for c in chunks))
    checks = [
        ("abstract_quote not in abstract", _norm(score.get("abstract_quote", "")) in source and score.get("abstract_quote")),
        ("evidence_quote not in retrieved chunks", _norm(score.get("evidence_quote", "")) in corpus and score.get("evidence_quote")),
        ("unknown hypothesis", score["matched_hypothesis"] in OPEN_HYPOTHESES),
    ]
    for msg, ok in checks:
        if not ok:
            return {**score, "relevant": False, "validation": f"rejected: {msg}"}
    return {**score, "validation": "ok"}
