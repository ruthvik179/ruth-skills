import yaml

from tailor_resume.report import write_report
from tailor_resume.render import render_resume_package
from tailor_resume.scrape import ScrapeResult, save_scrape_artifacts


def test_end_to_end_artifacts_are_created(tmp_path):
    selected = {
        "job": {"url": "https://example.com/job", "title": "Data Scientist", "company": "Example Employer", "location": "Remote"},
        "summary": {"text": "Data Scientist with production decision-system experience.", "source_ids": ["summary-001"]},
        "skills": {"groups": [{"name": "Programming", "items": ["Python", "SQL"]}, {"name": "Optimization", "items": ["Gurobi"]}]},
        "experience": [
            {
                "company": "Example Industrial Analytics",
                "location": "Wichita, KS",
                "roles": [
                    {
                        "role_id": "role-001",
                        "title": "Data Scientist",
                        "start": "2024-05",
                        "end": "Present",
                        "bullets": [
                            {
                                "text": "Built a plant-level optimization platform for contract allocation decisions.",
                                "source_ids": ["role-001-b001"],
                                "rationale": "Direct match for optimization and decision-system requirements.",
                            }
                        ],
                    }
                ],
            }
        ],
        "education": [{"text": "Oklahoma State University - Master's in Business Analytics and Data Science", "source_ids": ["edu-001"]}],
        "projects": [],
        "certifications": [],
        "extracurriculars": [],
        "gap_notes": ["No direct Kubernetes evidence found in resume YAML."],
        "ats_checklist": ["One-column layout.", "No icons or sidebars."],
    }
    selected_path = tmp_path / "selected-resume.yaml"
    selected_path.write_text(yaml.safe_dump(selected, sort_keys=False), encoding="utf-8")
    scrape = ScrapeResult(
        url="https://example.com/job",
        status="success",
        raw_html="<html><body>Data Scientist job</body></html>",
        cleaned_text="Data Scientist job requiring optimization and Python.",
        fallback_required=False,
        message="fixture scrape",
    )

    save_scrape_artifacts(scrape, tmp_path)
    render_resume_package(selected_path, tmp_path, max_pages=2)
    write_report(selected_path, tmp_path / "scrape.yaml", tmp_path / "render.yaml", tmp_path / "REPORT.md")

    assert (tmp_path / "job.txt").exists()
    assert (tmp_path / "scrape.yaml").exists()
    assert (tmp_path / "resume.docx").exists()
    assert (tmp_path / "resume.pdf").exists()
    assert (tmp_path / "render.yaml").exists()
    assert (tmp_path / "REPORT.md").exists()
    assert "No direct Kubernetes evidence" in (tmp_path / "REPORT.md").read_text(encoding="utf-8")
