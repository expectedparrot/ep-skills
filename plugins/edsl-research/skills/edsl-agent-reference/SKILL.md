---
name: edsl-agent-reference
description: EDSL agent reference - AgentList operations, trait manipulation, templates, codebooks, and instructions
allowed-tools: Read, Glob, Bash(python:*)
---

# EDSL Agent Reference

Consolidated reference for working with Agents and AgentLists in EDSL: list operations, trait manipulation, templates, codebooks, and instructions.

---

# AgentList Operations

Operations for manipulating collections of agents.

## Naming Agents

### Set Names from Traits

```python
agents = agents.give_names("respondent_id")
agents = agents.give_names("first_name", "last_name", remove_traits=False)
agents = agents.give_names("city", "id", separator="_")
```

### Assign UUID Names

```python
agents = agents.give_uuid_names()
```

## Sampling and Shuffling

```python
sample = agents.sample(n=10, seed=42)
shuffled = agents.shuffle(seed=42)
train, test = agents.split(frac_left=0.8, seed=42)
```

## Combining AgentLists

```python
combined = agents1 + agents2
collapsed = agents.collapse()
```

## Applying Deltas (Batch Updates)

```python
from edsl import AgentDelta, AgentListDeltas

deltas = AgentListDeltas({
    "Alice": AgentDelta({"age": 31, "status": "promoted"}),
    "Bob": AgentDelta({"age": 26})
})

updated_agents = agents.apply_deltas(deltas)
```

## Conversion

```python
dataset = agents.to_dataset()
scenarios = agents.to_scenario_list()
df = agents.to_pandas()
```

## Accessing Agents

```python
agent = agents[0]
subset = agents[0:5]
first = agents.first()
last = agents.last()
agent = agents.at(3)

for agent in agents:
    print(agent.traits)
```

## Running Surveys with Agents

```python
results = survey.by(agents).run()
results = agents.to(survey).run()
```

## Operations Quick Reference

| Operation | Method |
|-----------|--------|
| Name from traits | `agents.give_names("trait")` |
| UUID names | `agents.give_uuid_names()` |
| Sample | `agents.sample(n=10, seed=42)` |
| Shuffle | `agents.shuffle(seed=42)` |
| Split | `agents.split(frac_left=0.8)` |
| Combine | `agents1 + agents2` |
| Collapse | `agents.collapse()` |
| Apply deltas | `agents.apply_deltas(deltas)` |
| To Dataset | `agents.to_dataset()` |
| To ScenarioList | `agents.to_scenario_list()` |
| To DataFrame | `agents.to_pandas()` |
| First/Last | `agents.first()`, `agents.last()` |

---

# Trait Operations

All trait operations return new instances (immutable pattern).

## Adding Traits

```python
# Single agent
agent = agent.add_trait("weight", 150)
agent = agent.add_trait({"weight": 150, "height": 5.5})

# AgentList - single value for all agents
agents = agents.add_trait("status", value="participant")

# AgentList - different values per agent (must match length)
agents = agents.add_trait("score", values=[85, 90, 78, 92])
```

## Updating Traits

```python
agent = agent.update_trait("age", 31)
```

## Removing/Dropping Traits

```python
# Single agent
agent = agent.drop("temporary_id")
agent = agent.drop("temp1", "temp2")

# AgentList
agents = agents.drop("temporary_id")
agents = agents.drop("temp1", "temp2", "temp3")
```

## Keeping/Selecting Traits

```python
agent = agent.keep("age", "occupation")
agents = agents.keep("age", "occupation")
agents = agents.select("age", "occupation")  # Alias
```

## Renaming Traits

```python
agent = agent.rename("old_name", "new_name")
agent = agent.rename({"old1": "new1", "old2": "new2"})
agents = agents.rename("old_name", "new_name")
```

## Translating Trait Values

```python
agents = agents.translate_traits({
    "gender": {1: "male", 2: "female", 3: "other"},
    "education": {1: "high school", 2: "bachelor", 3: "graduate"}
})
```

## Converting String Traits to Numbers

