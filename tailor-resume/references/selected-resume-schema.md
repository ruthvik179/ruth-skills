# Selected Resume Schema

Codex must create `selected-resume.yaml` after analyzing a job and before rendering files.

Required top-level fields:

- `job`: `url`, `title`, `company`, and optional `location`.
- `summary`: final summary text plus `source_ids`.
- `skills`: grouped skill names selected from `resume.yaml`.
- `experience`: employer-grouped roles with final bullets.
- `education`: selected education lines with `source_ids`.
- `projects`: selected project lines with `source_ids`.
- `certifications`: selected certification lines with `source_ids`.
- `extracurriculars`: selected extracurricular lines with `source_ids`.
- `gap_notes`: unsupported important job requirements.
- `ats_checklist`: formatting and keyword checks.

Each final experience bullet must include:

```yaml
text: Final rewritten bullet.
source_ids:
  - role-001-b001
rationale: Why this bullet was selected and how it maps to the job.
```

Never add a resume claim without a source ID from `resume.yaml`.
