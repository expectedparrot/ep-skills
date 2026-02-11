---
description: Generate a comprehensive conjoint analysis report with utilities, charts, and segment analysis
argument-hint: <path to conjoint study directory (optional)>
allowed-tools: [Read, Write, Glob, Grep, Bash, AskUserQuestion]
---

# Analyze Conjoint Results

Generate a comprehensive, self-contained analysis report for a conjoint (choice-based) study.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, the skill will auto-detect study directories by searching for `design_spec.json`.

## Instructions

Use the `edsl-research:analyze-conjoint-results` skill to perform the analysis.

1. Invoke the `edsl-research:analyze-conjoint-results` skill for the full analysis workflow
2. Locate the study directory and load design artifacts
3. Compute part-worth utilities using the conjoint-study helpers
4. Generate charts (importance, utilities, position bias, segment heatmap, price sensitivity)
5. Build a comprehensive report with executive summary, methodology, results, key findings, and limitations
6. Convert to styled HTML via pandoc
