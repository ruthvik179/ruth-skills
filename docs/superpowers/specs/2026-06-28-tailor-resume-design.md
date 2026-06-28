# Tailor Resume Skill Design

## Goal

Create a Codex skill that takes a job posting URL, extracts the job description, and generates a tailored resume package from a complete YAML source of truth. The package must include a decision report, a DOCX resume, and a PDF resume in a new folder for each job.

The skill is based on the behavior of the `tailored-resume-generator` skill from `ComposioHQ/awesome-codex-skills`, but extends it with automated scraping, a structured master resume bank, provenance tracking, config-enforced constraints, deterministic file generation, and ATS validation.

## Output Contract

Each run creates a new folder under:

```text
outputs/<company>-<role>-<date>/
```

The folder contains:

- `REPORT.md`: job link, scrape status, extracted requirements, keyword rationale, tailoring decisions, bullet provenance, gap notes, and ATS checklist.
- `resume.docx`: primary ATS-safe resume output.
- `resume.pdf`: PDF version generated from the same structured resume content.
- `job.txt`: cleaned job description text.
- `job-raw.html` or equivalent raw scrape artifact when available.
- `selected-resume.yaml` or `selected-resume.json`: intermediate selected resume content with final bullets and provenance.

If a folder name already exists, the tool must avoid overwriting by adding a deterministic suffix or timestamp.

## Architecture

Use a Codex skill named `tailor-resume` backed by bundled scripts:

- `SKILL.md`: workflow instructions, triggering guidance, and guardrails for Codex.
- `config/resume.yaml`: complete resume source of truth.
- `scripts/scrape_job.py`: accepts a URL, extracts raw and cleaned job text, and records scrape metadata.
- `scripts/validate_resume_yaml.py`: validates required fields, constraints, per-role bullet counts, and source IDs.
- `scripts/render_resume.py`: renders `resume.docx` and `resume.pdf` from selected structured content.
- `scripts/create_report.py`: writes `REPORT.md` from job analysis, selection rationale, provenance, gaps, and ATS checks.

Codex handles judgment-heavy tasks: interpreting the job posting, matching skills and experience, selecting source-backed bullets, rewriting bullets honestly, and explaining decisions. Scripts handle deterministic mechanics: scraping, validation, output folder creation, rendering, and report scaffolding.

## YAML Source Of Truth

`resume.yaml` is the complete source of truth for generated resumes. It includes:

- contact information
- resume headline or current target title
- links
- target title variants
- summary fact bank
- education entries with research, capstone, GPA, and honors metadata
- certifications when available
- projects when available
- master skill inventory grouped by resume category
- experience grouped by employer, with multiple roles under one employer when needed
- bullet banks for each role
- extracurriculars, awards, and leadership entries
- constraints, rendering preferences, and section ordering

Every reusable claim must have a stable ID so final resume content can cite its source.

The current resume structure should be represented directly:

- Header: name, headline, phone, email, location, and LinkedIn.
- Summary: a concise paragraph assembled from source-backed summary facts.
- Education: school, location, degree, dates, research assistant roles, capstone details, and GPA when present.
- Key Experience: employer-grouped experience where one employer can contain several roles with different titles and dates.
- Skills: categorized groups such as programming, ML/AI, data/cloud, visualization, and optimization.
- Extracurriculars: leadership, awards, competitions, and other high-signal activities.

Suggested structure:

