# Ruth Skills

Codex plugin marketplace for reusable local skills.

## Plugins

- `tailor-resume`: Generates job-tailored resume packages from a user-provided YAML resume source of truth.

## Install From GitHub

After this repository is pushed to GitHub, install the marketplace:

```powershell
codex plugin marketplace add <owner>/<repo> --ref main
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
