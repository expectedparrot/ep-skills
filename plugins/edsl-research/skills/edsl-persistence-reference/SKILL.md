---
name: edsl-persistence-reference
description: Save/load Surveys, Agents, and AgentLists locally, push/pull to Expected Parrot cloud, git versioning
allowed-tools: Read, Glob, Bash(python:*)
---

# EDSL Persistence Reference

Consolidated reference for saving, loading, and sharing EDSL objects (Surveys, Agents, AgentLists) locally and via the Expected Parrot cloud.

---

# Local File Persistence (save/load)

## Saving to Local Files

```python
from edsl import Survey, Agent, AgentList

# Save (compressed by default)
survey.save("my_survey")       # Creates my_survey.json.gz
agent.save("my_agent")         # Creates my_agent.json.gz
agents.save("my_agents")       # Creates my_agents.json.gz

# Save uncompressed
survey.save("my_survey", compress=False)  # Creates my_survey.json
```

## Loading from Local Files

```python
from edsl import Survey, Agent, AgentList

survey = Survey.load("my_survey")     # Auto-detects .json.gz or .json
agent = Agent.load("my_agent")
agents = AgentList.load("my_agents")
```

## File Format Details

- **Compressed (default)**: `.json.gz` - gzip-compressed JSON, smaller file size
- **Uncompressed**: `.json` - plain JSON, human-readable
- The `load()` method auto-detects the format based on file extension

---

# Cloud Persistence (push/pull)

Objects can be stored on the Expected Parrot cloud platform for sharing and collaboration.

## Pushing to the Cloud

```python
# Basic push (unlisted by default)
response = survey.push()
response = agents.push()

# Push with metadata
response = survey.push(
    description="Customer satisfaction survey Q4 2024",
    alias="customer-satisfaction",
    visibility="private"              # "private", "unlisted", or "public"
)

# Update existing object
response = survey.push(
    alias="customer-satisfaction",
    force=True  # Patches existing object
)
```

## Pulling from the Cloud

```python
# Pull by UUID
survey = Survey.pull("123e4567-e89b-12d3-a456-426614174000")
agents = AgentList.pull("123e4567-e89b-12d3-a456-426614174000")

# Pull by full URL
survey = Survey.pull("https://expectedparrot.com/content/123e4567...")

# Pull by alias URL
survey = Survey.pull("https://expectedparrot.com/content/username/customer-satisfaction")

# Pull by shorthand alias (username/alias)
survey = Survey.pull("username/customer-satisfaction")
```

## Listing Cloud Objects

```python
# List your objects on the cloud
my_surveys = Survey.list()
my_agents = AgentList.list()

# Filter by visibility
public_surveys = Survey.list(visibility="public")

# Search by description
matching = Survey.list(search_query="customer satisfaction")

# Pagination
page_2 = Survey.list(page=2, page_size=20)

# Sort order (default: newest first)
oldest_first = Survey.list(sort_ascending=True)
```

## Managing Cloud Objects

```python
# Update metadata
Survey.patch(
    "123e4567-e89b-12d3-a456-426614174000",
    description="Updated description",
    visibility="public"
)

# Update with new value (instance method)
survey.patch(
    "123e4567-e89b-12d3-a456-426614174000",
    description="Added question 4"
)

# Delete from cloud
Survey.delete("123e4567-e89b-12d3-a456-426614174000")
```

## Visibility Levels

| Level | Description |
|-------|-------------|
| `"private"` | Only you can access |
| `"unlisted"` | Anyone with the URL/UUID can access (default) |
| `"public"` | Discoverable and accessible by everyone |

---

# Git-Based Versioning

```python
# Push to git-based storage
survey.git_push("my-survey")
agents.git_push("my-agent-population")

# Clone from git-based storage
survey = Survey.git_clone("username/my-survey")
agents = AgentList.git_clone("username/my-agent-population")
```

---

# Serialization to Dict/JSON/YAML

```python
# To/from dictionary
d = survey.to_dict()
survey = Survey.from_dict(d)

# To JSON string
json_str = survey.to_json()

# To/from YAML
yaml_str = survey.to_yaml()
survey = Survey.from_yaml(yaml_str)

# Save YAML to file
survey.to_yaml(filename="survey.yaml")
survey = Survey.from_yaml(filename="survey.yaml")
```

---

# SurveyList Persistence

```python
from edsl import SurveyList

surveys = SurveyList([survey1, survey2, survey3])
surveys.save("my_surveys")
surveys = SurveyList.load("my_surveys")
surveys.push(description="Survey collection", alias="my-survey-collection")
surveys = SurveyList.pull("uuid-or-alias")
```

---

# Quick Reference

| Task | Survey | Agent | AgentList |
|------|--------|-------|-----------|
| Save locally | `survey.save("file")` | `agent.save("file")` | `agents.save("file")` |
| Load locally | `Survey.load("file")` | `Agent.load("file")` | `AgentList.load("file")` |
| Push to cloud | `survey.push(alias="...")` | `agent.push(alias="...")` | `agents.push(alias="...")` |
| Pull from cloud | `Survey.pull("uuid")` | `Agent.pull("uuid")` | `AgentList.pull("uuid")` |
| List on cloud | `Survey.list()` | `Agent.list()` | `AgentList.list()` |
| Delete from cloud | `Survey.delete("uuid")` | `Agent.delete("uuid")` | `AgentList.delete("uuid")` |
| To dict | `survey.to_dict()` | `agent.to_dict()` | `agents.to_dict()` |
| From dict | `Survey.from_dict(d)` | `Agent.from_dict(d)` | `AgentList.from_dict(d)` |
