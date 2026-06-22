from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable
import re

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
C_DARK_BLUE   = colors.HexColor("#1a237e")   # chapter headings
C_MED_BLUE    = colors.HexColor("#283593")
C_ACCENT      = colors.HexColor("#1565C0")   # LAQ headings
C_SAQ         = colors.HexColor("#00695C")   # SAQ headings
C_VSAQ        = colors.HexColor("#4527A0")   # VSAQ headings
C_CLINICAL    = colors.HexColor("#B71C1C")   # clinical/applied
C_BOX_BG      = colors.HexColor("#E3F2FD")   # blue tint box bg
C_BOX_BORDER  = colors.HexColor("#1565C0")
C_CLIN_BG     = colors.HexColor("#FFEBEE")   # red tint clinical box
C_CLIN_BORDER = colors.HexColor("#C62828")
C_MNEM_BG     = colors.HexColor("#F3E5F5")   # purple mnemonic box
C_MNEM_BORDER = colors.HexColor("#6A1B9A")
C_TABLE_HEAD  = colors.HexColor("#1565C0")
C_TABLE_ALT   = colors.HexColor("#E8F4FD")
C_GOLD        = colors.HexColor("#F57F17")   # star / high yield
C_LIGHT_GREY  = colors.HexColor("#F5F5F5")
C_DIVIDER     = colors.HexColor("#90CAF9")
C_GREEN_BG    = colors.HexColor("#E8F5E9")
C_GREEN_BORDER= colors.HexColor("#2E7D32")

PAGE_W, PAGE_H = A4

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent='Normal', **kwargs):
    s = ParagraphStyle(name, parent=styles[parent], **kwargs)
    return s

ST_chapter   = make_style('chapter',   fontName='Helvetica-Bold', fontSize=20,
                           textColor=colors.white, spaceAfter=4, spaceBefore=10,
                           alignment=TA_LEFT, leading=26)
ST_section   = make_style('section',   fontName='Helvetica-Bold', fontSize=15,
                           textColor=C_ACCENT, spaceAfter=4, spaceBefore=12,
                           borderPad=3, leading=20)
ST_saq_head  = make_style('saq_head',  fontName='Helvetica-Bold', fontSize=13,
                           textColor=C_SAQ, spaceAfter=3, spaceBefore=10, leading=18)
ST_vsaq_head = make_style('vsaq_head', fontName='Helvetica-Bold', fontSize=13,
                           textColor=C_VSAQ, spaceAfter=3, spaceBefore=10, leading=18)
ST_subhead   = make_style('subhead',   fontName='Helvetica-Bold', fontSize=11,
                           textColor=C_MED_BLUE, spaceAfter=2, spaceBefore=8, leading=16)
ST_body      = make_style('body',      fontName='Helvetica', fontSize=9.5,
                           spaceAfter=3, spaceBefore=1, leading=15, alignment=TA_JUSTIFY)
ST_bullet    = make_style('bullet',    fontName='Helvetica', fontSize=9.5,
                           spaceAfter=2, spaceBefore=1, leading=14,
                           leftIndent=14, firstLineIndent=-10)
ST_bullet2   = make_style('bullet2',   fontName='Helvetica', fontSize=9,
                           spaceAfter=1, spaceBefore=0, leading=13,
                           leftIndent=26, firstLineIndent=-10)
ST_box_body  = make_style('box_body',  fontName='Helvetica', fontSize=9.5,
                           spaceAfter=2, spaceBefore=1, leading=14)
ST_clinical  = make_style('clinical',  fontName='Helvetica', fontSize=9.5,
                           textColor=colors.HexColor("#5D0000"), spaceAfter=2,
                           spaceBefore=1, leading=14)
ST_mnem      = make_style('mnem',      fontName='Helvetica-Bold', fontSize=10,
                           textColor=colors.HexColor("#4A148C"), spaceAfter=2,
                           spaceBefore=1, leading=15)
ST_toc       = make_style('toc',       fontName='Helvetica-Bold', fontSize=11,
                           textColor=C_DARK_BLUE, spaceAfter=4, spaceBefore=2)
ST_label     = make_style('label',     fontName='Helvetica-Bold', fontSize=9.5,
                           textColor=C_DARK_BLUE, spaceAfter=2, spaceBefore=2)
ST_mono      = make_style('mono',      fontName='Courier', fontSize=8.5,
                           spaceAfter=1, spaceBefore=1, leading=13)
ST_star      = make_style('star',      fontName='Helvetica-Bold', fontSize=8,
                           textColor=C_GOLD)
ST_viva_q    = make_style('viva_q',    fontName='Helvetica-Bold', fontSize=9.5,
                           textColor=C_DARK_BLUE, spaceAfter=1, spaceBefore=4, leading=14)
ST_viva_a    = make_style('viva_a',    fontName='Helvetica', fontSize=9.5,
                           textColor=colors.HexColor("#1B5E20"), spaceAfter=3,
                           spaceBefore=0, leading=14, leftIndent=12)
ST_footer    = make_style('footer',    fontName='Helvetica', fontSize=8,
                           textColor=colors.grey, alignment=TA_CENTER)

# ─────────────────────────────────────────────
# HELPER FLOWABLES
# ─────────────────────────────────────────────
class ColorBox(Flowable):
    """Coloured rounded box wrapping a list of paragraphs."""
    def __init__(self, paragraphs, bg=C_BOX_BG, border=C_BOX_BORDER,
                 padding=8, radius=4):
        super().__init__()
        self.paragraphs = paragraphs
        self.bg = bg
        self.border = border
        self.padding = padding
        self.radius = radius
        self._width = None
        self._height = None

    def wrap(self, aW, aH):
        inner_w = aW - 2 * self.padding
        total_h = self.padding
        for p in self.paragraphs:
            w, h = p.wrap(inner_w, aH)
            total_h += h + 2
        total_h += self.padding
        self._width = aW
        self._height = total_h
        return aW, total_h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.bg)
        c.setStrokeColor(self.border)
        c.setLineWidth(1.2)
        c.roundRect(0, 0, self._width, self._height,
                    self.radius, fill=1, stroke=1)
        y = self._height - self.padding
        inner_w = self._width - 2 * self.padding
        for p in self.paragraphs:
            w, h = p.wrap(inner_w, self._height)
            y -= h
            p.drawOn(c, self.padding, y)
            y -= 2
        c.restoreState()


def chapter_block(title, subtitle=""):
    """Full-width dark blue chapter banner."""
    elems = []
    tbl_data = [[Paragraph(f'<font color="white"><b>{title}</b></font>', ST_chapter)]]
    if subtitle:
        tbl_data.append([Paragraph(f'<font color="#BBDEFB">{subtitle}</font>',
                                   make_style('cs', fontName='Helvetica', fontSize=11,
                                              textColor=colors.HexColor("#BBDEFB"),
                                              leading=16))])
    t = Table(tbl_data, colWidths=[PAGE_W - 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_DARK_BLUE),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 16),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [6]),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 8))
    return elems


def laq_heading(text):
    """Blue LAQ question heading with left accent bar."""
    stars = ""
    m = re.search(r'(⭐+)', text)
    if m:
        stars = f' <font color="#F57F17" size="9">{m.group(1)}</font>'
        text = text[:m.start()].strip()
    inner = [Paragraph(f'<b>{text}</b>{stars}', ST_section)]
    t = Table([[inner[0]]], colWidths=[PAGE_W - 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor("#E8EAF6")),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LINEBEFORE',    (0,0), (0,-1),  5, C_ACCENT),
    ]))
    return [t, Spacer(1, 4)]


def saq_heading(text):
    stars = ""
    m = re.search(r'(⭐+)', text)
    if m:
        stars = f' <font color="#F57F17" size="9">{m.group(1)}</font>'
        text = text[:m.start()].strip()
    inner = Paragraph(f'<b>{text}</b>{stars}', ST_saq_head)
    t = Table([[inner]], colWidths=[PAGE_W - 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor("#E0F2F1")),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBEFORE',    (0,0), (0,-1),  5, C_SAQ),
    ]))
    return [t, Spacer(1, 4)]


def vsaq_heading(text):
    stars = ""
    m = re.search(r'(⭐+)', text)
    if m:
        stars = f' <font color="#F57F17" size="9">{m.group(1)}</font>'
        text = text[:m.start()].strip()
    inner = Paragraph(f'<b>{text}</b>{stars}', ST_vsaq_head)
    t = Table([[inner]], colWidths=[PAGE_W - 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor("#EDE7F6")),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBEFORE',    (0,0), (0,-1),  5, C_VSAQ),
    ]))
    return [t, Spacer(1, 4)]


def sub_heading(text):
    return [Paragraph(f'<b>{text}</b>', ST_subhead)]


def bullet_item(text, level=1):
    text = text.lstrip('●○•– -').strip()
    # bold key terms before colon
    text = re.sub(r'^([A-Z][^:]{0,40}):', r'<b>\1:</b>', text)
    prefix = "•" if level == 1 else "◦"
    st = ST_bullet if level == 1 else ST_bullet2
    return Paragraph(f'{prefix}  {text}', st)


def clinical_box(items, title="Applied / Clinical"):
    paras = [Paragraph(f'<b><font color="#B71C1C">⚕ {title}</font></b>', ST_clinical)]
    for item in items:
        item = item.lstrip('●○•– ').strip()
        item = re.sub(r'^([A-Z][^:]{0,50}):', r'<b>\1:</b>', item)
        paras.append(Paragraph(f'• {item}', ST_clinical))
    return ColorBox(paras, bg=C_CLIN_BG, border=C_CLIN_BORDER, padding=10)


def mnemonic_box(text):
    paras = [
        Paragraph('<b><font color="#6A1B9A">💡 Mnemonic</font></b>', ST_mnem),
        Paragraph(text, ST_mnem),
    ]
    return ColorBox(paras, bg=C_MNEM_BG, border=C_MNEM_BORDER, padding=10)


def info_box(items, title=""):
    paras = []
    if title:
        paras.append(Paragraph(f'<b><font color="#1565C0">{title}</font></b>', ST_box_body))
    for item in items:
        item = item.lstrip('●○•– ').strip()
        item = re.sub(r'^([A-Z][^:]{0,50}):', r'<b>\1:</b>', item)
        paras.append(Paragraph(f'• {item}', ST_box_body))
    return ColorBox(paras, bg=C_BOX_BG, border=C_BOX_BORDER, padding=10)


def divider():
    return HRFlowable(width="100%", thickness=0.5, color=C_DIVIDER,
                      spaceAfter=6, spaceBefore=4)


def body_para(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return Paragraph(text, ST_body)


def make_simple_table(headers, rows, col_widths=None):
    """Generic styled table."""
    avail = PAGE_W - 4*cm
    if col_widths is None:
        col_widths = [avail / len(headers)] * len(headers)
    data = [[Paragraph(f'<font color="white"><b>{h}</b></font>',
                       make_style(f'th{i}', fontName='Helvetica-Bold', fontSize=9,
                                  textColor=colors.white, leading=13))
             for i, h in enumerate(headers)]]
    for ridx, row in enumerate(rows):
        data.append([Paragraph(str(cell),
                               make_style(f'td{ridx}', fontName='Helvetica', fontSize=9,
                                          leading=13))
                     for cell in row])
    style = TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),   C_TABLE_HEAD),
        ('ROWBACKGROUNDS',(0,1), (-1,-1),   [colors.white, C_TABLE_ALT]),
        ('GRID',          (0,0), (-1,-1),  0.4, colors.HexColor("#B0BEC5")),
        ('TOPPADDING',    (0,0), (-1,-1),  5),
        ('BOTTOMPADDING', (0,0), (-1,-1),  5),
        ('LEFTPADDING',   (0,0), (-1,-1),  6),
        ('RIGHTPADDING',  (0,0), (-1,-1),  6),
        ('VALIGN',        (0,0), (-1,-1),  'TOP'),
    ])
    return Table(data, colWidths=col_widths, style=style)


def nerve_box(nerve, origin, course, branches, deformity, color):
    """Compact nerve summary box."""
    bg = colors.HexColor("#E8F5E9") if "Radial" in nerve else \
         colors.HexColor("#FFF8E1") if "Median" in nerve else \
         colors.HexColor("#E3F2FD")
    paras = [
        Paragraph(f'<b><font color="{color}">{nerve}</font></b>',
                  make_style('nb', fontName='Helvetica-Bold', fontSize=11,
                             textColor=colors.HexColor(color), leading=16)),
        Paragraph(f'<b>Origin:</b> {origin}', ST_box_body),
        Paragraph(f'<b>Course:</b> {course}', ST_box_body),
        Paragraph(f'<b>Key Branches:</b> {branches}', ST_box_body),
        Paragraph(f'<b>Injury Deformity:</b> <font color="#B71C1C">{deformity}</font>',
                  ST_box_body),
    ]
    return ColorBox(paras, bg=colors.HexColor(bg) if isinstance(bg, str) else bg,
                    border=colors.HexColor(color), padding=10)


# ─────────────────────────────────────────────
# PAGE TEMPLATE
# ─────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(C_DARK_BLUE)
    canvas.rect(doc.leftMargin, PAGE_H - 20*mm,
                PAGE_W - doc.leftMargin - doc.rightMargin, 8*mm, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.setFillColor(colors.white)
    canvas.drawString(doc.leftMargin + 5, PAGE_H - 15*mm,
                      "ANATOMY — Complete Notes & Exam-Oriented Answers")
    canvas.drawRightString(PAGE_W - doc.rightMargin - 5, PAGE_H - 15*mm,
                           f"Page {doc.page}")
    # Footer
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(PAGE_W / 2, 12*mm, "High-Yield | Exam-Ready | Fully Structured")
    canvas.setStrokeColor(C_DIVIDER)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 16*mm, PAGE_W - doc.rightMargin, 16*mm)
    canvas.restoreState()


# ─────────────────────────────────────────────
# BUILD CONTENT
# ─────────────────────────────────────────────
story = []
W = PAGE_W - 4*cm   # usable width

