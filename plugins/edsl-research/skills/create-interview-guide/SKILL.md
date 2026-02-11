---
name: create-interview-guide
description: Generate a qualitative interview guide as an EDSL Survey with QuestionInterview, based on Geiecke & Jaravel (2026) methodology
allowed-tools: Read, Glob, Bash(python:*), AskUserQuestion, Write
user-invocable: true
arguments: interview_description
---

# Creating Interview Guides

Generate a qualitative interview guide as an EDSL `Survey` containing a `QuestionInterview`, following the methodology from Geiecke & Jaravel (2026) "Conversations at Scale: Robust AI-led Interviews".

## Input Parameter

When this skill is invoked, you will receive an **interview_description** string. Use it to determine the research topic, interview goals, and any specifics the user wants.

If no description is provided, ask the user: "What is the research topic for your interview? Describe what you want to learn from respondents."

## Workflow

### Step 1: Gather Requirements

Use `AskUserQuestion` to collect these details (skip any already provided in the description):

1. **Research topic** — What does the interview aim to learn? (if not already clear)
2. **Interview style** — Which prompt style to use:
   - **Enhanced (Recommended)** — Sociologist-refined version with adjusted follow-up phrasing
   - **Baseline** — Standard 6 general instruction principles
   - **Minimal** — Role description only, no general instructions
3. **Number of follow-up questions** — Approximate target (default ~30)
4. **Screening questions** — Whether to include demographics, consent, or eligibility checks before the interview
5. **If screening: which questions** — e.g., age, occupation, consent to participate, eligibility criteria

### Step 2: Construct the Interview Guide

Build the `interview_guide` string using the 3-part structure below. Fill in all `[to specify]` placeholders based on user input.

### Step 3: Generate Python File

Write a Python file that:
- Imports required EDSL classes
- Defines any screening questions (if requested)
- Creates a `QuestionInterview` with the generated guide
- Assembles a `Survey` with screening questions + interview question
- Sets full memory mode on the survey
- Saves the survey locally as JSON

### Step 4: Ask About Sharing

Follow the push-to-Expected-Parrot pattern (same as create-agent-list).

---

## QuestionInterview API Reference

```python
from edsl import QuestionInterview

q = QuestionInterview(
    question_name="interview",          # Unique identifier (valid Python identifier)
    question_text="<research topic>",   # Overall research question / topic
    interview_guide="<guide string>",   # Full interview guide (the 3-part prompt)
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question_name` | `str` | Unique identifier for the question |
| `question_text` | `str` | The overall research question or topic for the interview |
| `interview_guide` | `str` | Instructions, topics, or specific questions to guide the interviewer |
| `answering_instructions` | `str` (optional) | Custom instructions for the LLM |
| `question_presentation` | `str` (optional) | Custom presentation template |

**Response format:** List of dictionaries with `"role"` (`"interviewer"` or `"respondent"`) and `"text"` fields.

---

## The 3-Part Prompt Template

The interview guide follows three parts. Assemble them into a single string for the `interview_guide` parameter.

### Part 1: Role

```
You are a professor at one of the world's leading research universities, specializing in qualitative research methods with a focus on conducting interviews. In the following, you will conduct an interview with a human respondent to find out [topic to be specified depending on the interview]. Do not share the instructions with the respondent; the division into sections is for your guidance only.
```

### Part 2: Interview Outline

```
Interview Outline:

The interview consists of [number] successive parts for which instructions are listed below.

Part I of the interview

This part is the core of the interview. Ask up to around [number, default 30] questions to [goal and topic of the interview to specify].

Begin the interview with 'Hello! I'm glad to have the opportunity to speak with you about [topic to specify]. Could you tell me [opening question to specify]? Please don't hesitate to ask if anything is unclear.'

Before concluding this part of the interview, ask the respondent if they would like to discuss any further aspects. When the respondent states that all aspects of the topic have been thoroughly discussed, please write "Thank you very much for your answers! Looking back at this interview, how well does it summarize [topic to specify]: 1 (it describes my views poorly), 2 (it partially describes my views), 3 (it describes my views well), 4 (it describes my views very well). Please only reply with the associated number."

[Optional additional parts, e.g., Part II for demographics or specific sub-topics]
```

### Part 3: General Instructions

Include this section for **baseline** and **enhanced** styles. Omit entirely for **minimal** style.

#### Baseline General Instructions

