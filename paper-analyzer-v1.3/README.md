**This is a literature reading skill that can quickly help you understand the main content of the literature.**



# Paper Analyzer — Scientific Paper Analysis Skill

> **Version: V1.3** — *Quality Gates + Evidence Visualization + Sub-agent + Parser Robustness* | [Changelog](#changelog) | [V1.2](#v12-2026-06-07--html-output--multi-level-bullets--bug-fixes) | [V1.1](#v11-2025-06-06--design-overhaul--bug-fixes) | [V1.0](#v10--initial-release)

Paper Analyzer is an [opencode](https://opencode.ai) skill that transforms academic papers into structured analytical reports. It reads papers from **local PDFs**, **Arxiv URLs**, or **web links**, and produces a reasoned analysis covering research motivation, contributions, methodological innovation, experimental framework, limitations, and more.

## Why Paper Analyzer?

Researchers spend huge amounts of time reading, digesting, and evaluating papers. This skill automates the **analysis phase** — not by generating vague summaries, but by reconstructing the paper's **argument spine**: what problem it solves, why it matters, how it proves it, and where it falls short.

It is designed to help you:
- **Rapidly browse** new literature (quick mode)
- **Evaluate paper quality** with evidence-aware critique (deep mode)
- **Build your own research** by systematically learning from existing work

## Features

- **Multiple input channels**: local PDF, Arxiv URL, general web URL, direct text
- **11 analysis dimensions**: metadata, motivation, problem definition, contributions, methodological innovation, theoretical framework, experimental framework, key results, limitations, future work, quality assessment
- **Experiment → Question → Conclusion mapping**: each experiment is analyzed by what claim it tests, what it found, and how strong the evidence is
- **Three output modes**: Quick (dense bullet), Standard (paragraphs), Deep (narrative with critical evaluation)
- **Configurable depth**: mix and match — e.g., deep analysis on methods, quick scan on limitations
- **Figure extraction** (optional): extract embedded images from PDF alongside analysis
- **Dimension control**: include or exclude any analysis dimension on demand
- **Standalone**: minimal dependencies, no heavy framework requirements
- **Multi-format output**: PDF report, standalone HTML with dark mode and sidebar TOC, Markdown file, structured JSON

## Installation

### Prerequisites

- [opencode](https://opencode.ai) with skill system enabled
- The [pdf](https://github.com/anomalyco/opencode/tree/main/skills/pdf) skill (for PDF text/figure extraction)

### Install

Place the `paper-analyzer` folder in your opencode skills directory:

```bash
# In your project or opencode config directory
cp -r paper-analyzer .opencode/skills/
```

Or clone and symlink:

```bash
git clone https://github.com/your-username/paper-analyzer.git
ln -s $(pwd)/paper-analyzer .opencode/skills/paper-analyzer
```

## Usage

Trigger the skill by asking to analyze or summarize a paper:

```
> 帮我分析这篇论文 E:\papers\transformer.pdf
> analyze this paper https://arxiv.org/abs/2305.12345
> summarize https://openreview.net/forum?id=xxxxx
> deep分析，提取图表
```

### Configuration Modifiers

| Modifier | Effect |
|----------|--------|
| `--mode=quick\|standard\|deep` | Set analysis depth |
| `--include=motivation,contributions,methods,experiments` | Only these dimensions |
| `--exclude=metadata,limitations,future` | Skip these dimensions |
| `--extract-figures` | Extract images from PDF |
| `--output=md\|html\|pdf\|json` | Output format (default: pdf) |

Examples:

```
# Quick scan, skip limitations
--mode=quick --exclude=limitations

# Deep analysis focusing on method and experiments, with figures
--mode=deep --include=methods,experiments --extract-figures
```

## Analysis Framework

### The 11 Dimensions

| Dimension | What It Captures |
|-----------|------------------|
| Metadata | Title, authors, venue, year, DOI, arxiv ID |
| Research Motivation | Why does the problem matter? Real-world or academic background |
| Problem Definition | What specific gap, bottleneck, or limitation is addressed? |
| Core Contributions | What does the paper claim as new? |
| Methodological Innovation | What is novel — new architecture, algorithm, framework, or theory? |
| Theoretical Framework | What theories, assumptions, or formalisms underpin the work? |
| Experimental Framework | Each experiment mapped to: what it did → question it answers → what it found → conclusion → evidence strength |
| Key Results | Quantitative and qualitative findings |
| Limitations | Acknowledged or identifiable weaknesses |
| Future Work | Suggested or implied next steps |
| Quality Assessment | How well does evidence support claims? How sound is the paper? |

### Experimental Framework (Core Innovation)

Instead of a flat list of experiments, the skill organizes them as a **question-answering map**:

```
Experiment [Name]:
  • What it did: description
  • Question it answers: what claim or design choice is being tested?
  • Setup: datasets, baselines, metrics
  • Results: key findings
  • Conclusion: what is validated or refuted?
  • Evidence strength: strong / moderate / weak
```

This makes it immediately clear *what evidence exists for each claim* — and where it is lacking.

### Output Modes

| Mode | Use Case | Structure |
|------|----------|-----------|
| `quick` | Rapid browsing, literature triage | 1-2 lines per dimension, dense bullets |
| `standard` (default) | Daily reading, note-taking | Paragraph per dimension + structured lists |
| `deep` | Thorough evaluation, critical review | Full narrative per dimension with evidence assessment, cross-experiment consistency check, and quality critique |

## Output Example

```markdown
---
title: Attention Is All You Need
authors: Vaswani et al.
affiliations: Google Brain
---

## Metadata
- Title: Attention Is All You Need
- Authors: Vaswani et al.
- Venue/Year: NeurIPS 2017

## Research Motivation
Recurrent models are sequential by nature, preventing parallelization and causing memory constraints with long sequences.

## Problem Definition
Can we design a sequence transduction model that relies entirely on attention mechanisms, eliminating recurrence and convolution?

## Core Contributions
1. **"We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."**
Evidence: Main experiment on WMT 2014 showing 28.4 BLEU.

2. **"We introduce multi-head attention and positional encodings to capture both parallel processing and sequence order."**
Evidence: Ablation study on attention heads in Section 4.

## Experimental Framework
### Experiment 1: Machine Translation (WMT 2014)
{Paragraph narrative: what was done, how, with what setup}

**What it did:** Compared Transformer vs. existing SOTA on EN-DE and EN-FR
**Question it answers:** Does Transformer match/exceed recurrent/convolutional models?
**Setup:** WMT 2014 EN-DE, WMT 2014 EN-FR, BLEU, single NVIDIA P100
**Results:** 28.4 BLEU (EN-DE), 41.8 BLEU (EN-FR)
**Conclusion:** Transformer outperforms all baselines with less training time
**Evidence strength:** strong

## Limitations
| Limitation | Acknowledged | Severity |
|------------|-------------|----------|
| Autoregressive decoding still sequential | Yes | Minor |

## Quality Assessment
- Strengths: Novel architecture, strong empirical results, clear presentation
- Weaknesses: Limited to translation; positional encoding alternatives not explored
- Overall Soundness: High
- Reproducibility: High (open-source code, detailed hyperparameters)
- Significance: High (foundational work, 100k+ citations)
```

## Dependencies

### Skill & Tool Dependencies

| Dependency | Type | How to Invoke | Purpose |
|-----------|------|--------------|---------|
| `pdf` skill | **Hard** | `skill: pdf` | PDF text/metadata/image extraction |
| `webfetch` tool | Hard | Built-in tool | Fetch URLs, HTML content |
| `websearch` tool | Soft (fallback) | Built-in tool | Paper search when direct access fails |

**Critical rule**: To ensure portability across projects and devices, PDF processing must go through the `pdf` skill. Do NOT call PDF libraries directly — always load the `pdf` skill first and follow its instructions. This guarantees the skill works correctly regardless of environment.

The skill is intentionally **standalone** — no dependency on nature-* or omr-* skills. It can feed into them later if desired.

### Python Library Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| `reportlab` | PDF generation | `pip install reportlab` |
| `mistune` | Markdown parsing (optional) | `pip install mistune` (usually pre-installed) |
| `pdfplumber` | PDF text extraction | `pip install pdfplumber` (via `pdf` skill) |

## Roadmap

- [x] Quick / Standard / Deep output modes
- [x] Dimension include/exclude control
- [x] Figure extraction from PDF
- [x] Schema-driven type mapping (V1.1: section titles define data types, no guessing)
- [x] Unified multi-output renderers (console / PDF / JSON)
- [x] JSON export for downstream pipelining (e.g., omr-evidence, omr-synthesis)
- [x] Multi-format output: Markdown file / standalone HTML with dark mode / PDF / JSON (V1.2)
- [x] Nested bullet support in HTML, PDF, and console rendering (V1.2)
- [x] Unicode dash (– —) bullet detection (V1.2)
- [x] Gate-based quality checks — A (content completeness), B (language), C (experiment fields) (V1.3)
- [x] Evidence strength visualization — colored badges (green/yellow/red) in HTML output (V1.3)
- [x] Sub-agent definition (`agents/openai.yaml`) for external invocation (V1.3)
- [x] Experiment field accumulation — multi-line bullet content captured into field value with `\n` separator (V1.3)
- [x] Contribution evidence deduplication — look-ahead lines correctly skipped to avoid double-parsing (V1.3)
- [x] Quality assessment label cleanup — `**` markers stripped from label and text (V1.3)
- [x] Bilingual field label deduplication — per-key single label selected by `lang`, no more duplicated Chinese+English labels (V1.3)
- [ ] **Batch analysis** — analyze multiple papers in one session
- [ ] **Comparison mode** — compare two papers side by side
- [ ] **Arxiv auto-suggest** — find related papers from analysis context
- [ ] **Multi-language support** — analyze papers in Japanese, Korean, etc.
- [ ] **Experiment flowchart generation** — auto-generate experiment relationship diagrams

## Architecture (V1.3)

```
analysis_schema.json          ← Single source of truth
    │
    ├── SKILL.md              ← AI reads this to produce correct Markdown
    │
    ├── agents/
    │   └── openai.yaml       ← Sub-agent definition for external invocation
    │
    └── scripts/
    ├── md_to_report.py   ← Schema-driven parser (title → type mapping)
    │                       (V1.2: Unicode dash detection, level tracking;
    │                        V1.3: experiment field accumulation, evidence dedup, QA cleanup)
    └── generate_report.py ← Unified renderers + gate checks
                                (V1.2: render_html(), nested bullets;
                                 V1.3: _gate_check(), evidence badges,
                                       bilingual field dedup, \\n → <br/>)
```

The schema defines which section titles map to which data types. The parser uses this mapping instead of guessing. This means:

- Any section titled "Limitations" gets parsed as a limitation table (3-column format)
- Any section titled "Quality Assessment" gets parsed as labeled bullets (Strengths/Weaknesses/etc.)
- Any section titled "Core Contributions" gets parsed for `1. **"quote"**` format
- No more `_detect_limitation_table()` keyword guessing — the title IS the type annotation

## Changelog

### V1.3 (2026-06-09) — Quality Gates + Evidence Visualization + Sub-agent + Parser Robustness

**New Features:**
- **Gate-based quality checks**: `_gate_check()` runs before every `build_report()` call — Gate A checks section content completeness (no empty sections), Gate B enforces language compliance, Gate C validates every experiment has `question` + `conclusion` + `evidence`. Failure blocks output and reports exact errors.
- **Evidence strength visualization**: HTML output renders evidence badges with color coding — green (`strong`), yellow (`moderate`), red (`weak`) — using pill-shaped CSS badges with light/dark theme support.
- **Sub-agent definition**: `agents/openai.yaml` added, enabling external skills to invoke paper-analyzer via `$paper-analyzer` with automatic context isolation.

**Bug Fixes:**
| # | File | Bug | Impact |
|---|------|-----|--------|
| 1 | `md_to_report.py` | Experiment fields (`**结果:**`, `**实验设置:**`) with bullet sub-lists only captured inline text; subsequent bullet lines silently routed to section-level bullets, breaking experiment-card display | Experiment data fragmentation in HTML output |
| 2 | `md_to_report.py` | Quality assessment labels with `**优势:**` (colon inside bold) split on `:` left `**` in both label and text, exposing raw bold markers | Visible `**` in rendered HTML |
| 3 | `md_to_report.py` | Contribution evidence look-ahead loop read and extracted evidence, but main loop index `i` was not advanced, causing evidence lines to be re-parsed as section paragraphs | Duplicate evidence text in output |
| 4 | `generate_report.py` | Experiment field rendering used flat `[(en_label, key), (zh_label, key)]` list, outputting both English and Chinese labels for the same field value per experiment | Duplicate bilingual labels in HTML output |

**Files Changed:**
| File | Change |
|------|--------|
| `scripts/generate_report.py` | Added `GateCheckError`, `_gate_check()` function, evidence badge CSS + rendering; integrated gate check into `build_report()` |
| `scripts/generate_report.py` | Experiment field labels changed from flat bilingual-list to `{key: (en, zh)}` dict with single label selected by `lang`; field values `\n` → `<br/>` for multi-line display |
| `scripts/md_to_report.py` | Added post-field-accumulation loop to collect bullet/paragraph content into experiment field values; advanced `i` past consumed evidence lines in contribution handler; stripped `**` from quality label and leading `**` from quality text |
| `SKILL.md` | Added Gate Check step (Mandatory) in Workflow between QA verification and Output Generation |
| `agents/openai.yaml` | New file — sub-agent definition for external invocation |

### V1.2 (2026-06-07) — HTML Output + Multi-level Bullets + Bug Fixes

**New Features:**
- **HTML output mode**: `build_report(md_text, output='html')` generates a standalone `.html` file with left-sidebar TOC, dark mode toggle, responsive layout — no external dependencies
- **Markdown file output**: `build_report(md_text, output='md')` saves the raw Markdown to a `.md` file for editing and version control
- **Multi-level bullet support**: bullets now track indentation level (2 spaces = 1 level) through the entire pipeline — Markdown → analysis_data → HTML/PDF/console; nested `<ul>` rendered in HTML, indentation in PDF and console
- **Unicode dash bullet detection**: `–` (en-dash) and `—` (em-dash) now recognized as valid bullet markers

**Bug Fixes:**
| # | File | Bug | Impact |
|---|------|-----|--------|
| 1 | `generate_report.py` | `_render_section_html` used `esc()` for table cells, leaving `**bold**` as literal `**` in HTML | Markdown formatting lost in table cells |
| 2 | `md_to_report.py` | `_is_bullet_line` only recognized ASCII `-`, `*`, `+`; Unicode `–` / `—` bullets silently dropped | Bullet data loss |
| 3 | `generate_report.py` | `_render_section_html` flat `<ul>` rendered all bullets at same level; no `str()` safety | Missing hierarchy, potential crash on non-string items |

**SKILL.md Updates:**
- Interactive prompt: added HTML and Markdown output options; removed console-only choice
- Experimental Framework: completeness checklist expanded from 4 vague items to 6 universal categories with `(universal checklist — adapt to the field)` guidance
- Interactive prompt format: replaced ` ```tool ` example block with rigid "MUST call" instruction to prevent model from skipping it
- Frontmatter description updated to list "PDF / HTML / Markdown" formats

### V1.1 (2025-06-06) — Design Overhaul + Bug Fixes

This version addresses fundamental design flaws discovered in V1.0 and fixes all known parser bugs.

**Design Changes (Schema-Driven Architecture):**
- Added `schema/analysis_schema.json` — single source of truth defining all 11 dimensions, data types, field schemas, and format hints. Both the AI agent and the parser reference this schema.
- Parser now uses **section title → schema type** mapping instead of keyword guessing. Titles like "Limitations" and "Quality Assessment" are explicit type annotations.
- Unified multi-output renderers: `render_console()` (formatted text), `render_pdf()` (unchanged), `render_json()` (new: structured JSON for downstream skills).
- New entry point `build_report(md_text, output='console|pdf|json', lang='zh|en', mode='quick|standard|deep')`.
- Split SKILL.md concerns: AI behavioral instructions vs. machine-readable schema vs. developer API docs.

**Bug Fixes (9 total):**
| # | File | Bug | Impact |
|---|------|-----|--------|
| 1 | `md_to_report.py` | `lstrip('-* ')` character-set bug corrupted text like `**bold**` → `*bold**` | Text corruption |
| 2 | `md_to_report.py` | Evidence lookup skipped bullet-format lines and didn't advance `i`, causing duplicate processing | Missing evidence data |
| 3 | `md_to_report.py` | Experiment field key_map only recognized English labels; Chinese labels silently dropped | Data loss in Chinese mode |
| 4 | `md_to_report.py` | Table separator regex failed on multi-column tables (`| --- | --- |`); `_adjust_col_widths` crashed on ragged rows; missing frontmatter `---` silently consumed entire document | Parsing crashes / data loss |
| 5 | `md_to_report.py` | `_detect_limitation_table` false-positive on any table with column "Severity" | Wrong table classification |
| 6 | `md_to_report.py` | `quality_buffer` save was nested inside `if bullet_buffer:` — lost when all bullets were quality items | Quality data silently dropped |
| 7 | `generate_report.py` | `TEMP_DIR` created at import time (module level); crashed on second `build_pdf()` call | Crashed on multi-call |
| 8 | `generate_report.py` | All font paths hardcoded to `C:\Windows\Fonts\` — non-functional on macOS/Linux | Cross-platform failure |
| 9 | `generate_report.py` | `HorizontalLine(170mm)` overflowed page margins; PDF filename collision silently overwrote files | Layout overflow / data loss |

**Template Fixes:**
- `templates/standard.md`: Limitations section changed from bullets to 3-column markdown table matching parser expectations
- `templates/standard.md`: Quality Assessment changed from single paragraph to labeled bullets
- `templates/deep.md`: Quality Assessment changed from `###` subsections to labeled bullets
- `templates/deep.md`: Contributions format changed from bullet list to numbered `1. **"quote"**` + `Evidence:` format

**Documentation Fixes:**
- `SKILL.md`: Output Example Structure rewritten to match actual parser expectations (contributions as `1. **"quote"**`, not bullets; full section title list; YAML frontmatter)
- `SKILL.md`: Added schema reference and canonical section title requirements in Key Principles
- `SKILL.md`: Added `reportlab` and `mistune` to Dependency Summary

### V1.0 — Initial Release
- 11-dimension analysis framework
- Quick / Standard / Deep output modes
- PDF text extraction via `pdf` skill
- Figure extraction from PDF
- Dimension include/exclude control
- `build_pdf()` entry point

## Contributing

This is an open, community-driven skill. Contributions of all kinds are welcome:

- **🐛 Bug reports**: Open an issue with the skill's behavior and expected output
- **💡 Feature suggestions**: Open an issue describing the feature and use case
- **🔧 Pull requests**: Improve `SKILL.md` logic, add templates, fix edge cases
- **📚 Templates**: Submit new analysis templates for different paper types (survey, system, empirical, theoretical, etc.)
- **🌐 Localization**: Help with multi-language trigger or output support

### Development Conventions

- Keep the skill **self-contained** — avoid adding new hard dependencies
- Follow the existing template structure in `templates/`
- Update `SKILL.md` if you change the analysis framework or configuration surface
- Test with at least one PDF and one Arxiv URL before submitting

### How to Extend

1. **Add a new analysis dimension**: Add it to the table in `SKILL.md` and update each template
2. **Create a new template**: Add a file in `templates/` and reference it in `SKILL.md`
3. **Add a configuration option**: Add it to the configuration table and handle it in the workflow logic

## License

MIT — free to use, modify, and share.

---

Built with opencode. Questions? Open an issue or start a discussion.
