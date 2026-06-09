"""Convert structured Markdown to analysis_data dict for build_pdf().
v2: Schema-driven. Uses section titles to determine type instead of guessing.
Usage: md_to_report(md_text) -> analysis_data dict"""
import re
import json
import os

# Load schema once at module level
_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schema', 'analysis_schema.json')
with open(_SCHEMA_PATH, 'r', encoding='utf-8') as _f:
    _SCHEMA = json.load(_f)

# Build title -> dimension_id mapping (fuzzy match: schema title is substring of section title)
_TITLE_TO_DIM = {}
_DIM_TO_SPEC = {}
for dim_id, spec in _SCHEMA['dimensions'].items():
    _DIM_TO_SPEC[dim_id] = spec
    for key in ('title_zh', 'title_en'):
        title = spec.get(key, '')
        if title:
            _TITLE_TO_DIM[title.lower()] = dim_id


def _match_section_type(section_title):
    """Match a section title to a schema dimension ID.
    Returns (dim_id, spec) or (None, None)."""
    lower = section_title.lower()
    # 1. Exact match against canonical titles
    for title, dim_id in _TITLE_TO_DIM.items():
        if title == lower:
            return dim_id, _DIM_TO_SPEC[dim_id]
    # 2. Canonical title is substring of section title
    for title, dim_id in _TITLE_TO_DIM.items():
        if title in lower:
            return dim_id, _DIM_TO_SPEC[dim_id]
    # 3. Schema ID appears in section title
    for dim_id, spec in _DIM_TO_SPEC.items():
        if dim_id.lower() in lower:
            return dim_id, spec
    return None, None


def _is_table_line(line):
    stripped = line.strip()
    return stripped.startswith('|') and stripped.endswith('|')


def _is_bullet_line(line):
    stripped = line.strip()
    return stripped.startswith(('- ', '* ', '+ ', '– ', '— '))

def _get_bullet_level(line):
    """Return indentation level (0-based) of a bullet line. 2 spaces = 1 level."""
    leading = len(line) - len(line.lstrip())
    return leading // 2


def _parse_table(lines, start_idx):
    """Parse a Markdown table."""
    headers = [h.strip() for h in lines[start_idx].strip().strip('|').split('|')]
    # Skip separator if present
    idx = start_idx + 1
    if idx < len(lines):
        sep = lines[idx].strip()
        if re.match(r'^\|[\s\-:|\s]+\|$', sep):
            idx = start_idx + 2
    rows = []
    while idx < len(lines) and _is_table_line(lines[idx]):
        row = [c.strip() for c in lines[idx].strip().strip('|').split('|')]
        rows.append(row)
        idx += 1
    return headers, rows, idx


def _adjust_col_widths(headers, rows):
    """Estimate column widths."""
    n = len(headers)
    if n == 0:
        return None
    all_rows = [headers] + rows
    max_lens = [max(len(str(r[i]) if i < len(r) else '') for r in all_rows) for i in range(n)]
    total = sum(max_lens)
    if total == 0:
        return None
    avail = 145  # mm
    return [max(20, int(avail * l / total)) for l in max_lens]


