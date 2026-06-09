"""Generic paper analysis report generator using reportlab.
Accepts structured analysis_data dict for any paper type.
Usage:
    build_pdf(analysis_data, lang='en') -> pdf_path
    render_console(analysis_data, lang='en') -> str
    render_json(analysis_data, output_path) -> json_path
    build_report(md_text, output='console', lang='zh', mode='standard') -> result"""
import os
import sys
import re as _re
import json as _json
from datetime import datetime


class LanguageComplianceError(ValueError):
    """Raised when output text language does not match the declared lang."""
    pass


def _check_language_compliance(text, lang):
    """Verify that text matches the expected language.
    For zh: CJK characters should be >= 8% of total characters.
    For en: CJK characters should be <= 5% of total characters.
    Raises LanguageComplianceError on violation.
    """
    if not text or not lang:
        return
    cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    total = max(len(text), 1)
    ratio = cjk / total

    if lang == 'zh' and ratio < 0.08:
        raise LanguageComplianceError(
            f"[LANG=zh] 输出文本 {total} 个字符中仅 {cjk} 个中文字符 (占比 {ratio:.1%})，"
            f"远低于 8% 阈值。请使用中文重新生成分析报告。"
        )
    if lang == 'en' and ratio > 0.05:
        raise LanguageComplianceError(
            f"[LANG=en] Output text has {cjk} CJK characters ({ratio:.1%}) "
            f"out of {total}. Please regenerate in English."
        )


def _extract_text_from_sections(sections):
    """Concatenate all text content from a list of section dicts."""
    parts = []
    for s in sections:
        for key in ('paragraphs', 'bullets'):
            for item in s.get(key, []):
                if isinstance(item, str):
                    parts.append(item)
        for c in s.get('contributions', []):
            parts.append(c.get('claim', ''))
            parts.append(c.get('evidence_ref', ''))
        for e in s.get('experiments', []):
            for fk in ('paragraph', 'what', 'question', 'setup', 'results', 'conclusion', 'evidence'):
                parts.append(e.get(fk, ''))
        for qi in s.get('quality_items', []):
            parts.append(qi.get('label', ''))
            parts.append(qi.get('text', ''))
        for lim in s.get('limitation_items', []):
            parts.append(lim.get('text', ''))
        parts.extend(_extract_text_from_sections(s.get('subsections', [])))
    return ' '.join(parts)
class GateCheckError(ValueError):
    """Raised when analysis_data fails gate quality checks."""
    pass


def _gate_check(analysis_data, lang='zh'):
    """Run quality gates on analysis_data before rendering.
    Gate A: Section content completeness — no empty sections.
    Gate B: Language compliance.
    Gate C: Experiment completeness — each must have question + conclusion + evidence.
    Returns None on success, raises GateCheckError on failure.
    """
    sections = analysis_data.get('sections', [])
    errors = []

    # Gate A: Section content completeness
    for s in sections:
        title = s.get('title', '(untitled)')
        has_content = (
            bool(s.get('paragraphs'))
            or bool(s.get('bullets'))
            or bool(s.get('contributions'))
            or bool(s.get('experiments'))
            or bool(s.get('tables'))
            or bool(s.get('limitation_items'))
            or bool(s.get('quality_items'))
        )
        if not has_content:
            errors.append(f"[Gate A] Section '{title}' has no content")

    # Gate B: Language compliance
    sections_text = _extract_text_from_sections(sections)
    try:
        _check_language_compliance(sections_text, lang)
    except LanguageComplianceError as e:
        errors.append(f"[Gate B] {e}")

    # Gate C: Experiment completeness
    for s in sections:
        for ei, exp in enumerate(s.get('experiments', []), 1):
            missing = []
            if not exp.get('question', '').strip():
                missing.append('question')
            if not exp.get('conclusion', '').strip():
                missing.append('conclusion')
            if not exp.get('evidence', '').strip():
                missing.append('evidence')
            if missing:
                sec_title = s.get('title', 'unknown')
                exp_name = exp.get('name', f'Experiment {ei}')
                errors.append(
                    f"[Gate C] Section '{sec_title}', {exp_name}: "
                    f"missing required fields: {', '.join(missing)}"
                )

    if errors:
        raise GateCheckError(
            f"Gate check FAILED ({len(errors)} issue(s)):\n" + "\n".join(errors)
        )


from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Table, TableStyle, Flowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.ttfonts import TTFError

DARK_BLUE = HexColor('#2C3E50')
MEDIUM_BLUE = HexColor('#34495E')
ACCENT_BLUE = HexColor('#3498DB')
LIGHT_GRAY = HexColor('#ECF0F1')
MED_GRAY = HexColor('#7F8C8D')
TEXT_COLOR = HexColor('#2C3E50')
QUOTE_COLOR = HexColor('#7F8C8D')

# Font globals – overridden by _setup_fonts()
_TITLE_FONT = 'Helvetica'
_TITLE_BOLD = 'Helvetica-Bold'
_BODY_FONT = 'Helvetica'
_BODY_BOLD = 'Helvetica-Bold'
_FONT_OBLIQUE = 'Helvetica-Oblique'
_SECTION_FONT = 'Helvetica'


def _register_font_safe(path, name):
    """Register a TTF font, returning True on success."""
    try:
        pdfmetrics.registerFont(TTFont(name, path))
        return True
    except (TTFError, OSError, Exception):
        return False


