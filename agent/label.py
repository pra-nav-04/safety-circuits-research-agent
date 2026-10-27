"""Blind labelling of a fresh paper pool: python -m agent.label  (build pool first: python -m agent.label --build)
Shows title + abstract only, never the model's verdict. Saves after every answer; safe to quit and resume."""
import argparse
import json
import random
from pathlib import Path

from agent import records, scrape
from agent.rag import OPEN_HYPOTHESES

EVAL = Path(__file__).resolve().parent.parent / "eval"
QUERIES = [
    'abs:"refusal direction" OR abs:"refusal" AND abs:"activation"',
    'abs:"attention heads" AND (abs:safety OR abs:jailbreak OR abs:refusal)',
    'abs:"activation steering" AND abs:safety',
    'abs:LoRA AND (abs:"safety" OR abs:"alignment") AND abs:fine-tuning',
    'abs:"circuit" AND abs:"language model" AND abs:interpretability',
    'abs:"unlearning" OR abs:"knowledge editing" AND abs:safety',
    'abs:"sparse autoencoder" AND abs:safety',
    'abs:"harmful fine-tuning" OR abs:"safety degradation"',
]


def build_pool(n: int = 60, seed: int = 7) -> None:
    known = {p["id"] for p in json.loads((EVAL / "papers.json").read_text())}
    cand: dict[str, dict] = {}
    for q in QUERIES:
        for p in records._query(search_query=q, sortBy="submittedDate", sortOrder="descending", max_results=12):
            if p["id"] not in known:
                cand.setdefault(p["id"], p)
    keyword = list(cand.values())
    other = [p for p in scrape.scrape_listing() + scrape.scrape_blog() if p["id"] not in known and p["id"] not in cand]
    rnd = random.Random(seed)
    rnd.shuffle(keyword)
    rnd.shuffle(other)
    pool = keyword[: int(n * 0.65)] + other[: n - int(n * 0.65)]   # keyword hits raise the share of positives
    rnd.shuffle(pool)                                              # order carries no information
    (EVAL / "pool.json").write_text(json.dumps(pool, indent=1))
    print(f"pool: {len(pool)} papers ({len(keyword)} keyword candidates, {len(other)} other) -> eval/pool.json")


RUBRIC = ("relevant = studies a refusal/safety MECHANISM, edits/trains safety behaviour (what transfers), localisable safety "
          "directions, or judge/metric validity for attack success.\nNOT: pure behavioural benchmarks/attacks, topic-only overlap.")


def label() -> None:
    pool = json.loads((EVAL / "pool.json").read_text())
    out_f = EVAL / "labels_new.json"
    out = json.loads(out_f.read_text()) if out_f.exists() else {}
    todo = [p for p in pool if p["id"] not in out]
    print(f"{len(out)} labelled, {len(todo)} left. Keys: y = relevant, n = not, s = skip, q = quit\n{RUBRIC}\n")
    for k, p in enumerate(todo, 1):
        print("=" * 90 + f"\n[{len(out) + 1}/{len(pool)}] {p['title']}\n\n{p['abstract'][:1400]}\n")
        while True:
            a = input("relevant? [y/n/s/q] ").strip().lower()
            if a in {"y", "n", "s", "q"}:
                break
        if a == "q":
            break
        if a == "s":
            continue
        hyp = "none"
        if a == "y":
            h = input(f"which item? {'/'.join(OPEN_HYPOTHESES)} (enter = unsure) ").strip()
            hyp = h if h in OPEN_HYPOTHESES else "unsure"
        out[p["id"]] = {"relevant": a == "y", "hypothesis": hyp, "labeller": "owner", "blind": True}
        out_f.write_text(json.dumps(out, indent=1))
    print(f"saved {len(out)} labels to {out_f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--n", type=int, default=60)
    a = ap.parse_args()
    build_pool(a.n) if a.build else label()
