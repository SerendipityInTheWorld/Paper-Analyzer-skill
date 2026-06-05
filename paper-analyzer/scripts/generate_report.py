"""Generate paper analysis PDF report using reportlab."""
import os
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Table, TableStyle, Image, KeepTogether, Flowable)
from reportlab.pdfbase import pdfmetrics

# Temp directory for intermediate files (cleaned up after PDF generation)
TEMP_DIR = tempfile.mkdtemp(prefix='paper_analyzer_')

# Colors
DARK_BLUE = HexColor('#2C3E50')
MEDIUM_BLUE = HexColor('#34495E')
ACCENT_BLUE = HexColor('#3498DB')
LIGHT_GRAY = HexColor('#ECF0F1')
MED_GRAY = HexColor('#7F8C8D')
TEXT_COLOR = HexColor('#2C3E50')
QUOTE_COLOR = HexColor('#7F8C8D')


def draw_experiment_flowchart():
    """Create experimental framework flowchart using matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    colors = {
        'scale': '#4A90D9',
        'task': '#50B86C',
        'control': '#E8833A',
        'question': '#9B59B6'
    }

    def draw_box(x, y, w, h, text, color, fontsize=8, text_color='white'):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor='none', alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=fontsize, color=text_color, fontweight='bold')

    def draw_arrow(x1, y1, x2, y2, color='gray'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

    ax.text(5, 6.7, 'AutoFocusFormer: Experimental Framework Overview',
            ha='center', va='center', fontsize=13, fontweight='bold', color='#2C3E50')

    draw_box(0.3, 4.8, 2.5, 0.6, 'Scale Variations', colors['scale'], 9)
    for i, (y, label) in enumerate([
        (3.8, 'AFF-Mini (6.75M)'), (3.0, 'AFF-Tiny (27M)'),
        (2.2, 'AFF-Small (42.6M)'), (1.4, 'AFF-Base (75.3M)'),
        (0.5, '1/5 Downsample Rate')
    ]):
        draw_box(0.5, y, 2.1, 0.5, label, colors['scale'], 7)

    tasks = [
        (4.0, 5.2, 'ImageNet-1K\nClassification'),
        (4.0, 3.8, 'ADE20K\nSemantic Seg.'),
        (4.0, 2.7, 'Cityscapes\nInstance+Panoptic'),
        (4.0, 1.6, 'COCO 2017\nInstance Seg.')
    ]
    for x, y, t in tasks:
        draw_box(x, y, 2.5, 0.8, t, colors['task'], 7)
    for y in [5.2, 3.8, 2.7, 1.6]:
        draw_arrow(2.9, 5.1, 3.9, y + 0.4)

    controls = [
        (7.2, 5.2, 'Ablation\n(per component)'),
        (7.2, 3.8, 'Alpha\nHyperparameter'),
        (7.2, 2.7, 'Head\nModification'),
    ]
    for x, y, t in controls:
        draw_box(x, y, 2.3, 0.8, t, colors['control'], 7)
    for y in [5.2, 3.8, 2.7]:
        draw_arrow(6.6, y + 0.4, 7.1, y + 0.4)

    questions = [
        ('0.5', 'Does adaptive\nbackbone work\nfor classification?'),
        ('3.5', 'Does it help\ndense prediction?'),
        ('6.0', 'Does it help\nsmall objects?'),
        ('8.0', 'Design choices\nvalidated?')
    ]
    for i, (x, q) in enumerate(questions):
        draw_box(float(x), -0.4, 2.5, 0.5, q, colors['question'], 6)

    plt.tight_layout()
    path = os.path.join(TEMP_DIR, 'experiment_flowchart.png')
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


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


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'TitlePage', fontName='Helvetica', fontSize=26, leading=32,
        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6*mm))
    styles.add(ParagraphStyle(
        'SubTitle', fontName='Helvetica', fontSize=14, leading=18,
        textColor=MEDIUM_BLUE, alignment=TA_CENTER, spaceAfter=3*mm))
    styles.add(ParagraphStyle(
        'AuthorLine', fontName='Helvetica', fontSize=10, leading=14,
        textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=2*mm))
    styles.add(ParagraphStyle(
        'SectionTitle', fontName='Helvetica-Bold', fontSize=16, leading=22,
        textColor=DARK_BLUE, spaceBefore=6*mm, spaceAfter=3*mm))
    styles.add(ParagraphStyle(
        'SubSectionTitle', fontName='Helvetica-Bold', fontSize=13, leading=18,
        textColor=MEDIUM_BLUE, spaceBefore=4*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle(
        'SubSubSectionTitle', fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=MEDIUM_BLUE, spaceBefore=3*mm, spaceAfter=1*mm))
    styles.add(ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=10, leading=14,
        textColor=TEXT_COLOR, alignment=TA_JUSTIFY, spaceAfter=2*mm))
    styles.add(ParagraphStyle(
        'BulletStyle', fontName='Helvetica', fontSize=10, leading=14,
        textColor=TEXT_COLOR, leftIndent=8*mm, spaceAfter=1*mm))
    styles.add(ParagraphStyle(
        'Quote', fontName='Helvetica-Oblique', fontSize=9, leading=13,
        textColor=QUOTE_COLOR, leftIndent=12*mm, rightIndent=12*mm,
        spaceBefore=1*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle(
        'TableCell', fontName='Helvetica', fontSize=8, leading=10,
        textColor=TEXT_COLOR, alignment=TA_CENTER))
    styles.add(ParagraphStyle(
        'TableHeader', fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=white, alignment=TA_CENTER))
    return styles


def make_table(data, col_widths=None):
    s = getSampleStyleSheet()
    cell_style = ParagraphStyle('Cell', fontName='Helvetica', fontSize=8, leading=10,
                                 textColor=TEXT_COLOR, alignment=TA_CENTER)
    header_style = ParagraphStyle('HCell', fontName='Helvetica-Bold', fontSize=8, leading=10,
                                   textColor=white, alignment=TA_CENTER)
    table_data = []
    for i, row in enumerate(data):
        if i == 0:
            table_data.append([Paragraph(c, header_style) for c in row])
        else:
            table_data.append([Paragraph(str(c), cell_style) for c in row])

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GRAY))
    t.setStyle(TableStyle(style_cmds))
    return t


LANG = 'en'  # default; override with lang='zh' for Chinese


def set_language(lang):
    global LANG
    LANG = lang


def _(en_text, zh_text=None):
    """Return text in active language."""
    if LANG == 'zh' and zh_text is not None:
        return zh_text
    return en_text


def build_pdf(output_dir=None, lang='en'):
    set_language(lang)
    flowchart_path = draw_experiment_flowchart()
    styles = build_styles()

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), 'analysis_result')
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, 'AutoFocusFormer_Image_Segmentation_off_the_Grid_Analysis_Report.pdf')

    doc = SimpleDocTemplate(pdf_path,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    story = []
    S = styles

    # ========== Title Page ==========
    story.append(Spacer(1, 50*mm))
    story.append(Paragraph(_('Paper Analysis Report', '论文分析报告'), S['TitlePage']))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        'AutoFocusFormer: Image Segmentation off the Grid', S['SubTitle']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('CVPR 2023 | arXiv: 2304.12406', S['AuthorLine']))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        'Chen Ziwen, Kaushik Patnaik, Shuangfei Zhai, Alvin Wan,<br/>'
        'Zhile Ren, Alex Schwing, Alex Colburn, Li Fuxin', S['AuthorLine']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        _('Oregon State University / Apple Inc.'), S['AuthorLine']))
    story.append(Paragraph(
        'Code: github.com/apple/ml-autofocusformer', S['AuthorLine']))
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph(
        _('Generated by Paper Analyzer Skill', '由 Paper Analyzer Skill 生成'), ParagraphStyle(
            'FooterNote', parent=S['AuthorLine'], fontSize=9, textColor=HexColor('#AAAAAA'))))
    story.append(PageBreak())

    # ========== 1. Metadata ==========
    story.append(Paragraph(_('1. Metadata', '1. 元数据'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    story.append(Spacer(1, 2*mm))
    meta_items = [
        ('Title', 'AutoFocusFormer: Image Segmentation off the Grid'),
        ('Authors', 'Chen Ziwen, Kaushik Patnaik, Shuangfei Zhai, Alvin Wan, Zhile Ren, Alex Schwing, Alex Colburn, Li Fuxin'),
        ('Affiliations', 'Oregon State University, Apple Inc.'),
        ('Venue', 'CVPR 2023, pp. 18227-18236'),
        ('arXiv', '2304.12406'),
        ('Code', 'https://github.com/apple/ml-autofocusformer'),
    ]
    for label, value in meta_items:
        story.append(Paragraph(f'<b>{label}:</b> {value}', S['Body']))

    # ========== 2. Research Motivation ==========
    story.append(PageBreak())
    story.append(Paragraph(_('2. Research Motivation', '2. 研究动机'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph(
        'Real-world images exhibit highly imbalanced content density. In a typical outdoor scene, '
        'large swaths of textureless regions (sky, ground) coexist with areas containing many small, '
        'detailed objects. However, most computer vision neural networks (CNNs and hierarchical '
        'Transformers alike) distribute computation uniformly across the image plane.', S['Body']))

    story.append(Paragraph(
        'Convolutional neural networks operate on regularly-arranged square patches with successive '
        'grid downsampling (stride convolution, pooling). Even transformer-based methods like Swin '
        'adopt grid-based techniques such as stride-16 convolutions and 7x7 square attention windows. '
        'The result: uniform downsampling makes small objects even smaller, potentially dropping '
        'pixel-level information critical for segmentation tasks.', S['Body']))

    story.append(Paragraph('Existing countermeasures are inadequate:', S['Body']))
    story.append(Paragraph(
        '&bull; Increasing input resolution (e.g., SPINet, Simple Training Strategies) is a brute-force '
        'approach that helps but at prohibitive memory/computation cost.', S['BulletStyle']))
    story.append(Paragraph(
        '&bull; Irregular point sampling in decoders (e.g., PointRend) cannot circumvent the '
        'uniformly-downsampled encoder\'s inherent limitations.', S['BulletStyle']))

    story.append(Paragraph(
        '<b>Key insight:</b> if the model could retain more pixels in "informative" areas (cluttered small '
        'objects, boundaries) while aggressively summarizing "unimportant" areas (uniform sky, road), '
        'it would preserve critical information without increasing resolution. This requires a '
        'fundamentally different downsampling strategy &ndash; one that is adaptive, non-uniform, and '
        'end-to-end learnable.', S['Body']))

    # ========== 3. Problem Definition ==========
    story.append(PageBreak())
    story.append(Paragraph(_('3. Problem Definition', '3. 问题定义'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph('3.1 Core Contradiction', S['SubSectionTitle']))
    story.append(Paragraph(
        'Image content is non-uniform by nature, but existing backbones allocate computation uniformly. '
        'This mismatch disproportionately harms small objects in dense prediction tasks like segmentation.',
        S['Body']))

    story.append(Paragraph('3.2 Key Challenges', S['SubSectionTitle']))

    challenges = [
        ('Challenge 1: Non-uniform downsampling breaks grid structure',
         'Existing architectures rely on rectangular grids. Adaptive sampling produces '
         'irregularly-distributed tokens with no natural grid topology.',
         '"Non-uniform downsampling breaks from the grid structure that existing architectures rely on."'),
        ('Challenge 2: Global attention cannot scale to segmentation',
         'Prior adaptive downsampling work uses global attention, which has quadratic complexity '
         'and cannot handle high-resolution segmentation inputs.',
         '"Global attention does not scale to resolutions much higher than that of ImageNet."'),
        ('Challenge 3: No natural local neighborhoods on irregular points',
         'On a grid, local windows are trivially defined. On irregular points, kNN is O(n\u00b2) '
         'and k-means produces uneven clusters causing padding waste.',
         'Balanced clustering is proposed to address this gap.'),
        ('Challenge 4: Gradient propagation for learnable downsampling',
         'Prior methods resort to heuristics (attention values), policy gradient, or Gumbel-Softmax '
         'to backpropagate through token selection/deletion.',
         '"How to make the adaptive downsampling module learnable has itself been a significant challenge."'),
        ('Challenge 5: Existing methods limited to classification-scale',
         'Most prior adaptive works cannot prune tokens during training or need uniform batch sizes, '
         'restricting them to ImageNet classification.',
         '"They cannot scale to high-resolution segmentation tasks."'),
    ]
    for title, desc, quote in challenges:
        story.append(Paragraph(title, S['SubSubSectionTitle']))
        story.append(Paragraph(desc, S['Body']))
        story.append(Paragraph(quote, S['Quote']))

    # ========== 4. Core Contributions ==========
    story.append(PageBreak())
    story.append(Paragraph(_('4. Core Contributions', '4. 核心贡献'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    contribs = [
        ('Contribution 1: First end-to-end segmentation network with successive adaptive downsampling',
         '"To our knowledge, we introduce the first end-to-end segmentation network with successive '
         'adaptive downsampling stages and with flexible downsampling rates."',
         'Supported by all segmentation experiments (ADE20K, Cityscapes, COCO)'),
        ('Contribution 2: Balanced clustering + learnable neighborhood merging',
         '"To facilitate a local attention transformer on irregularly spaced tokens, we propose a novel '
         'balanced clustering algorithm to group tokens into neighborhoods. We also propose a neighborhood '
         'merging module that enables end-to-end learning of adaptive downsampling."',
         'Supported by ablation studies (Table 5)'),
        ('Contribution 3: Adapted SOTA decoders for irregular point sets',
         '"We adapt state-of-the-art decoders such as deformable DETR, Mask2Former and HCFormer to '
         'operate on irregularly spaced sets of tokens."',
         'Supported by head modification experiments'),
        ('Contribution 4: SOTA results with fewer FLOPs, improved small object recognition',
         '"Results show that our approach achieves state-of-the-art for both image classification and '
         'segmentation with fewer FLOPs, and improves significantly on the recognition of small objects '
         'in instance segmentation tasks."',
         'Supported by all experiments'),
    ]
    for title, quote, evidence in contribs:
        story.append(Paragraph(title, S['SubSectionTitle']))
        story.append(Paragraph(quote, S['Quote']))
        story.append(Paragraph('&bull; Supporting evidence: ' + evidence, S['BulletStyle']))

    # ========== 5. Methodological Innovation ==========
    story.append(PageBreak())
    story.append(Paragraph(_('5. Methodological Innovation', '5. 方法创新'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph('5.1 Overall Architecture', S['SubSectionTitle']))
    story.append(Paragraph(
        'AFF backbone consists of four stages, each processing a successively downsampled set of tokens. '
        'Each stage comprises three components executed in sequence: (1) balanced clustering to define '
        'neighborhoods, (2) several local-attention transformer blocks using those neighborhoods, and '
        '(3) the adaptive downsampling module to select and merge tokens for the next stage.',
        S['Body']))

    story.append(Paragraph('5.2 Balanced Clustering', S['SubSectionTitle']))
    story.append(Paragraph(
        'Design motivation: defining local neighborhoods on irregular points. On grids, slicing windows '
        'is trivial. For unordered points, kNN is O(n\u00b2) and k-means produces uneven clusters. '
        'The solution: a non-iterative, perfectly balanced clustering algorithm operating only '
        'on 2D positions (not feature space) to maintain efficiency.', S['Body']))
    story.append(Paragraph(
        'Algorithm (4 steps):<br/>'
        '(1) Coarse grid quantization &ndash; divide the image into a coarse grid (grid count approximates '
        'desired cluster count); each grid center is a "space-filling anchor."<br/>'
        '(2) Space-filling curve ordering &ndash; a Hilbert/Morton curve establishes 1D order among anchors.<br/>'
        '(3) Distance ratio sorting &ndash; for each token p anchored at a<sub>i</sub>, compute '
        'r(p) = ||p \u2212 a<sub>i\u22121</sub>|| / ||p \u2212 a<sub>i+1</sub>||; '
        'within each anchor, sort tokens by r ascending.<br/>'
        '(4) Equal partition &ndash; all tokens, sorted by anchor order then local r order, are simply '
        'split into equal-sized clusters.<br/><br/>'
        'Time complexity: O(n log n), negligible compared to network forward pass since feature '
        'channels are not involved. Clustering runs once per stage and is shared across all '
        'attention blocks and the downsampling module.', S['Body']))

    story.append(Paragraph('5.3 Local Attention on Clusters', S['SubSectionTitle']))
    story.append(Paragraph(
        'Each token attends to tokens from R nearby clusters (not just its own cluster), mimicking '
        'Swin\'s shifting window strategy but for irregular points. The neighborhood size is several '
        'times the cluster size, ensuring overlapping receptive fields.<br/><br/>'
        'Position encoding: since token positions are unknown beforehand, a learnable function w() '
        '(implemented as one FC layer) maps relative coordinate difference to a scalar position embedding: '
        'P<sub>ij</sub> = w(p<sub>i</sub> \u2212 p<sub>j</sub>).<br/><br/>'
        'Attention: A = softmax(QK<sup>T</sup> + P), identical to standard self-attention but restricted '
        'to neighborhood tokens.', S['Body']))

    story.append(Paragraph('5.4 Adaptive Downsampling (Core Innovation)', S['SubSectionTitle']))
    story.append(Paragraph(
        'This is the paper\'s central technical contribution, comprising two sub-modules:', S['Body']))

    story.append(Paragraph('Learnable Importance Score', S['SubSubSectionTitle']))
    story.append(Paragraph(
        'Each token i predicts a scalar s<sub>i</sub> = \u03c3(l(f<sub>i</sub>)) via a fully-connected '
        'layer l plus sigmoid, indicating its importance to the task loss. The key design challenge is '
        'gradient flow: tokens not selected for merging must still receive gradients. The paper solves '
        'this through the merging mechanism itself &ndash; since every token participates in a weighted '
        'merge (not deletion), gradients flow naturally through the importance-weighting term s<sub>i</sub> '
        'in the PointConv merge operation.', S['Body']))

    story.append(Paragraph('Grid Prior and Token Selection', S['SubSubSectionTitle']))
    story.append(Paragraph(
        'Final score = g<sub>i</sub> + \u03b1 \u00b7 s<sub>i</sub>, where s<sub>i</sub> is the learned '
        'importance score, g<sub>i</sub> is a grid prior preventing collapse in uniform regions, and '
        '\u03b1 balances adaptivity vs. regularity.<br/><br/>'
        '<b>Adaptive Grid Prior (key detail):</b> For irregularly-sampled stages, a regular grid prior '
        'is invalid. Instead, compute local stride t<sub>i</sub> = 2<sup>\u2308log\u2082 min<sub>j</sub> '
        '||p<sub>i</sub> \u2212 p<sub>j</sub>||<sub>1</sub>\u2309</sup>, then '
        'g<sub>i</sub> = 1 if (x<sub>i</sub> mod 2t<sub>i</sub> = 0) AND (y<sub>i</sub> mod 2t<sub>i</sub> = 0). '
        '"Reserved" tokens (coarse grid positions) have g<sub>i</sub> = \u221e, guaranteeing global '
        'connectivity.', S['Body']))

    story.append(Paragraph('Neighborhood Merging (PointConv variant)', S['SubSubSectionTitle']))
    story.append(Paragraph(
        'Selected merging centers aggregate neighbors via a weighted PointConv layer:<br/><br/>'
        'f<sub>merged</sub>(p<sub>c</sub>) = vec( \u03a3 \u03c3(l(f<sub>i</sub>)) \u00b7 '
        'W(p<sub>i</sub> \u2212 p<sub>c</sub>) \u00b7 f<sub>i</sub><sup>T</sup> ) \u00b7 U<br/><br/>'
        'where W() is an MLP producing different weighted feature combinations based on relative '
        'coordinates, l(f<sub>i</sub>) = s<sub>i</sub> modulates neighbor importance, and U is the '
        'output projection. This is equivalent to continuous convolution with learned importance modulation.',
        S['Body']))

    story.append(Paragraph('5.5 Expanded Position Embedding', S['SubSectionTitle']))
    story.append(Paragraph(
        'Standard (\u0394x, \u0394y) relative position encoding fails under scale variation (tokens on small '
        'objects are closer together, producing different embeddings than tokens on large objects). '
        'Solution: expand to:<br/><br/>'
        '(\u0394x, \u0394y, \u221a(\u0394x\u00b2+\u0394y\u00b2), '
        '\u0394x/\u221a(\u0394x\u00b2+\u0394y\u00b2), \u0394y/\u221a(\u0394x\u00b2+\u0394y\u00b2))<br/><br/>'
        'where distance (\u221a) is rotation-invariant, and angle terms (cos, sin) are scale-invariant.',
        S['Body']))

    story.append(Paragraph('5.6 Blank Tokens', S['SubSectionTitle']))
    story.append(Paragraph(
        'Textureless image corners produce abnormally large feature norms because softmax '
        'generates strong gradients when it cannot separate near-identical irrelevant features. '
        'Solution: introduce learnable blank tokens (K<sub>blank</sub>, V<sub>blank</sub>) in each '
        'transformer block. When a neighborhood lacks useful content, softmax attends to the blank '
        'token instead of forcing unnatural attention distributions.', S['Body']))

    story.append(Paragraph('5.7 Point-based Segmentation Heads', S['SubSectionTitle']))
    story.append(Paragraph(
        'Two modifications to adapt Mask2Former and HCFormer for irregular tokens:<br/><br/>'
        '(1) Deformable attention interpolation: replace bilinear interpolation with inverse-distance '
        'weighted interpolation (gather 4 nearest tokens, weight by distance<sup>\u2212power</sup>).<br/>'
        '(2) Replace 3x3 convolutions with PointConv layers (FC \u2192 LayerNorm \u2192 GELU, C<sub>mid</sub> = 4).',
        S['Body']))

    # ========== 6. Experimental Framework ==========
    story.append(PageBreak())
    story.append(Paragraph(_('6. Experimental Framework', '6. 实验框架'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph(
        'The experimental framework spans three datasets, four model sizes, two task types, '
        'and three control axes (ablation, hyperparameter, head modification). The flowchart below '
        'provides an overview of how experiments are organized and what each validates.',
        S['Body']))
    story.append(Image(flowchart_path, width=170*mm, height=120*mm))
    story.append(Spacer(1, 3*mm))

    # 6.1
    story.append(Paragraph('6.1 ImageNet-1K Image Classification', S['SubSectionTitle']))
    story.append(Paragraph(
        '<b>Setup:</b> ImageNet-1K (1.28M train / 50K val, 1000 classes) at 224\u00d7224 resolution. '
        'Four model sizes (Mini/Tiny/Small/Base). Default: 1/4 downsampling, cluster size 8, '
        'neighborhood size 48. Global attention in last stage. Alpha=4. 300 epochs, Swin settings. '
        'Swin baselines retrained identically for fairness.', S['Body']))
    story.append(Paragraph('<b>Question answered:</b> Does adaptive downsampling maintain classification accuracy?', S['Body']))

    t1 = make_table([
        ['Model', 'Top-1 Acc', 'Params', 'FLOPs', 'vs Swin'],
        ['Swin-Mini', '76.9%', '6.76M', '1.07G', 'baseline'],
        ['AFF-Mini', '78.2%', '6.75M', '1.08G', '+1.3%'],
        ['Swin-Tiny', '81.9%', '27M', '4G', 'baseline'],
        ['AFF-Tiny', '83.0%', '27M', '4G', '+1.1%'],
        ['Swin-Small', '82.9%', '42.6M', '8.14G', 'baseline'],
        ['AFF-Small', '83.5%', '42.6M', '8.16G', '+0.5%'],
    ], [35*mm, 22*mm, 22*mm, 22*mm, 35*mm])
    story.append(t1)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph('Evidence strength: <b>Strong</b> &ndash; multi-scale, fair controls, transparent FLOPs.', S['Body']))

    # 6.2
    story.append(PageBreak())
    story.append(Paragraph('6.2 ADE20K Semantic Segmentation', S['SubSectionTitle']))
    story.append(Paragraph(
        '<b>Setup:</b> ADE20K (150 classes, 20K/2K). Mask2Former head modified for point cloud. '
        '512\u00d7512 crop. Both 1/4 and 1/5 rates evaluated.', S['Body']))
    story.append(Paragraph('<b>Question answered:</b> Does adaptive downsampling improve dense prediction?', S['Body']))

    t2 = make_table([
        ['Backbone', 'mIoU', 'FLOPs', 'Improvement'],
        ['Swin-Mini', '44.5', '54G', 'baseline'],
        ['AFF-Mini', '46.5', '48.3G', '+2.0, \u221211% FLOPs'],
        ['AFF-Mini-1/5', '46.0', '39.9G', '+1.5, \u221226% FLOPs'],
        ['Swin-Tiny', '47.7', '74G', 'baseline'],
        ['AFF-Tiny', '50.2', '64.6G', '+2.5, \u221213% FLOPs'],
        ['AFF-Tiny-1/5', '50.0', '51.1G', '+2.3, \u221231% FLOPs'],
    ], [35*mm, 20*mm, 22*mm, 55*mm])
    story.append(t2)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph('Evidence strength: <b>Strong</b> &ndash; consistent across sizes; 1/5 saves 20-31% FLOPs.', S['Body']))

    # 6.3
    story.append(Paragraph('6.3 Cityscapes Instance &amp; Panoptic Segmentation', S['SubSectionTitle']))
    story.append(Paragraph(
        '<b>Setup:</b> Cityscapes (19 classes, 2975/500). Evaluates Panoptic PQ + Instance AP. '
        'Cross-scale: AFF-Tiny vs Swin-Base (3.3\u00d7), AFF-Small vs Swin-Large (4.6\u00d7).',
        S['Body']))
    story.append(Paragraph('<b>Question answered:</b> Is adaptive downsampling beneficial for small objects?', S['Body']))

    t3 = make_table([
        ['Backbone', 'Panoptic PQ', 'Instance AP', 'Params', 'Note'],
        ['Swin-Tiny', '63.9', '39.7', '28M', 'baseline'],
        ['AFF-Tiny', '65.7', '42.7', '27M', '+1.8 PQ, +3.0 AP'],
        ['Swin-Small', '64.8', '41.8', '50M', 'baseline'],
        ['AFF-Small', '66.9', '44.0', '42.6M', '+2.1 PQ, +2.2 AP'],
        ['Swin-Base\u2020', '66.1', '42.0', '88M', '3.3\u00d7 AFF-Tiny'],
        ['Swin-Large\u2020', '66.6', '43.7', '197M', '4.6\u00d7 AFF-Small'],
    ], [30*mm, 22*mm, 22*mm, 22*mm, 40*mm])
    story.append(t3)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        '<b>Key finding:</b> Instance AP (+2.2 to +3.0) > PQ (+1.8 to +2.1), confirming '
        'adaptive downsampling is especially impactful for instance-level small objects. '
        'AFF-Tiny matches Swin-Base (3.3\u00d7 smaller); AFF-Small exceeds Swin-Large (4.6\u00d7 smaller).',
        S['Body']))
    story.append(Paragraph('Evidence strength: <b>Strong</b> &ndash; comprehensive metrics, compelling cross-scale.', S['Body']))

    # 6.4
    story.append(Paragraph('6.4 Ablation Studies', S['SubSectionTitle']))
    story.append(Paragraph(
        '<b>Setup:</b> AFF-Mini on ImageNet-1K. Each component removed independently. '
        'Hyperparameter \u03b1 tested across classification and segmentation.', S['Body']))
    story.append(Paragraph('<b>Question answered:</b> What is each component\'s contribution?', S['Body']))

    t4 = make_table([
        ['Variant', 'Top-1 Acc', 'Delta vs Full'],
        ['Full AFF-Mini (1/5)', '77.5%', 'baseline'],
        ['\u2212 Grid Prior', '76.6%', '\u22120.9%'],
        ['\u2212 Expanded Pos. Enc.', '76.6%', '\u22120.9%'],
        ['\u2212 Blank Token', '76.9%', '\u22120.6%'],
        ['\u2212 Reserved Tokens', '77.2%', '\u22120.3%'],
        ['= PatchMerging (Swin)', '77.7%', '\u22120.5% at 1/4'],
    ], [45*mm, 25*mm, 45*mm])
    story.append(t4)
    story.append(Spacer(1, 2*mm))

    t5 = make_table([
        ['\u03b1', 'ImageNet Acc', 'Cityscapes AP'],
        ['2', '78.4%', '37.5'],
        ['4', '78.2%', '38.7'],
        ['8', '\u2014', '40.0'],
    ], [30*mm, 30*mm, 30*mm])
    story.append(t5)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph('Evidence strength: <b>Strong</b> &ndash; all components independently ablated.', S['Body']))

    # ========== 7. Key Results ==========
    story.append(PageBreak())
    story.append(Paragraph(_('7. Key Results', '7. 关键结果'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    key_results = [
        'ImageNet-1K: AFF-Tiny 83.0% (+1.7% vs Swin-Tiny), AFF-Small 83.5% (+0.5%)',
        'ADE20K Semantic Seg.: AFF-Tiny 50.2 mIoU (+2.5% vs Swin-Tiny)',
        'Cityscapes Instance: AFF-Small AP 44.0 (+2.2), AFF-Tiny AP 42.7 (+3.0)',
        'Cross-scale: AFF-Tiny (27M) matches Swin-Base (88M, 3.3\u00d7 larger)',
        'AFF-Small (42.6M) exceeds Swin-Large (197M, 4.6\u00d7 larger)',
        'Efficiency: 1/5 rate saves 20\u201333% FLOPs with minimal accuracy loss (0.2\u20130.7%)',
    ]
    for r in key_results:
        story.append(Paragraph('&bull; ' + r, S['BulletStyle']))

    # ========== 8. Limitations ==========
    story.append(Paragraph(_('8. Limitations', '8. 局限性'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    t6 = make_table([
        ['Limitation', 'Acknowledged', 'Severity'],
        ['Classification gain moderate vs seg.', 'Yes', 'Moderate'],
        ['Only 2D location clustering used', 'Yes', 'Low'],
        ['Feature clustering not fully explored', 'Partial', 'Low'],
        ['Alpha tuning needed per task', 'No', 'Moderate'],
        ['No detection/tracking tasks tested', 'No', 'Moderate'],
        ['No actual inference latency reported', 'No', 'Moderate'],
        ['Ablation only on Mini level', 'No', 'Low'],
    ], [55*mm, 25*mm, 20*mm])
    story.append(t6)

    # ========== 9. Future Work ==========
    story.append(Paragraph(_('9. Future Work', '9. 未来工作'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    story.append(Paragraph(
        '<b>Explicitly suggested:</b> The backbone could inspire models for other tasks that benefit from '
        'the non-grid structure and adaptive focus on important image locations.', S['Body']))
    story.append(Paragraph(
        '<b>Implied but not stated:</b> Object detection, video understanding, medical imaging.', S['Body']))
    story.append(Paragraph(
        '<b>For your own research:</b> The balanced clustering + importance scoring pattern is transferable '
        'to any task requiring adaptive computation allocation.', S['Body']))

    # ========== 10. Quality Assessment ==========
    story.append(PageBreak())
    story.append(Paragraph(_('10. Quality Assessment', '10. 质量评估'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph('Strengths', S['SubSectionTitle']))
    strengths = [
        'Well-motivated problem: uniform downsampling\'s harm to small objects is real and underappreciated.',
        'Complete method: from clustering to attention to downsampling to decoder adaptation, forming a closed loop.',
        'Rigorous experiments: 3 datasets \u00d7 4 sizes \u00d7 classification + segmentation + ablation, with fair controls.',
        'Transparent reporting: FLOPs, params, and flexible 1/5 rate data all disclosed.',
        'Reproducible: Apple official open-source code on GitHub.',
    ]
    for s in strengths:
        story.append(Paragraph('&bull; ' + s, S['BulletStyle']))

    story.append(Paragraph('Weaknesses', S['SubSectionTitle']))
    weaknesses = [
        'No actual inference latency comparison (irregular memory access may slow real-world speed).',
        'Ablation only at Mini scale; larger model components not independently verified.',
        'Base model only tested with ImageNet-22K pretraining, not full-scale controlled comparison.',
    ]
    for w in weaknesses:
        story.append(Paragraph('&bull; ' + w, S['BulletStyle']))

    story.append(Paragraph('Overall Assessment', S['SubSectionTitle']))
    story.append(Paragraph(
        'A well-designed, thoroughly-evaluated CVPR paper. The core contribution &ndash; scaling adaptive '
        'downsampling from classification to segmentation via balanced clustering + learnable merging &ndash; '
        'is technically sound and empirically validated. Clear argument structure and transparent reporting. '
        '<b>Rating: Strong paper (4/5).</b>', S['Body']))

    # Build
    doc.build(story)

    # Clean up temp files
    import shutil
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print(f'PDF saved to: {pdf_path}')
    return pdf_path


if __name__ == '__main__':
    import sys
    lang = 'en'
    if '--lang=zh' in sys.argv:
        lang = 'zh'
    build_pdf(lang=lang)