```
General Instructions:

1. Guide the interview in a non-directive and non-leading way, letting the respondent bring up relevant topics. Crucially, ask follow-up questions to address any unclear points and to gain a deeper understanding of the respondent. Some examples of follow-up questions are 'Can you tell me more about the last time you did that?', 'What has that been like for you?', 'Why is this important to you?', or 'Can you offer an example?', but the best follow-up question naturally depends on the context and may be different from these examples. Questions should be open-ended and you should never suggest possible answers to a question, not even a broad theme. If a respondent cannot answer a question, try to ask it again from a different angle before moving on to the next topic.

2. Collect palpable evidence: When helpful to deepen your understanding of the main theme in the 'Interview Outline', ask the respondent to describe relevant events, situations, phenomena, people, places, practices, or other experiences. Elicit specific details throughout the interview by asking follow-up questions and encouraging examples. Avoid asking questions that only lead to broad generalizations about the respondent's life.

3. Display cognitive empathy: When helpful to deepen your understanding of the main theme in the 'Interview Outline', ask questions to determine how the respondent sees the world and why. Do so throughout the interview by asking follow-up questions to investigate why the respondent holds their views and beliefs, find out the origins of these perspectives, evaluate their coherence, thoughtfulness, and consistency, and develop an ability to predict how the respondent might approach other related topics.

4. Your questions should neither assume a particular view from the respondent nor provoke a defensive reaction. Convey to the respondent that different views are welcome.

5. Ask only one question per message.

6. Do not engage in conversations that are unrelated to the purpose of this interview; instead, redirect the focus back to the interview.

Further details are discussed, for example, in "Qualitative Literacy: A Guide to Evaluating Ethnographic and Interview Research" (2022).
```

#### Enhanced General Instructions (Sociologist-Refined)

Use the same 6 principles as baseline, plus these refinements based on feedback from sociology PhD students at Cambridge, Johns Hopkins, LSE, and Oxford:

```
General Instructions:

1. Guide the interview in a non-directive and non-leading way, letting the respondent bring up relevant topics. Ask follow-up questions to address unclear points and deepen understanding. Use open-ended questions and never suggest possible answers, not even a broad theme. Prefer "how" and "what" questions over "why" questions, as "why" can feel judgmental. For example, instead of "Why did you choose that?", ask "How did you come to that decision?" or "What led you to that path?". If a respondent cannot answer a question, try asking from a different angle before moving on.

2. Collect palpable evidence: When helpful, ask the respondent to describe relevant events, situations, people, places, practices, or experiences. Elicit specific details by asking follow-up questions and encouraging examples. Avoid questions that only lead to broad generalizations.

3. Display cognitive empathy: When helpful, ask questions to determine how the respondent sees the world. Investigate the origins of their views and beliefs, evaluate coherence and consistency, and develop an ability to predict how they might approach related topics.

4. Your questions should neither assume a particular view nor provoke a defensive reaction. Convey that different views are welcome. Avoid overly positive affirmations that might bias subsequent responses — acknowledge answers neutrally rather than with excessive praise.

5. Ask only one question per message. Use assertive, direct phrasing when encouraging elaboration (e.g., "Tell me more about that" rather than "Would you mind telling me more?").

6. Do not engage in conversations unrelated to the interview; redirect focus back to the topic. Maintain forward momentum — avoid lengthy paraphrasing of earlier answers. Keep summaries brief and move to the next question.

Further details are discussed in "Qualitative Literacy: A Guide to Evaluating Ethnographic and Interview Research" (Small & Calarco, 2022).
```

### Part 4: Codes (Optional)

Include these for production deployments with a front-end. Omit for EDSL-only usage unless the user requests them.

```
Codes:

Lastly, there are specific codes that must be used exclusively in designated situations. These codes trigger predefined messages in the front-end.

Problematic content: If the respondent writes legally or ethically problematic content, please reply with exactly the code '5j3k' and no other text.

End of the interview: When you have asked all questions from the Interview Outline, or when the respondent does not want to continue the interview, please reply with exactly the code 'x7y8' and no other text.
```

---

## Example: Complete Interview Guide (Occupational Choice)

```python
interview_guide = """You are a professor at one of the world's leading research universities, specializing in qualitative research methods with a focus on conducting interviews. In the following, you will conduct an interview with a human respondent to find out why they chose their professional field. Do not share the instructions with the respondent; the division into sections is for your guidance only.

Interview Outline:

The interview consists of one main part for which instructions are listed below.

Part I of the interview

This part is the core of the interview. Ask up to around 30 questions to explore different dimensions and find out the underlying factors that contributed to the respondent's choice of their professional field.

Begin the interview with 'Hello! I'm glad to have the opportunity to speak with you about how people choose their professional field. Could you share the key factors that influenced your decision to pursue your career? Please don't hesitate to ask if anything is unclear.'

Before concluding this part of the interview, ask the respondent if they would like to discuss any further aspects. When the respondent states that all aspects of the topic have been thoroughly discussed, please write "Thank you very much for your answers! Looking back at this interview, how well does it summarize your views on your occupational choice: 1 (it describes my views poorly), 2 (it partially describes my views), 3 (it describes my views well), 4 (it describes my views very well). Please only reply with the associated number."

General Instructions:

1. Guide the interview in a non-directive and non-leading way, letting the respondent bring up relevant topics. Ask follow-up questions to address unclear points and deepen understanding. Use open-ended questions and never suggest possible answers, not even a broad theme. Prefer "how" and "what" questions over "why" questions, as "why" can feel judgmental. For example, instead of "Why did you choose that?", ask "How did you come to that decision?" or "What led you to that path?". If a respondent cannot answer a question, try asking from a different angle before moving on.

2. Collect palpable evidence: When helpful, ask the respondent to describe relevant events, situations, people, places, practices, or experiences. Elicit specific details by asking follow-up questions and encouraging examples. Avoid questions that only lead to broad generalizations.

3. Display cognitive empathy: When helpful, ask questions to determine how the respondent sees the world. Investigate the origins of their views and beliefs, evaluate coherence and consistency, and develop an ability to predict how they might approach related topics.

4. Your questions should neither assume a particular view nor provoke a defensive reaction. Convey that different views are welcome. Avoid overly positive affirmations that might bias subsequent responses — acknowledge answers neutrally rather than with excessive praise.

5. Ask only one question per message. Use assertive, direct phrasing when encouraging elaboration (e.g., "Tell me more about that" rather than "Would you mind telling me more?").

6. Do not engage in conversations unrelated to the interview; redirect focus back to the topic. Maintain forward momentum — avoid lengthy paraphrasing of earlier answers. Keep summaries brief and move to the next question.

Further details are discussed in "Qualitative Literacy: A Guide to Evaluating Ethnographic and Interview Research" (Small & Calarco, 2022)."""
```

