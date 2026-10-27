"""RAG index over the research repo's paper + findings + plan. Chroma, default local embeddings."""
import os
import re
from pathlib import Path

import chromadb

SRC = Path(os.environ.get(
    "SAFETY_CIRCUITS_DIR",
    Path(__file__).resolve().parents[2] / "safety-circuits",
))
FILES = ["paper/paper.md", "FINDINGS.md", "RESEARCH_PLAN.md"]
DB = Path(__file__).resolve().parent.parent / "chroma_db"

# Open / partial / falsified items from FINDINGS.md (scorecard ~l.69, "What's next" ~l.396)
# and RESEARCH_PLAN.md (§1 hypotheses, §9 future work). The scorer must pick one of these keys.
OPEN_HYPOTHESES = {
    "H3": "Top-10 head ablation removes refusal: only PARTIAL (works for Qwen2/2.5/3, Gemma3; fails for Gemma1/2, Llama).",
    "H3b": "Removing refusal while preserving capability (dPPL<=5%): FALSIFIED. Refusal is causally concentrated but not modular.",
    "H4": "Same circuit structure across models: PARTIAL. Location migrates across generations; modularity scales with depth.",
    "F1": "Head-restricted LoRA: edit refusal by retraining only the identified heads.",
    "F2": "Generational sweep: how the refusal circuit location changes across model generations.",
    "F3": "Content-transfer: does the edited circuit produce harmful content or only the refusal opener?",
    "EXT": "Ongoing extensions: edit generalization, minimal clean edit, safety re-patch round-trip, refusal-direction shift, benign substance unlock.",
}


def chunk_markdown(text: str, max_chars: int = 1200) -> list[str]:
    """Split on blank lines, pack paragraphs into chunks of <= max_chars."""
    chunks, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        if cur and len(cur) + len(para) > max_chars:
            chunks.append(cur.strip())
            cur = ""
        cur += para + "\n\n"
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def build_index(path: Path = DB):
    client = chromadb.PersistentClient(path=str(path))
    col = client.get_or_create_collection("safety_circuits")
    if col.count() == 0:
        ids, docs, metas = [], [], []
        for f in FILES:
            for i, c in enumerate(chunk_markdown((SRC / f).read_text())):
                ids.append(f"{f}:{i}"); docs.append(c); metas.append({"source": f})
        col.add(ids=ids, documents=docs, metadatas=metas)
    return col


def retrieve(col, query: str, k: int = 4) -> list[dict]:
    res = col.query(query_texts=[query], n_results=k)
    return [{"source": m["source"], "text": d, "distance": dist}
            for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])]
