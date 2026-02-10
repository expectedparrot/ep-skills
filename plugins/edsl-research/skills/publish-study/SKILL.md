---
name: publish-study
description: Publish a completed study to GitHub - creates a repo with the analysis report as README.md, all charts, data, and a reproducibility footer linking to Expected Parrot
allowed-tools: Read, Glob, Grep, Bash(python3:*), Bash(gh *), Bash(git *), Bash(cp *), Bash(mkdir *), Write, AskUserQuestion
user-invocable: true
arguments: study_dir
---

# Publish Study

Takes a completed study directory (containing results, an experiment design, and an analysis report) and publishes it as a GitHub repository. The analysis report becomes `README.md` so it renders nicely on GitHub.

## Usage

```
/publish-study
/publish-study 2026-02-08_do-llms-exhibit-maternal-default-bias-when
```

If no study directory is specified, auto-detect from the current working directory by looking for directories matching `YYYY-MM-DD_*`.

## Workflow

### 1. Locate the Study Directory

If a directory was provided, confirm it exists. Otherwise, find candidates:

```python
import glob
import os

candidates = sorted(glob.glob("./[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_*"), key=os.path.getmtime, reverse=True)
candidates = [d for d in candidates if os.path.isdir(d)]
```

- **If zero candidates**, tell the user no study directories were found.
- **If exactly one**, use it automatically.
- **If multiple**, use `AskUserQuestion` to let the user pick:

```
Question: "Which study do you want to publish?"
Header: "Study"
Options: [list each directory as an option with its name as label and first line of experiment_design.md as description]
```

### 2. Select the Analysis

Find `analysis_N/` subdirectories that contain `report.md`:

```python
import os, glob

analysis_dirs = sorted(glob.glob(f"{study_dir}/analysis_*/"))
with_reports = [d for d in analysis_dirs if os.path.isfile(os.path.join(d, "report.md"))]
```

- **If zero**, tell the user to run `/analyze-results` first.
- **If exactly one**, use it automatically.
- **If multiple**, use `AskUserQuestion` to let the user pick which analysis to feature as the README:

```
Question: "Which analysis should be the primary report (README.md)?"
Header: "Analysis"
Options: [list each analysis_N with first line of its report.md as description]
```

### 3. Ensure Results Are on Expected Parrot

Check for `results.json.gz` in the study directory and push it to Expected Parrot so the repo can link to it for reproducibility.

```python
from edsl import Results

results = Results.load(f"{study_dir}/results")  # loads results.json.gz

# Push to Expected Parrot (unlisted by default)
info = results.push(description="Results for: <study_slug>")

# Extract the UUID and URL from the push response
# info is a dict with 'uuid' and 'url' keys
results_uuid = info["uuid"]
results_url = info["url"]
print(f"Results pushed: {results_url}")
print(f"UUID: {results_uuid}")
```

If the push fails or `results.json.gz` doesn't exist, warn the user but continue — the reproducibility section will note that results are not available on Expected Parrot.

### 4. Stage Repo Contents

Build the repository contents in a temporary directory. Copy files from the study and analysis directories:

```bash
# Create temp staging directory
mkdir -p /tmp/publish-study-staging
mkdir -p /tmp/publish-study-staging/images
mkdir -p /tmp/publish-study-staging/data
mkdir -p /tmp/publish-study-staging/questions
```

#### File Mapping

| Source | Destination in Repo | Notes |
|--------|-------------------|-------|
| `analysis_N/report.md` | `README.md` | Rewrite image/data paths, append reproducibility footer |
| `analysis_N/*.png` | `images/*.png` | All chart PNGs from the analysis |
| `experiment_design.md` | `experiment_design.md` | Research design document |
| `*_study.py` (or similar) | `study.py` | The experiment script |
| `analysis_N/survey.md` | `survey.md` | Survey documentation |
| `analysis_N/results.csv` | `data/results.csv` | Tabular results |
| `analysis_N/<slug>/answer.md` | `questions/<slug>.md` | Answer-question outputs (if any) |
| `analysis_N/<slug>/*.png` | `questions/<slug>/*.png` | Answer charts (if any) |
| — | `LICENSE` | MIT license (generated) |

#### Copy Commands

