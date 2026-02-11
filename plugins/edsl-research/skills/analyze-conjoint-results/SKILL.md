---
name: analyze-conjoint-results
description: Generate a comprehensive, self-contained analysis report for a conjoint (choice-based) study with executive summary, methodology, part-worth utilities, segment analysis, and limitations
allowed-tools: Read, Write, Glob, Grep, Bash(python3:*), Bash(pandoc *), Bash(cp *), AskUserQuestion
user-invocable: true
arguments: path to conjoint study directory (optional)
---

# Analyze Conjoint Results

Generates a comprehensive, self-contained HTML report for a conjoint analysis study. Reads design artifacts, computes part-worth utilities, generates charts, and writes a report covering executive summary, methodology, design quality, results, segment analysis, key findings, and limitations.

## Usage

```
/analyze-conjoint-results 2026-02-11_demand-and-price-sensitivity-for-frozen-chicken
/analyze-conjoint-results           # auto-detects study directory
```

## Workflow

### Phase 0: Setup and Discovery

1. **Read the report-reference skill** for quality guidelines:
```
Use Glob("**/report-reference/SKILL.md") to find it, then Read it.
```
Follow all guidelines from that reference throughout report generation.

2. **Locate helpers.py:**
```
Use Glob("**/conjoint-study/helpers.py") to find it. Store the path.
```

3. **Locate the study directory.** If the user provided a path argument, use it. Otherwise, auto-detect:
```
Use Glob("**/design_spec.json") to find directories containing conjoint study artifacts.
```
If multiple are found, use AskUserQuestion to let the user pick. The study directory must contain at least:
- `design_spec.json`
- `results.csv` (or `results.json.gz`)
- `conjoint_choice_sets.json`
- `study_agent_list.py`

4. **Create the output directory** inside the study directory:
```python
import os, glob

existing = glob.glob(os.path.join(study_dir, "analysis_*"))
existing_nums = []
for d in existing:
    try:
        num = int(os.path.basename(d).split("_")[-1])
        existing_nums.append(num)
    except ValueError:
        pass
next_num = max(existing_nums, default=0) + 1
output_dir = os.path.join(study_dir, f"analysis_{next_num}")
os.makedirs(output_dir, exist_ok=True)
```

5. **Locate report.css:**
```
Use Glob("**/assets/report.css") to find it. Store the path.
```

### Phase 1: Load All Study Artifacts

Read these files from the study directory:

```python
import json, csv, os

# 1. Design specification
with open(os.path.join(study_dir, "design_spec.json")) as f:
    design_spec = json.load(f)

attributes = design_spec["attributes"]       # dict: attr_name -> [levels]
n_tasks = design_spec.get("tasks_per_version", 8)
profiles_per_task = design_spec.get("profiles_per_task", 3)
n_versions = design_spec.get("n_versions", 4)
include_none = design_spec.get("include_none", False)

# 2. Choice sets (for example tasks)
with open(os.path.join(study_dir, "conjoint_choice_sets.json")) as f:
    choice_sets = json.load(f)

# 3. Agent list (parse the Python file to extract persona descriptions)
# Read study_agent_list.py as text and extract persona/segment traits
agent_file = os.path.join(study_dir, "study_agent_list.py")
```

**Parse agents from `study_agent_list.py`:** Read the file as text and extract all `Agent(traits={...})` blocks. For each agent, capture:
- `segment` trait (used as display label)
- `persona` trait (full description, never truncate)
- Any other traits

```python
import ast, re

agent_source = open(agent_file).read()

# Extract Agent constructors
agents = []
for match in re.finditer(r'Agent\(traits=(\{[^}]+\})\)', agent_source):
    traits_str = match.group(1)
    try:
        traits = ast.literal_eval(traits_str)
        agents.append(traits)
    except:
        pass
```

### Phase 2: Run Utility Computation

Call the existing `helpers.py analyze` command to compute utilities:

```bash
python3 <helpers_path> analyze <study_dir>/results.csv <study_dir>/design_spec.json --output-dir <output_dir>
```

