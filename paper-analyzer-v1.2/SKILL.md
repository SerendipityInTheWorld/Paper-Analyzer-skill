---
name: paper-analyzer
description: Analyze academic papers from local PDF files, URLs (especially Arxiv), or direct text input, producing structured key points and detailed analysis reports covering research motivation, contributions, methodological innovations, experimental framework, and limitations. Output formats: PDF report, standalone HTML with dark mode (recommended for sharing), Markdown file (.md). Supports optional chart/figure extraction from PDF and configurable analysis depth. Use this skill whenever the user asks to analyze, summarize, review, or deconstruct a paper; provides a local PDF path, an Arxiv URL, or any research article link; or needs structured paper insights for literature browsing, quality assessment, or building personal research directions.
---

# Paper Analyzer

## Purpose

Transform a research paper (PDF / URL / text) into a structured analytical report that reveals its research motivation, problem definition, methodological innovation, evidence logic, experimental framework, and limitations. Designed to help users rapidly understand new literature, evaluate paper quality, and build their own research by learning from existing work.

## Core Principle

Every paper tells a story. The goal is not to re-list sections, but to reconstruct the paper's **argument spine**:

1. What problem does the paper address?
2. Why does this problem matter?
3. What gap or bottleneck exists?
4. What did the authors do (method/core idea)?
5. How did they verify it (experimental evidence)?
6. What are the results and how strong is the evidence?
7. What are the boundaries, limitations, and future directions?
8. What can I learn for my own research?

## Skill Dependencies

This skill **requires** the following dependency skills to be installed and available:

### Hard Dependency: `pdf` skill
- **Purpose**: PDF text extraction, metadata extraction, image extraction, OCR
- **Invocation**: Load the `pdf` skill using `skill` tool before any PDF processing
- **Test**: Verify `pdf` skill is available before proceeding; if not found, inform user to install it first

### Tool Dependencies
| Tool | Purpose | Source |
|------|---------|--------|
| `skill` tool | Load dependency skills | Built-in |
| `webfetch` tool | Fetch web page content | Built-in |
| `websearch` tool | Search for papers when direct access fails | Built-in |

## Input Handling

### Accepted Inputs
- **Local PDF path** — extract full text + optional figure extraction (via `pdf` skill)
- **Arxiv URL** — fetch abstract metadata + download PDF for full analysis
- **General web URL** — fetch article content (when PDF not available)
- **Direct text** — user-pasted article text or notes

### PDF Processing — Chain of Invocation

**Step 1: Load the `pdf` skill**
```tool
skill: pdf
```
This loads the `pdf` skill's instructions into context, making its PDF processing methods available.

**Step 2: Select extraction method based on PDF condition**
Using the `pdf` skill's guidance (loaded above), in this priority order:

| Priority | Method (from `pdf` skill) | When to use | Fallback trigger |
|----------|--------------------------|-------------|------------------|
| 1st | pdfplumber `page.extract_text()` | Normally selectable PDF | If import fails → try 2nd |
| 2nd | pypdf `PdfReader().pages[i].extract_text()` | When pdfplumber unavailable | If import/read fails → try 3rd |
| 3rd | OCR (pytesseract + pdf2image) | Scanned PDF (no selectable text) | If not installed → try 4th |
| 4th | Web fallback: search paper title on web | All local methods fail (corrupted PDF, no tools) | — |

**Step 3: Handle extraction failures**

If the `pdf` skill's tools are not installed (import errors):
1. Follow the `pdf` skill's own installation instructions to install required packages
2. If installation fails (e.g., network restrictions), use **Web Fallback**:
   - For Arxiv URLs: use `webfetch` on arxiv HTML version (ar5iv)
   - For known paper titles: use `websearch` to find the paper on open-access repositories
   - Report the fallback to the user

**Important**: Do NOT attempt to bypass the `pdf` skill by writing custom PDF parsing code. The `pdf` skill is the sole PDF processing pipeline for this skill.

### Figure/Chart Extraction (optional)

When the user requests figure extraction or specifies `--extract-figures`:
1. Load the `pdf` skill (same as Step 1 above)
2. Following the `pdf` skill's image extraction instructions (PyMuPDF's `get_page_images` or pdfimages CLI tool), extract embedded images per page
3. Extract figure captions from surrounding text
4. Save figures as PNG/JPEG alongside the analysis report
5. Associate each figure with its context (which section, what it shows)

