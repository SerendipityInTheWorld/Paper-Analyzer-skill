# Deep Analysis Template
Use when `--mode=deep`. Full narrative with critical evaluation for each dimension.

## Metadata
- Title:
- Authors:
- Venue/Year:
- DOI/Arxiv ID:

## Research Motivation
{detailed context: why this problem is important, real-world or academic drivers, related neighboring areas}

## Problem Definition
{exact gap definition, what prior work fails to address, why existing solutions are insufficient}
{relation to broader literature context}

## Core Contributions
List each contribution with its supporting evidence and novelty assessment:

1. **"{one-sentence claim of contribution 1}"**
Evidence: {which experiments / analyses support this}
Novelty: {truly new / incremental improvement / known technique new application}

2. **"{one-sentence claim of contribution 2}"**
Evidence: {which experiments / analyses support this}
Novelty: {truly new / incremental improvement / known technique new application}

## Methodological Innovation
{detailed explanation of the method, with key design choices and their rationale}
{how it differs from prior approaches}

## Theoretical Framework (Optional)
{formalisms, theoretical assumptions, mathematical foundations — if paper has theoretical contributions}
{are assumptions reasonable? are there hidden assumptions?}
{If no substantial theoretical framework: note "No substantial theoretical framework; design rationale covered in Methodological Innovation"}

## Experimental Framework
For each experiment, provide:

### Experiment N: {Name}
- **Purpose**: What specific claim or hypothesis is being tested?
- **Design**: Dataset choice, baselines, metrics, hyperparameters
- **Procedure**: Step-by-step what was done
- **Results**: Full quantitative results with error bars / significance if reported
- **Interpretation**: What the authors claim vs. what the data actually shows
- **Critical analysis**: 
  - Is the experimental design appropriate for the question?
  - Are the baselines state-of-the-art and fairly tuned?
  - Are the metrics sufficient and unbiased?
  - Are missing controls or confounds present?
- **Evidence strength**: strong / moderate / weak + justification

Cross-experiment analysis:
- Do results across experiments tell a consistent story?
- Are there contradictions or unexplained patterns?

## Key Results
{comprehensive summary of all quantitative findings}
{comparison with prior reported numbers}

## Limitations
For each limitation:
- **Acknowledged by authors**: {yes/no}
- **Severity**: {critical / moderate / minor}
- **Potential remedy**: {how it could be addressed}

## Future Work
- {suggested by paper}
- {implied but not stated}
- **For your own research**: {what you could build on from here}

## Key Insights (for Your Research)
{actionable takeaways you can directly apply to your own work}
- Insight 1: {specific technique/principle} → {how to transfer}
- Insight 2: {specific technique/principle} → {how to transfer}
...

## Quality Assessment
- Strengths: {aspects done well — methodological rigor, originality, clarity, evidence quality}
- Weaknesses: {aspects lacking — missing controls, insufficient baselines, over-claiming, reproducibility concerns}
- Overall Soundness: {high / moderate / low — overall assessment of methodology, evidence, and reasoning quality}
- Reproducibility: {are details sufficient to reproduce? code/data available?}
- Significance: {how important would this be if true?}
