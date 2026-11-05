import re
import numpy as np

class SectionService:
    # Standard academic heading patterns
    SECTION_PATTERNS = [
        ('Abstract', r'^\s*(?:[0-9]+\.?\s*)?abstract\b'),
        ('Introduction', r'^\s*(?:[0-9]+\.?\s*)?introduction\b'),
        ('Literature Review', r'^\s*(?:[0-9]+\.?\s*)?(?:literature\s+review|related\s+work|background)\b'),
        ('Methodology', r'^\s*(?:[0-9]+\.?\s*)?(?:methodology|materials\s+and\s+methods|system\s+design|proposed\s+method|architecture)\b'),
        ('Results & Discussion', r'^\s*(?:[0-9]+\.?\s*)?(?:results|experiments?|discussion|findings)\b'),
        ('Conclusion', r'^\s*(?:[0-9]+\.?\s*)?(?:conclusions?|future\s+work|summary)\b'),
        ('References', r'^\s*(?:[0-9]+\.?\s*)?(?:references|bibliography|works\s+cited)\b'),
    ]

    @staticmethod
    def parse_sections(text, matches=None, ai_sentences=None):
        """
        Segments the document into standard academic sections and assigns
        section-level plagiarism and AI likelihood scores.
        """
        matches = matches or []
        ai_sentences = ai_sentences or []

        lines = text.split('\n')
        detected_sections = []
        current_section = {
            'section_name': 'General Content',
            'lines': [],
            'start_char': 0,
            'end_char': 0
        }

        running_char_count = 0

        for line in lines:
            trimmed = line.strip()
            line_len = len(line) + 1 # include newline
            
            # Check if this line is an academic section header
            matched_header = None
            if len(trimmed) < 60: # Section headers are concise
                for name, pattern in SectionService.SECTION_PATTERNS:
                    if re.match(pattern, trimmed, re.IGNORECASE):
                        matched_header = name
                        break

            if matched_header:
                # Close previous section if it has content
                if current_section['lines']:
                    current_section['end_char'] = running_char_count
                    detected_sections.append(current_section)
                
                # Start new section
                current_section = {
                    'section_name': matched_header,
                    'lines': [trimmed],
                    'start_char': running_char_count,
                    'end_char': running_char_count
                }
            else:
                current_section['lines'].append(line)

            running_char_count += line_len

        # Append last section
        if current_section['lines']:
            current_section['end_char'] = running_char_count
            detected_sections.append(current_section)

        # If no explicit sections were found, create default academic chunks
        if len(detected_sections) <= 1:
            detected_sections = SectionService._fallback_chunking(text)

        # Now compute metrics for each section
        section_results = []
        for sec in detected_sections:
            sec_text = "\n".join(sec['lines']).strip()
            words = sec_text.split()
            w_count = len(words)
            if w_count == 0:
                continue

            # Calculate section plagiarism based on matches that fall within this character range
            s_start = sec['start_char']
            s_end = sec['end_char']

            sec_matches = [
                m for m in matches
                if (m.get('start_char', 0) >= s_start and m.get('start_char', 0) <= s_end)
            ]
            matched_words = sum(len(m.get('query_text', '').split()) for m in sec_matches)
            sec_plag = round(min(100.0, (matched_words / max(1, w_count)) * 100), 1)

            # Calculate section AI likelihood from ai_sentences within range
            sec_ai_sents = [
                s for s in ai_sentences
                if (s.get('start_char', 0) >= s_start and s.get('start_char', 0) <= s_end)
            ]
            if sec_ai_sents:
                sec_ai = round(float(np.mean([s['ai_probability'] for s in sec_ai_sents])) * 100, 1)
            else:
                sec_ai = 15.0

            section_results.append({
                'section_name': sec['section_name'],
                'word_count': w_count,
                'plagiarism_score': sec_plag,
                'ai_score': sec_ai,
                'content_snippet': sec_text[:250] + ('...' if len(sec_text) > 250 else '')
            })

        return section_results

    @staticmethod
    def _fallback_chunking(text):
        """Splits document into logical thirds if headers are missing."""
        paras = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paras:
            return [{'section_name': 'Entire Document', 'lines': [text], 'start_char': 0, 'end_char': len(text)}]

        n = len(paras)
        c1 = max(1, n // 3)
        c2 = max(2, (2 * n) // 3)

        return [
            {'section_name': 'Opening / Introduction', 'lines': paras[:c1], 'start_char': 0, 'end_char': len("\n\n".join(paras[:c1]))},
            {'section_name': 'Main Body / Core Discussion', 'lines': paras[c1:c2], 'start_char': len("\n\n".join(paras[:c1])), 'end_char': len("\n\n".join(paras[:c2]))},
            {'section_name': 'Findings / Closing', 'lines': paras[c2:], 'start_char': len("\n\n".join(paras[:c2])), 'end_char': len(text)}
        ]

