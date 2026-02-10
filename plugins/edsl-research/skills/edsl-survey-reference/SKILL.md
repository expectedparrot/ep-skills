---
name: edsl-survey-reference
description: EDSL survey reference - question types, templating, rules, memory, helpers, and visualization
allowed-tools: Read, Glob, Bash(python:*)
---

# EDSL Survey Reference

Consolidated reference for building surveys with EDSL: question types, Jinja2 templating, skip/navigation rules, memory modes, helper utilities, and visualization.

---

# Question Types

EDSL provides a comprehensive set of question types for surveys. All questions require `question_name` (a valid Python identifier) and `question_text`.

## Core Question Types

### QuestionFreeText

Open-ended text responses without constraints.

```python
from edsl import QuestionFreeText

q = QuestionFreeText(
    question_name="feedback",
    question_text="What do you think about our service?"
)
```

### QuestionMultipleChoice

Single selection from a predefined list of options.

```python
from edsl import QuestionMultipleChoice

q = QuestionMultipleChoice(
    question_name="color",
    question_text="What is your favorite color?",
    question_options=["Red", "Blue", "Green", "Yellow"]
)
```

### QuestionCheckBox

Multiple selections from a predefined list (checkbox-style).

```python
from edsl import QuestionCheckBox

q = QuestionCheckBox(
    question_name="features",
    question_text="Which features do you use? (Select all that apply)",
    question_options=["Feature A", "Feature B", "Feature C", "Feature D"],
    min_selections=1,      # Optional: minimum selections required
    max_selections=3       # Optional: maximum selections allowed
)
```

### QuestionNumerical

Numeric responses with optional min/max bounds.

```python
from edsl import QuestionNumerical

q = QuestionNumerical(
    question_name="age",
    question_text="How old are you?",
    min_value=0,           # Optional: minimum allowed value
    max_value=120          # Optional: maximum allowed value
)
```

### QuestionYesNo

Simple binary yes/no question (derived from MultipleChoice).

```python
from edsl import QuestionYesNo

q = QuestionYesNo(
    question_name="consent",
    question_text="Do you agree to participate in this survey?"
)
# Options are automatically ["Yes", "No"]
```

### QuestionLinearScale

Linear scale with customizable range and endpoint labels.

```python
from edsl import QuestionLinearScale

q = QuestionLinearScale(
    question_name="satisfaction",
    question_text="How satisfied are you with our service?",
    question_options=[1, 2, 3, 4, 5],           # Scale values
    option_labels={1: "Very Unsatisfied", 5: "Very Satisfied"}  # Endpoint labels
)
```

### QuestionLikertFive

Standard 5-point Likert scale (agree/disagree).

```python
from edsl import QuestionLikertFive

q = QuestionLikertFive(
    question_name="statement_agree",
    question_text="I find the product easy to use."
)
# Options: Strongly disagree, Disagree, Neutral, Agree, Strongly agree
```

### QuestionList

Response as a list of items.

```python
from edsl import QuestionList

q = QuestionList(
    question_name="top_movies",
    question_text="List your top 3 favorite movies.",
    max_list_items=3       # Optional: maximum items allowed
)
```

### QuestionRank

Ranking/ordering items by preference.

```python
from edsl import QuestionRank

q = QuestionRank(
    question_name="priority",
    question_text="Rank these features by importance (1 = most important):",
    question_options=["Speed", "Security", "Price", "Support"],
    num_selections=4       # How many items to rank
)
```

### QuestionMatrix

Grid-based responses with rows (items) and columns (options).

```python
from edsl import QuestionMatrix

q = QuestionMatrix(
    question_name="product_ratings",
    question_text="Rate each product on the following attributes:",
    question_items=["Product A", "Product B", "Product C"],      # Rows
    question_options=["Poor", "Fair", "Good", "Excellent"],      # Columns
    option_labels=None     # Optional labels for options
)
```

### QuestionBudget

Allocating a fixed budget across multiple options.

