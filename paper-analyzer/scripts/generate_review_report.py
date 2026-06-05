"""Generate review paper analysis PDF report using reportlab."""
import os
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Table, TableStyle, Image, Flowable)
from reportlab.lib.colors import black

TEMP_DIR = tempfile.mkdtemp(prefix='review_analyzer_')

LANG = 'en'


def set_language(lang):
    global LANG
    LANG = lang


def _(en_text, zh_text=None):
    if LANG == 'zh' and zh_text is not None:
        return zh_text
    return en_text


DARK_BLUE = HexColor('#2C3E50')
MEDIUM_BLUE = HexColor('#34495E')
ACCENT_BLUE = HexColor('#3498DB')
LIGHT_GRAY = HexColor('#ECF0F1')
MED_GRAY = HexColor('#7F8C8D')
TEXT_COLOR = HexColor('#2C3E50')
QUOTE_COLOR = HexColor('#7F8C8D')


def draw_framework_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    C_BG = '#E8F4FD'
    C_RES = '#4A90D9'
    C_METH = '#50B86C'
    C_IMG = '#E8833A'

    def draw_box(x, y, w, h, text, color, fontsize=8, tc='white'):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor='none', alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=fontsize, color=tc, fontweight='bold')

    ax.text(5, 6.7, 'Retinal OCT Segmentation Review — Content Architecture',
            ha='center', va='center', fontsize=13, fontweight='bold', color='#2C3E50')

    draw_box(0.3, 4.8, 2.8, 0.6, 'Background (Sec 2)\nOCT Principles & Anatomy', C_IMG, 8)
    draw_box(0.3, 3.6, 2.8, 0.6, 'Resources (Sec 3-4)\n20 Datasets + 15 Metrics', C_RES, 8)
    draw_box(0.3, 2.4, 2.8, 0.6, 'Anatomy Seg. (Sec 5)\nFull + Limited Supervision', C_METH, 8)
    draw_box(0.3, 1.2, 2.8, 0.6, 'Lesion Seg. (Sec 6)\nFull + Limited Supervision', C_METH, 8)

    tasks = [
        (3.8, 4.8, 'OCT Imaging\n(3 generations)'),
        (3.8, 3.6, 'Classification by\nTech Strategy'),
        (3.8, 2.4, 'Innovation-driven\nTaxonomy'),
        (3.8, 1.2, 'Discussion (Sec 7)\nChallenges + Directions'),
    ]
    for x, y, t in tasks:
        draw_box(x, y, 2.5, 0.6, t, '#9B59B6', 7)

    for y in [4.8, 3.6, 2.4, 1.2]:
        ax.annotate('', xy=(3.7, y+0.3), xytext=(3.2, y+0.3),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

    stats_text = (
        "Key Stats:\n"
        "- 60 papers (2019-2024)\n"
        "- 81.5% full sup (anatomy)\n"
        "- 51.5% full sup (lesion)\n"
        "- Most used: UNet family"
    )
    draw_box(6.8, 3.6, 2.8, 2.4, stats_text, '#F5A623', 8, 'white')

    plt.tight_layout()
    path = os.path.join(TEMP_DIR, 'framework.png')
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
    styles.add(ParagraphStyle('TitlePage', fontName='Helvetica', fontSize=26, leading=32,
                textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6*mm))
    styles.add(ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=14, leading=18,
                textColor=MEDIUM_BLUE, alignment=TA_CENTER, spaceAfter=3*mm))
    styles.add(ParagraphStyle('AuthorLine', fontName='Helvetica', fontSize=10, leading=14,
                textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=2*mm))
    styles.add(ParagraphStyle('SectionTitle', fontName='Helvetica-Bold', fontSize=16, leading=22,
                textColor=DARK_BLUE, spaceBefore=6*mm, spaceAfter=3*mm))
    styles.add(ParagraphStyle('SubSectionTitle', fontName='Helvetica-Bold', fontSize=13, leading=18,
                textColor=MEDIUM_BLUE, spaceBefore=4*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle('SubSubSectionTitle', fontName='Helvetica-Bold', fontSize=11, leading=15,
                textColor=MEDIUM_BLUE, spaceBefore=3*mm, spaceAfter=1*mm))
    styles.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=10, leading=14,
                textColor=TEXT_COLOR, alignment=TA_JUSTIFY, spaceAfter=2*mm))
    styles.add(ParagraphStyle('BulletStyle', fontName='Helvetica', fontSize=10, leading=14,
                textColor=TEXT_COLOR, leftIndent=8*mm, spaceAfter=1*mm))
    styles.add(ParagraphStyle('Quote', fontName='Helvetica-Oblique', fontSize=9, leading=13,
                textColor=QUOTE_COLOR, leftIndent=12*mm, rightIndent=12*mm,
                spaceBefore=1*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle('TableCell', fontName='Helvetica', fontSize=8, leading=10,
                textColor=TEXT_COLOR, alignment=TA_CENTER))
    styles.add(ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=8, leading=10,
                textColor=white, alignment=TA_CENTER))
    return styles


