from pathlib import Path

from tailor_resume.schema import load_resume_yaml
from tailor_resume.selected import validate_selected_resume


RESUME = Path(__file__).resolve().parent / "fixtures" / "resume.yaml"


def _valid_selected():
    return {
        "job": {
            "url": "https://example.com/job",
            "title": "Data Scientist",
            "company": "Example Employer",
        },
        "summary": {
            "text": "Data Scientist experienced in decision systems and industrial analytics.",
            "source_ids": ["summary-001", "summary-002"],
        },
        "skills": {
            "groups": [
                {"name": "Programming", "items": ["Python", "SQL"]},
                {"name": "ML/AI", "items": ["RAG", "Vector Search"]},
            ]
        },
        "experience": [
            {
                "company_id": "company-001",
                "company": "Example Analytics Co",
                "location": "Wichita, KS",
                "roles": [
                    {
                        "role_id": "role-001",
                        "title": "Data Scientist",
                        "start": "2024-05",
                        "end": "Present",
                        "bullets": [
                            {
                                "text": "Built an optimization platform for plant-level contract allocation.",
                                "source_ids": ["role-001-b001"],
                                "rationale": "Matches optimization and decision-system requirements.",
                            }
                        ],
                    }
                ],
            }
        ],
        "education": [
            {
                "source_ids": ["edu-001"],
                "text": "Example University - Master's in Analytics",
            }
        ],
        "projects": [],
        "certifications": [],
        "extracurriculars": [
            {
                "source_ids": ["extra-001"],
                "text": "President, Entrepreneurship Development Cell.",
            }
        ],
        "gap_notes": ["No direct Kubernetes experience found in source YAML."],
        "ats_checklist": ["Uses one-column layout.", "Avoids icons and text boxes."],
    }


def test_valid_selected_resume_passes():
    resume = load_resume_yaml(RESUME)

    errors = validate_selected_resume(_valid_selected(), resume)

    assert errors == []


def test_unknown_source_id_fails():
    resume = load_resume_yaml(RESUME)
    selected = _valid_selected()
    selected["summary"]["source_ids"] = ["missing-id"]

    errors = validate_selected_resume(selected, resume)

    assert "unknown source id 'missing-id' in summary" in errors


def test_bullet_without_provenance_fails():
    resume = load_resume_yaml(RESUME)
    selected = _valid_selected()
    selected["experience"][0]["roles"][0]["bullets"][0]["source_ids"] = []

    errors = validate_selected_resume(selected, resume)

    assert "experience bullet must include at least one source id" in errors


def test_missing_required_selected_sections_fail():
    resume = load_resume_yaml(RESUME)
    selected = _valid_selected()
    selected.pop("projects")
    selected.pop("ats_checklist")

    errors = validate_selected_resume(selected, resume)

    assert "missing top-level key: projects" in errors
    assert "missing top-level key: ats_checklist" in errors


def test_job_requires_url_title_and_company():
    resume = load_resume_yaml(RESUME)
    selected = _valid_selected()
    selected["job"].pop("company")

    errors = validate_selected_resume(selected, resume)

    assert "job.company must be a non-empty string" in errors
