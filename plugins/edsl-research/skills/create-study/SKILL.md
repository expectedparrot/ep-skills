---
name: create-study
description: Design complete surveys from free text requirements - generates a multi-file study project with Survey, ScenarioList, AgentList, and a Makefile
allowed-tools: Read, Glob, Skill, AskUserQuestion, Write
arguments: research_question
---

# Design Study

This skill generates a multi-file study project with EDSL objects (Survey, ScenarioList, AgentList, ModelList) based on a free text description of what the user wants the study to accomplish.

Example:
```
/create-study Do LLMs exhibit anchoring bias?
```

## Project Structure

Every study is a directory containing these files:

```
<study_name>/
├── Makefile
├── study_survey.py
├── study_scenario_list.py
├── study_agent_list.py
├── study_model_list.py
└── create_results.py
```

| File | Purpose | Exports |
|------|---------|---------|
| `study_survey.py` | Defines questions and survey with rules/memory | `survey` |
| `study_scenario_list.py` | Defines scenario variations | `scenario_list` |
| `study_agent_list.py` | Defines respondent personas | `agent_list` |
| `study_model_list.py` | Defines which LLMs to use | `model_list` |
| `create_results.py` | Imports all objects, runs survey, saves results | (script) |
| `Makefile` | Build system for running the study | — |

## Workflow

### 1. Parse the User's Description

Extract from the free text:
- **Survey Goal**: What the survey is trying to measure
- **Questions needed**: Topics and question types implied
- **Scenarios**: Any variables that should vary across runs
- **Agents**: Any respondent personas mentioned
- **Rules**: Any branching or skip logic implied

If the description is ambiguous or missing key details, use AskUserQuestion to clarify before generating code.

### 2. Ask About Output Destination

Use AskUserQuestion to ask where the user wants the study:

```
Question: "Where would you like the study files?"
Header: "Output"
Options:
  1. "Write to directory (Recommended)" - "Create a study directory with all files based on the topic"
  2. "Display only" - "Show the code in the conversation without saving"
```

If the user chooses to write to a directory:
- Generate a snake_case directory name based on the study topic (e.g., `anchoring_bias_study/`, `food_preferences_study/`)
- Create the directory in the current working directory
- Write all files into it
- Inform the user of the directory and file names after writing

### 3. Reference Other Skills

Read the consolidated reference skill for detailed implementation guidance:

| Skill | When to Read |
|-------|--------------|
| **edsl-survey-reference** | Question types, templating, rules, memory, helpers, visualization |

Use the Skill tool to invoke `edsl-survey-reference`, or Read the SKILL.md file by using Glob("**/edsl-survey-reference/SKILL.md") to locate it.

### 4. Design the Survey Structure

Based on requirements, determine:

1. **Questions needed** and their types
2. **Scenario variables** for parameterization
3. **Agent traits** for respondent personas
4. **Rules** for branching/skip logic
5. **Memory configuration** for context

### 5. Generate the Files

Generate all files in the study directory. Each file is described below.

## File Specifications

### `study_survey.py`

Defines and exports a `survey` object. Contains all question definitions and survey construction.

```python
from edsl import (
    Survey,
    QuestionMultipleChoice,
    QuestionFreeText,
    QuestionLinearScale,
)

# === QUESTIONS ===

q_cuisine = QuestionMultipleChoice(
    question_name="favorite_cuisine",
    question_text="Which cuisine do you enjoy most?",
    question_options=["Italian", "Japanese", "Mexican", "Indian", "Thai"]
)

q_dish = QuestionFreeText(
    question_name="favorite_dish",
    question_text="What is your favorite {{ favorite_cuisine.answer }} dish?"
)

q_frequency = QuestionLinearScale(
    question_name="frequency",
    question_text="How often do you eat {{ favorite_cuisine.answer }} food?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Rarely", 5: "Very Often"}
)

q_why = QuestionFreeText(
    question_name="why_favorite",
    question_text="Why do you particularly enjoy {{ favorite_cuisine.answer }} cuisine?"
)

# === SURVEY ===

survey = (Survey([q_cuisine, q_dish, q_frequency, q_why])
    .set_full_memory_mode())
```

### `study_scenario_list.py`

Defines and exports a `scenario_list` object. If no scenarios are needed, export an empty `ScenarioList`.

```python
from edsl import Scenario, ScenarioList

scenario_list = ScenarioList([
    Scenario({"topic": "artificial intelligence"}),
    Scenario({"topic": "climate change"}),
    Scenario({"topic": "remote work"}),
])
```

When no scenarios are needed:
```python
from edsl import ScenarioList

scenario_list = ScenarioList()
```

### `study_agent_list.py`

Defines and exports an `agent_list` object. If no agents are needed, export an empty `AgentList`.

```python
from edsl import Agent, AgentList

agent_list = AgentList([
    Agent(traits={"persona": "health-conscious millennial", "age": 28}),
    Agent(traits={"persona": "traditional home cook", "age": 55}),
    Agent(traits={"persona": "adventurous foodie", "age": 35}),
    Agent(traits={"persona": "busy professional", "age": 42}),
])
```

When no agents are needed:
```python
from edsl import AgentList

agent_list = AgentList()
```

### `study_model_list.py`

Defines and exports a `model_list` object specifying which LLMs to use. If no specific models are needed, export a `ModelList` with a sensible default.

```python
from edsl import ModelList, Model

model_list = ModelList([
    Model("gpt-4o"),
    Model("claude-3-5-sonnet-20241022"),
])
```