## Analysis Framework

The skill analyzes papers along the following dimensions. **All dimensions are active by default**; the user can specify which to include or exclude via `--include=<dim1,dim2>` or `--exclude=<dim3,dim4>`.

| Dimension | Description |
|-----------|-------------|
| **Metadata** | Title, authors, venue, year, DOI, arxiv ID |
| **Research Motivation** | Why does the problem matter? Real-world/academic background |
| **Problem Definition** | What specific gap, bottleneck, or limitation is addressed? |
| **Core Contributions** | What does the paper claim as new? |
| **Methodological Innovation** | What is novel in the approach? New architecture, algorithm, framework, theory? |
| **Theoretical Framework** | What theories, assumptions, or formalisms underpin the work? |
| **Experimental Framework** | Organized by **experiment → question → conclusion** (see below) |
| **Key Results** | Quantitative and qualitative findings |
| **Limitations** | Acknowledged or identifiable weaknesses |
| **Future Work** | Suggested or implied next steps |
| **Quality Assessment** | How well does evidence support claims? Is the paper sound? |

### Experimental Framework Detail

The experimental framework section should be organized as a **question-answering map** — each experiment is presented as:

```
Experiment [Name/Setting]:
  • What it did: [brief description]
  • Question it answers: [what specific claim or design choice is being tested?]
  • How it was run: [datasets, baselines, metrics, setup]
  • What it found: [key numerical or qualitative result]
  • What it concludes: [what claim is validated or refuted?]
  • Evidence strength: [strong / moderate / weak — based on thoroughness]
```

Common experiment types to identify:
- **Main (core) experiment**: validates the primary contribution against baselines
- **Ablation study**: tests contribution of individual components
- **Qualitative analysis**: case studies, visualizations, examples
- **Robustness/generalization**: cross-domain, cross-dataset, parameter sensitivity
- **Efficiency analysis**: runtime, memory, parameter count
- **Statistical testing**: confidence intervals, significance tests

## Output Modes

### 1. Quick Scan (`--mode=quick`)
A dense bullet-point summary, one line per dimension. Ideal for rapid browsing.

### 2. Standard Analysis (`--mode=standard`) [Default]
Each dimension gets a paragraph-level explanation plus supporting evidence. Figures are referenced inline if extracted.

### 3. Deep Analysis (`--mode=deep`)
Full narrative for each dimension with critical evaluation. Includes:
- Comparison with related work context
- Evidence strength assessment (strong/moderate/weak per claim)
- Cross-experiment consistency check
- Quality assessment with explicit reasoning
- Connection to broader research landscape

Sections can be mixed — e.g., deep analysis for methods and experiments, quick scan for metadata and limitations.

## Analysis Quality Standards

Each analysis dimension must follow specific quality criteria. These standards ensure consistency, completeness, and traceability across all analyses.

### 📄 Metadata
- **Format**: Title, full author list, affiliations, venue/year, DOI/arxiv ID, code link (if available)
- **Standard**: Always include full author list when accessible; venue with full name + year

### 🎯 Research Motivation
- **Quality requirement**: Present the **full argument chain** from the original paper, not an oversimplified version
- **Must include**:
  - The real-world or academic background establishing the problem's importance
  - Why existing approaches are insufficient (specific limitations)
  - The paper's **key insight** or intuition (what makes them think their approach will work)
- **Forbidden**: Oversimplifying to a single sentence where the original uses multiple linked arguments
- **Traceability**: Use direct quotes for the paper's central claims about the problem, but embed them in explanatory narrative rather than listing in isolation

### 🔍 Problem Definition
- **Quality requirement**: Keep information **complete** — more words do not hurt analysis
- **Structure** (recommended):
  - **Core contradiction**: the central tension the paper addresses
  - **Existing limitations**: what prior work fails at, organized by aspect
  - **Key challenges**: specific technical obstacles that must be overcome (each with a traceable mapping to original text)
- **Traceability**: Each key challenge must be explicitly mappable to the original paper (cite relevant phrases or sections)
- **Forbidden**: Compressing a multi-faceted problem statement into a single bullet point

