---
description: Design a complete study project from a research question
argument-hint: <research question or description>
allowed-tools: [Read, Glob, Skill, AskUserQuestion, Write]
---

# Create Study

Design a complete survey study from free text requirements.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What would you like to study? Please describe your research question or requirements."

## Instructions

Use the `edsl-research:create-study` skill to create the study.

1. Invoke the `edsl-research:create-study` skill for the full study creation workflow
2. Generate a multi-file study project with Survey, ScenarioList, AgentList, and a Makefile
3. Structure the project for reproducibility