```python
from edsl import QuestionBudget

q = QuestionBudget(
    question_name="time_allocation",
    question_text="How would you allocate 100 hours across these activities?",
    question_options=["Work", "Exercise", "Leisure", "Sleep"],
    budget_sum=100         # Total that allocations must sum to
)
```

### QuestionDict

Response as key-value pairs (structured data).

```python
from edsl import QuestionDict

q = QuestionDict(
    question_name="contact_info",
    question_text="Provide your contact information:",
    answer_keys=["name", "email", "phone"]  # Required keys in response
)
```

### QuestionExtract

Extracting specific information from text.

```python
from edsl import QuestionExtract

q = QuestionExtract(
    question_name="entities",
    question_text="Extract all company names from the following text: {{ text }}",
    answer_template={"companies": "List of company names"}
)
```

### QuestionDropdown

BM25-powered search through large option sets.

```python
from edsl import QuestionDropdown

q = QuestionDropdown(
    question_name="country",
    question_text="Select your country:",
    question_options=["Afghanistan", "Albania", ..., "Zimbabwe"]  # Large list
)
```

## Derived/Special Question Types

### QuestionMultipleChoiceWithOther

Multiple choice with an "Other" option for custom responses.

```python
from edsl import QuestionMultipleChoiceWithOther

q = QuestionMultipleChoiceWithOther(
    question_name="source",
    question_text="How did you hear about us?",
    question_options=["Google", "Friend", "Advertisement"],
    other_option_label="Other (please specify)"
)
```

### QuestionCheckboxWithOther

Checkbox with an "Other" option for custom responses.

```python
from edsl import QuestionCheckboxWithOther

q = QuestionCheckboxWithOther(
    question_name="interests",
    question_text="What are your interests?",
    question_options=["Sports", "Music", "Reading"],
    other_option_label="Other"
)
```

### QuestionTopK

Select top K items from a list.

```python
from edsl import QuestionTopK

q = QuestionTopK(
    question_name="favorites",
    question_text="Select your top 3 favorite items:",
    question_options=["A", "B", "C", "D", "E"],
    k=3
)
```

### QuestionFunctional

Python function-based question (not sent to LLM - computed locally).

```python
from edsl import QuestionFunctional

def compute_sum(scenario, agent):
    numbers = scenario.get("numbers", [])
    return sum(numbers)

q = QuestionFunctional(
    question_name="total",
    question_text="Calculate the sum",
    func=compute_sum
)
```

### QuestionPydantic

Use custom Pydantic models as response schemas.

```python
from edsl import QuestionPydantic
from pydantic import BaseModel

class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

q = QuestionPydantic(
    question_name="person",
    question_text="Describe a person:",
    pydantic_model=PersonInfo
)
```

### QuestionMarkdown

Responses with markdown formatting.

```python
from edsl import QuestionMarkdown

q = QuestionMarkdown(
    question_name="formatted_response",
    question_text="Write a formatted response with headers and lists."
)
```

## Common Parameters

All questions support these common parameters:

| Parameter | Description |
|-----------|-------------|
| `question_name` | Unique identifier (valid Python identifier) |
| `question_text` | The question text (supports Jinja2 templating) |
| `answering_instructions` | Optional custom instructions for the LLM |
| `question_presentation` | Optional custom presentation template |

## Question Type Quick Reference

| Type | Use Case | Key Parameter |
|------|----------|---------------|
| `QuestionFreeText` | Open-ended responses | - |
| `QuestionMultipleChoice` | Single selection | `question_options` |
| `QuestionCheckBox` | Multiple selections | `question_options` |
| `QuestionNumerical` | Numbers | `min_value`, `max_value` |
| `QuestionYesNo` | Binary yes/no | - |
| `QuestionLinearScale` | Numeric scale | `question_options`, `option_labels` |
| `QuestionLikertFive` | 5-point agree/disagree | - |
| `QuestionList` | List of items | `max_list_items` |
| `QuestionRank` | Ordering | `question_options`, `num_selections` |
| `QuestionMatrix` | Grid/table | `question_items`, `question_options` |
| `QuestionBudget` | Budget allocation | `question_options`, `budget_sum` |
| `QuestionDict` | Key-value pairs | `answer_keys` |
| `QuestionExtract` | Extract from text | `answer_template` |
| `QuestionDropdown` | Large option sets | `question_options` |

