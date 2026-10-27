"""Human gate: python -m agent.review [run_dir]. Shows each draft with its evidence; y copies it to approved/.
Only approved drafts are ever candidates to send. Nothing is sent by this program."""
import json
import shutil
import sys
from pathlib import Path


def main():
    runs = Path("runs")
    run = Path(sys.argv[1]) if len(sys.argv) > 1 else max((d for d in runs.iterdir() if d.is_dir()), key=lambda d: d.name)
    scores = json.loads((run / "scores.json").read_text())
    papers = {p["id"]: p for p in json.loads((run / "records.json").read_text())}
    (run / "approved").mkdir(exist_ok=True)
    for f in sorted((run / "drafts").glob("*.md")):
        pid = next((i for i in scores if f.stem == i.replace(":", "_").replace("/", "_")), None)
        s = scores.get(pid, {})
        print("=" * 80, f"\n{papers[pid]['title'] if pid else f.stem}\nmatched {s.get('matched_hypothesis')}: {s.get('reason')}")
        print(f"paper quote:   {s.get('abstract_quote')}\nproject quote: {s.get('evidence_quote')}\n\n{f.read_text()}\n")
        if input("approve this draft? [y/N] ").strip().lower() == "y":
            shutil.copy(f, run / "approved" / f.name)
            print("approved")
    print(f"approved drafts: {len(list((run / 'approved').glob('*.md')))} in {run / 'approved'}")


if __name__ == "__main__":
    main()
