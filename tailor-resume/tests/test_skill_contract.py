from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def test_skill_requires_user_provided_resume_yaml_instead_of_bundled_config():
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata_text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert not (SKILL_ROOT / "config" / "resume.yaml").exists()
    assert "config/resume.yaml" not in skill_text
    assert "<resume-yaml>" in skill_text
    assert "user-provided resume YAML" in skill_text
    assert "resume YAML" in metadata_text
