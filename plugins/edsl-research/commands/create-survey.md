---
description: Create an EDSL survey from a description
argument-hint: <survey description>
allowed-tools: [Read, Glob, Bash, Write, AskUserQuestion]
---

# Create Survey

Create a survey in EDSL based on the user's description.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What is the survey for? Please describe its purpose and any specific topics or questions you'd like to include."

## Instructions

Use the `edsl-research:create-survey` skill to load full EDSL survey reference, then create the survey.

1. Invoke the `edsl-research:create-survey` skill for the complete EDSL Survey API reference
2. Design questions based on the user's description
3. Choose appropriate question types (free text, multiple choice, scale, etc.)
4. Structure the survey flow logically
5. Write a Python file with a descriptive name (e.g., `exit_interview.py`)
6. Save the survey as a local JSON file using:

```python
import os
survey_name = os.path.splitext(os.path.basename(__file__))[0]
survey.save(survey_name)
```
