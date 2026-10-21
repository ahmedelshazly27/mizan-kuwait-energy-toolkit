"""kwtk: the Kuwait Energy Toolkit command line.

    kwtk validate CONFIG.yaml [...]
"""

import argparse
import sys

from .config.validate import validate


def main() -> None:
    p = argparse.ArgumentParser(prog="kwtk", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check plant configurations against the schema")
    v.add_argument("files", nargs="+")
    args = p.parse_args()
    bad = 0
    for f in args.files:
        r = validate(f)
        print(f"{f}\n" + "\n".join("  " + line for line in r.text().splitlines()))
        bad += not r.ok
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
