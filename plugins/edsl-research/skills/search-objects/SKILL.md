---
name: search-objects
description: Search, browse, and pull EDSL objects (Surveys, Results, AgentLists, etc.) from Expected Parrot cloud
allowed-tools: Read, Glob, Bash(python:*), AskUserQuestion, Write
user-invocable: true
arguments: search query or UUID
---

# Search & Pull EDSL Objects from Expected Parrot

Search, browse, and retrieve EDSL objects stored on the Expected Parrot cloud using the Coop API.

## Usage

```
/search-objects customer survey
/search-objects 123e4567-e89b-12d3-a456-426614174000
/search-objects surveys about hiring
/search-objects
```

## Workflow

### 1. Parse the Input

Determine what the user provided:

- **UUID** (36-char hex with dashes, pattern `8-4-4-4-12`): go directly to step 4 (Retrieve)
- **URL** (starts with `http`): extract UUID or alias, go to step 4
- **Search query with type hint** (e.g., "surveys about hiring", "results for experiment"): extract the object type and search keywords, go to step 2
- **Search query without type hint** (e.g., "customer satisfaction"): search across all types, go to step 2
- **Nothing or vague**: use `AskUserQuestion` to ask:

```
Question: "What are you looking for?"
Header: "Search"
Options:
  - "Browse my objects" / "See your own objects on Expected Parrot"
  - "Search community" / "Search public objects shared by others"
  - "Pull by UUID" / "Retrieve a specific object by its UUID or URL"
```

Then follow up with type/keyword questions as needed.

### 2. Search

Run a Python script to search using `Coop().list()`:

```python
from edsl import Coop

coop = Coop()

# Search with filters
objects = coop.list(
    object_type=None,        # or "survey", "results", etc.
    search_query="keyword",  # searches description field
    visibility=None,         # "private", "public", "unlisted", or None for all
    community=False,         # True to search public objects by others
    page=1,
    page_size=10,
    sort_ascending=False,    # newest first by default
)

# Pagination info
print(f"Page {objects.current_page} of {objects.total_pages} ({objects.total_count} total)")

# Display results as a table
print(f"{'#':<4} {'Type':<15} {'Description':<50} {'Owner':<15} {'Visibility':<10} {'UUID':<36}")
print("-" * 130)
for i, obj in enumerate(objects, 1):
    desc = (obj.get("description") or "")[:50]
    print(f"{i:<4} {obj['object_type']:<15} {desc:<50} {obj.get('owner_username',''):<15} {obj['visibility']:<10} {obj['uuid']}")
```

**Type extraction hints** — map natural language to `object_type`:
- "survey(s)" → `"survey"`
- "result(s)" → `"results"`
- "agent(s)" / "agent list(s)" → `"agent_list"` (or `"agent"` for single)
- "scenario(s)" / "scenario list(s)" → `"scenario_list"` (or `"scenario"` for single)
- "question(s)" → `"question"`
- "model(s)" → `"model"` or `"model_list"`
- "cache(s)" → `"cache"`
- "notebook(s)" → `"notebook"`
- "macro(s)" → `"macro"` or `"composite_macro"`

**Supported object types** (all 13):
`agent`, `agent_list`, `cache`, `model`, `model_list`, `notebook`, `question`, `results`, `scenario`, `scenario_list`, `survey`, `macro`, `composite_macro`

### 3. Select

If multiple results are returned, present them to the user with `AskUserQuestion`:

- Show up to 4 options (the top results) with description snippets as labels and type/owner as descriptions
- Include a "Search again" option if the results don't look right
- If there are more pages, mention it: "Showing page 1 of N (M total results)"

If only one result, confirm with the user before pulling, or proceed directly if the match is clearly what they asked for.

### 4. Retrieve

Pull the selected object using the class-level `.pull()` method. First determine the correct class from the object type:

```python
from edsl.coop.utils import ObjectRegistry

# Get the EDSL class for the object type
edsl_class = ObjectRegistry.get_edsl_class_by_object_type(object_type)

# Pull the object
obj = edsl_class.pull(uuid)
```

Or use `Coop().pull()` directly:

```python
from edsl import Coop
coop = Coop()
obj = coop.pull(uuid, expected_object_type=object_type)
```

After pulling, display a summary based on the object type:

