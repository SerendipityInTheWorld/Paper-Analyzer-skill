**这是一个文献阅读技能，可以帮助您快速理解文献的主要内容。**

# Paper Analyzer — 科学论文分析技能

> **版本: V1.3** — *质量门禁 + Evidence 可视化 + 子代理 + 解析器健壮性* | [更新日志](#更新日志) | [V1.2](#v12-2026-06-07--html-输出--多层级列点--bug-修复) | [V1.1](#v11-2025-06-06--架构重构--bug-修复) | [V1.0](#v10--初始版本)

Paper Analyzer 是一个 [opencode](https://opencode.ai) 技能，能够将学术论文转换为结构化的分析报告。它支持从**本地 PDF**、**Arxiv 链接**或**网页链接**读取论文，并生成涵盖研究动机、贡献、方法创新、实验框架、局限性等多个维度的深入分析。

## 为什么选择 Paper Analyzer？

研究人员花费大量时间阅读、消化和评估论文。本技能自动化了**分析阶段**——不是生成模糊的摘要，而是重建论文的**论证主线**：它解决了什么问题、为什么重要、如何证明、以及哪里存在不足。

它旨在帮助您：
- **快速浏览**新文献（快速模式）
- **评估论文质量**，带有基于证据的评判（深度模式）
- **构建自己的研究**，通过系统性地学习现有工作

## 功能特性

- **多输入通道**：本地 PDF、Arxiv URL、通用网页 URL、直接文本输入
- **11 个分析维度**：元数据、研究动机、问题定义、核心贡献、方法创新、理论框架、实验框架、关键结果、局限性、未来工作、质量评估
- **实验 → 问题 → 结论映射**：每个实验都会分析它验证了什么主张、发现了什么、证据强度如何
- **三种输出模式**：快速（紧凑要点）、标准（段落说明）、深度（叙事性+批判性评估）
- **可配置深度**：混合搭配——例如，方法做深度分析，局限做快速扫描
- **图表提取**（可选）：从 PDF 中提取嵌入图像
- **维度控制**：按需包含或排除任意分析维度
- **独立运行**：最小依赖，无需重型框架
- **多路输出**（V1.1 新增）：控制台格式化文本、PDF 报告、结构化 JSON
- **多格式输出**（V1.2 新增）：PDF 报告、自包含 HTML（深色模式+侧栏目录）、Markdown 文件、结构化 JSON

## 安装

### 前置条件

- [opencode](https://opencode.ai) 并启用技能系统
- [pdf](https://github.com/anomalyco/opencode/tree/main/skills/pdf) 技能（用于 PDF 文本/图像提取）

### 安装步骤

将 `paper-analyzer` 文件夹放入您的 opencode 技能目录：

```bash
# 在您的项目或 opencode 配置目录下
cp -r paper-analyzer .opencode/skills/
```

或者克隆并创建符号链接：

```bash
git clone https://github.com/your-username/paper-analyzer.git
ln -s $(pwd)/paper-analyzer .opencode/skills/paper-analyzer
```

## 使用方法

通过要求分析或总结论文来触发技能：

```
> 帮我分析这篇论文 E:\papers\transformer.pdf
> analyze this paper https://arxiv.org/abs/2305.12345
> summarize https://openreview.net/forum?id=xxxxx
> 深度分析，提取图表
```

### 配置修饰符

| 修饰符 | 效果 |
|--------|------|
| `--mode=quick\|standard\|deep` | 设置分析深度 |
| `--include=motivation,contributions,methods,experiments` | 仅分析指定维度 |
| `--exclude=metadata,limitations,future` | 跳过指定维度 |
| `--extract-figures` | 从 PDF 中提取图像 |
| `--output=md\|html\|pdf\|json` | 输出格式（默认：pdf） |

示例：

```
# 快速扫描，跳过局限性
--mode=quick --exclude=limitations

# 深度分析方法与实验，提取图表
--mode=deep --include=methods,experiments --extract-figures
```

## 分析框架

### 11 个分析维度

| 维度 | 说明 |
|------|------|
| 元数据 | 标题、作者、发表 venue、年份、DOI、arxiv ID |
| 研究动机 | 问题为什么重要？实际应用或学术背景 |
| 问题定义 | 解决了什么具体的空白、瓶颈或局限？ |
| 核心贡献 | 论文声称的新贡献是什么？ |
| 方法创新 | 新颖在哪里——新架构、算法、框架或理论？ |
| 理论框架 | 支撑工作的理论、假设或形式化方法是什么？ |
| 实验框架 | 每个实验映射到：做了什么 → 回答什么问题 → 发现了什么 → 结论 → 证据强度 |
| 关键结果 | 定量和定性的研究发现 |
| 局限性 | 作者承认或可识别的弱点 |
| 未来工作 | 建议或隐含的下一步方向 |
| 质量评估 | 证据在多大程度上支持主张？论文是否严谨？ |

### 实验框架（核心创新）

不同于简单的实验列表，本技能将实验组织为**问题-答案映射**：

```
实验 [名称]：
  • 做了什么：描述
  • 回答的问题：验证了哪个主张或设计选择？
  • 实验设置：数据集、基线、指标
  • 结果：关键发现
  • 结论：验证或否定了什么？
  • 证据强度：强 / 中等 / 弱
```

这使得每个主张有什么证据支持——以及哪里缺乏证据——一目了然。

### 输出模式

| 模式 | 使用场景 | 结构 |
|------|---------|------|
| `quick` | 快速浏览、文献筛选 | 每个维度 1-2 行，紧凑要点 |
| `standard`（默认） | 日常阅读、做笔记 | 每段一段说明 + 结构化列表 |
| `deep` | 深入评估、批判性审阅 | 每个维度完整叙述，含证据评估、跨实验一致性检查和质量评判 |

## 输出示例

```markdown
---
title: Attention Is All You Need
authors: Vaswani et al.
affiliations: Google Brain
---

## 元数据
- 标题：Attention Is All You Need
- 作者：Vaswani et al.
- 会议/年份：NeurIPS 2017

## 研究动机
循环模型本质上是顺序的，无法并行化，且长序列带来内存瓶颈。

## 问题定义
能否设计一个完全基于注意力机制的序列转换模型，消除递归和卷积？

## 核心贡献
1. **"我们提出了 Transformer，一种仅基于注意力机制的简单网络架构，完全摒弃了递归和卷积。"**
Evidence: WMT 2014 主实验，28.4 BLEU。

2. **"我们引入多头注意力和位置编码，以同时捕获并行处理和序列顺序。"**
Evidence: Section 4 注意力头数的消融实验。

## 实验框架
### 实验 1：机器翻译（WMT 2014）
{段落叙述：做了什么、如何设置、使用什么数据}

**做了什么**：Transformer 与现有 SOTA 模型在 EN-DE 和 EN-FR 翻译上的对比
**验证的问题**：Transformer 能否达到或超越递归/卷积模型？
**实验设置**：WMT 2014 EN-DE、WMT 2014 EN-FR、BLEU、单卡 P100
**结果**：28.4 BLEU（EN-DE）、41.8 BLEU（EN-FR）
**结论**：Transformer 优于所有基线，训练时间更少
**证据强度**：强

## 局限性
| 局限性 | 作者是否承认 | 严重程度 |
|--------|-------------|---------|
| 自回归解码仍为顺序执行 | Yes | Minor |

## 质量评估
- Strengths: 新颖架构、强大的实验结果、清晰的表达
- Weaknesses: 仅限翻译任务；位置编码替代方案未探索
- Overall Soundness: 高
- Reproducibility: 高（开源代码、详细的超参数设置）
- Significance: 高（奠基性工作，10 万+引用）
```

## 依赖项

### 技能与工具依赖

| 依赖项 | 类型 | 调用方式 | 用途 |
|--------|------|---------|------|
| `pdf` 技能 | **硬依赖** | `skill: pdf` | PDF 文本/元数据/图像提取 |
| `webfetch` 工具 | 硬依赖 | 内置工具 | 获取 URL、HTML 内容 |
| `websearch` 工具 | 软依赖（备选） | 内置工具 | 直接访问失败时搜索论文 |

**关键规则**：为确保跨项目和设备的可移植性，PDF 处理必须通过 `pdf` 技能进行。请勿直接调用 PDF 库——始终先加载 `pdf` 技能并遵循其说明。这保证了技能在任何环境下都能正确运行。

本技能是**独立的**——无需依赖 nature-* 或 omr-* 技能。如果需要，它可以后续为这些技能提供输入。

### Python 库依赖

| 包名 | 用途 | 安装命令 |
|------|------|---------|
| `reportlab` | PDF 生成 | `pip install reportlab` |
| `mistune` | Markdown 解析（可选） | `pip install mistune`（通常已预装） |
| `pdfplumber` | PDF 文本提取 | `pip install pdfplumber`（通过 `pdf` 技能） |

## 路线图

- [x] 快速 / 标准 / 深度输出模式
- [x] 维度的包含/排除控制
- [x] 从 PDF 提取图表
- [x] Schema 驱动的类型映射（V1.1：标题即类型标注，无需关键词猜测）
- [x] 统一多路输出渲染器（控制台 / PDF / JSON）
- [x] JSON 导出用于下游流水线（如 omr-evidence、omr-synthesis）
- [x] 多格式输出：Markdown 文件 / 自包含 HTML（深色模式）/ PDF / JSON（V1.2）
- [x] 多层级列点支持（HTML / PDF / 控制台）（V1.2）
- [x] Unicode 破折号（– —）bullet 检测（V1.2）
- [x] Gate 质量门禁 — A（内容完整性）、B（语言合规）、C（实验必填字段）（V1.3）
- [x] Evidence 强度可视化 — 绿/黄/红三色徽章显示在 HTML 输出中（V1.3）
- [x] 子代理定义（`agents/openai.yaml`）支持外部调用（V1.3）
- [x] 实验字段值多行积累 — bullet 子列表自动追加到字段值中，以 `\n` 分隔（V1.3）
- [x] 贡献 evidence 去重 — look-ahead 行正确跳过，避免二次解析（V1.3）
- [x] 质量评估标签清理 — label 和 text 中的 `**` 标记被自动去除（V1.3）
- [x] 双语字段标签去重 — 每个 key 只根据 `lang` 选一个标签，不再中英文同时渲染（V1.3）
- [ ] **批量分析**——一次会话中分析多篇论文
- [ ] **对比模式**——并排比较两篇论文
- [ ] **Arxiv 自动推荐**——从分析上下文中发现相关论文
- [ ] **多语言支持**——分析日文、韩文等语言的论文
- [ ] **实验流程图生成**——自动生成实验关系图

## 架构（V1.3）

```
schema/analysis_schema.json     ← 唯一真相源
    │
    ├── SKILL.md                ← AI 读取此文件以生成正确的 Markdown
    │
    ├── agents/
    │   └── openai.yaml         ← 子代理定义，支持外部调用
    │
    └── scripts/
    ├── md_to_report.py     ← Schema 驱动的解析器（标题 → 类型映射）
    │                       （V1.2：Unicode dash 检测、层级追踪；
    │                        V1.3：实验字段积累、evidence 去重、QA 标签清理）
    └── generate_report.py  ← 统一渲染器 + Gate 质量门禁
                                （V1.2：render_html()、嵌套列点；
                                 V1.3：_gate_check()、evidence 彩色徽章、
                                       双语字段去重、\\n → <br/>）
```

解析器通过标题匹配 schema 中定义的类型，不再靠关键词猜测。这意味着：

- 任何标题含「局限性」的章节自动解析为 3 列表格（Limitation | Acknowledged | Severity）
- 任何标题含「质量评估」的章节自动解析为标签化 bullet（Strengths / Weaknesses 等）
- 任何标题含「核心贡献」的章节自动解析为 `1. **"quote"**` 格式
- 不再有 `_detect_limitation_table()` 关键词猜测——标题本身就是类型标注

## 贡献

这是一个开放的、社区驱动的技能。欢迎各种形式的贡献：

- **🐛 报告 Bug**：提交 Issue，描述技能的行为和预期输出
- **💡 功能建议**：提交 Issue，描述功能和使用场景
- **🔧 拉取请求**：改进 `SKILL.md` 逻辑、添加模板、修复边缘情况
- **📚 模板**：为不同论文类型（综述、系统、实证、理论等）提交新分析模板
- **🌐 本地化**：帮助支持多语言触发或输出

### 开发约定

- 保持技能**自包含**——避免添加新的硬依赖
- 遵循 `templates/` 中现有的模板结构
- 如果更改了分析框架或配置接口，请更新 `SKILL.md`
- 提交前至少使用一个 PDF 和一个 Arxiv URL 进行测试

### 如何扩展

1. **添加新的分析维度**：在 `SKILL.md` 的表格中添加，并更新每个模板
2. **创建新模板**：在 `templates/` 中添加文件，并在 `SKILL.md` 中引用
3. **添加配置选项**：在配置表格中添加，并在工作流逻辑中处理

## 更新日志

### V1.3 (2026-06-09) — 质量门禁 + Evidence 可视化 + 子代理 + 解析器健壮性

**新增功能：**
- **Gate 质量门禁**：`_gate_check()` 在每次 `build_report()` 前执行——Gate A 检查章节内容完整性（无空 section），Gate B 强制语言合规，Gate C 验证每个实验有 `question` + `conclusion` + `evidence`。不通过则阻塞输出并报告具体错误。
- **Evidence 强度可视化**：HTML 输出中证据强度以彩色徽章显示——绿色（`strong`/`强`）、黄色（`moderate`/`中等`）、红色（`weak`/`弱`），使用药丸状 CSS 徽章，支持浅色/深色主题。
- **子代理定义**：新增 `agents/openai.yaml`，允许外部技能通过 `$paper-analyzer` 调用，自动获得上下文隔离。

**Bug 修复：**
| # | 文件 | Bug 描述 | 影响 |
|---|------|---------|------|
| 1 | `md_to_report.py` | 实验字段（`**结果:**`、`**实验设置:**`）后跟 bullet 子列表时，仅捕获同行文本；后续 bullet 行静默进入节级 bullets，导致实验卡片显示破碎 | HTML 输出中实验数据碎片化 |
| 2 | `md_to_report.py` | 质量评估标签使用 `**优势:**`（冒号在加粗内部）时，`partition(':')` 将 `**` 残留在 label 和 text 中，暴露为字面 `**` | HTML 中可见的 `**` 标记 |
| 3 | `md_to_report.py` | 贡献 evidence 的 look-ahead 循环虽提取了文本，但主循环索引 `i` 未推进，导致 evidence 行被二次解析为节级段落 | 输出中 evidence 内容重复 |
| 4 | `generate_report.py` | 实验字段渲染使用扁平的 `[(en_label, key), (zh_label, key)]` 列表，每个字段值同时输出中英文标签 | HTML 输出中双语标签重复 |

**变更文件：**
| 文件 | 变更内容 |
|------|---------|
| `scripts/generate_report.py` | 新增 `GateCheckError`、`_gate_check()` 函数、evidence 徽章 CSS + 渲染逻辑；在 `build_report()` 中集成门禁检查 |
| `scripts/generate_report.py` | 实验字段标签从扁平双语列表改为 `{key: (en, zh)}` 字典，按 `lang` 选择单标签；字段值 `\n` → `<br/>` 支持多行显示 |
| `scripts/md_to_report.py` | 新增字段后行积累循环，将 bullet/段落内容追加到实验字段值；贡献 handler 中推进 `i` 跳过已消费的 evidence 行；质量评估的 label 中去掉 `**`、text 中去掉前导 `**` |
| `SKILL.md` | 工作流中新增 Gate Check 步骤（强制），位于质量验证和输出生成之间 |
| `agents/openai.yaml` | 新文件——子代理定义，支持外部调用 |

### V1.2 (2026-06-07) — HTML 输出 + 多层级列点 + Bug 修复

**新增功能：**
- **HTML 输出模式**：`build_report(md_text, output='html')` 生成自包含 `.html` 文件，含左侧导航目录、深色模式切换、响应式布局，无需外部依赖
- **Markdown 文件输出**：`build_report(md_text, output='md')` 将原始 Markdown 保存为 `.md` 文件，便于编辑和版本管理
- **多层级列点支持**：bullet 点现在在整个流水线中追踪缩进层级（2 空格 = 1 级）——Markdown → analysis_data → HTML/PDF/控制台；HTML 渲染嵌套 `<ul>`，PDF 和控台使用递进缩进
- **Unicode 破折号检测**：`–`（en-dash）和 `—`（em-dash）现被识别为合法的 bullet 标记

**Bug 修复：**
| # | 文件 | Bug 描述 | 影响 |
|---|------|---------|------|
| 1 | `generate_report.py` | `_render_section_html` 表格单元格使用 `esc()` 而非 `fmt()`，导致 `**bold**` 显示为字面 `**` | Markdown 格式在表格中丢失 |
| 2 | `md_to_report.py` | `_is_bullet_line` 仅识别 ASCII `-`、`*`、`+`；Unicode `–`/`—` 列点静默丢弃 | 列点数据丢失 |
| 3 | `generate_report.py` | `_render_section_html` 使用扁平 `<ul>`，所有列点同级别；缺少 `str()` 安全转换 | 层级丢失，非字符串项可能崩溃 |

**SKILL.md 更新：**
- 交互式提示：新增 HTML 和 Markdown 输出选项；移除纯控制台选项
- 实验框架：完整性检查清单从 4 个宽泛条目扩展为 6 个通用类别，附加 `(universal checklist — adapt to the field)` 说明
- 交互式提示格式：` ```tool ` 示例代码块替换为严格的 "MUST call" 指令，防止模型跳过
- Frontmatter description 更新为列出 "PDF / HTML / Markdown" 格式

### V1.1 (2025-06-06) — 架构重构 + Bug 修复

本次版本解决了 V1.0 中发现的设计缺陷，并修复了所有已知的解析器 Bug。

**设计变更（Schema 驱动架构）：**
- 新增 `schema/analysis_schema.json`——定义全部 11 个维度、数据类型、字段模式和格式提示的唯一真相源。AI 代理和解析器均引用此 schema。
- 解析器改为**章节标题 → schema 类型**映射，替代关键词猜测。章节标题如「局限性」和「质量评估」本身就是显式类型标注。
- 统一多路输出渲染器：`render_console()`（格式化文本）、`render_pdf()`（保持不变）、`render_json()`（新增：结构化 JSON 供下游技能使用）。
- 新增统一入口 `build_report(md_text, output='console|pdf|json', lang='zh|en', mode='quick|standard|deep')`。
- SKILL.md 关注点分离：AI 行为指令 vs. 机器可读 schema vs. 开发者 API 文档。

**Bug 修复（共 9 项）：**

| # | 文件 | Bug 描述 | 影响 |
|---|------|---------|------|
| 1 | `md_to_report.py` | `lstrip('-* ')` 字符集误用，`**bold**` 被截断为 `*bold**` | 文本损坏 |
| 2 | `md_to_report.py` | Evidence 查找跳过 bullet 格式行且不推进 `i`，导致重复处理 | Evidence 数据丢失 |
| 3 | `md_to_report.py` | 实验字段 key_map 仅支持英文标签，中文标签静默丢弃 | 中文模式数据丢失 |
| 4 | `md_to_report.py` | 表格分隔线正则不匹配多列表格；`_adjust_col_widths` 遇参差行崩溃；frontmatter 无关闭符时静默吞噬全文 | 解析崩溃/数据丢失 |
| 5 | `md_to_report.py` | `_detect_limitation_table` 对任何含 "Severity" 列的表格误报 | 表格分类错误 |
| 6 | `md_to_report.py` | `quality_buffer` 保存嵌套在 `if bullet_buffer:` 内部——所有 bullet 均为 quality item 时静默丢失 | Quality 数据丢失 |
| 7 | `generate_report.py` | `TEMP_DIR` 在模块导入时创建（模块级别）；第二次 `build_pdf()` 调用崩溃 | 多次调用崩溃 |
| 8 | `generate_report.py` | 字体路径全部硬编码为 `C:\Windows\Fonts\`——macOS/Linux 完全不可用 | 跨平台失败 |
| 9 | `generate_report.py` | `HorizontalLine(170mm)` 溢出页边距；PDF 文件名碰撞静默覆盖文件 | 布局溢出/数据丢失 |

**模板修复：**
- `templates/standard.md`：Limitations 从 bullet 改为 3 列 markdown 表格以匹配解析器
- `templates/standard.md`：Quality Assessment 从单段改为标签化 bullet
- `templates/deep.md`：Quality Assessment 从 `###` 子章节改为标签化 bullet
- `templates/deep.md`：Contributions 从 bullet 列表改为 `1. **"quote"**` + `Evidence:` 格式

**文档修复：**
- `SKILL.md`：Output Example Structure 重写为与解析器实际期望一致（contributions 使用 `1. **"quote"**` 而非 bullet；完整章节标题列表；YAML frontmatter）
- `SKILL.md`：Key Principles 中添加 schema 引用和规范章节标题要求
- `SKILL.md`：Dependency Summary 中添加 `reportlab` 和 `mistune`

### V1.0 — 初始版本
- 11 维度分析框架
- 快速 / 标准 / 深度输出模式
- 通过 `pdf` 技能的 PDF 文本提取
- PDF 图表提取
- 维度包含/排除控制
- `build_pdf()` 入口函数

## 许可证

MIT — 可自由使用、修改和分享。

---

基于 opencode 构建。有问题？提交 Issue 或发起讨论。
