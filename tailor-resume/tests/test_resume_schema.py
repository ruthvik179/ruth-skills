import copy
from pathlib import Path

import yaml

from tailor_resume.schema import collect_source_ids, load_resume_yaml, validate_resume


FIXTURE = Path(__file__).resolve().parents[1] / "config" / "resume.yaml"


def test_valid_resume_yaml_passes_validation():
    data = load_resume_yaml(FIXTURE)

    errors = validate_resume(data)

    assert errors == []


def test_collect_source_ids_includes_role_bullets_and_summary_facts():
    data = load_resume_yaml(FIXTURE)

    source_ids = collect_source_ids(data)

    assert "summary-001" in source_ids
    assert "role-001-b001" in source_ids
    assert "extra-001" in source_ids


def test_missing_required_top_level_key_fails_validation():
    data = load_resume_yaml(FIXTURE)
    broken = copy.deepcopy(data)
    broken.pop("profile")

    errors = validate_resume(broken)

    assert "missing top-level key: profile" in errors


def test_role_bullet_count_is_enforced():
    data = load_resume_yaml(FIXTURE)
    broken = copy.deepcopy(data)
    broken["experience"][0]["roles"][0]["master_bullets"] = []

    errors = validate_resume(broken)

    assert "role role-001 requires 4 bullets but has 0" in errors


def test_bullet_skill_must_exist_in_inventory_or_aliases():
    data = load_resume_yaml(FIXTURE)
    broken = copy.deepcopy(data)
    broken["experience"][0]["roles"][0]["master_bullets"][0]["skills"].append("Unknown Tool")

    errors = validate_resume(broken)

    assert "unknown skill 'Unknown Tool' in bullet role-001-b001" in errors


def test_yaml_file_is_valid_yaml():
    raw = FIXTURE.read_text(encoding="utf-8")

    parsed = yaml.safe_load(raw)

    assert isinstance(parsed, dict)