```bash
STUDY_DIR="<study_dir>"
ANALYSIS_DIR="<analysis_dir>"
STAGING="/tmp/publish-study-staging"

# Clean staging area
rm -rf "$STAGING"
mkdir -p "$STAGING/images" "$STAGING/data" "$STAGING/questions"

# Copy analysis PNGs to images/
cp "$ANALYSIS_DIR"/*.png "$STAGING/images/" 2>/dev/null || true

# Copy experiment design
cp "$STUDY_DIR/experiment_design.md" "$STAGING/experiment_design.md" 2>/dev/null || true

# Copy study script (find the *_study.py or similar)
cp "$STUDY_DIR"/*_study.py "$STAGING/study.py" 2>/dev/null || \
cp "$STUDY_DIR"/*_survey.py "$STAGING/study.py" 2>/dev/null || \
cp "$STUDY_DIR"/*.py "$STAGING/study.py" 2>/dev/null || true

# Copy survey documentation
cp "$ANALYSIS_DIR/survey.md" "$STAGING/survey.md" 2>/dev/null || true

# Copy results CSV
cp "$ANALYSIS_DIR/results.csv" "$STAGING/data/results.csv" 2>/dev/null || true
```

#### Copy Answer-Question Outputs

Check for subdirectories inside the analysis directory that contain `answer.md`:

```python
import glob, os, shutil

staging = "/tmp/publish-study-staging"
analysis_dir = "<analysis_dir>"

answer_dirs = [d for d in glob.glob(f"{analysis_dir}/*/")
               if os.path.isfile(os.path.join(d, "answer.md"))]

for answer_dir in answer_dirs:
    slug = os.path.basename(answer_dir.rstrip("/"))
    dest = f"{staging}/questions/{slug}"
    os.makedirs(dest, exist_ok=True)

    # Copy answer.md as <slug>.md
    shutil.copy2(f"{answer_dir}/answer.md", f"{staging}/questions/{slug}.md")

    # Copy any PNGs
    for png in glob.glob(f"{answer_dir}/*.png"):
        os.makedirs(f"{dest}", exist_ok=True)
        shutil.copy2(png, f"{dest}/{os.path.basename(png)}")
```

### 5. Generate README.md

Read the original `report.md` and apply three modifications:

```python
import re

with open(f"{analysis_dir}/report.md", "r") as f:
    readme = f.read()

# 1. Rewrite image paths: (foo.png) -> (images/foo.png)
#    Match markdown image syntax ![desc](filename.png)
readme = re.sub(
    r'(!\[[^\]]*\])\(([^/)][^)]*\.png)\)',
    r'\1(images/\2)',
    readme
)

# 2. Rewrite results.csv links: (results.csv) -> (data/results.csv)
readme = readme.replace("(results.csv)", "(data/results.csv)")

# 3. Append reproducibility footer
footer = f"""

---

## Reproducibility

This study was conducted using [Expected Parrot EDSL](https://docs.expectedparrot.com/).

### Results on Expected Parrot

The full results object is available on Expected Parrot:

- **URL:** [{results_url}]({results_url})
- **UUID:** `{results_uuid}`

### Pull the Results

```python
from edsl import Results

results = Results.pull("{results_uuid}")
df = results.to_pandas()
```

### Study Code

The experiment script is available in [`study.py`](study.py). The experimental design is documented in [`experiment_design.md`](experiment_design.md).

### License

This study and its artifacts are released under the [MIT License](LICENSE).

---

*Generated with [Expected Parrot EDSL](https://docs.expectedparrot.com/)*
"""

readme += footer

with open(f"{staging}/README.md", "w") as f:
    f.write(readme)
```

If the EP push failed (no `results_uuid`), use a simpler footer without the EP link:

```python
footer_no_ep = """

---

## Reproducibility

This study was conducted using [Expected Parrot EDSL](https://docs.expectedparrot.com/).

### Study Code

The experiment script is available in [`study.py`](study.py). The experimental design is documented in [`experiment_design.md`](experiment_design.md).

### License

This study and its artifacts are released under the [MIT License](LICENSE).

---

*Generated with [Expected Parrot EDSL](https://docs.expectedparrot.com/)*
"""
```

### 6. Generate LICENSE

Write a standard MIT license file:

```python
from datetime import datetime

year = datetime.now().year

license_text = f"""MIT License

Copyright (c) {year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

with open(f"{staging}/LICENSE", "w") as f:
    f.write(license_text)
```

### 7. Ask User for Repo Details

Use `AskUserQuestion` to confirm the repo name, visibility, and GitHub account:

```
Question: "What should the GitHub repo be named?"
Header: "Repo name"
Options:
  1. "<study-slug>" - "Default: slug from the study directory name (without date prefix)"
  2. "Custom name" - "Enter a custom repository name"
```

Then ask about visibility:

