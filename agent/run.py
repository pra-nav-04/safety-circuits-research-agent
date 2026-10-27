"""One command: python -m agent.run --max-papers 15"""
import argparse
import datetime
import json
import re
import sys
import time
from pathlib import Path

from agent.graph import build_graph
from agent.ops import acquire_lock, digest, health_check, log_run, release_lock


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-papers", type=int, default=15)
    ap.add_argument("--out", default="runs")
    ap.add_argument("--no-validate", action="store_true", help="skip the grounding check (higher recall, more false positives)")
    ap.add_argument("--no-state", action="store_true", help="ignore state/seen.json and rescore everything")
    a = ap.parse_args()

    ok_, msg = health_check()
    if not ok_:
        print(f"not running: {msg}", file=sys.stderr)
        log_run({"time": datetime.datetime.now().isoformat(timespec="seconds"), "status": "skipped", "reason": msg})
        sys.exit(1)
    if not acquire_lock():
        print("not running: another run holds state/run.lock", file=sys.stderr)
        sys.exit(0)
    try:
        run(a)
    finally:
        release_lock()


def run(a):
    t0 = time.time()
    seen_file = Path("state/seen.json")
    seen = [] if a.no_state or not seen_file.exists() else json.loads(seen_file.read_text())
    state = build_graph().invoke({"max_papers": a.max_papers, "seen": seen, "validate": not a.no_validate})
    if not state["papers"]:
        print(f"0 new papers (already seen: {len(seen)})")
        log_run({"time": datetime.datetime.now().isoformat(timespec="seconds"), "status": "ok", "papers": 0})
        return

    out = Path(a.out) / datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")   # never overwrite an earlier run
    (out / "drafts").mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(json.dumps(state["papers"], indent=2))
    (out / "scores.json").write_text(json.dumps(state["scores"], indent=2))
    for pid, text in state.get("drafts", {}).items():
        (out / "drafts" / f"{re.sub(r'[^A-Za-z0-9._-]+', '_', pid)}.md").write_text(text)
    ok = [i for i, sc in state["scores"].items() if "error" not in sc]   # failed ones are retried next run
    seen_file.parent.mkdir(exist_ok=True)
    seen_file.write_text(json.dumps(sorted(set(seen) | set(ok))))
    rel = sum(s["relevant"] for s in state["scores"].values())
    md = digest(state["papers"], state["scores"], state.get("drafts", {}), out.name)
    (out / "digest.md").write_text(md)
    Path(a.out, "latest.md").write_text(md)
    log_run({"time": datetime.datetime.now().isoformat(timespec="seconds"), "status": "ok", "papers": len(state["papers"]),
             "relevant": rel, "errors": len(state["papers"]) - len(ok), "seconds": round(time.time() - t0), "dir": str(out)})
    print(f"{len(state['papers'])} papers, {rel} relevant, {len(state.get('drafts', {}))} drafts -> {out}")


if __name__ == "__main__":
    main()
