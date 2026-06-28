from __future__ import annotations

from typing import Any

from tailor_resume.schema import collect_source_ids


REQUIRED_TOP_LEVEL = (
    "job",
    "summary",
    "skills",
    "experience",
    "education",
    "projects",
    "certifications",
    "extracurriculars",
    "gap_notes",
    "ats_checklist",
)


def validate_selected_resume(selected: dict[str, Any], resume: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source_ids = collect_source_ids(resume)

    if not isinstance(selected, dict):
        return ["selected resume must be a mapping"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in selected:
            errors.append(f"missing top-level key: {key}")

    for key in ("job", "summary", "skills"):
        if key in selected:
            _validate_required_mapping(selected, key, errors)

    job = selected.get("job", {})
    if isinstance(job, dict):
        for key in ("url", "title", "company"):
            if not _non_empty_string(job.get(key)):
                errors.append(f"job.{key} must be a non-empty string")

    summary = selected.get("summary", {})
    if isinstance(summary, dict):
        _validate_source_list(summary.get("source_ids"), "summary", source_ids, errors)
        if not _non_empty_string(summary.get("text")):
            errors.append("summary.text must be a non-empty string")

    if "skills" in selected:
        _validate_skills(selected.get("skills", {}), errors)
    if "experience" in selected:
        _validate_experience(selected.get("experience", []), source_ids, errors)

    for section_name in ("education", "projects", "certifications", "extracurriculars"):
        if section_name in selected:
            _validate_sourced_items(selected.get(section_name, []), section_name, source_ids, errors)

    for field in ("gap_notes", "ats_checklist"):
        if field in selected and not isinstance(selected[field], list):
            errors.append(f"{field} must be a list")

    return errors


def _validate_required_mapping(data: dict[str, Any], key: str, errors: list[str]) -> None:
    value = data.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be a mapping")


def _validate_source_list(value: Any, path: str, known_ids: set[str], errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path} must include at least one source id")
        return
    for source_id in value:
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"{path} source ids must be non-empty strings")
            continue
        if source_id not in known_ids:
            errors.append(f"unknown source id '{source_id}' in {path}")


def _validate_skills(skills: Any, errors: list[str]) -> None:
    if not isinstance(skills, dict):
        return
    groups = skills.get("groups")
    if not isinstance(groups, list):
        errors.append("skills.groups must be a list")
        return
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            errors.append(f"skills.groups[{index}] must be a mapping")
            continue
        if not _non_empty_string(group.get("name")):
            errors.append(f"skills.groups[{index}].name must be a non-empty string")
        items = group.get("items")
        if not isinstance(items, list):
            errors.append(f"skills.groups[{index}].items must be a list")
            continue
        for item_index, item in enumerate(items):
            if not _non_empty_string(item):
                errors.append(f"skills.groups[{index}].items[{item_index}] must be a non-empty string")


def _validate_experience(experience: Any, known_ids: set[str], errors: list[str]) -> None:
    if not isinstance(experience, list):
        errors.append("experience must be a list")
        return
    for company_index, company in enumerate(experience):
        if not isinstance(company, dict):
            errors.append(f"experience[{company_index}] must be a mapping")
            continue
        roles = company.get("roles")
        if not isinstance(roles, list):
            errors.append(f"experience[{company_index}].roles must be a list")
            continue
        for role_index, role in enumerate(roles):
            if not isinstance(role, dict):
                errors.append(f"experience[{company_index}].roles[{role_index}] must be a mapping")
                continue
            bullets = role.get("bullets", [])
            if not isinstance(bullets, list):
                errors.append(f"role {role.get('role_id', '<missing>')}.bullets must be a list")
                continue
            if not bullets:
                errors.append(f"role {role.get('role_id', '<missing>')} must include at least one bullet")
            for bullet in bullets:
                if not isinstance(bullet, dict):
                    errors.append("experience bullet must be a mapping")
                    continue
                source_list = bullet.get("source_ids")
                if not source_list:
                    errors.append("experience bullet must include at least one source id")
                    continue
                _validate_source_list(source_list, "experience bullet", known_ids, errors)
                if not _non_empty_string(bullet.get("text")):
                    errors.append("experience bullet text must be a non-empty string")


def _validate_sourced_items(items: Any, section_name: str, known_ids: set[str], errors: list[str]) -> None:
    if section_name not in ("education", "projects", "certifications", "extracurriculars"):
        return
    if items is None:
        return
    if not isinstance(items, list):
        errors.append(f"{section_name} must be a list")
        return
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{section_name}[{index}] must be a mapping")
            continue
        _validate_source_list(item.get("source_ids"), section_name, known_ids, errors)
        if not _non_empty_string(item.get("text")):
            errors.append(f"{section_name}[{index}].text must be a non-empty string")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