---

# Jinja2 Templating in Questions

EDSL uses Jinja2 templating to create dynamic questions. Template variables are enclosed in `{{ }}` and are rendered at runtime with values from scenarios, agents, or previous answers.

## Scenario Templating

Scenarios provide key-value data that gets substituted into questions:

```python
from edsl import QuestionFreeText, Scenario

q = QuestionFreeText(
    question_name="opinion",
    question_text="What do you think about {{ scenario.fruit }}?"
)

scenarios = [
    Scenario({"fruit": "apples"}),
    Scenario({"fruit": "oranges"}),
    Scenario({"fruit": "bananas"})
]

results = q.by(scenarios).run()
```

### Multiple Variables

```python
q = QuestionFreeText(
    question_name="review",
    question_text="Review the {{ scenario.product }} priced at ${{ scenario.price }}."
)

scenario = Scenario({"product": "Widget X", "price": 29.99})
```

### Nested Scenario Data

```python
q = QuestionFreeText(
    question_name="address",
    question_text="Describe the location: {{ scenario.location.city }}, {{ scenario.location.country }}"
)

scenario = Scenario({
    "location": {
        "city": "Paris",
        "country": "France"
    }
})
```

### Full Scenario Access

```python
q = QuestionFreeText(
    question_name="summary",
    question_text="Given this data: {{ scenario }}, provide a summary."
)
```

## Agent Templating

Reference agent traits in questions:

```python
from edsl import QuestionFreeText, Agent

q = QuestionFreeText(
    question_name="perspective",
    question_text="As a {{ agent.occupation }}, what do you think about remote work?"
)

agent = Agent(traits={"occupation": "software engineer", "age": 35})
results = q.by(agent).run()
```

## Piping (Answer References)

Reference previous answers within a survey:

```python
from edsl import Survey, QuestionFreeText, QuestionMultipleChoice

q1 = QuestionFreeText(
    question_name="name",
    question_text="What is your name?"
)

q2 = QuestionFreeText(
    question_name="greeting",
    question_text="Hello {{ name.answer }}! How are you today?"
)

survey = Survey([q1, q2])
```

## Templating in Question Options

```python
q = QuestionMultipleChoice(
    question_name="preference",
    question_text="Which {{ scenario.category }} do you prefer?",
    question_options=[
        "{{ scenario.option_a }}",
        "{{ scenario.option_b }}",
        "{{ scenario.option_c }}"
    ]
)
```

## Conditional Logic in Templates

```python
q = QuestionFreeText(
    question_name="advice",
    question_text="""
    {% if scenario.age < 18 %}
    As a young person, what advice would you give your peers?
    {% else %}
    As an adult, what advice would you give young people?
    {% endif %}
    """
)
```

## Template Variables Reference

| Variable | Access Pattern | Example |
|----------|---------------|---------|
| Scenario value | `{{ scenario.key }}` | `{{ scenario.fruit }}` |
| Nested scenario | `{{ scenario.obj.key }}` | `{{ scenario.location.city }}` |
| Full scenario | `{{ scenario }}` | Converts to string |
| Agent trait | `{{ agent.trait }}` | `{{ agent.occupation }}` |
| Prior answer | `{{ question_name.answer }}` | `{{ q1.answer }}` |

## Best Practices

1. **Use descriptive scenario keys**: `{{ scenario.product_name }}` over `{{ scenario.p }}`
2. **Test templates**: Use `question.render(scenario_dict)` to test rendering
3. **Handle missing values**: `"{{ scenario.name | default('Unknown') }}"`
4. **Avoid forward references**: Only reference questions that come BEFORE the current question

---

# Survey Rules and Flow Control

Rules define conditional navigation through surveys using Jinja2 template expressions.

