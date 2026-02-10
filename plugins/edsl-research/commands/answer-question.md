---
description: Answer a question about a generated analysis report
argument-hint: <question> [analysis_dir]
allowed-tools: [Read, Glob, Grep, Bash, Write, AskUserQuestion]
---

# Answer Question

Answer questions about a generated analysis report.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What question do you have about the analysis? If the analysis is in a specific directory, please provide that too."

## Instructions

Use the `edsl-research:answer-question` skill to answer the question.

1. Invoke the `edsl-research:answer-question` skill for the full workflow
2. Read report artifacts from the analysis directory
3. Perform additional analysis if needed
4. Save the answer with metadata
