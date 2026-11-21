# -*- coding: utf-8 -*-
"""
generate_presentation.py
Generates a professional 25-slide PowerPoint presentation (.pptx)
featuring IIT Hyderabad logo, Department of Electrical Engineering,
authors Samagna Potham & Harsha Sri Akkamgari, guided by Prof. Zafar,
and comprehensive technical coverage with embedded figures and tables.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    C_NAVY     = RGBColor(15, 44, 89)      # #0F2C59 - Primary
    C_BLUE     = RGBColor(30, 58, 138)     # #1E3A8A - Headers
    C_TEAL     = RGBColor(15, 118, 110)    # #0F766E - Secondary
    C_ORANGE   = RGBColor(217, 119, 6)     # #D97706 - Accent
    C_DARK     = RGBColor(30, 41, 59)      # #1E293B - Body text
    C_MUTED    = RGBColor(100, 116, 139)   # #64748B - Subtitles/Meta
    C_BG_CARD  = RGBColor(248, 250, 252)   # #F8FAFC - Card background
    C_BORDER   = RGBColor(203, 213, 225)   # #CBD5E1 - Border
    C_WHITE    = RGBColor(255, 255, 255)
    C_GOLD     = RGBColor(245, 158, 11)

    logo_path = 'report/figures/iith_logo.png'

    # Helper: Add Header & Running Tracker to Slide
    def add_slide_header(slide, title_text, category_text="COURSE PROJECT PRESENTATION"):
        # Category Banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = 'Helvetica'
        p_cat.font.size = Pt(9)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(10.5), Inches(0.65))
        tf = t_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = 'Helvetica'
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = C_NAVY

        # Accent Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.025))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.color.rgb = C_BORDER

        # Mini student header top right
        meta_box = slide.shapes.add_textbox(Inches(8.5), Inches(0.4), Inches(4.0), Inches(0.35))
        tf_meta = meta_box.text_frame
        p_meta = tf_meta.paragraphs[0]
        p_meta.text = "S. Potham & H. S. Akkamgari | EE, IITH"
        p_meta.font.name = 'Helvetica'
        p_meta.font.size = Pt(8.5)
        p_meta.font.color.rgb = C_MUTED
        p_meta.alignment = PP_ALIGN.RIGHT

    # Helper: Add Content Card
    def add_card(slide, left, top, width, height, bg_color=C_BG_CARD, border_color=C_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # ==========================================================================
    # SLIDE 1: Title Slide (with IIT Hyderabad Logo)
    # ==========================================================================
    s1 = prs.slides.add_slide(blank_layout)

    # Top banner background card
    add_card(s1, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3), C_WHITE, C_BORDER)

    # IITH Logo
    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(1.2), Inches(1.0), width=Inches(3.8))

    # Department & Institute Header
    dept_box = s1.shapes.add_textbox(Inches(5.5), Inches(1.0), Inches(6.6), Inches(1.1))
    tf_dept = dept_box.text_frame
    p_dept1 = tf_dept.paragraphs[0]
    p_dept1.text = "DEPARTMENT OF ELECTRICAL ENGINEERING"
    p_dept1.font.name = 'Helvetica'
    p_dept1.font.size = Pt(13)
    p_dept1.font.bold = True
    p_dept1.font.color.rgb = C_NAVY
    p_dept2 = tf_dept.add_paragraph()
    p_dept2.text = "INDIAN INSTITUTE OF TECHNOLOGY HYDERABAD"
    p_dept2.font.name = 'Helvetica'
    p_dept2.font.size = Pt(11)
    p_dept2.font.bold = True
    p_dept2.font.color.rgb = C_MUTED

    # Title & Subtitle Card
    title_card = add_card(s1, Inches(1.2), Inches(2.2), Inches(10.933), Inches(2.4), C_BG_CARD, C_BORDER)
    t_box = s1.shapes.add_textbox(Inches(1.5), Inches(2.35), Inches(10.3), Inches(2.1))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True

    p_t = tf_t.paragraphs[0]
    p_t.text = "Adaptive Stochastic Rounding for Low-Precision Floating-Point MAC Architectures in DNN Training"
    p_t.font.name = 'Helvetica'
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Beyond DATE 2024: Quantitative Comparison, Bit-Width Sensitivity, and Hardware-Efficient Adaptive SR"
    p_sub.font.name = 'Helvetica'
    p_sub.font.size = Pt(13)
    p_sub.font.bold = True
    p_sub.font.color.rgb = C_TEAL
    p_sub.space_before = Pt(8)

    # Authors Card (Left)
    auth_card = add_card(s1, Inches(1.2), Inches(4.8), Inches(5.3), Inches(1.8), C_WHITE, C_BORDER)
    abox = s1.shapes.add_textbox(Inches(1.4), Inches(4.9), Inches(4.9), Inches(1.6))
    atf = abox.text_frame
    ap1 = atf.paragraphs[0]
    ap1.text = "PROJECT MEMBERS"
    ap1.font.name = 'Helvetica'
    ap1.font.size = Pt(9.5)
    ap1.font.bold = True
    ap1.font.color.rgb = C_TEAL

    ap2 = atf.add_paragraph()
    ap2.text = "• Samagna Potham (EE26MTECH14010)"
    ap2.font.name = 'Helvetica'
    ap2.font.size = Pt(11)
    ap2.font.bold = True
    ap2.font.color.rgb = C_DARK
    ap2.space_before = Pt(4)

    ap3 = atf.add_paragraph()
    ap3.text = "• Harsha Sri Akkamgari (EE26MTECH14003)"
    ap3.font.name = 'Helvetica'
    ap3.font.size = Pt(11)
    ap3.font.bold = True
    ap3.font.color.rgb = C_DARK
    ap3.space_before = Pt(4)

    # Guide & Metadata Card (Right)
    guide_card = add_card(s1, Inches(6.8), Inches(4.8), Inches(5.3), Inches(1.8), C_WHITE, C_BORDER)
    gbox = s1.shapes.add_textbox(Inches(7.0), Inches(4.9), Inches(4.9), Inches(1.6))
    gtf = gbox.text_frame
    gp1 = gtf.paragraphs[0]
    gp1.text = "GUIDED BY"
    gp1.font.name = 'Helvetica'
    gp1.font.size = Pt(9.5)
    gp1.font.bold = True
    gp1.font.color.rgb = C_TEAL

    gp2 = gtf.add_paragraph()
    gp2.text = "Prof. Zafar"
    gp2.font.name = 'Helvetica'
    gp2.font.size = Pt(12)
    gp2.font.bold = True
    gp2.font.color.rgb = C_NAVY
    gp2.space_before = Pt(4)

    gp3 = gtf.add_paragraph()
    gp3.text = "Course: Matrix Theory & Numerical Linear Algebra in VLSI / DL\nNovember 2026"
    gp3.font.name = 'Helvetica'
    gp3.font.size = Pt(9.5)
    gp3.font.color.rgb = C_MUTED
    gp3.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 2: Executive Overview & Faculty Review Mandate
    # ==========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, "Executive Overview & Faculty Review Mandate", "PROJECT SCOPE")

    add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    b1 = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf1 = b1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "The Research Challenge"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_NAVY

    bullets1 = [
        "<b>Low-Precision Trend:</b> Transitioning DNN matrix multiplications from FP32/FP16 to FP8 (E5M2) multiplicands significantly reduces silicon area and power.",
        "<b>The Swamping Problem:</b> In low-precision FP12 accumulators, tiny gradient updates vanish under Round-to-Nearest (RN) rounding (accuracy plateaus at 83%).",
        "<b>DATE 2024 Baseline:</b> Ben Ali et al. proposed FP12 Eager Stochastic Rounding (SR), but relied on a static, expensive 18-bit random number generator for all operations."
    ]
    for b in bullets1:
        p = tf1.add_paragraph()
        p.text = b.replace('<b>','').replace('</b>','')
        p.font.size = Pt(10.5)
        p.space_before = Pt(10)

    add_card(s2, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    b2 = s2.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf2 = b2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Mandate from Prof. Zafar & Our Deliverables"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = C_TEAL

    bullets2 = [
        "<b>Point 1 (Hardware Comparison):</b> Comprehensive area, delay, LUT, FF, and energy comparison of RN, Lazy SR, and Eager SR across ASIC and FPGA.",
        "<b>Point 2 (Convergence vs Baselines):</b> Verify convergence against FP16 and FP32 baselines on ResNet-20 / CIFAR-10.",
        "<b>Point 3 (Bit-Width Sensitivity):</b> Parametric sweep across r ∈ {4, 7, 9, 11, 13}; identify the true saturation threshold.",
        "<b>Point 4 (Original Innovation):</b> Propose Adaptive Stochastic Rounding (ASR) to achieve baseline accuracy with lower hardware complexity than fixed 13-bit SR.",
        "<b>Point 5 (Academic Demarcation):</b> Strictly separate paper reproduction from novel contributions."
    ]
    for b in bullets2:
        p = tf2.add_paragraph()
        p.text = b.replace('<b>','').replace('</b>','')
        p.font.size = Pt(10)
        p.space_before = Pt(7)

    # ==========================================================================
    # SLIDE 3: Multiply-Accumulate (MAC) Operations in Deep Learning
    # ==========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "Multiply-Accumulate (MAC) Operations in Deep Learning", "THEORETICAL FOUNDATION")

    cards_data = [
        ("Forward GEMM (Inference & Activation)", "Y = W · X", "Computes layer activations. In ResNet-20, input dimensions span Cin=3 to 64. Output activations are preserved accurately even under coarse precision."),
        ("Backward Activation GEMM (dgrad)", "dX = W^T · dY", "Propagates error gradients back to previous layers. Requires balanced dynamic range to prevent vanishing backprop gradients."),
        ("Backward Weight GEMM (wgrad)", "dW = dY · X^T", "Iteratively accumulates parameter gradients. Highly susceptible to swamping because fine updates (d < 2^-7) must sum into large running weights.")
    ]
    for idx, (head, eq, desc) in enumerate(cards_data):
        top_pos = Inches(1.6 + idx * 1.75)
        add_card(s3, Inches(0.8), top_pos, Inches(11.733), Inches(1.5))
        cbox = s3.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.15), Inches(11.1), Inches(1.2))
        ctf = cbox.text_frame
        cp = ctf.paragraphs[0]
        cp.text = f"{head} — {eq}"
        cp.font.bold = True
        cp.font.size = Pt(12)
        cp.font.color.rgb = C_NAVY

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.size = Pt(10.5)
        cp2.font.color.rgb = C_DARK
        cp2.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 4: Floating-Point Representations Comparison
    # ==========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "Floating-Point Spectrum & Format Specifications", "NUMBER SYSTEMS")

    rows = 6; cols = 7
    table_shape = s4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.7), Inches(11.733), Inches(4.5))
    table = table_shape.table

    table_data = [
        ["Format", "Sign", "Exp (e)", "Mant (m)", "Bias", "Dynamic Range (Vmin, Vmax)", "Machine Epsilon (ε)"],
        ["FP32 (Single)", "1", "8", "23", "127", "1.18 × 10^-38 to 3.40 × 10^38", "2^-23 ≈ 1.19 × 10^-7"],
        ["FP16 (Half)", "1", "5", "10", "15", "6.10 × 10^-5 to 65,504", "2^-10 ≈ 9.77 × 10^-4"],
        ["BF16 (Brain)", "1", "8", "7", "127", "1.18 × 10^-38 to 3.40 × 10^38", "2^-7 ≈ 7.81 × 10^-3"],
        ["FP12 (Accumulator)", "1", "6", "5", "31", "4.66 × 10^-10 to 4.29 × 10^9", "2^-5 = 0.03125 (1/32)"],
        ["FP8 E5M2 (Multiplier)", "1", "5", "2", "15", "6.10 × 10^-5 to 57,344", "2^-2 = 0.25 (1/4)"]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.name = 'Helvetica'
            p.font.size = Pt(9.5 if r_idx > 0 else 10)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_NAVY
            elif r_idx == 4:
                p.font.bold = True
                p.font.color.rgb = C_NAVY
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(254, 243, 199) # Highlight
            else:
                p.font.color.rgb = C_DARK
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_WHITE if r_idx % 2 == 1 else C_BG_CARD

    # Note
    nbox = s4.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11.733), Inches(0.8))
    np = nbox.text_frame.paragraphs[0]
    np.text = "Key Takeaway: FP12 E6M5 provides 6 exponent bits, matching the dynamic range of FP16 while trimming significand bits down to 5. Stochastic Rounding restores resolution lost by the 5-bit mantissa."
    np.font.size = Pt(9.5)
    np.font.bold = True
    np.font.color.rgb = C_TEAL

    # ==========================================================================
    # SLIDE 5: The Gradient Swamping Trap (Numerical Stagnation)
    # ==========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "The Gradient Swamping Trap: Why Standard Rounding Fails", "NUMERICAL STAGNATION")

    add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    t1 = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf = t1.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "The Exponent Alignment Distance"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_list = [
        "Floating-point addition requires aligning exponents: d = e_acc - e_prod.",
        "In FP12 E6M5, significand precision is P = 6 bits (including implicit 1).",
        "When d > P = 6, the incoming product significand shifts completely below the LSB of the accumulator.",
        "If the discarded fraction is < 0.5 ULP, standard Round-to-Nearest (RN) systematically truncates it to 0:",
        "RN(acc + Δ) = acc,  for all Δ < 2^{e_acc - 6}",
        "Result: Millions of gradient updates vanish, capping accuracy at 83%."
    ]
    for b in b_list:
        p = tf.add_paragraph(); p.text = b; p.font.size = Pt(10.5); p.space_before = Pt(8)

    add_card(s5, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    t2 = s5.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf = t2.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Visual Analogy: The Measuring Tape"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_ORANGE
    b_list2 = [
        "Imagine measuring rainfall in a large 100-liter tank using a coarse gauge marked only in 1-liter increments.",
        "Adding 1 milliliter (drop of water) per minute under deterministic rounding always rounds to 0 liters.",
        "Over 10,000 minutes (10 liters of actual water), the tank measurement stays frozen at 0 liters!",
        "In DNN backpropagation, weight updates Δ = η · (∂L/∂w) are tiny fractions.",
        "Standard RN causes weights to completely freeze, leading to premature training stagnation."
    ]
    for b in b_list2:
        p = tf.add_paragraph(); p.text = b; p.font.size = Pt(10.5); p.space_before = Pt(8)

    # ==========================================================================
    # SLIDE 6: Mathematical Foundation of Stochastic Rounding (SR)
    # ==========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, "Mathematical Foundation: Stochastic Rounding Unbiased Expectation", "PROBABILISTIC ARITHMETIC")

    add_card(s6, Inches(0.8), Inches(1.6), Inches(11.733), Inches(2.2))
    t = s6.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(1.8))
    tf = t.text_frame
    p = tf.paragraphs[0]; p.text = "Mathematical Definition of Stochastic Rounding (SR)"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    p2 = tf.add_paragraph()
    p2.text = "SR maps an intermediate real value x ∈ [⌊x⌋, ⌈x⌉] probabilistically:\n" \
              "SR(x) = ⌈x⌉ with probability q = (x - ⌊x⌋) / (⌈x⌉ - ⌊x⌋)\n" \
              "SR(x) = ⌊x⌋ with probability 1 - q"
    p2.font.size = Pt(12); p2.font.bold = True; p2.font.color.rgb = C_TEAL; p2.space_before = Pt(6)

    add_card(s6, Inches(0.8), Inches(4.1), Inches(5.6), Inches(2.8))
    t1 = s6.shapes.add_textbox(Inches(1.0), Inches(4.2), Inches(5.2), Inches(2.5))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "Strictly Unbiased Expectation"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_NAVY
    b1 = [
        "E[SR(x)] = ⌈x⌉ · q + ⌊x⌋ · (1 - q)",
        "E[SR(x)] = ⌊x⌋ + (⌈x⌉ - ⌊x⌋) · q = x",
        "Proof: The mathematical expectation of SR is identical to the exact real value x.",
        "Zero systematic bias accumulates over time."
    ]
    for b in b1:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(4)

    add_card(s6, Inches(6.9), Inches(4.1), Inches(5.6), Inches(2.8))
    t2 = s6.shapes.add_textbox(Inches(7.1), Inches(4.2), Inches(5.2), Inches(2.5))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "Why SR Defeats Swamping in DNNs"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_TEAL
    b2 = [
        "If a gradient update has a round-up probability of q = 2^-9 (≈ 0.00195):",
        "Deterministic RN gives it 0% chance of being recorded.",
        "Stochastic Rounding will round UP once every ~512 steps.",
        "Across K = 2048 accumulation steps, expected sum matches the exact gradient perfectly!"
    ]
    for b in b2:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 7: DATE 2024 Baseline Architecture Overview
    # ==========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(s7, "DATE 2024 Baseline Architecture Overview", "BASELINE REPRODUCTION")

    modules = [
        ("FP8 (E5M2) Multiplier", "Exact multiplication of two FP8 inputs into an exact FP12 (E6M5) product. Sized for 1 sign, 5 exponent, 2 mantissa bits. Product mantissa is 6 bits wide (3x3 multiplier)."),
        ("Galois LFSR PRNG", "18-bit Galois Linear Feedback Shift Register using polynomial x^18 + x^11 + 1. Generates 18 pseudo-random bits per cycle for stochastic rounding carry evaluation."),
        ("FP12 RN Adder", "Deterministic dual-path adder baseline with round-to-nearest-even tie-breaking logic. Sized for FP12 inputs (6 exponent, 5 mantissa bits)."),
        ("FP12 Lazy SR Adder", "Baseline stochastic adder: performs significand addition, leading-zero detection, and normalization before serializing an r-bit random adder at the output."),
        ("FP12 Eager SR Adder", "Paper's optimized adder: decouples stochastic rounding into parallel Sticky Round addition and 2-bit Round Correction, removing random adder from critical path.")
    ]
    for idx, (m_title, m_desc) in enumerate(modules):
        top_pos = Inches(1.6 + idx * 1.05)
        add_card(s7, Inches(0.8), top_pos, Inches(11.733), Inches(0.95))
        mb = s7.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.08), Inches(11.3), Inches(0.8))
        mtf = mb.text_frame
        mp = mtf.paragraphs[0]; mp.text = m_title; mp.font.bold = True; mp.font.size = Pt(11); mp.font.color.rgb = C_NAVY
        mp2 = mtf.add_paragraph(); mp2.text = m_desc; mp2.font.size = Pt(9.5); mp2.font.color.rgb = C_DARK; mp2.space_before = Pt(2)

    # ==========================================================================
    # SLIDE 8: Adder Architectures: Lazy vs. Eager vs. Adaptive (FIGURE 1)
    # ==========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(s8, "Adder Architectures: Lazy SR vs. Eager SR vs. Adaptive SR", "HARDWARE ARCHITECTURE")

    if os.path.exists('report/figures/fig1_adder_architectures.png'):
        s8.shapes.add_picture('report/figures/fig1_adder_architectures.png', Inches(0.8), Inches(1.6), width=Inches(11.733))

    b_card = add_card(s8, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.3))
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(5.7), Inches(11.3), Inches(1.1))
    tbf = tb.text_frame
    tp = tbf.paragraphs[0]; tp.text = "Key Architectural Differences:"; tp.font.bold = True; tp.font.size = Pt(11); tp.font.color.rgb = C_NAVY
    tp2 = tbf.add_paragraph()
    tp2.text = "• Lazy SR: Wide random adder directly in series with normalizer -> severe timing delay.\n" \
               "• Eager SR (DATE 2024): Sticky round operates in parallel with significand adder -> critical path shortened.\n" \
               "• Adaptive SR (Ours): Dynamic Operand Gating silences unused bits -> 27.4% dynamic power savings with zero hardware replication."
    tp2.font.size = Pt(9.5); tp2.font.color.rgb = C_DARK; tp2.space_before = Pt(2)

    # ==========================================================================
    # SLIDE 9: Eager SR Mechanism: Sticky Round & Round Correction Logic
    # ==========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(s9, "Eager SR Mechanism: Sticky Round & Round Correction Logic", "PIPELINE DETAILS")

    add_card(s9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    t1 = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "1. Sticky Round Stage (Parallel)"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b1 = [
        "Shifted operand significand is divided into upper P+1 bits (Ytop) and lower r-2 bits (Ylow).",
        "The Sticky Round unit tentatively adds Ylow to random bits R3_ext in parallel with main adder.",
        "Computes three carry signals:",
        "• S1 = carry(Ylow + R3_ext)",
        "• S2 = carry(Ylow[r-4:0] + R3_ext[r-4:0])",
        "• S3 = carry(Ylow[r-5:0] + R3_ext[r-5:0])",
        "S3 was our original addition to handle 2-bit normalization shifts in far-path subtractions."
    ]
    for b in b1:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(5)

    add_card(s9, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    t2 = s9.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "2. Round Correction Stage"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_TEAL
    b2 = [
        "Normalizer performs leading zero detection (LZD) and shifts upper bits by j positions.",
        "In far path: j ∈ {0, 1, 2}; in close path: cancellation may cause larger shifts.",
        "Round Correction logic uses shift amount j, guard bits g, top 2 random bits R12, and carries {S1, S2, S3}.",
        "Generates a 1-bit increment signal 'up':",
        "mz = {1'b0, sig} + up",
        "Result: Perfect unbiased stochastic rounding with minimal 2-bit post-normalization logic."
    ]
    for b in b2:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(5)

    # ==========================================================================
    # SLIDE 10: Galois LFSR Pseudo-Random Number Generator Design
    # ==========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(s10, "Galois LFSR Pseudo-Random Number Generator Design", "PRNG HARDWARE")

    add_card(s10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    t1 = s10.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "Galois vs. Fibonacci Topology"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b1 = [
        "Characteristic Polynomial: x^18 + x^11 + 1.",
        "Feedback Mask: 18'h20400.",
        "Why Galois Architecture?",
        "• Fibonacci LFSR: Long chain of XOR gates in the feedback path -> high gate delay and fanout.",
        "• Galois LFSR: XOR gates are placed modularly between register stages -> parallel operation and maximum clock frequency.",
        "Delivers 18 independent pseudo-random bits every cycle."
    ]
    for b in b1:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(6)

    add_card(s10, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    t2 = s10.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "Statistical Properties & Periodicity"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_TEAL
    b2 = [
        "Maximum Length Sequence (m-sequence):",
        "• Period = 2^18 - 1 = 262,143 non-zero states.",
        "• Uniform distribution across all non-zero states.",
        "Dynamic Loss of Entropy in Fixed SR:",
        "• Fixed 18-bit LFSR draws dynamic switching power on all 18 flip-flops on every MAC cycle.",
        "• In our proposed ASR, lower LFSR flip-flops are clock-gated or masked during coarse epochs."
    ]
    for b in b2:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(6)

    # ==========================================================================
    # SLIDE 11: Functional RTL Verification & Golden Model Matching
    # ==========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_header(s11, "Functional Verification: Zero Mismatches Across 200,000+ Vectors", "VERIFICATION")

    v_cards = [
        ("FP8 Multiplier Exhaustive Test", "65,536 Vectors", "All 256 × 256 input combinations simulated in Icarus Verilog against Python golden model. Verified bit-exact (0 mismatches)."),
        ("FP12 Adder Verification", "210,993 Vectors", "180,993 vectors at r=18 and 30,000 vectors each across r ∈ {9, 12, 14, 16}. Zero mismatches across RN, Lazy, and Eager adders."),
        ("Sequential Top-Level MAC", "4,000 Steps", "Sequential MAC accumulation with dynamic Galois LFSR random word generation tested in Icarus Verilog (0 mismatches)."),
        ("Statistical Binomial Probability Test", "10,000 Pairs × 1,000 Words", "Verified exact round-up probability q. Exact two-sided binomial tail probability confirmed p > 10^-6 across all pairs.")
    ]
    for idx, (v_title, v_stat, v_desc) in enumerate(v_cards):
        top_pos = Inches(1.6 + idx * 1.3)
        add_card(s11, Inches(0.8), top_pos, Inches(11.733), Inches(1.15))
        vb = s11.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.1), Inches(11.1), Inches(0.95))
        vtf = vb.text_frame
        vp = vtf.paragraphs[0]; vp.text = f"{v_title} — [{v_stat}]"; vp.font.bold = True; vp.font.size = Pt(11); vp.font.color.rgb = C_NAVY
        vp2 = vtf.add_paragraph(); vp2.text = v_desc; vp2.font.size = Pt(9.5); vp2.font.color.rgb = C_DARK; vp2.space_before = Pt(3)

    # ==========================================================================
    # SLIDE 12: Quantitative Hardware Comparison: ASIC & FPGA (TABLE 2)
    # ==========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_header(s12, "Quantitative Hardware Comparison Across Precisions (Point 1)", "HARDWARE EVALUATION")

    rows = 7; cols = 7
    table_shape = s12.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.3))
    t = table_shape.table

    h_data = [
        ["Configuration", "Accum. Format", "Random Bits (r)", "28nm Area (μm²)", "28nm Delay (ns)", "FPGA LUTs (VU9P)", "FPGA Delay (ns)"],
        ["FP32 RN Baseline", "E8M23", "--", "1337.42", "4.69", "645", "12.45"],
        ["FP16 RN Baseline", "E5M10", "--", "662.43", "2.75", "301", "8.29"],
        ["FP12 RN (No SR)", "E6M5", "--", "462.67", "1.88", "195", "6.92"],
        ["FP12 Lazy SR", "E6M5", "18", "675.20", "2.45", "344", "8.76"],
        ["FP12 Eager SR (Paper)", "E6M5", "18", "628.48", "2.10", "251", "8.04"],
        ["Phase-ASR (Ours)", "E6M5", "7 -> 13", "588.60", "1.94", "234", "7.70"]
    ]
    for r_idx, row in enumerate(h_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.name = 'Helvetica'
            p.font.size = Pt(9.5 if r_idx > 0 else 10)
            if r_idx == 0:
                p.font.bold = True; p.font.color.rgb = C_WHITE; cell.fill.solid(); cell.fill.fore_color.rgb = C_NAVY
            elif r_idx == 6:
                p.font.bold = True; p.font.color.rgb = C_NAVY; cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(254, 243, 199)
            else:
                p.font.color.rgb = C_DARK; cell.fill.solid(); cell.fill.fore_color.rgb = C_WHITE if r_idx % 2 == 1 else C_BG_CARD

    # Summary box
    sbox = s12.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.9))
    sp = sbox.text_frame.paragraphs[0]
    sp.text = "Key Findings for Sir's Point 1: Eager SR is 14.3% faster in delay and consumes 27.0% fewer FPGA LUTs than Lazy SR at r=18. Adding Eager SR over baseline RN requires only +35.8% area overhead while completely eliminating gradient swamping."
    sp.font.size = Pt(9.5); sp.font.bold = True; sp.font.color.rgb = C_TEAL

    # ==========================================================================
    # SLIDE 13: Hardware Complexity Scaling Across r (FIGURE 2)
    # ==========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_header(s13, "Hardware Complexity Scaling Across r in {4, 7, 9, 11, 13, 18}", "SCALING ANALYSIS")

    if os.path.exists('report/figures/fig2_hardware_scaling.png'):
        s13.shapes.add_picture('report/figures/fig2_hardware_scaling.png', Inches(0.8), Inches(1.5), width=Inches(6.8))

    add_card(s13, Inches(7.8), Inches(1.5), Inches(4.7), Inches(5.4))
    sb = s13.shapes.add_textbox(Inches(8.0), Inches(1.7), Inches(4.3), Inches(5.0))
    stf = sb.text_frame; stf.word_wrap = True
    p = stf.paragraphs[0]; p.text = "Parametric Hardware Scaling"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_scale = [
        "• Sticky Adder Width: Scales linearly as (r - 2) bits (2 bits at r=4 to 11 bits at r=13).",
        "• 28nm Area: Increases monotonically from 493 μm² (r=4) to 580 μm² (r=13) and 628 μm² (r=18).",
        "• Critical Path Delay: Only increases by 4.3% between r=4 (1.84 ns) and r=13 (1.92 ns).",
        "• Dynamic Energy: Scales linearly from 0.45 nW/MHz (r=4) to 0.54 nW/MHz (r=13).",
        "• Phase-ASR Operating Point: By annealing precision, Phase-ASR drops energy to 0.41 nW/MHz!"
    ]
    for b in b_scale:
        p = stf.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(8)

    # ==========================================================================
    # SLIDE 14: Accumulator Swamping Resilience Across Depth K (FIGURE 3)
    # ==========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_slide_header(s14, "Accumulator Swamping Resilience Across Depth K (Point 3)", "SWAMPING EXPERIMENT")

    if os.path.exists('report/figures/fig3_swamping_depth.png'):
        s14.shapes.add_picture('report/figures/fig3_swamping_depth.png', Inches(0.8), Inches(1.6), width=Inches(7.2))

    add_card(s14, Inches(8.2), Inches(1.6), Inches(4.3), Inches(5.3))
    sb = s14.shapes.add_textbox(Inches(8.4), Inches(1.8), Inches(3.9), Inches(4.9))
    stf = sb.text_frame; stf.word_wrap = True
    p = stf.paragraphs[0]; p.text = "Depth Experiment Findings"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_depth = [
        "Setup: Repeated addition of small terms A0 = 1.0, Δ = 2^-7 across depth K ∈ {144, 288, 576, 2048}.",
        "1. RN: Completely swamped. Remains frozen at 1.000 across all depths.",
        "2. r=4: Caps prematurely at 4.000 for K >= 576 (underflow occurs when d > 4).",
        "3. r=13: Accurately accumulates to 17.45 at K=2048 (exact math sum = 16.99).",
        "Conclusion: r=13 is the critical threshold to eliminate swamping."
    ]
    for b in b_depth:
        p = stf.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_before = Pt(7)

    # ==========================================================================
    # SLIDE 15: ResNet-20 Layer-by-Layer Reduction Depth Matrix
    # ==========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_slide_header(s15, "Layer-by-Layer Accumulation Depth Matrix (ResNet-20)", "SPATIAL SENSITIVITY")

    rows = 6; cols = 6
    table_shape = s15.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.5))
    t = table_shape.table

    l_data = [
        ["Layer Name", "Filter", "Input Channels (Cin)", "Reduction Depth (K)", "Swamping Risk", "Optimal r Allocation"],
        ["conv1 (Input Stage)", "3 × 3", "3", "K = 27", "Very Low (Short depth)", "r = 7 (Low Complexity)"],
        ["layer1 (3 Blocks)", "3 × 3", "16", "K = 144", "Moderate", "r = 9"],
        ["layer2 (3 Blocks)", "3 × 3", "32", "K = 288", "Elevated", "r = 11"],
        ["layer3 (3 Blocks)", "3 × 3", "64", "K = 576", "High (Severe swamping)", "r = 13 (High Precision)"],
        ["fc (Linear Classifier)", "1 × 1", "64", "K = 64", "Low", "r = 9"]
    ]
    for r_idx, row in enumerate(l_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.name = 'Helvetica'
            p.font.size = Pt(9.5 if r_idx > 0 else 10)
            if r_idx == 0:
                p.font.bold = True; p.font.color.rgb = C_WHITE; cell.fill.solid(); cell.fill.fore_color.rgb = C_NAVY
            else:
                p.font.color.rgb = C_DARK; cell.fill.solid(); cell.fill.fore_color.rgb = C_WHITE if r_idx % 2 == 1 else C_BG_CARD

    # Note
    nbox = s15.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11.733), Inches(0.8))
    np = nbox.text_frame.paragraphs[0]
    np.text = "Mathematical Justification: Reduction depth K = Cin · kh · kw determines how many products are summed into each accumulator register. Deep layers have 21x larger accumulation depths than conv1, justifying spatial layer-adaptive precision."
    np.font.size = Pt(9.5); np.font.bold = True; np.font.color.rgb = C_TEAL

    # ==========================================================================
    # SLIDE 16: Training Convergence vs. Baselines (FIGURE 4)
    # ==========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_slide_header(s16, "Training Accuracy & Convergence vs. Baselines (Point 2)", "CONVERGENCE PROOF")

    if os.path.exists('report/figures/fig4_training_convergence.png'):
        s16.shapes.add_picture('report/figures/fig4_training_convergence.png', Inches(0.8), Inches(1.5), width=Inches(7.2))

    add_card(s16, Inches(8.2), Inches(1.5), Inches(4.3), Inches(5.4))
    sb = s16.shapes.add_textbox(Inches(8.4), Inches(1.7), Inches(3.9), Inches(5.0))
    stf = sb.text_frame; stf.word_wrap = True
    p = stf.paragraphs[0]; p.text = "Key Convergence Takeaways"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_conv = [
        "1. Full 165-Epoch Accuracy:",
        "• FP32 Baseline: 91.47% (Our Kaggle run: 91.07%)",
        "• FP16 Baseline: 91.10%",
        "• FP12 RN (No SR): 83.03% (Swamped)",
        "• FP12 Eager SR: 91.39% (Full recovery)",
        "2. Early-Epoch Convergence (1 Epoch):",
        "• FP32: 45.25%",
        "• FP12 Eager SR: 44.89% (Tracks FP32!)",
        "• FP12 RN: 22.91% (Lags immediately)",
        "Proof: SR eliminates swamping from epoch 1."
    ]
    for b in b_conv:
        p = stf.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 17: Post-Training Inference Sensitivity (Kaggle Empirical Results)
    # ==========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_slide_header(s17, "Post-Training Inference Sensitivity (Kaggle Empirical Results)", "TEST-TIME INFERENCE")

    add_card(s17, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    t1 = s17.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "Kaggle Test-Time Accuracy Measurements"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_inf = [
        "We evaluated pre-trained ResNet-20 weights on the complete CIFAR-10 test set (N=10,000) with emulated FP12 MAC:",
        "• eager r = 4:  89.50% test acc  (71s)",
        "• eager r = 7:  89.46% test acc  (73s)",
        "• eager r = 9:  89.40% test acc  (73s)",
        "• eager r = 11: 89.31% test acc  (73s)",
        "• eager r = 13: 89.35% test acc  (73s)",
        "All configurations achieve virtually identical accuracy (~89.4%) regardless of r!"
    ]
    for b in b_inf:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(6)

    add_card(s17, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    t2 = s17.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "The Training vs. Inference Asymmetry"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_TEAL
    b_asym = [
        "Why does r=4 fail in training (52.4%) but succeed in inference (89.5%)?",
        "• Training (Backpropagation): Involves repeated, iterative accumulation of vanishingly small gradient updates. High precision (r >= 13) is vital.",
        "• Inference (Forward Pass): Activations and weights are already well-conditioned. There is no cumulative vanishing effect.",
        "Practical Deployment Value: Edge inference accelerators can aggressively downscale to r=4 to maximize energy savings."
    ]
    for b in b_asym:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(6)

    # ==========================================================================
    # SLIDE 18: Motivation for Innovation: The Inefficiency of Fixed SR
    # ==========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_slide_header(s18, "Motivation for Innovation: The Inefficiency of Fixed SR", "PROPOSED INNOVATION")

    cards_ineff = [
        ("Static Bit-Width Inefficiency", "DATE 2024 uses a static, fixed 18-bit LFSR and sticky adder for every operation across all layers and epochs. This causes continuous dynamic switching power dissipation in hardware even when coarse precision is sufficient."),
        ("Temporal Opportunity (Training Phase)", "Early in training (large learning rate η = 0.1), gradient magnitudes are large, and swamping distance d <= 6. Coarse stochastic rounding (r = 7) provides ample precision and natural regularization. High precision is only needed during late fine-tuning."),
        ("Spatial Opportunity (Network Depth)", "Input conv1 accumulates over K = 27 channels, whereas stage 3 blocks accumulate over K = 576 channels. Sizing the hardware uniformly for the worst-case layer wastes dynamic power in 75% of operations.")
    ]
    for idx, (head, desc) in enumerate(cards_ineff):
        top_pos = Inches(1.6 + idx * 1.75)
        add_card(s18, Inches(0.8), top_pos, Inches(11.733), Inches(1.5))
        cbox = s18.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.15), Inches(11.1), Inches(1.2))
        ctf = cbox.text_frame
        cp = ctf.paragraphs[0]; cp.text = head; cp.font.bold = True; cp.font.size = Pt(12); cp.font.color.rgb = C_NAVY
        cp2 = ctf.add_paragraph(); cp2.text = desc; cp2.font.size = Pt(10.5); cp2.font.color.rgb = C_DARK; cp2.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 19: Proposed Innovation: Adaptive Stochastic Rounding (ASR)
    # ==========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    add_slide_header(s19, "Proposed Innovation: Adaptive Stochastic Rounding (ASR)", "ALGORITHMIC POLICIES")

    add_card(s19, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.3))
    t1 = s19.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(3.3), Inches(4.9))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "1. Phase-Adaptive SR"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_NAVY
    b1 = [
        "Cosine precision schedule:",
        "r(t) = r_min + (r_max - r_min) · progress",
        "• Early epochs: r = 7",
        "• Mid epochs: r = 9, 11",
        "• Late epochs: r = 13",
        "Average active bits: r̄ = 9.98.",
        "Matches 18-bit baseline accuracy (91.38%)."
    ]
    for b in b1:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_before = Pt(5)

    add_card(s19, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.3))
    t2 = s19.shapes.add_textbox(Inches(5.0), Inches(1.8), Inches(3.3), Inches(4.9))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "2. Layer-Adaptive SR"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_TEAL
    b2 = [
        "Reduction-depth mapping:",
        "• conv1 (K=27) -> r = 7",
        "• layer1 (K=144) -> r = 9",
        "• layer2 (K=288) -> r = 11",
        "• layer3 (K=576) -> r = 13",
        "Average active bits: r̄ = 10.12.",
        "Allocates bits exactly where swamping risk exists."
    ]
    for b in b2:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_before = Pt(5)

    add_card(s19, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.3))
    t3 = s19.shapes.add_textbox(Inches(9.0), Inches(1.8), Inches(3.3), Inches(4.9))
    tf3 = t3.text_frame; tf3.word_wrap = True
    p = tf3.paragraphs[0]; p.text = "3. Hybrid-ASR"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_ORANGE
    b3 = [
        "Joint spatiotemporal policy:",
        "Blends epoch progress annealing with layer depth requirement.",
        "Average active bits: r̄ = 9.40.",
        "Delivers 32.7% dynamic power savings with 91.35% accuracy."
    ]
    for b in b3:
        p = tf3.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_before = Pt(6)

    # ==========================================================================
    # SLIDE 20: Hardware RTL Realization: Dynamic Operand Gating
    # ==========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    add_slide_header(s20, "Hardware RTL Realization: MSB-Aligned Dynamic Operand Gating", "CIRCUIT DESIGN")

    add_card(s20, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    t1 = s20.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "Architectural Circuit Design (RTL)"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b1 = [
        "Implemented in fp12_add_sr_adaptive.v with max width Rmax = 13 (11-bit carry chain).",
        "Controlled via 3-bit mode register r_sel (0:4, 1:7, 2:9, 3:11, 4:13).",
        "MSB-Aligned Embedding:",
        "• For active width r, lower fractional bits and PRNG bits align to the MSB of the 11-bit sticky adder.",
        "• Inactive lower (11 - k) bits are masked to 0 via bitmask.",
        "Hardware Overhead: Only 11 AND gates + 3-bit register (< 1.5% area overhead!)."
    ]
    for b in b1:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(5)

    add_card(s20, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    t2 = s20.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "Dynamic Power Suppression Mechanism"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_TEAL
    b2 = [
        "In CMOS digital logic, dynamic power is:",
        "P_dyn = α · C · V^2 · f",
        "where α is the switching activity factor.",
        "Zeroing Lower Carry Bits:",
        "• By masking lower adder inputs to static zero, input transitions never occur.",
        "• Switching activity factor drops to zero (α = 0).",
        "• Dynamic power dissipation in inactive adder slices and LFSR flip-flops is completely silenced!"
    ]
    for b in b2:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(5)

    # ==========================================================================
    # SLIDE 21: Hardware Verification of Adaptive Adder & MAC
    # ==========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    add_slide_header(s21, "Hardware Verification: 25,000 Vectors Across All Adaptive Modes", "RTL VERIFICATION")

    v_modes = [
        ("Mode 0: r = 4 (r_sel = 0)", "5,000 Vectors Checked", "Zero mismatches against dedicated reference eager adder (R=4)"),
        ("Mode 1: r = 7 (r_sel = 1)", "5,000 Vectors Checked", "Zero mismatches against dedicated reference eager adder (R=7)"),
        ("Mode 2: r = 9 (r_sel = 2)", "5,000 Vectors Checked", "Zero mismatches against dedicated reference eager adder (R=9)"),
        ("Mode 3: r = 11 (r_sel = 3)", "5,000 Vectors Checked", "Zero mismatches against dedicated reference eager adder (R=11)"),
        ("Mode 4: r = 13 (r_sel = 4)", "5,000 Vectors Checked", "Zero mismatches against dedicated reference eager adder (R=13)")
    ]
    for idx, (m_title, m_count, m_res) in enumerate(v_modes):
        top_pos = Inches(1.6 + idx * 1.05)
        add_card(s21, Inches(0.8), top_pos, Inches(11.733), Inches(0.95))
        mb = s21.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.08), Inches(11.1), Inches(0.8))
        mtf = mb.text_frame
        mp = mtf.paragraphs[0]; mp.text = f"{m_title} — [{m_count}]"; mp.font.bold = True; mp.font.size = Pt(11); mp.font.color.rgb = C_NAVY
        mp2 = mtf.add_paragraph(); mp2.text = m_res; mp2.font.size = Pt(9.5); mp2.font.color.rgb = C_DARK; mp2.space_before = Pt(2)

    # ==========================================================================
    # SLIDE 22: Experimental Results & Power Trade-Off Matrix (FIGURE 5 & TABLE 4)
    # ==========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    add_slide_header(s22, "Innovation Results & Power Savings (Point 4 Mandate Met)", "RESULTS & VALIDATION")

    if os.path.exists('report/figures/fig5_adaptive_power_tradeoff.png'):
        s22.shapes.add_picture('report/figures/fig5_adaptive_power_tradeoff.png', Inches(0.8), Inches(1.5), width=Inches(7.2))

    add_card(s22, Inches(8.2), Inches(1.5), Inches(4.3), Inches(5.4))
    sb = s22.shapes.add_textbox(Inches(8.4), Inches(1.7), Inches(3.9), Inches(5.0))
    stf = sb.text_frame; stf.word_wrap = True
    p = stf.paragraphs[0]; p.text = "Comparison vs Fixed 13-bit"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_res = [
        "1. Training Accuracy:",
        "• Fixed 18-bit (Paper): 91.39%",
        "• Fixed 13-bit (Target): 91.24%",
        "• Phase-ASR (Ours): 91.38% (Matches 18-bit!)",
        "2. Dynamic Power Savings:",
        "• Sticky Adder: +27.4% vs r=13 (+50.1% vs r=18)",
        "• PRNG Energy: +23.2% vs r=13 (+44.6% vs r=18)",
        "• Total MAC Energy: 0.41 nW/MHz vs 0.54 nW/MHz",
        "Objective Met: Equal accuracy with substantially lower hardware complexity."
    ]
    for b in b_res:
        p = stf.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_before = Pt(4)

    # ==========================================================================
    # SLIDE 23: Explicit Demarcation of Work (TABLE 5)
    # ==========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    add_slide_header(s23, "Explicit Demarcation: Paper Reproduction vs. Novel Contributions", "ACADEMIC INTEGRITY")

    add_card(s23, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    t1 = s23.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf1 = t1.text_frame; tf1.word_wrap = True
    p = tf1.paragraphs[0]; p.text = "Reproduced from DATE 2024 Paper"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_NAVY
    b_reprod = [
        "• Architecture of FP8 E5M2 multiplier and exact FP12 product.",
        "• RTL of FP12 RN, Lazy SR, and Eager SR adders at static r=18.",
        "• 18-step Galois LFSR with polynomial x^18 + x^11 + 1.",
        "• Baseline verification methodology (adder vectors, binomial test).",
        "• Baseline training benchmarks for FP32, FP16, and FP12 Eager (r=18) on ResNet-20."
    ]
    for b in b_reprod:
        p = tf1.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(8)

    add_card(s23, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    t2 = s23.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
    tf2 = t2.text_frame; tf2.word_wrap = True
    p = tf2.paragraphs[0]; p.text = "Our Proposed Contributions & Innovations"; p.font.bold = True; p.font.size = Pt(13); p.font.color.rgb = C_TEAL
    b_novel = [
        "• Multi-platform quantitative hardware comparison (28nm ASIC, FPGA VU9P, Nangate 45nm).",
        "• Parametric sweep across r ∈ {4, 7, 9, 11, 13} and swamping depth analysis.",
        "• Discovery and proof that r=13 is the optimal saturation threshold.",
        "• Formulation of Adaptive Stochastic Rounding (ASR) paradigm.",
        "• Novel hardware RTL with MSB-aligned dynamic operand gating (fp12_add_sr_adaptive.v).",
        "• Integration of Phase-, Layer-, and Hybrid-ASR in PyTorch emulator.",
        "• Experimental validation of 27.4% dynamic power reduction with matching 91.38% accuracy."
    ]
    for b in b_novel:
        p = tf2.add_paragraph(); p.text = b; p.font.size = Pt(10); p.space_before = Pt(5)

    # ==========================================================================
    # SLIDE 24: Summary of Achievements Addressing Faculty Review
    # ==========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    add_slide_header(s24, "Summary of Achievements: Faculty Review Checklist", "REVIEW SUMMARY")

    checklist = [
        ("Point 1: Quantitative Hardware Comparison", "COMPLETED", "Evaluated area, delay, LUTs, FFs, and energy across 3 platforms. Proved Eager SR is 14.3% faster and saves 27% LUTs over Lazy SR."),
        ("Point 2: Training Convergence vs Baselines", "COMPLETED", "Demonstrated that FP12 RN drops to 83.03% (swamped), while Eager SR reaches 91.39%, matching FP16 (91.10%) and FP32 (91.47%)."),
        ("Point 3: Random Bit Sweep r ∈ {4, 7, 9, 11, 13}", "COMPLETED", "Evaluated swamping depth K and accuracy. Proved r=13 is the saturation threshold for training, while inference is robust down to r=4."),
        ("Point 4: Adaptive Stochastic Rounding (ASR)", "COMPLETED", "Designed and validated ASR with operand gating. Achieved 91.38% accuracy with 27.4% adder power savings vs fixed 13-bit SR."),
        ("Point 5: Explicit Demarcation of Work", "COMPLETED", "Clearly separated reproduced paper components from original contributions in Table 5.")
    ]
    for idx, (c_point, c_status, c_detail) in enumerate(checklist):
        top_pos = Inches(1.6 + idx * 1.05)
        add_card(s24, Inches(0.8), top_pos, Inches(11.733), Inches(0.95))
        cb = s24.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.08), Inches(11.1), Inches(0.8))
        ctf = cb.text_frame
        cp = ctf.paragraphs[0]; cp.text = f"{c_point} — [{c_status}]"; cp.font.bold = True; cp.font.size = Pt(11); cp.font.color.rgb = C_NAVY
        cp2 = ctf.add_paragraph(); cp2.text = c_detail; cp2.font.size = Pt(9.5); cp2.font.color.rgb = C_DARK; cp2.space_before = Pt(2)

    # ==========================================================================
    # SLIDE 25: Conclusion & Repository Deliverables
    # ==========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    add_slide_header(s25, "Conclusion & Repository Deliverables", "CONCLUSION")

    add_card(s25, Inches(0.8), Inches(1.6), Inches(11.733), Inches(2.2), C_WHITE, C_BORDER)
    tb = s25.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(1.8))
    tbf = tb.text_frame
    tp = tbf.paragraphs[0]; tp.text = "Concluding Remarks"; tp.font.bold = True; tp.font.size = Pt(14); tp.font.color.rgb = C_NAVY
    tp2 = tbf.add_paragraph()
    tp2.text = "In this work, we advanced beyond reproducing the DATE 2024 architecture by resolving all faculty review guidelines. " \
               "We proved that static 18-bit and 13-bit SR impose unnecessary switching activity, and introduced Adaptive Stochastic Rounding (ASR). " \
               "By dynamically modulating active precision through MSB-aligned operand gating, ASR delivers state-of-the-art training accuracy (91.38%) " \
               "while cutting adder dynamic power by 27.4% and total MAC energy by over 24%."
    tp2.font.size = Pt(11); tp2.font.color.rgb = C_DARK; tp2.space_before = Pt(6)

    # Deliverables & Links Card
    add_card(s25, Inches(0.8), Inches(4.1), Inches(11.733), Inches(2.6), C_BG_CARD, C_BORDER)
    db = s25.shapes.add_textbox(Inches(1.1), Inches(4.3), Inches(11.1), Inches(2.2))
    dtf = db.text_frame
    dp = dtf.paragraphs[0]; dp.text = "Open-Source Deliverables & Repository"; dp.font.bold = True; dp.font.size = Pt(13); dp.font.color.rgb = C_TEAL
    dp2 = dtf.add_paragraph()
    dp2.text = "• Public Repository: https://github.com/Sam802scr/MatrixTheoryProject\n" \
               "• Verilog RTL Modules: fp12_add_sr_adaptive.v, fp_mac_adaptive.v, fp8_multiplier.v, lfsr_galois.v\n" \
               "• Self-Checking Testbenches: 25,000 adaptive vectors simulated with 0 mismatches\n" \
               "• PyTorch Emulator: Custom autograd layers supporting Phase-, Layer-, and Hybrid-ASR\n" \
               "• Formal Report: Adaptive_Stochastic_Rounding_Project_Report.pdf (compiled master PDF)"
    dp2.font.size = Pt(10.5); dp2.font.color.rgb = C_DARK; dp2.space_before = Pt(6)

    output_path = "report/Adaptive_Stochastic_Rounding_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully generated and saved to: {output_path}")

if __name__ == '__main__':
    create_deck()
