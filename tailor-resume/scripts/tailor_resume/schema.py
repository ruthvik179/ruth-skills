from __future__ import annotations

from collections import Counter
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
    if not isinstance(skills, dict):
        return names
    groups = skills.get("groups", [])
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, dict):
                continue
            items = group.get("items", [])
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, str) and item.strip():
                    names.add(item)
    aliases = skills.get("aliases", {})
    if isinstance(aliases, dict):
        for canonical, aliases in aliases.items():
            if isinstance(canonical, str) and canonical.strip():
                names.add(canonical)
            if not isinstance(aliases, list):
                continue
            for alias in aliases:
                if isinstance(alias, str) and alias.strip():
                    names.add(alias)
    return names


def collect_source_id_counts(data: dict[str, Any]) -> Counter[str]:
    source_id_counts: Counter[str] = Counter()

    targeting = _as_mapping(data.get("targeting"))
    for fact in _as_list(targeting.get("summary_facts")):
        _count_id(source_id_counts, fact)

    for education in _as_list(data.get("education")):
        _count_id(source_id_counts, education)
        education_mapping = _as_mapping(education)
        for detail in _as_list(education_mapping.get("details")):
            _count_id(source_id_counts, detail)

    for company in _as_list(data.get("experience")):
        _count_id(source_id_counts, company)
        company_mapping = _as_mapping(company)
        for role in _as_list(company_mapping.get("roles")):
            _count_id(source_id_counts, role)
            role_mapping = _as_mapping(role)
            for bullet in _as_list(role_mapping.get("master_bullets")):
                _count_id(source_id_counts, bullet)

    for collection_name in ("projects", "certifications", "extracurriculars"):
        for item in _as_list(data.get(collection_name)):
            _count_id(source_id_counts, item)
            item_mapping = _as_mapping(item)
            for bullet in _as_list(item_mapping.get("master_bullets")):
                _count_id(source_id_counts, bullet)

    return source_id_counts


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _count_id(source_id_counts: Counter[str], item: Any) -> None:
    if not isinstance(item, dict):
        return
    value = item.get("id")
    if value:
        source_id_counts[str(value)] += 1


def _item_id(item: Any) -> str:
    if not isinstance(item, dict):
        return "<invalid>"
    return str(item.get("id", "<missing>"))


def _is_valid_skill_inventory(data: dict[str, Any]) -> bool:
    skills = data.get("skills")
    return isinstance(skills, dict) and isinstance(skills.get("groups"), list)


def _validate_skill_field(item: dict[str, Any], path: str, known_skills: set[str], errors: list[str]) -> None:
    if "skills" not in item:
        return
    skills = item["skills"]
    if not _require_list(skills, f"{path}.skills", errors):
        return
    for index, skill in enumerate(skills):
        if not isinstance(skill, str) or not skill.strip():
            errors.append(f"{path}.skills[{index}] must be a non-empty string")
            continue
        if str(skill) not in known_skills:
            errors.append(f"unknown skill '{skill}' in {path}")


def _validate_duplicate_source_ids(data: dict[str, Any], errors: list[str]) -> None:
    for source_id, count in collect_source_id_counts(data).items():
        if count > 1:
            errors.append(f"duplicate source id: {source_id}")


def collect_source_ids(data: dict[str, Any]) -> set[str]:
    return set(collect_source_id_counts(data))


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
    _validate_duplicate_source_ids(data, errors)
    _validate_skill_references(data, errors)

    return errors


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
    if not isinstance(item, dict):
        errors.append(f"{path} must be a mapping")
        return
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key} must be a non-empty string")


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_constraints(data: dict[str, Any], errors: list[str]) -> None:
    constraints = data["constraints"]
    if not _require_mapping(constraints, "constraints", errors):
        return
    max_pages = constraints.get("max_pages")
    if not _is_plain_int(max_pages) or max_pages < 1:
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
        if not _require_mapping(labels, "rendering.section_labels", errors):
            return
        for section in section_order:
            if not isinstance(section, str) or not section.strip():
                errors.append("rendering.section_order item must be a string")
                continue
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
    _require_list(targeting.get("title_variants"), "targeting.title_variants", errors)
    facts = targeting.get("summary_facts")
    if _require_list(facts, "targeting.summary_facts", errors):
        for index, fact in enumerate(facts):
            if not _require_mapping(fact, f"targeting.summary_facts[{index}]", errors):
                continue
            _require_non_empty_string(fact, "id", f"targeting.summary_facts[{index}]", errors)
            _require_non_empty_string(fact, "text", f"summary fact {_item_id(fact)}", errors)


def _validate_education(data: dict[str, Any], errors: list[str]) -> None:
    if not _require_list(data["education"], "education", errors):
        return
    for index, entry in enumerate(data["education"]):
        if not _require_mapping(entry, f"education[{index}]", errors):
            continue
        path = f"education {_item_id(entry)}"
        for key in ("id", "institution", "degree", "start", "end"):
            _require_non_empty_string(entry, key, path, errors)
        details = entry.get("details", [])
        if not _require_list(details, f"{path}.details", errors):
            continue
        for detail_index, detail in enumerate(details):
            if not _require_mapping(detail, f"{path}.details[{detail_index}]", errors):
                continue
            detail_path = f"education detail {_item_id(detail)}"
            _require_non_empty_string(detail, "id", detail_path, errors)
            _require_non_empty_string(detail, "text", detail_path, errors)


