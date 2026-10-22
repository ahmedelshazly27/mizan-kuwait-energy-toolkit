"""kwtk: the Kuwait Energy Toolkit command line.

    kwtk validate CONFIG.yaml [...]
    kwtk evaluate CONFIG.yaml            simulate and cost a plant; writes results/<id>/
    kwtk compare A.yaml B.yaml [...]     evaluate several plants and print them side by side
    kwtk inputs import --dataset PATH    refresh inputs/dataset/ from a dataset build
    kwtk inputs verify                   check inputs/dataset/ against its manifest
    kwtk inputs demand                   rebuild the hourly demand reconstruction
"""

import argparse
import sys
from pathlib import Path

from .config.validate import validate


def main() -> None:
    p = argparse.ArgumentParser(prog="kwtk", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check plant configurations against the schema")
    v.add_argument("files", nargs="+")
    ev = sub.add_parser("evaluate", help="simulate and cost a plant configuration")
    ev.add_argument("file")
    cm = sub.add_parser("compare", help="evaluate several configurations side by side")
    cm.add_argument("files", nargs="+")
    i = sub.add_parser("inputs", help="the dataset snapshot in inputs/dataset/")
    isub = i.add_subparsers(dest="action", required=True)
    imp = isub.add_parser("import", help="copy a local dataset build into inputs/dataset/")
    imp.add_argument("--dataset", required=True, type=Path, help="a clone of mizan-kuwait-electricity-data after `make`")
    isub.add_parser("verify", help="check every file against MANIFEST.yaml")
    isub.add_parser("demand", help="rebuild inputs/demand/ (hourly gross load, a reconstruction)")
    args = p.parse_args()

    if args.cmd in ("evaluate", "compare"):
        from .plant import report
        from .plant.evaluate import evaluate
        from .plant.resolve import OpenAssumption
        try:
            runs = [evaluate(f) for f in ([args.file] if args.cmd == "evaluate" else args.files)]
        except (OpenAssumption, ValueError) as e:
            sys.exit(f"cannot evaluate: {e}")
        for run in runs:
            d = report.write(run)
            for w in run["result"]["warnings"]:
                print(f"warning: {w}")
            unv = run["result"]["unverified_inputs"]
            if unv:
                print(f"note: {len(unv)} inputs rest on sources that could not be verified: {', '.join(unv)}")
            print(f"{run['result']['id']}: results in {d}")
        print(report.compare([run["result"] for run in runs]).round(3).to_string())
        return

    if args.cmd == "inputs":
        from .inputs import dataset
        if args.action == "demand":
            from .inputs import demand
            m = demand.build()
            for v in m["validation_peak_days"]:
                print(f"held-out {v['day']}: MAPE {v['mape']:.1%}, worst hour {v['max_abs_error']:.1%}")
            return
        if args.action == "import":
            m = dataset.import_snapshot(args.dataset)
            print(f"imported dataset commit {m['commit'][:12]}: {', '.join(m['files'])}")
            return
        problems = dataset.verify()
        print("\n".join(problems) if problems else "inputs/dataset/ matches MANIFEST.yaml")
        sys.exit(1 if problems else 0)

    bad = 0
    for f in args.files:
        r = validate(f)
        print(f"{f}\n" + "\n".join("  " + line for line in r.text().splitlines()))
        bad += not r.ok
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
