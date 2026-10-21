"""kwtk: the Kuwait Energy Toolkit command line.

    kwtk validate CONFIG.yaml [...]
    kwtk inputs import --dataset PATH    refresh inputs/dataset/ from a dataset build
    kwtk inputs verify                   check inputs/dataset/ against its manifest
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
    i = sub.add_parser("inputs", help="the dataset snapshot in inputs/dataset/")
    isub = i.add_subparsers(dest="action", required=True)
    imp = isub.add_parser("import", help="copy a local dataset build into inputs/dataset/")
    imp.add_argument("--dataset", required=True, type=Path, help="a clone of mizan-kuwait-electricity-data after `make`")
    isub.add_parser("verify", help="check every file against MANIFEST.yaml")
    args = p.parse_args()

    if args.cmd == "inputs":
        from .inputs import dataset
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
