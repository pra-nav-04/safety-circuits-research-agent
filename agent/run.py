"""One command: python -m agent.run --max-papers 15"""
import argparse
import datetime
import json
from pathlib import Path

from agent.graph import build_graph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-papers", type=int, default=15)
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()

    state = build_graph().invoke({"max_papers": a.max_papers})

    out = Path(a.out) / datetime.date.today().isoformat()
    (out / "drafts").mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(json.dumps(state["papers"], indent=2))
    (out / "scores.json").write_text(json.dumps(state["scores"], indent=2))
    for pid, text in state.get("drafts", {}).items():
        (out / "drafts" / f"{pid.replace('/', '_')}.md").write_text(text)
    rel = sum(s["relevant"] for s in state["scores"].values())
    print(f"{len(state['papers'])} papers, {rel} relevant, {len(state.get('drafts', {}))} drafts -> {out}")


if __name__ == "__main__":
    main()
