---
name: design-experiment
description: Design a detailed experimental plan from a research question - includes literature review, randomization plan, survey design, power analysis, and sample size recommendation
allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, Bash(python3:*)
user-invocable: true
arguments: research_question
---

# Design Experiment

Takes a research question and produces a comprehensive experimental design document (`experiment_design.md`) inside a dedicated project directory. The design includes treatment conditions, randomization, outcome measures, power analysis, and sample size recommendations.

## Usage

```
/design-experiment Do people exhibit anchoring bias when estimating prices?
/design-experiment Does framing an issue as a loss vs. gain change policy support?
/design-experiment How does social proof affect willingness to donate?
```

## Workflow

> **Path Discovery:** This skill bundles a `helpers.py` script. Before running it, use `Glob("**/design-experiment/helpers.py")` to locate it. Store the result in a variable and use it for all subsequent calls.

### 0. Create Project Directory

Generate a short, descriptive directory name from the research question:

1. **Slugify** the research question into a directory name: lowercase, remove punctuation, replace spaces with hyphens, truncate to ~50 characters at a word boundary. Prefix with the current date as `YYYY-MM-DD_`. Example: `2026-02-08_llm-prospect-theory-lottery-choices`

2. **Create** the directory using the helper script bundled with this skill:
```bash
# First, locate helpers.py using Glob("**/design-experiment/helpers.py")
# Then run with the discovered path:
python3 <discovered_path> setup-dir "<research_question>"
```
This prints two lines: the directory name (e.g. `2026-02-08_do-llms-exhibit-status-quo-bias`) and either `NEW` or `EXISTS`.

3. **Check** if `experiment_design.md` already exists inside that directory. If it does, use AskUserQuestion:

```
Question: "A design already exists at <dir_name>/experiment_design.md. What would you like to do?"
Header: "Existing file"
Options:
  1. "Start fresh" - "Overwrite the existing design with a new one"
  2. "Modify existing" - "Read the current design and revise it based on your new input"
  3. "Cancel" - "Keep the existing file unchanged"
```

- **Start fresh**: Proceed with the full workflow below, overwriting the file.
- **Modify existing**: Read the existing file, understand the current design, then ask the user what they want to change. Apply targeted edits and re-run any affected sections (e.g., update power analysis if sample size changes).
- **Cancel**: Stop and inform the user.

All output files for this experiment are written into `<dir_name>/`.

### 1. Parse the Research Question

Extract from the user's input:
- **Core research question**: The causal or descriptive question being asked
- **Independent variable(s)**: What is being manipulated or varied
- **Dependent variable(s)**: What is being measured
- **Implied population**: Who the question is about
- **Any constraints or details** the user specified (e.g., specific stimuli, number of conditions, population)

If the research question is too vague to design an experiment, use AskUserQuestion to clarify:

```
Question: "Could you provide more detail about your research question? For example: What specifically do you want to manipulate? What outcome do you want to measure?"
Header: "Clarify"
```

### 2. Literature Review (Optional)

Use AskUserQuestion to ask if the user wants a literature review:

```
Question: "Would you like me to search the literature for relevant prior studies? This helps calibrate expected effect sizes, identify proven experimental designs, and avoid common pitfalls."
Header: "Lit review"
Options:
  1. "Yes, do a literature review (Recommended)" - "Search for relevant papers and use findings to inform the design"
  2. "Skip literature review" - "Design the experiment based on general principles only"
```

If the user opts in, conduct a literature review:

1. **Search** for relevant prior work using WebSearch. Run 2-4 searches with different query angles:
   - The core phenomenon (e.g., "anchoring bias experiment survey design")
   - Methodological approaches (e.g., "anchoring effect experimental paradigm")
   - Effect sizes (e.g., "anchoring bias effect size meta-analysis Cohen's d")
   - Recent or seminal papers (e.g., "Tversky Kahneman anchoring experiment")