```
Question: "Should the repo be public or private?"
Header: "Visibility"
Options:
  1. "Public (Recommended)" - "Anyone can see this repository"
  2. "Private" - "Only you and collaborators can see this repository"
```

The **study slug** is derived from the directory name by stripping the date prefix:

```python
# "2026-02-08_do-llms-exhibit-maternal-default-bias-when" -> "do-llms-exhibit-maternal-default-bias-when"
study_slug = os.path.basename(study_dir).split("_", 1)[1] if "_" in os.path.basename(study_dir) else os.path.basename(study_dir)
```

### 8. Create GitHub Repo and Push

```bash
REPO_NAME="<repo_name>"
VISIBILITY="--public"  # or "--private"
STAGING="/tmp/publish-study-staging"

# Create the GitHub repo
gh repo create "$REPO_NAME" $VISIBILITY --description "Research study: <short description>"

# Initialize git in the staging directory and push
cd "$STAGING"
git init
git add .
git commit -m "Initial commit: publish study results

Generated with Expected Parrot EDSL
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# Add remote and push
git remote add origin "$(gh repo view "$REPO_NAME" --json url -q .url)"
git branch -M main
git push -u origin main
```

### 9. Report Back

Tell the user:
- The GitHub repo URL
- A summary of what was published (number of images, whether results are on EP, etc.)
- The direct link to the README (which is the repo homepage)

```
Question: (none — just report)
```

Example output:

```
Published to: https://github.com/<user>/do-llms-exhibit-maternal-default-bias-when

Repository contents:
- README.md (analysis report with 6 charts)
- experiment_design.md
- study.py
- survey.md
- data/results.csv
- images/ (6 PNGs)
- LICENSE (MIT)

Results are also available on Expected Parrot:
  https://expectedparrot.com/content/<uuid>
```

## Example: Publishing the Maternal Default Bias Study

Given a study directory:
```
2026-02-08_do-llms-exhibit-maternal-default-bias-when/
├── experiment_design.md
├── maternal_default_bias_study.py
├── results.json.gz
├── results.csv
└── analysis_1/
    ├── report.md
    ├── report.html
    ├── survey.md
    ├── results.csv
    ├── confidence_by_choice.png
    ├── context_effect_by_model.png
    ├── manipulation_check.png
    ├── maternal_default_by_model.png
    ├── maternal_default_heatmap.png
    ├── order_effect_by_model.png
    └── urgency_effect_by_model.png
```

The published repo would contain:
```
do-llms-exhibit-maternal-default-bias-when/
├── README.md                        # report.md with rewritten paths + reproducibility footer
├── experiment_design.md
├── study.py                         # maternal_default_bias_study.py
├── survey.md
├── LICENSE
├── data/
│   └── results.csv
└── images/
    ├── confidence_by_choice.png
    ├── context_effect_by_model.png
    ├── manipulation_check.png
    ├── maternal_default_by_model.png
    ├── maternal_default_heatmap.png
    ├── order_effect_by_model.png
    └── urgency_effect_by_model.png
```

## Checklist Before Publishing

- [ ] Study directory exists and contains `results.json.gz`
- [ ] At least one `analysis_N/` directory has a `report.md`
- [ ] `experiment_design.md` exists in the study directory
- [ ] A Python study script exists (e.g., `*_study.py`)
- [ ] All image paths in README.md point to `images/`
- [ ] results.csv link points to `data/results.csv`
- [ ] Reproducibility footer includes EP link (if push succeeded)
- [ ] LICENSE file is present
- [ ] GitHub repo was created successfully
- [ ] All files were committed and pushed

## Output

| File | Description |
|------|-------------|
| `README.md` | Analysis report adapted for GitHub with image paths rewritten and reproducibility footer |
| `experiment_design.md` | Full experimental design document |
| `study.py` | Python script that defines and runs the study |
| `survey.md` | Survey documentation (questions, types, options) |
| `data/results.csv` | Tabular results data |
| `images/*.png` | All analysis chart PNGs |
| `questions/<slug>.md` | Answer-question outputs (if any) |
| `questions/<slug>/*.png` | Answer-question charts (if any) |
| `LICENSE` | MIT license |

## Tips

- Run `/analyze-results` before `/publish-study` — you need at least one analysis with a `report.md`
- If you want to refine the report before publishing, edit `analysis_N/report.md` first
- The repo name defaults to the study slug (directory name without date prefix)
- Results are pushed to Expected Parrot as "unlisted" by default — change visibility on EP separately if needed
- If `gh` CLI is not authenticated, run `gh auth login` first