def _find_cjk_fonts():
    if sys.platform == 'win32':
        base = r'C:\Windows\Fonts'
        candidates = [
            (os.path.join(base, 'msyh.ttc'), 'MicrosoftYaHei'),
            (os.path.join(base, 'msyhbd.ttc'), 'MicrosoftYaHei-Bold'),
            (os.path.join(base, 'simsun.ttc'), 'SimSun'),
            (os.path.join(base, 'simhei.ttf'), 'SimHei'),
        ]
    elif sys.platform == 'darwin':
        candidates = [
            ('/System/Library/Fonts/PingFang.ttc', 'PingFang'),
            ('/System/Library/Fonts/STHeiti Light.ttc', 'STHeiti'),
            ('/Library/Fonts/Arial Unicode.ttf', 'ArialUnicode'),
        ]
    else:  # Linux
        candidates = [
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WenQuanYi'),
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WenQuanYiMicro'),
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
        ]
    result = {'title': None, 'body': None}
    for path, name in candidates:
        if os.path.exists(path):
            registered = _register_font_safe(path, name)
            if registered and not result['body']:
                result['body'] = name
            if registered and not result['title'] and 'bold' not in name.lower():
                result['title'] = name or result['title']
    if not result['title']:
        result['title'] = result['body']
    return result


def _setup_fonts(lang):
    global _TITLE_FONT, _TITLE_BOLD, _BODY_FONT, _BODY_BOLD, _FONT_OBLIQUE, _SECTION_FONT
    if lang == 'zh':
        fonts = _find_cjk_fonts()
        if fonts['title']:
            _TITLE_FONT = fonts['title']
            _TITLE_BOLD = fonts['title']
        if fonts['body']:
            _BODY_FONT = fonts['body']
            _BODY_BOLD = fonts['body']
        _FONT_OBLIQUE = _BODY_FONT if _BODY_FONT else 'Helvetica'
        _SECTION_FONT = _TITLE_FONT if _TITLE_FONT else 'Helvetica'
        # Try SimHei for section titles on Windows
        simhei_path = r'C:\Windows\Fonts\simhei.ttf'
        if os.path.exists(simhei_path) and sys.platform == 'win32':
            if _register_font_safe(simhei_path, 'SimHei'):
                _SECTION_FONT = 'SimHei'
    else:
        if sys.platform == 'win32':
            tnr_paths = {
                'TimesNewRoman': r'C:\Windows\Fonts\times.ttf',
                'TimesNewRoman-Bold': r'C:\Windows\Fonts\timesbd.ttf',
                'TimesNewRoman-Italic': r'C:\Windows\Fonts\timesi.ttf',
            }
            for name, path in tnr_paths.items():
                if os.path.exists(path):
                    _register_font_safe(path, name)
        _TITLE_FONT = 'TimesNewRoman-Bold'
        _TITLE_BOLD = 'TimesNewRoman-Bold'
        _BODY_FONT = 'TimesNewRoman'
        _BODY_BOLD = 'TimesNewRoman-Bold'
        _FONT_OBLIQUE = 'TimesNewRoman-Italic'
        _SECTION_FONT = 'TimesNewRoman-Bold'


class HorizontalLine(Flowable):
    def __init__(self, width, color=ACCENT_BLUE, thickness=0.5):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness
        self.height = thickness + 4

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 2, self.width, 2)


def _md_to_xml(text):
    """Convert Markdown inline formatting to ReportLab XML tags.
    **bold** → <b>bold</b>, *italic* → <i>italic</i>"""
    if not text:
        return text
    # Bold: **text**
    text = _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic: *text* (not **)
    text = _re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    return text


def build_styles():
    styles = getSampleStyleSheet()
    TB = _TITLE_BOLD
    TF = _TITLE_FONT
    BF = _BODY_FONT

    # --- Title page (keep original style) ---
    styles.add(ParagraphStyle('TitlePage', fontName=TF, fontSize=26, leading=32,
                textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6*mm))
    styles.add(ParagraphStyle('SubTitle', fontName=TF, fontSize=14, leading=18,
                textColor=MEDIUM_BLUE, alignment=TA_CENTER, spaceAfter=3*mm))
    styles.add(ParagraphStyle('AuthorLine', fontName=BF, fontSize=10, leading=14,
                textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=2*mm))

    # --- Section headings (thesis-style) ---
    SF = _SECTION_FONT
    styles.add(ParagraphStyle('SectionTitle', fontName=SF, fontSize=16, leading=22,
                textColor=DARK_BLUE, spaceBefore=6*mm, spaceAfter=3*mm))
    styles.add(ParagraphStyle('SubSectionTitle', fontName=SF, fontSize=14, leading=18,
                textColor=MEDIUM_BLUE, spaceBefore=4*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle('SubSubSectionTitle', fontName=SF, fontSize=12, leading=16,
                textColor=MEDIUM_BLUE, spaceBefore=3*mm, spaceAfter=1*mm))

    # --- Body (thesis-style: 12pt, 1.5x leading, 2-char indent) ---
    styles.add(ParagraphStyle('Body', fontName=BF, fontSize=12, leading=20,
                textColor=TEXT_COLOR, alignment=TA_JUSTIFY, spaceAfter=0,
                firstLineIndent=24))
    styles.add(ParagraphStyle('BulletStyle', fontName=BF, fontSize=12, leading=20,
                textColor=TEXT_COLOR, leftIndent=8*mm, spaceAfter=0))

    # --- Quote ---
    styles.add(ParagraphStyle('Quote', fontName=_FONT_OBLIQUE, fontSize=11, leading=15,
                textColor=QUOTE_COLOR, leftIndent=12*mm, rightIndent=12*mm,
                spaceBefore=1*mm, spaceAfter=2*mm))

    # --- Table ---
    styles.add(ParagraphStyle('TableCell', fontName=BF, fontSize=10, leading=13,
                textColor=TEXT_COLOR, alignment=TA_CENTER))
    styles.add(ParagraphStyle('TableHeader', fontName=_BODY_BOLD, fontSize=10, leading=13,
                textColor=white, alignment=TA_CENTER))

    return styles


def make_table(data, col_widths=None):
    cell_style = ParagraphStyle('_Cell', fontName=_BODY_FONT, fontSize=10, leading=13,
                                 textColor=TEXT_COLOR, alignment=TA_CENTER)
    header_style = ParagraphStyle('_HCell', fontName=_BODY_BOLD, fontSize=10, leading=13,
                                   textColor=white, alignment=TA_CENTER)
    table_data = []
    for i, row in enumerate(data):
        style = header_style if i == 0 else cell_style
        table_data.append([Paragraph(str(c), style) for c in row])
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GRAY))
    t.setStyle(TableStyle(cmds))
    return t


