from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_TOP_LEVEL = [
    "constraints",
    "rendering",
    "profile",
    "targeting",
    "education",
    "skills",
    "experience",
    "projects",
    "certifications",
    "extracurriculars",
]


def load_resume_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("resume YAML must contain a mapping at the top level")
    return data


def collect_skill_names(data: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    skills = data.get("skills", {})
    for group in skills.get("groups", []):
        for item in group.get("items", []):
            names.add(str(item))
    for canonical, aliases in skills.get("aliases", {}).items():
        names.add(str(canonical))
        for alias in aliases or []:
            names.add(str(alias))
    return names


def collect_source_ids(data: dict[str, Any]) -> set[str]:
    source_ids: set[str] = set()

    for fact in data.get("targeting", {}).get("summary_facts", []):
        _add_id(source_ids, fact)

    for education in data.get("education", []):
        _add_id(source_ids, education)
        for detail in education.get("details", []):
            _add_id(source_ids, detail)

    for company in data.get("experience", []):
        _add_id(source_ids, company)
        for role in company.get("roles", []):
            _add_id(source_ids, role)
            for bullet in role.get("master_bullets", []):
                _add_id(source_ids, bullet)

    for collection_name in ("projects", "certifications", "extracurriculars"):
        for item in data.get(collection_name, []):
            _add_id(source_ids, item)
            for bullet in item.get("master_bullets", []):
                _add_id(source_ids, bullet)

    return source_ids


def validate_resume(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"missing top-level key: {key}")

    if errors:
        return errors

    _validate_constraints(data, errors)
    _validate_rendering(data, errors)
    _validate_profile(data, errors)
    _validate_targeting(data, errors)
    _validate_education(data, errors)
    _validate_skills(data, errors)
    _validate_experience(data, errors)
    _validate_optional_collections(data, errors)
    _validate_bullet_skills(data, errors)

    return errors


def _add_id(source_ids: set[str], item: dict[str, Any]) -> None:
    value = item.get("id")
    if value:
        source_ids.add(str(value))


def _require_mapping(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path} must be a mapping")
        return False
    return True


def _require_list(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return False
    return True


def _require_non_empty_string(item: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key} must be a non-empty string")


def _validate_constraints(data: dict[str, Any], errors: list[str]) -> None:
    constraints = data["constraints"]
    if not _require_mapping(constraints, "constraints", errors):
        return
    max_pages = constraints.get("max_pages")
    if not isinstance(max_pages, int) or max_pages < 1:
        errors.append("constraints.max_pages must be an integer greater than 0")
    if not _require_list(constraints.get("bullet_reduction_order", []), "constraints.bullet_reduction_order", errors):
        return


def _validate_rendering(data: dict[str, Any], errors: list[str]) -> None:
    rendering = data["rendering"]
    if not _require_mapping(rendering, "rendering", errors):
        return
    if rendering.get("primary_format") != "docx":
        errors.append("rendering.primary_format must be docx")
    section_order = rendering.get("section_order")
    if _require_list(section_order, "rendering.section_order", errors):
        labels = rendering.get("section_labels", {})
        for section in section_order:
            if section not in labels:
                errors.append(f"missing rendering.section_labels entry for {section}")


def _validate_profile(data: dict[str, Any], errors: list[str]) -> None:
    profile = data["profile"]
    if not _require_mapping(profile, "profile", errors):
        return
    for key in ("name", "headline", "email", "phone", "location"):
        _require_non_empty_string(profile, key, "profile", errors)


def _validate_targeting(data: dict[str, Any], errors: list[str]) -> None:
    targeting = data["targeting"]
    if not _require_mapping(targeting, "targeting", errors):
        return
    if not _require_list(targeting.get("title_variants"), "targeting.title_variants", errors):
        return
    facts = targeting.get("summary_facts")
    if _require_list(facts, "targeting.summary_facts", errors):
        for fact in facts:
            _require_non_empty_string(fact, "id", "targeting.summary_facts[]", errors)
            _require_non_empty_string(fact, "text", f"summary fact {fact.get('id', '<missing>')}", errors)


def _validate_education(data: dict[str, Any], errors: list[str]) -> None:
    if not _require_list(data["education"], "education", errors):
        return
    for entry in data["education"]:
        path = f"education {entry.get('id', '<missing>')}"
        for key in ("id", "institution", "degree", "start", "end"):
            _require_non_empty_string(entry, key, path, errors)
        for detail in entry.get("details", []):
            detail_path = f"education detail {detail.get('id', '<missing>')}"
            _require_non_empty_string(detail, "id", detail_path, errors)
            _require_non_empty_string(detail, "text", detail_path, errors)


def _validate_skills(data: dict[str, Any], errors: list[str]) -> None:
    skills = data["skills"]
    if not _require_mapping(skills, "skills", errors):
        return
    groups = skills.get("groups")
    if not _require_list(groups, "skills.groups", errors):
        return
    for group in groups:
        group_path = f"skill group {group.get('id', '<missing>')}"
        _require_non_empty_string(group, "id", group_path, errors)
        _require_non_empty_string(group, "name", group_path, errors)
        if not _require_list(group.get("items"), f"{group_path}.items", errors):
            continue
        if not group["items"]:
            errors.append(f"{group_path}.items must not be empty")


def _validate_experience(data: dict[str, Any], errors: list[str]) -> None:
    if not _require_list(data["experience"], "experience", errors):
        return
    for company in data["experience"]:
        company_path = f"company {company.get('id', '<missing>')}"
        for key in ("id", "company", "location"):
            _require_non_empty_string(company, key, company_path, errors)
        roles = company.get("roles")
        if not _require_list(roles, f"{company_path}.roles", errors):
            continue
        for role in roles:
            role_id = role.get("id", "<missing>")
            role_path = f"role {role_id}"
            for key in ("id", "title", "start", "end"):
                _require_non_empty_string(role, key, role_path, errors)
            required = role.get("bullets_required")
            bullets = role.get("master_bullets")
            if not isinstance(required, int) or required < 0:
                errors.append(f"{role_path}.bullets_required must be an integer greater than or equal to 0")
                required = 0
            if not _require_list(bullets, f"{role_path}.master_bullets", errors):
                continue
            if role.get("include", True) and len(bullets) < required:
                errors.append(f"role {role_id} requires {required} bullets but has {len(bullets)}")
            for bullet in bullets:
                bullet_path = f"bullet {bullet.get('id', '<missing>')}"
                _require_non_empty_string(bullet, "id", bullet_path, errors)
                _require_non_empty_string(bullet, "text", bullet_path, errors)


def _validate_optional_collections(data: dict[str, Any], errors: list[str]) -> None:
    for collection_name in ("projects", "certifications", "extracurriculars"):
        collection = data[collection_name]
        if not _require_list(collection, collection_name, errors):
            continue
        for item in collection:
            item_path = f"{collection_name} item {item.get('id', '<missing>')}"
            _require_non_empty_string(item, "id", item_path, errors)
            if collection_name != "certifications":
                _require_non_empty_string(item, "text", item_path, errors)


def _validate_bullet_skills(data: dict[str, Any], errors: list[str]) -> None:
    known_skills = collect_skill_names(data)
    for company in data.get("experience", []):
        for role in company.get("roles", []):
            for bullet in role.get("master_bullets", []):
                for skill in bullet.get("skills", []):
                    if str(skill) not in known_skills:
                        errors.append(f"unknown skill '{skill}' in bullet {bullet.get('id', '<missing>')}")
    for fact in data.get("targeting", {}).get("summary_facts", []):
        for skill in fact.get("skills", []):
            if str(skill) not in known_skills:
                errors.append(f"unknown skill '{skill}' in summary fact {fact.get('id', '<missing>')}")
