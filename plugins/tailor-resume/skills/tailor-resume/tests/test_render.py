from pathlib import Path

import yaml

from tailor_resume.render import extract_pdf_text, render_resume_package


def _selected():
    return {
        "job": {"url": "https://example.com/job", "title": "Data Scientist", "company": "Example Employer"},
        "summary": {
            "text": "Data Scientist experienced in optimization and data engineering.",
            "source_ids": ["summary-001"],
        },
        "skills": {"groups": [{"name": "Programming", "items": ["Python", "SQL"]}]},
        "experience": [
            {
                "company": "Example Industrial Analytics",
                "location": "Wichita, KS",
                "roles": [
                    {
                        "title": "Data Scientist",
                        "start": "2024-05",
                        "end": "Present",
                        "bullets": [
                            {
                                "text": "Built an optimization platform.",
                                "source_ids": ["role-001-b001"],
                                "rationale": "Relevant.",
                            }
                        ],
                    }
                ],
            }
        ],
        "education": [
            {
                "text": "Oklahoma State University - Master's in Business Analytics and Data Science",
                "source_ids": ["edu-001"],
            }
        ],
        "projects": [],
        "certifications": [],
        "extracurriculars": [],
        "gap_notes": [],
        "ats_checklist": [],
    }


def test_render_resume_package_creates_docx_pdf_and_metadata(tmp_path):
    selected_path = tmp_path / "selected-resume.yaml"
    selected_path.write_text(yaml.safe_dump(_selected(), sort_keys=False), encoding="utf-8")

    metadata = render_resume_package(selected_path, tmp_path, max_pages=2)

    assert (tmp_path / "resume.docx").exists()
    assert (tmp_path / "resume.pdf").exists()
    assert (tmp_path / "render.yaml").exists()
    assert metadata["page_count"] >= 1
    assert metadata["page_count"] <= 2
    assert metadata["pdf_text_check"] == "pass"


def test_extract_pdf_text_returns_visible_resume_text(tmp_path):
    selected_path = tmp_path / "selected-resume.yaml"
    selected_path.write_text(yaml.safe_dump(_selected(), sort_keys=False), encoding="utf-8")

    render_resume_package(selected_path, tmp_path, max_pages=2)
    text = extract_pdf_text(Path(tmp_path / "resume.pdf"))

    assert "Data Scientist" in text
    assert "Example Industrial Analytics" in text