## Rule Types

| Type | When Evaluated | Purpose |
|------|----------------|---------|
| Skip Rule | BEFORE question | Skip question entirely if condition is True |
| Navigation Rule | AFTER question | Jump to specific question based on answer |
| Stop Rule | AFTER question | End survey if condition is True |

## Skip Rules (Before Rules)

```python
survey = Survey([q1, q2, q3])

# Skip pet_name if no pet
survey = survey.add_skip_rule(
    "pet_name",
    "{{ has_pet.answer }} == 'No'"
)
```

## Navigation Rules (After Rules)

```python
survey = (survey
    .add_rule("preference", "{{ preference.answer }} == 'A'", "section_a")
    .add_rule("preference", "{{ preference.answer }} == 'B'", "section_b")
    .add_rule("preference", "{{ preference.answer }} == 'C'", "section_c"))

# Also skip sections that shouldn't be shown
survey = (survey
    .add_skip_rule("section_a", "{{ preference.answer }} != 'A'")
    .add_skip_rule("section_b", "{{ preference.answer }} != 'B'")
    .add_skip_rule("section_c", "{{ preference.answer }} != 'C'"))
```

## Stop Rules (Early Termination)

```python
survey = survey.add_stop_rule(
    "eligibility",
    "{{ eligibility.answer }} == 'No'"
)
```

## Expression Syntax

```python
"{{ question_name.answer }} == 'value'"
"{{ age.answer }} > 18"
"{{ q1.answer }} == 'yes' and {{ q2.answer }} != 'no'"
"{{ agent.persona }} == 'expert'"
"{{ scenario.condition }} == 'treatment'"
"randint(1, 10) > 5"
```

## Rule Priority

```python
survey = survey.add_rule("q1", "{{ q1.answer }} == 'special'", "special_section", priority=1)
survey = survey.add_rule("q1", "{{ q1.answer }} != ''", "normal_section", priority=0)
```

## EndOfSurvey Marker

```python
from edsl.surveys.navigation_markers import EndOfSurvey

survey = survey.add_rule("screening", "{{ screening.answer }} == 'disqualified'", EndOfSurvey)
```

## Common Rule Patterns

```python
# Branching survey
survey = (Survey([q1, section_a, section_b, conclusion])
    .add_rule("q1", "{{ q1.answer }} == 'A'", "section_a")
    .add_rule("q1", "{{ q1.answer }} == 'B'", "section_b")
    .add_skip_rule("section_a", "{{ q1.answer }} != 'A'")
    .add_skip_rule("section_b", "{{ q1.answer }} != 'B'"))

# Screening with early exit
survey = (Survey([screener, main_q1, main_q2, main_q3])
    .add_stop_rule("screener", "{{ screener.answer }} == 'No'"))

# Conditional follow-up
survey = (Survey([main_q, followup, next_q])
    .add_skip_rule("followup", "{{ main_q.answer }} != 'Yes'"))
```

## Rules Quick Reference

| Task | Method |
|------|--------|
| Add skip rule | `survey.add_skip_rule(question, expression)` |
| Add navigation rule | `survey.add_rule(question, expression, next_question)` |
| Add stop rule | `survey.add_stop_rule(question, expression)` |
| Set priority | `survey.add_rule(q, expr, next_q, priority=1)` |
| View rules | `survey.show_rules()` |
| Jump to end | `survey.add_rule(q, expr, EndOfSurvey)` |

---

# Survey Memory System

Memory controls which previous question-answer pairs an agent sees when answering each question.

## Memory Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| No Memory | Agent sees no prior answers | Independent questions |
| Full Memory | Agent sees ALL prior answers | Conversational surveys |
| Lagged Memory | Agent sees last N answers | Recent context only |
| Targeted Memory | Specific questions see specific priors | Precise control |

## Full Memory Mode

```python
survey = Survey([q1, q2, q3, q4, q5])
survey = survey.set_full_memory_mode()
```

## Lagged Memory Mode

