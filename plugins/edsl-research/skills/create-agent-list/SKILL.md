---
name: create-agent-list
description: Create AgentLists from web searches, descriptions, local files, or programmatic generation
allowed-tools: Read, Glob, Bash(python:*), WebSearch, WebFetch, AskUserQuestion
user-invocable: true
arguments: agent_list_description
---

# Creating AgentLists

## Generating Agents

Agents can be generated from descriptions or external sources (not just loaded from files):

```python
# Example: Generate agents from web search results
# 1. Search for data (e.g., sports roster, company employees, historical figures)
# 2. Extract relevant traits
# 3. Build AgentList programmatically

from edsl import Agent, AgentList

# Generated from research/web data
agents = AgentList([
    Agent(name="Person A", traits={"role": "CEO", "age": 45, "company": "Acme"}),
    Agent(name="Person B", traits={"role": "CTO", "age": 38, "company": "Acme"}),
])
```

## From a List of Agents

```python
from edsl import Agent, AgentList

# Create agents individually
agent1 = Agent(traits={"age": 25, "occupation": "teacher"})
agent2 = Agent(traits={"age": 35, "occupation": "doctor"})

# Combine into AgentList
agents = AgentList([agent1, agent2])
```

## From External Data Sources

The `from_source()` method auto-detects the source type:

```python
from edsl import AgentList

# From CSV file
agents = AgentList.from_source("people.csv")

# From Excel file
agents = AgentList.from_source("data.xlsx", sheet_name="Participants")

# From dictionary
agents = AgentList.from_source({
    "age": [25, 30, 35],
    "name": ["Alice", "Bob", "Charlie"],
    "occupation": ["teacher", "doctor", "engineer"]
})

# From pandas DataFrame
import pandas as pd
df = pd.DataFrame({"age": [25, 30], "city": ["NYC", "LA"]})
agents = AgentList.from_source(df)
```

## With Instructions and Codebook

```python
# Apply instructions to all agents at creation time
agents = AgentList.from_source(
    "people.csv",
    instructions="Answer as if you were this person",
    codebook={"age": "Age in years", "income": "Annual income in USD"},
    name_field="respondent_name"  # Use this column as agent names
)

# Or load codebook from a CSV file (2 columns: key, description)
agents = AgentList.from_source(
    "people.csv",
    codebook="codebook.csv"
)
```

## Programmatically with Combinations

```python
from edsl import Agent, AgentList
from itertools import product

# Create agents for all combinations
ages = [25, 35, 45]
occupations = ["teacher", "doctor", "engineer"]

agents = AgentList([
    Agent(traits={"age": age, "occupation": occ})
    for age, occ in product(ages, occupations)
])
# Creates 9 agents (3 ages × 3 occupations)
```

## Quick Reference

| Source | Example |
|--------|---------|
| List of Agents | `AgentList([agent1, agent2])` |
| CSV file | `AgentList.from_source("file.csv")` |
| Excel file | `AgentList.from_source("file.xlsx", sheet_name="Sheet1")` |
| Dictionary | `AgentList.from_source({"col": [1, 2, 3]})` |
| DataFrame | `AgentList.from_source(df)` |


## Saving 

You will create a Python file with a descriptive name e.g., 'occupation_agent_list.py'
Whatever the name of your agent list, you will also save it as local JSON file:
```python
import os
agent_list_name = os.path.splitext(os.path.basename(__file__))[0]
agent.save(survey_name)
```

You can also ask the user if they want to push that agent list to coop (Expected Parrot's servers).

Use `AskUserQuestion` to ask the user:
- "Should we push this agent list to Expected Parrot?"
- Options: Yes / No

If they answer 'Yes' ask them for the visibility setting with `AskUserQuestion`: 
- "What visibility setting?
- Options: "public", "private", "unlisted"

Only proceed after receiving a response.

The description should be a short paragraph you write.
The alias should be a valid URL slug e.g., 'exit-interview' 

```python
agent_list.push(
    visibility = "unlisted", 
    description = "<paragraph description of the survey>", 
    alias = "<valid url slug>"
)
```
After pushing, you should print the results so the user can see them. If there is any error in pushing from your parameters, update the names.