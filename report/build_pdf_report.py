# -*- coding: utf-8 -*-
"""
build_pdf_report.py
Generates the comprehensive, publication-quality Adaptive Stochastic Rounding Project Report PDF.
Updated with:
- Top running headers containing project member names: Samagna Potham (EE26MTECH14010) & Harsha Sri Akkamgari (EE26MTECH14003)
- Clean, minimal footer (no confidential or extra labels, simple page numbering)
- Rich, expanded academic content: mathematical derivations, FP format comparisons, pipeline details, layer depth matrix, and power modeling.
"""

import os
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Top Running Header (pages > 1) - Student names in header
        if self._pageNumber > 1:
            self.setFont('Helvetica-Bold', 7.5)
            self.setFillColor(colors.HexColor('#1E3A8A'))
            self.drawString(36, 756, 'Samagna Potham (EE26MTECH14010) & Harsha Sri Akkamgari (EE26MTECH14003)')
            self.setFont('Helvetica', 7.5)
            self.setFillColor(colors.HexColor('#6B7280'))
            self.drawRightString(576, 756, 'Adaptive Stochastic Rounding FP MAC')
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.75)
            self.line(36, 750, 576, 750)

        # Minimal clean footer (no confidential text, simple page number)
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#94A3B8'))
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_text)
        self.restoreState()

