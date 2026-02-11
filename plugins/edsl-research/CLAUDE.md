# EDSL Research Plugin

This plugin provides Claude Code skills for AI-powered survey research using EDSL (Expected Parrot's Domain Specific Language).

## Skill Routing Guide

Use this to pick the right skill based on user intent:

### Research Workflow (typical sequence)
```
Research question → /design-experiment → /create-study → /analyze-results → /answer-question → /publish-study
```

### By User Intent

| User says... | Skill to use |
|---|---|
| "I have a research question" / "Design an experiment" | `/design-experiment` |
| "Build me a survey" / "Create a study" | `/create-study` or `/create-survey` |
| "I need synthetic respondents" / "Create agents" | `/create-agent-list` |
| "I have results to analyze" / "Analyze this data" | `/analyze-results` |
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

### Bundled Assets

This plugin includes bundled files referenced by skills:

| File | Used by | Discovery |
|---|---|---|
| `assets/report.css` | `analyze-results`, `answer-question` | `Glob("**/assets/report.css")` |
| `skills/design-experiment/helpers.py` | `design-experiment` | `Glob("**/design-experiment/helpers.py")` |
| `skills/conjoint-study/helpers.py` | `conjoint-study` | `Glob("**/conjoint-study/helpers.py")` |
