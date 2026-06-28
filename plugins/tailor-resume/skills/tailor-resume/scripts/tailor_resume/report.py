from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def build_report_markdown(selected: dict[str, Any], scrape: dict[str, Any], render: dict[str, Any]) -> str:
    job = selected.get("job", {})
    lines: list[str] = [
        "# Tailored Resume Report",
        "",
        "## Job",
        "",
        f"- URL: {job.get('url', '')}",
        f"- Company: {job.get('company', '')}",
        f"- Role: {job.get('title', '')}",
        f"- Location: {job.get('location', '')}",
        "",
        "## Scrape Status",
        "",
        f"- Status: {scrape.get('status', '')}",
        f"- Fallback required: {str(scrape.get('fallback_required', False)).lower()}",
        f"- Message: {scrape.get('message', '')}",
        "",
        "## Selected Summary",
        "",
        selected.get("summary", {}).get("text", ""),
        "",
        "## Selected Skills",
        "",
    ]

    for group in selected.get("skills", {}).get("groups", []):
        items = ", ".join(group.get("items", []))
        lines.append(f"- {group.get('name', '')}: {items}")

    lines.extend(["", "## Bullet Rationale", ""])
    for company in selected.get("experience", []):
        lines.append(f"### {company.get('company', '')}")
        lines.append("")
        for role in company.get("roles", []):
            lines.append(f"#### {role.get('title', '')}")
            lines.append("")
            for bullet in role.get("bullets", []):
                source_ids = ", ".join(bullet.get("source_ids", []))
                lines.append(f"- Resume bullet: {bullet.get('text', '')}")
                lines.append(f"  Source IDs: {source_ids}")
                lines.append(f"  Rationale: {bullet.get('rationale', '')}")
        lines.append("")

    lines.extend(["## Gap Notes", ""])
    gap_notes = selected.get("gap_notes", [])
    lines.extend([f"- {note}" for note in gap_notes] or ["- None recorded."])

    lines.extend(["", "## ATS Checklist", ""])
    ats_items = selected.get("ats_checklist", [])
    lines.extend([f"- {item}" for item in ats_items] or ["- One-column layout.", "- DOCX generated as primary format."])

    lines.extend(
        [
            "",
            "## Render Results",
            "",
            f"- Page count: {render.get('page_count', '')}",
            f"- PDF text check: {render.get('pdf_text_check', '')}",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    selected_path: str | Path,
    scrape_path: str | Path,
    render_path: str | Path,
    output_path: str | Path,
) -> None:
    selected = yaml.safe_load(Path(selected_path).read_text(encoding="utf-8"))
    scrape = yaml.safe_load(Path(scrape_path).read_text(encoding="utf-8"))
    render = yaml.safe_load(Path(render_path).read_text(encoding="utf-8"))
    markdown = build_report_markdown(selected, scrape, render)
    Path(output_path).write_text(markdown, encoding="utf-8")
