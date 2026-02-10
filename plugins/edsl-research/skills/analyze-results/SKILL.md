---
name: analyze-results
description: Analyze EDSL Results objects - load by UUID or file path, export survey documentation, and generate analysis reports
allowed-tools: Read, Glob, Bash(python:*), Bash(pandoc *), Write, AskUserQuestion
user-invocable: true
arguments: UUID or path to results.json.gz file
---

# Analyze EDSL Results

Load an EDSL Results object from Expected Parrot (by UUID) or from a local file (results.json.gz), export documentation files, and generate a comprehensive analysis report.

## Usage

```
/edsl-analyze-results <uuid-or-path>
```

Examples:
```
/edsl-analyze-results 123e4567-e89b-12d3-a456-426614174000
/edsl-analyze-results ./my_experiment/results.json.gz
```

After loading the results, the skill will ask you to choose an analysis focus (full analysis, summary statistics, cross-tabulation, or a specific custom focus).

**IMPORTANT:** Always ask this question, even if the user provided a query with the UUID. The question helps clarify what type of analysis they want. If they select "Specific focus", follow up to get their specific question or hypothesis.


## Workflow

### 1. Parse the Input

Determine if the input is:
- **UUID**: A 36-character UUID (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- **File path**: A path ending in `.json.gz` or `.json`

If unclear, use AskUserQuestion to clarify.

### 2. Load the Results

```python
from edsl import Results

# Load by UUID (from Expected Parrot cloud)
results = Results.pull("123e4567-e89b-12d3-a456-426614174000")

# OR load from local file
results = Results.load("path/to/results")  # .json.gz extension optional
```

### 3. Create Output Directory and Ask about Report Focus

Create a directory for the analysis outputs using sequential numbering:

```python
import os
import glob

# Find existing analysis directories and get next number
existing = glob.glob("./analysis_*")
existing_nums = []
for d in existing:
    try:
        num = int(d.split("_")[-1])
        existing_nums.append(num)
    except ValueError:
        pass

next_num = max(existing_nums, default=0) + 1
output_dir = f"./analysis_{next_num}"
os.makedirs(output_dir, exist_ok=True)
```

**always** use AskUserQuestion to ask about the analysis focus.
This ensures the report is tailored to the user's needs. It's a free text question:

```
Question: "What would you like me to focus on in the analysis?"
Header: "Focus"
```

### 4. Export Documentation Files

Export three core documentation files:

```python
# Get survey from results
survey = results.survey

# 1. Export survey as markdown
survey_md = survey.to_markdown()
with open(f"{output_dir}/survey.md", "w") as f:
    f.write(survey_md)

# 2. Export survey as mermaid diagram
# Note: Sanitize HTML tags for mermaid v11+ compatibility
import re
survey_mermaid = survey.to_mermaid()
# Remove HTML tags that cause syntax errors in newer mermaid versions
survey_mermaid = re.sub(r'<b>|</b>|<br/>', '\n', survey_mermaid)
survey_mermaid = re.sub(r'\n+', '\n', survey_mermaid)  # Clean up multiple newlines
with open(f"{output_dir}/survey.mermaid", "w") as f:
    f.write(survey_mermaid)

# 3. Export results as CSV
results_csv = results.to_csv()
results_csv.write(f"{output_dir}/results.csv")
# OR: with open(f"{output_dir}/results.csv", "w") as f: f.write(results_csv.text)
```

### 5. Initial Data Exploration

Before analysis, explore the data structure:

```python
import pandas as pd

# Load and examine the CSV
df = pd.read_csv(f"{output_dir}/results.csv")

# Get column info
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Identify question answer columns (answer.*)
answer_cols = [c for c in df.columns if c.startswith('answer.')]
print(f"Answer columns: {answer_cols}")

# Identify agent columns (agent.*)
agent_cols = [c for c in df.columns if c.startswith('agent.')]
print(f"Agent columns: {agent_cols}")

# Identify scenario columns (scenario.*)
scenario_cols = [c for c in df.columns if c.startswith('scenario.')]
print(f"Scenario columns: {scenario_cols}")

# Identify question text columns (question_text.*)
question_text_cols = [c for c in df.columns if c.startswith('question_text.')]
print(f"Question text columns: {question_text_cols}")

# Identify question option columns (question_options.*)
question_options_cols = [c for c in df.columns if c.startswith('question_options.')]
print(f"Question options columns: {question_options_cols}")

# Identify question type columns (question_type.*)
question_type_cols = [c for c in df.columns if c.startswith('question_type.')]
print(f"Question type columns: {question_type_cols}")
```

### 6. Generate Analysis Report

Create a comprehensive `report.md` with:

#### Structure

```markdown
# Results Analysis Report

## Study Design

### Questions

[For EACH question in the survey, show:]

#### Q1: [question_name] ([question_type])

**Template:** [The raw question template text from question_text.* column]

**Options:** [The options from question_options.* column, if applicable]

**Realized versions:**

[If the question uses scenario variables (Jinja2 templates like {{ var }}), show a table
of ALL unique realized question texts across scenario conditions. Group by scenario
variables to show what each condition looked like.]

| Scenario Condition | Realized Question Text |
|--------------------|----------------------|
| [condition 1]      | [full realized text] |
| [condition 2]      | [full realized text] |
...

[Repeat for each question]

### Scenario Variables

[Show ALL scenario variables and their unique values]

| Variable | Unique Values |
|----------|--------------|
| scenario.domain | health_insurance, software_platform, ... |
| scenario.framing | neutral, status_quo |
...

### Scenario Matrix

[Show the full crossing of scenario variables as a table, so the reader can see
every unique experimental condition. Include the count of observations per cell.]

### Agents / Models

[Show the models or agents used, their configuration (temperature, etc.),
and how many responses each produced]

## Data Summary
- Number of responses: N
- Agent traits collected: [list]
- Scenarios tested: [list]

## Detailed Results

### Q1: [Question Name]
[Response distribution table]
![Question 1 visualization](q1_distribution.png)
[Interpretation of results]

### Q2: [Question Name]
[Same pattern - table, visualization, interpretation together]

## Key Findings
[Main insights from the data]

## Cross-Tabulations (if applicable)
[Relationships between variables - only include agent breakdowns if agents have meaningful names, not UUIDs]

## Files Generated

| File | Description |
|------|-------------|
| [survey.md](survey.md) | Survey documentation |
| [survey.mermaid](survey.mermaid) | Survey flow diagram |
| [results.csv](results.csv) | Raw results data |
| [report.html](report.html) | This report (HTML) |
```

#### Generating the Study Design Section

The Study Design section is critical — it should make the report **self-contained** so a reader understands exactly what was asked without needing to open separate files.

**For each question**, extract the realized text from the data:

```python
# Get unique realized question texts per scenario condition
for qt_col in question_text_cols:
    q_name = qt_col.replace('question_text.', '').replace('_question_text', '')
    template = df[qt_col].iloc[0]  # Template text (may have {{ var }} syntax)

    # Check if question uses scenario variables by looking at prompt columns
    # The actual realized text (with scenarios filled in) is in the prompt.* columns
    prompt_col = f'prompt.{q_name}_user_prompt'
    if prompt_col in df.columns:
        # Extract unique realized prompts grouped by scenario conditions
        if scenario_cols:
            # Group by scenario variables to show each condition
            groups = df.groupby([c for c in scenario_cols if df[c].nunique() > 1])
            for name, group in groups:
                realized_text = group[prompt_col].iloc[0]
                # Include in report table
```

**For scenario variables**, enumerate all unique values:

```python
for col in scenario_cols:
    unique_vals = df[col].dropna().unique()
    # Show variable name (without 'scenario.' prefix) and all its values
```

**For the scenario matrix**, show the full experimental design:

```python
# Cross-tabulate scenario variables to show the design
if len(scenario_cols) >= 2:
    # Pick the most meaningful scenario columns (skip index/id columns)
    meaningful_scenario_cols = [c for c in scenario_cols
                                 if not c.endswith('_index') and not c.endswith('_id')]
    # Show unique combinations and observation counts
    design = df.groupby(meaningful_scenario_cols).size().reset_index(name='n_observations')
```

**IMPORTANT:** When listing files in the report, always use relative hyperlinks (e.g., `[survey.md](survey.md)`) so users can click through to the files.

**IMPORTANT:**
- Do NOT include mermaid diagrams in the report (they often don't render correctly in HTML output). The mermaid file is still exported separately for reference.
- Only include per-agent analysis if agents have meaningful names (not UUIDs). Check if agent names look like UUIDs (36-character strings with hyphens in pattern 8-4-4-4-12) and skip agent breakdowns if so.

**IMPORTANT:** Place each visualization immediately after its corresponding question's data table, not in a separate section at the end. This keeps the analysis coherent and easy to follow.

#### Generate Visualizations (Inline with Questions)

For each question, generate and save a visualization, then reference it in the report immediately after the question's statistics:

```python
import matplotlib.pyplot as plt

# For each question, generate chart and include in report immediately
for col in answer_cols:
    question_name = col.replace('answer.', '')
    value_counts = df[col].value_counts()

    # Add question section to report
    report += f"### {question_name}\n\n"
    report += "[Response distribution table here]\n\n"

    # Generate and save chart
    if len(value_counts) <= 20:
        fig, ax = plt.subplots(figsize=(10, 6))
        value_counts.plot(kind='bar', ax=ax)
        ax.set_title(f'Response Distribution: {question_name}')
        ax.set_xlabel('Response')
        ax.set_ylabel('Count')
        plt.tight_layout()
        chart_path = f"{question_name}_distribution.png"
        plt.savefig(f'{output_dir}/{chart_path}', dpi=150)
        plt.close()

        # Include chart immediately after question data
        report += f"![{question_name} distribution]({chart_path})\n\n"

    report += "[Interpretation of this question's results]\n\n"
```

### 7. Save All Outputs

Ensure all files are saved to the output directory:

```
output_dir/
├── survey.md          # Survey in markdown format
├── survey.mermaid     # Survey flow diagram
├── results.csv        # Full results data
├── report.md          # Analysis report
├── report.html        # Styled HTML report
├── *.png              # Visualization files
└── analysis.py        # Optional: reproducible analysis script
```

### 8. Generate HTML Report with Pandoc

After saving `report.md`, convert it to a styled HTML report using pandoc:

```bash
# Locate the bundled CSS using Glob("**/assets/report.css")
CSS_FILE="<discovered_css_path>"

# Generate HTML report (no --metadata title to avoid duplicate with markdown h1)
pandoc "${output_dir}/report.md" \
    -o "${output_dir}/report.html" \
    --css="${CSS_FILE}" \
    --standalone
```

Or in Python:

```python
import subprocess
import os

# Locate the bundled CSS file
# Use Glob("**/assets/report.css") to find the path, then:
import glob as g
css_matches = g.glob("**/assets/report.css", recursive=True)
css_file = css_matches[0] if css_matches else None
# Note: Don't use --metadata title= since report.md already has # heading
subprocess.run([
    "pandoc",
    f"{output_dir}/report.md",
    "-o", f"{output_dir}/report.html",
    f"--css={css_file}",
    "--standalone"
], check=True)
print(f"Generated: {output_dir}/report.html")
```

**Note:** The mermaid diagram is exported separately as `survey.mermaid` but not embedded in the report due to rendering issues in HTML output.

## Complete Example Script

```python
"""
EDSL Results Analysis Script
"""
from edsl import Results
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from datetime import datetime

# === CONFIGURATION ===
# Modify this to load your results
RESULTS_UUID = "123e4567-e89b-12d3-a456-426614174000"  # Or use file path
# RESULTS_PATH = "./results.json.gz"

# === LOAD RESULTS ===
results = Results.pull(RESULTS_UUID)
# results = Results.load(RESULTS_PATH)

# === CREATE OUTPUT DIRECTORY ===
import glob
existing = glob.glob("./analysis_*")
existing_nums = []
for d in existing:
    try:
        num = int(d.split("_")[-1])
        existing_nums.append(num)
    except ValueError:
        pass
next_num = max(existing_nums, default=0) + 1
output_dir = f"./analysis_{next_num}"
os.makedirs(output_dir, exist_ok=True)

# === EXPORT DOCUMENTATION ===
survey = results.survey

# Survey markdown
with open(f"{output_dir}/survey.md", "w") as f:
    f.write(survey.to_markdown())

# Survey mermaid (sanitize HTML tags for mermaid v11+ compatibility)
survey_mermaid = survey.to_mermaid()
survey_mermaid = re.sub(r'<b>|</b>|<br/>', '\n', survey_mermaid)
survey_mermaid = re.sub(r'\n+', '\n', survey_mermaid)
with open(f"{output_dir}/survey.mermaid", "w") as f:
    f.write(survey_mermaid)

# Results CSV
results_csv = results.to_csv()
results_csv.write(f"{output_dir}/results.csv")

# === LOAD DATA FOR ANALYSIS ===
df = pd.read_csv(f"{output_dir}/results.csv")

# Identify column types
answer_cols = [c for c in df.columns if c.startswith('answer.')]
agent_cols = [c for c in df.columns if c.startswith('agent.')]
scenario_cols = [c for c in df.columns if c.startswith('scenario.')]

# === HELPER: Check if string looks like a UUID ===
import re
def is_uuid(s):
    """Check if a string looks like a UUID (8-4-4-4-12 hex pattern)."""
    if not isinstance(s, str):
        return False
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, s.lower()))

# Check if agents have meaningful names (not UUIDs)
has_meaningful_agents = False
if 'agent.agent_name' in df.columns:
    agent_names = df['agent.agent_name'].dropna().unique()
    has_meaningful_agents = len(agent_names) > 0 and not all(is_uuid(str(name)) for name in agent_names)

# === GENERATE STUDY DESIGN SECTION ===
# Identify column types for study design
question_text_cols = [c for c in df.columns if c.startswith('question_text.')]
question_options_cols = [c for c in df.columns if c.startswith('question_options.')]
question_type_cols = [c for c in df.columns if c.startswith('question_type.')]
prompt_cols = [c for c in df.columns if c.startswith('prompt.') and c.endswith('_user_prompt')]
model_cols = [c for c in df.columns if c.startswith('model.')]

study_design = ""

# --- Questions section ---
study_design += "## Study Design\n\n### Questions\n\n"

for qt_col in question_text_cols:
    q_name = qt_col.replace('question_text.', '').replace('_question_text', '')
    template = str(df[qt_col].iloc[0])

    # Get question type
    qt_type_col = f'question_type.{q_name}_question_type'
    q_type = str(df[qt_type_col].iloc[0]) if qt_type_col in df.columns else 'unknown'

    # Get question options
    qo_col = f'question_options.{q_name}_question_options'
    q_options = str(df[qo_col].iloc[0]) if qo_col in df.columns and df[qo_col].notna().any() else None

    study_design += f"#### {q_name} ({q_type})\n\n"
    study_design += f"**Template:** {template}\n\n"
    if q_options and q_options != 'nan':
        study_design += f"**Options:** {q_options}\n\n"

    # Show realized versions if scenarios exist
    # Use the prompt column which has the fully realized text
    prompt_col = f'prompt.{q_name}_user_prompt'
    if prompt_col in df.columns and scenario_cols:
        meaningful_scenario_cols = [c for c in scenario_cols
                                     if not c.endswith('_index') and df[c].nunique() > 1]
        if meaningful_scenario_cols:
            # Get unique realized prompts per scenario combination
            unique_prompts = df.groupby(meaningful_scenario_cols)[prompt_col].first().reset_index()
            if len(unique_prompts) > 1:  # Only show if there are actual variations
                study_design += "**Realized versions by scenario:**\n\n"
                study_design += "| " + " | ".join(c.replace('scenario.', '') for c in meaningful_scenario_cols) + " | Question Text |\n"
                study_design += "| " + " | ".join("---" for _ in meaningful_scenario_cols) + " | --- |\n"
                for _, row in unique_prompts.iterrows():
                    conditions = " | ".join(str(row[c]) for c in meaningful_scenario_cols)
                    # Truncate very long prompts for the table; show key differences
                    prompt_text = str(row[prompt_col]).replace('\n', ' ').replace('|', '\\|')
                    if len(prompt_text) > 200:
                        prompt_text = prompt_text[:200] + "..."
                    study_design += f"| {conditions} | {prompt_text} |\n"
                study_design += "\n"

    study_design += "\n"

# --- Scenario Variables section ---
if scenario_cols:
    study_design += "### Scenario Variables\n\n"
    study_design += "| Variable | # Unique | Values |\n"
    study_design += "|----------|----------|--------|\n"
    for col in scenario_cols:
        if not col.endswith('_index'):
            unique_vals = df[col].dropna().unique()
            vals_str = ", ".join(str(v) for v in sorted(unique_vals, key=str))
            if len(vals_str) > 150:
                vals_str = vals_str[:150] + "..."
            study_design += f"| {col.replace('scenario.', '')} | {len(unique_vals)} | {vals_str} |\n"
    study_design += "\n"

    # --- Scenario Matrix ---
    meaningful_scenario_cols = [c for c in scenario_cols
                                 if not c.endswith('_index') and not c.endswith('_id') and df[c].nunique() > 1]
    if len(meaningful_scenario_cols) >= 2:
        study_design += "### Scenario Matrix\n\n"
        design_matrix = df.groupby(meaningful_scenario_cols).size().reset_index(name='n_observations')
        study_design += design_matrix.to_markdown(index=False) + "\n\n"

# --- Agents / Models section ---
study_design += "### Agents / Models\n\n"
if 'model.model' in df.columns:
    model_info = df.groupby('model.model').size().reset_index(name='n_responses')
    study_design += "| Model | Responses |\n"
    study_design += "|-------|-----------|\n"
    for _, row in model_info.iterrows():
        study_design += f"| {row['model.model']} | {row['n_responses']} |\n"
    study_design += "\n"
    # Show model config
    config_cols = [c for c in model_cols if c not in ['model.model', 'model.model_index'] and df[c].nunique() == 1]
    if config_cols:
        study_design += "**Model configuration:** "
        configs = [f"{c.replace('model.', '')}={df[c].iloc[0]}" for c in config_cols]
        study_design += ", ".join(configs) + "\n\n"

if has_meaningful_agents:
    agent_info = df.groupby('agent.agent_name').size().reset_index(name='n_responses')
    study_design += "| Agent | Responses |\n"
    study_design += "|-------|-----------|\n"
    for _, row in agent_info.iterrows():
        study_design += f"| {row['agent.agent_name']} | {row['n_responses']} |\n"
    study_design += "\n"

# === GENERATE REPORT ===
report = f"""# Results Analysis Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{study_design}

## Data Summary

- **Total responses**: {len(df)}
- **Questions**: {len(answer_cols)}
- **Agent traits**: {len(agent_cols)} ({', '.join(agent_cols) if agent_cols else 'None'})
- **Scenario variables**: {len(scenario_cols)} ({', '.join(scenario_cols) if scenario_cols else 'None'})

## Response Distributions

"""

# Add distribution for each answer column
for col in answer_cols:
    question_name = col.replace('answer.', '')
    value_counts = df[col].value_counts()

    report += f"### {question_name}\n\n"
    report += "| Response | Count | Percentage |\n"
    report += "|----------|-------|------------|\n"
    for val, count in value_counts.items():
        pct = count / len(df) * 100
        report += f"| {val} | {count} | {pct:.1f}% |\n"
    report += "\n"

    # Generate chart
    if len(value_counts) <= 20:  # Only plot if reasonable number of categories
        fig, ax = plt.subplots(figsize=(10, 6))
        value_counts.plot(kind='bar', ax=ax)
        ax.set_title(f'Response Distribution: {question_name}')
        ax.set_xlabel('Response')
        ax.set_ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        chart_path = f"{question_name}_distribution.png"
        plt.savefig(f'{output_dir}/{chart_path}', dpi=150)
        plt.close()
        report += f"![{question_name} distribution]({chart_path})\n\n"

# Only add agent analysis if agents have meaningful names
if has_meaningful_agents:
    report += """## Analysis by Agent

"""
    # Add per-agent breakdowns here
    for col in answer_cols:
        question_name = col.replace('answer.', '')
        crosstab = pd.crosstab(df['agent.agent_name'], df[col], normalize='index') * 100
        report += f"### {question_name} by Agent\n\n"
        report += crosstab.to_markdown() + "\n\n"

report += """## Key Findings

[Add key findings based on the analysis]

## Methodology Notes

This analysis was generated from EDSL Results data. The survey was administered to AI agents
using the Expected Parrot platform.
"""

# Save report
with open(f"{output_dir}/report.md", "w") as f:
    f.write(report)

# Generate HTML report with pandoc (no --metadata title to avoid duplicate)
import subprocess

# Locate the bundled CSS file
# Use Glob("**/assets/report.css") to find the path, then:
import glob as g
css_matches = g.glob("**/assets/report.css", recursive=True)
css_file = css_matches[0] if css_matches else None
subprocess.run([
    "pandoc",
    f"{output_dir}/report.md",
    "-o", f"{output_dir}/report.html",
    f"--css={css_file}",
    "--standalone"
], check=True)

print(f"Analysis complete! Output saved to: {output_dir}/")
print(f"  - survey.md")
print(f"  - survey.mermaid")
print(f"  - results.csv")
print(f"  - report.md")
print(f"  - report.html")
```

9. Ask about PowerPoint

Use the `AskUserQuestion` if they'd like a PPTX slideshow as well. If they say yes, create a PPTX file for them based on the `report.md`
- Question: Would you like a Power Point version of the results?
-Options: Yes/No

## Output Files

| File | Description |
|------|-------------|
| `survey.md` | Human-readable survey documentation with questions, options, and rules |
| `survey.mermaid` | Mermaid diagram showing survey flow and skip logic |
| `results.csv` | Full results data in CSV format for analysis |
| `report.md` | Comprehensive analysis report with findings and visualizations |
| `report.html` | Styled HTML report (via pandoc with Expected Parrot CSS) |
| `*.png` | Charts and visualizations referenced in the report |
| `analysis.py` | (Optional) Reproducible Python script for the analysis |

## Output options



## Tips

- Check `survey.mermaid` separately to understand skip logic before analyzing
- Look for patterns in agent traits vs. responses (only if agents have meaningful names, not UUIDs)
- Compare responses across scenarios (if scenarios were used)
- The `answer.*` columns contain question responses
- The `agent.*` columns contain agent trait values
- The `scenario.*` columns contain scenario variable values
- Use `comment.*` columns to see free-text explanations (if available)
- Per-agent breakdowns are automatically skipped when agent names are UUIDs (not meaningful for analysis)

## Common Analysis Patterns

### Cross-tabulation by Scenario

```python
# Compare responses across scenarios
pd.crosstab(df['scenario.condition'], df['answer.question_name'], normalize='index')
```

### Agent Trait Analysis

```python
# First check if agents have meaningful names (not UUIDs)
import re
def is_uuid(s):
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, str(s).lower()))

# Only analyze by agent if names are meaningful
if not all(is_uuid(name) for name in df['agent.agent_name'].dropna().unique()):
    df.groupby('agent.agent_name')['answer.question_name'].value_counts(normalize=True)
```

### Response Correlation

```python
# For numeric responses
df[[c for c in answer_cols if df[c].dtype in ['int64', 'float64']]].corr()
```
