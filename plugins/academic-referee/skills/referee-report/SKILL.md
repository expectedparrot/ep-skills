---
name: referee-report
description: Write a detailed referee report for an academic paper in economics or a related discipline
allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, Bash
user-invocable: true
arguments: paper_path
---

# Referee Report

Takes a path to an academic paper (PDF) and produces a detailed, structured referee report following the conventions of economics and related social science journals. The report is saved as a Markdown file alongside the paper.

## Usage

```
/referee-report ~/papers/smith-jones-2025-labor-supply.pdf
/referee-report ./submissions/manuscript.pdf
```

## Workflow

### 0. Locate and Read the Paper

1. **Validate the input path.** If the user provided a path, confirm it exists using `Glob`. If the path is a directory, look for PDF files inside it. If no path was provided, use AskUserQuestion to request one.

2. **Read the paper.** Use the `Read` tool on the PDF. For long papers (more than 10 pages), read in batches of 15-20 pages at a time to ensure complete coverage. You MUST read the **entire** paper before writing the report — do not skip appendices, tables, figures, or references.

3. **Determine the output path.** The report will be saved as `referee_report.md` in the same directory as the paper. If a report already exists, use AskUserQuestion:

```
Question: "A referee report already exists at <path>. What would you like to do?"
Header: "Existing report"
Options:
  1. "Overwrite" - "Replace the existing report with a new one"
  2. "Cancel" - "Keep the existing report unchanged"
```

### 1. Understand the Paper

Before writing anything, carefully analyze:

- **Research question**: What is the paper trying to answer?
- **Contribution**: What is novel relative to existing literature?
- **Methodology**: What empirical strategy, theoretical framework, or computational approach is used?
- **Data**: What data are used? How are key variables constructed?
- **Main results**: What are the central findings?
- **Robustness**: What robustness checks are performed?
- **Limitations**: What does the paper acknowledge, and what does it miss?

### 2. Optional Literature Context

Use AskUserQuestion:

```
Question: "Would you like me to do a quick web search for related papers to better assess novelty and positioning in the literature?"
Header: "Lit search"
Options:
  1. "Yes (Recommended)" - "Search for closely related work to assess contribution and novelty"
  2. "No, just review the paper as-is" - "Write the report based solely on the manuscript"
```

If yes, use WebSearch to find 3-5 closely related papers. Focus on:
- Direct precedents for the research question
- Papers using similar methods on similar questions
- Recent surveys or handbook chapters on the topic

This context helps you assess novelty and whether the paper adequately engages with the literature. Incorporate what you learn into the report, but do not pad the report with tangential references.

### 3. Write the Referee Report

Write the report in the following structure. Use clear, direct, professional prose. Be constructive — the goal is to help the authors improve the paper, not to demonstrate cleverness. Where you raise a concern, explain *why* it matters and, when possible, suggest a path forward.

---

#### Report Structure

```markdown
# Referee Report

**Paper**: [Title]
**Authors**: [if identifiable; otherwise "Anonymous"]
**Date of report**: [today's date]

## Summary

[One to two paragraphs summarizing what the paper does, how it does it, and what it finds. This demonstrates to the editor and authors that you understood the paper. Be precise about the research question, the identification strategy or theoretical approach, the data, and the headline results. Do not editorialize here — just summarize.]

## Assessment of Contribution

[One to two paragraphs evaluating the paper's contribution. Consider:
- Is the research question important and well-motivated?
- Is the contribution incremental or substantial?
- How does it relate to and advance the existing literature?
- Is there a clear "value-added" relative to what we already know?]

## Major Comments

[Numbered list of substantive concerns that could affect the paper's conclusions or publishability. These are issues that the authors MUST address. Each comment should:
1. State the concern clearly
2. Explain why it matters (e.g., threatens identification, limits external validity, etc.)
3. Where possible, suggest how the authors might address it

Examples of major comments:
- Identification concerns (omitted variables, reverse causality, selection)
- Questionable assumptions in the theoretical model
- Missing important robustness checks
- Inadequate engagement with closely related work
- Mismatch between claims and evidence
- Sample or data concerns that affect interpretation
- Internal inconsistencies in results

Typically 3-8 major comments. Be specific — reference particular tables, equations, or sections.]

## Minor Comments

[Numbered list of smaller issues that should be addressed but are unlikely to change the paper's conclusions. These include:
- Presentation improvements
- Requests for clarification
- Suggestions for additional discussion
- Notation inconsistencies
- Missing variable definitions
- Figures or tables that could be improved
- Minor econometric points (e.g., clustering, standard error computation)
- Typos or grammatical errors worth noting (do not exhaustively catalog typos — just flag a few representative ones if the paper needs proofreading)

Typically 5-15 minor comments.]

## Questions for the Authors

[Optional section. Numbered list of genuine questions — things you are curious about or that would help you evaluate the paper. These are distinct from criticisms; they are requests for information or clarification that could go either way.]

## Overall Assessment

[One paragraph with your overall take. Weigh the strengths against the weaknesses. Is this a paper that, if the major concerns are addressed, would make a meaningful contribution? Be honest but fair.

End with an explicit recommendation. Use one of:
- **Accept**: The paper is ready for publication with at most minor revisions.
- **Minor Revision**: The paper is strong but needs small changes. A re-review is likely unnecessary.
- **Major Revision**: The paper has potential but significant concerns need to be addressed. The authors should resubmit and the paper should be re-reviewed.
- **Reject**: The paper has fundamental problems that cannot be addressed through revision, or the contribution is insufficient for the journal.]
```

---

### 4. Calibration Guidelines

Follow these norms when writing the report:

**Tone**
- Professional, constructive, and respectful. Write the report you would want to receive.
- Avoid dismissive language ("the authors fail to...", "obviously...", "trivially...").
- Use "the paper" rather than "the authors" when discussing weaknesses (e.g., "the paper does not address..." rather than "the authors neglect to...").
- It's fine to note strengths — a good referee report is not purely critical.

**Substance**
- Every major comment should have a clear "so what" — explain why the issue matters for the paper's conclusions.
- Be specific. Reference equation numbers, table numbers, page numbers, and variable names.
- Do not demand that the paper be a different paper. Evaluate what the authors set out to do, not what you would have done.
- Distinguish between fatal flaws and issues that can be fixed.
- If the identification strategy is fundamentally sound, say so — don't just list every conceivable threat to validity.

**Scope**
- A good report is typically 2-5 pages (roughly 1000-3000 words).
- Quality over quantity. A few incisive major comments are more valuable than an exhaustive list of nitpicks.
- If the paper is in a field you don't know well, be transparent about the limits of your assessment rather than bluffing.

**Economics-Specific Conventions**
- For empirical papers, pay close attention to identification strategy, standard errors, and robustness.
- For theory papers, assess whether assumptions are reasonable and results are novel.
- For structural papers, evaluate both the model and the estimation approach.
- For lab/field experiments, consider internal validity, external validity, and pre-registration.
- For computational/simulation papers, assess calibration, sensitivity, and validation.

### 5. Save the Report

1. Write the completed report to `referee_report.md` in the same directory as the paper using the `Write` tool.
2. Inform the user that the report has been saved and provide the path.
3. Ask if they would like to modify any section or adjust the tone/emphasis.

```
Question: "The report has been saved. Would you like to adjust anything?"
Header: "Follow-up"
Options:
  1. "Looks good" - "No changes needed"
  2. "Adjust tone" - "Make the report more or less critical"
  3. "Expand a section" - "Add more detail to a specific section"
  4. "Add/remove comments" - "I want to add or remove specific points"
```
