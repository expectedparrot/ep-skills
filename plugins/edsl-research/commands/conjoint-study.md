---
description: Design, execute, and analyze a conjoint analysis study
argument-hint: <research question or product/service to study>
allowed-tools: [Read, Write, Glob, Grep, Skill, AskUserQuestion, Bash]
---

# Conjoint Study

Design, execute, and analyze a conjoint analysis (choice experiment) study.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What product or service would you like to study? Please describe the decision context and trade-offs you're interested in measuring."

## Instructions

Use the `edsl-research:conjoint-study` skill to create the conjoint study.

1. Invoke the `edsl-research:conjoint-study` skill for the full conjoint analysis workflow
2. Guide the user through attribute and level definition
3. Generate a balanced experimental design
4. Create EDSL project files (Survey, ScenarioList, AgentList, runner, analysis)
5. Optionally run the study and analyze results with part-worth utilities
