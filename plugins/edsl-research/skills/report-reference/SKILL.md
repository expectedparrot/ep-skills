---
name: report-reference
description: Quality standards and guidelines for generating analysis reports across all report-producing skills
allowed-tools: Read
user-invocable: false
---

# Report Quality Reference

This reference skill codifies quality standards for all report-generating skills in the EDSL Research plugin. Any skill that produces a `report.md` / `report.html` should read this file first and follow these guidelines.

## Required Report Sections

Every analysis report MUST include these sections, in order:

1. **Executive Summary** — Research question, 3-5 quantified key findings, and the single most important takeaway. This section should let a reader understand the study without reading anything else.
2. **Study Design** — What was tested, how, and with whom. Sufficient detail for replication.
3. **Methodology** — Statistical/analytical methods used, with brief plain-language explanations.
4. **Results** — Detailed findings with tables, charts, and interpretation.
5. **Key Findings** — Substantive prose paragraphs synthesizing the results (see below).
6. **Limitations** — Honest assessment of study constraints.
7. **Files Generated** — Table of output files with relative links.

## Key Findings Must Be Substantive

The "Key Findings" section must contain 4-6 paragraphs of substantive prose written by Claude. Each paragraph should:
- State a specific, quantified finding (e.g., "Price was the dominant factor at 32.1% importance...")
- Explain what it means in practical terms
- Connect it to other findings where relevant

**Never** use placeholder text like "[Add key findings based on the analysis]" or "[Insert findings here]". Claude must write the actual findings based on the data.

## Show Realized Examples, Not Raw Templates

When a survey uses Jinja2 scenario templates (e.g., `{{ task_1_opt_a }}`):
- **Do NOT** show the raw template syntax in the report body
- **Do** show 1-2 fully realized examples with actual values filled in
- If showing the template is useful for documentation, put it in a "Survey Template" subsection and clearly label it as a template

## Deduplicate Repeated Templates

If the same question template is used for N tasks (common in conjoint studies), do NOT list it N times. Instead:
- Show the template once
- Note "This template was used for N choice tasks"
- Show 1-2 realized examples

## Never Truncate Persona Descriptions

When displaying agent/respondent personas:
- Show the FULL persona description, never truncated with "..."
- Use the `segment` trait as the display label/header
- Skip UUID-based agent names entirely (do not display them)

## Agent Display Rules

- Use the `segment` trait value as the primary label for each agent
- If agents have UUID-style names (8-4-4-4-12 hex pattern), hide them entirely
- Always show the full `persona` trait text under each segment label
- In tables, use segment labels for row/column headers, not agent name UUIDs

## Image and File Path Rules

All images referenced in `report.md` MUST be in the same directory as the report:
- **Correct:** `![Chart](importance_chart.png)`
- **Wrong:** `![Chart](../importance_chart.png)`
- **Wrong:** `![Chart](/absolute/path/importance_chart.png)`

Copy any images generated outside the output directory into the output directory before referencing them.

## Analytical N vs. Row Count

Report the analytical N (number of independent observations/choices), not just the CSV row count:
- For conjoint: N = number of choice tasks answered (rows x tasks_per_version)
- For surveys: N = number of unique respondents
- Always state what the unit of analysis is

## Pandoc HTML Conversion

Convert `report.md` to `report.html` using:

```bash
pandoc report.md -o report.html --css=<css_path> --standalone
```

- Locate the CSS file with `Glob("**/assets/report.css")`
- Do NOT use `--metadata title=` (the markdown `# heading` serves as the title)
- The HTML file must be self-contained: all images referenced must be local

## Color Scheme

Use these colors consistently across all charts:

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary / positive values | Steel blue | `#4C78A8` |
| Negative values / warnings | Coral red | `#E45756` |
| Secondary | Teal | `#72B7B2` |
| Accent | Orange | `#F58518` |
| Neutral | Gray | `#BAB0AC` |

## File Links in Reports

Always use relative links for files generated alongside the report:
- `[results.csv](results.csv)` not `[results.csv](./analysis_1/results.csv)`
- `[utilities.json](utilities.json)` not an absolute path

## Report Metadata

Include a generation timestamp at the top of the report:
```markdown
*Generated: YYYY-MM-DD HH:MM:SS*
```
