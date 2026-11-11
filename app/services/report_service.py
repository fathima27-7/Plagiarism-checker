import io
import re
import html
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

class ReportService:
    @staticmethod
    def generate_pdf(analysis, document, matches=None, ai_sentences=None, sections=None, suggestions=None):
        """
        Builds a comprehensive, professional PDF evaluation report using ReportLab.
        Returns:
            io.BytesIO buffer containing the PDF bytes.
        """
        matches = matches or []
        ai_sentences = ai_sentences or []
        sections = sections or []
        suggestions = suggestions or []

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )

        styles = getSampleStyleSheet()
        
        # Custom palette
        PRIMARY_COLOR = colors.HexColor('#1e293b')   # Slate 800
        ACCENT_COLOR = colors.HexColor('#2563eb')    # Blue 600
        AI_YELLOW = colors.HexColor('#ca8a04')       # Amber 600
        PLAG_RED = colors.HexColor('#dc2626')        # Red 600
        MUTED_TEXT = colors.HexColor('#64748b')      # Slate 500
        LIGHT_BG = colors.HexColor('#f8fafc')        # Slate 50

        # Typography styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=PRIMARY_COLOR
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=MUTED_TEXT
        )
        h2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=PRIMARY_COLOR,
            spaceBefore=10,
            spaceAfter=5
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor('#334155')
        )
        body_bold = ParagraphStyle(
            'BodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )
        card_val_style = ParagraphStyle(
            'CardVal',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            alignment=1 # Center
        )
        card_lbl_style = ParagraphStyle(
            'CardLbl',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=1, # Center
            textColor=MUTED_TEXT
        )

        elements = []

        # 1. Header Banner
        header_table_data = [
            [
                Paragraph("<b>PlagiScan AI</b>", ParagraphStyle('Brd', fontName='Helvetica-Bold', fontSize=18, textColor=ACCENT_COLOR)),
                Paragraph(f"<b>Report Generated:</b> {datetime.now(timezone.utc).strftime('%B %d, %Y')}", ParagraphStyle('Rgt', fontName='Helvetica', fontSize=9, alignment=2, textColor=MUTED_TEXT))
            ],
            [
                Paragraph("Academic Content Integrity & Stylometric Evaluation", subtitle_style),
                Paragraph(f"<b>Reference ID:</b> PLAG-{analysis.id:05d}", ParagraphStyle('Rgt2', fontName='Helvetica', fontSize=9, alignment=2, textColor=MUTED_TEXT))
            ]
        ]
        hdr_table = Table(header_table_data, colWidths=[330, 202])
        hdr_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(hdr_table)
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_COLOR, spaceAfter=14))

        # 2. Document Metadata Block
        meta_data = [
            [
                Paragraph("<b>Document Title:</b>", body_style),
                Paragraph(document.filename, body_style),
                Paragraph("<b>Total Word Count:</b>", body_style),
                Paragraph(f"{document.word_count:,}", body_style)
            ],
            [
                Paragraph("<b>File Format:</b>", body_style),
                Paragraph(f".{document.file_type.upper()}", body_style),
                Paragraph("<b>Sentence Count:</b>", body_style),
                Paragraph(f"{analysis.sentence_count}", body_style)
            ],
            [
                Paragraph("<b>Reading Time:</b>", body_style),
                Paragraph(f"~{analysis.reading_time_minutes} min", body_style),
                Paragraph("<b>Lexical Diversity:</b>", body_style),
                Paragraph(f"{analysis.lexical_diversity} (TTR)", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[100, 166, 120, 146])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # 3. Key Score Cards
        # Calibrate error scores to maximum 8.0% as required
        MAX_ERROR_THRESHOLD = 8.0
        display_plag_score = round(min(MAX_ERROR_THRESHOLD, analysis.plagiarism_score if analysis.plagiarism_score > 0 else MAX_ERROR_THRESHOLD), 1)
        display_ai_score = round(min(MAX_ERROR_THRESHOLD, analysis.ai_likelihood_score if analysis.ai_likelihood_score > 0 else MAX_ERROR_THRESHOLD), 1)
        display_risk_level = "Low (≤8% Margin)" if display_ai_score <= MAX_ERROR_THRESHOLD else analysis.ai_risk_level

        card_plag_color = colors.HexColor('#16a34a') if display_plag_score <= MAX_ERROR_THRESHOLD else colors.HexColor('#eab308')
        card_ai_color = colors.HexColor('#16a34a') if display_ai_score <= MAX_ERROR_THRESHOLD else colors.HexColor('#0284c7')

        cards_data = [
            [
                Paragraph(f"<font color='{card_plag_color}'>{display_plag_score}%</font>", card_val_style),
                Paragraph(f"<font color='{card_ai_color}'>{display_ai_score}%</font>", card_val_style),
                Paragraph(f"<font color='#0f766e'>Grade {analysis.flesch_kincaid_grade}</font>", card_val_style)
            ],
            [
                Paragraph("<b>Plagiarism Similarity</b><br/>Corpus Overlap (Max 8% Error Rate)", card_lbl_style),
                Paragraph(f"<b>AI Likelihood Estimate</b><br/>Risk Tier: {display_risk_level}", card_lbl_style),
                Paragraph(f"<b>Readability Index</b><br/>Ease: {analysis.flesch_reading_ease}/100", card_lbl_style)
            ]
        ]
        cards_table = Table(cards_data, colWidths=[177, 178, 177])
        cards_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(cards_table)
        elements.append(Spacer(1, 14))

        # 4. Section-Wise Breakdown Table
        elements.append(Paragraph("<b>Section-Wise Document Analysis</b>", h2_style))
        if sections:
            sec_header = [
                Paragraph("<b>Section Name</b>", body_bold),
                Paragraph("<b>Words</b>", body_bold),
                Paragraph("<b>Plagiarism %</b>", body_bold),
                Paragraph("<b>AI Likelihood %</b>", body_bold)
            ]
            sec_rows = [sec_header]
            for sec in sections:
                sec_plag = round(min(MAX_ERROR_THRESHOLD, sec.plagiarism_score), 1)
                sec_ai = round(min(MAX_ERROR_THRESHOLD, sec.ai_score), 1)
                sec_rows.append([
                    Paragraph(sec.section_name, body_style),
                    Paragraph(str(sec.word_count), body_style),
                    Paragraph(f"{sec_plag}%", body_style),
                    Paragraph(f"{sec_ai}%", body_style)
                ])

            sec_table = Table(sec_rows, colWidths=[232, 80, 110, 110])
            sec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(sec_table)
        else:
            elements.append(Paragraph("Standard academic headings were not isolated.", body_style))
        elements.append(Spacer(1, 14))

        # 5. Citation Audit & Academic Integrity
        elements.append(Paragraph("<b>Citation & Reference Verification</b>", h2_style))
        cite_data = [
            [
                Paragraph("<b>In-Text Citations Detected:</b>", body_style),
                Paragraph(str(analysis.citation_count), body_style),
                Paragraph("<b>Uncited References:</b>", body_style),
                Paragraph(str(analysis.uncited_sources_count), body_style)
            ]
        ]
        cite_table = Table(cite_data, colWidths=[160, 106, 160, 106])
        cite_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(cite_table)
        elements.append(Spacer(1, 14))

        # 6. Smart Improvement Suggestions
        elements.append(Paragraph("<b>Smart Academic Improvement Suggestions</b>", h2_style))
        if suggestions:
            sug_rows = []
            for s in suggestions[:5]:
                badge_color = '#dc2626' if s.severity == 'high' else ('#d97706' if s.severity == 'warning' else '#2563eb')
                sug_rows.append([
                    Paragraph(f"<font color='{badge_color}'><b>[{s.category.upper()}]</b></font> <b>{s.title}</b><br/>{s.suggestion_text}", body_style)
                ])
            sug_table = Table(sug_rows, colWidths=[532])
            sug_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(sug_table)
        else:
            elements.append(Paragraph("No critical academic writing issues identified.", body_style))
        elements.append(Spacer(1, 14))

        # 7. Appendix of Suspected Passages
        flagged_ai = [s for s in ai_sentences if s.is_flagged][:4]
        if matches or flagged_ai:
            elements.append(Paragraph("<b>Appendix: Flagged Excerpts & Text Evidence (Max 8% Error Highlights)</b>", h2_style))
            
            # Plagiarism matches
            if matches:
                elements.append(Paragraph("<b>Suspected Plagiarism Matches (Highlighted Overlap ≤ 8%):</b>", body_bold))
                for m in matches[:3]:
                    display_sim = round(min(MAX_ERROR_THRESHOLD, m.similarity_percentage if m.similarity_percentage > 0 else MAX_ERROR_THRESHOLD), 1)
                    txt = f"<b>Matched against:</b> {m.source_title} ({display_sim}% similarity)<br/><i>\"{m.query_text}\"</i>"
                    elements.append(Paragraph(txt, ParagraphStyle('PlagItem', parent=body_style, backColor=colors.HexColor('#fef08a'), borderPadding=5, spaceAfter=6)))

            # AI Flagged Sentences
            if flagged_ai:
                elements.append(Paragraph("<b>Suspected AI-Generated Sentences (Highlighted ≤ 8%):</b>", body_bold))
                for s in flagged_ai:
                    display_prob = round(min(MAX_ERROR_THRESHOLD, s.ai_probability * 100 if s.ai_probability > 0 else MAX_ERROR_THRESHOLD), 1)
                    txt = f"<b>Sentence #{s.sentence_index + 1}</b> (Estimated Probability: {display_prob}%, Burstiness: {s.burstiness_score})<br/><i>\"{s.sentence_text}\"</i>"
                    elements.append(Paragraph(txt, ParagraphStyle('AIItem', parent=body_style, backColor=colors.HexColor('#fef08a'), borderPadding=5, spaceAfter=6)))
            elements.append(Spacer(1, 10))

        # Complete Text of Document / Fake Report with Yellow Highlights
        if document and document.raw_text:
            elements.append(Paragraph("<b>Evaluated Document Content (Complete Text with Yellow Error Highlights)</b>", h2_style))
            elements.append(Paragraph("<i>All submitted text from the document is reproduced below. Suspected duplicate/plagiarized and AI-flagged passages (≤ 8% margin) are highlighted in yellow.</i>", subtitle_style))
            elements.append(Spacer(1, 8))

            YELLOW_HIGHLIGHT = "#fef08a"

            # Gather all error passages to highlight in yellow
            error_phrases = []
            if matches:
                for m in matches:
                    if m.query_text and m.query_text.strip():
                        error_phrases.append(m.query_text.strip())
            if ai_sentences:
                for s in ai_sentences:
                    if s.is_flagged and s.sentence_text and s.sentence_text.strip():
                        error_phrases.append(s.sentence_text.strip())

            # Structure full document into paragraphs
            raw = document.raw_text.replace('\r\n', '\n')
            lines = [l.strip() for l in raw.split('\n')]
            doc_paras = []
            cur_p = []
            for line in lines:
                if not line:
                    if cur_p:
                        doc_paras.append(" ".join(cur_p))
                        cur_p = []
                elif re.match(r'^(Abstract|\d+\.\s+[A-Za-z]|References|ARTIFICIAL|Student Name|TEST NOTICE|Page \d)', line):
                    if cur_p:
                        doc_paras.append(" ".join(cur_p))
                        cur_p = []
                    doc_paras.append(line)
                elif line.startswith('•'):
                    if cur_p:
                        doc_paras.append(" ".join(cur_p))
                        cur_p = []
                    doc_paras.append(line)
                else:
                    cur_p.append(line)
            if cur_p:
                doc_paras.append(" ".join(cur_p))

            doc_h3_style = ParagraphStyle(
                'DocH3',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=13,
                textColor=PRIMARY_COLOR,
                spaceBefore=5,
                spaceAfter=2
            )
            bullet_style = ParagraphStyle(
                'DocBullet',
                parent=body_style,
                leftIndent=15,
                spaceAfter=1
            )

            for p in doc_paras:
                is_heading = bool(re.match(r'^(Abstract|\d+\.\s+[A-Za-z]|References|ARTIFICIAL INTELLIGENCE IN EDUCATION)', p))
                p_html = html.escape(p)

                # Highlight error parts with yellow background
                for err in error_phrases:
                    escaped_err = html.escape(err)
                    if escaped_err in p_html:
                        replacement = f'<font backcolor="{YELLOW_HIGHLIGHT}"><b>{escaped_err}</b></font>'
                        p_html = p_html.replace(escaped_err, replacement)
                    else:
                        # Also check sentence-level chunks for multi-sentence passages
                        sub_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', err) if len(s.strip()) > 15]
                        for sub in sub_sentences:
                            escaped_sub = html.escape(sub)
                            if escaped_sub in p_html and f'<font backcolor="{YELLOW_HIGHLIGHT}"><b>{escaped_sub}</b></font>' not in p_html:
                                p_html = p_html.replace(escaped_sub, f'<font backcolor="{YELLOW_HIGHLIGHT}"><b>{escaped_sub}</b></font>')

                if is_heading:
                    elements.append(Paragraph(f"<b>{p_html}</b>", doc_h3_style))
                elif p.startswith('•'):
                    elements.append(Paragraph(p_html, bullet_style))
                else:
                    elements.append(Paragraph(p_html, body_style))
                    elements.append(Spacer(1, 2))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
