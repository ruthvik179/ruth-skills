---
name: tailor-resume
description: Generate job-tailored resume packages from a complete YAML resume source of truth. Use when the user provides a job posting URL or pasted job description and wants a tailored resume, ATS checklist, gap notes, rationale report, DOCX resume, PDF resume, or provenance-backed resume rewrite using a master bullet and skills bank.
---

# Tailor Resume

Create a job-specific resume package from `config/resume.yaml` and a job posting.

## Inputs

- Job URL from the user.
- `config/resume.yaml` as the source of truth.
- Pasted job text, saved HTML, or PDF when scraping fails or produces thin text.

## Workflow

1. Create a new output folder under `outputs/<company>-<role>-<date>/`. Add a suffix when the folder already exists.
2. Run `scripts/scrape_job.py <url> --output-dir <output-folder>`.
3. If scraping fails or reports `fallback_required: true`, ask the user for pasted job text, saved HTML, or PDF. Save the fallback content as `job.txt` and record the fallback in `scrape.yaml`.
4. Run `scripts/validate_resume_yaml.py config/resume.yaml`.
5. Analyze `job.txt` for required skills, preferred skills, responsibilities, seniority, domain terms, repeated keywords, and ATS-relevant language.
6. Select source-backed summary facts, skills, education details, experience bullets, and extracurriculars from `config/resume.yaml`.
7. Rewrite selected bullets using job language while preserving factual claims.
8. Write `selected-resume.yaml` using `references/selected-resume-schema.md`.
9. Validate that every final bullet has one or more source IDs from `config/resume.yaml`.
10. Run `scripts/render_resume.py --selected <output-folder>/selected-resume.yaml --output-dir <output-folder> --max-pages <constraints.max_pages>`.
11. Run `scripts/create_report.py --selected <output-folder>/selected-resume.yaml --scrape <output-folder>/scrape.yaml --render <output-folder>/render.yaml --output <output-folder>/REPORT.md`.

## Guardrails

- Never invent tools, metrics, employers, dates, credentials, outcomes, or responsibilities.
- Convert unsupported job requirements into gap notes.
- Allow synthesized bullets only when all supporting source IDs are listed.
- Keep DOCX as the primary submission format.
- Keep formatting ATS-safe: one column, standard headings, no icons, no text boxes, no sidebars, no decorative elements.
- If rendered output exceeds the configured page limit, reduce content according to `constraints.bullet_reduction_order`, re-render, and document removed content in `REPORT.md`.

## References

- Use `references/selected-resume-schema.md` before writing `selected-resume.yaml`.
- Use `references/report-fields.md` before writing or reviewing `REPORT.md`.