def build_pdf(analysis_data, output_dir=None, lang='en', cleanup_files=None):
    _setup_fonts(lang)
    styles = build_styles()

    # Language compliance check for zh: verify CJK character ratio
    sections_text = _extract_text_from_sections(analysis_data.get('sections', []))
    _check_language_compliance(sections_text, lang)

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), 'analysis_result')
    os.makedirs(output_dir, exist_ok=True)

    safe_title = analysis_data.get('title', 'paper')
    safe_title = '_'.join(safe_title.split())
    for ch in ':/\\?%*|"<>':
        safe_title = safe_title.replace(ch, '_')
    safe_title = safe_title.strip('._')[:80]
    pdf_path = os.path.join(output_dir, f'{safe_title}_Analysis_Report.pdf')
    # Avoid filename collision by appending timestamp if file exists
    if os.path.exists(pdf_path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_path = os.path.join(output_dir, f'{safe_title}_{ts}_Analysis_Report.pdf')

    if lang == 'zh':
        lm = rm = 3.17*cm
        tm = bm = 2.54*cm
    else:
        lm = rm = tm = bm = 25*mm
    content_width = (210*mm - lm - rm)  # available text width in points
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
        leftMargin=lm, rightMargin=rm,
        topMargin=tm, bottomMargin=bm)

    story = []
    S = styles

    report_title = '论文分析报告' if lang == 'zh' else 'Paper Analysis Report'
    story.append(Spacer(1, 50*mm))
    story.append(Paragraph(report_title, S['TitlePage']))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(analysis_data.get('title', ''), S['SubTitle']))
    if analysis_data.get('subtitle'):
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(analysis_data['subtitle'], S['AuthorLine']))
    story.append(Spacer(1, 6*mm))
    if analysis_data.get('authors'):
        story.append(Paragraph(analysis_data['authors'], S['AuthorLine']))
    story.append(Spacer(1, 4*mm))
    if analysis_data.get('affiliations'):
        story.append(Paragraph(analysis_data['affiliations'], S['AuthorLine']))
    for label, value in analysis_data.get('meta_items', []):
        story.append(Paragraph(f'<b>{label}:</b> {value}', S['AuthorLine']))
    story.append(Spacer(1, 30*mm))
    footer = '由 Paper Analyzer Skill 生成' if lang == 'zh' else 'Generated by Paper Analyzer Skill'
    story.append(Paragraph(footer,
        ParagraphStyle('FooterNote', parent=S['AuthorLine'], fontSize=9, textColor=HexColor('#AAAAAA'))))
    story.append(PageBreak())

    for si, section in enumerate(analysis_data.get('sections', [])):
        _add_section(story, S, section, content_width)
        if si < len(analysis_data['sections']) - 1:
            story.append(PageBreak())

    doc.build(story)
    if cleanup_files:
        for f in cleanup_files:
            if isinstance(f, str) and os.path.exists(f):
                os.remove(f)
    return pdf_path