def make_table(data, col_widths=None):
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


def build_pdf(output_dir=None, lang='en'):
    set_language(lang)
    framework_path = draw_framework_diagram()
    styles = build_styles()

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), 'analysis_result')
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, 'Retinal_OCT_Image_Segmentation_Review_Analysis_Report.pdf')

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
        'Retinal OCT Image Segmentation with Deep Learning:\n'
        'A Review of Advances, Datasets, and Evaluation Metrics', S['SubTitle']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(_('Review Paper | 60 Papers (2019-2024)', '综述论文 | 60 篇 (2019-2024)'), S['AuthorLine']))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        'Huihong Zhang, Bing Yang, Sanqian Li, Xiaoqing Zhang, Xiaoling Li,<br/>'
        'Tianhang Liu, Risa Higashita, Jiang Liu', S['AuthorLine']))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        'Harbin Institute of Technology / Southern University of Science and Technology / '
        'University of Nottingham Ningbo China', S['AuthorLine']))
    story.append(Paragraph(
        'Code: github.com/ZhangHH233/Retinal_OCT_Image_Segmentation_via_Deep_Learning', S['AuthorLine']))
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
        ('Title', 'Retinal OCT Image Segmentation with Deep Learning: A Review of Advances, Datasets, and Evaluation Metrics'),
        ('Authors', 'Huihong Zhang, Bing Yang, Sanqian Li, Xiaoqing Zhang, Xiaoling Li, Tianhang Liu, Risa Higashita, Jiang Liu'),
        ('Affiliations', 'HIT Harbin, SUSTech Shenzhen, Univ. of Nottingham Ningbo China'),
        ('Type', 'Literature Review (60 papers, 2019-2024)'),
        ('Code', 'https://github.com/ZhangHH233/Retinal_OCT_Image_Segmentation_via_Deep_Learning'),
        ('Target Venue', 'Elsevier (Preprint)'),
    ]
    for label, value in meta_items:
        story.append(Paragraph(f'<b>{label}:</b> {value}', S['Body']))

    # ========== 2. Research Motivation ==========
    story.append(PageBreak())
    story.append(Paragraph(_('2. Research Motivation', '2. 研究动机'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    story.append(Paragraph(
        'Optical coherence tomography (OCT) is a widely used non-invasive imaging technology in ophthalmic '
        'clinical practice, providing high-resolution cross-sectional images of retinal microstructures. '
        'Segmentation of anatomical structures and pathological lesions in OCT images directly impacts '
        'clinical decisions, providing crucial biomarkers for diagnosis of ocular diseases such as '
        'age-related macular degeneration (AMD), diabetic macular edema (DME), and glaucoma.', S['Body']))
    story.append(Paragraph(
        'While commercial OCT devices offer automatic retinal layer segmentation with satisfactory accuracy '
        'in healthy eyes, their performance degrades severely under pathological conditions due to speckle '
        'noise, artifacts, and lesions. Deep learning methods have achieved remarkable progress, but the '
        'field lacks a systematic review that (1) covers both anatomy and lesion segmentation, '
        '(2) organizes methods by core technical strategy rather than backbone architecture, and '
        '(3) bridges the gap between technical advances and clinical requirements.', S['Body']))

    story.append(Paragraph('<b>Need for this review (three critical gaps):</b>', S['Body']))
    story.append(Paragraph(
        '&bull; Prior reviews focus predominantly on anatomical layer segmentation, with limited discussion '
        'on pathological lesion characterization crucial for diseases like diabetic macular edema.',
        S['BulletStyle']))
    story.append(Paragraph(
        '&bull; Current taxonomies largely follow conventional architectural classifications (CNN vs '
        'Encoder-decoder), with limited emphasis on innovations addressing domain-specific challenges '
        'like annotation scarcity.', S['BulletStyle']))
    story.append(Paragraph(
        '&bull; Despite the rapid development of advanced techniques such as uncertainty learning and '
        'attention mechanisms in medical imaging, their applications in OCT segmentation remain '
        'underexplored in existing reviews.', S['BulletStyle']))
    story.append(Paragraph(
        '<b>Key insight:</b> An innovation-driven taxonomy (grouping methods by core technical strategy '
        'rather than backbone) can better reveal the evolution of the field and help researchers '
        'identify effective approaches for specific challenges.', S['Body']))

    # ========== 3. Problem Definition ==========
    story.append(PageBreak())
    story.append(Paragraph(_('3. Problem Definition', '3. 问题定义'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph('3.1 Core Contradiction', S['SubSectionTitle']))
    story.append(Paragraph(
        'OCT segmentation is critical for clinical decision-making, but commercial devices fail '
        'under pathological conditions, while academic methods are fragmented across diverse '
        'architectures, supervision strategies, and evaluation standards.', S['Body']))

    story.append(Paragraph('3.2 Key Challenges', S['SubSectionTitle']))
    challenges = [
        ('Challenge 1: OCT image quality limitations',
         'Reduced resolution in deeper tissues due to light attenuation; speckle noise obscuring '
         'fine details; shadow artifacts and motion artifacts degrading image quality.',
         '"Reduced resolution of deeper tissues... Speckle noise inherent in OCT images...'),
        ('Challenge 2: Annotation scarcity',
         'Requires professional ophthalmologists; time-consuming and labor-intensive; rare '
         'disease cases are particularly scarce; existing datasets limited in scale with '
         'inconsistent annotation quality.',
         '"The acquisition of high-quality OCT data is challenging, particularly for rare diseases...'),
        ('Challenge 3: Lesion variability',
         'Pathological lesions differ significantly in shape, size, and location across diseases '
         'and progression stages, making pattern recognition extremely challenging.',
         '"Variability in retinal lesions, which differ in shape, size, and location...'),
        ('Challenge 4: Evaluation inconsistency',
         'Experimental paradigms diverge across studies (data sources, preprocessing, metrics), '
         'hindering comparative analysis; lack of clinically relevant standardized metrics.',
         '"Divergent experimental paradigms... hinder the comparative analysis of segmentation performance...'),
    ]
    for title, desc, quote in challenges:
        story.append(Paragraph(title, S['SubSubSectionTitle']))
        story.append(Paragraph(desc, S['Body']))

    # ========== 4. Core Contributions ==========
    story.append(PageBreak())
    story.append(Paragraph(_('4. Core Contributions', '4. 核心贡献'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    contribs = [
        ('Contribution 1: Latest comprehensive review',
         '"This review presents an analysis of 60 recent state-of-the-art deep learning studies '
         '(from January 2019 to June 2024) applied to OCT image segmentation."'),
        ('Contribution 2: Innovation-driven taxonomy',
         '"We introduce an innovation-driven taxonomy that categorizes methods based on their '
         'core technical strategies (e.g., multi-scale feature fusion, prior knowledge incorporation, '
         'uncertainty learning, attention mechanisms, dimension hybrid fusion, multi-task learning) '
         'rather than backbone architectures."'),
        ('Contribution 3: Medical-technical bridge',
         '"The review bridges the technical-clinical knowledge gap by introducing retinal OCT imaging, '
         'with detailed descriptions of key anatomical structures and pathological lesions."'),
        ('Contribution 4: Comprehensive resource compilation',
         '"The review systematically summarizes 20 publicly available datasets and 15 evaluation '
         'metrics used in OCT image segmentation."'),
        ('Contribution 5: Open-source code repository',
         'Provides implementable code templates for key algorithms via an open repository, '
         'accompanied by evaluation metrics and public datasets for performance benchmarking.'),
    ]
    for title, quote in contribs:
        story.append(Paragraph(title, S['SubSectionTitle']))
        story.append(Paragraph(quote, S['Quote']))

    # ========== 5. Content Architecture ==========
    story.append(PageBreak())
    story.append(Paragraph(_('5. Content Architecture', '5. 内容体系'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph('5.1 Review Structure Overview', S['SubSectionTitle']))
    story.append(Image(framework_path, width=170*mm, height=120*mm))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph('5.2 Background Layer (Section 2)', S['SubSectionTitle']))
    story.append(Paragraph(
        'Covers OCT technology principles and evolution (TD-OCT -> SD-OCT -> SS-OCT with increasing '
        'speed and resolution), imaging protocols (macular-centered vs ONH-centered), normal retinal '
        'anatomy with 18 consensus-based anatomical landmarks per the IN-OCT nomenclature, and '
        'pathological lesion OCT characteristics across 6 major disease categories (AMD, DME, CSC, '
        'RVO, glaucoma, trauma). This section is particularly valuable for computer science researchers '
        'without clinical training.', S['Body']))

    story.append(Paragraph('5.3 Resource Layer (Sections 3-4)', S['SubSectionTitle']))
    story.append(Paragraph(
        '20 publicly available datasets summarized in a unified table (Table 1) covering data volume, '
        'disease labels, annotation types, and imaging devices. Key datasets include DUKE family, '
        'Cell/Kermany (108,312 B-scans), RETOUCH, OCTA-500, and GOALS. '
        '15 evaluation metrics categorized into 5 types: region-based (DSC, IoU), contour-based '
        '(HD, HD95, ASSD, MAD), pixel error-based (MSE, RMSE), confusion matrix-based (Acc, Sens, '
        'Spec, AUC), and biomarker-based (Thickness Difference, Vascularity Index).', S['Body']))

    story.append(Paragraph('5.4 Method Layer - Anatomy Segmentation (Section 5)', S['SubSectionTitle']))
    story.append(Paragraph(
        'Full supervision methods (81.5% of studies): FCN/UNet baselines, multi-scale feature fusion '
        '(atrous conv, ASPP), prior knowledge incorporation (4 strategies: feature learning, model design, '
        'regularization, post-processing), uncertainty learning (Bayesian vs deterministic), attention '
        'mechanisms (CNN-Transformer hybrids: layer-wise embedding vs bottom embedding), and dimension '
        'hybrid fusion (1D A-line, 2.5D B-scan sequence, 3D volumetric). '
        'Limited supervision methods (18.5%): exclusively semi-supervised learning via label propagation '
        'and consistency regularization.', S['Body']))

    story.append(Paragraph('5.5 Method Layer - Lesion Segmentation (Section 6)', S['SubSectionTitle']))
    story.append(Paragraph(
        'Full supervision (51.5%): UNet, GAN, and Transformer backbones; multi-scale fusion (SPP, ASPP, '
        'sASPP); uncertainty learning (Bayesian UNet, ensemble methods); attention mechanisms; '
        'multi-task learning (heterogeneous: segmentation+classification; homogeneous: multi-lesion or '
        'lesion+anatomy joint segmentation). '
        'Limited supervision (48.5%): semi-supervised (label propagation, consistency, contrastive learning), '
        'weakly supervised (image-level heatmaps, point-level annotations), and unsupervised '
        '(domain adaptation, clustering, pretext tasks).', S['Body']))

    # ========== 6. Taxonomy & Analysis ==========
    story.append(PageBreak())
    story.append(Paragraph(_('6. Classification Taxonomy & Statistical Analysis', '6. 分类法与统计分析'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph(
        'The paper\'s most distinctive methodological contribution is its innovation-driven taxonomy. '
        'Instead of the conventional "CNN vs Transformer" architectural split, methods are categorized '
        'by the core technical strategy they employ to address domain-specific challenges.', S['Body']))

    story.append(Paragraph('6.1 Prior Knowledge Incorporation (4 strategies)', S['SubSectionTitle']))
    t1 = make_table([
        ['Category', 'Mechanism', 'Example', 'Ref.'],
        ['Feature Learning', 'Inject shape descriptors\nas additional features', 'FourierNet: Fourier\ndescriptors for HFL', '[49]'],
        ['Model Design', 'Embed prior into\nnetwork modules', 'GraphConv: layered\nstructure as graph prior', '[51]'],
        ['Regularization', 'Design losses from\nprior info', 'Thickness regularization;\nboundary continuity', '[55, 56]'],
        ['Post-processing', 'Correct outputs using\nanatomical constraints', 'Topology correction\nmodule with contrastive loss', '[57]'],
    ], [30*mm, 35*mm, 45*mm, 20*mm])
    story.append(t1)
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph('6.2 Multi-Task Learning in Lesion Segmentation', S['SubSectionTitle']))
    t2 = make_table([
        ['Type', 'Task Combo', 'Rationale', 'Ref.'],
        ['Heterogeneous', 'Seg + Classification', 'Lesion shape/size linked to\ndisease diagnosis', '[90]'],
        ['Homogeneous', 'Multi-lesion Seg', 'Shared features for multiple\nlesion types', '[93]'],
        ['Homogeneous', 'Lesion + Anatomy Seg', 'Anatomy context improves\nlesion localization', '[89, 91, 92]'],
    ], [25*mm, 35*mm, 55*mm, 25*mm])
    story.append(t2)
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph('6.3 Statistical Insights', S['SubSectionTitle']))
    t3 = make_table([
        ['Metric', 'Anatomy Seg', 'Lesion Seg'],
        ['Total studies reviewed', '27', '33'],
        ['Full supervision', '22 (81.5%)', '17 (51.5%)'],
        ['Limited supervision', '5 (18.5%)', '16 (48.5%)'],
        ['... Semi-supervised', '5 (100%)', '5 (31.2%)'],
        ['... Weakly supervised', '0', '5 (31.2%)'],
        ['... Unsupervised', '0', '6 (37.5%)'],
        ['Most used public dataset', 'HC-MS, DUKE', 'RETOUCH, Cell'],
    ], [40*mm, 40*mm, 40*mm])
    story.append(t3)

    # ========== 7. Key Findings ==========
    story.append(PageBreak())
    story.append(Paragraph(_('7. Key Findings', '7. 关键发现'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    findings = [
        'UNet, FCN, and their derivatives are the most widely adopted backbone architectures for both '
        'anatomy and lesion segmentation tasks.',
        'Prior knowledge incorporation is uniquely suited for anatomy segmentation where layer topology '
        'is well-defined, but less applicable to lesion segmentation due to high morphological variability.',
        'Anatomy segmentation is dominated by full supervision (81.5%), while lesion segmentation shows '
        'a near-balanced split (51.5% full vs 48.5% limited supervision), reflecting greater annotation '
        'difficulty for lesions.',
        'Multi-scale feature fusion (especially ASPP and its variants) is the most widely used technical '
        'strategy across both tasks, driven by the inherent multi-scale nature of retinal anatomy and lesions.',
        'Unsupervised learning accounts for 37.5% of limited-supervision lesion studies, suggesting '
        'significant interest in label-free approaches for this challenging domain.',
        'DSC and MAD remain the dominant evaluation metrics; biomarker-based metrics (e.g., thickness '
        'difference) are recognized as clinically relevant but rarely used by computer science researchers.',
    ]
    for f in findings:
        story.append(Paragraph('&bull; ' + f, S['BulletStyle']))

    # ========== 8. Limitations ==========
    story.append(PageBreak())
    story.append(Paragraph(_('8. Limitations', '8. 局限性'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    t4 = make_table([
        ['Limitation', 'Acknowledged', 'Severity'],
        ['No quantitative performance comparison table\nacross methods on same benchmark', 'No', 'High'],
        ['Only 60 papers; potential selection bias\nfrom limited search scope', 'No', 'Medium'],
        ['Specific databases and exclusion criteria\nnot fully disclosed', 'No', 'Medium'],
        ['Weak supervision only covers image-level\nand point-level; no box/scribble', 'No', 'Medium'],
        ['No systematic quality assessment of\nincluded studies (e.g., QUADAS)', 'No', 'Medium'],
        ['Limited connection to OCTA / fundus\nimaging or clinical outcome studies', 'No', 'Medium'],
        ['Code repository provides templates only,\nnot directly reproducible results', 'Yes', 'Low'],
        ['Future directions section is generic;\nlacks specific implementation roadmap', 'Yes', 'Low'],
    ], [65*mm, 25*mm, 20*mm])
    story.append(t4)

    # ========== 9. Future Work ==========
    story.append(Paragraph(_('9. Future Work', '9. 未来工作'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))
    story.append(Paragraph('<b>Explicitly suggested by authors:</b>', S['SubSectionTitle']))
    suggestions = [
        'Large-scale multi-center datasets with standardized annotations',
        'Synthetic data (GANs, diffusion models) to augment rare disease cases',
        'Advanced vision transformers and foundation models pre-trained on multimodal ophthalmic data',
        'Data augmentation, domain generalization, and federated learning for cross-device robustness',
        'Multimodal fusion (fundus photography, OCT angiography) for enhanced segmentation',
        'Standardized evaluation framework with unified experimental settings and metric reporting',
        'Community-wide open-source algorithm and pre-trained model sharing',
    ]
    for s in suggestions:
        story.append(Paragraph('&bull; ' + s, S['BulletStyle']))

    story.append(Paragraph('<b>Implied but not stated (potential extensions):</b>', S['SubSectionTitle']))
    implied = [
        'OCT segmentation results correlated with clinical prognosis and treatment outcomes',
        'Real-time intra-operative OCT segmentation for surgical guidance',
        'Foundation model adaptation (SAM, MedSAM) specifically for OCT imaging',
        'Longitudinal segmentation analysis for disease progression tracking (especially glaucoma)',
    ]
    for i in implied:
        story.append(Paragraph('&bull; ' + i, S['BulletStyle']))

    # ========== 10. Quality Assessment ==========
    story.append(PageBreak())
    story.append(Paragraph(_('10. Quality Assessment', '10. 质量评估'), S['SectionTitle']))
    story.append(HorizontalLine(170*mm))

    story.append(Paragraph('Strengths', S['SubSectionTitle']))
    strengths = [
        'Comprehensive medical background (Section 2) - provides essential clinical context for non-expert researchers, covering OCT principles, 18 anatomical landmarks, and 6 disease categories with corresponding OCT features',
        'Innovative classification scheme - grouping methods by core technical strategy reveals cross-architectural patterns and provides better guidance for addressing specific challenges',
        'Resource compilation value - 20 datasets and 15 metrics systematically organized with key characteristics, serving as a practical reference for researchers entering the field',
        'Full supervision spectrum coverage - from fully supervised to unsupervised, providing a complete landscape view',
        'Open-source code and dataset index - enhances reproducibility and lowers entry barrier',
    ]
    for s in strengths:
        story.append(Paragraph('&bull; ' + s, S['BulletStyle']))

    story.append(Paragraph('Weaknesses', S['SubSectionTitle']))
    weaknesses = [
        'No performance benchmark table - the most significant gap; without quantitative comparison across methods on the same dataset, the review cannot serve as a practical reference for method selection',
        'Limited search methodology transparency - specific databases, inclusion/exclusion criteria, and PRISMA-style flow diagram not provided',
        'No statistical trend analysis - despite 60 papers, no quantitative analysis of performance trends over time or across architectures',
    ]
    for w in weaknesses:
        story.append(Paragraph('&bull; ' + w, S['BulletStyle']))

    story.append(Paragraph('Overall Assessment', S['SubSectionTitle']))
    story.append(Paragraph(
        'A well-structured review with strong medical foundations and an innovative classification '
        'framework. The background layer (OCT principles, anatomy, pathology) is a valuable resource '
        'for cross-disciplinary researchers. The resource compilation (datasets + metrics) provides '
        'immediate practical utility. However, the absence of a quantitative benchmark table '
        'significantly limits its value as a reference tool for method comparison and selection. '
        '<b>Rating: Good review (3.0/5).</b>', S['Body']))

    # Build
    doc.build(story)

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
