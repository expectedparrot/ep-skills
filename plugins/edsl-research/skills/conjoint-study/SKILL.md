---
name: conjoint-study
description: Design, execute, and analyze conjoint analysis studies - guides through attribute/level definition, experimental design, EDSL survey generation, and part-worth utility estimation
allowed-tools: Read, Write, Glob, Grep, Skill, AskUserQuestion, Bash(python3:*)
user-invocable: true
arguments: research_question
---

# Conjoint Study

Takes a research question and guides the user through designing a conjoint analysis study, generating balanced experimental designs, creating EDSL project files, running the study, and analyzing results with part-worth utilities.

## Usage

```
/conjoint-study What features matter most when choosing a streaming service?
/conjoint-study How do job seekers trade off salary, remote work, and company size?
/conjoint-study What attributes drive consumer preference for electric vehicles?
```

## Workflow

> **Path Discovery:** This skill bundles a `helpers.py` script. Before running it, use `Glob("**/conjoint-study/helpers.py")` to locate it. Store the result in a variable and use it for all subsequent calls.

### Phase 0: Setup

1. **Locate helpers.py** using `Glob("**/conjoint-study/helpers.py")`.

2. **Create the project directory** using the helper:
```bash
python3 <helpers_path> setup-dir "<research_question>"
```
This prints two lines: the directory name (e.g. `2026-02-10_streaming-service-preferences`) and either `NEW` or `EXISTS`.

3. **Check for existing design.** If `EXISTS`, use AskUserQuestion:
```
Question: "A conjoint design already exists at <dir_name>/conjoint_design.md. What would you like to do?"
Header: "Existing file"
Options:
  1. "Start fresh" - "Overwrite the existing design with a new one"
  2. "Modify existing" - "Read the current design and revise it"
  3. "Cancel" - "Keep the existing file unchanged"
```

All output files are written into `<dir_name>/`.

### Phase 1: Elicit Study Design

Conduct 6 AskUserQuestion interactions to gather the full study specification.

#### 1a. Research Question

If the user's input is vague, clarify:
```
Question: "Could you describe your conjoint study in more detail? Specifically: What product/service are you studying? What decision are respondents making? What trade-offs are you interested in?"
Header: "Clarify"
```

Parse from the input:
- **Product/service category** being evaluated
- **Decision context** (purchase, subscription, job choice, etc.)
- **Key trade-offs** the researcher wants to measure

#### 1b. Attributes and Levels

Ask the user to define attributes and their levels:
```
Question: "Please list the attributes and levels for your conjoint study. Format each as 'Attribute: Level1, Level2, Level3'. For example:\n\nPrice: $9.99, $14.99, $19.99\nContent Library: Small, Medium, Large\nAd Experience: No ads, Limited ads, Full ads\n\nGuidelines:\n- Use 3-8 attributes\n- Use 2-5 levels per attribute\n- Attributes should be actionable and independent\n- Levels should span a realistic range\n- Avoid 'must-have' attributes where one level always dominates"
Header: "Attributes"
```

After receiving the response, parse the attributes and levels. **Validate:**
- 3-8 attributes (warn if outside range)
- 2-5 levels per attribute (warn if outside range)

Present a formatted confirmation table:
```
Question: "Here are the attributes and levels I've parsed:\n\n| Attribute | Levels |\n|-----------|--------|\n| Price | $9.99, $14.99, $19.99 |\n| ... | ... |\n\nTotal unique profiles: <N>\n\nDoes this look correct?"
Header: "Confirm attrs"
Options:
  1. "Looks good" - "Proceed with these attributes and levels"
  2. "Make changes" - "Edit the attributes or levels"
```

#### 1c. Conjoint Method

```
Question: "Which conjoint method would you like to use?"
Header: "Method"
Options:
  1. "Choice-Based Conjoint (CBC) (Recommended)" - "Respondents choose their preferred option from a set of profiles. Most widely used method."
  2. "Ranking-Based" - "Respondents rank profiles from most to least preferred. Provides more data per task but higher cognitive load."
  3. "MaxDiff (Best-Worst)" - "Respondents pick the best and worst from a set. Good for measuring attribute importance directly."
```

