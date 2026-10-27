"""Score node: match a paper to open hypotheses + pre-qualify, grounded in retrieved chunks."""
import re
from difflib import SequenceMatcher
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
    strength: int = 0          # 1-5 rubric, see PROMPT; 0 when not relevant


PROMPT_NARROW = """You pre-qualify new arXiv papers for a research project on attention heads that cause
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
- strength: integer 1-5. 5 = the abstract directly tests, extends or contradicts the matched item;
  3 = same general topic only; 1 = keyword overlap. Use 0 when relevant=false.
- reason: 1-2 sentences citing what in the abstract and what in the excerpts connect."""


PROMPT_WIDE = PROMPT_NARROW.replace(
    "Decide if the paper bears directly on ONE open hypothesis. Rules:\n- relevant=true only if the abstract itself supports the link; do not guess.",
    "Decide if a researcher on this project (mechanistic study of refusal/safety, safety fine-tuning or editing, activation steering,\n"
    "interpretability methods, LoRA or other parameter-efficient adaptation, unlearning, safety evaluation validity) would want to read\n"
    "this paper, and link it to the CLOSEST open item. Rules:\n- relevant=true only if the abstract itself supports the link; do not guess.")
PROMPT = PROMPT_WIDE   # default; the narrow wording is kept so agent.eval can compare


def score_paper(paper: dict, chunks: list[dict], llm=None, prompt: str | None = None) -> dict:
    """Never raises: parse/validation/API failures become relevant=False with an error note."""
    llm = (llm or get_llm(0)).with_structured_output(Score)
    prompt = (prompt or PROMPT).format(
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


MIN_STRENGTH = 3        # eval: a gate at 4 cost recall without raising precision (README); 5 keeps only ~29% of positives
FUZZY_RATIO = 0.85      # share of a quote that must be found in the source text
MIN_BLOCK = 8           # matching runs shorter than this (chars) do not count


def _contains(quote: str, text: str, fuzzy: bool) -> bool:
    q, t = _norm(quote), _norm(text)
    if not q:
        return False
    if q in t:
        return True
    if not fuzzy:
        return False
    blocks = SequenceMatcher(None, q, t, autojunk=False).get_matching_blocks()
    return sum(b.size for b in blocks if b.size >= MIN_BLOCK) / len(q) >= FUZZY_RATIO


def validate_score(paper: dict, chunks: list[dict], score: dict, fuzzy: bool = True,
                   min_strength: int = MIN_STRENGTH) -> dict:
    """Grounding + strength check, no LLM: a 'relevant' verdict must quote real text from both sides
    and be a strong match. Flags exist so agent/eval.py can compare variants on the labelled set."""
    if not score["relevant"]:
        return {**score, "validation": "skipped (not relevant)"}
    source = paper["title"] + " " + paper["abstract"]
    corpus = " ".join(c["text"] for c in chunks)
    checks = [
        ("abstract_quote not in abstract", _contains(score.get("abstract_quote", ""), source, fuzzy)),
        ("evidence_quote not in retrieved chunks", _contains(score.get("evidence_quote", ""), corpus, fuzzy)),
        ("unknown hypothesis", score["matched_hypothesis"] in OPEN_HYPOTHESES),
        (f"weak match (strength {score.get('strength', 0)} < {min_strength})", score.get("strength", 0) >= min_strength),
    ]
    for msg, ok in checks:
        if not ok:
            return {**score, "relevant": False, "validation": f"rejected: {msg}"}
    return {**score, "validation": "ok"}

