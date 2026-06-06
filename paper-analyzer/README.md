**This is a literature reading skill that can quickly help you understand the main content of the literature.**



# Paper Analyzer — Scientific Paper Analysis Skill

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
| `--output=markdown\|json` | Output format (default: markdown) |

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
## Metadata
- Title: Attention Is All You Need
- Authors: Vaswani et al.
- Venue/Year: NeurIPS 2017
- DOI: ...

## Research Motivation
Recurrent models are sequential by nature, preventing parallelization and causing memory constraints with long sequences.

## Problem Definition
Can we design a sequence transduction model that relies entirely on attention mechanisms, eliminating recurrence and convolution?

## Core Contributions
- Propose the Transformer architecture based solely on attention
- Introduce multi-head self-attention and positional encodings
- Achieve SOTA translation quality with significantly less training time

## Experimental Framework
### Experiment 1: Machine Translation (WMT 2014)
- **What it did**: Transformer vs. existing SOTA models on EN-DE and EN-FR translation
- **Question it answers**: Does the Transformer match or exceed recurrent/convolutional models?
- **Setup**: WMT 2014 EN-DE, WMT 2014 EN-FR, BLEU score
- **Results**: 28.4 BLEU (EN-DE), 41.8 BLEU (EN-FR) — new SOTA
- **Conclusion**: The Transformer outperforms all baselines while requiring less training time
- **Evidence strength**: strong
...
```

## Dependencies

| Dependency | Type | How to Invoke | Purpose |
|-----------|------|--------------|---------|
| `pdf` skill | **Hard** | `skill: pdf` | PDF text/metadata/image extraction |
| `webfetch` tool | Hard | Built-in tool | Fetch URLs, HTML content |
| `websearch` tool | Soft (fallback) | Built-in tool | Paper search when direct access fails |

**Critical rule**: To ensure portability across projects and devices, PDF processing must go through the `pdf` skill. Do NOT call PDF libraries directly — always load the `pdf` skill first and follow its instructions. This guarantees the skill works correctly regardless of environment.

The skill is intentionally **standalone** — no dependency on nature-* or omr-* skills. It can feed into them later if desired.

## Roadmap

- [ ] **Basic paper analysis** (current)
- [x] Quick / Standard / Deep output modes
- [x] Dimension include/exclude control
- [x] Figure extraction from PDF
- [ ] **Batch analysis** — analyze multiple papers in one session
- [ ] **Comparison mode** — compare two papers side by side
- [ ] **Export formats** — JSON for downstream pipelining
- [ ] **Arxiv auto-suggest** — find related papers from analysis context
- [ ] **Multi-language support** — analyze papers in Chinese, Japanese, etc.

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
