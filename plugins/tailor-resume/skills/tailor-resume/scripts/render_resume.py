from __future__ import annotations

import argparse
from pathlib import Path

from tailor_resume.render import render_resume_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Render selected resume YAML to DOCX and PDF.")
    parser.add_argument("--selected", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-pages", type=int, required=True)
    args = parser.parse_args()

    metadata = render_resume_package(args.selected, args.output_dir, args.max_pages)
    print(f"wrote resume.docx and resume.pdf with {metadata['page_count']} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
