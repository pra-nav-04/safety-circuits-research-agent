"""Evaluate the pipeline on labelled papers: python -m agent.eval
dev  = eval/papers.json + labels.json      (used to choose settings)
test = eval/pool.json + labels_new.json    (fresh, blind owner labels; never used to tune anything)
Each paper is scored REPEATS times (the LLM is not deterministic); variants of the validation step are
compared offline on the same scores. CIs: bootstrap over papers, picking a random run per paper."""
import argparse
import json
import random
from pathlib import Path

from agent import rag
from agent import score as sc
from agent.score import score_paper, validate_score

EVAL = Path(__file__).resolve().parent.parent / "eval"
REPEATS = 3

VARIANTS = {
    "no validation": None,
    "quotes, exact": dict(fuzzy=False, min_strength=0),
    "quotes, fuzzy": dict(fuzzy=True, min_strength=0),
    "fuzzy + strength>=4": dict(fuzzy=True, min_strength=4),
    "fuzzy + strength>=5": dict(fuzzy=True, min_strength=5),
}


def prf(pred: dict, gold: dict, ids) -> tuple[float, float, float]:
    tp = sum(pred[i] and gold[i] for i in ids)
    fp = sum(pred[i] and not gold[i] for i in ids)
    fn = sum(not pred[i] and gold[i] for i in ids)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def bootstrap(runs: list[dict], gold: dict, n: int = 1000, seed: int = 0) -> list[tuple[float, float]]:
    """95% CI for (precision, recall, F1): resample papers, and for each resampled paper pick a random run."""
    rnd, ids = random.Random(seed), list(gold)
    res = [[], [], []]
    for _ in range(n):
        pick = [(i, rnd.choice(runs)[i]) for i in (rnd.choice(ids) for _ in ids)]
        tp = sum(p and gold[i] for i, p in pick)
        fp = sum(p and not gold[i] for i, p in pick)
        fn = sum(not p and gold[i] for i, p in pick)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        for k, v in enumerate((pr, rc, 2 * pr * rc / (pr + rc) if pr + rc else 0.0)):
            res[k].append(v)
    q = lambda xs, f: sorted(xs)[int(f * (len(xs) - 1))]
    return [(q(x, 0.025), q(x, 0.975)) for x in res]


def kappa(a: dict, b: dict) -> float:
    ids = list(a)
    po = sum(a[i] == b[i] for i in ids) / len(ids)
    pa, pb = sum(a.values()) / len(ids), sum(b[i] for i in ids) / len(ids)
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def load(papers_f: str, labels_f: str) -> tuple[list, dict]:
    labels_p = EVAL / labels_f
    if not labels_p.exists():
        return [], {}
    labels = {i: v["relevant"] for i, v in json.loads(labels_p.read_text()).items()}
    papers = [p for p in json.loads((EVAL / papers_f).read_text()) if p["id"] in labels]
    return papers, labels


def evaluate(papers: list, gold: dict, col, prompt: str | None = None) -> dict:
    runs = {name: [] for name in VARIANTS}
    errors = 0
    for _ in range(REPEATS):
        scored = {}
        for p in papers:
            chunks = rag.retrieve(col, p["title"] + "\n" + p["abstract"])
            scored[p["id"]] = (p, chunks, score_paper(p, chunks, prompt=prompt))
        errors += sum("error" in s for _, _, s in scored.values())
        for name, kw in VARIANTS.items():
            runs[name].append({i: (s["relevant"] if kw is None else validate_score(p, ch, s, **kw)["relevant"])
                               for i, (p, ch, s) in scored.items()})
    out = {}
    for name, rs in runs.items():
        pt = [prf(r, gold, gold) for r in rs]
        mean = [sum(x[k] for x in pt) / len(pt) for k in range(3)]
        out[name] = (mean, bootstrap(rs, gold))
    out["_errors"] = errors
    return out


def table(title: str, gold: dict, res: dict) -> list[str]:
    n_pos = sum(gold.values())
    rows = [f"## {title}: n={len(gold)} ({n_pos} positive), scoring errors: {res['_errors']}\n",
            "| variant | precision (95% CI) | recall (95% CI) | F1 (95% CI) |", "|---|---|---|---|"]
    for name, val in res.items():
        if name != "_errors":
            mean, ci = val
            rows.append(f"| {name} | " + " | ".join(f"{mean[k]:.2f} ({ci[k][0]:.2f}-{ci[k][1]:.2f})" for k in range(3)) + " |")
    return rows + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", choices=["narrow", "wide"], default="wide")
    a = ap.parse_args()
    prompt = sc.PROMPT_NARROW if a.prompt == "narrow" else sc.PROMPT_WIDE
    col = rag.build_index()
    out = ["# Eval results", "", f"Scorer prompt: **{a.prompt}**. Mean of {REPEATS} scoring runs; CI = bootstrap over papers (1000 resamples). Small n: wide intervals.", ""]
    dev_p, dev_g = load("papers.json", "labels.json")
    out += table("DEV (owner-reviewed, used to choose settings)", dev_g, evaluate(dev_p, dev_g, col, prompt))
    ai = set(json.loads((EVAL / "ai_first_pass.json").read_text())["positive"])
    out += [f"AI first-draft vs owner final labels on DEV: Cohen's kappa = {kappa({i: i in ai for i in dev_g}, dev_g):.2f}", ""]
    test_p, test_g = load("pool.json", "labels_new.json")
    if test_g:
        out += table("TEST (fresh pool, blind owner labels, never tuned on)", test_g, evaluate(test_p, test_g, col, prompt))
    else:
        out.append("TEST: no labels yet (run `python -m agent.label`).\n")
    (EVAL / f"results_{a.prompt}.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