# ═══════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════
story.append(Spacer(1, 60))
cover_title = Table(
    [[Paragraph('<font color="white"><b>ANATOMY</b></font>',
                make_style('ct', fontName='Helvetica-Bold', fontSize=36,
                           textColor=colors.white, leading=44, alignment=TA_CENTER)),
      ],
     [Paragraph('<font color="#BBDEFB">Complete Notes &amp; Exam-Oriented Answers</font>',
                make_style('cs2', fontName='Helvetica', fontSize=16,
                           textColor=colors.HexColor("#BBDEFB"), leading=22,
                           alignment=TA_CENTER))],
     [Paragraph('<font color="#90CAF9">Upper Limb · Head &amp; Neck · Neuroanatomy · '
                'Lower Limb · Thorax · Abdomen &amp; Pelvis · General Anatomy</font>',
                make_style('cs3', fontName='Helvetica', fontSize=11,
                           textColor=colors.HexColor("#90CAF9"), leading=16,
                           alignment=TA_CENTER))]
     ],
    colWidths=[W]
)
cover_title.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), C_DARK_BLUE),
    ('TOPPADDING',    (0,0), (-1,-1), 20),
    ('BOTTOMPADDING', (0,0), (-1,-1), 20),
    ('LEFTPADDING',   (0,0), (-1,-1), 20),
    ('RIGHTPADDING',  (0,0), (-1,-1), 20),
    ('ROUNDEDCORNERS', [10]),
]))
story.append(cover_title)
story.append(Spacer(1, 30))

badges = [
    ("LAQ", "Long Answer Questions", C_ACCENT),
    ("SAQ", "Short Answer Questions", C_SAQ),
    ("VSAQ", "Very Short Answer Questions", C_VSAQ),
]
badge_data = []
for code, label, col in badges:
    cell = Table(
        [[Paragraph(f'<font color="white"><b>{code}</b></font>',
                    make_style(f'b{code}', fontName='Helvetica-Bold', fontSize=14,
                               textColor=colors.white, alignment=TA_CENTER))],
         [Paragraph(label,
                    make_style(f'bl{code}', fontName='Helvetica', fontSize=8.5,
                               textColor=colors.white, alignment=TA_CENTER))]],
        colWidths=[W/3 - 10]
    )
    cell.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), col),
        ('TOPPADDING',    (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [6]),
    ]))
    badge_data.append(cell)

badges_tbl = Table([badge_data], colWidths=[W/3]*3, hAlign='CENTER')
badges_tbl.setStyle(TableStyle([
    ('LEFTPADDING',  (0,0), (-1,-1), 4),
    ('RIGHTPADDING', (0,0), (-1,-1), 4),
]))
story.append(badges_tbl)
story.append(Spacer(1, 30))

key_box = info_box([
    "⭐ Star ratings indicate exam frequency and importance",
    "🔴 Applied/Clinical boxes highlight high-yield examination points",
    "💡 Mnemonic boxes provide memory aids for difficult concepts",
    "All content preserved exactly — only formatting enhanced",
], title="How to Use This Document")
story.append(key_box)
story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: UPPER LIMB
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("UPPER LIMB", "Anatomy of the Upper Extremity"))

# ── LAQ 1: Mammary Glands ────────────────────────────────────────────────────
story.extend(laq_heading("LAQ 1: Mammary Glands (Breast) ⭐⭐⭐⭐⭐"))

story.extend(sub_heading("A. Extent"))
for b in ["Vertical: Extends from the 2nd to the 6th rib.",
          "Horizontal: Extends from the lateral border of the sternum to the mid-axillary line.",
          "Axillary Tail of Spence: A prolongation from the superolateral quadrant that pierces the deep fascia (foramen of Langer) to enter the axilla."]:
    story.append(bullet_item(b))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Relations"))
for b in ["Superficial: Covered by skin. The nipple is located in the 4th intercostal space, containing smooth muscle fibers and 15–20 lactiferous ducts.",
          "Deep (Breast Bed): Separated from deep structures by the retromammary space (contains loose areolar tissue allowing mobility).",
          "Lies on the deep fascia covering three muscles: Pectoralis major, Serratus anterior, and External oblique abdominis."]:
    story.append(bullet_item(b))
story.append(Spacer(1,4))

story.extend(sub_heading("C. Structure"))
story.append(body_para("Divided into three components: <b>Skin, Stroma,</b> and <b>Parenchyma.</b>"))
for b in ["Skin: Features the nipple and the areola (contains modified sebaceous glands of Montgomery which enlarge during pregnancy).",
          "Stroma (Framework): Fatty and fibrous tissue. Fibrous bands form the suspensory ligaments of Cooper which anchor the gland to the skin and deep fascia.",
          "Parenchyma (Glandular Tissue): Composed of 15–20 lobes arranged radially. Each lobe drains into a lactiferous duct, which exhibits a focal dilation called the lactiferous sinus before opening onto the nipple."]:
    story.append(bullet_item(b))
story.append(Spacer(1,4))

story.extend(sub_heading("D. Blood Supply"))
story.append(body_para("<b>Arterial Supply:</b>"))
for b in ["Internal thoracic artery (via perforating branches).",
          "Lateral thoracic and superior thoracic arteries (branches of the axillary artery).",
          "Lateral cutaneous branches of the posterior intercostal arteries."]:
    story.append(bullet_item(b))
story.append(bullet_item("Venous Drainage: Veins follow the arteries and drain into the internal thoracic, axillary, and posterior intercostal veins."))
story.append(Spacer(1,4))

story.extend(sub_heading("E. Lymphatic Drainage ⭐⭐"))
lymph_headers = ["Node Group", "% Drainage", "Drains"]
lymph_rows = [
    ["Axillary (Anterior/Pectoral)", "75%", "Major portion of the breast"],
    ["Internal Mammary (Parasternal)", "20%", "Medial breast"],
    ["Posterior Intercostal", "5%", "Posterior breast"],
]
story.append(make_simple_table(lymph_headers, lymph_rows,
                               col_widths=[W*0.35, W*0.18, W*0.47]))
story.append(Spacer(1,6))
story.append(bullet_item("Deep lymphatics drain the parenchyma, nipple, and areola via the subareolar Plexus of Sappey before reaching axillary nodes."))
story.append(Spacer(1,6))

story.append(KeepTogether([
    clinical_box([
        "Carcinoma of the Breast: Malignant invasion of the suspensory ligaments of Cooper causes traction → skin dimpling.",
        "Peau d'orange: Obstruction of superficial cutaneous lymphatics by tumor cells → localized lymphedema, skin resembles orange peel.",
        "Retraction of Nipple: Caused by tumor infiltration and fibrosis of the lactiferous ducts.",
    ]),
    Spacer(1,6)
]))

story.append(divider())

# ── LAQ 2: Brachial Plexus ───────────────────────────────────────────────────
story.extend(laq_heading("LAQ 2: Brachial Plexus ⭐⭐⭐⭐⭐"))

story.extend(sub_heading("A. Formation"))
story.append(body_para("Formed by the anterior primary rami of <b>C5, C6, C7, C8, and T1</b> spinal nerves. May receive contributions from C4 (pre-fixed) or T2 (post-fixed)."))
story.append(Spacer(1,4))

bp_headers = ["Component", "Composition", "Notes"]
bp_rows = [
    ["Roots", "C5, C6, C7, C8, T1", "Anterior primary rami"],
    ["Upper Trunk", "C5 + C6", "Junction = Erb's Point"],
    ["Middle Trunk", "C7", "Continuation of C7"],
    ["Lower Trunk", "C8 + T1", "Junction = Klumpke's region"],
    ["Lateral Cord", "Ant. div. Upper + Middle", "Lateral to axillary artery"],
    ["Medial Cord", "Ant. div. Lower trunk", "Medial to axillary artery"],
    ["Posterior Cord", "Post. div. all three trunks", "Posterior to axillary artery"],
]
story.append(make_simple_table(bp_headers, bp_rows,
                               col_widths=[W*0.28, W*0.36, W*0.36]))
story.append(Spacer(1,6))

story.extend(sub_heading("B. Branches ⭐⭐⭐"))
branch_headers = ["Origin", "Branch", "Root Value"]
branch_rows = [
    ["From Roots", "Long thoracic nerve", "C5, C6, C7"],
    ["From Roots", "Dorsal scapular nerve", "C5"],
    ["Upper Trunk", "Suprascapular nerve", "C5, C6"],
    ["Upper Trunk", "Nerve to subclavius", "C5, C6"],
    ["Lateral Cord", "Lateral pectoral, Musculocutaneous, Lateral root of median", "C5–C7"],
    ["Medial Cord", "Medial pectoral, Medial cutaneous n. arm & forearm, Ulnar n., Medial root of median", "C8, T1"],
    ["Posterior Cord", "Upper/Lower subscapular, Thoracodorsal, Axillary (C5,C6), Radial (C5–T1)", "C5–T1"],
]
story.append(make_simple_table(branch_headers, branch_rows,
                               col_widths=[W*0.22, W*0.5, W*0.28]))
story.append(Spacer(1,6))

story.extend(sub_heading("C. Applied Anatomy"))
palsy_headers = ["Feature", "Erb's Palsy (Upper Trunk)", "Klumpke's Palsy (Lower Trunk)"]
palsy_rows = [
    ["Roots Involved", "C5, C6", "C8, T1"],
    ["Cause", "Increased neck–shoulder angle (birth trauma)", "Hyper-abduction of arm (clutching branch)"],
    ["Deformity", "\"Waiter's / Policeman's Tip\" hand", "True Claw Hand"],
    ["Key Features", "Arm adducted, medially rotated; forearm extended & pronated", "All intrinsic muscles paralysed; may have Horner's syndrome"],
]
story.append(make_simple_table(palsy_headers, palsy_rows,
                               col_widths=[W*0.2, W*0.4, W*0.4]))
story.append(Spacer(1,6))
story.append(divider())

# ── LAQ 3: Shoulder Joint ─────────────────────────────────────────────────────
story.extend(laq_heading("LAQ 3: Shoulder Joint ⭐⭐⭐"))
story.extend(sub_heading("A. Type"))
story.append(bullet_item("Synovial joint — ball-and-socket (spheroidal) variety."))

story.extend(sub_heading("B. Articular Surfaces"))
story.append(bullet_item("Head of humerus articulates with the shallow glenoid cavity of scapula, deepened by the fibrocartilaginous glenoid labrum."))

story.extend(sub_heading("C. Ligaments"))
lig_rows = [
    ["Capsular Ligament", "Encloses the joint; thin and lax inferiorly to allow free movement"],
    ["Glenohumeral Ligaments", "Three thickenings (superior, middle, inferior) within anterior capsule"],
    ["Coracohumeral Ligament", "Root of coracoid process → greater tubercle"],
    ["Transverse Humeral Ligament", "Bridges bicipital groove; holds LHB tendon"],
]
story.append(make_simple_table(["Ligament", "Description"], lig_rows,
                               col_widths=[W*0.38, W*0.62]))
story.append(Spacer(1,6))

story.extend(sub_heading("D. Movements & Muscles ⭐⭐⭐"))
mov_headers = ["Movement", "Primary Muscles", "Secondary"]
mov_rows = [
    ["Flexion (0–90°)", "Pectoralis major (clavicular head), Anterior deltoid", "Coracobrachialis, Biceps"],
    ["Extension", "Latissimus dorsi, Posterior deltoid", "Teres major"],
    ["Abduction 0–15°", "Supraspinatus", "—"],
    ["Abduction 15–90°", "Deltoid (multipennate acromial fibres)", "—"],
    ["Abduction >90°", "Serratus anterior, Upper & lower Trapezius", "Overhead scapular rotation"],
    ["Medial Rotation", "Subscapularis, Pec major, Latissimus dorsi", "Teres major"],
    ["Lateral Rotation", "Infraspinatus, Teres minor", "Posterior deltoid"],
]
story.append(make_simple_table(mov_headers, mov_rows,
                               col_widths=[W*0.25, W*0.45, W*0.3]))
story.append(Spacer(1,6))

