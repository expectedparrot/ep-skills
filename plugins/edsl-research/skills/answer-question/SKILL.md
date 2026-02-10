---
name: answer-question
description: Answer questions about a generated analysis report - reads report artifacts, performs additional analysis if needed, and saves the answer with metadata
allowed-tools: Read, Glob, Grep, Bash(python:*), Bash(pandoc *), Write, AskUserQuestion
user-invocable: true
arguments: question [analysis_dir]
---

# Answer Question

Read a generated analysis report (from `/analyze-results`) and answer a specific question about it. Can perform additional analysis on the underlying data if the existing report doesn't fully answer the question. Saves the answer as markdown with supporting files in a dedicated directory.

## Usage

```
/answer-question What is the sample size?
/answer-question How does weight vary by position? ./analysis_1
```

If no analysis directory is specified, the skill will locate the most recent one automatically.

## Workflow

### 1. Parse the Input

Extract two things from the user's input:
- **Question**: The question to answer (required)
- **Analysis directory**: An optional path to a specific analysis directory (e.g., `./analysis_3`)

If no analysis directory is provided, check how many analysis directories contain a `report.md`:

```python
import glob
import os

existing = sorted(glob.glob("./analysis_*"), key=os.path.getmtime, reverse=True)
with_reports = [d for d in existing if os.path.isfile(os.path.join(d, "report.md"))]
```

- **If zero directories have reports**, tell the user to run `/analyze-results` first.
- **If exactly one directory has a report**, use it automatically.
- **If multiple directories have reports**, use `AskUserQuestion` to let the user pick. Read the first line of each `report.md` to build descriptive labels:

```python
# Build option labels like "analysis_5 — Anchoring Bias Experiment (2026-02-06)"
options = []
for d in with_reports:
    first_line = open(os.path.join(d, "report.md")).readline().strip().lstrip("# ")
    options.append({"label": os.path.basename(d), "description": first_line})
```

Then ask:
```
Which analysis directory should I use?
```
with those options. Use the user's choice as `analysis_dir`.

### 2. Read the Report and Data

Load the key artifacts from the analysis directory:

1. **`report.md`** — The main analysis report. Read it fully.
2. **`results.csv`** — The raw data. Load it into pandas for potential follow-up analysis.
3. **`survey.md`** — The survey structure. Read it for context about question wording and types.

```python
import pandas as pd

report_md = open(f"{analysis_dir}/report.md").read()
survey_md = open(f"{analysis_dir}/survey.md").read()
df = pd.read_csv(f"{analysis_dir}/results.csv")
```

Also read any other files in the directory (mermaid diagrams, existing charts) to have full context.

### 3. Create Output Directory

Create a directory named with a slugified version of the question:

```python
import re
import os

def slugify(text, max_length=60):
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    # Remove punctuation except hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace whitespace with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Truncate to max_length at a word boundary
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]
    return text

slug = slugify(question)
output_dir = f"{analysis_dir}/{slug}"
os.makedirs(output_dir, exist_ok=True)
```

For example:
- "What is the sample size?" → `analysis_1/what-is-the-sample-size/`
- "How does weight vary by position?" → `analysis_1/how-does-weight-vary-by-position/`

If the directory already exists, append a numeric suffix: `what-is-the-sample-size-2`.

### 4. Answer the Question

Attempt to answer the question in this order:

**a) Check the existing report first.** If the report already contains the answer, extract and summarize it. No additional analysis needed.

**b) If the report doesn't fully answer the question, do additional analysis.** Write and run Python scripts against `results.csv` to compute statistics, generate charts, or perform deeper analysis. Save any generated charts or data files to the output directory.

**c) If the question requires information not available in the data,** say so clearly and explain what data would be needed.

When performing additional analysis, save the Python script as `analysis.py` in the output directory for reproducibility.

### 5. Write the Answer

Write the answer as `answer.md` in the output directory:

```markdown
# [Question text here]

[Clear, concise answer in 1-3 paragraphs]

## Supporting Evidence

[Tables, statistics, or references to charts that back up the answer]

## Additional Context

[Any caveats, limitations, or related observations — only if relevant]
```

Keep answers direct and focused. Lead with the answer, then provide evidence.

If charts or visualizations were generated, reference them with relative paths:

```markdown
![Description](chart_name.png)
```

### 6. Write Metadata

Save a `meta.json` file in the output directory:

```python
import json
from datetime import datetime, timezone

meta = {
    "question": question,
    "slug": slug,
    "analysis_dir": analysis_dir,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "files": os.listdir(output_dir),
    "required_additional_analysis": True  # or False
}

with open(f"{output_dir}/meta.json", "w") as f:
    json.dump(meta, f, indent=2)
```

### 7. Generate HTML (optional)

If the answer includes charts or tables, convert to HTML for easy viewing:

```bash
# Locate the bundled CSS using Glob("**/assets/report.css")
CSS_FILE="<discovered_css_path>"
pandoc "${output_dir}/answer.md" \
    -o "${output_dir}/answer.html" \
    --css="${CSS_FILE}" \
    --standalone
```

### 8. Report Back

Tell the user:
- The answer (summarized directly in chat)
- The path to the output directory with all files

## Output Files

| File | Description |
|------|-------------|
| `answer.md` | The answer in markdown format |
| `answer.html` | Styled HTML version of the answer (if generated) |
| `meta.json` | Metadata: question, timestamp, files list, flags |
| `analysis.py` | Python script used for additional analysis (if any) |
| `*.png` | Charts or visualizations generated (if any) |

## Example

User runs:
```
/answer-question What is the average weight by position?
```

Skill finds `./analysis_1/` (most recent), reads `report.md` and `results.csv`, sees the report already has a position breakdown, extracts and reformats it, and produces:

```
analysis_1/what-is-the-average-weight-by-position/
├── answer.md
├── answer.html
└── meta.json
```

If the report didn't have that breakdown, the skill would write and run a script:

```
analysis_1/what-is-the-average-weight-by-position/
├── answer.md
├── answer.html
├── meta.json
├── analysis.py
└── weight_by_position.png
```

## Tips

- Always read the full report before deciding whether additional analysis is needed
- When doing additional analysis, save the script so results are reproducible
- Keep answers concise — a paragraph or two plus a table is usually sufficient
- Reference existing charts from the parent analysis directory when they're relevant rather than regenerating them
- Use relative paths for all file references so the directory is portable