def _add_section(story, styles, section, content_width=None, depth=0):
    title_styles = [styles['SectionTitle'], styles['SubSectionTitle'], styles['SubSubSectionTitle']]
    ts = title_styles[min(depth, len(title_styles) - 1)]

    if content_width is None:
        content_width = 170*mm  # fallback

    if section.get('title'):
        story.append(Paragraph(section['title'], ts))
        story.append(HorizontalLine(content_width / mm * mm))  # ensure mm units
        story.append(Spacer(1, 2*mm))

    for p in section.get('paragraphs', []):
        story.append(Paragraph(_md_to_xml(p), styles['Body']))

    for q in section.get('quotes', []):
        story.append(Paragraph(_md_to_xml(q), styles['Quote']))

    for b in section.get('bullets', []):
        text = b['text'] if isinstance(b, dict) else b
        level = b.get('level', 0) if isinstance(b, dict) else 0
        prefix = '&bull; ' if not text.strip().startswith('&bull;') else ''
        indent = level * 8 * mm
        bs = styles['BulletStyle']
        if indent:
            bs = ParagraphStyle('BulletNested', parent=bs, leftIndent=bs.leftIndent + indent)
        story.append(Paragraph(prefix + _md_to_xml(text), bs))

    # Core Contributions: direct quote + evidence reference
    for ci, contrib in enumerate(section.get('contributions', []), 1):
        claim = contrib.get('claim', '')
        evid = contrib.get('evidence_ref', '')
        text = f'<b>{ci}. {claim}</b>'
        if evid:
            text += f'<br/><i>Evidence: {evid}</i>'
        story.append(Paragraph(text, styles['BulletStyle']))

    for t in section.get('tables', []):
        data = [t['headers']] + t['rows']
        w = t.get('col_widths')
        if w:
            w = [x * mm if isinstance(x, (int, float)) else x for x in w]
        story.append(make_table(data, w))
        story.append(Spacer(1, 2*mm))

    # Experiments: structured per SKILL.md (narrative + 6-field mapping)
    for exp in section.get('experiments', []):
        name = exp.get('name', '')
        if name:
            story.append(Paragraph(f'<b>Experiment: {name}</b>', styles['SubSubSectionTitle']))
        para = exp.get('paragraph', '')
        if para:
            story.append(Paragraph(_md_to_xml(para), styles['Body']))
        fields = [
            ('What it did', 'what'),
            ('Question it answers', 'question'),
            ('Setup', 'setup'),
            ('Results', 'results'),
            ('Conclusion', 'conclusion'),
        ]
        for label, key in fields:
            val = exp.get(key, '')
            if val:
                story.append(Paragraph(f'<b>{label}:</b> {_md_to_xml(val)}', styles['Body']))
        ev = exp.get('evidence', '')
        if ev:
            story.append(Paragraph(f'<b>Evidence strength:</b> {_md_to_xml(ev)}', styles['Body']))
        story.append(Spacer(1, 2*mm))

    # Limitation items: auto-table from SKILL.md standard
    lims = section.get('limitation_items', [])
    if lims:
        rows = []
        for lim in lims:
            rows.append([lim.get('text', ''), lim.get('acknowledged', ''), lim.get('severity', '')])
        t = make_table([['Limitation', 'Acknowledged', 'Severity']] + rows,
                       col_widths=[80*mm, 20*mm, 20*mm])
        story.append(t)
        story.append(Spacer(1, 2*mm))

    # Quality items: label → text
    for qi in section.get('quality_items', []):
        label = qi.get('label', '')
        text = qi.get('text', '')
        if label and text:
            story.append(Paragraph(f'<b>{label}:</b> {_md_to_xml(text)}', styles['BulletStyle']))

    for sub in section.get('subsections', []):
        _add_section(story, styles, sub, content_width, depth + 1)


# ============================================================
# Unified renderers (v2): console, JSON, and the unified entry
# ============================================================

_SEP = '=' * 70
_THIN = '-' * 50


def render_console(analysis_data, lang='zh'):
    """Render analysis_data as formatted console Markdown string."""
    lines = []

    # Title block
    title = analysis_data.get('title', 'Unknown')
    lines.append(_SEP)
    lines.append(f"  {title}")
    lines.append(_SEP)

    authors = analysis_data.get('authors', '')
    if authors:
        lines.append(f"  Authors: {authors}")
    affiliations = analysis_data.get('affiliations', '')
    if affiliations:
        lines.append(f"  Affiliations: {affiliations}")

    for label, value in analysis_data.get('meta_items', []):
        lines.append(f"  {label}: {value}")

    lines.append('')
    lines.append(_SEP)

    # Sections
    for section in analysis_data.get('sections', []):
        title = section.get('title', '')
        schema_id = section.get('schema_id', '')

        lines.append('')
        lines.append(f"## {title}")
        if schema_id:
            lines.append(f"  [schema: {schema_id}]")
        lines.append(_THIN)

        for p in section.get('paragraphs', []):
            lines.append('')
            lines.append(p)

        for b in section.get('bullets', []):
            text = b['text'] if isinstance(b, dict) else b
            level = b.get('level', 0) if isinstance(b, dict) else 0
            lines.append(f'{"  " * level}  - {text}')

        for contrib in section.get('contributions', []):
            claim = contrib.get('claim', '')
            evid = contrib.get('evidence_ref', '')
            lines.append(f'  > {claim}')
            if evid:
                lines.append(f'    Evidence: {evid}')

        for exp in section.get('experiments', []):
            name = exp.get('name', '')
            lines.append(f'  ### Experiment: {name}')
            for key, label in [('what', 'What'), ('question', 'Question'),
                               ('setup', 'Setup'), ('results', 'Results'),
                               ('conclusion', 'Conclusion'), ('evidence', 'Evidence')]:
                val = exp.get(key, '')
                if val:
                    lines.append(f'    **{label}:** {val}')

        for t in section.get('tables', []):
            headers = t.get('headers', [])
            rows = t.get('rows', [])
            # Simple text table
            col_w = [max(len(str(r[i]) if i < len(r) else '') for r in [headers] + rows) for i in range(len(headers))]
            hdr_line = ' | '.join(h.ljust(col_w[i]) for i, h in enumerate(headers))
            lines.append(f'  | {hdr_line} |')
            sep_line = ' | '.join('-' * col_w[i] for i in range(len(headers)))
            lines.append(f'  |-{sep_line}-|')
            for row in rows:
                r_line = ' | '.join(str(row[i] if i < len(row) else '').ljust(col_w[i]) for i in range(len(headers)))
                lines.append(f'  | {r_line} |')

        for lim in section.get('limitation_items', []):
            lines.append(f'  [{lim.get("severity", "")}] {lim.get("text", "")} (acknowledged: {lim.get("acknowledged", "")})')

        for qi in section.get('quality_items', []):
            lines.append(f'  **{qi.get("label", "")}:** {qi.get("text", "")}')

        for sub in section.get('subsections', []):
            lines.append(f'  ### {sub.get("title", "")}')
            for sp in sub.get('paragraphs', []):
                lines.append(f'    {sp}')

    return '\n'.join(lines)


