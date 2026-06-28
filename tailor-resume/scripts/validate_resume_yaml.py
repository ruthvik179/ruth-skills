from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tailor_resume.schema import load_resume_yaml, validate_resume


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a tailor-resume YAML source file.")
    parser.add_argument("resume_yaml", type=Path)
    args = parser.parse_args()

    try:
        data = load_resume_yaml(args.resume_yaml)
    except Exception as exc:
        print(f"ERROR: could not read {args.resume_yaml}: {exc}", file=sys.stderr)
        return 2

    errors = validate_resume(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.resume_yaml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