```python
survey = Survey([q1, q2, q3, q4, q5])
survey = survey.set_lagged_memory(lags=2)
```

## Targeted Memory

```python
survey = survey.add_targeted_memory("q3", "q1")
survey = survey.add_memory_collection("summary", ["q1", "q2", "q3"])

# Chain multiple targeted memories
survey = (survey
    .add_targeted_memory("q3", "q1")
    .add_targeted_memory("q4", "q2")
    .add_memory_collection("summary", ["q1", "q2", "q3", "q4"]))
```

## Combining Memory Modes

```python
survey = (Survey([intro, q1, q2, q3, q4, summary])
    .set_lagged_memory(lags=1)
    .add_memory_collection("summary", ["q1", "q2", "q3", "q4"]))
```

## Memory Quick Reference

| Task | Method |
|------|--------|
| Full memory | `survey.set_full_memory_mode()` |
| Lagged memory | `survey.set_lagged_memory(lags=N)` |
| Single targeted | `survey.add_targeted_memory(focal, prior)` |
| Multiple targeted | `survey.add_memory_collection(focal, [priors])` |
| View memory plan | `survey.memory_plan` |

---

# Survey Helper Utilities

## Question Renaming

```python
# Rename and auto-update ALL references (rules, memory, piping)
new_survey = survey.with_renamed_question("q1", "intro_question")
```

## Matrix Combiner

Combine multiple MC questions with same options into a matrix:

```python
from edsl.surveys.survey_helpers.matrix_combiner import combine_multiple_choice_to_matrix

new_survey = combine_multiple_choice_to_matrix(
    survey=survey,
    question_names=["trust_freelancer", "trust_ai", "trust_agency"],
    matrix_question_name="trust_matrix"
)
```

## Follow-up Questions

Auto-generate conditional follow-ups for each MC option:

```python
q_restaurant = QuestionMultipleChoice(
    question_name="restaurants",
    question_text="Which restaurant do you prefer?",
    question_options=["Italian", "Chinese", "Mexican"]
)

q_followup = QuestionFreeText(
    question_name="why_restaurant",
    question_text="Why do you like {{ restaurants.answer }}?"
)

survey = Survey([q_restaurant])
survey = survey.add_followup_questions("restaurants", q_followup)
```

## Other Operations

```python
survey = survey.delete_question("question_name")
survey = survey.move_question("question_name", new_index=0)
```

## Helpers Quick Reference

| Task | Method |
|------|--------|
| Rename question | `survey.with_renamed_question(old, new)` |
| Combine to matrix | `combine_multiple_choice_to_matrix(survey, names, new_name)` |
| Add follow-ups | `survey.add_followup_questions(ref_q, template)` |
| Delete question | `survey.delete_question(name)` |
| Move question | `survey.move_question(name, new_index)` |

---

# Survey Visualization

Visualize survey structure using Mermaid diagrams.

## Mermaid Flowchart

```python
from edsl.surveys.survey_helpers.survey_mermaid import SurveyMermaidVisualization

viz = SurveyMermaidVisualization(survey)
mermaid_code = viz.to_mermaid()
print(mermaid_code)
```

## Visualization Options

```python
viz = SurveyMermaidVisualization(
    survey,
    max_text_length=40,
    show_options=True,
    show_piping=True,
    show_default_flow=True
)
```

## Diagram Elements

| Element | Meaning |
|---------|---------|
| Solid arrow `-->` | Sequential flow |
| Dashed arrow `-.->` | Skip rule |
| Solid arrow with label | Navigation rule |
| Dotted arrow | Piping dependency |

## Other Visualization

```python
survey.show_rules()           # Text-based rule table
dag = survey.dag              # Dependency graph
```

## Visualization Quick Reference

| Task | Method |
|------|--------|
| Create visualization | `SurveyMermaidVisualization(survey)` |
| Get Mermaid code | `viz.to_mermaid()` |
| Display in Jupyter | `viz` (auto-renders) |
| Show rules (text) | `survey.show_rules()` |
| Get DAG | `survey.dag` |