def render_json(analysis_data, output_path):
    """Serialize analysis_data as JSON file."""
    # Remove internal markers for clean output
    clean = {
        'title': analysis_data.get('title', ''),
        'authors': analysis_data.get('authors', ''),
        'affiliations': analysis_data.get('affiliations', ''),
        'meta_items': analysis_data.get('meta_items', []),
        'sections': [],
    }
    for s in analysis_data.get('sections', []):
        clean_s = {'title': s.get('title', ''), 'schema_id': s.get('schema_id', '')}
        for key in ['paragraphs', 'bullets', 'contributions', 'experiments',
                     'tables', 'limitation_items', 'quality_items', 'subsections']:
            val = s.get(key)
            if val:
                clean_s[key] = val
        clean['sections'].append(clean_s)

    with open(output_path, 'w', encoding='utf-8') as f:
        _json.dump(clean, f, ensure_ascii=False, indent=2)
    return output_path


def render_html(analysis_data, lang='zh'):
    """Render analysis_data as a standalone HTML file with left-sidebar TOC and dark mode toggle."""
    title = analysis_data.get('title', '')
    authors = analysis_data.get('authors', '')
    affiliations = analysis_data.get('affiliations', '')
    meta_items = analysis_data.get('meta_items', [])
    sections = analysis_data.get('sections', [])

    report_title = '论文分析报告' if lang == 'zh' else 'Paper Analysis Report'
    html_lang = 'zh-CN' if lang == 'zh' else 'en'
    toggle_light = '浅色' if lang == 'zh' else 'Light'
    toggle_dark = '深色' if lang == 'zh' else 'Dark'
    toc_title = '目录' if lang == 'zh' else 'Contents'

    body_font_zh = ('"Noto Serif CJK SC", "Source Han Serif CN", '
                    '"SimSun", "STSong", serif')
    heading_font_zh = ('"Noto Sans CJK SC", "Source Han Sans CN", '
                       '"Microsoft YaHei", "PingFang SC", sans-serif')
    body_font_en = 'Georgia, "Times New Roman", serif'
    heading_font_en = ('"Helvetica Neue", "Segoe UI", Arial, sans-serif')

    bf = body_font_zh if lang == 'zh' else body_font_en
    hf = heading_font_zh if lang == 'zh' else heading_font_en

    def esc(text):
        if text is None:
            return ''
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def fmt(text):
        if not text:
            return ''
        text = esc(text)
        text = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = _re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
        return text

    # ── TOC ──
    toc_lines = []
    sec_html_parts = []

    for i, section in enumerate(sections):
        sec_title = section.get('title', '')
        sec_id = f'sec-{i}'
        if sec_title:
            toc_lines.append(
                f'<li><a class="toc-link" href="#{sec_id}">{esc(sec_title)}</a></li>'
            )
        sec_html_parts.append(_render_section_html(section, sec_id, fmt, lang, esc=esc))

    toc_html = f'''<nav class="sidebar" aria-label="Table of Contents">
  <div class="toc-sticky">
    <h3 class="toc-title">{esc(toc_title)}</h3>
    <ul class="toc-list">{' '.join(toc_lines)}</ul>
  </div>
</nav>'''

    # ── Meta items ──
    meta_html = ''
    for label, value in meta_items:
        meta_html += f'<span class="meta-item"><strong>{esc(label)}:</strong> {esc(value)}</span>\n'

    # ── Title page ──
    title_html = f'''<header class="report-header">
  <p class="report-type">{esc(report_title)}</p>
  <h1 class="report-title">{esc(title)}</h1>
  {f'<p class="report-authors">{esc(authors)}</p>' if authors else ''}
  {f'<p class="report-affiliations">{esc(affiliations)}</p>' if affiliations else ''}
  <div class="meta-bar">{meta_html}</div>
</header>'''

    # ── Assemble ──
    sections_html = '\n\n'.join(sec_html_parts)
    content_html = f'<main class="content">{title_html}{sections_html}</main>'

    # ── CSS ──
    css = f'''*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#FAFAF8;--bg-card:#FFFFFF;--bg-sidebar:#F5F3FF;--text:#2C2C2C;--text-secondary:#6B7280;--accent:#7C3AED;--accent-hover:#6D28D9;--accent-light:#EDE9FE;--border:#E5E7EB;--quote-bg:#F9F9FB;--quote-border:#D1D5DB;--table-header-bg:#7C3AED;--table-header-text:#FFFFFF;--table-stripe:#F9F9FB;--code-bg:#F3F4F6;--shadow:0 1px 3px rgba(0,0,0,0.08);--shadow-lg:0 4px 12px rgba(0,0,0,0.1);--radius:8px;--radius-sm:4px}}
[data-theme="dark"]{{--bg:#1A1A2E;--bg-card:#242538;--bg-sidebar:#1E1F3A;--text:#E0E0E0;--text-secondary:#9CA3AF;--accent:#A78BFA;--accent-hover:#C4B5FD;--accent-light:#2D1B69;--border:#374151;--quote-bg:#1F2137;--quote-border:#4B5563;--table-header-bg:#A78BFA;--table-header-text:#1A1A2E;--table-stripe:#1F2137;--code-bg:#2D2D3F;--shadow:0 1px 3px rgba(0,0,0,0.3);--shadow-lg:0 4px 12px rgba(0,0,0,0.4)}}
body{{font-family:{bf};font-size:16px;line-height:1.8;color:var(--text);background:var(--bg);-webkit-font-smoothing:antialiased}}
.app-container{{display:flex;max-width:1320px;margin:0 auto;padding:0 24px;gap:32px;min-height:100vh}}
.content{{flex:1;min-width:0;padding:40px 0 80px}}
.sidebar{{width:260px;flex-shrink:0;padding-top:40px}}
.toc-sticky{{position:sticky;top:24px;max-height:calc(100vh - 48px);overflow-y:auto;padding:16px 12px;background:var(--bg-sidebar);border-radius:var(--radius);border:1px solid var(--border)}}
.toc-title{{font-family:{hf};font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-secondary);margin-bottom:12px;padding:0 8px}}
.toc-list{{list-style:none;padding:0;margin:0}}
.toc-link{{display:block;padding:5px 8px;font-size:13px;line-height:1.4;color:var(--text-secondary);text-decoration:none;border-radius:var(--radius-sm);transition:all 0.15s}}
.toc-link:hover{{background:var(--accent-light);color:var(--accent)}}
.toc-link.active{{background:var(--accent-light);color:var(--accent);font-weight:600;border-left:3px solid var(--accent)}}
.theme-toggle{{position:fixed;top:16px;right:16px;z-index:1000;width:40px;height:40px;border-radius:50%;border:1px solid var(--border);background:var(--bg-card);color:var(--text);cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow);transition:all 0.2s}}
.theme-toggle:hover{{box-shadow:var(--shadow-lg);border-color:var(--accent)}}
.report-header{{margin-bottom:48px;padding-bottom:32px;border-bottom:2px solid var(--accent-light)}}
.report-type{{font-family:{hf};font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--accent);margin-bottom:8px}}
.report-title{{font-family:{hf};font-size:28px;font-weight:700;line-height:1.3;margin-bottom:12px;color:var(--text)}}
.report-authors{{font-size:15px;color:var(--text-secondary);margin-bottom:4px}}
.report-affiliations{{font-size:14px;color:var(--text-secondary);margin-bottom:8px}}
.meta-bar{{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:12px}}
.meta-item{{font-size:13px;color:var(--text-secondary)}}
h2{{font-family:{hf};font-size:22px;font-weight:700;margin-top:48px;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid var(--accent-light);color:var(--text);scroll-margin-top:24px}}
h3{{font-family:{hf};font-size:18px;font-weight:600;margin-top:32px;margin-bottom:12px;color:var(--text);scroll-margin-top:24px}}
h4{{font-family:{hf};font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px;color:var(--text)}}
p{{margin-bottom:12px}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{color:var(--accent-hover);text-decoration:underline}}
blockquote{{margin:12px 0;padding:12px 16px;background:var(--quote-bg);border-left:4px solid var(--quote-border);border-radius:0 var(--radius-sm) var(--radius-sm) 0;color:var(--text-secondary);font-style:italic}}
ul,ol{{padding-left:24px;margin-bottom:12px}}
li{{margin-bottom:4px}}
code{{font-family:"SFMono-Regular","Consolas","Liberation Mono",monospace;font-size:0.875em;padding:2px 6px;background:var(--code-bg);border-radius:var(--radius-sm);color:var(--text)}}
.contrib-block{{margin:16px 0}}
.contribution{{margin-bottom:16px;padding:12px 16px;background:var(--quote-bg);border-radius:var(--radius);border-left:4px solid var(--accent)}}
.contribution .contrib-number{{font-family:{hf};font-weight:700;color:var(--accent);margin-right:4px}}
.contribution > blockquote{{margin:4px 0;padding:0;background:transparent;border:none;font-style:normal;color:var(--text)}}
.contribution .contrib-evidence{{font-size:14px;color:var(--text-secondary);margin-top:4px}}
.experiment-card{{margin:16px 0;padding:20px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);transition:box-shadow 0.2s}}
.experiment-card:hover{{box-shadow:var(--shadow-lg)}}
.exp-name{{font-family:{hf};font-size:15px;font-weight:600;color:var(--accent);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
.exp-fields p{{margin-bottom:6px;font-size:14px;line-height:1.6}}
.exp-fields strong{{color:var(--text);font-weight:600}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px;line-height:1.5}}
th,td{{padding:8px 12px;text-align:left;border:1px solid var(--border)}}
th{{background:var(--table-header-bg);color:var(--table-header-text);font-weight:600;font-family:{hf}}}
tr:nth-child(even){{background:var(--table-stripe)}}
tr:hover{{background:var(--accent-light);transition:background 0.15s}}
.limitation-table th:first-child{{width:60%}}
.quality-items p{{margin-bottom:8px;padding:8px 12px;background:var(--bg-card);border-radius:var(--radius-sm);border-left:3px solid var(--accent-light)}}
.quality-items strong{{color:var(--text);font-weight:600}}
.evidence-badge{{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;letter-spacing:0.03em}}
.evidence-strong{{background:#DCFCE7;color:#166534;border:1px solid #BBF7D0}}
.evidence-moderate{{background:#FEF9C3;color:#854D0E;border:1px solid #FDE68A}}
.evidence-weak{{background:#FEE2E2;color:#991B1B;border:1px solid #FECACA}}
[data-theme="dark"] .evidence-strong{{background:#052E16;color:#86EFAC;border-color:#166534}}
[data-theme="dark"] .evidence-moderate{{background:#422006;color:#FDE68A;border-color:#854D0E}}
[data-theme="dark"] .evidence-weak{{background:#450A0A;color:#FCA5A5;border-color:#991B1B}}
@media(max-width:900px){{.sidebar{{display:none}}.app-container{{padding:0 16px}}.report-title{{font-size:24px}}}}
@media(max-width:480px){{.report-title{{font-size:20px}}h2{{font-size:20px}}}}
@media print{{.sidebar,.theme-toggle{{display:none!important}}.app-container{{display:block;max-width:none;padding:0}}.experiment-card{{break-inside:avoid;box-shadow:none;border:1px solid #ccc}}}}'''

    # ── JS ──
    js = f'''document.addEventListener('DOMContentLoaded',function(){{
var t=document.getElementById('theme-toggle'),h=document.documentElement;
var s=localStorage.getItem('theme');
if(!s){{s=window.matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';localStorage.setItem('theme',s)}}
h.setAttribute('data-theme',s);
t.textContent=s==='dark'?'☀️':'🌙';
t.setAttribute('aria-label',s==='dark'?'{toggle_light}':'{toggle_dark}');
t.addEventListener('click',function(){{
var n=h.getAttribute('data-theme')==='dark'?'light':'dark';
h.setAttribute('data-theme',n);localStorage.setItem('theme',n);
t.textContent=n==='dark'?'☀️':'🌙';
t.setAttribute('aria-label',n==='dark'?'{toggle_light}':'{toggle_dark}')
}});
var o=new IntersectionObserver(function(e){{e.forEach(function(e){{var l=document.querySelector('.toc-link[href="#'+e.target.id+'"]');if(l)l.classList.toggle('active',e.isIntersecting)}})}},{{threshold:0.3,rootMargin:'-80px 0px'}});
document.querySelectorAll('section[id]').forEach(function(e){{o.observe(e)}});
document.querySelectorAll('.toc-link').forEach(function(e){{e.addEventListener('click',function(e){{e.preventDefault();var t=document.querySelector(this.getAttribute('href'));if(t)t.scrollIntoView({{behavior:'smooth',block:'start'}})}})}})}});'''

    return f'''<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — {esc(report_title)}</title>
<style>{css}</style>
</head>
<body>
<button id="theme-toggle" class="theme-toggle" aria-label="{toggle_dark}">🌙</button>
<div class="app-container">{toc_html}{content_html}</div>
<script>{js}</script>
</body>
</html>'''