This produces in `output_dir`:
- `utilities.json` — part-worth utilities and importance weights
- `utilities.csv` — utilities in tabular form
- `conjoint_report.md` — basic report (we will replace this with a comprehensive one)
- `segment_analysis.json` — per-segment utilities (if agents exist)
- `generate_charts.py` — chart generation script

Then load the computed results:

```python
with open(os.path.join(output_dir, "utilities.json")) as f:
    util_data = json.load(f)

utilities = util_data["utilities"]
importance = util_data["importance"]
n_observations = util_data["n_observations"]

# Load segment analysis if it exists
segment_path = os.path.join(output_dir, "segment_analysis.json")
segment_data = None
if os.path.exists(segment_path):
    with open(segment_path) as f:
        segment_data = json.load(f)
```

### Phase 3: Generate Charts

Generate all charts in the output directory. Use `#4C78A8` as primary color and `#E45756` for negative values.

#### 3a. Attribute Importance Chart

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

attrs_sorted = sorted(importance, key=importance.get, reverse=True)
vals = [importance[a] for a in attrs_sorted]

fig, ax = plt.subplots(figsize=(10, max(4, len(attrs_sorted) * 0.8)))
bars = ax.barh(attrs_sorted, vals, color="#4C78A8")
ax.set_xlabel("Importance (%)")
ax.set_title("Attribute Importance")
ax.invert_yaxis()
for bar, val in zip(bars, vals):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "importance_chart.png"), dpi=150, bbox_inches="tight")
plt.close()
```

#### 3b. Part-Worth Utilities Chart

```python
n_attrs = len(utilities)
fig, axes = plt.subplots(1, n_attrs, figsize=(4 * n_attrs, max(4, max(len(v) for v in attributes.values()) * 0.8)))
if n_attrs == 1:
    axes = [axes]

for ax, attr_name in zip(axes, attrs_sorted):
    attr_utils = utilities[attr_name]
    levels = sorted(attr_utils, key=attr_utils.get, reverse=True)
    vals = [attr_utils[l] for l in levels]
    colors = ["#4C78A8" if v >= 0 else "#E45756" for v in vals]
    ax.barh(levels, vals, color=colors)
    ax.set_title(attr_name.replace("_", " ").title())
    ax.axvline(x=0, color="gray", linewidth=0.5)
    ax.invert_yaxis()

plt.suptitle("Part-Worth Utilities", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "utilities_chart.png"), dpi=150, bbox_inches="tight")
plt.close()
```

#### 3c. Position Bias Chart

Check whether position (Option A/B/C) is equally chosen across all tasks:

```python
import pandas as pd

df = pd.read_csv(os.path.join(study_dir, "results.csv"))

# Count position choices across all tasks
position_counts = {}
for t in range(1, n_tasks + 1):
    col = f"answer.choice_task_{t}"
    if col in df.columns:
        for val in df[col].dropna():
            position_counts[val] = position_counts.get(val, 0) + 1

positions = sorted(position_counts.keys())
counts = [position_counts[p] for p in positions]
total = sum(counts)
expected = total / len(positions) if positions else 1

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(positions, counts, color="#4C78A8")
ax.axhline(y=expected, color="#E45756", linestyle="--", label=f"Expected ({expected:.0f})")
ax.set_xlabel("Option Chosen")
ax.set_ylabel("Count")
ax.set_title("Position Bias Check")
ax.legend()

for bar, count in zip(bars, counts):
    pct = count / total * 100 if total > 0 else 0
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{pct:.1f}%", ha="center", va="bottom")

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "position_bias_chart.png"), dpi=150, bbox_inches="tight")
plt.close()
```

#### 3d. Price Sensitivity Chart (if price attribute exists)

If any attribute name contains "price" (case-insensitive), generate a dedicated price chart:

```python
price_attr = None
for attr_name in attributes:
    if "price" in attr_name.lower():
        price_attr = attr_name
        break

