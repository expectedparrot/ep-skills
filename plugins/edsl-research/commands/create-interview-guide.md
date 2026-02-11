---
description: Generate a qualitative interview guide based on Geiecke & Jaravel (2026)
argument-hint: <research topic or interview description>
allowed-tools: [Read, Glob, Bash, Write, AskUserQuestion]
---

# Create Interview Guide

Generate a qualitative interview guide as an EDSL Survey with QuestionInterview.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What is the research topic for your interview? Describe what you want to learn from respondents."

## Instructions

Use the `edsl-research:create-interview-guide` skill to create the interview guide.

1. Invoke the `edsl-research:create-interview-guide` skill for the full interview guide workflow
2. Follow the interactive workflow to gather requirements
3. Generate the interview guide and EDSL Survey
4. Save as a Python file and JSON