def _render_bullets_html(bullets, fmt_func):
    """Render nested bullet lists from flat (level, text) items.
    Supports both dict items ({'text':..., 'level':...}) and legacy str items (level=0)."""
    if not bullets:
        return ''
    parts = []
    prev_level = 0
    first = True
    for item in bullets:
        text = str(item['text']) if isinstance(item, dict) else str(item)
        level = item.get('level', 0) if isinstance(item, dict) else 0
        if first:
            parts.append('<ul>\n')
            parts.append(f'<li>{fmt_func(text)}')
            prev_level = level
            first = False
            continue
        if level > prev_level:
            parts.append('\n<ul>\n' * (level - prev_level))
            parts.append(f'<li>{fmt_func(text)}')
        elif level == prev_level:
            parts.append(f'</li>\n<li>{fmt_func(text)}')
        else:
            parts.append('</li>\n</ul>\n' * (prev_level - level))
            parts.append(f'</li>\n<li>{fmt_func(text)}')
        prev_level = level
    parts.append('</li>\n')
    parts.append('</ul>\n' * (prev_level + 1))
    return ''.join(parts)


def _render_section_html(section, sec_id, fmt, lang, depth=0, esc=None):
    """Render a section dict as HTML."""
    parts = []
    sec_title = section.get('title', '')
    tag = 'h2' if depth == 0 else 'h3' if depth == 1 else 'h4'
    if sec_title:
        parts.append(f'<{tag} id="{sec_id}">{fmt(sec_title)}</{tag}>')

    for p in section.get('paragraphs', []):
        parts.append(f'<p>{fmt(p)}</p>')

    for q in section.get('quotes', []):
        parts.append(f'<blockquote>{fmt(q)}</blockquote>')

    parts.append(_render_bullets_html(section.get('bullets', []), fmt))

    contribs = section.get('contributions', [])
    if contribs:
        contribs_html = []
        for ci, c in enumerate(contribs, 1):
            claim = c.get('claim', '')
            evid = c.get('evidence_ref', '')
            ch = f'<span class="contrib-number">{ci}.</span><blockquote>{fmt(claim)}</blockquote>'
            if evid:
                ch += f'<p class="contrib-evidence"><strong>Evidence:</strong> {fmt(evid)}</p>'
            contribs_html.append(f'<div class="contribution">{ch}</div>')
        parts.append(f'<div class="contrib-block">{"".join(contribs_html)}</div>')

    exps = section.get('experiments', [])
    for exp in exps:
        name = exp.get('name', '')
        para = exp.get('paragraph', '')
        exp_parts = []
        if name:
            exp_parts.append(f'<div class="exp-name">{fmt(name)}</div>')
        if para:
            exp_parts.append(f'<p>{fmt(para)}</p>')
        field_defs = {
            'what':       ('What it did',         '做了什么'),
            'question':   ('Question it answers', '验证的问题'),
            'setup':      ('Setup',               '实验设置'),
            'results':    ('Results',             '结果'),
            'conclusion': ('Conclusion',          '结论'),
        }
        label_idx = 0 if lang == 'en' else 1
        fhtml = ''
        for key, (en, zh) in field_defs.items():
            val = exp.get(key, '')
            if val:
                label = en if lang == 'en' else zh
                formatted = fmt(val).replace('\n', '<br/>')
                fhtml += f'<p><strong>{esc(label)}:</strong> {formatted}</p>'
        ev = exp.get('evidence', '')
        if ev:
            ev_label = 'Evidence strength' if lang == 'en' else '证据强度'
            ev_lower = ev.strip().lower()
            if ev_lower in ('strong', '强'):
                badge = f'<span class="evidence-badge evidence-strong">{esc(ev)}</span>'
            elif ev_lower in ('moderate', '中等'):
                badge = f'<span class="evidence-badge evidence-moderate">{esc(ev)}</span>'
            elif ev_lower in ('weak', '弱'):
                badge = f'<span class="evidence-badge evidence-weak">{esc(ev)}</span>'
            else:
                badge = esc(ev)
            fhtml += f'<p><strong>{esc(ev_label)}:</strong> {badge}</p>'
        if fhtml:
            exp_parts.append(f'<div class="exp-fields">{fhtml}</div>')
        parts.append(f'<div class="experiment-card">{"".join(exp_parts)}</div>')

    tables = section.get('tables', [])
    for t in tables:
        headers = t.get('headers', [])
        rows = t.get('rows', [])
        if headers:
            hrow = ''.join(f'<th>{esc(h)}</th>' for h in headers)
            brows = ''
            for row in rows:
                cells = ''.join(
                    f'<td>{fmt(cell) if isinstance(cell, str) else fmt(str(cell))}</td>'
                    for cell in row[:len(headers)]
                )
                brows += f'<tr>{cells}</tr>'
            parts.append(f'<table><thead><tr>{hrow}</tr></thead><tbody>{brows}</tbody></table>')

    lims = section.get('limitation_items', [])
    if lims:
        lh1 = 'Limitation' if lang == 'en' else '局限性'
        lh2 = 'Acknowledged' if lang == 'en' else '作者是否承认'
        lh3 = 'Severity' if lang == 'en' else '严重程度'
        lrows = ''.join(
            f'<tr><td>{fmt(lim.get("text", ""))}</td>'
            f'<td>{esc(lim.get("acknowledged", ""))}</td>'
            f'<td>{esc(lim.get("severity", ""))}</td></tr>'
            for lim in lims
        )
        parts.append(
            f'<table class="limitation-table">'
            f'<thead><tr><th>{lh1}</th><th>{lh2}</th><th>{lh3}</th></tr></thead>'
            f'<tbody>{lrows}</tbody></table>'
        )

    qitems = section.get('quality_items', [])
    if qitems:
        qhtml = ''.join(
            f'<p><strong>{fmt(qi.get("label", ""))}:</strong> {fmt(qi.get("text", ""))}</p>'
            for qi in qitems
        )
        parts.append(f'<div class="quality-items">{qhtml}</div>')

    subs = section.get('subsections', [])
    for sub in subs:
        sub_id = f'{sec_id}-sub-{subs.index(sub)}'
        parts.append(_render_section_html(sub, sub_id, fmt, lang, depth + 1, esc=esc))

    return f'<section id="{sec_id}">{"".join(parts)}</section>'