```python
agents = agents.numberify()
```

## Filtering Agents

```python
young_agents = agents.filter("age < 30")
doctors = agents.filter("occupation == 'doctor'")
young_doctors = agents.filter("age < 30 and occupation == 'doctor'")
alice = agents.filter("name == 'Alice'")

# Remove agents with None/NaN values
clean_agents = agents.filter_na()
clean_agents = agents.filter_na(["age", "income"])
```

## Trait Operations Quick Reference

| Operation | Single Agent | AgentList |
|-----------|--------------|-----------|
| Add trait | `agent.add_trait("key", value)` | `agents.add_trait("key", values=[...])` |
| Update trait | `agent.update_trait("key", value)` | N/A |
| Drop trait | `agent.drop("key")` | `agents.drop("key")` |
| Keep traits | `agent.keep("k1", "k2")` | `agents.keep("k1", "k2")` |
| Rename trait | `agent.rename("old", "new")` | `agents.rename("old", "new")` |
| Filter | N/A | `agents.filter("age > 30")` |
| Filter NA | N/A | `agents.filter_na()` |
| Translate | `agent.translate_traits({...})` | `agents.translate_traits({...})` |
| Numberify | N/A | `agents.numberify()` |

---

# Traits, Templates, Codebooks, and Instructions

## Traits Presentation Template

Controls how agent traits appear in LLM prompts.

### Default Behavior

Without a template, traits are shown as a dictionary:
```
Your traits: {'age': 30, 'occupation': 'doctor'}
```

With a codebook but no custom template:
```
Your traits:
Age in years: 30
Current profession: doctor
```

### Setting Custom Templates

Templates use Jinja2 syntax with access to trait values:

```python
from edsl import Agent, AgentList

agent = Agent(
    traits={"age": 30, "occupation": "doctor", "city": "Boston"},
    traits_presentation_template="You are a {{age}}-year-old {{occupation}} living in {{city}}."
)

agents = agents.set_traits_presentation_template(
    "You are a {{age}}-year-old {{occupation}} living in {{city}}."
)
```

### Template Variables Available

Inside templates, you can reference:
- Individual trait keys: `{{age}}`, `{{occupation}}`
- The full traits dict: `{{traits}}`
- The codebook: `{{codebook}}`

## Codebooks

Codebooks map trait keys to human-readable descriptions.

```python
agent = Agent(
    traits={"age": 30, "occ": "MD"},
    codebook={"age": "Age in years", "occ": "Occupation code"}
)

agents = agents.set_codebook({
    "age": "Age in years",
    "income": "Annual income in USD",
    "edu": "Highest education level"
})
```

## Instructions

```python
agent = Agent(
    traits={"age": 30},
    instruction="Answer honestly based on your life experience."
)

agents = agents.set_instruction("Answer as if you were this person.")
agents = agents.add_instructions("Answer honestly and thoughtfully.")
```

## Dynamic Traits

Dynamic traits are computed at question-answering time:

```python
def dynamic_func(question):
    if "income" in question.question_text.lower():
        return {"disclosure_level": "private"}
    return {"disclosure_level": "public"}

agent = Agent(
    traits={"age": 30},
    dynamic_traits_function=dynamic_func
)

# Map questions to relevant traits
agents = agents.set_dynamic_traits_from_question_map({
    "hometown_question": ["hometown", "state"],
    "food_question": ["favorite_food", "dietary_restrictions"]
})
```

## Templates Quick Reference

| Task | Single Agent | AgentList |
|------|--------------|-----------|
| Set codebook | `Agent(..., codebook={...})` | `agents.set_codebook({...})` |
| Set instruction | `Agent(..., instruction="...")` | `agents.set_instruction("...")` |
| Set template | `Agent(..., traits_presentation_template="...")` | `agents.set_traits_presentation_template("...")` |
| View codebook | `agent.codebook` | `agents.codebook` |
| View instruction | `agent.instruction` | `agents.instruction` |
| View template | `agent.traits_presentation_template` | `agents.traits_presentation_template` |