#### 1d. Design Parameters

```
Question: "How many choice tasks and profiles per task?"
Header: "Design size"
Options:
  1. "Standard (8 tasks, 3 profiles) (Recommended)" - "Good balance of statistical power and respondent burden"
  2. "Compact (6 tasks, 2 profiles)" - "Fewer tasks for lower respondent burden, still adequate power"
  3. "Rich (12 tasks, 4 profiles)" - "More data per respondent, higher cognitive load"
  4. "Custom" - "Specify your own number of tasks and profiles per task"
```

If Custom, ask for specific numbers.

Then ask about the "none" option:
```
Question: "Should respondents have a 'None of these' option in each choice task?"
Header: "None option"
Options:
  1. "Yes" - "Include 'None of these' — useful when non-purchase is a realistic outcome"
  2. "No (Recommended)" - "Force a choice between the presented profiles"
```

#### 1e. Respondent Segments

```
Question: "How would you like to define respondents?"
Header: "Respondents"
Options:
  1. "Define segments" - "Specify respondent segments with distinct traits (e.g., budget-conscious, tech enthusiast)"
  2. "Generic respondents" - "Use a default set of diverse respondents without specific segments"
  3. "Skip agents" - "Run without agent personas (default LLM behavior)"
```

If "Define segments", ask for segment descriptions:
```
Question: "Describe the respondent segments you want. For each segment, provide a name and key traits. For example:\n\nBudget-conscious: price-sensitive, value-oriented, income=$50k\nTech enthusiast: early adopter, feature-focused, income=$100k\nCasual user: convenience-oriented, low engagement"
Header: "Segments"
```

#### 1f. Confirm Full Design

Present a complete summary:
```
Question: "Here is your conjoint study design:\n\n| Parameter | Value |\n|-----------|-------|\n| Method | Choice-Based Conjoint |\n| Attributes | <N> |\n| Total unique profiles | <N> |\n| Tasks per respondent | <N> |\n| Profiles per task | <N> |\n| Include 'None' option | Yes/No |\n| Respondent segments | <N> segments |\n| Design versions | 4 |\n| Total observations | tasks × versions × segments |\n\nReady to proceed?"
Header: "Confirm"
Options:
  1. "Proceed" - "Generate the experimental design and EDSL project files"
  2. "Modify" - "Go back and change some parameters"
  3. "Save design doc only" - "Save the design specification without generating code"
```

### Phase 2: Generate Experimental Design

1. **Write the design spec** as `design_spec.json` in the project directory:
```json
{
  "attributes": {
    "price": ["$9.99", "$14.99", "$19.99"],
    "content_library": ["Small", "Medium", "Large"],
    "ad_experience": ["No ads", "Limited ads", "Full ads"]
  },
  "method": "cbc",
  "tasks_per_version": 8,
  "profiles_per_task": 3,
  "n_versions": 4,
  "include_none": false,
  "min_attribute_diff": 2,
  "seed": 42
}
```

2. **Run the design generator:**
```bash
python3 <helpers_path> generate-design <dir_name>/design_spec.json --output <dir_name>/conjoint_choice_sets.json
```

3. **Write `conjoint_design.md`** documenting the full design — research question, attributes table, method, parameters, and choice set summary.

### Phase 3: Create EDSL Project Files

Generate a study directory following the `create-study` pattern. Before generating survey code, read the `edsl-survey-reference` skill for question type details:

```
Use Glob("**/edsl-survey-reference/SKILL.md") and read it for QuestionMultipleChoice details.
```

#### Project Structure

```
<dir_name>/
  conjoint_design.md          # Design document
  design_spec.json            # Machine-readable specification
  conjoint_choice_sets.json   # Generated choice sets
  study_survey.py             # Survey with choice task questions
  study_scenario_list.py      # Each design version as a Scenario
  study_agent_list.py         # Respondent segments
  study_model_list.py         # LLM models
  create_results.py           # Runner script
  analyze_conjoint.py         # Conjoint-specific analysis
  Makefile                    # Build targets
```

#### `study_survey.py`

Each choice task is a separate `QuestionMultipleChoice`. Profile descriptions are embedded in question text via Jinja2 scenario variables. Option labels are static ("Option A", "Option B", etc.).

