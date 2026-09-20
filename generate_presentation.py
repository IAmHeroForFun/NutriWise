"""
NutriWise - Hackday 1.0 Presentation Generator (Zero-Blank-Space & INR Edition)
Generates a modern, visual, 16:9 widescreen PowerPoint presentation with:
- Full-bleed visual layout (zero awkward blank white space)
- Indian Rupee (INR / ₹) currency format for market & revenue slides
- Visual flowcharts, directional arrows, status pills, and KPI metric chips
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_CANVAS = RGBColor(0xF1, 0xF5, 0xF9)      # Slate 100 Canvas #F1F5F9
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)          # Pure White
    PRIMARY_DARK = RGBColor(0x0F, 0x2E, 0x22)   # Deep Forest #0F2E22
    PRIMARY = RGBColor(0x1B, 0x4D, 0x3E)        # Forest Green #1B4D3E
    PRIMARY_LIGHT = RGBColor(0xEC, 0xFD, 0xF5)  # Mint Green Tint #ECFDF5
    PRIMARY_BORDER = RGBColor(0xA7, 0xF3, 0xD0) # Mint Border #A7F3D0
    ACCENT_CORAL = RGBColor(0xEA, 0x58, 0x0C)   # Vibrant Coral Orange #EA580C
    ACCENT_RED = RGBColor(0xDC, 0x26, 0x26)     # Bold Red #DC2626
    RED_BG = RGBColor(0xFE, 0xF2, 0xF2)         # Red Tint #FEF2F2
    RED_BORDER = RGBColor(0xFE, 0xCA, 0xCA)     # Red Border #FECACA
    AMBER_BG = RGBColor(0xFF, 0xFB, 0xEB)       # Amber Tint #FFFBEB
    AMBER_BORDER = RGBColor(0xFD, 0xE6, 0x8A)   # Amber Border #FDE68A
    BLUE_BG = RGBColor(0xEF, 0xF6, 0xFF)        # Blue Tint #EFF6FF
    BLUE_BORDER = RGBColor(0xBF, 0xDB, 0xFE)    # Blue Border #BFDBFE
    PURPLE_BG = RGBColor(0xFA, 0xF5, 0xFF)      # Purple Tint #FAF5FF
    PURPLE_BORDER = RGBColor(0xE9, 0xD5, 0xFF)  # Purple Border #E9D5FF
    TEXT_TITLE = RGBColor(0x0F, 0x17, 0x2A)     # Slate 900 #0F172A
    TEXT_BODY = RGBColor(0x33, 0x41, 0x55)      # Slate 700 #334155
    TEXT_MUTED = RGBColor(0x64, 0x74, 0x8B)     # Slate 500 #64748B

    def add_top_accent_bar(slide):
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACCENT_CORAL
        bar.line.fill.background()

    def set_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_CANVAS
        add_top_accent_bar(slide)

    def add_header(slide, badge, title, subtitle):
        tb = slide.shapes.add_textbox(Inches(0.66), Inches(0.3), Inches(12.01), Inches(1.15))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = badge.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_CORAL
        p0.space_after = Pt(2)

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY_DARK

        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_MUTED

    def add_footer(slide, current_num):
        tb = slide.shapes.add_textbox(Inches(0.66), Inches(7.05), Inches(12.01), Inches(0.35))
        tf = tb.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"NutriWise  |  Team DECODEP  |  Hackday 1.0 Final Submission                                                                   Slide {current_num} of 7"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED

    def create_card(slide, left, top, width, height, fill_color=WHITE, border_color=PRIMARY_BORDER, border_width=1.5):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
        return shape

    def add_arrow(slide, left, top, width, height, color=PRIMARY):
        arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, width, height)
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = color
        arrow.line.fill.background()
        return arrow

    def add_pill_chip(slide, left, top, width, height, text, bg_color=PRIMARY_LIGHT, text_color=PRIMARY):
        chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        chip.fill.solid()
        chip.fill.fore_color.rgb = bg_color
        chip.line.fill.background()
        tf = chip.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = text_color
        p.alignment = PP_ALIGN.CENTER
        return chip

    # =========================================================================
    # SLIDE 1: 1️⃣ PROBLEM STATEMENT (Side-by-Side Comparison + Full Bleed)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)
    add_header(s1, "1️⃣  Problem Statement", "The Crisis of Unverified & Hallucinatory AI in Nutrition",
               "Generic AI chatbots give ungrounded, dangerous advice with zero medical accountability.")
    add_footer(s1, 1)

    # Left Container: ❌ Generic AI Chatbots
    col_w = Inches(5.85)
    col_h = Inches(4.35)
    col_top = Inches(1.6)

    create_card(s1, Inches(0.66), col_top, col_w, col_h, fill_color=RED_BG, border_color=RED_BORDER, border_width=2.0)
    tb_l = s1.shapes.add_textbox(Inches(0.95), col_top + Inches(0.25), col_w - Inches(0.6), col_h - Inches(0.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "❌  Generic AI Chatbots (ChatGPT / Gemini)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(16)

    pts_l = [
        ("Fake Recipes & Claims", "Hallucinates nutritional values and invented health benefits."),
        ("Zero Medical Citations", "No book sources, page numbers, or clinical references to verify."),
        ("Climate & Weather Blind", "Ignores local temperature, monsoons, and natural body heat."),
        ("Chatbot UX Fatigue", "Requires 20 minutes of chatting instead of an instant whole-day plan.")
    ]
    for title, desc in pts_l:
        p_t = tf_l.add_paragraph()
        run1 = p_t.add_run()
        run1.text = f"•  {title}: "
        run1.font.bold = True
        run1.font.size = Pt(12)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p_t.add_run()
        run2.text = desc
        run2.font.bold = False
        run2.font.size = Pt(11.5)
        run2.font.color.rgb = TEXT_BODY
        p_t.space_after = Pt(10)

    # Bottom Pill for Left
    add_pill_chip(s1, Inches(0.95), col_top + Inches(3.65), col_w - Inches(0.6), Inches(0.45),
                  "⚠️  CRITICAL RISK: Unverified AI recipes can trigger acute medical emergencies",
                  bg_color=RGBColor(0xFE, 0xE2, 0xE2), text_color=ACCENT_RED)

    # Right Container: ⚠️ Real-World Danger
    create_card(s1, Inches(6.82), col_top, col_w, col_h, fill_color=AMBER_BG, border_color=AMBER_BORDER, border_width=2.0)
    tb_r = s1.shapes.add_textbox(Inches(7.11), col_top + Inches(0.25), col_w - Inches(0.6), col_h - Inches(0.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "⚠️  The Real-World Health Hazards"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xB4, 0x53, 0x09)
    p.space_after = Pt(16)

    pts_r = [
        ("Diabetic Health Hazards", "Recommending high-glycemic foods disguised as 'healthy' snacks."),
        ("Allergy Contamination", "Deadly errors for Celiac (gluten) & severe nut allergy sufferers."),
        ("Contradictory Regimens", "Conflicting diet advice that undermines prescribed medicines."),
        ("Zero Legal Recourse", "When patients fall ill, no one is accountable for chatbot outputs.")
    ]
    for title, desc in pts_r:
        p_t = tf_r.add_paragraph()
        run1 = p_t.add_run()
        run1.text = f"•  {title}: "
        run1.font.bold = True
        run1.font.size = Pt(12)
        run1.font.color.rgb = TEXT_TITLE
        run2 = p_t.add_run()
        run2.text = desc
        run2.font.bold = False
        run2.font.size = Pt(11.5)
        run2.font.color.rgb = TEXT_BODY
        p_t.space_after = Pt(10)

    # Bottom Pill for Right
    add_pill_chip(s1, Inches(7.11), col_top + Inches(3.65), col_w - Inches(0.6), Inches(0.45),
                  "📉  DATA REALITY: 83% of commercial AI diet answers lack empirical sources",
                  bg_color=RGBColor(0xFE, 0xF3, 0xC7), text_color=RGBColor(0x92, 0x40, 0x0E))

    # Bottom Full-Width Hero Callout
    create_card(s1, Inches(0.66), Inches(6.15), Inches(12.01), Inches(0.75), fill_color=PRIMARY_DARK, border_color=PRIMARY_DARK)
    tb_c = s1.shapes.add_textbox(Inches(0.86), Inches(6.25), Inches(11.61), Inches(0.55))
    tf_c = tb_c.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.text = "💡  Core Reality: Clinical nutrition demands 100% mathematical certainty — not creative AI guessing."
    p_c.font.size = Pt(14)
    p_c.font.bold = True
    p_c.font.color.rgb = WHITE
    p_c.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: 2️⃣ PROPOSED SOLUTION (Flowchart Pipeline + 3 Pillars)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "2️⃣  Proposed Solution", "NutriWise: 100% Source-Grounded Dietary Intelligence",
               "A hybrid clinical system combining verified literature RAG with deterministic safety shields.")
    add_footer(s2, 2)

    # Top Flowchart (4 Connected Stages)
    steps = [
        ("1. Ingest Literature", "Uploaded books, EPUBs & clinical research"),
        ("2. Safety Shield", "Hard filters eliminate allergens & medical AVOID"),
        ("3. Grounded RAG", "Gemini selects ONLY candidate foods in DB"),
        ("4. Daily Meal Plan", "Ready in < 15ms with verified book page citations")
    ]
    box_w = Inches(2.55)
    box_h = Inches(1.3)
    arrow_w = Inches(0.35)
    start_x = Inches(0.66)

    for i, (stitle, sdesc) in enumerate(steps):
        bx = start_x + i * (box_w + arrow_w + Inches(0.24))
        create_card(s2, bx, Inches(1.6), box_w, box_h, fill_color=PRIMARY_LIGHT, border_color=PRIMARY, border_width=1.5)
        tb_step = s2.shapes.add_textbox(bx + Inches(0.1), Inches(1.72), box_w - Inches(0.2), box_h - Inches(0.25))
        tf_step = tb_step.text_frame
        tf_step.word_wrap = True

        p = tf_step.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_DARK
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(4)

        p_desc = tf_step.add_paragraph()
        p_desc.text = sdesc
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = TEXT_BODY
        p_desc.alignment = PP_ALIGN.CENTER

        if i < 3:
            add_arrow(s2, bx + box_w + Inches(0.08), Inches(2.1), arrow_w, Inches(0.32), color=PRIMARY)

    # Bottom 3 Full-Height Solution Pillar Cards
    pillars = [
        ("🛡️  Zero-Hallucination RAG", "Absolute Grounding", [
            "AI is locked to candidate food records from ingested books.",
            "Cannot invent dishes, recipes, or unverified claims.",
            "Books and clinical research are treated as authoritative law."
        ], "🎯  100% Verified Book Grounding"),
        ("📖  Verified Book Citations", "Complete Transparency", [
            "Every food card shows exact book title, chapter & page number.",
            "Interactive citation modal displays the author's medical quote.",
            "Users and doctors can audit the exact clinical evidence."
        ], "🔍  Exact Source Quote on Every Card"),
        ("☀️  Weather & Climate Adaptive", "Thermoregulated Nutrition", [
            "Live OpenWeather API integration maps real-time heat & rain.",
            "Promotes cooling foods during heatwaves, warming foods in cold.",
            "Harmonizes modern nutrition with traditional seasonal wisdom."
        ], "🌡️  Real-Time Ambient Weather Sync")
    ]

    p_w = Inches(3.78)
    p_h = Inches(3.7)
    p_top = Inches(3.1)

    for i, (title, sub, pts, chip_text) in enumerate(pillars):
        px = Inches(0.66 + i * 4.11)
        create_card(s2, px, p_top, p_w, p_h, fill_color=WHITE, border_color=PRIMARY_BORDER, border_width=1.5)
        tb_p = s2.shapes.add_textbox(px + Inches(0.25), p_top + Inches(0.22), p_w - Inches(0.5), p_h - Inches(0.85))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        p0 = tf_p.paragraphs[0]
        p0.text = sub.upper()
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_CORAL
        p0.space_after = Pt(2)

        p1 = tf_p.add_paragraph()
        p1.text = title
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY_DARK
        p1.space_after = Pt(12)

        for pt in pts:
            p_pt = tf_p.add_paragraph()
            p_pt.text = f"✓  {pt}"
            p_pt.font.size = Pt(11.5)
            p_pt.font.color.rgb = TEXT_BODY
            p_pt.space_after = Pt(8)

        add_pill_chip(s2, px + Inches(0.25), p_top + Inches(3.05), p_w - Inches(0.5), Inches(0.42),
                      chip_text, bg_color=PRIMARY_LIGHT, text_color=PRIMARY)

    # =========================================================================
    # SLIDE 3: 3️⃣ TARGET USERS (4 Distinct Visual Persona Containers)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "3️⃣  Target Users", "Built for Real Clinical & Lifestyle Nutrition Needs",
               "Serving high-stakes medical conditions, severe allergy sufferers, and health-conscious families.")
    add_footer(s3, 3)

    personas = [
        ("🩸", "Chronic Illness", "Diabetics & Cardiac", RED_BG, RED_BORDER, [
            "Strict low-glycemic foods to stabilize daily blood sugar spikes.",
            "Low-sodium, heart-healthy lipids & high soluble fiber.",
            "PCOS & Thyroid hormonal balance through targeted diet."
        ], "🎯  Blood Sugar & BP Precision"),
        ("🚫", "Zero-Tolerance", "Severe Allergies", PURPLE_BG, PURPLE_BORDER, [
            "Celiac disease (gluten), lactose, and severe nut allergies.",
            "100% binary safety filtering with zero cross-contamination.",
            "Pantry alternative matcher when dishes cannot be cooked."
        ], "🛡️  0% Cross-Contamination Risk"),
        ("🌿", "Natural Wellness", "Seasonal & Holistic", PRIMARY_LIGHT, PRIMARY_BORDER, [
            "Eaters seeking natural body thermoregulation.",
            "Aligns diet with live local heatwaves, monsoons, and chills.",
            "Rooted in verified Ayurvedic & traditional food science."
        ], "🌡️  Thermoregulated Nutrition"),
        ("⏱️", "Daily Efficiency", "Busy Families", BLUE_BG, BLUE_BORDER, [
            "Instant whole-day meal roadmap (Breakfast to Dinner) in < 15ms.",
            "Zero tedious calorie counting or spreadsheet tracking.",
            "Pantry-friendly ingredients with simple home cooking."
        ], "⚡  Complete Day Plan in < 15ms")
    ]

    card_w = Inches(2.82)
    card_h = Inches(5.2)
    card_top = Inches(1.6)

    for i, (icon, badge, title, fill, border, pts, chip_t) in enumerate(personas):
        cx = Inches(0.66 + i * 3.06)
        create_card(s3, cx, card_top, card_w, card_h, fill_color=fill, border_color=border, border_width=1.8)
        tb_p = s3.shapes.add_textbox(cx + Inches(0.2), card_top + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.85))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        p_icon = tf_p.paragraphs[0]
        p_icon.text = icon
        p_icon.font.size = Pt(28)
        p_icon.space_after = Pt(2)

        p_badge = tf_p.add_paragraph()
        p_badge.text = badge.upper()
        p_badge.font.size = Pt(9.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = ACCENT_CORAL
        p_badge.space_after = Pt(2)

        p_title = tf_p.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(14)
        p_title.font.bold = True
        p_title.font.color.rgb = PRIMARY_DARK
        p_title.space_after = Pt(12)

        for pt in pts:
            p_pt = tf_p.add_paragraph()
            p_pt.text = f"•  {pt}"
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_BODY
            p_pt.space_after = Pt(8)

        add_pill_chip(s3, cx + Inches(0.18), card_top + Inches(4.55), card_w - Inches(0.36), Inches(0.44),
                      chip_t, bg_color=WHITE, text_color=PRIMARY_DARK)

    # =========================================================================
    # SLIDE 4: 4️⃣ TECHNICAL APPROACH (Flow Architecture + Big Metric Badges)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "4️⃣  Technical Approach", "Hybrid Clinical Engine: Fast, Safe, and Grounded",
               "Engineered for sub-15ms cached serving, strict RAG grounding, and autonomous pattern learning.")
    add_footer(s4, 4)

    # Top Architecture Layers
    layers = [
        ("📥  1. Ingestion Pipeline", "PyMuPDF, ebooklib & BS4 strip noise, extract canonical foods & composite ingredients."),
        ("🛡️  2. Clinical Hard Filters", "6-stage safety shield eliminates allergens, medical AVOID conditions & dislikes."),
        ("🧠  3. Grounded Gemini AI", "Curates complementary meals with multi-model fallback (3.6 → 3.5 → latest → 2.5)."),
        ("⚡  4. Auto-Learner & Cache", "Distills rationale into DB benefits; caches daily plan for instant local serving.")
    ]

    layer_w = Inches(2.82)
    layer_h = Inches(2.4)
    layer_top = Inches(1.6)

    for i, (ltitle, ldesc) in enumerate(layers):
        lx = Inches(0.66 + i * 3.06)
        create_card(s4, lx, layer_top, layer_w, layer_h, fill_color=WHITE, border_color=PRIMARY_BORDER, border_width=1.5)
        tb_l = s4.shapes.add_textbox(lx + Inches(0.2), layer_top + Inches(0.2), layer_w - Inches(0.4), layer_h - Inches(0.4))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True

        p0 = tf_l.paragraphs[0]
        p0.text = ltitle
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = PRIMARY_DARK
        p0.space_after = Pt(8)

        p1 = tf_l.add_paragraph()
        p1.text = ldesc
        p1.font.size = Pt(11)
        p1.font.color.rgb = TEXT_BODY

    # Bottom 3 Big Stat Metric Callout Banners
    stat_metrics = [
        ("< 15 ms", "Lightning Serving Speed", "Cached in local SQLite database; zero lag on dashboard reloads", "⚡  Instant UI Response"),
        ("0 API Calls", "Zero Rate-Limit Risk", "Page reloads make zero external API calls, ensuring high availability", "🛡️  Zero-Dependency Reloads"),
        ("100% Grounded", "Zero Hallucinations", "Every recommendation verified against published literature with citations", "📚  Peer-Reviewed Citations")
    ]

    stat_w = Inches(3.78)
    stat_h = Inches(2.55)
    stat_top = Inches(4.25)

    for i, (bignum, stitle, sdesc, chip_t) in enumerate(stat_metrics):
        sx = Inches(0.66 + i * 4.11)
        create_card(s4, sx, stat_top, stat_w, stat_h, fill_color=PRIMARY_LIGHT, border_color=PRIMARY, border_width=1.5)
        tb_s = s4.shapes.add_textbox(sx + Inches(0.2), stat_top + Inches(0.18), stat_w - Inches(0.4), stat_h - Inches(0.7))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True

        p_num = tf_s.paragraphs[0]
        p_num.text = bignum
        p_num.font.size = Pt(32)
        p_num.font.bold = True
        p_num.font.color.rgb = PRIMARY_DARK
        p_num.alignment = PP_ALIGN.CENTER

        p_t = tf_s.add_paragraph()
        p_t.text = stitle
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_CORAL
        p_t.alignment = PP_ALIGN.CENTER
        p_t.space_after = Pt(4)

        p_d = tf_s.add_paragraph()
        p_d.text = sdesc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_BODY
        p_d.alignment = PP_ALIGN.CENTER

        add_pill_chip(s4, sx + Inches(0.2), stat_top + Inches(1.95), stat_w - Inches(0.4), Inches(0.42),
                      chip_t, bg_color=WHITE, text_color=PRIMARY)

    # =========================================================================
    # SLIDE 5: 5️⃣ MARKET & BUSINESS POTENTIAL (INR Format & Zero White Space)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "5️⃣  Market & Business Potential", "Monetizing the ₹94,000+ Cr ($11.3B) Nutrition Market",
               "Multi-stream revenue model in Indian Rupees (INR): consumer freemium, clinical B2B SaaS, and quick-commerce.")
    add_footer(s5, 5)

    # Hero Market Banner in INR
    create_card(s5, Inches(0.66), Inches(1.55), Inches(12.01), Inches(1.2), fill_color=PRIMARY_DARK, border_color=PRIMARY_DARK)
    tb_m = s5.shapes.add_textbox(Inches(0.9), Inches(1.68), Inches(11.53), Inches(0.95))
    tf_m = tb_m.text_frame
    p0 = tf_m.paragraphs[0]
    p0.text = "📈  ₹94,000+ Crore ($11.3B) Global Market  ·  16.4% CAGR (2024–2030)"
    p0.font.size = Pt(20)
    p0.font.bold = True
    p0.font.color.rgb = WHITE
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf_m.add_paragraph()
    p1.text = "🇮🇳  India's Preventive Healthcare & Dietary Wellness Market is expanding at 22% CAGR, driven by the urban metabolic health crisis."
    p1.font.size = Pt(12)
    p1.font.color.rgb = RGBColor(0xD1, 0xFA, 0xE5)
    p1.alignment = PP_ALIGN.CENTER
    p1.space_before = Pt(4)

    # 3 Revenue Stream Cards with INR Pricing
    rev_streams = [
        ("👤", "B2C Consumer", "Freemium Subscription", "₹399 / Month", "₹2,999 / Year", [
            "Free: Daily verified meal plans & ingredient alternatives.",
            "Pro: Access to specialized clinical book packs (Renal, PCOS, Heart).",
            "Family health profiles with shared grocery synchronization."
        ], "🎯  Target: 50,000 Users = ₹24 Cr ARR"),
        ("🏥", "B2B Healthcare", "Clinical Dietitian SaaS", "₹14,999 / Month", "Per Hospital / Clinic", [
            "Licensed software for hospitals, outpatient dietitians & metabolic clinics.",
            "Enables doctors to upload proprietary clinical literature.",
            "Generates verified, personalized patient diet plans in 5 seconds."
        ], "🎯  Target: 500 Clinics = ₹9 Cr ARR"),
        ("🛒", "Quick-Commerce", "1-Click Grocery Carts", "3% – 7% GMV", "Affiliate Commission", [
            "API partnerships with Blinkit, Zepto, Swiggy Instamart & BigBasket.",
            "1-click 'Cart My Plan': Automatically populates required fresh ingredients.",
            "High order conversion on high-intent daily cooking recipes."
        ], "🎯  Target: ₹50 Lakhs Monthly GMV")
    ]

    card_w = Inches(3.78)
    card_h = Inches(3.9)
    card_top = Inches(2.95)

    for i, (icon, tag, title, price, period, pts, chip_t) in enumerate(rev_streams):
        cx = Inches(0.66 + i * 4.11)
        create_card(s5, cx, card_top, card_w, card_h, fill_color=WHITE, border_color=PRIMARY_BORDER, border_width=1.5)
        tb_r = s5.shapes.add_textbox(cx + Inches(0.25), card_top + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.85))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        p_tag = tf_r.paragraphs[0]
        p_tag.text = f"{icon}  {tag.upper()}"
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_CORAL
        p_tag.space_after = Pt(2)

        p_t = tf_r.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = PRIMARY_DARK

        p_pr = tf_r.add_paragraph()
        run_p = p_pr.add_run()
        run_p.text = price
        run_p.font.size = Pt(18)
        run_p.font.bold = True
        run_p.font.color.rgb = PRIMARY
        run_sub = p_pr.add_run()
        run_sub.text = f"  ({period})"
        run_sub.font.size = Pt(10)
        run_sub.font.color.rgb = TEXT_MUTED
        p_pr.space_after = Pt(10)

        for pt in pts:
            p_pt = tf_r.add_paragraph()
            p_pt.text = f"•  {pt}"
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_BODY
            p_pt.space_after = Pt(6)

        add_pill_chip(s5, cx + Inches(0.25), card_top + Inches(3.3), card_w - Inches(0.5), Inches(0.42),
                      chip_t, bg_color=PRIMARY_LIGHT, text_color=PRIMARY_DARK)

    # =========================================================================
    # SLIDE 6: 6️⃣ SCALABILITY & FUTURE (4 Enterprise Scale Cards + Full Canvas)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "6️⃣  Scalability & Future", "Engineering for Millions: Speed, Scale, and Localization",
               "Transitioning from hackathon prototype to robust enterprise-grade healthcare infrastructure.")
    add_footer(s6, 6)

    horizons = [
        ("🗄️", "Data Architecture", "PostgreSQL + pgvector", [
            "Seamless upgrade to PostgreSQL with pgvector embeddings.",
            "Sub-50ms semantic RAG search across millions of medical pages.",
            "Partitioned indexing by clinical condition & culinary region."
        ], "🚀  Q1 2027: Enterprise RAG"),
        ("⚡", "High-Throughput", "Distributed Worker Queues", [
            "Celery + Redis worker cluster for async OCR and PDF ingestion.",
            "Decouples gigabyte-scale document processing from web traffic.",
            "Auto-scaling stateless Docker containers on cloud clusters."
        ], "🚀  Q2 2027: Async Processing"),
        ("🇮🇳", "Local Access", "Indian Regional Languages", [
            "Taxonomy translation into Hindi, Tamil, Telugu, and Marathi.",
            "Support for regional cuisines (South Indian, Gujarati, Bengali).",
            "Brings clinical food intelligence to Tier 2 & Tier 3 cities."
        ], "🚀  Q3 2027: Bharat Localization"),
        ("⌚", "Biometrics", "Wearable & CGM Sync", [
            "SDK connections to Apple HealthKit, Google Fit & CGM sensors.",
            "Dynamically adjusts meal glycemic loads based on live activity.",
            "Closes the loop between daily energy burn and food intake."
        ], "🚀  Q4 2027: Continuous Sync")
    ]

    card_w = Inches(2.82)
    card_h = Inches(5.2)
    card_top = Inches(1.6)

    for i, (icon, tag, title, pts, chip_t) in enumerate(horizons):
        cx = Inches(0.66 + i * 3.06)
        create_card(s6, cx, card_top, card_w, card_h, fill_color=WHITE, border_color=PRIMARY_BORDER, border_width=1.5)
        tb_h = s6.shapes.add_textbox(cx + Inches(0.2), card_top + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.85))
        tf_h = tb_h.text_frame
        tf_h.word_wrap = True

        p_icon = tf_h.paragraphs[0]
        p_icon.text = icon
        p_icon.font.size = Pt(28)
        p_icon.space_after = Pt(2)

        p_tag = tf_h.add_paragraph()
        p_tag.text = tag.upper()
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_CORAL
        p_tag.space_after = Pt(2)

        p_title = tf_h.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(14)
        p_title.font.bold = True
        p_title.font.color.rgb = PRIMARY_DARK
        p_title.space_after = Pt(12)

        for pt in pts:
            p_pt = tf_h.add_paragraph()
            p_pt.text = f"•  {pt}"
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_BODY
            p_pt.space_after = Pt(8)

        add_pill_chip(s6, cx + Inches(0.18), card_top + Inches(4.55), card_w - Inches(0.36), Inches(0.44),
                      chip_t, bg_color=PRIMARY_LIGHT, text_color=PRIMARY)

    # =========================================================================
    # SLIDE 7: 7️⃣ IF WE HAD MORE TIME (Project "ConsumerShield" + Zero Gaps)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "7️⃣  If We Had More Time (Next Project Vision)", "Project 'ConsumerShield': Autonomous Regulatory Escalation",
               "Turning collective consumer grievances against substandard products into automated legal evidence and regulatory action.")
    add_footer(s7, 7)

    # 4-Stage Horizontal Flowchart with Rich Visual Containers
    cs_steps = [
        ("Step 1", "📸 Report with Proof", "Consumers log defective goods with receipt photos, batch numbers & lab tests.", "User Submits Evidence"),
        ("Step 2", "🔍 AI Evidence Cluster", "AI correlates independent reports to identify widespread batch safety violations.", "Pattern Detected"),
        ("Step 3", "⚖️ Auto-Legal Filing", "Auto-compiles formal petitions & dispatches directly to FSSAI & Consumer Courts.", "Petition Dispatched"),
        ("Step 4", "📢 Public Action Tracker", "Transparent dashboard tracking authority notices, recalls & corporate penalties.", "Enforcement Live")
    ]

    step_w = Inches(2.55)
    step_h = Inches(3.4)
    start_x = Inches(0.66)
    arrow_w = Inches(0.35)

    for i, (stg, stitle, sdesc, chip_t) in enumerate(cs_steps):
        bx = start_x + i * (step_w + arrow_w + Inches(0.24))
        create_card(s7, bx, Inches(1.6), step_w, step_h, fill_color=WHITE, border_color=PRIMARY_BORDER, border_width=1.5)
        tb_step = s7.shapes.add_textbox(bx + Inches(0.18), Inches(1.78), step_w - Inches(0.36), step_h - Inches(0.85))
        tf_step = tb_step.text_frame
        tf_step.word_wrap = True

        p_stg = tf_step.paragraphs[0]
        p_stg.text = stg.upper()
        p_stg.font.size = Pt(10)
        p_stg.font.bold = True
        p_stg.font.color.rgb = ACCENT_CORAL
        p_stg.space_after = Pt(2)

        p_t = tf_step.add_paragraph()
        p_t.text = stitle
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = PRIMARY_DARK
        p_t.space_after = Pt(10)

        p_d = tf_step.add_paragraph()
        p_d.text = sdesc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_BODY

        add_pill_chip(s7, bx + Inches(0.18), Inches(4.45), step_w - Inches(0.36), Inches(0.42),
                      chip_t, bg_color=PRIMARY_LIGHT, text_color=PRIMARY)

        if i < 3:
            add_arrow(s7, bx + step_w + Inches(0.08), Inches(3.05), arrow_w, Inches(0.35), color=PRIMARY)

    # Bottom Big Mission Banner (Filling full lower canvas)
    create_card(s7, Inches(0.66), Inches(5.2), Inches(12.01), Inches(1.65), fill_color=PRIMARY_DARK, border_color=PRIMARY_DARK)
    tb_vis = s7.shapes.add_textbox(Inches(0.9), Inches(5.35), Inches(11.53), Inches(1.35))
    tf_vis = tb_vis.text_frame
    tf_vis.word_wrap = True

    p_vh = tf_vis.paragraphs[0]
    p_vh.text = "🎯  The Grand Vision: Democratizing Product Safety & Consumer Justice in India"
    p_vh.font.size = Pt(17)
    p_vh.font.bold = True
    p_vh.font.color.rgb = WHITE
    p_vh.alignment = PP_ALIGN.CENTER
    p_vh.space_after = Pt(6)

    p_vb = tf_vis.add_paragraph()
    p_vb.text = "Today, corporations bury single complaints. ConsumerShield transforms individual consumer frustration into collective, legally admissible evidence — automating regulatory enforcement under the Consumer Protection Act and FSSAI guidelines to hold food & product manufacturers accountable."
    p_vb.font.size = Pt(12)
    p_vb.font.color.rgb = RGBColor(0xD1, 0xFA, 0xE5)
    p_vb.alignment = PP_ALIGN.CENTER

    output_path = "/mnt/Work/projects/hackday1.0/NutriWise_Hackday_Presentation.pptx"
    prs.save(output_path)
    print(f"Zero-blank-space presentation with INR currency saved successfully to: {output_path}")

if __name__ == "__main__":
    build_deck()
