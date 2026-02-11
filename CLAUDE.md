# ep-skills Development Guide

This repo contains Claude Code plugins for AI-powered survey research. Each plugin lives in `plugins/<plugin-name>/` and gets deployed to the local Claude Code plugin cache.

## Repository Structure

```
ep-skills/
├── plugins/
│   ├── edsl-research/              # Main research plugin (source of truth)
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json         # Name, description, version
│   │   ├── CLAUDE.md               # Skill routing guide (loaded by Claude Code)
│   │   ├── install.py              # Deploys source → cache
│   │   ├── assets/
│   │   │   └── report.css          # Shared CSS for HTML reports
│   │   ├── commands/               # Slash command entry points (thin wrappers)
│   │   │   └── <skill-name>.md     # Maps /skill-name to its SKILL.md
│   │   └── skills/                 # Full skill implementations
│   │       └── <skill-name>/
│   │           └── SKILL.md        # Complete skill instructions
│   └── academic-referee/           # Another plugin (same structure)
├── 2026-MM-DD_<study-slug>/        # Study output directories (gitignored analysis_*)
├── README.md                       # Public-facing docs
└── CLAUDE.md                       # This file
```

## How Plugins Work

### Source vs. Cache

- **Source of truth:** `plugins/<plugin-name>/` in this repo
- **Cache (runtime):** `~/.claude/plugins/cache/ep-skills/<plugin-name>/<version>/`

Claude Code reads skills from the **cache**, not from this repo directly. The cache contains versioned copies (1.0.0, 1.1.0, 1.2.0, etc.) so older versions persist for reference.

### Plugin Anatomy

Each plugin has three layers:

1. **`plugin.json`** — metadata (name, description, version)
2. **`commands/*.md`** — thin slash-command wrappers that route to skills. These define what shows up as `/skill-name`. They contain `$ARGUMENTS` for user input and point to the corresponding skill.
3. **`skills/*/SKILL.md`** — the full implementation. These are detailed instruction files that tell Claude exactly what to do, including code snippets, file mappings, and workflow steps.

### Skill Types

- **User-invocable skills** (`user-invocable: true` in SKILL.md frontmatter): Triggered via `/skill-name`. Have a matching `commands/<skill-name>.md`.
- **Reference skills** (`user-invocable: false`): Internal documentation read by other skills at runtime (e.g., `report-reference`, `edsl-survey-reference`).

### Bundled Assets

Skills can reference bundled files (CSS, Python helpers) via glob patterns at runtime:
```
Glob("**/assets/report.css")
Glob("**/conjoint-study/helpers.py")
```

## Editing a Skill

1. Edit the source file: `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
2. If the skill has a command wrapper, check if `plugins/<plugin-name>/commands/<skill-name>.md` needs updating too
3. Deploy to cache (see below)

## Bumping the Version

1. Edit `plugins/<plugin-name>/.claude-plugin/plugin.json` — update the `"version"` field
2. Deploy to cache

The version string follows semver: bump **patch** (1.2.0 → 1.2.1) for fixes, **minor** (1.2.0 → 1.3.0) for new features or skill changes, **major** for breaking changes.

## Deploying to Cache

After editing source files, deploy to the cache so Claude Code picks up the changes:

```bash
python plugins/edsl-research/install.py           # deploy current version
python plugins/edsl-research/install.py --dry-run  # preview what would be copied
```

This reads the version from `plugin.json` and copies the plugin tree to `~/.claude/plugins/cache/ep-skills/edsl-research/<version>/`. If the version directory already exists, it is replaced.

**Important:** Always deploy after editing. If you only edit source files without deploying, Claude Code will still use the old cached version.

## Typical Workflow

```bash
# 1. Edit the skill
vim plugins/edsl-research/skills/publish-study/SKILL.md

# 2. Bump version in plugin.json
#    (edit "version": "1.3.0" → "1.4.0")

# 3. Deploy to cache
python plugins/edsl-research/install.py

# 4. Test the skill
#    (use /publish-study in Claude Code to verify)

# 5. Commit and push
git add plugins/edsl-research/
git commit -m "Bump edsl-research to v1.4.0: description of changes"
git push
```

## Study Directories

Study output directories follow the naming convention `YYYY-MM-DD_<study-slug>/`. They contain:
- EDSL component files (`study_survey.py`, `study_agent_list.py`, etc.)
- Results (`results.json.gz`, `results.csv`)
- Analysis subdirectories (`analysis_1/`, `analysis_2/`, etc.) with reports and charts

The `analysis_*/` directories are gitignored. Top-level study files are not — commit them if you want the study reproducible from this repo.
