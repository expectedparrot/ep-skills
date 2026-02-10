# ep-skills

A Claude Code plugin marketplace for AI-powered survey research using [EDSL](https://docs.expectedparrot.com/) (Expected Parrot's Domain Specific Language).

## Installation

### From GitHub

```
/plugin marketplace add expectedparrot/ep-skills
/plugin install edsl-research@ep-skills
```

### From local directory

```
/plugin marketplace add ~/tools/ep/ep-skills
/plugin install edsl-research@ep-skills
```

## Available Plugins

### edsl-research

Complete AI-powered survey research workflow with 11 skills covering experiment design, survey creation, agent generation, result analysis, and publication.

#### Research Workflow

```
Research question → /design-experiment → /create-study → /analyze-results → /answer-question → /publish-study
```

#### Skills

| Skill | Description |
|---|---|
| `/design-experiment` | Design a detailed experimental plan from a research question -- includes literature review, randomization plan, survey design, power analysis, and sample size recommendation |
| `/create-study` | Generate a multi-file study project with Survey, ScenarioList, AgentList, and a Makefile from a free text description |
| `/create-survey` | Create EDSL Surveys from questions, QSF files, or programmatically with branching logic |
| `/create-agent-list` | Create AgentLists from web searches, descriptions, local files, or programmatic generation |
| `/analyze-results` | Load EDSL Results objects by UUID or file path, export survey documentation, and generate analysis reports |
| `/answer-question` | Answer questions about a generated analysis report with additional analysis if needed |
| `/publish-study` | Publish a completed study to GitHub with the analysis report as README.md |
| `/search-objects` | Search, browse, and pull EDSL objects from the Expected Parrot cloud |

#### Reference Skills (used internally)

| Skill | Covers |
|---|---|
| `edsl-survey-reference` | Question types, Jinja2 templating, skip/nav rules, memory modes, helpers, visualization |
| `edsl-agent-reference` | AgentList operations, trait manipulation, templates, codebooks, instructions |
| `edsl-persistence-reference` | Save/load locally, push/pull to Expected Parrot cloud, git versioning |

## Prerequisites

- Python 3.9+
- [EDSL](https://pypi.org/project/edsl/) (`pip install edsl`)
- [pandoc](https://pandoc.org/installing.html) (for HTML report generation)
- An [Expected Parrot](https://expectedparrot.com/) API key (set `EXPECTED_PARROT_API_KEY` env var)

## About

Built by [Expected Parrot](https://expectedparrot.com/) for conducting AI-powered survey research with EDSL.
