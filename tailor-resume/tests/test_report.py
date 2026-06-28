from tailor_resume.report import build_report_markdown


def test_report_contains_required_sections():
    selected = {
        "job": {"url": "https://example.com/job", "title": "Data Scientist", "company": "Example Employer"},
        "summary": {"text": "Summary", "source_ids": ["summary-001"]},
        "skills": {"groups": [{"name": "Programming", "items": ["Python"]}]},
        "experience": [
            {
                "company": "Koch Ag & Energy Solutions",
                "roles": [
                    {
                        "title": "Data Scientist",
                        "bullets": [
                            {
                                "text": "Built an optimization platform.",
                                "source_ids": ["role-001-b001"],
                                "rationale": "Matches optimization requirement.",
                            }
                        ],
                    }
                ],
            }
        ],
        "gap_notes": ["No direct Kubernetes evidence in source YAML."],
        "ats_checklist": ["One-column layout."],
    }
    scrape = {"status": "success", "fallback_required": False, "message": "scraped with requests"}
    render = {"page_count": 1, "pdf_text_check": "pass"}

    markdown = build_report_markdown(selected, scrape, render)

    assert "# Tailored Resume Report" in markdown
    assert "## Job" in markdown
    assert "## Scrape Status" in markdown
    assert "## Bullet Rationale" in markdown
    assert "## Gap Notes" in markdown
    assert "## ATS Checklist" in markdown
    assert "role-001-b001" in markdown
