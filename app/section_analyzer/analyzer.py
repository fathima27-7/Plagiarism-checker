import re
import numpy as np
from app.utils.nlp_utils import count_words

class SectionAnalyzer:
    STANDARD_SECTION_PATTERNS = [
        ('Abstract', r'^\s*(?:[0-9]+\.?\s*)?abstract\b'),
        ('Introduction', r'^\s*(?:[0-9]+\.?\s*)?introduction\b'),
        ('Literature Review', r'^\s*(?:[0-9]+\.?\s*)?(?:literature\s+review|related\s+work|background|prior\s+work)\b'),
        ('Methodology', r'^\s*(?:[0-9]+\.?\s*)?(?:methodology|materials\s+and\s+methods|system\s+design|proposed\s+method|architecture|implementation)\b'),
        ('Results', r'^\s*(?:[0-9]+\.?\s*)?(?:results|findings|experimental\s+evaluation)\b'),
        ('Discussion', r'^\s*(?:[0-9]+\.?\s*)?(?:discussion|comparative\s+analysis)\b'),
        ('Results & Discussion', r'^\s*(?:[0-9]+\.?\s*)?(?:results\s+and\s+discussion|experiments?\s+and\s+findings)\b'),
        ('Conclusion', r'^\s*(?:[0-9]+\.?\s*)?(?:conclusions?|future\s+work|concluding\s+remarks|summary)\b'),
        ('References', r'^\s*(?:[0-9]+\.?\s*)?(?:references|bibliography|works\s+cited|literature\s+cited)(?:\s*\(.*?\))?\b'),
    ]

    GENERIC_NUMBERED_HEADER = r'^\s*\d+(?:\.\d+)*\.?\s+[A-Za-z]'

    @staticmethod
    def parse_sections(text, matches=None, ai_sentences=None):
        """
        Segments the document into standard or numbered academic sections.
        Guarantees that the sum of section word counts equals the total document word count.
        """
        matches = matches or []
        ai_sentences = ai_sentences or []

        if not text or not text.strip():
            return []

        lines = text.split('\n')
        detected_sections = []
        cur_section_name = 'Title & Preliminary Information'
        cur_lines = []

        for line in lines:
            trimmed = line.strip()
            matched_header = None

            if 2 < len(trimmed) < 80:
                # Check standard academic patterns
                for canonical_name, pattern in SectionAnalyzer.STANDARD_SECTION_PATTERNS:
                    if re.match(pattern, trimmed, re.IGNORECASE):
                        matched_header = trimmed
                        break

                # Check generic numbered headings (e.g., 2. Applications, 3. Advantages)
                if not matched_header and re.match(SectionAnalyzer.GENERIC_NUMBERED_HEADER, trimmed):
                    matched_header = trimmed

            if matched_header:
                if cur_lines and any(l.strip() for l in cur_lines):
                    detected_sections.append({
                        'section_name': cur_section_name,
                        'lines': cur_lines
                    })
                cur_section_name = matched_header
                cur_lines = [line]
            else:
                cur_lines.append(line)

        if cur_lines and any(l.strip() for l in cur_lines):
            detected_sections.append({
                'section_name': cur_section_name,
                'lines': cur_lines
            })

        # Fallback chunking if no structural headings were found
        if len(detected_sections) <= 1:
            detected_sections = SectionAnalyzer._fallback_chunking(text)

        total_doc_words = count_words(text)
        section_results = []
        accumulated_words = 0

        # Running character offset tracker for accurate match mapping
        running_char_offset = 0

        for i, sec in enumerate(detected_sections):
            sec_text = "\n".join(sec['lines'])
            w_count = count_words(sec_text)
            
            # Skip completely empty sections (e.g. only whitespace)
            if w_count == 0 and len(detected_sections) > 1:
                continue

            sec_start_char = running_char_offset
            sec_end_char = sec_start_char + len(sec_text)
            running_char_offset = sec_end_char + 1

            # Map matching plagiarism passages inside this section
            sec_matches = [
                m for m in matches
                if (m.get('start_char', 0) >= sec_start_char and m.get('start_char', 0) <= sec_end_char)
                or (m.get('query_text', '') in sec_text)
            ]
            matched_words = sum(count_words(m.get('query_text', '')) for m in sec_matches)
            sec_plag = round(min(100.0, (matched_words / max(1, w_count)) * 100), 1) if w_count > 0 else 0.0

            # Map AI sentence probabilities in this section
            sec_ai_sents = [
                s for s in ai_sentences
                if (s.get('start_char', 0) >= sec_start_char and s.get('start_char', 0) <= sec_end_char)
                or (s.get('sentence_text', '') in sec_text)
            ]
            if sec_ai_sents:
                sec_ai = round(float(np.mean([s['ai_probability'] for s in sec_ai_sents])) * 100, 1)
            else:
                sec_ai = 0.0

            clean_snippet = re.sub(r'\s+', ' ', sec_text).strip()
            snippet = clean_snippet[:220] + ('...' if len(clean_snippet) > 220 else '')

            section_results.append({
                'section_name': sec['section_name'],
                'word_count': w_count,
                'plagiarism_score': sec_plag,
                'ai_score': sec_ai,
                'content_snippet': snippet,
                'section_text': sec_text
            })
            accumulated_words += w_count

        # Reconciliation check
        # If there is any rounding or trailing space variance, reconcile with the last section
        if section_results and accumulated_words != total_doc_words:
            diff = total_doc_words - accumulated_words
            section_results[-1]['word_count'] += diff

        return section_results

    @staticmethod
    def _fallback_chunking(text):
        paras = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paras:
            return [{'section_name': 'Entire Document', 'lines': [text]}]

        n = len(paras)
        if n == 1:
            return [{'section_name': 'Entire Document', 'lines': paras}]
        elif n == 2:
            return [
                {'section_name': 'Opening / Introduction', 'lines': [paras[0]]},
                {'section_name': 'Core Content', 'lines': [paras[1]]}
            ]

        c1 = max(1, n // 3)
        c2 = max(2, (2 * n) // 3)

        return [
            {'section_name': 'Opening / Introduction', 'lines': paras[:c1]},
            {'section_name': 'Main Body / Core Discussion', 'lines': paras[c1:c2]},
            {'section_name': 'Findings / Closing', 'lines': paras[c2:]}
        ]