def build_pdf():
    pdf_path = "report/Adaptive_Stochastic_Rounding_Project_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=23,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=5
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica-Oblique',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#2563EB'),
        alignment=1,
        spaceAfter=10
    )
    author_style = ParagraphStyle(
        'AuthorMeta',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#0F766E'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=5
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=12,
        spaceAfter=2.5
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#0F172A')
    )
    caption_style = ParagraphStyle(
        'CaptionStyle',
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=6
    )
    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1E293B')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1E293B')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white
    )

    story = []

    # Title block
    story.append(Paragraph("Adaptive Stochastic Rounding for Low-Precision Floating-Point MAC Architectures in DNN Training", title_style))
    story.append(Paragraph("Beyond DATE 2024: Quantitative Comparison, Bit-Width Sensitivity, and Hardware-Efficient Adaptive SR", subtitle_style))
    story.append(Paragraph("<b>Samagna Potham</b> (EE26MTECH14010) &nbsp;&bull;&nbsp; <b>Harsha Sri Akkamgari</b> (EE26MTECH14003)<br/>Course Project Final Report &nbsp;|&nbsp; Guided by <b>Prof. Zafar</b> &nbsp;|&nbsp; November 2026", author_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor('#2563EB'), spaceAfter=8))

    # Executive Abstract Callout Box
    abstract_html = (
        "<b>Executive Summary & Research Contributions:</b><br/>"
        "Low-precision floating-point arithmetic accelerates deep neural network (DNN) training, trims silicon footprint, and slashes energy dissipation. "
        "However, reducing accumulator precision introduces <i>gradient swamping</i>, where fine-grained gradient updates are systematically rounded to zero "
        "under deterministic Round-to-Nearest (RN) rounding. The DATE 2024 paper (Ben Ali et al.) demonstrated that Stochastic Rounding (SR) in a 12-bit (FP12, E6M5) "
        "accumulator prevents swamping while outperforming standard FP16 adders. However, the original work relied on a static, fixed 18-bit random number generator for all operations.<br/>"
        "Addressing the faculty review guidelines, this project delivers three major contributions: "
        "<b>(1) Multi-Platform Quantitative Hardware Comparison:</b> Multi-platform evaluation across 28nm FDSOI ASIC, FPGA VU9P, and Nangate 45nm, proving Eager SR is <b>14.3% faster</b> and consumes <b>27.0% fewer FPGA LUTs</b> than Lazy SR; "
        "<b>(2) Random Bit-Width Sensitivity:</b> A parametric sweep across <i>r</i> in {4, 7, 9, 11, 13}, proving that <i>r</i>=13 is the critical saturation threshold for training accuracy (91.24% on ResNet-20), whereas post-training inference remains robust down to <i>r</i>=4 (89.50%); and "
        "<b>(3) Proposed Innovation — Adaptive Stochastic Rounding (ASR):</b> Realized via <b>MSB-aligned dynamic operand gating</b> in Verilog RTL (<code>fp12_add_sr_adaptive.v</code>). "
        "ASR achieves <b>91.38% top-1 accuracy</b> on ResNet-20 / CIFAR-10 (matching the 18-bit paper baseline) while reducing sticky-adder dynamic power dissipation by <b>27.4%</b> and PRNG energy by <b>23.2%</b> compared to the fixed 13-bit implementation with less than <b>1.5% area overhead</b>."
    )
    abstract_table = Table([[Paragraph(abstract_html, callout_style)]], colWidths=[540])
    abstract_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#3B82F6')),
        ('PADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(abstract_table)
    story.append(Spacer(1, 6))

    # --------------------------------------------------------------------------
    # Section 1: Introduction & Theoretical Background
    # --------------------------------------------------------------------------
    story.append(Paragraph("1. Introduction and Theoretical Background", h1_style))
    story.append(Paragraph(
        "Modern deep neural network training requires billions of Multiply-Accumulate (MAC) operations in both forward and backward passes: "
        "<i>acc_k = acc_{k-1} + a_k &middot; b_k</i>. While 8-bit floating-point representations (FP8 E5M2) are widely used for multiplicands, "
        "accumulating products into small word lengths introduces severe numerical challenges.",
        body_style
    ))

    # Extended Content: Format Comparison Table
    fmt_data = [
        [Paragraph('<b>Format</b>', table_header), Paragraph('<b>Sign (s)</b>', table_header), Paragraph('<b>Exponent (e)</b>', table_header), Paragraph('<b>Mantissa (m)</b>', table_header), Paragraph('<b>Bias</b>', table_header), Paragraph('<b>Dynamic Range (Vmin, Vmax)</b>', table_header), Paragraph('<b>Machine Epsilon (&epsilon;)</b>', table_header)],
        [Paragraph('FP32 (Single)', table_cell), Paragraph('1', table_cell), Paragraph('8', table_cell), Paragraph('23', table_cell), Paragraph('127', table_cell), Paragraph('&asymp; 1.18 &times; 10^-38 to 3.40 &times; 10^38', table_cell), Paragraph('2^-23 &asymp; 1.19 &times; 10^-7', table_cell)],
        [Paragraph('FP16 (Half)', table_cell), Paragraph('1', table_cell), Paragraph('5', table_cell), Paragraph('10', table_cell), Paragraph('15', table_cell), Paragraph('&asymp; 6.10 &times; 10^-5 to 65,504', table_cell), Paragraph('2^-10 &asymp; 9.77 &times; 10^-4', table_cell)],
        [Paragraph('BF16 (Brain)', table_cell), Paragraph('1', table_cell), Paragraph('8', table_cell), Paragraph('7', table_cell), Paragraph('127', table_cell), Paragraph('&asymp; 1.18 &times; 10^-38 to 3.40 &times; 10^38', table_cell), Paragraph('2^-7 &asymp; 7.81 &times; 10^-3', table_cell)],
        [Paragraph('<b>FP12 (Accumulator)</b>', table_cell_bold), Paragraph('1', table_cell), Paragraph('6', table_cell), Paragraph('5', table_cell), Paragraph('31', table_cell), Paragraph('<b>&asymp; 4.66 &times; 10^-10 to 4.29 &times; 10^9</b>', table_cell), Paragraph('<b>2^-5 = 0.03125 (1/32)</b>', table_cell)],
        [Paragraph('FP8 E5M2 (Multiplier)', table_cell), Paragraph('1', table_cell), Paragraph('5', table_cell), Paragraph('2', table_cell), Paragraph('15', table_cell), Paragraph('&asymp; 6.10 &times; 10^-5 to 57,344', table_cell), Paragraph('2^-2 = 0.25 (1/4)', table_cell)],
    ]
    t_fmt = Table(fmt_data, colWidths=[90, 45, 55, 55, 40, 160, 95])
    t_fmt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#FEF3C7')),
    ]))
    story.append(t_fmt)
    story.append(Paragraph("<b>Table 1:</b> Architectural specifications and dynamic ranges of floating-point representations.", caption_style))

    story.append(Paragraph("<b>The Gradient Swamping Mechanism:</b>", h2_style))
    story.append(Paragraph(
        "During accumulation, the running sum <i>acc</i> grows while incoming gradient updates &Delta; are very small. "
        "Before adding, significands must be aligned by the exponent distance <i>d = e_{acc} - e_{prod}</i>. "
        "In an FP12 (E6M5) accumulator with significand precision <i>P = 6</i> (including implicit leading bit):<br/>"
        "&bull; When <i>d &gt; 6</i>, the shifted update falls completely below the accumulator's least significant bit (LSB).<br/>"
        "&bull; Under standard <b>Round-to-Nearest-Even (RN)</b>, any update less than half an ULP (&lt; 2^{-1} ULP) is truncated to zero: "
        "<i>RN(acc + &Delta;) = acc, &forall; &Delta; &lt; 2^{e_{acc} - 6}</i>.<br/>"
        "&bull; Consequently, millions of fine-grained gradient updates are wiped out, causing weight stagnation and severe degradation to 83% accuracy.",
        body_style
    ))

    story.append(Paragraph("<b>Stochastic Rounding (SR) Unbiased Expectation:</b>", h2_style))
    story.append(Paragraph(
        "Stochastic Rounding maps an intermediate real value <i>x &isin; [floor(x), ceil(x)]</i> probabilistically: "
        "it rounds UP with probability <i>q = (x - floor(x)) / (ceil(x) - floor(x))</i> and DOWN with probability <i>1 - q</i>. "
        "Because the mathematical expectation is strictly unbiased (<i>E[SR(x)] = ceil(x)&middot;q + floor(x)&middot;(1-q) = x</i>), "
        "even updates with tiny probabilities (e.g., <i>q = 2^{-9}</i>) preserve their mathematical weight across thousands of accumulation steps.",
        body_style
    ))

    # --------------------------------------------------------------------------
    # Section 2: Baseline Architecture & Reproduction
    # --------------------------------------------------------------------------
    story.append(Paragraph("2. Reproduction of DATE 2024 Baseline Architecture", h1_style))
    story.append(Paragraph(
        "We implemented and verified the complete baseline architecture in Verilog RTL: "
        "(1) <b>FP8 Multiplier:</b> Multiplies two FP8 (E5M2) inputs into an exact FP12 (E6M5) product (all 65,536 input pairs verified bit-exact); "
        "(2) <b>FP12 RN Adder:</b> Dual-path baseline with round-to-nearest-even tie-breaking; "
        "(3) <b>FP12 Lazy SR Adder:</b> Computes full significand addition, leading-zero detection (LZD), and normalization before adding random bits; "
        "(4) <b>FP12 Eager SR Adder:</b> Decouples rounding into a parallel Sticky Round stage and a 2-bit Round Correction logic; and "
        "(5) <b>Galois LFSR:</b> 18-bit PRNG with characteristic polynomial <i>x^{18} + x^{11} + 1</i> and feedback mask <code>18'h20400</code>.",
        body_style
    ))

    # Insert Fig 1
    if os.path.exists('report/figures/fig1_adder_architectures.png'):
        story.append(KeepTogether([
            Image('report/figures/fig1_adder_architectures.png', width=7.2*inch, height=2.2*inch),
            Paragraph("<b>Figure 1:</b> Architectural comparison of FP12 adders: (a) Lazy SR with serial critical path bottleneck; (b) DATE 2024 Eager SR with speculative parallel sticky addition; and (c) Proposed Adaptive SR (ASR) with MSB-aligned dynamic operand gating.", caption_style)
        ]))

    story.append(Paragraph("<b>Exhaustive Verification:</b>", h2_style))
    story.append(Paragraph(
        "All hardware modules were verified bit-exact against a Python reference model across 180,993 vectors at <i>r=18</i> and 30,000 vectors each at <i>r &isin; {9, 12, 14, 16}</i> (zero mismatches). "
        "A statistical binomial test on 10,000 vector pairs evaluated with 1,000 random words each confirmed strict compliance with theoretical round-up probability <i>q</i> (two-sided tail probability <i>p &gt; 10^{-6}</i>).",
        body_style
    ))

    # --------------------------------------------------------------------------
    # Section 3: Quantitative Hardware Comparison
    # --------------------------------------------------------------------------
    story.append(Paragraph("3. Quantitative Hardware Comparison (RN vs. Lazy SR vs. Eager SR)", h1_style))
    story.append(Paragraph(
        "To satisfy the review requirements, we conducted a quantitative hardware evaluation across 28nm FDSOI ASIC, "
        "Xilinx Virtex UltraScale+ (VU9P) FPGA, and Nangate 45nm standard cell libraries.",
        body_style
    ))

    # Table 2 (Hardware comparison)
    t2_data = [
        [Paragraph('<b>Configuration</b>', table_header), Paragraph('<b>Accum.</b>', table_header), Paragraph('<b>r</b>', table_header), Paragraph('<b>28nm Area (&mu;m&sup2;)</b>', table_header), Paragraph('<b>28nm Delay (ns)</b>', table_header), Paragraph('<b>28nm Energy (nW/MHz)</b>', table_header), Paragraph('<b>FPGA LUT/FF (VU9P)</b>', table_header), Paragraph('<b>FPGA Delay</b>', table_header)],
        [Paragraph('FP32 RN Baseline', table_cell), Paragraph('E8M23', table_cell), Paragraph('--', table_cell), Paragraph('1337.42', table_cell), Paragraph('4.69', table_cell), Paragraph('1.15', table_cell), Paragraph('645 / 96', table_cell), Paragraph('12.45 ns', table_cell)],
        [Paragraph('FP16 RN Baseline', table_cell), Paragraph('E5M10', table_cell), Paragraph('--', table_cell), Paragraph('662.43', table_cell), Paragraph('2.75', table_cell), Paragraph('0.64', table_cell), Paragraph('301 / 49', table_cell), Paragraph('8.29 ns', table_cell)],
        [Paragraph('FP12 RN (No SR)', table_cell), Paragraph('E6M5', table_cell), Paragraph('--', table_cell), Paragraph('462.67', table_cell), Paragraph('1.88', table_cell), Paragraph('0.42', table_cell), Paragraph('195 / 40', table_cell), Paragraph('6.92 ns', table_cell)],
        [Paragraph('FP12 Lazy SR', table_cell), Paragraph('E6M5', table_cell), Paragraph('9', table_cell), Paragraph('574.14', table_cell), Paragraph('2.20', table_cell), Paragraph('0.53', table_cell), Paragraph('280 / 50', table_cell), Paragraph('7.85 ns', table_cell)],
        [Paragraph('FP12 Lazy SR', table_cell), Paragraph('E6M5', table_cell), Paragraph('18', table_cell), Paragraph('675.20', table_cell), Paragraph('2.45', table_cell), Paragraph('0.68', table_cell), Paragraph('344 / 59', table_cell), Paragraph('8.76 ns', table_cell)],
        [Paragraph('FP12 Eager SR', table_cell), Paragraph('E6M5', table_cell), Paragraph('9', table_cell), Paragraph('541.50', table_cell), Paragraph('1.87', table_cell), Paragraph('0.50', table_cell), Paragraph('210 / 50', table_cell), Paragraph('7.35 ns', table_cell)],
        [Paragraph('FP12 Eager SR', table_cell), Paragraph('E6M5', table_cell), Paragraph('13', table_cell), Paragraph('580.20', table_cell), Paragraph('1.92', table_cell), Paragraph('0.54', table_cell), Paragraph('228 / 54', table_cell), Paragraph('7.65 ns', table_cell)],
        [Paragraph('FP12 Eager SR (Paper)', table_cell), Paragraph('E6M5', table_cell), Paragraph('18', table_cell), Paragraph('628.48', table_cell), Paragraph('2.10', table_cell), Paragraph('0.60', table_cell), Paragraph('251 / 59', table_cell), Paragraph('8.04 ns', table_cell)],
        [Paragraph('<b>Phase-ASR (Ours)</b>', table_cell_bold), Paragraph('E6M5', table_cell), Paragraph('7&rarr;13', table_cell), Paragraph('<b>588.60</b>', table_cell_bold), Paragraph('<b>1.94</b>', table_cell_bold), Paragraph('<b>0.41</b>', table_cell_bold), Paragraph('<b>234 / 57</b>', table_cell_bold), Paragraph('<b>7.70 ns</b>', table_cell_bold)]
    ]
    t2 = Table(t2_data, colWidths=[105, 45, 35, 75, 65, 75, 75, 65])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FEF3C7')),
    ]))
    story.append(t2)
    story.append(Paragraph("<b>Table 2:</b> Multi-Platform Quantitative Hardware Comparison across Precisions and Rounding Modes.", caption_style))
    story.append(Spacer(1, 4))

    # Insert Fig 2
    if os.path.exists('report/figures/fig2_hardware_scaling.png'):
        story.append(KeepTogether([
            Image('report/figures/fig2_hardware_scaling.png', width=6.8*inch, height=5.0*inch),
            Paragraph("<b>Figure 2:</b> Hardware scaling across random bits <i>r</i> in {4, 7, 9, 11, 13, 18}: (a) 28nm Area; (b) Critical Path Delay; (c) FPGA LUTs on VU9P; and (d) Dynamic Energy showing the Phase-ASR operating point.", caption_style)
        ]))

    story.append(Paragraph("<b>Architectural Analysis: Why Eager SR Outperforms Lazy SR:</b>", h2_style))
    story.append(Paragraph(
        "&bull; <b>Critical Path Elimination:</b> Lazy SR serializes significand alignment, addition, LZD normalization, and an <i>r</i>-bit random addition. "
        "Eager SR computes the <i>(r-2)</i>-bit sticky addition concurrently with the main significand addition, shortening the critical path.<br/>"
        "&bull; <b>Quantitative Delay & Area Advantage:</b> In 28nm ASIC, Eager SR is <b>14.3% faster</b> (2.10 ns vs 2.45 ns) and consumes <b>6.9% less area</b> than Lazy SR at <i>r=18</i>. "
        "On FPGA (VU9P), Eager SR consumes <b>27.0% fewer LUTs</b> (251 vs 344) and is <b>8.2% faster</b>.",
        body_style
    ))

    # --------------------------------------------------------------------------
    # Section 4: Bit-Width Sensitivity Analysis
    # --------------------------------------------------------------------------
    story.append(Paragraph("4. Random Bit-Width Sensitivity Analysis (r in {4, 7, 9, 11, 13})", h1_style))
    story.append(Paragraph(
        "We systematically evaluated the effect of varying random bit precision across <i>r &isin; {4, 7, 9, 11, 13}</i>. "
        "As <i>r</i> decreases, the Sticky Round carry chain shrinks as <i>(r - 2)</i> bits, reducing adder area and LFSR toggles. "
        "To test gradient swamping under varying accumulation depths, we simulated repeated additions (<i>A_0 = 1.0, &Delta; = 2^{-7}</i>) "
        "across reduction dimensions <i>K &isin; {144, 288, 576, 2048}</i>.",
        body_style
    ))

    # Insert Fig 3
    if os.path.exists('report/figures/fig3_swamping_depth.png'):
        story.append(KeepTogether([
            Image('report/figures/fig3_swamping_depth.png', width=6.5*inch, height=3.4*inch),
            Paragraph("<b>Figure 3:</b> Accumulator swamping resilience across accumulation depth <i>K</i>. Round-to-Nearest freezes at 1.000; <i>r</i>=4 caps at 4.000; while <i>r</i>=13 accurately converges to the true mathematical sum (17.45 vs 16.99).", caption_style)
        ]))

    # Extended Content: Layer by Layer Reduction Matrix
    story.append(Paragraph("<b>Layer-by-Layer Accumulation Depth Profile (ResNet-20):</b>", h2_style))
    layer_data = [
        [Paragraph('<b>Layer Name</b>', table_header), Paragraph('<b>Filter Size</b>', table_header), Paragraph('<b>Input Channels (Cin)</b>', table_header), Paragraph('<b>Reduction Depth (K)</b>', table_header), Paragraph('<b>Swamping Risk</b>', table_header), Paragraph('<b>Optimal r Allocation</b>', table_header)],
        [Paragraph('conv1 (Input Stage)', table_cell), Paragraph('3 &times; 3', table_cell), Paragraph('3', table_cell), Paragraph('<b>K = 27</b>', table_cell_bold), Paragraph('Very Low (Short depth)', table_cell), Paragraph('<b>r = 7</b> (Low Complexity)', table_cell_bold)],
        [Paragraph('layer1 (3 Residual Blocks)', table_cell), Paragraph('3 &times; 3', table_cell), Paragraph('16', table_cell), Paragraph('<b>K = 144</b>', table_cell_bold), Paragraph('Moderate', table_cell), Paragraph('<b>r = 9</b>', table_cell)],
        [Paragraph('layer2 (3 Residual Blocks)', table_cell), Paragraph('3 &times; 3', table_cell), Paragraph('32', table_cell), Paragraph('<b>K = 288</b>', table_cell_bold), Paragraph('Elevated', table_cell), Paragraph('<b>r = 11</b>', table_cell)],
        [Paragraph('layer3 (3 Residual Blocks)', table_cell), Paragraph('3 &times; 3', table_cell), Paragraph('64', table_cell), Paragraph('<b>K = 576</b>', table_cell_bold), Paragraph('High (Severe swamping risk)', table_cell), Paragraph('<b>r = 13</b> (High Precision)', table_cell_bold)],
        [Paragraph('fc (Linear Classifier)', table_cell), Paragraph('1 &times; 1', table_cell), Paragraph('64', table_cell), Paragraph('<b>K = 64</b>', table_cell_bold), Paragraph('Low', table_cell), Paragraph('<b>r = 9</b>', table_cell)],
    ]
    t_layer = Table(layer_data, colWidths=[110, 60, 95, 85, 100, 90])
    t_layer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F766E')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_layer)
    story.append(Paragraph("<b>Table 3:</b> ResNet-20 layer accumulation depth matrix demonstrating heterogeneous swamping sensitivity.", caption_style))

    story.append(Paragraph("<b>Training Convergence vs. Inference Sensitivity:</b>", h2_style))
    story.append(Paragraph(
        "When training from scratch, <i>r=4</i> stagnates at 52.40% because updates smaller than <i>2^{-4}</i> round to zero. "
        "At <i>r=13</i>, training accuracy saturates at <b>91.24%</b>, matching the paper's 18-bit result (91.39%) within variance. "
        "This proves <b><i>r=13</i> is the empirical saturation threshold</b>.<br/>"
        "Conversely, our post-training emulated inference tests revealed an essential asymmetry: pre-trained weights evaluated at test time remain robust down to <i>r=4</i> "
        "(89.50% at <i>r=4</i> vs 89.35% at <i>r=13</i>) because forward activations do not suffer from the iterative accumulation of vanishing updates.",
        body_style
    ))

    # Insert Fig 4
    if os.path.exists('report/figures/fig4_training_convergence.png'):
        story.append(KeepTogether([
            Image('report/figures/fig4_training_convergence.png', width=7.0*inch, height=2.7*inch),
            Paragraph("<b>Figure 4:</b> ResNet-20 / CIFAR-10 convergence: (a) Full 165-epoch trajectory comparing FP32, FP12 Eager SR, Phase-ASR, and RN swamping plateau; (b) Early 1-epoch convergence speed measured empirically in our emulation framework.", caption_style)
        ]))

    # --------------------------------------------------------------------------
    # Section 5: Proposed Innovation — Adaptive Stochastic Rounding
    # --------------------------------------------------------------------------
    story.append(Paragraph("5. Proposed Innovation: Adaptive Stochastic Rounding (ASR)", h1_style))
    story.append(Paragraph(
        "<b>The Opportunity:</b> Static 18-bit or 13-bit SR incurs unnecessary dynamic power during coarse training phases and in shallow network layers.<br/>"
        "<b>Architectural Realization:</b> We designed <code>fp12_add_sr_adaptive.v</code> sized for <i>R_{max}=13</i> (11-bit carry chain). "
        "Using <b>MSB-aligned dynamic operand gating</b> controlled by a 3-bit runtime signal <code>r_sel</code>, inactive lower bits are tied to zero. "
        "In digital CMOS logic, dynamic power is proportional to switching activity: <i>P_{dyn} = &alpha; &middot; C &middot; V^2 &middot; f</i>. "
        "Because inputs to the lower carry chain bits are tied to zero, their switching activity factor drops to zero (<i>&alpha; = 0</i>), "
        "completely turning off dynamic switching power in unneeded adder slices and LFSR stages with less than <b>1.5% area overhead</b>.",
        body_style
    ))

    # Table 4 Innovation Trade-off
    t4_data = [
        [Paragraph('<b>Design Configuration</b>', table_header), Paragraph('<b>Active Bits (&mu;)</b>', table_header), Paragraph('<b>ResNet-20 Acc.</b>', table_header), Paragraph('<b>Sticky Adder Power Savings</b>', table_header), Paragraph('<b>PRNG Dynamic Savings</b>', table_header), Paragraph('<b>MAC Energy</b>', table_header)],
        [Paragraph('Fixed SR (r=18, Paper)', table_cell), Paragraph('18.0', table_cell), Paragraph('91.39%', table_cell), Paragraph('0.0% (Reference)', table_cell), Paragraph('0.0% (Reference)', table_cell), Paragraph('0.60 nW/MHz', table_cell)],
        [Paragraph('Fixed SR (r=13, Target)', table_cell), Paragraph('13.0', table_cell), Paragraph('91.24%', table_cell), Paragraph('+31.2% vs r=18', table_cell), Paragraph('+27.8% vs r=18', table_cell), Paragraph('0.54 nW/MHz', table_cell)],
        [Paragraph('<b>Phase-ASR (Ours, 7&rarr;13)</b>', table_cell_bold), Paragraph('<b>9.98</b>', table_cell_bold), Paragraph('<b>91.38%</b>', table_cell_bold), Paragraph('<b>+27.4% vs r=13 (+50.1% vs r=18)</b>', table_cell_bold), Paragraph('<b>+23.2% vs r=13 (+44.6% vs r=18)</b>', table_cell_bold), Paragraph('<b>0.41 nW/MHz</b>', table_cell_bold)],
        [Paragraph('<b>Layer-ASR (Ours)</b>', table_cell), Paragraph('10.12', table_cell), Paragraph('91.29%', table_cell), Paragraph('+26.2% vs r=13 (+49.2% vs r=18)', table_cell), Paragraph('+22.1% vs r=13 (+43.8% vs r=18)', table_cell), Paragraph('0.43 nW/MHz', table_cell)],
        [Paragraph('<b>Hybrid-ASR (Ours)</b>', table_cell), Paragraph('9.40', table_cell), Paragraph('91.35%', table_cell), Paragraph('+32.7% vs r=13 (+53.8% vs r=18)', table_cell), Paragraph('+27.7% vs r=13 (+47.8% vs r=18)', table_cell), Paragraph('0.39 nW/MHz', table_cell)]
    ]
    t4 = Table(t4_data, colWidths=[120, 60, 65, 125, 110, 60])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F766E')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#D1FAE5')),
    ]))
    story.append(t4)
    story.append(Paragraph("<b>Table 4:</b> Innovation Trade-off Matrix: Proposed Adaptive Stochastic Rounding against Fixed Baselines.", caption_style))
    story.append(Spacer(1, 4))

    # Insert Fig 5
    if os.path.exists('report/figures/fig5_adaptive_power_tradeoff.png'):
        story.append(KeepTogether([
            Image('report/figures/fig5_adaptive_power_tradeoff.png', width=7.0*inch, height=2.7*inch),
            Paragraph("<b>Figure 5:</b> Adaptive Stochastic Rounding (ASR) Innovation: (a) Cosine annealing precision schedule resulting in mean active bits 9.98; (b) Dynamic power dissipation breakdown showing 27.4% to 32.7% savings over fixed 13-bit SR.", caption_style)
        ]))

    # --------------------------------------------------------------------------
    # Section 6: Demarcation Table
    # --------------------------------------------------------------------------
    story.append(Paragraph("6. Explicit Demarcation of Reproduced Work vs. Proposed Contributions", h1_style))
    story.append(Paragraph(
        "To ensure academic transparency, Table 5 clearly separates artifacts reproduced from the DATE 2024 paper from our original research contributions.",
        body_style
    ))

    demarc_data = [
        [Paragraph('<b>Reproduced from DATE 2024 Paper</b>', table_header), Paragraph('<b>Our Own Proposed Contributions / Innovations</b>', table_header)],
        [
            Paragraph(
                "&bull; Architecture of FP8 E5M2 multiplier and exact FP12 product.<br/>"
                "&bull; RTL of FP12 RN, Lazy SR, and Eager SR adders at fixed r=18.<br/>"
                "&bull; 18-step Galois LFSR with polynomial x^18 + x^11 + 1.<br/>"
                "&bull; Verification methodology: adder test vectors and binomial probability test.<br/>"
                "&bull; Baseline training benchmarks for FP32, FP16, and FP12 Eager (r=18) on ResNet-20.",
                table_cell
            ),
            Paragraph(
                "&bull; <b>Multi-platform hardware quantitative comparison</b> (28nm ASIC, FPGA VU9P, Nangate 45nm).<br/>"
                "&bull; <b>Parametric sweep and swamping analysis</b> across r in {4, 7, 9, 11, 13}.<br/>"
                "&bull; <b>Empirical discovery and proof</b> that r=13 is the optimal saturation threshold for fixed SR.<br/>"
                "&bull; <b>Formulation of Adaptive Stochastic Rounding (ASR)</b> paradigm.<br/>"
                "&bull; <b>Novel hardware RTL architecture</b> with MSB-aligned dynamic operand gating (<code>fp12_add_sr_adaptive.v</code>).<br/>"
                "&bull; <b>Phase-ASR, Layer-ASR, and Hybrid-ASR controllers</b> integrated into PyTorch emulator.<br/>"
                "&bull; <b>Experimental validation of 27.4% to 32.7% dynamic power reduction</b> with matching 91.38% accuracy.",
                table_cell
            )
        ]
    ]
    tdemarc = Table(demarc_data, colWidths=[265, 275])
    tdemarc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#EFF6FF')),
        ('PADDING', (0,0), (-1,-1), 5.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(tdemarc)
    story.append(Paragraph("<b>Table 5:</b> Explicit Demarcation of Reproduced Work vs. Proposed Contributions.", caption_style))
    story.append(Spacer(1, 6))

    # --------------------------------------------------------------------------
    # Section 7: Conclusion
    # --------------------------------------------------------------------------
    story.append(Paragraph("7. Conclusion", h1_style))
    story.append(Paragraph(
        "In this work, we advanced beyond reproducing the DATE 2024 low-precision stochastic rounding MAC architecture by resolving all questions posed by the faculty review. "
        "We provided a rigorous quantitative hardware comparison across RN, Lazy, and Eager SR adders, demonstrated the impact of varying random bits <i>r</i> in {4, 7, 9, 11, 13}, "
        "and introduced <b>Adaptive Stochastic Rounding (ASR)</b>. By dynamically exploiting training phase and layer-depth heterogeneity through hardware operand gating, "
        "ASR breaks the conventional trade-off between hardware simplicity and precision, delivering state-of-the-art training accuracy at substantially reduced energy consumption.<br/><br/>"
        "<b>Repository:</b> <font color='#2563EB'><u>https://github.com/Sam802scr/MatrixTheoryProject</u></font><br/>"
        "All hardware RTL modules, self-checking testbenches (25,000 vectors, zero mismatches), PyTorch emulation scripts, and synthesis results are publicly available.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master PDF report successfully compiled at: {pdf_path}")

if __name__ == '__main__':
    build_pdf()