```yaml
constraints:
  max_pages: 2
  default_bullets_per_role: 4
  bullet_reduction_order:
    - extracurriculars
    - projects
    - oldest_role_bullets
  require_exact_role_bullet_count: true
  allow_synthesis: true
  synthesis_requires_provenance: true

rendering:
  primary_format: docx
  generate_pdf: true
  section_order:
    - summary
    - education
    - experience
    - skills
    - projects
    - certifications
    - extracurriculars
  section_labels:
    summary: Summary
    education: Education
    experience: Key Experience
    skills: Skills
    extracurriculars: Extracurriculars

profile:
  name: Your Name
  headline: Data Scientist
  email: you@example.com
  phone: "555-555-5555"
  location: City, ST
  links:
    linkedin: https://linkedin.com/in/example
    github: https://github.com/example

targeting:
  title_variants:
    - Data Scientist
    - Machine Learning Engineer
    - Data Analyst
    - Data Engineer
  summary_facts:
    - id: summary-001
      text: 5+ years across applied data science, data engineering, and industrial analytics.
      themes: [data-science, data-engineering, industrial-analytics]
    - id: summary-002
      text: Experience building production decision systems using optimization, GenAI/RAG, geospatial modeling, and cloud data pipelines.
      skills: [optimization, RAG, geospatial-modeling, cloud-data-pipelines]
      themes: [decision-systems, production-systems]

education:
  - id: edu-001
    institution: Oklahoma State University
    location: Stillwater, USA
    degree: Master's in Business Analytics and Data Science
    start: 2022-08
    end: 2024-05
    gpa: "3.9/4"
    details:
      - id: edu-001-d001
        text: Research Assistant, Behavioral Lab.
        themes: [research, behavioral-analytics]
      - id: edu-001-d002
        text: Capstone project building lead-generation models for an insurance firm.
        skills: [machine-learning, lead-generation]
        themes: [capstone, predictive-modeling]
  - id: edu-002
    institution: Hyderabad Institute of Technology and Management
    location: Hyderabad, India
    degree: Bachelor's in Computer Science
    start: 2016-06
    end: 2020-06
    details:
      - id: edu-002-d001
        text: Research Assistant, AI/ML Lab.
        skills: [AI, machine-learning]

skills:
  groups:
    - id: skills-programming
      name: Programming
      items: [Python, SQL]
    - id: skills-ml-ai
      name: ML/AI
      items: [PyTorch, Deep Learning, Time Series, GIS, RAG, LangChain, LangSmith, Embeddings, Vector Search]
    - id: skills-data-cloud
      name: Data/Cloud
      items: [Airflow, Docker, dbt, AWS S3, AWS Redshift, AWS Lambda, PySpark, TimescaleDB, pgvector]
    - id: skills-visualization
      name: Visualization
      items: [Power BI, Plotly Dash, Streamlit]
    - id: skills-optimization
      name: Optimization
      items: [Gurobi, Linear Programming]

experience:
  - id: company-001
    company: Example Corp
    location: Wichita, KS
    roles:
      - id: role-001
        title: Data Scientist
        start: 2024-05
        end: Present
        bullets_required: 4
        master_bullets:
          - id: role-001-b001
            text: Built a Dash-based optimization platform with an API Gateway/Lambda-backed MILP engine for plant-level contract allocation.
            outcomes:
              - sale reallocations worth about $2.5M in finance-validated P&L uplift
            skills: [Plotly Dash, AWS API Gateway, AWS Lambda, MILP, optimization]
            themes: [contract-allocation, decision-systems, operations-optimization]
            rewrite_guidance:
              preserve:
                - finance-validated impact
                - plant-level contract allocation scope
              avoid:
                - claiming ownership of finance validation unless explicitly supported
          - id: role-001-b002
            text: Developed a market-intelligence pipeline that parsed notification emails, retrieved historical analogs, and generated alerts.
            outcomes:
              - reduced manual market-review effort for the commercial team
            skills: [TimescaleDB, pgvector, embeddings, retrieval, alerting]
            themes: [market-intelligence, retrieval, workflow-automation]
          - id: role-001-b003
            text: Deployed geospatial demand-estimation models using sales, crop acreage, and weather data to guide fertilizer inventory positioning.
            outcomes:
              - contributed about $500K in seasonal revenue uplift through reduced terminal stockouts
            skills: [geospatial modeling, weather data, demand estimation]
            themes: [inventory-positioning, geospatial-analytics, demand-forecasting]
          - id: role-001-b004
            text: Led development of a multimodal barge-intelligence system combining AIS data, satellite imagery classification, terminal mapping, and lock data to estimate product volumes.
            outcomes:
              - informed positioning decisions worth about $1.5M in annualized value
            skills: [AIS data, satellite imagery classification, terminal mapping, multimodal modeling]
            themes: [logistics-intelligence, multimodal-analytics, volume-estimation]
      - id: role-002
        title: Data Science Co-op
        start: 2023-08
        end: 2024-05
        bullets_required: 2
        master_bullets:
          - id: role-002-b001
            text: Developed an AI trade-capture system using schema-constrained extraction, validation rules, and human-in-the-loop review.
            outcomes:
              - improved extraction accuracy from 86% to 98%
            skills: [GenAI, schema-constrained extraction, validation, human-in-the-loop review]
            themes: [trade-capture, structured-extraction, workflow-automation]
          - id: role-002-b002
            text: Automated product ID standardization across multi-plant procurement using a GPT-4o-powered real-time pipeline.
            outcomes:
              - streamlined vendor selection
              - supported about 8% procurement cost reduction
            skills: [GPT-4o, real-time pipelines, data standardization]
            themes: [procurement-automation, vendor-selection, master-data-standardization]
      - id: role-003
        title: Summer Intern
        start: 2023-05
        end: 2023-08
        bullets_required: 2
        master_bullets:
          - id: role-003-b001
            text: Performed cost-benefit analyses to identify high-ROI plant upgrades.
            outcomes:
              - enabled selection of improvements that reduced turnaround time and increased terminal throughput
            skills: [cost-benefit analysis, operations analysis]
            themes: [plant-upgrades, throughput, ROI-analysis]
          - id: role-003-b002
            text: Deployed a real-time driver performance monitoring solution in Power BI.
            outcomes:
              - decreased delivery delays by about 15%
            skills: [Power BI, real-time monitoring]
            themes: [driver-performance, logistics-analytics, delay-reduction]
  - id: company-002
    company: Example Data Services
    location: Hyderabad, India
    roles:
      - id: role-004
        title: Data Engineer
        start: 2020-08
        end: 2022-07
        bullets_required: 3
        master_bullets:
          - id: role-004-b001
            text: Migrated legacy SSIS jobs to Airflow with PySpark and integrated workforce-management data into Redshift.
            outcomes:
              - supported a 1,200-agent network
              - achieved about 15% faster loading
              - lowered compute costs by about 20%
            skills: [SSIS, Airflow, PySpark, Redshift]
            themes: [migration, data-pipelines, workforce-analytics]
          - id: role-004-b002
            text: Designed a standardized error-handling framework for dbt-based ETL workflows.
            outcomes:
              - reduced annual maintenance costs by about $80K
              - saved about 10 development hours per sprint across a 6+ person team
            skills: [dbt, ETL, error handling]
            themes: [data-quality, maintainability, workflow-standardization]
          - id: role-004-b003
            text: Designed end-to-end ODI pipelines that processed about 2 million records daily.
            outcomes:
              - reduced pipeline latency by about 35%
            skills: [ODI, ETL, data pipelines]
            themes: [pipeline-design, high-volume-processing, latency-reduction]
      - id: role-005
        title: Data Engineer Co-op
        start: 2020-01
        end: 2020-08
        bullets_required: 2
        master_bullets:
          - id: role-005-b001
            text: Wrote and scheduled Airflow DAGs to replace manual workflow runs with retries and backfills.
            outcomes:
              - saved about 3 hours per week
            skills: [Airflow, DAGs, retries, backfills]
            themes: [workflow-automation, orchestration]
          - id: role-005-b002
            text: Implemented batching and backoff for API ingestion while staying within rate limits.
            outcomes:
              - increased throughput by about 30%
            skills: [API ingestion, batching, backoff, rate limits]
            themes: [data-ingestion, throughput-improvement, reliability]

projects: []

certifications: []

extracurriculars:
  - id: extra-001
    text: President, Entrepreneurship Development Cell.
    outcomes:
      - helped incubate 3 early-stage startups
    themes: [leadership, entrepreneurship]
  - id: extra-002
    text: Student of the Year for academic excellence and extracurricular engagement.
    themes: [academic-excellence, leadership]
  - id: extra-003
    text: 2nd Runner-Up, Adobe Analytics Challenge.
    outcomes:
      - competition included 2000+ global entries and 3000+ students from 40+ countries
    themes: [analytics-competition, data-storytelling]
```

