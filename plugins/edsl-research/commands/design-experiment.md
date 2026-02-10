---
description: Design a detailed experimental plan from a research question
argument-hint: <research question>
allowed-tools: [Read, Write, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, Bash]
---

# Design Experiment

Design a detailed experimental plan from a research question.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What is your research question? Please describe the hypothesis or topic you want to investigate."

## Instructions

Use the `edsl-research:design-experiment` skill to design the experiment.

1. Invoke the `edsl-research:design-experiment` skill for the full experimental design workflow
2. Conduct a brief literature review on the topic
3. Develop a randomization plan
4. Design the survey instrument
5. Perform power analysis and sample size recommendation
6. Output a complete experimental plan
