from __future__ import annotations

import argparse
from pathlib import Path

from tailor_resume.scrape import save_scrape_artifacts, scrape_job_url


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape a job posting into raw and cleaned artifacts.")
    parser.add_argument("url")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    result = scrape_job_url(args.url)
    save_scrape_artifacts(result, args.output_dir)
    print(f"{result.status}: {result.message}")
    return 1 if result.fallback_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