def build_report(md_text, output='pdf', lang='zh', mode='standard', output_dir=None):
    """Unified entry point: parse Markdown and render to MD/PDF/JSON/HTML."""
    # Language compliance check on raw Markdown input
    _check_language_compliance(md_text, lang)

    # Import parser here to avoid circular dependency
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'md_to_report',
        os.path.join(os.path.dirname(__file__), 'md_to_report.py'))
    md_parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(md_parser)
    analysis_data = md_parser.md_to_report(md_text)

    # Run gate check before rendering — raise on failure
    _gate_check(analysis_data, lang=lang)

    if output == 'console':
        return render_console(analysis_data, lang)
    elif output == 'json':
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'analysis_result')
        os.makedirs(output_dir, exist_ok=True)
        safe_title = analysis_data.get('title', 'paper')
        safe_title = '_'.join(safe_title.split())[:80]
        for ch in ':/\\?%*|"<>':
            safe_title = safe_title.replace(ch, '_')
        json_path = os.path.join(output_dir, f'{safe_title}_analysis.json')
        return render_json(analysis_data, json_path)
    elif output == 'pdf':
        return build_pdf(analysis_data, output_dir=output_dir, lang=lang)
    elif output == 'md':
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'analysis_result')
        os.makedirs(output_dir, exist_ok=True)
        safe_title = analysis_data.get('title', 'paper')
        safe_title = '_'.join(safe_title.split())[:80]
        for ch in ':/\\?%*|"<>':
            safe_title = safe_title.replace(ch, '_')
        md_path = os.path.join(output_dir, f'{safe_title}_analysis.md')
        if os.path.exists(md_path):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            md_path = os.path.join(output_dir, f'{safe_title}_{ts}_analysis.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        return md_path
    elif output == 'html':
        html_content = render_html(analysis_data, lang=lang)
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'analysis_result')
        os.makedirs(output_dir, exist_ok=True)
        safe_title = analysis_data.get('title', 'paper')
        safe_title = '_'.join(safe_title.split())[:80]
        for ch in ':/\\?%*|"<>':
            safe_title = safe_title.replace(ch, '_')
        html_path = os.path.join(output_dir, f'{safe_title}_Analysis_Report.html')
        if os.path.exists(html_path):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_path = os.path.join(output_dir, f'{safe_title}_{ts}_Analysis_Report.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_path
    else:
        raise ValueError(f"Unknown output format: {output}")