The YAML can use real employer names and real bullet text in the user's private source file. Public examples in the skill should use anonymized employers unless the user explicitly wants a personal sample config generated.

Validation must enforce that:

- every `summary_facts`, `education.details`, `experience.roles`, `master_bullets`, `projects`, `certifications`, and `extracurriculars` item has a stable ID when it can be selected or cited
- every role with `bullets_required` has at least that many available `master_bullets`, unless the role is marked `include: false`
- every generated resume bullet references one or more source IDs from the YAML
- skill names used in bullet metadata either match the master skill inventory or are explicitly allowed aliases
- section names and ordering are driven by `rendering.section_order` and `rendering.section_labels`

## Workflow

1. Accept a job URL.
2. Try to scrape the page into raw HTML or raw text plus cleaned job description text.
3. If scraping fails, the page is unavailable, or extracted text is too thin, ask for pasted job text, saved HTML, or a PDF.
4. Record the scrape method and fallback status.
5. Extract job signals:
   - title
   - company
   - location or work mode when available
   - required skills
   - preferred skills
   - responsibilities
   - seniority level
   - domain terms
   - repeated keywords
6. Load and validate `resume.yaml`.
7. Score master bullets and skills against the extracted job signals.
8. Select the configured number of bullets for each held position.
9. Rewrite selected bullets using relevant job language while preserving the factual claim.
10. Allow synthesis only when the final bullet cites all supporting source IDs.
11. Add unsupported important requirements to gap notes, not to the resume.
12. Render DOCX and PDF.
13. Check rendered page count and extracted PDF text order.
14. If the resume exceeds `constraints.max_pages`, compact or reduce content according to config rules, document the change, and re-render.
15. Write `REPORT.md`.