if price_attr:
    price_utils = utilities[price_attr]
    # Sort levels by numeric value extracted from the level string
    import re as re_mod
    def extract_number(s):
        m = re_mod.search(r'[\d.]+', s)
        return float(m.group()) if m else 0

    levels_sorted = sorted(price_utils.keys(), key=extract_number)
    vals = [price_utils[l] for l in levels_sorted]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(levels_sorted, vals, marker="o", linewidth=2, color="#4C78A8", markersize=8)
    ax.fill_between(range(len(levels_sorted)), vals, alpha=0.1, color="#4C78A8")
    ax.set_xlabel(price_attr.replace("_", " ").title())
    ax.set_ylabel("Part-Worth Utility")
    ax.set_title("Price Sensitivity")
    ax.axhline(y=0, color="gray", linewidth=0.5)
    ax.set_xticks(range(len(levels_sorted)))
    ax.set_xticklabels(levels_sorted)

    for i, (level, val) in enumerate(zip(levels_sorted, vals)):
        ax.annotate(f"{val:+.3f}", (i, val), textcoords="offset points",
                    xytext=(0, 10), ha="center")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "price_sensitivity_chart.png"), dpi=150, bbox_inches="tight")
    plt.close()
```

#### 3e. Segment Importance Heatmap (if segment data exists)

```python
if segment_data and "segment" in segment_data:
    seg_importance = segment_data["segment"]

    segments = sorted(seg_importance.keys())
    all_attrs = attrs_sorted  # use importance-sorted order

    heatmap_data = []
    for seg in segments:
        row = []
        seg_imp = seg_importance[seg]["importance"]
        for attr in all_attrs:
            row.append(seg_imp.get(attr, 0))
        heatmap_data.append(row)

    heatmap_array = np.array(heatmap_data)

    fig, ax = plt.subplots(figsize=(max(8, len(all_attrs) * 1.5), max(5, len(segments) * 0.7)))
    im = ax.imshow(heatmap_array, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(all_attrs)))
    ax.set_xticklabels([a.replace("_", " ").title() for a in all_attrs], rotation=45, ha="right")
    ax.set_yticks(range(len(segments)))
    ax.set_yticklabels([s.replace("_", " ").title() for s in segments])

    # Add text annotations
    for i in range(len(segments)):
        for j in range(len(all_attrs)):
            val = heatmap_array[i, j]
            color = "white" if val > heatmap_array.max() * 0.7 else "black"
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center", color=color, fontsize=9)

    ax.set_title("Attribute Importance by Segment (%)")
    plt.colorbar(im, label="Importance (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "segment_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close()
```

### Phase 4: Build the Report

Build `report.md` with the following sections. **Claude must write all prose sections** — do not use placeholder text.

#### Report Structure

```markdown
# Conjoint Analysis Report: [Research Question / Product Category]

*Generated: YYYY-MM-DD HH:MM:SS*

## Executive Summary

[Claude writes 1 paragraph stating the research question, the method used, the sample, and 3-5 quantified key findings. End with the optimal product configuration.]

**Optimal product configuration:** [List each attribute and its highest-utility level]

## Study Design

### Attributes and Levels

| Attribute | Levels |
|-----------|--------|
| [attr1]   | [level1, level2, ...] |
| ...       | ... |

### Design Parameters

| Parameter | Value |
|-----------|-------|
| Method | Choice-Based Conjoint (CBC) |
| Tasks per respondent | [N] |
| Profiles per task | [N] |
| Design versions | [N] |
| Include "None" option | [Yes/No] |
| Total unique profiles | [N] |
| Total choice observations | [N] |

### Example Choice Tasks

[Show 1-2 REALIZED choice tasks from conjoint_choice_sets.json — not raw templates.
Format as the respondent would see them:]

> **Choice Task 1 (Version 1):**
>
> | Attribute | Option A | Option B | Option C |
> |-----------|----------|----------|----------|
> | Price     | $6.99    | $12.99   | $8.99    |
> | Pack Size | 24 wings | 8 wings  | 16 wings |
> | ...       | ...      | ...      | ...      |
>
> *Which option would you choose?*

[Show a second example from a different task or version.]

### Respondent Segments

[For EACH agent, show the segment label as a header and the FULL persona description. Never truncate.]

| Segment | Persona Description |
|---------|-------------------|
| [segment_label] | [Full persona text — do not truncate] |
| ... | ... |

**Total respondents:** [N segments] x [N design versions] = [N total response sets]

## Methodology

### Choice-Based Conjoint Analysis

Choice-Based Conjoint (CBC) is a stated-preference methodology where respondents evaluate sets of product profiles defined by multiple attributes and choose their preferred option. By observing which attribute combinations are chosen, we estimate the relative value (part-worth utility) each attribute level contributes to overall preference.

### Experimental Design

The experimental design was generated using a randomized search algorithm that optimizes for:
- **Level balance:** Each attribute level appears approximately equally often
- **Minimum attribute differences:** Profiles within each choice task differ on at least [N] attributes
- **Position debiasing:** Profile presentation order is shuffled across design versions

### Utility Estimation

Part-worth utilities are computed using a counting-based approach:

```
utility(level) = log(choice_share / expected_share)
```

Where `choice_share` is the proportion of times a level was present in the chosen profile, and `expected_share` is 1/(number of levels). Utilities are zero-centered within each attribute.

**Attribute importance** is computed as the range of utilities within an attribute divided by the sum of all ranges:

```
importance(attr) = range(attr_utilities) / sum(all_ranges) × 100
```

### LLM Agent Simulation

Respondents in this study are simulated using large language model (LLM) agents, each assigned a distinct persona. Each agent independently evaluates the choice tasks based on its persona characteristics. This approach enables rapid, cost-effective preference estimation, though results should be validated against human respondent data for high-stakes decisions.

## Design Quality

### Position Bias

![Position Bias Check](position_bias_chart.png)

[Claude writes 1-2 sentences interpreting the position bias chart. Are options chosen roughly equally? Any concerning bias?]

### Design Balance

| Version | Balance Score |
|---------|--------------|
| [1]     | [score]      |
| ...     | ...          |

[Claude writes 1 sentence interpreting balance scores. Lower is better.]

## Overall Results

### Attribute Importance

![Attribute Importance](importance_chart.png)

| Attribute | Importance (%) |
|-----------|---------------|
| [attr]    | [value]       |
| ...       | ...           |

[Claude writes 2-3 sentences interpreting the importance rankings.]

### Part-Worth Utilities

![Part-Worth Utilities](utilities_chart.png)

[For EACH attribute, show a utility table:]

#### [Attribute Name] ([importance]%)

| Level | Utility |
|-------|---------|
| [level] | [+/-value] |
| ...     | ...        |

[Claude writes 1-2 sentences interpreting this attribute's utilities.]

### Optimal Product Configuration

Based on the highest part-worth utility for each attribute:

| Attribute | Optimal Level | Utility |
|-----------|--------------|---------|
| [attr]    | [best level] | [value] |
| ...       | ...          | ...     |

## Price Sensitivity

[ONLY include this section if a price attribute exists.]

![Price Sensitivity](price_sensitivity_chart.png)

[Claude writes 2-3 sentences about the price-utility relationship. Is it monotonically decreasing? Any interesting non-linearities?]

## Segment Analysis

### Importance Comparison Across Segments

![Segment Importance Heatmap](segment_heatmap.png)

[Claude writes 2-3 sentences comparing which segments weight which attributes most heavily.]

### Per-Segment Utilities

[For EACH segment, show:]

#### [Segment Label]: [Full Persona Description]

**Top priorities:** [List top 2-3 attributes by importance for this segment]

| Attribute | Importance (%) |
|-----------|---------------|
| ...       | ...           |

**Optimal product for this segment:**

| Attribute | Preferred Level | Utility |
|-----------|----------------|---------|
| ...       | ...            | ...     |

[Claude writes 1-2 sentences about what distinguishes this segment.]

## Key Findings

[Claude writes 4-6 substantive paragraphs. Each paragraph should make a specific, quantified claim and explain its practical implications. Example topics:

1. Which attribute dominates preference and by how much
2. Price sensitivity patterns and willingness-to-pay implications
3. The most/least preferred levels within key attributes
4. Segment differences — which segments diverge most and on what
5. The optimal product configuration and how much utility it captures
6. Surprising findings or counter-intuitive patterns]

## Limitations

1. **LLM agent simulation:** Respondents are AI agents, not human consumers. Preferences may not perfectly reflect real-world purchase behavior. Results should be validated with human respondent studies before making high-stakes business decisions.

2. **Sample size:** With [N] design versions and [N] agent segments, the effective sample size is [N] response sets. Larger samples would increase confidence in utility estimates.

3. **Ecological validity:** Choice tasks present simplified attribute descriptions. Real purchase decisions involve additional factors (brand loyalty, shelf placement, availability) not captured here.

4. **Counting-based utilities:** The utility estimation uses a simple counting method rather than hierarchical Bayes or mixed logit. This may underestimate heterogeneity within segments.

5. **Attribute independence:** The model assumes attributes contribute independently to utility. Interaction effects (e.g., price × brand) are not estimated.

## Files Generated

| File | Description |
|------|-------------|
| [report.md](report.md) | This report in Markdown format |
| [report.html](report.html) | Styled HTML version of this report |
| [utilities.json](utilities.json) | Part-worth utilities and importance weights |
| [utilities.csv](utilities.csv) | Utilities in tabular format |
| [segment_analysis.json](segment_analysis.json) | Per-segment utility estimates |
| [importance_chart.png](importance_chart.png) | Attribute importance bar chart |
| [utilities_chart.png](utilities_chart.png) | Part-worth utilities by attribute |
| [position_bias_chart.png](position_bias_chart.png) | Position bias check |
| [price_sensitivity_chart.png](price_sensitivity_chart.png) | Price-utility curve (if applicable) |
| [segment_heatmap.png](segment_heatmap.png) | Cross-segment importance comparison |
```

### Phase 5: Write Report and Convert to HTML

1. **Write `report.md`** to the output directory. Claude must fill in ALL prose sections with substantive content based on the actual data — no placeholders.

2. **Convert to HTML:**
```bash
pandoc <output_dir>/report.md -o <output_dir>/report.html --css=<css_path> --standalone
```

3. **Verify the report:**
   - No `{{ }}` template syntax in the body
   - No `../` image paths
   - All image files exist in the output directory
   - All prose sections are filled in (no placeholder text)
   - Persona descriptions are complete (not truncated)

### Phase 6: Follow-Up

After generating the report, ask:

```
Question: "The conjoint analysis report has been generated at <output_dir>/report.html. What would you like to do next?"
Header: "Next steps"
Options:
  1. "Generate PowerPoint" - "Create a slide deck summarizing the key findings"
  2. "Run market simulation" - "Predict choice shares for specific product configurations"
  3. "Publish with /publish-study" - "Share the study and report"
  4. "Done" - "No further analysis needed"
```

If "Run market simulation", ask the user to define competing product profiles and run:
```bash
python3 <helpers_path> market-sim <output_dir>/utilities.json <profiles_file>
```

## Implementation Notes

- All chart generation must be done in a single Python script executed via Bash, or in sequential Bash calls. Do NOT attempt to run matplotlib interactively.
- The `helpers.py analyze` command is the source of truth for utility computation. Do not reimplement the counting logic.
- Always copy images into the output directory. Never use `../` paths in the report.
- The report must be fully self-contained: a reader should understand the study without opening any other files.
- Use `segment` trait values (not agent names) as display labels throughout.

## Output

The skill creates an `analysis_N/` directory inside the study directory containing:

| File | Description |
|------|-------------|
| `report.md` | Comprehensive conjoint analysis report |
| `report.html` | Styled HTML report |
| `utilities.json` | Part-worth utilities and importance |
| `utilities.csv` | Tabular utility data |
| `segment_analysis.json` | Per-segment analysis |
| `importance_chart.png` | Attribute importance chart |
| `utilities_chart.png` | Part-worth utilities chart |
| `position_bias_chart.png` | Position bias check |
| `price_sensitivity_chart.png` | Price sensitivity (if applicable) |
| `segment_heatmap.png` | Cross-segment heatmap |
| `generate_charts.py` | Reproducible chart script |
| `conjoint_report.md` | Basic report from helpers.py |
