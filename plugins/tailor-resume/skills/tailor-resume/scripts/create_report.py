from __future__ import annotations

import argparse
from pathlib import Path

from tailor_resume.report import write_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Create REPORT.md for a tailored resume package.")
    parser.add_argument("--selected", type=Path, required=True)
    parser.add_argument("--scrape", type=Path, required=True)
    parser.add_argument("--render", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    write_report(args.selected, args.scrape, args.render, args.output)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
