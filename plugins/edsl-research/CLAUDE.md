# EDSL Research Plugin

This plugin provides Claude Code skills for AI-powered survey research using EDSL (Expected Parrot's Domain Specific Language).

## Skill Routing Guide

Use this to pick the right skill based on user intent:

### Research Workflows (typical sequences)
```
General:  Research question → /design-experiment → /create-study → /analyze-results → /answer-question → /publish-study
Conjoint: Research question → /conjoint-study → /analyze-conjoint-results → /publish-study
```

### By User Intent

| User says... | Skill to use |
|---|---|
| "I have a research question" / "Design an experiment" | `/design-experiment` |
| "Build me a survey" / "Create a study" | `/create-study` or `/create-survey` |
| "I need synthetic respondents" / "Create agents" | `/create-agent-list` |
| "I have results to analyze" / "Analyze this data" | `/analyze-results` |
| "Analyze conjoint results" / "Conjoint report" | `/analyze-conjoint-results` |
| "What does this result mean?" / follow-up on analysis | `/answer-question` |
| "Publish this study" / "Share on GitHub" | `/publish-study` |
| "Conjoint analysis" / "Choice experiment" / "Product preference" | `/conjoint-study` |
| "Find existing surveys/agents/results" | `/search-objects` |

### Reference Skills (used internally by workflow skills)

These are not user-facing commands. They provide EDSL API documentation and are invoked by workflow skills or when you need implementation details:

| Skill | Covers |
|---|---|
| `edsl-survey-reference` | Question types, Jinja2 templating, skip/nav rules, memory modes, helpers, visualization |
| `edsl-agent-reference` | AgentList operations, trait manipulation, templates, codebooks, instructions |
| `edsl-persistence-reference` | Save/load locally, push/pull to Expected Parrot cloud, git versioning |
| `report-reference` | Report quality standards: required sections, image paths, color scheme, agent display rules |

### Bundled Assets

This plugin includes bundled files referenced by skills:

| File | Used by | Discovery |
|---|---|---|
| `assets/report.css` | `analyze-results`, `analyze-conjoint-results`, `answer-question` | `Glob("**/assets/report.css")` |
| `skills/design-experiment/helpers.py` | `design-experiment` | `Glob("**/design-experiment/helpers.py")` |
| `skills/conjoint-study/helpers.py` | `conjoint-study`, `analyze-conjoint-results` | `Glob("**/conjoint-study/helpers.py")` |
| `skills/report-reference/SKILL.md` | `analyze-results`, `analyze-conjoint-results` | `Glob("**/report-reference/SKILL.md")` |
