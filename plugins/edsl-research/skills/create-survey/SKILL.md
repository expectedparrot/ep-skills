---
name: create-survey
description: Create Surveys from questions, QSF files, or programmatically with branching logic
allowed-tools: Read, Glob, Bash(python:*), AskUserQuestion
user-invocable: true
arguments: survey_description
---

# Creating Surveys

You will create a survey in EDSL. 

## Input Parameter

When this skill is invoked, you will receive a **survey_description** string that explains the purpose and context of the survey. Use this description to:

1. Determine the appropriate questions to include
2. Choose suitable question types (free text, multiple choice, scale, etc.)
3. Structure the survey flow logically
4. Name the output file descriptively based on the survey's purpose

If no description is provided, ask the user: "What is the survey for? Please describe its purpose and any specific topics or questions you'd like to include." 

## Basic Survey Creation

```python
from edsl import Survey, QuestionFreeText, QuestionMultipleChoice

# Create questions
q1 = QuestionFreeText(
    question_name="name",
    question_text="What is your name?"
)
q2 = QuestionMultipleChoice(
    question_name="color",
    question_text="What is your favorite color?",
    question_options=["Red", "Blue", "Green", "Yellow"]
)
q3 = QuestionFreeText(
    question_name="why_color",
    question_text="Why do you like that color?"
)

# Create survey from list of questions
survey = Survey([q1, q2, q3])
```

## Adding Questions Incrementally

Survey is immutable - each operation returns a new Survey instance:

```python
from edsl import Survey, QuestionFreeText

survey = Survey()

# Each add_question returns a NEW survey
survey = survey.add_question(QuestionFreeText(
    question_name="q1",
    question_text="First question?"
))

survey = survey.add_question(QuestionFreeText(
    question_name="q2",
    question_text="Second question?"
))

# Add at specific index
survey = survey.add_question(new_question, index=1)
```

## Adding Instructions

Instructions are displayed to respondents between questions:

```python
from edsl import Survey, Instruction

instruction = Instruction(
    text="Please answer the following questions honestly.",
    name="intro"  # Optional name
)

# Add instruction at the beginning
survey = survey.add_instruction(instruction, index=0)

# Add instruction between questions
survey = survey.add_instruction(
    Instruction(text="Now for some demographic questions..."),
    index=3
)
```

## Question Types Available

To see the question types available, use 

```python
from edsl import Question 
Question.available()
```

You can import them like so: 
```python
from edsl import (
    QuestionFreeText,        # Open-ended text response
    QuestionMultipleChoice,  # Single selection from options
    QuestionCheckBox,        # Multiple selections allowed
    QuestionLinearScale,     # Numeric scale (1-5, 1-10, etc.)
    QuestionNumerical,       # Numeric answer
    QuestionYesNo,           # Yes/No question
    QuestionList,            # Return a list of items
    QuestionRank,            # Rank items in order
    QuestionMatrix,          # Grid/matrix question
)
```

## Survey with Piping (Dynamic Text)

Reference previous answers in question text:

```python
q1 = QuestionFreeText(
    question_name="name",
    question_text="What is your name?"
)
q2 = QuestionFreeText(
    question_name="greeting",
    question_text="Hello {{ name.answer }}! How are you today?"
)

survey = Survey([q1, q2])
# q2 will display the answer from q1 in its text
```

## Chaining Operations

Survey methods can be chained since each returns a new Survey:

```python
survey = (Survey([q1, q2, q3])
    .add_rule("q1", "{{ q1.answer }} == 'skip'", "q3")
    .add_skip_rule("q2", "{{ q1.answer }} == 'skip'")
    .add_question(q4))

```


## Saving 
You will create a Python file with a descriptive name e.g., 'exit_interview.py'
Whatever the name of your survey, you will also save it as local JSON file:
```python
import os
survey_name = os.path.splitext(os.path.basename(__file__))[0]
survey.save(survey_name)
```

## Quick Reference

| Task | Method |
|------|--------|
| Create survey | `Survey([q1, q2, q3])` |
| Add question | `survey.add_question(q, index=None)` |
| Add instruction | `survey.add_instruction(inst, index=0)` |
| Get question | `survey.get("question_name")` |
| List questions | `survey.questions` |
| Question names | `survey.question_names` |
| Number of questions | `len(survey)` |