When only one model is needed (default):
```python
from edsl import ModelList, Model

model_list = ModelList([Model("gpt-4o")])
```

### `create_results.py`

Imports from the other study files, builds the job, runs it, saves results as compressed JSON, then exports to CSV.

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

Key rules for `create_results.py`:
- Always import from the four study files
- Chain `.by()` calls: `survey.by(scenario_list).by(agent_list).by(model_list)`
- Empty ScenarioList/AgentList are fine to pass — EDSL handles them gracefully
- First save `results.json.gz` (the primary artifact — compressed JSON with full fidelity)
- Then export `results.csv` (derived convenience format)

### `Makefile`

Provides a build target for running the study.

```makefile
results.json.gz: create_results.py study_survey.py study_scenario_list.py study_agent_list.py study_model_list.py
	python create_results.py
```

Key rules for the Makefile:
- The main target is `results.json.gz`
- Dependencies include `create_results.py` and all four study component files
- If any component file changes, the results are rebuilt
- `create_results.py` also produces `results.csv` as a side effect
- Use a tab character (not spaces) for the recipe line

## Example: Full Study

### User Request
"I want to survey people about their food preferences across 5 cuisines with different persona types."

### Generated Files

**`food_preferences_study/study_survey.py`**
```python
from edsl import (
    Survey,
    QuestionMultipleChoice,
    QuestionFreeText,
    QuestionLinearScale,
)

q_cuisine = QuestionMultipleChoice(
    question_name="favorite_cuisine",
    question_text="Which cuisine do you enjoy most?",
    question_options=["Italian", "Japanese", "Mexican", "Indian", "Thai"]
)

q_dish = QuestionFreeText(
    question_name="favorite_dish",
    question_text="What is your favorite {{ favorite_cuisine.answer }} dish?"
)

q_frequency = QuestionLinearScale(
    question_name="frequency",
    question_text="How often do you eat {{ favorite_cuisine.answer }} food?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Rarely", 5: "Very Often"}
)

q_why = QuestionFreeText(
    question_name="why_favorite",
    question_text="Why do you particularly enjoy {{ favorite_cuisine.answer }} cuisine?"
)

survey = (Survey([q_cuisine, q_dish, q_frequency, q_why])
    .set_full_memory_mode())
```

**`food_preferences_study/study_scenario_list.py`**
```python
from edsl import ScenarioList

scenario_list = ScenarioList()
```

**`food_preferences_study/study_agent_list.py`**
```python
from edsl import Agent, AgentList

agent_list = AgentList([
    Agent(traits={"persona": "health-conscious millennial", "age": 28}),
    Agent(traits={"persona": "traditional home cook", "age": 55}),
    Agent(traits={"persona": "adventurous foodie", "age": 35}),
    Agent(traits={"persona": "busy professional", "age": 42}),
])
```

**`food_preferences_study/study_model_list.py`**
```python
from edsl import ModelList, Model

model_list = ModelList([Model("gpt-4o")])
```

**`food_preferences_study/create_results.py`**
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

**`food_preferences_study/Makefile`**
```makefile
results.json.gz: create_results.py study_survey.py study_scenario_list.py study_agent_list.py study_model_list.py
	python create_results.py
```

## Design Patterns

### Pattern 1: Simple Survey (No Scenarios, No Agents)

All three component files are still created. `study_scenario_list.py` and `study_agent_list.py` export empty lists.

### Pattern 2: Parameterized Survey with Scenarios

`study_survey.py` uses `{{ scenario.variable }}` templating. `study_scenario_list.py` defines the variations.

### Pattern 3: Agent-Based Survey (Personas)

`study_survey.py` may reference `{{ agent.trait }}`. `study_agent_list.py` defines the personas.

### Pattern 4: Full Factorial Design (Scenarios x Agents)

Both `study_scenario_list.py` and `study_agent_list.py` define their respective objects. `create_results.py` chains all: `survey.by(scenario_list).by(agent_list).by(model_list)`.

### Pattern 5: Multi-Model Comparison

`study_model_list.py` defines multiple models to compare responses across LLMs. Results are crossed with scenarios and agents.

## Output

Generate a study directory containing:

1. **`study_survey.py`** — imports EDSL question/survey classes, defines questions, creates and exports `survey`
2. **`study_scenario_list.py`** — imports EDSL scenario classes, creates and exports `scenario_list` (empty if not needed)
3. **`study_agent_list.py`** — imports EDSL agent classes, creates and exports `agent_list` (empty if not needed)
4. **`study_model_list.py`** — imports EDSL model classes, creates and exports `model_list`
5. **`create_results.py`** — imports from the four study files, runs the survey, saves `results.json.gz` and `results.csv`
6. **`Makefile`** — build target for `results.json.gz` with all dependencies

## Checklist Before Generating

- [ ] All question names are valid Python identifiers
- [ ] Question types match the data being collected
- [ ] Piping references only reference earlier questions
- [ ] Skip rules cover all branches appropriately
- [ ] Memory mode is appropriate for the survey flow
- [ ] Scenarios cover all required variations
- [ ] Agent traits are realistic and relevant
- [ ] Each file has the correct imports (no unused imports)
- [ ] Export names are exactly: `survey`, `scenario_list`, `agent_list`, `model_list`
- [ ] `create_results.py` imports from all four study files
- [ ] `create_results.py` saves both `results.json.gz` and `results.csv`
- [ ] Makefile lists all five `.py` files as dependencies
- [ ] Makefile uses tab characters for recipe lines
