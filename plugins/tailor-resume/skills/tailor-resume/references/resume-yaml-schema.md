# Resume YAML Schema

Users provide the resume YAML as an input file outside the skill folder. The skill must not store personal resume data in `tailor-resume/`.

Required top-level fields:

- `constraints`
- `rendering`
- `profile`
- `targeting`
- `education`
- `skills`
- `experience`
- `projects`
- `certifications`
- `extracurriculars`

Every selectable claim needs a stable `id` so final resume bullets can cite provenance.

Minimal shape:

```yaml
constraints:
  max_pages: 2
  default_bullets_per_role: 3
  bullet_reduction_order: [extracurriculars, projects, oldest_role_bullets]
  require_exact_role_bullet_count: true
  allow_synthesis: true
  synthesis_requires_provenance: true

rendering:
  primary_format: docx
  generate_pdf: true
  section_order: [summary, education, experience, skills, projects, certifications, extracurriculars]
  section_labels:
    summary: Summary
    education: Education
    experience: Experience
    skills: Skills
    projects: Projects
    certifications: Certifications
    extracurriculars: Extracurriculars

profile:
  name: Example Candidate
  headline: Data Scientist
  email: candidate@example.com
  phone: "+1 (555) 555-5555"
  location: City, ST
  links:
    linkedin: https://www.linkedin.com/in/example

targeting:
  title_variants: [Data Scientist]
  summary_facts:
    - id: summary-001
      text: Source-backed summary claim.
      skills: [Python]
      themes: [analytics]

education:
  - id: edu-001
    institution: Example University
    location: City, ST
    degree: Example Degree
    start: 2020-08
    end: 2024-05
    details:
      - id: edu-001-d001
        text: Source-backed education detail.

skills:
  aliases: {}
  groups:
    - id: skills-programming
      name: Programming
      items: [Python, SQL]

experience:
  - id: company-001
    company: Example Company
    location: City, ST
    roles:
      - id: role-001
        title: Example Role
        start: 2024-01
        end: Present
        bullets_required: 2
        master_bullets:
          - id: role-001-b001
            text: Source-backed accomplishment.
            outcomes: []
            skills: [Python]
            themes: [analytics]
          - id: role-001-b002
            text: Another source-backed accomplishment.
            outcomes: []
            skills: [SQL]
            themes: [data]

projects: []
certifications: []
extracurriculars: []
```
