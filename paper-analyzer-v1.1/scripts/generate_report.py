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
        prefix = '&bull; ' if not b.strip().startswith('&bull;') else ''
        story.append(Paragraph(prefix + _md_to_xml(b), styles['BulletStyle']))

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
            lines.append(f'  - {b}')

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


def build_report(md_text, output='console', lang='zh', mode='standard', output_dir=None):
    """Unified entry point: parse Markdown and render to console/PDF/JSON.

    Args:
        md_text: Markdown string with YAML frontmatter
        output: 'console' | 'pdf' | 'json'
        lang: 'zh' | 'en'
        mode: 'quick' | 'standard' | 'deep'
        output_dir: required for pdf/json output

    Returns:
        console: str (formatted text)
        pdf: str (file path)
        json: str (file path)
    """
    # Import parser here to avoid circular dependency
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'md_to_report',
        os.path.join(os.path.dirname(__file__), 'md_to_report.py'))
    md_parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(md_parser)
    analysis_data = md_parser.md_to_report(md_text)

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
    else:
        raise ValueError(f"Unknown output format: {output}")