### 🏆 Core Contributions
- **Quality requirement**: Preserve the **original wording** of claimed contributions; do not rephrase so aggressively that the original meaning is lost
- **Format**: Numbered list, each contribution with:
  - Direct quote from the paper (paper's own claim)
  - Inline evidence reference (which experiments/analyses support this claim)
- **Forbidden**: Paraphrasing so aggressively that the contribution scope changes

### ⚙️ Methodological Innovation
- **Quality requirement**: This is the **most critical section** — do NOT omit subtle design details that could be sources of inspiration
- **Must include** for each module/component:
  - **Design motivation**: what problem does this module solve?
  - **Technical details**: the actual mechanism (prefer keeping formulas if they carry meaning)
  - **Design choices & rationale**: why this specific design over alternatives
  - **Novelty positioning**: what is new compared to prior work
  - **Implementation nuance**: learnable parameters, edge case handling (e.g., blank tokens for textureless regions)
- **Structure**: Organize by functional modules, not by paper section order
- **Forbidden**: Omitting a module because "it's too detailed" — details ARE the point

### 🧪 Experimental Framework
- **Quality requirement**: Each experiment must be described at **two levels** — narrative + structured summary
- **Format per experiment**:
  ```
  1. Paragraph: "做了什么" (what was done, how it was set up, datasets, metrics)
  2. Table: quick reference summary
  3. Question mapping: what specific claim does this experiment validate?
  4. Evidence strength assessment
  ```
- **Must include** (universal checklist — adapt to the field):
  - **Dataset / data source**: name, scale, domain
  - **Baselines / control conditions**: what methods or settings are compared
  - **Task & evaluation metrics**: what is being measured, with what metric
  - **Key numerical results**: the main quantitative findings
  - **Implementation / setup details**: parameters needed to understand how the experiment was conducted
    (e.g., hyperparameters, iterations, model size, preprocessing, training cost, hardware if relevant)
  - **Inference / test procedure**: how the trained model or method is deployed at test time
- **Flowchart**: Include an experimental framework overview diagram showing:
  - All experiments and their relationships
  - What each experiment validates (which contribution/claim)
  - Model size variations, task types, and control variables (ablations, hyperparameters)
- **Forbidden**: Only a table without prose; only prose without structured comparison

### 📊 Key Results
- **Quality requirement**: Summarize the most important numbers across all experiments
- **Structure**: Organized by task (classification → segmentation → instance), then by model size
- Include cross-scale comparisons (small model vs large baseline) where available

### ⚠️ Limitations
- **Format**: Table with three columns: limitation, acknowledged by authors (yes/partial/no), severity (critical/moderate/minor)
- **Forbidden**: Only listing paper-acknowledged limitations; include identifiable ones too
- **Tone**: Critical but fair — no strawman arguments

### 🔭 Future Work
- **Format**: Three categories — explicitly suggested, implied but not stated, potential extension for your own research

### 📋 Quality Assessment
- **Format**: Strengths (→), Weaknesses (→), Overall soundness, Reproducibility, Significance
- **Tone**: Evidence-based judgment, not opinion

### General Rules
1. **Fidelity over brevity**: If choosing between being concise and being faithful to the original, choose faithfulness
2. **Traceability**: Claims about the paper should be traceable to specific sections or quotes
3. **No forced compression**: Using many words is acceptable if it improves understanding
4. **Default language**: Chinese (Simplified) for Chinese-speaking users; preserve technical terms (model names, dataset names, metrics, equations) in English

### 📝 Text Generation Conventions
- **Punctuation**: In Chinese output, use Chinese colon "：" instead of em dash "——" for separating labels from descriptions (e.g., "挑战一：语义差异" not "挑战一——语义差异"). This applies to all nested labels in paragraphs and bullet points.
- **Terminology**: Preserve ALL English technical terms (model names, dataset names, metrics, equations, code symbols) in their original form regardless of output language
- **Formatting**: Use consistent Markdown heading hierarchy (## for dimensions, ### for subsections, #### for experiments)

Users may control the analysis via command modifiers:

| Modifier | Effect |
|----------|--------|
| `--mode=quick\|standard\|deep` | Set overall depth |
| `--include=motivation,contributions,methods,experiments` | Only these dimensions |
| `--exclude=metadata,limitations,future` | Skip these dimensions |
| `--extract-figures` | Enable image extraction from PDF |
| `--output=md\|json\|pdf\|html` | Output format |

If the user says "不需要某一部分" or "skip X", treat that as `--exclude=X`.

## Interactive User Prompt — MANDATORY

After receiving the user's paper input (PDF path / URL / text), you MUST call the `question` tool below **before** starting any extraction or analysis. Do NOT skip this step. Do NOT proceed without both choices made.

**Purpose**: Set both the output language and the output delivery format in a single step.

### Question Tool Call (EXECUTE THIS — do not treat as example)

```
question:
  - header: "Analysis Language"
    question: "请选择分析报告使用的语言 / Please select output language"
    options:
      - label: "中文 (Chinese)"
        description: "输出简体中文分析报告，保留英文专业术语"
      - label: "English"
        description: "Output analysis report in English"
      - label: "Other"
        description: "Specify a custom language (will be prompted)"
  - header: "Output Format"
    question: "请选择输出方式 / Choose output format"
    options:
      - label: "生成 PDF 报告"
        description: "保存为 PDF 文件并告知路径，包含完整分析 + 实验流程图"
      - label: "生成 HTML 网页报告"
        description: "保存为自包含 HTML 文件，含左侧导航目录、深色模式切换，适合浏览器阅读和分享"
      - label: "生成 MD 文件"
        description: "保存为 Markdown 源文件，方便后续编辑、版本对比或再次转换"
```

### Handling — Language

- `中文`: Set `[LANG=zh]`. ALL subsequent narrative text MUST be written in Chinese (Simplified). Technical terms (model names, dataset names, metrics, equations, code symbols) are preserved in English.
- `English`: Set `[LANG=en]`. ALL subsequent narrative text MUST be written in English.
- `Other`: Prompt the user to specify a custom language code, fall back gracefully if unsupported.

### Handling — Output Format

- `生成 PDF 报告`: Set `[OUTPUT=pdf]`. Run full analysis and generate a PDF report. Report the full file path.
- `生成 HTML 网页报告`: Set `[OUTPUT=html]`. Run full analysis and generate a standalone HTML file with left-sidebar TOC and dark mode toggle. Report the file path.
- `生成 MD 文件`: Set `[OUTPUT=md]`. Run full analysis and save the Markdown report to a file. Report the file path.

### Enforcement (MANDATORY)

1. After the user answers, record both choices as `[LANG=zh]` or `[LANG=en]` and `[OUTPUT=pdf]` or `[OUTPUT=md]` or `[OUTPUT=html]` at the start of the analysis.
2. EVERY narrative paragraph, header, bullet, and table cell MUST be written in `[LANG]`.
3. Both variables persist through the entire session. All output (MD / PDF / HTML) MUST respect both `[LANG]` and `[OUTPUT]`.

## Workflow — Complete Chain

```
0. Dependency Check
   └── Load `pdf` skill via `skill` tool
       ├── If available: proceed
       └── If not: inform user to install `pdf` skill, STOP

1. Input Reception
   ├── Identify input type (PDF path / URL / text)
   ├── If URL: determine if Arxiv (use arxiv API) or general (use `webfetch`)
   └── If PDF: validate path exists

--- [Combined Interactive Prompt: Language + Output Format] ---
--- [MANDATORY: Record `[LANG=zh]` or `[LANG=en]` and `[OUTPUT=pdf]` or `[OUTPUT=md]` or `[OUTPUT=html]` as visible variables] ---
   (Language determines ALL narrative text; Output determines delivery strategy. Both set before any computation.)

2. Content Extraction
   ├── If PDF:
   │   ├── Step 1: Load `pdf` skill → get its text extraction methods
   │   ├── Step 2: Try pdfplumber (from `pdf` skill) for text extraction
   │   │   ├── Success → extract metadata, tables, figures
   │   │   ├── ImportError → try pypdf method (from `pdf` skill)
   │   │   └── No text found → try OCR method (from `pdf` skill)
   │   └── Step 3: If ALL PDF methods fail → Web Fallback:
   │       ├── Has URL? → use `webfetch` to get HTML/text version
   │       ├── Has title? → `websearch` for paper → `webfetch` content
   │       └── Report fallback to user
   ├── If URL (non-PDF): use `webfetch` to retrieve content
   └── If direct text: use as-is

3. Structured Analysis
   ├── Apply analysis framework dimensions in `[LANG]`
   ├── Identify experiment → question → conclusion map
   ├── Assess evidence strength
   ├── Respect user's include/exclude and depth settings
    └── [LANGUAGE VERIFICATION] Before proceeding, scan ALL sections written so far:
        ├── Every narrative paragraph is in `[LANG]` (NOT the other language)
        ├── Technical terms (model names, datasets, metrics, equations) remain in English
        └── If any violation found → rewrite the offending section before continuing
    └── [QUALITY STANDARDS VERIFICATION] MANDATORY — check before output:
        ├── For each dimension in the analysis:
        │   ├── Read the dimension's quality requirements in "Analysis Quality Standards" above
        │   ├── Verify your analysis_data matches EVERY listed requirement
        │   │   ├── Research Motivation: full argument chain + direct quotes? (not compressed)
        │   │   ├── Problem Definition: core contradiction + existing limitations + key challenges + traceability?
        │   │   ├── Core Contributions: original wording + evidence_ref per item?
        │   │   ├── Methodological Innovation: design motivation + technical details + design choices + novelty + nuance?
        │   │   ├── Experimental Framework: narrative + structured + question mapping per experiment?
        │   │   │   └── Completeness checklist:
        │   │   │       ├── Dataset / data source (name, scale, domain)?
        │   │   │       ├── Baselines / control conditions listed?
        │   │   │       ├── Task & metrics defined?
        │   │   │       ├── Key numerical results reported?
        │   │   │       ├── Implementation / setup details sufficient?
        │   │   │       └── If any missing → rewrite the experiment before proceeding
        │   │   ├── Limitations: table with acknowledged + severity columns? unacknowledged ones included?
        │   │   ├── Future Work: three categories (explicit/implicit/potential)?
        │   │   └── Quality Assessment: Strengths/Weaknesses/Soundness/Reproducibility/Significance?
        │   └── If ANY requirement is unmet → rewrite the dimension before proceeding
        └── THIS IS NOT OPTIONAL — any violation is a bug

 4. Output Generation
    ├── Write the full analysis as a single Markdown string (in `[LANG]`) with YAML frontmatter for metadata (title, authors, affiliations, venue, code)
    ├── If `[OUTPUT=md]`:
    │   ├── Create `analysis_result/` directory under project root (if not exists)
    │   ├── Write the Markdown string directly to `analysis_result/{PaperTitle}_analysis.md`
    │   └── Report full file path to user
    ├── If `[OUTPUT=pdf]`:
    │   ├── Create `analysis_result/` directory under project root (if not exists)
    │   ├── Write the Markdown string to a temp file `analysis_result/{PaperTitle}_analysis.md`
    │   ├── Convert Markdown to analysis_data dict using `md_to_report(md_text)` from `scripts/md_to_report.py`
    │   │   ├── This handles YAML frontmatter → metadata, `##` → sections, `###` → subsections,
    │   │   │   `-` → bullets, `|...|` → tables, `**Experiment:**` → experiments, `1. **"..."**` → contributions
    │   │   └── Limitation tables and quality assessment bullets are auto-detected
    │   ├── Generate PDF via `build_pdf(analysis_data, ..., lang=[LANG])` using `scripts/generate_report.py`
    │   │   └── The PDF typography standard from "PDF Generation Standards" section is applied (fonts, sizes, line spacing, margins per `[LANG]`)
    │   ├── Save PDF to `analysis_result/{PaperTitle}_Analysis_Report.pdf`
    │   ├── [CLEANUP] Delete the intermediate `.md` temp file
    │   └── Report full file path to user
    ├── If `[OUTPUT=json]`:
    │   ├── Parse Markdown via `md_to_report(md_text)`
    │   └── Save to `analysis_result/{PaperTitle}_analysis.json`
    ├── If `[OUTPUT=html]`:
    │   ├── Create `analysis_result/` directory under project root (if not exists)
    │   ├── Save the Markdown string to `analysis_result/{PaperTitle}_analysis.md` (permanent)
    │   ├── Convert Markdown to analysis_data dict via `md_to_report(md_text)` (same pipeline as PDF)
    │   ├── Generate HTML via `render_html(analysis_data, lang=[LANG])` from `scripts/generate_report.py`
    │   │   └── The HTML uses fixed embedded CSS (left-sidebar TOC, dark mode toggle, responsive layout) — no external dependencies
    │   ├── Save HTML to `analysis_result/{PaperTitle}_Analysis_Report.html`
    │   └── Report both file paths to user (`.md` and `.html`)
    └── Include extracted figures if --extract-figures was specified
```

## Dependency Summary

| Dependency | Type | How to Invoke | Purpose |
|-----------|------|--------------|---------|
| `pdf` skill | **Hard** | `skill: pdf` | PDF text/metadata/image extraction |
| `webfetch` tool | Hard | Built-in tool | Fetch URLs, HTML content |
| `websearch` tool | Soft (fallback) | Built-in tool | Search for paper when direct access fails |
| `reportlab` | Hard | `pip install reportlab` | PDF generation |
| `mistune` | Soft | `pip install mistune` | Markdown parsing (installed by default on most systems) |

**Rule**: Do NOT bypass the `pdf` skill by calling its underlying libraries directly (e.g., do NOT call pdfplumber/PyMuPDF unless the `pdf` skill's instructions direct you to). Always load the `pdf` skill first and follow its instructions.

No dependency on nature-* or omr-* skills. This skill is a standalone entry point.

## Output Example Structure

```markdown
---
title: Paper Title
authors: Author Names
affiliations: Institution Name
code: https://github.com/...
---

## Metadata
- Title: ...
- Authors: ...
- Venue/Year: ...
- DOI: ...

## Research Motivation
{Full argument chain paragraph(s)}

## Problem Definition
{Core contradiction, existing limitations, key challenges}

## Core Contributions
1. **"Exact quote from paper stating contribution 1"**
Evidence: Supported by experiments X and Y.

2. **"Exact quote from paper stating contribution 2"**
Evidence: See ablation study in Section Z.

## Methodological Innovation
{Detailed explanation by functional modules}

## Experimental Framework
### Experiment 1: [Name]
{Paragraph narrative}

**What it did:** {brief description}
**Question it answers:** {specific claim tested}
**Setup:** {datasets, baselines, metrics}
**Results:** {key findings}
**Conclusion:** {what claim is validated?}
**Evidence strength:** strong / moderate / weak

## Key Findings
{Main results organized by task}

## Limitations
{Paragraph introduction}

| Limitation | Acknowledged | Severity |
|------------|-------------|----------|
| First limitation | Yes | Minor |
| Second limitation | No | Moderate |

## Future Work
{Three categories: explicit, implicit, potential}

## Quality Assessment
- Strengths: {aspects done well}
- Weaknesses: {aspects lacking}
- Overall Soundness: {high / moderate / low}
- Reproducibility: {high / moderate / low}
- Significance: {high / moderate / low}
```

## PDF Generation Standards

### Typography

| Parameter | Language=zh | Language=en |
|-----------|-------------|-------------|
| Body font | SimSun (宋体) | Times New Roman |
| Body size / line spacing | 12pt / 20pt fixed | 12pt / 1.5x |
| Section title font (一级) | SimHei (黑体) 16pt | Times New Roman Bold 16pt |
| Subsection title font (二级) | SimHei (黑体) 14pt | Times New Roman Bold 14pt |
| Page margins | top/bottom 2.54cm, left/right 3.17cm | 25mm uniform |
| Cover page | Keep unchanged | Keep unchanged |

### Post-generation Cleanup

After PDF generation succeeds, delete any intermediate script files (e.g., inline Python scripts written to the output directory) that were created solely for the generation process. Only the final PDF should remain in the output directory.

## Key Principles

1. **Use canonical section titles**. The parser matches sections by schema-defined titles (see `schema/analysis_schema.json`). Always use the exact titles: `Metadata`, `Research Motivation`, `Problem Definition`, `Core Contributions`, `Methodological Innovation`, `Experimental Framework`, `Key Findings`, `Limitations`, `Future Work`, `Quality Assessment`. Chinese equivalents are also accepted.
2. **Follow the schema format for each dimension**. The schema defines exact field requirements: contributions use `1. **"quote"**` + `Evidence:` format, limitations use a 3-column markdown table, quality uses labeled bullets.
3. **Do not copy paper section order**. Reorganize around the argument spine.
4. **Every experiment must answer a question**. If unclear, flag it.
5. **Evidence strength matters**. Distinguish what the paper proves vs. merely suggests.
6. **Respect user exclusions**. If user says skip a dimension, skip it completely.
7. **Be critical but fair**. Identify limitations without strawman arguments.
8. **Language compliance is MANDATORY**. After the language prompt, `[LANG]` is explicitly set. ALL output MUST be in `[LANG]`. Technical terms are always preserved in English.

## Future Extensibility

The output of paper-analyzer is designed to feed naturally into downstream skills:
- `nature-paper2ppt` — use analysis as slide content
- `omr-evidence` — extract claims for evidence mapping
- `omr-synthesis` — aggregate multiple analyses for survey writing

These are purely optional; the skill is complete on its own.