```python
from edsl import Survey, QuestionMultipleChoice

# === CHOICE TASKS ===

q_choice_1 = QuestionMultipleChoice(
    question_name="choice_task_1",
    question_text="""Consider the following options for a streaming service:

Option A: {{ task_1_opt_a }}
Option B: {{ task_1_opt_b }}
Option C: {{ task_1_opt_c }}

Which option would you choose?""",
    question_options=["Option A", "Option B", "Option C"]
)

q_choice_2 = QuestionMultipleChoice(
    question_name="choice_task_2",
    question_text="""Consider the following options for a streaming service:

Option A: {{ task_2_opt_a }}
Option B: {{ task_2_opt_b }}
Option C: {{ task_2_opt_c }}

Which option would you choose?""",
    question_options=["Option A", "Option B", "Option C"]
)

# ... repeat for all N tasks

# === SURVEY ===

survey = Survey([q_choice_1, q_choice_2, ...])
```

Key design decisions:
- **Static option labels** ("Option A", "Option B", "Option C") as `question_options` — NOT the profile descriptions
- **Scenario templating** for profile descriptions: each `{{ task_N_opt_X }}` is a formatted string describing one profile's attributes
- If `include_none` is True, add `"None of these"` to `question_options`
- Do NOT use `set_full_memory_mode()` — choice tasks are independent

#### `study_scenario_list.py`

Each design version becomes a separate `Scenario`. Scenario variables encode the formatted profile descriptions for every task and option.

```python
from edsl import Scenario, ScenarioList

# Each scenario encodes one complete design version.
# Variables: task_{t}_opt_{a|b|c} = formatted profile description

scenario_list = ScenarioList([
    Scenario({
        "design_version": 1,
        "task_1_opt_a": "Price: $9.99, Content: Large, Ads: Full ads",
        "task_1_opt_b": "Price: $19.99, Content: Small, Ads: No ads",
        "task_1_opt_c": "Price: $14.99, Content: Medium, Ads: Limited ads",
        "task_2_opt_a": "...",
        # ... all tasks for version 1
    }),
    Scenario({
        "design_version": 2,
        # ... all tasks for version 2
    }),
    # ... more versions
])
```

To build the scenario list, read `conjoint_choice_sets.json` and format each profile as a multi-attribute description string. Also include individual attribute columns for analysis:
```python
# For each task/option, also store individual attributes for analysis:
# task_{t}_opt_{x}_{attr_name} = level value
```

The scenario list construction should be done programmatically in the generated file:

```python
import json
from edsl import Scenario, ScenarioList

with open("conjoint_choice_sets.json", "r") as f:
    design = json.load(f)

attributes = design["attributes"]
attr_names = list(attributes.keys())

scenarios = []
for version in design["versions"]:
    s = {"design_version": version["version"]}
    for t_idx, choice_set in enumerate(version["choice_sets"], 1):
        for p_idx, profile in enumerate(choice_set):
            opt_letter = chr(ord("a") + p_idx)
            # Formatted description for question text
            desc = ", ".join(f"{attr}: {profile[attr]}" for attr in attr_names)
            s[f"task_{t_idx}_opt_{opt_letter}"] = desc
            # Individual attributes for analysis
            for attr in attr_names:
                s[f"task_{t_idx}_opt_{opt_letter}_{attr}"] = profile[attr]
    scenarios.append(Scenario(s))

scenario_list = ScenarioList(scenarios)
```

#### `study_agent_list.py`

If segments were defined, create agents with traits. If generic respondents, create a diverse set. If skipped, export empty `AgentList`.

```python
from edsl import Agent, AgentList

agent_list = AgentList([
    Agent(traits={"persona": "budget-conscious consumer", "segment": "budget", "income": "$50k"}),
    Agent(traits={"persona": "tech enthusiast", "segment": "tech", "income": "$100k"}),
    Agent(traits={"persona": "casual user", "segment": "casual", "income": "$75k"}),
])
```

#### `study_model_list.py`

```python
from edsl import ModelList, Model

model_list = ModelList([Model("gpt-4o")])
```

#### `create_results.py`