story.append(KeepTogether([
    clinical_box([
        "Dislocation of Shoulder Joint: Most commonly occurs inferiorly / antero-inferiorly (capsule least supported here). Axillary nerve at high risk.",
        "Dawbarn's Sign: In subacromial bursitis — pain over acromion when arm hangs; disappears on abduction (bursa slips under bone).",
        "Frozen Shoulder (Adhesive Capsulitis): Progressive inflammation and fibrosis → severe pain and global restriction of movements.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

# ── LAQ 4: Axillary System & Scapular Anastomosis ──────────────────────────
story.extend(laq_heading("LAQ 4: Axillary System & Scapular Anastomosis"))

story.extend(sub_heading("A. Axillary Artery — Parts & Branches"))
story.append(body_para("Continuation of subclavian artery at outer border of 1st rib. Divided into <b>3 parts</b> by Pectoralis minor."))
ax_headers = ["Part", "No. of Branches", "Branches"]
ax_rows = [
    ["1st Part", "1", "Superior thoracic artery"],
    ["2nd Part", "2", "Thoracoacromial artery, Lateral thoracic artery"],
    ["3rd Part", "3", "Subscapular artery, Anterior circumflex humeral a., Posterior circumflex humeral a."],
]
story.append(make_simple_table(ax_headers, ax_rows, col_widths=[W*0.18, W*0.2, W*0.62]))
story.append(Spacer(1,6))

story.extend(sub_heading("B. Axillary Lymph Nodes"))
ln_headers = ["Group", "Location", "Drains"]
ln_rows = [
    ["Anterior (Pectoral)", "Lower border of pectoralis minor", "Major portion of breast"],
    ["Posterior (Subscapular)", "Lower border of posterior axillary wall", "Back of trunk"],
    ["Lateral", "Upper part of humerus", "Entire upper limb"],
    ["Central", "Embedded in axillary fat", "Receives from above 3 groups"],
    ["Apical", "Apex of axilla", "Receives from central → subclavian trunk"],
]
story.append(make_simple_table(ln_headers, ln_rows, col_widths=[W*0.25, W*0.35, W*0.4]))
story.append(Spacer(1,6))

story.extend(sub_heading("C. Anastomosis Around the Scapula ⭐⭐⭐⭐⭐"))
story.append(info_box([
    "Provides vital collateral circulation between the 1st part of subclavian artery and the 3rd part of axillary artery.",
    "Suprascapular artery (from thyrocervical trunk of subclavian).",
    "Deep branch of transverse cervical artery / dorsal scapular artery (from subclavian).",
    "Circumflex scapular artery (branch of subscapular from 3rd part of axillary artery).",
], title="Participating Arteries"))
story.append(Spacer(1,6))
story.append(divider())

# ── LAQ 5: Ulnar Nerve ──────────────────────────────────────────────────────
story.extend(laq_heading("LAQ 5: Ulnar Nerve ⭐⭐⭐⭐⭐⭐"))

story.extend(sub_heading("A. Origin, Course & Termination"))
story.append(bullet_item("Origin: Terminal branch of the medial cord of the brachial plexus (C8, T1; sometimes C7)."))
story.append(bullet_item("Course: Medial side of axilla and arm → pierces medial intermuscular septum → behind medial epicondyle of humerus (\"funny bone\") → between two heads of flexor carpi ulnaris → superficial to flexor retinaculum → Guyon's canal → hand."))
story.append(bullet_item("Termination: Divides into superficial and deep terminal branches at the level of the pisiform bone."))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Branches & Distribution"))
un_headers = ["Region", "Motor Supply", "Sensory Supply"]
un_rows = [
    ["Arm", "No branches", "—"],
    ["Forearm", "Flexor carpi ulnaris; Medial ½ of FDP", "Palmar & dorsal cutaneous branches"],
    ["Hand (Superficial)", "Palmaris brevis", "Medial 1½ fingers (palmar)"],
    ["Hand (Deep)", "All interossei, Medial 2 lumbricals, Adductor pollicis, Hypothenar muscles", "Medial 1½ fingers (dorsal)"],
]
story.append(make_simple_table(un_headers, un_rows, col_widths=[W*0.2, W*0.45, W*0.35]))
story.append(Spacer(1,6))

story.append(KeepTogether([
    clinical_box([
        "Low Ulnar Nerve Injury (at Wrist): Paralysis of intrinsic muscles → hyperextension at MCP + flexion at IP joints of 4th & 5th digits (Claw Hand).",
        "Ulnar Paradox: Injury at elbow causes LESS clawing than at wrist, because elbow injury also paralyses FDP, removing the IP flexion force.",
        "Guyon's Canal: Fibroosseous tunnel between pisiform and hook of hamate — compression here causes Ulnar Tunnel Syndrome.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

# ── LAQ 6: Radial Nerve ─────────────────────────────────────────────────────
story.extend(laq_heading("LAQ 6: Radial Nerve ⭐⭐"))

story.extend(sub_heading("A. Origin, Course & Termination"))
story.append(bullet_item("Origin: Largest branch of the posterior cord (C5, C6, C7, C8, T1)."))
story.append(bullet_item("Course: Behind 3rd part of axillary artery → lower triangular space → spiral (radial) groove of humerus → pierces lateral intermuscular septum → front of lateral epicondyle."))
story.append(bullet_item("Termination: Divides into Superficial radial nerve (sensory) and Deep radial nerve / PIN (motor) anterior to lateral epicondyle."))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Branches"))
story.append(bullet_item("Muscular: Triceps brachii, Anconeus, Brachioradialis, ECRL."))
story.append(bullet_item("Cutaneous: Posterior cutaneous nerve of arm, Lower lateral cutaneous nerve of arm, Posterior cutaneous nerve of forearm."))
story.append(bullet_item("PIN (Posterior Interosseous Nerve): All remaining extensors in posterior compartment of forearm."))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Axilla Injury ('Saturday Night Palsy' / Crutch Palsy): Total loss of extension → profound Wrist Drop + sensory loss on posterior arm & forearm.",
        "Spiral Groove Injury (humeral shaft fracture): Wrist Drop. Triceps largely preserved (branches originate higher). Sensory loss restricted to web space of thumb.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

# ── LAQ 7: Median Nerve ─────────────────────────────────────────────────────
story.extend(laq_heading("LAQ 7: Median Nerve ⭐⭐⭐⭐"))

story.extend(sub_heading("A. Origin, Course & Termination"))
story.append(bullet_item("Origin: Formed by lateral root (C5,C6,C7) and medial root (C8,T1)."))
story.append(bullet_item("Course: Lateral to brachial artery → crosses to medial in cubital fossa → between heads of pronator teres → deep to FDS → beneath flexor retinaculum (carpal tunnel) → palm."))
story.append(bullet_item("Termination: Lateral and medial digital branches in palm."))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Branches & Distribution"))
mn_headers = ["Region", "Motor Supply", "Sensory Supply"]
mn_rows = [
    ["Arm", "No branches", "—"],
    ["Forearm", "All superficial flexors (except FCU); AIN → FPL, Lateral ½ FDP, Pronator quadratus", "—"],
    ["Hand", "3 Thenar muscles (via recurrent branch); Lateral 2 lumbricals", "Lateral 3½ digits (palmar)"],
]
story.append(make_simple_table(mn_headers, mn_rows, col_widths=[W*0.18, W*0.52, W*0.3]))
story.append(Spacer(1,6))

story.append(KeepTogether([
    clinical_box([
        "Carpal Tunnel Syndrome: Compression within carpal tunnel → pain & paresthesia in lateral 3½ digits + wasting of thenar eminence (Ape Thumb deformity).",
        "Supracondylar Fracture Injury: High lesion → loss of forearm pronation; loss of flexion of thumb & index finger. Making a fist → Hand of Benediction.",
    ]),
    Spacer(1,6)
]))

# ── Nerve Comparison Table ─────────────────────────────────────────────────
story.extend(sub_heading("High-Yield Nerve Comparison"))
story.append(make_simple_table(
    ["Feature", "Radial Nerve", "Median Nerve", "Ulnar Nerve"],
    [
        ["Origin (Cord)", "Posterior (C5–T1)", "Medial & Lateral (C5–T1)", "Medial (C8, T1)"],
        ["Forearm Motor", "Extensors via PIN", "Flexors (except FCU, med. ½ FDP)", "FCU and medial ½ FDP"],
        ["Hand Motor", "None", "3 Thenar muscles, 2 Lumbricals", "All interossei, Add. pollicis, 2 Lumbricals"],
        ["Injury Deformity", "Wrist Drop", "Ape Thumb / Hand of Benediction", "Claw Hand"],
    ],
    col_widths=[W*0.22, W*0.26, W*0.26, W*0.26]
))
story.append(Spacer(1,6))

# ── SAQ Section: Upper Limb ─────────────────────────────────────────────────
story.append(divider())
story.append(Paragraph("<b>SHORT ANSWER QUESTIONS — UPPER LIMB</b>",
                       make_style('saqbar', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_SAQ, spaceAfter=6, spaceBefore=6)))

story.extend(saq_heading("SAQ 1: Clavipectoral Fascia ⭐⭐"))
story.append(body_para("A strong fascial sheet lying deep to the clavicular head of pectoralis major."))
story.append(bullet_item("Superiorly: splits to enclose subclavius → attaches to clavicle."))
story.append(bullet_item("Inferiorly: splits to enclose pectoralis minor → continues as suspensory ligament of axilla."))
story.append(body_para("<b>Structures Piercing It:</b>"))
for s in ["Cephalic vein (inward → axillary vein)",
          "Thoracoacromial artery (outward)",
          "Lateral pectoral nerve (outward)",
          "Lymphatics connecting breast to apical axillary nodes"]:
    story.append(bullet_item(s))
story.append(Spacer(1,4))

story.extend(saq_heading("SAQ 2: Pectoralis Major & Pectoralis Minor"))
pm_rows = [
    ["Origin", "Clavicular head: Ant. surface medial ½ clavicle; Sternocostal head: Ant. sternum, upper 6 costal cartilages",
               "3rd, 4th, 5th ribs near costal cartilages"],
    ["Insertion", "Lateral lip of bicipital groove", "Medial border & upper surface of coracoid process"],
    ["Nerve", "Lateral & medial pectoral nerves (C5–T1)", "Medial pectoral nerve (C8, T1)"],
    ["Action", "Adduction & medial rotation; clavicular head flexes arm", "Depresses shoulder; draws scapula forward (protraction)"],
]
story.append(make_simple_table(["Feature", "Pectoralis Major ⭐⭐⭐", "Pectoralis Minor"],
                               pm_rows, col_widths=[W*0.2, W*0.4, W*0.4]))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 3: Serratus Anterior & Winging of Scapula ⭐⭐⭐"))
story.append(bullet_item("Origin: By 8 digitations from outer surfaces of upper 8 ribs."))
story.append(bullet_item("Insertion: Costal surface of medial border of scapula (bulk at inferior angle)."))
story.append(bullet_item("Nerve Supply: Long thoracic nerve / Nerve of Bell (C5, C6, C7)."))
story.append(bullet_item("Action: Protraction of scapula; steadying medial border; essential for overhead abduction (>90°) via scapular rotation."))
story.append(KeepTogether([
    clinical_box(["Winging of Scapula: Injury to long thoracic nerve (e.g., during radical mastectomy) paralyses serratus anterior → medial border of scapula projects backward when patient pushes against wall."]),
    Spacer(1,4)
]))

story.extend(saq_heading("SAQ 5: Rotator Cuff (Musculotendinous Cuff) ⭐⭐⭐⭐⭐⭐"))
story.append(body_para("Fibrous sheath formed by flattened tendons of 4 muscles blending with shoulder joint capsule → provides dynamic stability."))
story.append(mnemonic_box("SITS — Supraspinatus (Superior) · Infraspinatus (Posterior) · Teres minor (Posterior) · Subscapularis (Anterior)"))
rc_rows = [
    ["Supraspinatus", "Superior reinforcement", "Initiates abduction (0–15°)"],
    ["Infraspinatus", "Posterior reinforcement", "Lateral rotation"],
    ["Teres Minor", "Posterior reinforcement", "Lateral rotation"],
    ["Subscapularis", "Anterior reinforcement", "Medial rotation"],
]
story.append(make_simple_table(["Muscle", "Position", "Main Action"],
                               rc_rows, col_widths=[W*0.3, W*0.35, W*0.35]))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Inferior aspect of the cuff is DEFICIENT — most vulnerable site for shoulder dislocations.",
                  "Supraspinatus tendon is most commonly torn due to chronic friction (calcific tendinitis)."]),
    Spacer(1,4)
]))

story.extend(saq_heading("SAQ 6: Intermuscular Spaces Around Shoulder ⭐⭐⭐"))
space_rows = [
    ["Quadrangular Space", "Superior: Teres minor; Inferior: Teres major; Medial: Long head triceps; Lateral: Surgical neck humerus",
     "Axillary nerve + Posterior circumflex humeral vessels"],
    ["Upper Triangular Space", "Superior: Teres minor; Inferior: Teres major; Lateral: Long head triceps",
     "Circumflex scapular artery"],
    ["Lower Triangular Space", "Medial: Long head triceps; Lateral: Shaft of humerus; Superior: Teres major",
     "Radial nerve + Profunda brachii vessels"],
]
story.append(make_simple_table(["Space", "Boundaries", "Contents"],
                               space_rows, col_widths=[W*0.25, W*0.45, W*0.3]))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 8: Superficial Veins of Upper Limb ⭐⭐⭐⭐⭐⭐⭐"))
vein_rows = [
    ["Cephalic Vein", "Lateral side of dorsal venous network → lateral forearm → deltopectoral groove → pierces clavipectoral fascia → axillary vein",
     "IV access, PICC line insertion"],
    ["Basilic Vein", "Medial side of dorsal venous network → medial forearm → pierces deep fascia mid-arm → continues as axillary vein at lower border of teres major",
     "PICC line insertion"],
    ["Median Cubital Vein", "Obliquely across cubital fossa connecting cephalic to basilic; protected from brachial artery by bicipital aponeurosis",
     "Premier site for venepuncture, IV injections, blood transfusion"],
]
story.append(make_simple_table(["Vein", "Course", "Clinical Significance"],
                               vein_rows, col_widths=[W*0.22, W*0.48, W*0.3]))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 11: Cubital Fossa ⭐⭐⭐⭐⭐⭐"))
story.append(body_para("An inverted triangular space at the front of the elbow."))
story.append(make_simple_table(
    ["Boundary", "Structure"],
    [["Lateral", "Medial border of Brachioradialis"],
     ["Medial", "Lateral border of Pronator teres"],
     ["Base", "Imaginary line between two epicondyles of humerus"],
     ["Floor", "Brachialis + Supinator muscles"],
     ["Roof", "Skin, superficial fascia (median cubital vein), deep fascia reinforced by bicipital aponeurosis"]],
    col_widths=[W*0.25, W*0.75]
))
story.append(Spacer(1,4))
story.append(mnemonic_box("Contents (Medial → Lateral): MBBR — Median nerve · Brachial artery · Biceps brachii tendon · Radial nerve"))
story.append(Spacer(1,4))
story.append(KeepTogether([
    clinical_box(["Premier site for blood pressure auscultation (over brachial artery) and venepuncture (via median cubital vein).",
                  "Volkmann's Ischemic Contracture: Severe uncorrected compartment syndrome (e.g., after supracondylar fracture) → ischemic necrosis of flexor muscles."]),
    Spacer(1,6)
]))

story.extend(saq_heading("SAQ 13: Flexor Retinaculum of Hand ⭐⭐⭐⭐⭐⭐⭐"))
story.append(body_para("A strong fibrous band arching over carpal bones, converting the anterior concavity into the <b>carpal tunnel</b>."))
story.append(make_simple_table(
    ["Attachment", "Structure"],
    [["Medial", "Pisiform bone + Hook of hamate"],
     ["Lateral", "Tubercle of scaphoid + Crest of trapezium"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(Spacer(1,4))
story.append(info_box([
    "SUPERFICIAL to retinaculum: Palmaris longus tendon, Ulnar nerve, Ulnar artery, Palmar cutaneous branches of median & ulnar nerves.",
    "DEEP (inside carpal tunnel): Median nerve, 4 tendons FDS, 4 tendons FDP, Tendon of FPL — total 9 tendons + 1 nerve.",
], title="Relations"))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 15: Carpal Tunnel Syndrome ⭐⭐⭐⭐"))
story.append(KeepTogether([
    clinical_box([
        "Pathophysiology: Any condition reducing carpal tunnel volume (tenosynovitis, myxoedema, pregnancy) compresses the median nerve.",
        "Clinical Presentation: Burning pain, tingling, numbness in lateral 3½ digits.",
        "Progressive: Weakness and wasting of thenar muscles → Ape Thumb deformity (loss of thumb opposition).",
    ]),
    Spacer(1,6)
]))

story.extend(saq_heading("SAQ 19: Anatomical Snuff Box ⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Boundary", "Structure"],
    [["Medial (Posterior)", "Tendon of Extensor pollicis longus"],
     ["Lateral (Anterior)", "Tendons of Abductor pollicis longus + Extensor pollicis brevis"],
     ["Floor", "Scaphoid + Trapezium bones"],
     ["Roof", "Skin & superficial fascia (origin of cephalic vein, superficial radial nerve branches)"],
     ["Contents", "Radial artery (crossing the floor from anterior to posterior)"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Scaphoid Fracture: Tenderness in floor of snuff box following fall on outstretched hand → suggests scaphoid fracture. Blood supply enters distally → proximal pole at risk of avascular necrosis."]),
    Spacer(1,6)
]))

story.extend(saq_heading("SAQ 20: Arteries of the Hand ⭐⭐⭐"))
arch_rows = [
    ["Superficial Palmar Arch", "Ulnar artery (main) + superficial palmar branch of radial artery",
     "Deep to palmar aponeurosis, anterior to long flexor tendons"],
    ["Deep Palmar Arch", "Radial artery (main) + deep palmar branch of ulnar artery",
     "Deep to flexor tendons, resting on metacarpal bases"],
]
story.append(make_simple_table(["Arch", "Formation", "Location"],
                               arch_rows, col_widths=[W*0.28, W*0.42, W*0.3]))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 22: Lumbricals & Interossei ⭐⭐⭐"))
story.append(make_simple_table(
    ["Muscle", "Number", "Origin", "Nerve", "Action"],
    [
        ["Lumbricals", "4", "Tendons of FDP", "1st & 2nd: Median; 3rd & 4th: Ulnar (deep)", "Flex MCP + Extend IP joints"],
        ["Palmar Interossei", "4", "Unipennate", "Deep branch of ulnar nerve", "ADduct fingers (PAD)"],
        ["Dorsal Interossei", "4", "Bipennate", "Deep branch of ulnar nerve", "ABduct fingers (DAB)"],
    ],
    col_widths=[W*0.2, W*0.12, W*0.2, W*0.28, W*0.2]
))
story.append(Spacer(1,6))
story.append(mnemonic_box("PAD — Palmar interossei ADduct | DAB — Dorsal interossei ABduct"))

story.extend(saq_heading("SAQ 26: Claw Hand Deformity ⭐⭐⭐"))
story.append(body_para("<b>Anatomical Basis:</b> Ulnar nerve lesion → paralysis of 3rd & 4th lumbricals and all interossei → long extensors (radial) and long flexors (median/ulnar) unopposed."))
story.append(KeepTogether([
    clinical_box(["Hyperextension at MCP joints + marked flexion at PIP & DIP joints, most pronounced in 4th and 5th digits.",
                  "Ulnar Paradox: High lesion (elbow) = less clawing than low lesion (wrist) because FDP also paralysed at elbow."]),
    Spacer(1,6)
]))

story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: HEAD AND NECK
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("HEAD AND NECK", "Anatomy of the Cervical & Cranial Regions"))

story.extend(laq_heading("LAQ 1: Triangles of the Neck ⭐⭐"))
tri_headers = ["Triangle", "Boundaries", "Key Contents"]
tri_rows = [
    ["Carotid Triangle", "Anterosup: Post. belly of digastric; Anteroinf: Sup. belly of omohyoid; Post: SCM",
     "Common/Internal/External carotid aa., IJV, CN X, CN XII, Ansa cervicalis, Sympathetic trunk"],
    ["Digastric (Submandibular)", "Anteroinf: Ant. belly digastric; Posteroinf: Post. belly digastric + stylohyoid; Superior: Mandible base",
     "Submandibular gland, Facial a. & v., Submandibular LN, CN XII, Mylohyoid n."],
    ["Suboccipital Triangle", "Anteromedial: Rectus capitis post. major; Posterolateral: Obliquus capitis sup.; Inferolateral: Obliquus capitis inf.",
     "3rd part vertebral artery; Suboccipital nerve (dorsal ramus C1)"],
]
story.append(make_simple_table(tri_headers, tri_rows, col_widths=[W*0.2, W*0.42, W*0.38]))
story.append(Spacer(1,6))

story.extend(laq_heading("LAQ 2: Parotid Gland ⭐⭐⭐⭐"))
story.extend(sub_heading("A. Location"))
story.append(bullet_item("Largest salivary gland; located in deep recess below external acoustic meatus, wedged between ramus of mandible and mastoid process."))

story.extend(sub_heading("B. Stensen's Duct"))
story.append(bullet_item("5 cm long; emerges from anterior border of gland → runs across masseter → turns medially → pierces buccinator → opens into vestibule of mouth opposite upper 2nd molar."))

story.extend(sub_heading("C. Contents (Deep → Superficial) ⭐"))
story.append(make_simple_table(
    ["Structure", "Details"],
    [["External Carotid Artery", "Enters inferiorly; divides into maxillary and superficial temporal arteries"],
     ["Retromandibular Vein", "Formed by superficial temporal + maxillary veins; divides into ant. & post. divisions"],
     ["Facial Nerve (CN VII)", "Enters posteromedial surface; divides into 5 terminal branches (pes anserinus): Temporal, Zygomatic, Buccal, Marginal Mandibular, Cervical"]],
    col_widths=[W*0.32, W*0.68]
))
story.append(Spacer(1,4))

story.extend(sub_heading("D. Secretomotor Pathway"))
story.append(info_box([
    "Inferior salivatory nucleus → Glossopharyngeal nerve (CN IX) → Tympanic branch (Jacobson's nerve) → Tympanic plexus → Lesser petrosal nerve → Otic ganglion → Auriculotemporal nerve → Parotid gland.",
], title="Parasympathetic Pathway"))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Mumps: Acute viral parotitis; unyielding capsule → severe pain during chewing.",
        "Frey's Syndrome (Gustatory Sweating): Abnormal regeneration post-auriculotemporal nerve injury → parasympathetic fibres misgrow into sympathetic sweat gland pathways → cheek flushes & sweats while eating.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 3: Thyroid Gland ⭐⭐⭐⭐"))
story.extend(sub_heading("A. Location & Capsule"))
story.append(bullet_item("Located at C5–T1 level; two lateral lobes connected by isthmus crossing 2nd–4th tracheal rings."))
story.append(bullet_item("True inner fibrous capsule + false outer capsule from pretracheal fascia — fixes gland to larynx → thyroid moves upward on swallowing."))

story.extend(sub_heading("B. Blood Supply"))
story.append(make_simple_table(
    ["Vessel", "Origin", "Clinical Relation"],
    [["Superior Thyroid Artery", "1st branch of External Carotid", "Near upper pole → related to External Laryngeal Nerve"],
     ["Inferior Thyroid Artery", "Thyrocervical trunk (subclavian)", "Near lower pole → related to Recurrent Laryngeal Nerve"],
     ["Superior & Middle Thyroid Veins", "—", "Drain to Internal Jugular Vein"],
     ["Inferior Thyroid Veins", "—", "Drain to Left Brachiocephalic Vein"]],
    col_widths=[W*0.3, W*0.35, W*0.35]
))
story.append(Spacer(1,4))

story.extend(sub_heading("C. Histology ⭐⭐⭐"))
story.append(info_box([
    "Spherical thyroid follicles lined by simple cuboidal epithelium.",
    "Lumen filled with homogeneous protein gel — colloid (thyroglobulin).",
    "Parafollicular C-cells scattered between follicles — secrete calcitonin.",
], title="Microscopic Features"))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Goitre: Any thyroid enlargement; may compress trachea (respiratory distress) or recurrent laryngeal nerve (hoarseness).",
        "Thyroidectomy Surgical Anatomy: Ligate superior thyroid artery close to upper pole to protect external laryngeal nerve; ligate inferior thyroid artery far from lower pole to protect recurrent laryngeal nerve.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 4: Tongue ⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. External Features"))
story.append(bullet_item("V-shaped sulcus terminalis divides it into anterior 2/3rd (oral) and posterior 1/3rd (pharyngeal). Foramen caecum at apex of sulcus."))

story.extend(sub_heading("B. Papillae"))
story.append(make_simple_table(
    ["Type", "Number/Description", "Taste Buds"],
    [["Vallate (Circumvallate)", "8–12 large circular projections; just anterior to sulcus terminalis", "Yes (numerous)"],
     ["Fungiform", "Mushroom-shaped; scattered over sides and apex", "Yes"],
     ["Filiform", "Most numerous; small conical; cover dorsum", "No (friction only)"]],
    col_widths=[W*0.28, W*0.52, W*0.2]
))
story.append(Spacer(1,6))

story.extend(sub_heading("C. Nerve Supply ⭐⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Region", "General Sensation", "Taste"],
    [["Anterior 2/3rd", "Lingual nerve (CN V3)", "Chorda tympani (CN VII)"],
     ["Posterior 1/3rd", "Glossopharyngeal nerve (CN IX)", "Glossopharyngeal nerve (CN IX)"],
     ["Root / Vallecula", "Internal laryngeal nerve (CN X)", "Internal laryngeal nerve (CN X)"]],
    col_widths=[W*0.28, W*0.36, W*0.36]
))
story.append(Spacer(1,4))
story.append(mnemonic_box("Motor to ALL tongue muscles = CN XII (Hypoglossal)\n— EXCEPT Palatoglossus = CN X via Pharyngeal Plexus"))
story.append(Spacer(1,4))

story.extend(sub_heading("D. Lymphatic Drainage ⭐⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Region", "Drains To"],
    [["Apex", "Submental lymph nodes (bilateral)"],
     ["Lateral Anterior 2/3rd", "Submandibular lymph nodes (unilateral)"],
     ["Central Anterior 2/3rd", "Deep cervical lymph nodes"],
     ["Posterior 1/3rd", "Jugulo-digastric & jugulo-omohyoid deep cervical nodes (bilateral)"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box([
        "Carcinoma of tongue spreads rapidly due to rich interconnecting lymphatic network.",
        "Hypoglossal Nerve Injury: Tongue deviates toward side of lesion (contralateral genioglossus unopposed).",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 5: Cavernous Sinus ⭐⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. Location"))
story.append(bullet_item("Large paired dural venous sinus located on either side of the body of sphenoid bone (within middle cranial fossa). Between endosteal and meningeal layers of dura mater."))

story.extend(sub_heading("B. Contents ⭐"))
story.append(make_simple_table(
    ["Location within Sinus", "Structures"],
    [["Through the CENTER", "Internal Carotid Artery (with sympathetic plexus); Abducens Nerve (CN VI) — inferolateral to artery"],
     ["In the LATERAL WALL (Sup → Inf)", "Oculomotor Nerve (CN III); Trochlear Nerve (CN IV); Ophthalmic Nerve (CN V1); Maxillary Nerve (CN V2)"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Cavernous Sinus Thrombosis: Infections from the 'dangerous area of the face' track backward via facial and ophthalmic veins → septic thrombosis → proptosis, pain, ophthalmoplegia (CN III, IV, V, VI paralysis).",
        "Dangerous Area of the Face: Upper lip, ala of nose, and nasal septum — facial vein is valveless; communicates with cavernous sinus via superior ophthalmic vein.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 6: Scalp ⭐⭐⭐⭐⭐⭐⭐⭐"))
story.append(mnemonic_box("SCALP — Skin · Connective tissue (dense) · Aponeurosis (galea) · Loose areolar tissue (DANGEROUS) · Pericranium"))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Layer", "Name", "Key Feature"],
    [["S", "Skin", "Thick, hair-bearing; many sebaceous glands"],
     ["C", "Connective Tissue (dense superficial fascia)", "Lobulated fat with fibrous septa; blood vessels firmly anchored here"],
     ["A", "Aponeurosis (Galea Aponeurotica)", "Strong fibrous sheet connecting frontal and occipital bellies of occipitofrontalis"],
     ["L", "Loose Areolar Tissue", "⚠️ DANGEROUS LAYER — emissary veins here; infections spread easily"],
     ["P", "Pericranium", "External periosteum of skull bones"]],
    col_widths=[W*0.05, W*0.3, W*0.65]
))
story.append(Spacer(1,4))
story.append(KeepTogether([
    clinical_box([
        "Dangerous Layer (L4 — Loose Areolar Tissue): Infections spread across skull vault and track inward via emissary veins → meningitis or sinus thrombosis.",
        "Cephalhematoma: Blood under pericranium (L5) — limited to boundaries of one bone (pericranium dips into sutural ligaments).",
        "Safety Valve Bleeding: Dense fibrous tissue in L2 holds bleeding vessels OPEN → profuse scalp haemorrhage.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 7: Posterior Triangle of the Neck ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Feature", "Detail"],
    [["Boundaries", "Anterior: Post. border SCM; Posterior: Ant. border Trapezius; Base: Middle 1/3rd of clavicle"],
     ["Divisions", "Omohyoid divides into occipital triangle (above) and supraclavicular triangle (below)"],
     ["Key Nerves", "Spinal Accessory (CN XI), Brachial plexus roots/trunks, Cervical plexus branches (lesser occipital, great auricular, transverse cervical, supraclavicular)"],
     ["Arteries", "Subclavian artery (3rd part), Suprascapular artery, Superficial cervical artery"],
     ["Veins", "External Jugular Vein (pierces roof in supraclavicular triangle)"]],
    col_widths=[W*0.28, W*0.72]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Spinal Accessory Nerve (CN XI) vulnerability: Lies superficially in roof — at risk during lymph node biopsies or neck dissections → paralysis of trapezius → shoulder droop; difficulty abducting arm above 90°."]),
    Spacer(1,6)
]))

# SAQs Head & Neck
story.append(Paragraph("<b>SHORT ANSWER QUESTIONS — HEAD &amp; NECK</b>",
                       make_style('saqbar2', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_SAQ, spaceAfter=6, spaceBefore=6)))

story.extend(saq_heading("SAQ 1: Anatomical Basis of Bell's Palsy ⭐⭐⭐⭐⭐"))
story.append(body_para("Acute unilateral <b>lower motor neuron</b> paralysis of CN VII, typically from inflammation/compression within the stylomastoid foramen."))
story.append(make_simple_table(
    ["Feature Affected", "Structure Paralysed", "Clinical Sign"],
    [["Forehead wrinkling", "Frontalis muscle", "Cannot wrinkle forehead"],
     ["Eye closure", "Orbicularis oculi", "Cannot close eye → corneal ulceration risk"],
     ["Mouth", "Orbicularis oris + Zygomaticus major", "Drooping corner; saliva dribbles"],
     ["Chewing", "Buccinator", "Food accumulates in vestibule"]],
    col_widths=[W*0.3, W*0.35, W*0.35]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 10: Muscles of Mastication ⭐⭐⭐⭐⭐"))
story.append(body_para("All derived from the <b>1st pharyngeal arch</b>; all supplied by the <b>anterior division of CN V3</b>."))
story.append(make_simple_table(
    ["Muscle", "Origin", "Insertion", "Main Action"],
    [["Masseter", "Zygomatic arch", "Lateral surface of ramus of mandible", "Elevates mandible (closes jaw)"],
     ["Temporalis", "Temporal fossa", "Coronoid process of mandible", "Elevates & retracts mandible"],
     ["Medial Pterygoid", "Medial pterygoid plate", "Medial surface of angle of mandible", "Elevates & protracts mandible"],
     ["Lateral Pterygoid ⭐", "Greater wing & lateral pterygoid plate", "Neck of mandible & TMJ capsule", "Depresses (opens) jaw; protracts mandible"]],
    col_widths=[W*0.22, W*0.24, W*0.27, W*0.27]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 12: Horner's Syndrome ⭐⭐⭐"))
story.append(body_para("Caused by interruption of the <b>cervical sympathetic chain</b> (e.g., Pancoast tumour at lung apex)."))
story.append(make_simple_table(
    ["Feature", "Mechanism"],
    [["Ptosis", "Paralysis of smooth muscle — superior tarsal muscle"],
     ["Miosis", "Unopposed parasympathetic sphincter pupillae"],
     ["Anhidrosis", "Loss of sweating on affected face"],
     ["Enophthalmos", "Apparent sinking of eyeball into orbit"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 13: Waldeyer's Lymphatic Ring ⭐⭐⭐⭐⭐"))
story.append(body_para("An uninterrupted ring of lymphoid tissue surrounding the gateway to the respiratory and alimentary tracts."))
story.append(make_simple_table(
    ["Component", "Location"],
    [["Nasopharyngeal tonsil (Adenoid)", "Roof of nasopharynx (Superior)"],
     ["Tubal tonsils", "Around opening of auditory tube (Lateral)"],
     ["Palatine tonsils", "Oropharynx (Lateral)"],
     ["Lingual tonsil", "Posterior 1/3rd of tongue (Inferior)"]],
    col_widths=[W*0.45, W*0.55]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 16: Middle Ear (Tympanic Cavity) ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Boundary", "Structure"],
    [["Roof (Tegmen tympani)", "Thin plate separating from middle cranial fossa"],
     ["Floor (Jugular wall)", "Separates from internal jugular vein bulb"],
     ["Lateral", "Tympanic membrane (eardrum)"],
     ["Medial (Labyrinthine wall)", "Contains oval and round windows"],
     ["Contents", "Malleus, Incus, Stapes (auditory ossicles); Chorda tympani; Tensor tympani; Stapedius"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(Spacer(1,6))

story.append(make_simple_table(
    ["Feature", "Maxillary Sinus", "Details"],
    [["Size", "Largest paranasal sinus", "Within body of maxilla"],
     ["Drainage", "Middle meatus via hiatus semilunaris", "Ostium is high on medial wall"],
     ["Clinical", "Prone to chronic sinusitis", "Cannot drain efficiently in upright position"]],
    col_widths=[W*0.2, W*0.35, W*0.45]
))

# VSAQs Head & Neck
story.append(Paragraph("<b>VERY SHORT ANSWER QUESTIONS — HEAD &amp; NECK</b>",
                       make_style('vsaqbar2', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_VSAQ, spaceAfter=6, spaceBefore=6)))

story.extend(vsaq_heading("VSAQ 1: Pterion ⭐⭐⭐"))
story.append(body_para("<b>H-shaped</b> craniometric junction where 4 bones meet: Frontal, Parietal, Squamous Temporal, Greater wing of Sphenoid."))
story.append(KeepTogether([
    clinical_box(["Bone here is thin; overlies anterior division of middle meningeal artery. Fracture → rupture of artery → Extradural Haematoma."]),
    Spacer(1,4)
]))

story.extend(vsaq_heading("VSAQ 2: Kiesselbach's Plexus / Little's Area ⭐⭐⭐"))
story.append(body_para("Vascular anastomosis on the <b>anteroinferior nasal septum</b>. Most common site for epistaxis (nosebleed)."))
story.append(make_simple_table(
    ["Artery", "Source"],
    [["Septal branch of anterior ethmoidal", "Ophthalmic artery"],
     ["Septal branch of superior labial", "Facial artery"],
     ["Sphenopalatine artery", "Maxillary artery"],
     ["Greater palatine artery", "Maxillary artery"]],
    col_widths=[W*0.6, W*0.4]
))
story.append(Spacer(1,6))

story.extend(vsaq_heading("VSAQ 4: Foramen Passages Quick Reference ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Foramen", "Major Structures Passing Through"],
    [["Foramen Ovale", "CN V3 (Mandibular); Accessory meningeal a.; Lesser petrosal n.; Emissary veins (MALE)"],
     ["Foramen Magnum", "Medulla oblongata; Vertebral arteries; Spinal roots of CN XI"],
     ["Jugular Foramen", "CN IX, X, XI; Internal jugular vein"],
     ["Foramen Spinosum", "Middle meningeal artery; Nervous spinosus"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: NEUROANATOMY
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("NEUROANATOMY", "Central Nervous System — Key Structures"))

story.extend(laq_heading("LAQ 1: Fourth Ventricle ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. Location & Boundaries"))
story.append(bullet_item("Cavity of hindbrain, shaped like a tent. Anterior to cerebellum; posterior to pons and upper medulla."))
story.append(make_simple_table(
    ["Part", "Structures"],
    [["Upper Lateral Boundaries", "Superior cerebellar peduncles"],
     ["Lower Lateral Boundaries", "Inferior cerebellar peduncles, gracile & cuneate tubercles"],
     ["Roof (Posterior Wall)", "Superior medullary velum (above) + Inferior medullary velum (below)"],
     ["Openings for CSF", "Foramen of Magendie (median aperture); Two Foramina of Luschka (lateral apertures)"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(Spacer(1,6))

story.extend(sub_heading("B. Floor (Rhomboid Fossa) ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Feature", "Location", "Significance"],
    [["Median Sulcus", "Divides floor longitudinally", "Separates medial motor zone from lateral sensory zone"],
     ["Sulcus Limitans", "Longitudinal groove", "Separates median eminence (motor) from vestibular area (sensory)"],
     ["Facial Colliculus", "Lower median eminence", "CN VII axons winding around CN VI nucleus"],
     ["Hypoglossal Triangle", "Near inferior angle", "Overlies CN XII motor nucleus"],
     ["Vagal Triangle", "Lateral to hypoglossal", "Overlies dorsal motor nucleus of CN X"],
     ["Striae Medullares", "Transverse fibres across floor", "Enter inferior cerebellar peduncle"]],
    col_widths=[W*0.25, W*0.3, W*0.45]
))
story.append(Spacer(1,6))
story.append(divider())

story.extend(laq_heading("LAQ 2: Corpus Callosum ⭐⭐⭐⭐⭐"))
story.append(body_para("The <b>largest commissural pathway</b> in the brain. Connects neocortex of both cerebral hemispheres."))
story.append(make_simple_table(
    ["Part", "Location", "Fibres / Feature"],
    [["Rostrum", "Thin tapering anterior end", "Extends downward to lamina terminalis"],
     ["Genu", "Curved anterior extremity", "Fibres curve forward into frontal lobes → Forceps Minor"],
     ["Trunk (Body)", "Long central mass", "Connects frontal, parietal, temporal lobes; forms roof of lateral ventricle (tapetum)"],
     ["Splenium", "Thick rounded posterior end", "Large fibres curve into occipital lobes → Forceps Major"]],
    col_widths=[W*0.18, W*0.27, W*0.55]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Split-Brain Syndrome: Surgical transection (for intractable epilepsy) isolates hemispheres. Object in left hand (right hemisphere) cannot be named — language centres are in left hemisphere."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 3: Internal Capsule ⭐⭐⭐⭐⭐"))
story.append(body_para("Large V-shaped band of projection fibres (ascending + descending). Bounded medially by caudate nucleus & thalamus; laterally by lentiform nucleus."))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Part", "Between", "Key Fibres"],
    [["Anterior Limb", "Head of caudate nucleus & lentiform nucleus", "Frontopontine fibres; Anterior thalamic radiations"],
     ["Genu", "Junction of anterior & posterior limbs", "Corticobulbar (corticonuclear) fibres → control cranial nerve motor nuclei"],
     ["Posterior Limb", "Thalamus & lentiform nucleus", "Corticospinal fibres (UL, Trunk, LL — somatotopic); Superior thalamic radiations; Optic radiations"],
     ["Retrolentiform Part", "Behind lentiform nucleus", "Optic radiations → visual cortex"],
     ["Sublentiform Part", "Beneath lentiform nucleus", "Auditory radiations → auditory cortex"]],
    col_widths=[W*0.25, W*0.35, W*0.4]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box([
        "Lenticulostriate Artery = 'Artery of Cerebral Haemorrhage' (Charcot's artery). Branch of middle cerebral artery; prone to rupture/occlusion.",
        "Posterior limb lesion destroys corticospinal fibres → Contralateral Hemiplegia.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 4: Cerebellum ⭐"))
story.extend(sub_heading("A. Cerebellar Cortex (3 Layers)"))
story.append(make_simple_table(
    ["Layer", "Cells Present", "Key Feature"],
    [["Molecular (Outer)", "Stellate cells, Basket cells, Parallel axons", "Unmyelinated parallel fibres"],
     ["Purkinje Cell (Middle)", "Large flask-shaped Purkinje cells", "SOLE OUTPUT from cerebellar cortex; extensive dendritic trees"],
     ["Granule Cell (Inner)", "Granule cells, Golgi cells", "Densely packed; receive mossy fibre input"]],
    col_widths=[W*0.28, W*0.37, W*0.35]
))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Deep Cerebellar Nuclei"))
story.append(mnemonic_box("Don't Eat Greasy Foods — Dentate · Emboliform · Globose · Fastigial"))
story.append(Spacer(1,4))

story.extend(sub_heading("C. Cerebellar Peduncles ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Peduncle", "Connects To", "Main Fibre Type"],
    [["Superior Cerebellar Peduncle", "Midbrain", "Efferent (dentatothalamic tracts)"],
     ["Middle Cerebellar Peduncle", "Pons", "Afferent pontocerebellar fibres (from contralateral pontine nuclei)"],
     ["Inferior Cerebellar Peduncle", "Medulla", "Afferent spinal (dorsal spinocerebellar tract)"]],
    col_widths=[W*0.32, W*0.23, W*0.45]
))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Cerebellar Syndrome (DANIN): Dysdiadochokinesia · Ataxia (wide-based gait) · Nystagmus · Intention tremor · Nystagmus · past-pointing (Dysmetria).",
        "No true paralysis — only incoordination of movement.",
    ]),
    Spacer(1,6)
]))

# Neuro SAQs
story.append(Paragraph("<b>SHORT ANSWER QUESTIONS — NEUROANATOMY</b>",
                       make_style('saqbarn', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_SAQ, spaceAfter=6, spaceBefore=6)))

story.extend(saq_heading("SAQ 2: Medullary Syndromes ⭐"))
story.append(make_simple_table(
    ["Feature", "Medial Medullary Syndrome", "Lateral Medullary Syndrome (Wallenberg's)"],
    [["Artery Occluded", "Anterior spinal artery", "Posterior Inferior Cerebellar Artery (PICA)"],
     ["Limb Motor", "Contralateral hemiplegia (corticospinal)", "No hemiplegia"],
     ["Limb Sensory", "Contralateral loss of proprioception (medial lemniscus)", "Contralateral loss pain/temperature (spinothalamic)"],
     ["Cranial Nerve", "Ipsilateral CN XII (tongue deviates to side of lesion)", "Ipsilateral facial pain/temperature (spinal V); dysphagia & hoarseness (nucleus ambiguus CN IX, X)"],
     ["Other", "—", "Vertigo, nystagmus; ipsilateral Horner's syndrome"]],
    col_widths=[W*0.22, W*0.39, W*0.39]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 5: Subarachnoid Cisterns ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Cistern", "Location", "Contents"],
    [["Cisterna Magna (Cerebellomedullary)", "Between medulla and inferior cerebellum", "Receives CSF from 4th ventricle via foramen of Magendie"],
     ["Interpeduncular Cistern", "Over interpeduncular fossa", "Circle of Willis"],
     ["Pontine Cistern", "Ventral surface of pons", "Basilar artery"]],
    col_widths=[W*0.3, W*0.38, W*0.32]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 7: Circle of Willis ⭐⭐⭐⭐⭐"))
story.append(info_box([
    "Arterial polygon at base of brain within interpeduncular cistern.",
    "Anteriorly: Anterior cerebral arteries + Anterior communicating artery.",
    "Laterally: Internal carotid arteries + Posterior communicating arteries.",
    "Posteriorly: Posterior cerebral arteries (terminal branches of basilar artery).",
    "Function: Provides collateral circulation between internal carotid and vertebrobasilar systems.",
], title="Formation"))
story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: LOWER LIMB
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("LOWER LIMB", "Anatomy of the Lower Extremity"))

story.extend(laq_heading("LAQ 1: Sciatic Nerve ⭐⭐"))
story.extend(sub_heading("A. Root Value & Origin"))
story.append(bullet_item("L4, L5, S1, S2, S3 — Largest nerve in the body; terminal branch of the sacral plexus."))

story.extend(sub_heading("B. Course"))
story.append(bullet_item("Exits pelvis through greater sciatic foramen BELOW piriformis."))
story.append(bullet_item("Descends through gluteal region (deep to gluteus maximus) → posterior thigh → rests on adductor magnus."))
story.append(bullet_item("Terminates at upper angle of popliteal fossa → Tibial nerve + Common peroneal nerve."))

story.extend(sub_heading("C. Branches in Thigh"))
story.append(make_simple_table(
    ["Muscle Supplied", "Component of Sciatic Nerve"],
    [["Biceps femoris (long head)", "Tibial component"],
     ["Semitendinosus", "Tibial component"],
     ["Semimembranosus", "Tibial component"],
     ["Hamstring part of Adductor magnus", "Tibial component"],
     ["Biceps femoris (short head)", "Common peroneal component"]],
    col_widths=[W*0.5, W*0.5]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box([
        "Sciatica: Radiating pain (gluteal region → posterior thigh → lateral leg → dorsum of foot); most commonly from L5/S1 disc herniation.",
        "IM Injections: Given in SUPEROLATERAL quadrant of gluteal region to avoid sciatic nerve.",
        "Foot Drop: Complete sciatic lesion → paralysis of all dorsiflexors; loss of sensation below knee (except medial saphenous territory).",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 2: Hip Joint ⭐⭐⭐"))
story.extend(sub_heading("A. Type & Articular Surfaces"))
story.append(bullet_item("Synovial — ball-and-socket (multiaxial). Head of femur articulates with acetabulum, deepened by acetabular labrum."))

story.extend(sub_heading("B. Ligaments ⭐⭐⭐"))
story.append(make_simple_table(
    ["Ligament", "Description", "Function"],
    [["Capsular Ligament", "Proximal: acetabular rim; Distal: intertrochanteric line", "Encloses the joint"],
     ["Iliofemoral (Bigelow's Y-ligament)", "STRONGEST ligament in the body", "Prevents hyperextension while standing"],
     ["Pubofemoral Ligament", "Triangular", "Limits excessive abduction"],
     ["Ischiofemoral Ligament", "Weakest of three capsular", "Limits excessive medial rotation"],
     ["Ligamentum Teres", "Intracapsular; acetabular notch → fovea capitis", "Carries acetabular branch of obturator artery to femoral head"]],
    col_widths=[W*0.28, W*0.38, W*0.34]
))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Congenital Dislocation of Hip (CDH): More common in females; underdeveloped superior acetabular rim → femoral head slips upward.",
        "Avascular Necrosis (AVN) of Femoral Head: Neck of femur fractures tear retinacular vessels (medial circumflex femoral artery) → blood supply to head cut off → AVN.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 3: Arches of the Foot ⭐⭐⭐"))
story.append(make_simple_table(
    ["Feature", "Medial Longitudinal Arch", "Lateral Longitudinal Arch"],
    [["Bones", "Calcaneus, Talus, Navicular, 3 Cuneiforms, Medial 3 Metatarsals", "Calcaneus, Cuboid, Lateral 2 Metatarsals"],
     ["Keystone", "Head of Talus", "Cuboid"],
     ["Main Tie-Beam", "Plantar aponeurosis", "Plantar aponeurosis"],
     ["Key Ligament", "Spring Ligament (Plantar calcaneonavicular)", "Long and short plantar ligaments"],
     ["Dynamic Sling", "Tibialis anterior, Tibialis posterior, FHL", "Peroneus longus, Peroneus brevis"],
     ["Character", "Higher; more resilient; shock absorption", "Lower; more rigid; weight-bearing"]],
    col_widths=[W*0.25, W*0.375, W*0.375]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box([
        "Pes Planus (Flat Foot): Weakness/stretching of spring ligament and tibialis posterior tendon → medial longitudinal arch collapses → medial border touches ground.",
        "Pes Cavus: Abnormally high arch — often associated with neurological conditions.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 4: Knee Joint ⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. Type"))
story.append(bullet_item("Synovial — modified hinge joint (condylar / bicondylar). Allows flexion/extension + limited rotation when flexed."))

story.extend(sub_heading("B. Ligaments"))
story.append(make_simple_table(
    ["Ligament", "Attachment", "Function"],
    [["Ligamentum Patellae", "Patella → tibial tuberosity", "Continuation of quadriceps femoris tendon"],
     ["Tibial Collateral (Medial)", "Broad, flat band firmly attached to medial meniscus", "Resist valgus stress"],
     ["Fibular Collateral (Lateral)", "Cord-like; separated from lateral meniscus by popliteus tendon", "Resist varus stress"],
     ["ACL", "Ant. intercondylar tibia → medial surface of lateral femoral condyle", "Prevents anterior tibial displacement"],
     ["PCL", "Post. intercondylar tibia → lateral surface of medial femoral condyle", "Prevents posterior tibial displacement"]],
    col_widths=[W*0.25, W*0.42, W*0.33]
))
story.append(Spacer(1,4))

story.extend(sub_heading("C. Locking & Unlocking ⭐"))
story.append(info_box([
    "LOCKING: Final medial rotation of femur on tibia during full extension → knee 'locks' → allows prolonged standing without muscle fatigue. Produced by tensor fasciae latae and gluteus maximus.",
    "UNLOCKING: Lateral rotation of femur on tibia produced by POPLITEUS muscle — must occur before flexion can begin.",
], title="Locking Mechanism"))
story.append(Spacer(1,4))
story.append(KeepTogether([
    clinical_box([
        "Unhappy Triad of O'Donoghue: Blow to lateral knee with foot fixed → simultaneous tear of ACL + Tibial Collateral Ligament + Medial Meniscus.",
        "Anterior Drawer Sign: ACL torn → tibia can be pulled abnormally forward.",
        "Posterior Drawer Sign: PCL torn → tibia can be pushed abnormally backward.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 5: Great Saphenous Vein ⭐⭐⭐⭐⭐"))
story.append(bullet_item("Origin: Formed on dorsum of foot by medial marginal vein + dorsal venous arch."))
story.append(bullet_item("Course: Anterior to medial malleolus → medial leg → behind medial condyle of knee → anteromedial thigh → through saphenous opening → femoral vein."))
story.append(bullet_item("Perforators (Cockett's, Boyd's, Dodd's): Connect superficial to deep veins — valves allow flow only from superficial to deep."))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box([
        "Varicose Veins: Incompetent perforator or saphenofemoral junction valves → high deep venous pressure → superficial veins dilated and tortuous.",
        "CABG (Coronary Artery Bypass Grafting): Great saphenous vein segments used as autografts.",
    ]),
    Spacer(1,6)
]))

# SAQs Lower Limb
story.append(Paragraph("<b>SHORT ANSWER QUESTIONS — LOWER LIMB</b>",
                       make_style('saqbarl', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_SAQ, spaceAfter=6, spaceBefore=6)))

story.extend(saq_heading("SAQ 1: Femoral Triangle ⭐⭐⭐"))
story.append(make_simple_table(
    ["Boundary", "Structure"],
    [["Lateral", "Medial border of Sartorius"],
     ["Medial", "Medial border of Adductor longus"],
     ["Superior (Base)", "Inguinal ligament"],
     ["Floor (Medial → Lateral)", "Adductor longus, Pectineus, Iliopsoas"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(Spacer(1,4))
story.append(mnemonic_box("Contents (NAVEL): Nerve (Femoral) · Artery (Femoral) · Vein (Femoral) · Empty space (femoral canal) · Lymphatics (lymph node of Cloquet)"))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 5: Popliteal Fossa ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Boundary", "Structure"],
    [["Superolateral", "Biceps femoris"],
     ["Superomedial", "Semitendinosus + Semimembranosus"],
     ["Inferolateral", "Lateral head of gastrocnemius"],
     ["Inferomedial", "Medial head of gastrocnemius"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(Spacer(1,4))
story.append(info_box([
    "DEEP → SUPERFICIAL: Popliteal artery (deepest, closest to joint capsule) → Popliteal vein → Tibial nerve (most superficial).",
    "Common peroneal nerve: Runs along medial border of biceps femoris tendon.",
], title="Contents (Deep → Superficial)"))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ: Inversion & Eversion of the Foot ⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Movement", "Description", "Primary Muscles", "Joints Involved"],
    [["Inversion", "Sole faces medially (soles face each other)", "Tibialis anterior, Tibialis posterior", "Subtalar + Transverse tarsal joints"],
     ["Eversion", "Sole faces laterally (soles face away)", "Peroneus longus, Peroneus brevis", "Subtalar + Transverse tarsal joints"]],
    col_widths=[W*0.18, W*0.28, W*0.3, W*0.24]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ: Trendelenburg's Sign ⭐⭐⭐"))
story.append(body_para("<b>Normal:</b> Standing on one leg → gluteus medius + minimus on weight-bearing side contract → elevate opposite pelvis."))
story.append(KeepTogether([
    clinical_box(["Positive Sign: If gluteus medius/minimus are weak or paralysed (superior gluteal nerve injury or hip dislocation) → pelvis SAGS DOWN on unsupported side."]),
    Spacer(1,6)
]))

story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: THORAX
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("THORAX", "Thoracic Cavity & its Contents"))

story.extend(laq_heading("LAQ 1: Thoraco-Abdominal Diaphragm ⭐"))
story.extend(sub_heading("A. Origin"))
story.append(make_simple_table(
    ["Part", "Origin"],
    [["Sternal Part", "Two slips from posterior surface of xiphoid process"],
     ["Costal Part", "Inner surfaces of lower 6 ribs and costal cartilages (interdigitates with transversus abdominis)"],
     ["Lumbar Part", "Right crura (L1–L3); Left crura (L1–L2); Medial and lateral arcuate ligaments"]],
    col_widths=[W*0.25, W*0.75]
))
story.append(Spacer(1,4))
story.append(info_box(["All muscle fibres insert into the central cloverleaf-shaped CENTRAL TENDON (no direct bony attachments)."], title="Insertion"))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Major Openings ⭐⭐⭐"))
story.append(mnemonic_box("Voice Of America at 8, 10, 12 — Vena cava (T8) · Oesophagus (T10) · Aorta (T12)"))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Level", "Opening", "Structures Passing Through"],
    [["T8", "Vena Caval Opening", "Inferior Vena Cava; Right phrenic nerve"],
     ["T10", "Oesophageal Opening", "Oesophagus; Left & right vagus nerves; Oesophageal branches of left gastric vessels"],
     ["T12", "Aortic Opening", "Aorta; Thoracic Duct; Azygos Vein"]],
    col_widths=[W*0.1, W*0.28, W*0.62]
))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Hernia of Bochdalek (Posterolateral Diaphragmatic Hernia): Congenital failure of pleuroperitoneal membrane closure — most commonly LEFT side → abdominal organs protrude into thorax → lung compression → severe respiratory distress at birth.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 2: Typical Intercostal Space ⭐⭐⭐⭐"))
story.extend(sub_heading("A. Intercostal Muscles (Layers)"))
story.append(make_simple_table(
    ["Layer", "Fibre Direction", "Note"],
    [["External Intercostal", "Obliquely downward and FORWARD ('hands in pockets')", "Outermost layer"],
     ["Internal Intercostal", "Obliquely downward and BACKWARD (at right angles to external)", "Middle layer"],
     ["Innermost Intercostal (Intimus)", "Deepest layer", "Separated from internal layer by neurovascular bundle"]],
    col_widths=[W*0.28, W*0.45, W*0.27]
))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Neurovascular Bundle ⭐⭐⭐"))
story.append(info_box([
    "Arrangement in costal groove (SUPERIOR to INFERIOR): Vein — Artery — Nerve (VAN).",
    "Located along the LOWER BORDER of the UPPER rib, between internal and innermost intercostal layers.",
], title="VAN Arrangement"))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Thoracocentesis (Pleural Tap): Insert needle just ABOVE the UPPER BORDER of the LOWER rib to avoid injuring the main neurovascular bundle running along the upper rib."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 3: Bronchopulmonary Segments ⭐⭐⭐⭐⭐"))
story.append(info_box([
    "A well-defined, anatomical, functional, and surgical unit of lung tissue.",
    "Aerated by a specific tertiary (segmental) bronchus; supplied by a specific segmental branch of the pulmonary artery.",
    "Pyramidal in shape — apex toward lung root; base toward lung surface.",
    "Pulmonary veins are INTERsegmental (run in connective tissue septa between segments).",
    "Diseased segment can be surgically removed (segmentectomy) without damaging surrounding tissue.",
], title="Definition & Characteristics"))
story.append(Spacer(1,4))

story.append(make_simple_table(
    ["Lung", "Total Segments", "Upper Lobe", "Middle Lobe", "Lower Lobe"],
    [["Right Lung", "10", "3 (Apical, Anterior, Posterior)", "2 (Medial, Lateral)", "5 (Apical, Ant basal, Post basal, Med basal, Lat basal)"],
     ["Left Lung", "10", "5 (Apical, Post, Ant, Sup lingular, Inf lingular)", "None (lingular instead)", "5 (Apical, Ant basal, Post basal, Med basal, Lat basal)"]],
    col_widths=[W*0.15, W*0.12, W*0.27, W*0.2, W*0.26]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Aspiration Pneumonia: In supine position, aspirated foreign body → apical segment of lower lobe (Segment 6) because its bronchus branches directly off the posterior main bronchus."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 4: Heart ⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. Coronary Circulation ⭐⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Artery", "Origin", "Supplies"],
    [["Right Coronary Artery (RCA)", "Anterior aortic sinus", "Right atrium, Right ventricle, Part of left ventricle, SA node (60%), AV node → gives Marginal branch → Posterior Interventricular artery"],
     ["Left Anterior Descending (LAD)", "Left Coronary Artery (from left posterior aortic sinus)", "Left ventricle (anterior), Interventricular septum"],
     ["Circumflex Artery", "Left Coronary Artery", "Left atrium, Left ventricle (posterior/lateral)"]],
    col_widths=[W*0.28, W*0.3, W*0.42]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["LAD (Left Anterior Descending Artery) = 'Widow Maker' — most frequently occluded artery in myocardial infarction.",
                  "Venous drainage: Coronary sinus (in posterior coronary sulcus → right atrium) with tributaries: great, middle, and small cardiac veins."]),
    Spacer(1,6)
]))

story.extend(laq_heading("LAQ 5: Right Atrium ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Part", "Features"],
    [["Anterior Smooth-Walled Part (Sinus Venarum)", "Derived from embryonic sinus venosus. Openings: SVC, IVC (guarded by Eustachian valve), Coronary sinus (guarded by Thebesian valve)"],
     ["Posterior Rough Muscular Part", "Contains parallel muscular ridges — musculi pectinati (extending from crista terminalis)"],
     ["Interatrial Septum", "Fossa ovalis: Shallow oval depression = site of embryonic foramen ovale; surrounded by limbus fossa ovalis"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(Spacer(1,6))

# Thorax SAQs
story.append(Paragraph("<b>SHORT ANSWER QUESTIONS — THORAX</b>",
                       make_style('saqbart', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_SAQ, spaceAfter=6, spaceBefore=6)))

story.extend(saq_heading("SAQ 1: Sternal Angle (Angle of Louis) ⭐⭐⭐"))
story.append(body_para("Junction of manubrium and body of sternum (manubriosternal joint); at level of <b>T4–T5 intervertebral disc</b>."))
story.append(info_box([
    "Arch of the Aorta begins and ends here.",
    "Trachea bifurcates into left and right primary bronchi.",
    "Pulmonary trunk divides into left and right pulmonary arteries.",
    "Boundary between superior mediastinum and inferior mediastinum.",
], title="High-Yield Events at This Level"))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 3: Thoracic Duct ⭐⭐⭐"))
story.append(body_para("Largest lymphatic vessel in the body."))
story.append(make_simple_table(
    ["Feature", "Detail"],
    [["Origin", "Cisterna chyli at T12 lower border"],
     ["Entry into Thorax", "Through aortic opening of diaphragm"],
     ["Course", "Ascends on right side of vertebral column → crosses to LEFT at T5 level (sternal angle) → runs up into neck"],
     ["Termination", "Drains into junction of left internal jugular and left subclavian veins"],
     ["Drainage Area", "Almost entire body EXCEPT upper right quadrant"]],
    col_widths=[W*0.28, W*0.72]
))
story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: ABDOMEN & PELVIS
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("ABDOMEN AND PELVIS", "Abdominal & Pelvic Anatomy"))

story.extend(laq_heading("LAQ 1: Rectus Sheath ⭐⭐⭐"))
story.append(body_para("Strong fibrous sheath enclosing rectus abdominis on each side. Formed by interlocking aponeuroses of external oblique, internal oblique, and transversus abdominis."))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Level", "Anterior Wall", "Posterior Wall"],
    [["Above Costal Margin", "External oblique aponeurosis only", "DEFICIENT — rectus lies on costal cartilages"],
     ["Between Costal Margin & Arcuate Line", "Ext. oblique + Ant. split of int. oblique aponeurosis", "Post. split of int. oblique + Transversus abdominis aponeurosis"],
     ["Below Arcuate Line (Line of Douglas)", "ALL THREE aponeuroses pass anterior to rectus", "DEFICIENT — only fascia transversalis"]],
    col_widths=[W*0.32, W*0.36, W*0.32]
))
story.append(Spacer(1,4))
story.append(info_box(["Contents: Rectus abdominis + Pyramidalis (muscles); Superior epigastric vessels (from internal thoracic) + Inferior epigastric vessels (from external iliac) — anastomose within sheath; Terminal branches of T7–T12 spinal nerves."], title="Contents"))
story.append(Spacer(1,6))
story.append(divider())

story.extend(laq_heading("LAQ 2: Inguinal Canal ⭐⭐"))
story.append(body_para("Oblique intermuscular tunnel ~4 cm long, just above medial half of inguinal ligament. Extends from <b>deep inguinal ring</b> (in fascia transversalis) to <b>superficial inguinal ring</b> (in external oblique aponeurosis)."))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Boundary", "Structure"],
    [["Anterior Wall", "External oblique aponeurosis (entire length); reinforced laterally by internal oblique fibres"],
     ["Posterior Wall", "Fascia transversalis (entire length); reinforced medially by conjoint tendon"],
     ["Roof", "Arching fibres of internal oblique + transversus abdominis"],
     ["Floor", "Grooved upper surface of inguinal ligament + lacunar ligament"]],
    col_widths=[W*0.28, W*0.72]
))
story.append(Spacer(1,4))
story.append(info_box(["MALE: Spermatic cord (vas deferens, testicular artery, pampiniform plexus).",
                       "FEMALE: Round ligament of the uterus.",
                       "BOTH SEXES: Ilioinguinal nerve."], title="Contents"))
story.append(Spacer(1,4))

story.append(KeepTogether([
    clinical_box([
        "Indirect Inguinal Hernia: Through deep ring, down canal inside spermatic cord coverings → can descend into scrotum. Caused by patent processus vaginalis.",
        "Direct Inguinal Hernia: Pushes directly through posterior wall via Hesselbach's Triangle. Bypasses deep ring; rarely descends into scrotum.",
    ]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 3: Stomach ⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. Blood Supply"))
story.append(make_simple_table(
    ["Location", "Artery", "Origin"],
    [["Lesser curvature", "Left gastric artery", "Coeliac trunk"],
     ["Lesser curvature", "Right gastric artery", "Hepatic artery"],
     ["Greater curvature", "Left gastroepiploic artery", "Splenic artery"],
     ["Greater curvature", "Right gastroepiploic artery", "Gastroduodenal artery"],
     ["Fundus", "Short gastric arteries", "Splenic artery"]],
    col_widths=[W*0.25, W*0.37, W*0.38]
))
story.append(Spacer(1,4))
story.append(info_box([
    "Stomach Bed (Posterior Relations — separated by lesser sac): Pancreas body & tail; Splenic artery; Left kidney & suprarenal gland; Spleen; Transverse mesocolon & colon; Left crus of diaphragm.",
], title="Posterior Relations"))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Posterior gastric ulcer perforation → stomach contents leak into lesser sac. Erosion can damage underlying splenic artery → severe internal bleeding."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 4: Liver ⭐⭐⭐⭐"))
story.extend(sub_heading("A. External Features"))
story.append(bullet_item("Largest gland in body. Located in right hypochondrium and epigastrium. Anatomical division by falciform ligament into right and left lobes."))
story.append(bullet_item("Ligamentum teres (obliterated left umbilical vein) in lower margin of falciform ligament. Ligamentum venosum (obliterated ductus venosus) posteriorly."))
story.append(Spacer(1,4))
story.append(info_box([
    "Bare Area of Liver: Large triangular area on posterior surface of right lobe — devoid of peritoneum; liver tissue in direct contact with diaphragm. Bounded by coronary ligaments.",
    "Hepatic Segments: 8 functionally independent segments (based on portal vein, hepatic artery, bile duct branches). Each has independent vascular inflow → individual segment can be resected (segmentectomy).",
], title="Key Features"))
story.append(Spacer(1,6))
story.append(divider())

story.extend(laq_heading("LAQ 5: Portal Vein & Portocaval Anastomosis ⭐⭐⭐⭐"))
story.append(bullet_item("Formation: Superior Mesenteric Vein + Splenic Vein (behind neck of pancreas)."))
story.append(bullet_item("Course: Behind 1st part of duodenum → right margin of lesser omentum (posterior to hepatic artery and bile duct) → porta hepatis."))
story.append(Spacer(1,4))

story.extend(sub_heading("Sites of Portocaval Anastomosis ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Site", "Portal Branch", "Systemic Branch", "Clinical Complication"],
    [["Lower Oesophagus", "Left Gastric Vein", "Oesophageal branches of Azygos", "Oesophageal Varices → haematemesis"],
     ["Anal Canal", "Superior Rectal Vein", "Middle & Inferior Rectal Veins", "Internal Haemorrhoids (Piles)"],
     ["Umbilicus", "Paraumbilical Veins", "Superficial Epigastric Vein", "Caput Medusae"],
     ["Retroperitoneal", "Colic Veins", "Lumbar Veins", "Silent collaterals"]],
    col_widths=[W*0.22, W*0.22, W*0.24, W*0.32]
))
story.append(Spacer(1,6))
story.append(divider())

story.extend(laq_heading("LAQ 6: Pancreas ⭐⭐⭐⭐⭐"))
story.append(body_para("Retroperitoneal organ at L1–L2. Parts: <b>Head</b> (in C of duodenum; has uncinate process) → <b>Neck</b> → <b>Body</b> → <b>Tail</b> (touches hilum of spleen)."))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Duct", "Course", "Drains Into"],
    [["Main Pancreatic Duct (of Wirsung)", "Tail → head; joins common bile duct → hepatopancreatic ampulla of Vater", "2nd part of duodenum at Major Duodenal Papilla"],
     ["Accessory Duct (of Santorini)", "Drains upper part of head", "2nd part of duodenum at Minor Duodenal Papilla"]],
    col_widths=[W*0.3, W*0.4, W*0.3]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Carcinoma of Head of Pancreas: Compresses common bile duct → obstructive jaundice + palpable non-tender gallbladder. Courvoisier's Law: Palpable, non-tender gallbladder + jaundice → likely carcinoma of head of pancreas."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(laq_heading("LAQ 10: Uterus ⭐⭐⭐⭐⭐"))
story.extend(sub_heading("A. Normal Axes"))
story.append(make_simple_table(
    ["Axis", "Angle", "Definition"],
    [["Anteversion", "~90°", "Long axis of cervix tilted forward relative to long axis of vagina"],
     ["Anteflexion", "~125°", "Long axis of body of uterus bent forward relative to long axis of cervix"]],
    col_widths=[W*0.25, W*0.15, W*0.6]
))
story.append(Spacer(1,4))

story.extend(sub_heading("B. Supports of the Uterus ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Support", "Type", "Function"],
    [["Pelvic Diaphragm (levator ani + coccygeus)", "Primary (muscular floor)", "Primary muscular floor support"],
     ["Mackenrodt's Ligaments (Cardinal/Lateral cervical)", "Primary (fibromuscular)", "PRIMARY support — prevent downward sagging"],
     ["Uterosacral Ligaments", "Primary (fibromuscular)", "Anchor cervix backward to sacrum"],
     ["Pubocervical Ligaments", "Primary (fibromuscular)", "Anchor cervix forward to pubic bones"],
     ["Broad Ligament", "Secondary (peritoneal)", "Contains uterine vessels, ureter"],
     ["Round Ligament", "Secondary (peritoneal)", "Maintains anteversion"]],
    col_widths=[W*0.35, W*0.28, W*0.37]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box([
        "Uterine artery crosses SUPERIOR to ureter ('water runs under the bridge') — critical hazard during hysterectomy.",
        "Uterine Prolapse: Downward displacement into vagina if pelvic floor muscles or cardinal ligaments torn during childbirth.",
    ]),
    Spacer(1,6)
]))

# Abdomen SAQs
story.append(Paragraph("<b>SHORT ANSWER QUESTIONS — ABDOMEN &amp; PELVIS</b>",
                       make_style('saqbara', fontName='Helvetica-Bold', fontSize=12,
                                  textColor=C_SAQ, spaceAfter=6, spaceBefore=6)))

story.extend(saq_heading("SAQ 1: Transpyloric Plane ⭐⭐⭐"))
story.append(body_para("Horizontal plane crossing trunk halfway between jugular notch and pubic symphysis; at level of <b>L1 vertebra</b>."))
story.append(info_box([
    "Pylorus of the stomach.",
    "Hila of both kidneys (left slightly above, right slightly below).",
    "Head and body of the pancreas.",
    "Termination of spinal cord (conus medullaris).",
    "Origin of superior mesenteric artery.",
], title="High-Yield Structures at L1"))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 4: Calot's Triangle ⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Feature", "Structure"],
    [["Inferior (Lateral) boundary", "Cystic duct"],
     ["Medial boundary", "Common hepatic duct"],
     ["Superior boundary", "Inferior surface of the liver"],
     ["Contents", "Cystic artery (typically from right hepatic artery)"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Surgeons must carefully dissect Calot's Triangle during cholecystectomy (gallbladder removal) to safely isolate and ligate the cystic artery and cystic duct without damaging the common hepatic duct."]),
    Spacer(1,6)
]))

story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: GENERAL ANATOMY & GENETICS
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("GENERAL ANATOMY & GENETICS", "Osteology, Genetics & Embryology"))

story.extend(laq_heading("LAQ 1: Blood Supply of a Long Bone ⭐⭐⭐⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Vessel System", "Supplies", "Key Feature"],
    [["Nutrient Artery (primary)", "Inner 2/3rds of compact cortex + medullary cavity", "Enters obliquely through nutrient foramen; splits into ascending & descending branches. Mnemonic: 'To the elbow I go, from the knee I flee'"],
     ["Periosteal Arteries", "Outer 1/3rd of compact cortex", "Derived from surrounding muscles"],
     ["Metaphyseal Arteries", "Zone of ossification (metaphysis)", "Arise from articular vascular networks"],
     ["Epiphyseal Arteries", "Epiphysis (growing cartilage & marrow)", "Arise from joint networks; separate until growth plate fuses"]],
    col_widths=[W*0.25, W*0.3, W*0.45]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Acute Haematogenous Osteomyelitis: Metaphyseal arteries terminate in hairpin-like loops just below epiphyseal plate. Slow blood flow → bacteria settle here → most common site for childhood osteomyelitis."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(saq_heading("SAQ 1: Epiphysis ⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Type", "Location", "Example"],
    [["Pressure Epiphysis", "Weight-bearing ends of bones (transmits body weight)", "Head of femur, condyles of tibia"],
     ["Traction Epiphysis", "Where tendons/muscles attach; subjected to pulling forces; NOT part of joint surface", "Greater/lesser trochanters; greater tubercle of humerus"],
     ["Atavistic Epiphysis", "Phylogenetically independent in lower animals; fused in humans", "Coracoid process of scapula"],
     ["Aberrant Epiphysis", "Non-constant extra epiphysis", "Base of 2nd metacarpal (instead of head)"]],
    col_widths=[W*0.25, W*0.45, W*0.3]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 3: Down's Syndrome (Trisomy 21) ⭐⭐⭐⭐⭐⭐"))
story.append(info_box([
    "Genetic Basis: Three copies of chromosome 21 (Trisomy 21). Caused by meiotic non-disjunction (predominantly maternal). Risk increases with maternal age.",
], title="Genetics"))
story.append(Spacer(1,4))
story.append(make_simple_table(
    ["Feature", "Detail"],
    [["Facies", "Flat facial profile; depressed nasal bridge"],
     ["Eyes", "Upward-slanting palpebral fissures; prominent epicanthic folds"],
     ["Hand", "Single transverse palmar crease (Simian Crease)"],
     ["Tone", "Hypotonia (floppy muscles)"],
     ["Feet", "Wide gap between 1st and 2nd toes"],
     ["Cardiac", "Congenital heart defects (most commonly endocardial cushion defect)"],
     ["CNS", "Severe mental retardation and developmental delay"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 4: Turner's Syndrome (Monosomy X) ⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Feature", "Detail"],
    [["Karyotype", "45, XO"],
     ["Stature", "Short stature; broad webbed neck (pterygium colli)"],
     ["Gonads", "Streak ovaries → primary amenorrhoea and infertility"],
     ["Chest", "Broad shield-like chest with widely spaced nipples"],
     ["Cardiac", "Coarctation of the aorta"],
     ["Intelligence", "Normal intelligence; secondary sexual characteristics fail to develop at puberty"]],
    col_widths=[W*0.28, W*0.72]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 5: Klinefelter's Syndrome ⭐⭐⭐"))
story.append(make_simple_table(
    ["Feature", "Detail"],
    [["Karyotype", "47, XXY (males with extra X chromosome)"],
     ["Stature", "Tall; abnormally long lower limbs (eunuchoid proportions)"],
     ["Gonads", "Small, firm testes; infertility; low testosterone"],
     ["Gynecomastia", "Enlargement of breast tissue in males"],
     ["Hair", "Sparse facial and body hair"],
     ["Cognition", "Mild cognitive impairment or learning disabilities"],
     ["Barr Body", "POSITIVE on buccal smear (abnormal for males)"]],
    col_widths=[W*0.28, W*0.72]
))
story.append(Spacer(1,6))

story.extend(saq_heading("SAQ 6: Barr Body & Lyon's Hypothesis ⭐⭐⭐⭐"))
story.append(info_box([
    "Barr Body: Densely staining mass of condensed chromatin found attached to inner nuclear membrane in somatic cells of females. Represents inactivated X chromosome.",
    "Formula: Number of Barr Bodies = Total X chromosomes − 1.",
    "Lyon's Hypothesis (X-Inactivation): In female embryonic somatic cells, one X chromosome undergoes random, permanent, and complete inactivation early in development (ensures dosage compensation).",
], title="Key Concepts"))
story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: EMBRYOLOGY & HISTOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("SYSTEMIC EMBRYOLOGY & HISTOLOGY", "High-Priority Review"))

story.extend(sub_heading("Pharyngeal Arch Derivatives ⭐⭐⭐⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Arch", "Nerve", "Muscles", "Skeletal Structures"],
    [["1st (Mandibular)", "CN V3 (Mandibular)", "Muscles of mastication (masseter, temporalis, medial & lateral pterygoids); Ant. belly digastric; Mylohyoid; Tensor tympani; Tensor veli palatini",
      "Meckel's cartilage → Malleus, Incus, fibrous template of mandible"],
     ["2nd (Hyoid)", "CN VII (Facial)", "Muscles of facial expression; Post. belly digastric; Stylohyoid; Stapedius",
      "Reichert's cartilage → Stapes, Styloid process, Stylohyoid ligament, Lesser cornu of hyoid"],
     ["3rd", "CN IX (Glossopharyngeal)", "Stylopharyngeus",
      "Greater cornu and lower body of hyoid bone"],
     ["4th & 6th", "CN X (4th: Superior laryngeal n.; 6th: Recurrent laryngeal n.)", "Soft palate muscles; Pharyngeal constrictors; All intrinsic laryngeal muscles",
      "Laryngeal cartilages (thyroid, cricoid, arytenoid)"]],
    col_widths=[W*0.12, W*0.15, W*0.43, W*0.3]
))
story.append(Spacer(1,6))

story.extend(sub_heading("Pharyngeal Pouch Derivatives"))
story.append(make_simple_table(
    ["Pouch", "Derivatives"],
    [["1st Pouch", "Auditory (Eustachian) tube + Middle ear cavity"],
     ["2nd Pouch", "Crypts and lymphoid organisation of Palatine Tonsil"],
     ["3rd Pouch", "Inferior parathyroid glands + Thymus gland (migrates downward)"],
     ["4th Pouch", "Superior parathyroid glands + Ultimobranchial body (→ thyroid C-cells)"]],
    col_widths=[W*0.2, W*0.8]
))
story.append(Spacer(1,6))
story.append(divider())

story.extend(sub_heading("Congenital Heart Anomalies ⭐⭐⭐⭐⭐"))

story.extend(saq_heading("Tetralogy of Fallot (TOF) ⭐⭐⭐⭐⭐"))
story.append(body_para("Caused by abnormal development of the spiral aorticopulmonary septum. Four simultaneous structural anomalies:"))
story.append(make_simple_table(
    ["Component", "Description"],
    [["1. Pulmonary Stenosis", "Narrowing of right ventricular outflow tract"],
     ["2. Ventricular Septal Defect (VSD)", "Hole in the interventricular wall"],
     ["3. Overriding of the Aorta", "Aorta sits over the VSD — receives blood from BOTH ventricles"],
     ["4. Right Ventricular Hypertrophy", "Due to high outflow resistance"]],
    col_widths=[W*0.35, W*0.65]
))
story.append(KeepTogether([
    Spacer(1,4),
    clinical_box(["Blue Baby: Severe cyanosis during crying/feeding.", "Chest X-ray: Classic boot-shaped heart (coeur en sabot)."]),
    Spacer(1,6)
]))

story.extend(saq_heading("Tracheoesophageal Fistula (TEF) ⭐⭐⭐"))
story.append(body_para("Failure of embryonic tracheoesophageal septum to separate respiratory from digestive tract."))
story.append(KeepTogether([
    clinical_box(["Most common variant: Upper oesophagus ends blindly (atresia); lower oesophagus connects to trachea via fistula. At birth: immediate choking, coughing, and regurgitation of milk during first feeding."]),
    Spacer(1,6)
]))
story.append(divider())

story.extend(sub_heading("High-Yield Histology Quick-Review ⭐⭐⭐⭐"))
story.append(make_simple_table(
    ["Tissue / Organ", "Defining Microscopic Characteristics"],
    [["Hyaline Cartilage", "Homogeneous glassy basophilic matrix; chondrocytes in isogenous nests inside lacunae; surrounded by perichondrium"],
     ["Compact Bone", "Concentric layers in Haversian systems (osteons); osteocytes in lacunae connected by canaliculi"],
     ["Elastic Artery (e.g., Aorta)", "Thick tunica media with concentric, wavy sheets of fenestrated elastic fibres"],
     ["Skeletal Muscle", "Long parallel unbranched fibres; transverse striations; multiple peripheral flat nuclei"],
     ["Cardiac Muscle", "Branching fibres; central nuclei; unique transverse intercalated discs"],
     ["Lymph Node", "Capsule; outer cortex with rounded lymphatic nodules (B-cells); inner medulla with medullary cords"],
     ["Thymus", "Incomplete lobules; outer cortex; inner medulla containing Hassall's corpuscles; no lymphatic nodules"]],
    col_widths=[W*0.3, W*0.7]
))
story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# VIVA QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════════
story.extend(chapter_block("VIVA QUESTIONS & ANSWERS", "High-Yield Rapid Revision"))

viva_qs = [
    ("Which nerve is called the musician's nerve and why?",
     "The ulnar nerve — because it controls the fine, highly coordinated movements of the fingers by supplying most of the intrinsic muscles of the hand."),
    ("What structures are found in the carpal tunnel?",
     "Median nerve; 4 tendons of flexor digitorum superficialis; 4 tendons of flexor digitorum profundus; 1 tendon of flexor pollicis longus. (Total: 9 tendons + 1 nerve)"),
    ("Why does a scaphoid fracture often fail to heal?",
     "Because its blood supply enters through the distal pole. A fracture across the waist cuts off blood supply to the proximal pole → non-union and avascular necrosis."),
    ("What is the anatomical basis of a 'winged scapula'?",
     "Injury to the long thoracic nerve → paralysis of serratus anterior → medial border of scapula cannot be held flat against thoracic wall → projects backward."),
    ("What is the Ulnar Paradox?",
     "A low ulnar nerve lesion (at wrist) causes MORE clawing than a high lesion (at elbow), because a high lesion also paralyses FDP, removing the IP joint flexion force."),
    ("What is the Dangerous Layer of the Scalp?",
     "The 4th layer — Loose Areolar Tissue. Infections spread easily across the skull vault and can track inward via emissary veins → meningitis or dural sinus thrombosis."),
    ("What is Courvoisier's Law?",
     "A palpable, non-tender gallbladder with obstructive jaundice suggests carcinoma of the head of the pancreas (NOT gallstones, because gallstone obstruction → contracted gallbladder)."),
    ("Why does the thyroid gland move on swallowing?",
     "Because the false (outer) capsule is derived from the pretracheal fascia, which attaches to the larynx and cricoid cartilage — so the gland moves with laryngeal elevation during swallowing."),
    ("What is Pes Anserinus in the parotid gland?",
     "The branching pattern formed by CN VII dividing within the parotid gland into its 5 terminal branches (Temporal, Zygomatic, Buccal, Marginal Mandibular, Cervical) — resembling a goose's foot."),
    ("What is Frey's Syndrome?",
     "Gustatory sweating — caused by abnormal regeneration following auriculotemporal nerve injury. Parasympathetic fibres misgrow into sympathetic sweat gland pathways → cheek sweats and flushes while eating."),
]

for i, (q, a) in enumerate(viva_qs):
    story.append(KeepTogether([
        Paragraph(f'<b>Q{i+1}.</b> {q}', ST_viva_q),
        Paragraph(f'✔ {a}', ST_viva_a),
        Spacer(1, 5),
    ]))

story.append(divider())

# ─── Last-Minute Revision Sheet ──────────────────────────────────────────────
story.extend(chapter_block("LAST-MINUTE REVISION SHEET", "High-Yield Quick Facts"))

rev_items = [
    ("Mammary Gland Axillary Drainage", "75% to axillary nodes (mainly anterior pectoral group); 20% internal mammary; 5% posterior intercostal."),
    ("Brachial Plexus Cords Relationship", "Named based on their orientation around the SECOND PART of the axillary artery."),
    ("Rotator Cuff Mnemonic", "SITS: Supraspinatus (Superior), Infraspinatus (Posterior), Teres minor (Posterior), Subscapularis (Anterior). Inferior aspect is DEFICIENT."),
    ("Spiral Groove Contents", "Radial nerve + Profunda brachii artery. Humeral shaft fractures can cause wrist drop."),
    ("Scalp — Dangerous Layer", "Layer 4 (Loose Areolar Tissue). Emissary veins track infection inward."),
    ("Diaphragm Openings", "T8: IVC + right phrenic nerve | T10: Oesophagus + vagus nerves | T12: Aorta + thoracic duct + azygos vein."),
    ("Intercostal Neurovascular Bundle", "VAN: Vein–Artery–Nerve in costal groove. Pleural tap: insert needle ABOVE lower rib."),
    ("Sternal Angle (T4–T5)", "Marks: Aortic arch begin/end, trachea bifurcation, pulmonary trunk division, superior/inferior mediastinum boundary."),
    ("Circle of Willis", "Collateral anastomosis of internal carotid + vertebrobasilar systems at base of brain within interpeduncular cistern."),
    ("Portal Hypertension Signs", "Oesophageal varices + Haemorrhoids + Caput Medusae = Portocaval anastomosis opening up."),
    ("Carpal Tunnel Contents", "Median nerve + 9 tendons (4 FDS + 4 FDP + 1 FPL). Everything but ulnar nerve/artery."),
    ("Unhappy Triad of O'Donoghue", "ACL + Tibial Collateral Ligament + Medial Meniscus (all torn together by valgus blow with foot fixed)."),
    ("Tongue Motor Supply", "ALL tongue muscles = CN XII (hypoglossal), EXCEPT palatoglossus = CN X via pharyngeal plexus."),
    ("Erb's vs. Klumpke's", "Erb's: C5,C6 → Waiter's tip. Klumpke's: C8,T1 → True Claw Hand + possible Horner's syndrome."),
    ("Barr Body Formula", "Number of Barr Bodies = Total X chromosomes − 1."),
]

for title, detail in rev_items:
    row_data = [[
        Paragraph(f'<b>{title}</b>',
                  make_style(f'rt{title[:4]}', fontName='Helvetica-Bold', fontSize=9.5,
                             textColor=C_DARK_BLUE, leading=14)),
        Paragraph(detail, ST_body)
    ]]
    t = Table(row_data, colWidths=[W*0.35, W*0.65])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,0), colors.HexColor("#E8EAF6")),
        ('GRID',          (0,0), (-1,-1), 0.3, colors.HexColor("#C5CAE9")),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
    ]))
    story.append(t)

story.append(Spacer(1, 20))

# Final note
final_table = Table([[Paragraph(
    '<font color="white"><b>All content is preserved exactly as in the original source. '
    'Only formatting and visual organisation have been enhanced for clarity and exam readiness.</b></font>',
    make_style('final', fontName='Helvetica', fontSize=9.5, textColor=colors.white,
               alignment=TA_CENTER, leading=15))]],
    colWidths=[W]
)
final_table.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), C_DARK_BLUE),
    ('TOPPADDING',    (0,0), (-1,-1), 12),
    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ('LEFTPADDING',   (0,0), (-1,-1), 12),
    ('RIGHTPADDING',  (0,0), (-1,-1), 12),
    ('ROUNDEDCORNERS', [8]),
]))
story.append(KeepTogether([final_table]))

# ─────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────
output_path = "c:/Users/samee/Downloads/doc/Anatomy_Enhanced_Notes.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=2*cm,
    rightMargin=2*cm,
    topMargin=2.5*cm,
    bottomMargin=2.2*cm,
    title="Anatomy — Complete Notes & Exam-Oriented Answers",
    author="Enhanced Format",
    subject="Medical Anatomy",
)

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {output_path}")