## Constraints And Guardrails

- Resume length must be at or under `constraints.max_pages`.
- Each position gets the exact configured bullet count unless page length forces a documented reduction.
- Tailored bullets may be rewritten, but every claim must trace to one or more YAML source IDs.
- Synthesis is allowed only when all source IDs are cited.
- No unsupported skills, tools, metrics, credentials, titles, employers, dates, responsibilities, or outcomes may be invented.
- Important job requirements missing from the YAML become gap notes.
- Scrape failures and fallback methods must be recorded in `REPORT.md`.
- Output folders must not overwrite previous runs.
- Resume formatting must stay ATS-safe.

## Rendering And ATS Validation

Use DOCX as the primary submission format. Generate PDF from the same selected structured resume content.

Rendering rules:

- one-column layout
- standard section headings such as `Summary`, `Skills`, `Experience`, `Projects`, `Education`, and `Certifications`
- no icons
- no sidebars
- no text boxes
- no images
- no decorative elements
- avoid tables unless a future renderer proves safe extraction
- conservative fonts and spacing
- stable section ordering

After rendering:

- verify page count
- run PDF text extraction
- confirm extracted text follows the expected reading order
- report ATS risks in `REPORT.md`

LaTeX is not the default renderer. It can be considered later as an optional renderer only if it produces single-column, text-extractable PDFs that pass the same ATS validation checks.

## Report Contents

`REPORT.md` includes:

- job URL
- scrape status and fallback status
- generated folder timestamp
- extracted company, role, location, and seniority when available
- core job requirements
- preferred requirements
- selected keywords
- chosen resume sections
- chosen skills and why they were included
- final bullet list with source IDs
- rationale for each bullet rewrite
- synthesized bullet provenance when applicable
- omitted strong bullets and why they were omitted
- gap notes for unsupported job requirements
- ATS checklist
- page-count result
- PDF text extraction result

## Error Handling

If scraping fails:

- ask for pasted job text, saved HTML, or PDF
- continue once fallback content is available
- record the fallback in `REPORT.md`

If `resume.yaml` is invalid:

- stop before generation
- report the exact missing or invalid fields
- do not invent missing source data

If rendering fails:

- keep `selected-resume.yaml` and `REPORT.md` draft artifacts when possible
- report the failed command and likely cause
- do not claim DOCX or PDF generation succeeded

If page count exceeds the configured maximum:

- reduce or compact content according to explicit config rules
- re-render and re-check
- document any removed bullets or compacting decisions in `REPORT.md`

## Testing Strategy

Use focused tests around deterministic components:

- YAML validation accepts complete valid data and rejects missing required fields.
- Scraper saves raw and cleaned artifacts for accessible pages.
- Scraper fallback path records fallback metadata.
- Folder creation avoids overwriting prior runs.
- Report generation includes required sections.
- Renderer creates DOCX and PDF files.
- Page-count validation detects over-limit output.
- PDF text extraction returns expected section order for a sample resume.

Judgment-heavy tailoring should be checked through fixture-based review:

- sample job description
- sample `resume.yaml`
- expected selected source IDs
- expected gap notes
- expected ATS checklist items

## Open Implementation Notes

- This workspace is currently not a git repository, so the design document cannot be committed unless a repository is initialized or the work is moved into an existing repo.
- The rendering stack should be chosen during implementation. A practical default is Python with `python-docx` for DOCX generation and a platform-available DOCX-to-PDF path for PDF generation.
- The scraper should prefer robust text extraction and clear fallback behavior over brittle job-board-specific automation.
