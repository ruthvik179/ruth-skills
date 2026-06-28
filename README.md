# Ruth Skills

Codex plugin marketplace for reusable local skills.

## Plugins

- `tailor-resume`: Generates job-tailored resume packages from a user-provided YAML resume source of truth.

## Install From GitHub

Install the marketplace from GitHub:

```powershell
codex plugin marketplace add ruthvik179/ruth-skills --ref master
codex plugin add tailor-resume@ruth-skills
```

For a private repository, make sure the person installing has Git access first.

## Test Locally

From this repository root:

```powershell
codex plugin marketplace add .\
codex plugin add tailor-resume@ruth-skills
```

Start a new Codex thread after installing so the plugin metadata is loaded.