2. **Fetch** the most promising 3-5 results using WebFetch to extract:
   - Experimental design details (conditions, stimuli, measures)
   - Sample sizes used
   - Reported effect sizes (Cohen's d, odds ratios, etc.)
   - Key findings and boundary conditions

3. **Synthesize** findings into a summary noting:
   - What designs have been used successfully
   - Typical effect sizes observed (for power analysis)
   - Common pitfalls or confounds to avoid
   - Gaps in the literature the user's study could address

### 3. Design the Experiment

Based on the research question (and literature review if conducted), design the experiment:

#### 3a. Identify Conditions and Factors

Determine:
- **Between-subjects factors**: Conditions participants are randomly assigned to (e.g., high anchor vs. low anchor)
- **Within-subjects factors**: Conditions all participants experience (if any)
- **Factorial structure**: If multiple factors, specify the full factorial or fractional design
- **Control condition**: Whether a no-treatment control is needed

Example for anchoring bias:
| Factor | Levels | Type |
|--------|--------|------|
| Anchor value | High ($500), Low ($50) | Between-subjects |
| Product category | Electronics, Clothing, Food | Within-subjects (scenario) |

This yields a 2 (anchor) x 3 (category) mixed design = 2 between-subjects cells.

#### 3b. Define Stimuli and Scenarios

Specify the concrete stimuli for each condition. In EDSL, these become `Scenario` objects:

- What text/prompt each participant sees
- What varies across conditions (the manipulation)
- What stays constant (controls)
- Whether stimuli are parameterized with Jinja2 templates

#### 3c. Define Outcome Measures

For each dependent variable, specify:
- The question text
- The question type (e.g., `QuestionNumerical`, `QuestionLinearScale`, `QuestionMultipleChoice`)
- The response scale or options
- Any attention checks or manipulation checks

#### 3d. Define the Survey Flow

Specify the order of:
1. Consent / instructions
2. Attention or comprehension checks (if needed)
3. Treatment exposure (stimuli)
4. Outcome measures
5. Manipulation checks
6. Demographics or covariates (if needed)
7. Debrief (if needed)

### 4. Power Analysis and Sample Size

Run the power analysis using the helper script bundled with this skill. Use the effect sizes from the literature review, or reasonable defaults if no literature review was conducted.

```bash
# Use Glob("**/design-experiment/helpers.py") to locate helpers.py first, then:

# Two independent groups (e.g., treatment vs. control):
python3 <discovered_path> power --test two-means --effect-size 0.2 0.5 0.8 --power 0.80 0.90 --cells 2

# Two proportions:
python3 <discovered_path> power --test two-proportions --effect-size 0.3 0.5 --power 0.80 0.90

# Multiple groups (ANOVA):
python3 <discovered_path> power --test anova --effect-size 0.10 0.25 0.40 --power 0.80 0.90 --cells 3
```

The script outputs a markdown table of sample size requirements. Choose the appropriate test and effect sizes for the design.

Provide sample size recommendations at three power levels:
| Power | Effect Size | N per cell | Total N |
|-------|-------------|-----------|---------|
| 0.80 | d = 0.5 (medium) | 64 | 128 |
| 0.90 | d = 0.5 (medium) | 86 | 172 |
| 0.80 | d = 0.3 (small-medium) | 176 | 352 |

If no effect size estimate is available from the literature, present a range:
- Small effect (d = 0.2): N per cell = ...
- Medium effect (d = 0.5): N per cell = ...
- Large effect (d = 0.8): N per cell = ...

### 5. Write the Design Document

Write the complete experiment design to `<dir_name>/experiment_design.md` using the Write tool. Follow this structure:

```markdown
# Experiment Design: [Short Title]

**Research Question:** [Full research question]
**Date:** [Current date]

## 1. Literature Review

[If conducted: Summary of prior work, key findings, effect sizes, and how they inform this design]
[If skipped: "Literature review was not conducted for this design."]

### Key References
- [Author (Year). Title. *Journal*. Key finding.]
- ...

### Implications for Design
- Expected effect size: [estimate with justification]
- Recommended design features based on prior work
- Potential confounds identified in the literature

## 2. Experimental Design

### Overview
[1-2 paragraph summary of the design: what is manipulated, what is measured, and how]

### Design Type
- **Type**: [Between-subjects / Within-subjects / Mixed / Factorial]
- **Factors**: [List each factor with levels]
- **Number of cells**: [Total experimental conditions]

### Conditions

| Cell | [Factor 1] | [Factor 2] | Description |
|------|-----------|-----------|-------------|
| 1 | Level A | Level X | [What participants in this cell experience] |
| 2 | Level A | Level Y | ... |
| 3 | Level B | Level X | ... |
| 4 | Level B | Level Y | ... |

### Randomization Plan
- **Unit of randomization**: [Participant / Scenario / etc.]
- **Assignment method**: [Simple random / Stratified / Block]
- **Balance**: [How balance across conditions is ensured]

## 3. Stimuli and Materials

### Treatment Materials
[Describe the exact stimuli for each condition. Include example text that participants would see.]

**Condition 1: [Name]**
> [Exact stimulus text or description]

**Condition 2: [Name]**
> [Exact stimulus text or description]

### Control Materials (if applicable)
> [Exact control stimulus text or description]

## 4. Measures

### Primary Outcome
- **Variable**: [Name]
- **Question text**: "[Exact question wording]"
- **Type**: [Question type, e.g., QuestionNumerical, QuestionLinearScale]
- **Scale/Options**: [Response options]

### Secondary Outcomes (if any)
- ...

### Manipulation Check
- **Question**: "[Question to verify treatment was perceived]"
- **Expected pattern**: [What responses indicate successful manipulation]

### Attention Check (if any)
- **Question**: "[Attention check question]"
- **Correct answer**: [Expected response]

## 5. Survey Flow

```
1. Instructions / Consent
2. [Attention check (if included)]
3. Treatment exposure (randomized by condition)
4. Primary outcome measure(s)
5. Secondary outcome measure(s)
6. Manipulation check
7. Demographics / Covariates (if included)
```

## 6. Power Analysis

### Assumptions
- **Test**: [Statistical test to be used, e.g., independent samples t-test, chi-squared, ANOVA]
- **Expected effect size**: [Cohen's d / f / w = X, with justification]
- **Significance level**: alpha = 0.05
- **Desired power**: 0.80 (and 0.90 for comparison)

### Sample Size Requirements

| Power | Effect Size | N per Cell | Total N | Notes |
|-------|-------------|-----------|---------|-------|
| 0.80  | [size]      | [n]       | [N]     | Recommended minimum |
| 0.90  | [size]      | [n]       | [N]     | Conservative estimate |
| 0.80  | [smaller]   | [n]       | [N]     | If effect is smaller than expected |

### Recommendation
**Recommended sample size: [N] total ([n] per cell)**
[Justification: why this sample size balances cost and statistical power]

## 7. Analysis Plan

### Primary Analysis
- [Statistical test] comparing [outcome] across [conditions]
- [Pre-registered hypothesis and direction]

### Secondary Analyses
- [Any planned subgroup analyses, robustness checks, etc.]

### Exclusion Criteria
- [Criteria for excluding responses, e.g., failed attention check, incomplete responses]

## 8. EDSL Implementation Notes

### Scenarios (Treatment Conditions)
The experimental conditions should be implemented as EDSL `Scenario` objects:
```python
from edsl import Scenario, ScenarioList
scenarios = ScenarioList([
    Scenario({"condition": "...", "stimulus": "..."}),
    # ...
])
```

### Survey Structure
Key questions should use these EDSL types:
- [Primary outcome]: `[QuestionType]`
- [Manipulation check]: `[QuestionType]`

### Running the Experiment
```
# Pseudocode for running
results = survey.by(scenarios).by(agents).run()
```

## 9. Limitations and Considerations

- [Key limitations of this design]
- [Potential confounds and how they are addressed]
- [External validity considerations]
- [Ethical considerations if relevant]
```

### 6. Present the Design

After writing `<dir_name>/experiment_design.md`, inform the user:

1. Confirm the file was written and its full path (including directory)
2. Provide a brief summary of the key design choices:
   - Number of conditions
   - Primary outcome measure
   - Recommended sample size
3. Ask if they'd like to modify anything

Use AskUserQuestion:

```
Question: "The experiment design has been saved to <dir_name>/experiment_design.md. Would you like to:"
Header: "Next steps"
Options:
  1. "Looks good!" - "Keep the design as-is"
  2. "Modify the design" - "Adjust conditions, measures, sample size, or other elements"
  3. "Generate EDSL code" - "Create a Python script implementing this design using EDSL (invokes /create-study)"
```

If the user wants to generate EDSL code, invoke the `create-study` skill with the research question and the design document as context.

## Design Principles

When designing experiments, follow these principles:

1. **Simplicity**: Prefer simpler designs (fewer factors, cleaner manipulations) unless complexity is justified
2. **Clean manipulations**: Each condition should differ on exactly the intended dimension
3. **Validated measures**: Use established scales and question wordings when available from the literature
4. **Statistical power**: Recommend sample sizes that give at least 80% power for the expected effect size
5. **Pre-registration mindset**: The design document should be specific enough to serve as a pre-registration
6. **Practical effect sizes**: Use realistic effect size estimates from prior work, not optimistic guesses. When uncertain, power for a small-to-medium effect.

## Example: Anchoring Bias Experiment

**User input**: "Do people exhibit anchoring bias when estimating prices?"

**Key design elements**:
- 2 (anchor: high vs. low) x 3 (product: laptop, jacket, dinner) mixed design
- Between-subjects factor: anchor value (high vs. low)
- Within-subjects factor: product category (implemented as scenarios)
- Primary outcome: price estimate (QuestionNumerical)
- Manipulation check: recall of anchor value
- Expected effect: d = 0.5-0.8 based on Tversky & Kahneman (1974) and subsequent meta-analyses
- Recommended N: 64 per cell (128 total) for 80% power at d = 0.5

## Output

The skill creates a project directory and produces a design document inside it:

| Path | Description |
|------|-------------|
| `<dir_name>/` | Project directory named `YYYY-MM-DD_<slugified-question>` |
| `<dir_name>/experiment_design.md` | Complete experimental design document with all sections above |

The document is designed to be:
- **Self-contained**: All design decisions and justifications in one place
- **Actionable**: Specific enough to implement directly (or feed into `/create-study`)
- **Reproducible**: Power analysis is documented with all assumptions
- **Living document**: Can be modified by re-running the skill with "Modify existing" option
- **Organized**: Each experiment gets its own directory, keeping the workspace clean