```python
from study_survey import survey
from study_scenario_list import scenario_list
from study_agent_list import agent_list
from study_model_list import model_list

job = survey.by(scenario_list).by(agent_list).by(model_list)
results = job.run()
results.to_json("results.json.gz")
results.to_csv("results.csv")
```

#### `analyze_conjoint.py`

A script that calls `helpers.py analyze` and then generates charts:

```python
import subprocess
import sys

# Run conjoint analysis
subprocess.run([
    sys.executable, "<helpers_path>",
    "analyze", "results.csv", "design_spec.json",
    "--output-dir", "."
], check=True)

# Generate charts
subprocess.run([sys.executable, "generate_charts.py"], check=True)

print("Conjoint analysis complete. See:")
print("  conjoint_report.md  - Full analysis report")
print("  utilities.json      - Part-worth utilities")
print("  utilities.csv       - Utilities in CSV format")
print("  importance_chart.png - Attribute importance chart")
print("  utilities_chart.png  - Part-worth utilities chart")
```

**Important:** When generating `analyze_conjoint.py`, replace `<helpers_path>` with the actual discovered path to `helpers.py`.

#### `Makefile`

```makefile
results.json.gz: create_results.py study_survey.py study_scenario_list.py study_agent_list.py study_model_list.py
	python create_results.py

analyze: results.csv analyze_conjoint.py design_spec.json
	python analyze_conjoint.py

results.csv: results.json.gz
	@echo "results.csv is produced alongside results.json.gz"
```

### Phase 4: Run Study (Optional)

Ask the user:
```
Question: "The conjoint study files have been generated in <dir_name>/. Would you like to run the study now?"
Header: "Run study"
Options:
  1. "Run now" - "Execute the study (this will make API calls to LLM providers)"
  2. "Run later" - "I'll run it manually with 'make' or 'python create_results.py'"
```

If "Run now":
```bash
cd <dir_name> && python3 create_results.py
```

### Phase 5: Analyze Results

After the study completes (or if results already exist):

1. **Run the analysis:**
```bash
cd <dir_name> && python3 analyze_conjoint.py
```

2. **Present key findings** from `conjoint_report.md`:
   - Attribute importance rankings
   - Top part-worth utilities
   - Segment differences (if applicable)

3. **Suggest next steps:**
```
Question: "The conjoint analysis is complete. What would you like to do next?"
Header: "Next steps"
Options:
  1. "Run market simulation" - "Predict choice shares for specific product profiles"
  2. "Explore further with /analyze-results" - "Do additional analysis on the raw results"
  3. "Publish with /publish-study" - "Share the study on GitHub"
  4. "Done" - "No further analysis needed"
```

If "Run market simulation", ask for competing product profiles and run:
```bash
python3 <helpers_path> market-sim <dir_name>/utilities.json <dir_name>/profiles.json
```

## Design Principles

1. **Balanced designs**: The randomized search optimizer ensures each attribute level appears approximately equally often across all choice tasks
2. **Positional debiasing**: Profile presentation order is shuffled across design versions to mitigate LLM positional bias
3. **Multiple versions**: 4 design versions by default increases effective sample size and reduces order effects
4. **Minimum attribute differences**: Profiles within a task differ on at least 2 attributes, forcing meaningful trade-offs
5. **Static option labels**: Using "Option A/B/C" rather than profile descriptions as answer choices ensures clean response parsing
6. **Scenario-based variation**: Each design version is a separate Scenario, leveraging EDSL's built-in parallelism

## Output

The skill creates a project directory with all files needed to run and analyze a conjoint study:

| Path | Description |
|------|-------------|
| `conjoint_design.md` | Human-readable design document |
| `design_spec.json` | Machine-readable design specification |
| `conjoint_choice_sets.json` | Generated balanced choice sets |
| `study_survey.py` | EDSL Survey with choice task questions |
| `study_scenario_list.py` | ScenarioList encoding design versions |
| `study_agent_list.py` | AgentList with respondent segments |
| `study_model_list.py` | ModelList specifying LLMs |
| `create_results.py` | Runner script |
| `analyze_conjoint.py` | Analysis script producing utilities and charts |
| `Makefile` | Build targets for running and analyzing |