def md_to_report(md_text):
    """Parse structured Markdown into analysis_data dict."""
    lines = md_text.split('\n')
    meta = {'title': '', 'authors': '', 'affiliations': '', 'meta_items': []}

    # Parse YAML frontmatter
    if lines and lines[0].strip() == '---':
        end = 1
        while end < len(lines) and lines[end].strip() != '---':
            end += 1
        if end < len(lines):
            for line in lines[1:end]:
                m = re.match(r'([\w-]+):\s*(.+)', line)
                if m:
                    key, val = m.group(1).strip(), m.group(2).strip()
                    if key in ('title', 'authors', 'affiliations'):
                        meta[key] = val
                    elif key == 'code':
                        meta['meta_items'].append(('Code', val))
                    elif key == 'arxiv':
                        meta['meta_items'].append(('ArXiv', val))
            lines = lines[end+1:]

    sections = []
    current_section = None
    current_dim = None
    current_spec = None
    section_id = None
    i = 0
    para_buffer = []
    bullet_buffer = []
    table_buffer = []
    experiment_buffer = []
    contribution_buffer = []
    limitation_buffer = []
    quality_buffer = []
    subsections = []
    current_sub = None
    sub_para_buffer = []
    sub_bullet_buffer = []
    current_subsub = None
    subsub_para_buffer = []

    def _flush_subsub():
        nonlocal subsub_para_buffer
        if current_subsub is not None:
            if subsub_para_buffer:
                current_subsub['paragraphs'] = subsub_para_buffer
                subsub_para_buffer = []
            current_sub.setdefault('subsections', []).append(current_subsub)

    def _flush_sub():
        nonlocal sub_para_buffer, sub_bullet_buffer
        _flush_subsub()
        if current_sub is not None:
            if sub_para_buffer:
                current_sub['paragraphs'] = sub_para_buffer
                sub_para_buffer = []
            if sub_bullet_buffer:
                current_sub['bullets'] = sub_bullet_buffer
                sub_bullet_buffer = []
            subsections.append(current_sub)

    def _flush_section():
        nonlocal para_buffer, bullet_buffer, table_buffer, section_id
        nonlocal experiment_buffer, contribution_buffer, limitation_buffer, quality_buffer
        nonlocal subsections, current_sub, sub_para_buffer, sub_bullet_buffer
        nonlocal current_subsub, subsub_para_buffer
        if current_section is not None:
            _flush_sub()
            if para_buffer:
                current_section['paragraphs'] = para_buffer
                para_buffer = []
            if bullet_buffer:
                current_section['bullets'] = bullet_buffer
                bullet_buffer = []
            if table_buffer:
                current_section['tables'] = table_buffer
                table_buffer = []
            if experiment_buffer:
                current_section['experiments'] = experiment_buffer
                experiment_buffer = []
            if contribution_buffer:
                current_section['contributions'] = contribution_buffer
                contribution_buffer = []
            if limitation_buffer:
                current_section['limitation_items'] = limitation_buffer
                limitation_buffer = []
            if quality_buffer:
                current_section['quality_items'] = quality_buffer
                quality_buffer = []
            if subsections:
                current_section['subsections'] = subsections
                subsections = []
            if section_id:
                current_section['schema_id'] = section_id
            sections.append(current_section)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # ### Subsection (may also be an Experiment heading)
        if stripped.startswith('### '):
            title = stripped[4:].strip()
            # Experiment heading: "### Experiment N: Name" or "### 实验 N: Name"
            if (re.match(r'^[Ee]xperiment\b', title)
                    or re.match(r'^实验\s*\d', title)
                    or re.match(r'^实验\s*[：:]', title)):
                _flush_sub()
                experiment_buffer.append({
                    'name': title,
                    'paragraph': '', 'what': '', 'question': '',
                    'setup': '', 'results': '', 'conclusion': '', 'evidence': ''
                })
            else:
                _flush_sub()
                current_sub = {'title': title, 'paragraphs': []}
                sub_para_buffer = []
                sub_bullet_buffer = []
                current_subsub = None
                subsub_para_buffer = []
            i += 1
            continue

        # #### Sub-subsection
        if stripped.startswith('#### '):
            _flush_subsub()
            title = stripped[5:].strip()
            if current_sub is not None:
                current_subsub = {'title': title, 'paragraphs': []}
                subsub_para_buffer = []
            else:
                # No current_sub: treat as subsection
                _flush_sub()
                current_sub = {'title': title, 'paragraphs': []}
                sub_para_buffer = []
                sub_bullet_buffer = []
            i += 1
            continue

        # ## Section (schema-driven)
        if stripped.startswith('## '):
            _flush_section()
            title = stripped[3:].strip()
            # Remove leading emoji if present
            title = re.sub(r'^[\U0001F300-\U0001F9FF]\s*', '', title).strip()
            current_section = {'title': title}
            section_id, section_spec = _match_section_type(title)
            current_dim = section_id
            current_spec = section_spec
            para_buffer = []
            bullet_buffer = []
            table_buffer = []
            experiment_buffer = []
            contribution_buffer = []
            limitation_buffer = []
            quality_buffer = []
            subsections = []
            current_sub = None
            sub_para_buffer = []
            sub_bullet_buffer = []
            current_subsub = None
            subsub_para_buffer = []
            i += 1
            continue

        # Contribution: 1. **"quote"** or 1. **title**desc
        contrib_match = re.match(r'(\d+)\.\s+\*\*"(.+?)"\*\*', stripped)
        if not contrib_match:
            contrib_match = re.match(r'(\d+)\.\s+\*\*(.+?)\*\*', stripped)
        if contrib_match:
            claim = contrib_match.group(2).strip()
            evid = ''
            inline_ev = re.search(r'[Ee]vidence:\s*(.+)', stripped)
            if inline_ev:
                evid = inline_ev.group(1).strip()
            else:
                j = i + 1
                while j < len(lines):
                    ns = lines[j].strip()
                    if ns.startswith('## ') or ns.startswith('### ') or ns.startswith('#### ') or re.match(r'\d+\.\s+\*\*', ns):
                        break
                    evid_line = ns
                    if _is_bullet_line(evid_line):
                        evid_line = evid_line[2:].strip()
                    if evid_line.lower().startswith('evidence'):
                        evid = evid_line.split(':', 1)[-1].strip()
                        break
                    j += 1
            # Skip consumed evidence lines to avoid duplication into paragraphs
            if evid:
                i = j
            contribution_buffer.append({'claim': claim, 'evidence_ref': evid})
            i += 1
            continue

        # Experiment: **Experiment: Name**
        exp_match = re.match(r'\*\*Experiment:\s*(.+?)\*\*', stripped)
        if exp_match:
            experiment_buffer.append({
                'name': exp_match.group(1).strip(),
                'paragraph': '', 'what': '', 'question': '',
                'setup': '', 'results': '', 'conclusion': '', 'evidence': ''
            })
            i += 1
            continue

        # Experiment narrative paragraph: text between **Experiment: Name** and first **field:**
        if experiment_buffer:
            exp = experiment_buffer[-1]
            if (not re.match(r'\*\*(.+?):\*\*', stripped)
                    and not stripped.startswith('#')
                    and not _is_bullet_line(stripped)
                    and not _is_table_line(stripped)):
                if exp['paragraph']:
                    exp['paragraph'] += ' ' + stripped
                else:
                    exp['paragraph'] = stripped
                i += 1
                continue

        # Experiment field: **label:** value
        if experiment_buffer:
            exp = experiment_buffer[-1]
            fld_match = re.match(r'\*\*(.+?):\*\*\s*(.*)', stripped)
            if fld_match:
                label = fld_match.group(1).strip()
                val = fld_match.group(2).strip()
                key_map = {
                    'What it did': 'what', '做了什么': 'what',
                    'Question it answers': 'question', '验证的问题': 'question',
                    'Setup': 'setup', '实验设置': 'setup',
                    'Results': 'results', '结果': 'results',
                    'Conclusion': 'conclusion', '结论': 'conclusion',
                    'Evidence strength': 'evidence', '证据强度': 'evidence',
                }
                if label in key_map:
                    field_key = key_map[label]
                    exp[field_key] = val
                    i += 1
                    # Accumulate subsequent bullet/paragraph content into this field
                    while i < len(lines):
                        nxt = lines[i].strip()
                        if not nxt:
                            i += 1
                            continue
                        if re.match(r'\*\*(.+?):\*\*', nxt):
                            break
                        if nxt.startswith('## ') or nxt.startswith('### ') or nxt.startswith('#### '):
                            break
                        accumulated = nxt[2:].strip() if _is_bullet_line(nxt) else nxt
                        if exp[field_key]:
                            exp[field_key] += '\n' + accumulated
                        else:
                            exp[field_key] = accumulated
                        i += 1
                    continue
                if label.lower() == 'evidence':
                    exp['evidence'] = val
                    i += 1
                    continue

        # Table: schema-driven behavior
        if _is_table_line(stripped):
            headers, rows, next_i = _parse_table(lines, i)
            # Use schema type to decide how to parse the table
            if current_dim == 'limitations':
                for row in rows:
                    if len(row) >= 3:
                        limitation_buffer.append({
                            'text': row[0], 'acknowledged': row[1], 'severity': row[2]
                        })
            else:
                table_buffer.append({'headers': headers, 'rows': rows,
                                     'col_widths': _adjust_col_widths(headers, rows)})
            i = next_i
            continue

        # Bullet: schema-driven behavior; route to subsection if inside one
        if _is_bullet_line(stripped):
            text = stripped[2:].strip()
            level = _get_bullet_level(line)
            bullet_item = {'text': text, 'level': level}
            if current_dim == 'quality_assessment':
                if '\uff1a' in text:
                    label, _, rest = text.partition('\uff1a')
                else:
                    label, _, rest = text.partition(':')
                quality_buffer.append({
                    'label': label.strip().strip('*').strip(),
                    'text': rest.lstrip('*').strip()
                })
            elif current_sub is not None:
                sub_bullet_buffer.append(bullet_item)
            else:
                bullet_buffer.append(bullet_item)
            i += 1
            continue

        # General text → paragraph buffer (subsub > sub > section)
        if current_subsub is not None:
            subsub_para_buffer.append(stripped)
        elif current_sub is not None:
            sub_para_buffer.append(stripped)
        else:
            para_buffer.append(stripped)
        i += 1

    _flush_section()

    return {
        'title': meta['title'],
        'authors': meta['authors'],
        'affiliations': meta['affiliations'],
        'meta_items': meta['meta_items'],
        'sections': sections,
    }