def _validate_skills(data: dict[str, Any], errors: list[str]) -> None:
    skills = data["skills"]
    if not _require_mapping(skills, "skills", errors):
        return
    aliases = skills.get("aliases", {})
    if _require_mapping(aliases, "skills.aliases", errors):
        for canonical, aliases_for_canonical in aliases.items():
            alias_path = f"skills.aliases.{canonical}"
            if not _require_list(aliases_for_canonical, alias_path, errors):
                continue
            for index, alias in enumerate(aliases_for_canonical):
                if not isinstance(alias, str) or not alias.strip():
                    errors.append(f"{alias_path}[{index}] must be a non-empty string")
    groups = skills.get("groups")
    if not _require_list(groups, "skills.groups", errors):
        return
    for index, group in enumerate(groups):
        if not _require_mapping(group, f"skills.groups[{index}]", errors):
            continue
        group_path = f"skill group {_item_id(group)}"
        _require_non_empty_string(group, "id", group_path, errors)
        _require_non_empty_string(group, "name", group_path, errors)
        if not _require_list(group.get("items"), f"{group_path}.items", errors):
            continue
        if not group["items"]:
            errors.append(f"{group_path}.items must not be empty")
        for item_index, item in enumerate(group["items"]):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{group_path}.items[{item_index}] must be a non-empty string")


def _validate_experience(data: dict[str, Any], errors: list[str]) -> None:
    if not _require_list(data["experience"], "experience", errors):
        return
    for company_index, company in enumerate(data["experience"]):
        if not _require_mapping(company, f"experience[{company_index}]", errors):
            continue
        company_path = f"company {_item_id(company)}"
        for key in ("id", "company", "location"):
            _require_non_empty_string(company, key, company_path, errors)
        roles = company.get("roles")
        if not _require_list(roles, f"{company_path}.roles", errors):
            continue
        for role_index, role in enumerate(roles):
            if not _require_mapping(role, f"{company_path}.roles[{role_index}]", errors):
                continue
            role_id = _item_id(role)
            role_path = f"role {role_id}"
            for key in ("id", "title", "start", "end"):
                _require_non_empty_string(role, key, role_path, errors)
            required = role.get("bullets_required")
            bullets = role.get("master_bullets")
            if not _is_plain_int(required) or required < 0:
                errors.append(f"{role_path}.bullets_required must be an integer greater than or equal to 0")
                required = 0
            if not _require_list(bullets, f"{role_path}.master_bullets", errors):
                continue
            if role.get("include", True) and len(bullets) < required:
                errors.append(f"role {role_id} requires {required} bullets but has {len(bullets)}")
            for bullet_index, bullet in enumerate(bullets):
                if not _require_mapping(bullet, f"{role_path}.master_bullets[{bullet_index}]", errors):
                    continue
                bullet_path = f"bullet {_item_id(bullet)}"
                _require_non_empty_string(bullet, "id", bullet_path, errors)
                _require_non_empty_string(bullet, "text", bullet_path, errors)


def _validate_optional_collections(data: dict[str, Any], errors: list[str]) -> None:
    for collection_name in ("projects", "certifications", "extracurriculars"):
        collection = data[collection_name]
        if not _require_list(collection, collection_name, errors):
            continue
        for index, item in enumerate(collection):
            if not _require_mapping(item, f"{collection_name}[{index}]", errors):
                continue
            item_path = f"{collection_name} item {_item_id(item)}"
            _require_non_empty_string(item, "id", item_path, errors)
            if collection_name != "certifications":
                _require_non_empty_string(item, "text", item_path, errors)
            bullets = item.get("master_bullets", [])
            if not _require_list(bullets, f"{item_path}.master_bullets", errors):
                continue
            for bullet_index, bullet in enumerate(bullets):
                if not _require_mapping(bullet, f"{item_path}.master_bullets[{bullet_index}]", errors):
                    continue
                bullet_path = f"{item_path} bullet {_item_id(bullet)}"
                _require_non_empty_string(bullet, "id", bullet_path, errors)
                _require_non_empty_string(bullet, "text", bullet_path, errors)


def _validate_skill_references(data: dict[str, Any], errors: list[str]) -> None:
    if not _is_valid_skill_inventory(data):
        return
    known_skills = collect_skill_names(data)

    targeting = _as_mapping(data.get("targeting"))
    for fact in _as_list(targeting.get("summary_facts")):
        if isinstance(fact, dict):
            _validate_skill_field(fact, f"summary fact {_item_id(fact)}", known_skills, errors)

    for education in _as_list(data.get("education")):
        education_mapping = _as_mapping(education)
        for detail in _as_list(education_mapping.get("details")):
            if isinstance(detail, dict):
                _validate_skill_field(detail, f"education detail {_item_id(detail)}", known_skills, errors)

    for company in _as_list(data.get("experience")):
        company_mapping = _as_mapping(company)
        for role in _as_list(company_mapping.get("roles")):
            role_mapping = _as_mapping(role)
            for bullet in _as_list(role_mapping.get("master_bullets")):
                if isinstance(bullet, dict):
                    _validate_skill_field(bullet, f"bullet {_item_id(bullet)}", known_skills, errors)

    for collection_name in ("projects", "certifications", "extracurriculars"):
        for item in _as_list(data.get(collection_name)):
            if not isinstance(item, dict):
                continue
            item_path = f"{collection_name} item {_item_id(item)}"
            _validate_skill_field(item, item_path, known_skills, errors)
            for bullet in _as_list(item.get("master_bullets")):
                if isinstance(bullet, dict):
                    _validate_skill_field(bullet, f"{item_path} bullet {_item_id(bullet)}", known_skills, errors)
