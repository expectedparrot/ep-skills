---
description: Create an EDSL AgentList from descriptions, web searches, or files
argument-hint: <agent list description>
allowed-tools: [Read, Glob, Bash, WebSearch, WebFetch, AskUserQuestion]
---

# Create Agent List

Create an EDSL AgentList from web searches, descriptions, local files, or programmatic generation.

## Arguments

The user provided: $ARGUMENTS

If no arguments were provided, ask: "What kind of agents do you need? Describe the population or personas you want to create."

## Instructions

Use the `edsl-research:create-agent-list` skill to create the agent list.

1. Invoke the `edsl-research:create-agent-list` skill for the full AgentList creation reference
2. Determine the best source for agents (web search, description, file, or programmatic)
3. Create the AgentList with appropriate traits
4. Save as a Python file and JSON