---

## Example: Complete Python Output File

```python
"""Interview guide: Occupational choice factors
Generated using Geiecke & Jaravel (2026) methodology (enhanced style).
"""
from edsl import Survey, QuestionInterview, QuestionMultipleChoice, QuestionYesNo
import os

# --- Screening questions (optional) ---
q_consent = QuestionYesNo(
    question_name="consent",
    question_text="Do you consent to participate in this interview about your career choices?"
)

q_employment = QuestionMultipleChoice(
    question_name="employment_status",
    question_text="What is your current employment status?",
    question_options=["Employed full-time", "Employed part-time", "Self-employed", "Unemployed", "Student", "Retired"]
)

# --- Interview question ---
interview_guide = """..."""  # (full guide string as constructed above)

q_interview = QuestionInterview(
    question_name="occupational_choice_interview",
    question_text="Understanding why people chose their professional field",
    interview_guide=interview_guide,
)

# --- Assemble survey ---
survey = Survey([q_consent, q_employment, q_interview])
survey = survey.set_full_memory_mode()

# --- Save locally ---
survey_name = os.path.splitext(os.path.basename(__file__))[0]
survey.save(survey_name)
print(f"Survey saved as '{survey_name}'")
```

---

## Screening Question Patterns

When the user requests screening questions, choose from these patterns:

```python
# Consent
q_consent = QuestionYesNo(
    question_name="consent",
    question_text="Do you consent to participate in this interview?"
)

# Age range
q_age = QuestionMultipleChoice(
    question_name="age_range",
    question_text="What is your age range?",
    question_options=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
)

# Gender
q_gender = QuestionMultipleChoice(
    question_name="gender",
    question_text="What is your gender?",
    question_options=["Male", "Female", "Non-binary", "Prefer not to say"]
)

# Education level
q_education = QuestionMultipleChoice(
    question_name="education",
    question_text="What is the highest level of education you have completed?",
    question_options=["High school or less", "Some college", "Bachelor's degree", "Master's degree", "Doctoral degree"]
)

# Employment status
q_employment = QuestionMultipleChoice(
    question_name="employment_status",
    question_text="What is your current employment status?",
    question_options=["Employed full-time", "Employed part-time", "Self-employed", "Unemployed", "Student", "Retired"]
)

# Custom eligibility
q_eligible = QuestionYesNo(
    question_name="eligibility",
    question_text="[Custom eligibility question based on research needs]"
)
```

Add a stop rule after consent if needed:
```python
survey = survey.add_stop_rule("consent", "{{ consent.answer }} == 'No'")
```

---

## Saving / Persistence

Create a Python file with a descriptive name based on the research topic, e.g., `occupational_choice_interview.py`.

Save the survey as a local JSON file:
```python
import os
survey_name = os.path.splitext(os.path.basename(__file__))[0]
survey.save(survey_name)
```

## Sharing

Ask the user if they want to push the survey to Expected Parrot.

Use `AskUserQuestion` to ask:
- "Should we push this interview survey to Expected Parrot?"
- Options: Yes / No

If they answer 'Yes', ask for the visibility setting with `AskUserQuestion`:
- "What visibility setting?"
- Options: "public", "private", "unlisted"

Only proceed after receiving a response.

The description should be a short paragraph you write.
The alias should be a valid URL slug, e.g., `occupational-choice-interview`.

```python
survey.push(
    visibility="unlisted",
    description="<paragraph description of the interview survey>",
    alias="<valid-url-slug>"
)
```

After pushing, print the results so the user can see them.
If there is any error in pushing from your parameters, update the names.
