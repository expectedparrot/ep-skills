---
description: Publish a completed study to GitHub
argument-hint: <study directory>
allowed-tools: [Read, Glob, Grep, Bash, Write, AskUserQuestion]
---

# Publish Study

Publish a completed study to GitHub with the analysis report as README.md, all charts, data, and a reproducibility footer.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "Which study directory would you like to publish to GitHub?"

## Instructions

Use the `edsl-research:publish-study` skill to publish.

1. Invoke the `edsl-research:publish-study` skill for the full publishing workflow
2. Create a GitHub repo with the analysis report as README.md
3. Include all charts, data, and supporting files
4. Add a reproducibility footer linking to Expected Parrot
