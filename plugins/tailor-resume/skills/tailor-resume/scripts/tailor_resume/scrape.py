from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import requests
import yaml
from bs4 import BeautifulSoup


MIN_CLEAN_TEXT_CHARS = 500


@dataclass(frozen=True)
class ScrapeResult:
    url: str
    status: str
    raw_html: str
    cleaned_text: str
    fallback_required: bool
    message: str


def clean_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    useful = [line for line in lines if line]
    return "\n".join(useful)


def scrape_job_url(url: str, timeout: int = 20) -> ScrapeResult:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; tailor-resume-skill/0.1)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except Exception as exc:
        return ScrapeResult(
            url=url,
            status="failed",
            raw_html="",
            cleaned_text="",
            fallback_required=True,
            message=f"request failed: {exc}",
        )

    raw_html = response.text
    cleaned = clean_html_text(raw_html)
    if len(cleaned) < MIN_CLEAN_TEXT_CHARS:
        return ScrapeResult(
            url=url,
            status="thin",
            raw_html=raw_html,
            cleaned_text=cleaned,
            fallback_required=True,
            message=f"cleaned text has {len(cleaned)} characters; ask for pasted text, saved HTML, or PDF",
        )

    return ScrapeResult(
        url=url,
        status="success",
        raw_html=raw_html,
        cleaned_text=cleaned,
        fallback_required=False,
        message="scraped with requests and BeautifulSoup",
    )


def save_scrape_artifacts(result: ScrapeResult, output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    if result.raw_html:
        (output_path / "job-raw.html").write_text(result.raw_html, encoding="utf-8")
    (output_path / "job.txt").write_text(result.cleaned_text, encoding="utf-8")
    metadata = {
        "url": result.url,
        "status": result.status,
        "fallback_required": result.fallback_required,
        "message": result.message,
    }
    (output_path / "scrape.yaml").write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