| Object Type | Summary to Show |
|-------------|-----------------|
| `survey` | Question count, question names, has rules/memory |
| `results` | Row count, column names (answer/agent/scenario columns) |
| `agent_list` | Agent count, trait names, sample agent traits |
| `agent` | Agent name, trait names and values |
| `scenario_list` | Scenario count, key names, sample values |
| `scenario` | Key names and values |
| `question` | Question type, name, text, options (if applicable) |
| `cache` | Entry count |
| `model` / `model_list` | Model name(s), parameters |
| `notebook` | Cell count |
| `macro` / `composite_macro` | Description, components |

**Summary examples:**

```python
# Survey
print(f"Survey with {len(obj)} questions: {obj.question_names}")

# Results
df = obj.to_pandas()
answer_cols = [c for c in df.columns if c.startswith('answer.')]
agent_cols = [c for c in df.columns if c.startswith('agent.')]
scenario_cols = [c for c in df.columns if c.startswith('scenario.')]
print(f"Results: {len(df)} rows, {len(answer_cols)} questions, {len(agent_cols)} agent traits, {len(scenario_cols)} scenario vars")

# AgentList
print(f"AgentList with {len(obj)} agents, traits: {obj.trait_names}")

# ScenarioList
print(f"ScenarioList with {len(obj)} scenarios, keys: {list(obj[0].keys()) if len(obj) > 0 else []}")
```

### 5. Save

Ask the user if and where to save locally:

```
Question: "Save this object locally?"
Header: "Save"
Options:
  - "Yes, default filename" / "Save as {slug}.json.gz in current directory"
  - "Yes, custom filename" / "Choose a filename and location"
  - "No" / "Don't save, just inspect"
```

Generate a default filename from the description:

```python
import re

def slugify(text, max_length=60):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-')
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]
    return text

filename = slugify(description) + ".json.gz"
```

Save using the `.save()` method:

```python
obj.save(filename)
print(f"Saved to: {filename}")
```

If "custom filename", use `AskUserQuestion` to get the desired filename, then save.

### 6. Report

Summarize what was done:

- What was found (object type, description, owner)
- File path if saved
- Quick-reference for loading it back:

```python
# To load this object later:
from edsl import {ClassName}
obj = {ClassName}.load("{filename}")

# Or pull fresh from the cloud:
obj = {ClassName}.pull("{uuid}")
```

## Class Name Mapping

Map object types to import names for the load-back reference:

| Object Type | Class Name |
|-------------|-----------|
| `survey` | `Survey` |
| `results` | `Results` |
| `agent` | `Agent` |
| `agent_list` | `AgentList` |
| `scenario` | `Scenario` |
| `scenario_list` | `ScenarioList` |
| `question` | `Question` |
| `cache` | `Cache` |
| `model` | `Model` |
| `model_list` | `ModelList` |
| `notebook` | `Notebook` |
| `macro` | `Macro` |
| `composite_macro` | `CompositeMacro` |

## Pagination

If there are multiple pages of results:

```python
# Check pagination
if objects.total_pages > 1:
    print(f"\nShowing page {objects.current_page} of {objects.total_pages} ({objects.total_count} total)")
    print("Use /search-objects to search again or ask for 'next page'")
```

To get the next page, re-run with `page=page+1`.

## Error Handling

- **No results found**: Suggest broadening the search (remove type filter, try different keywords, try `community=True`)
- **UUID not found**: Check if it's a valid UUID format, suggest searching by description instead
- **Authentication error**: Remind user to set up their Expected Parrot API key (`EXPECTED_PARROT_API_KEY` env var or run `edsl config`)
- **Network error**: Suggest checking internet connection and trying again

## Examples

### Search for surveys about customers
```
/search-objects surveys about customers
```
→ Extracts type="survey", query="customers" → runs `coop.list(object_type="survey", search_query="customers")` → shows results → user picks one → pulls and summarizes → offers to save

### Pull by UUID
```
/search-objects 123e4567-e89b-12d3-a456-426614174000
```
→ Detects UUID → runs `coop.pull(uuid)` → shows summary → offers to save

### Browse community objects
```
/search-objects
```
→ No input → asks what user is looking for → user picks "Search community" → asks for type/keywords → searches with `community=True` → shows results
