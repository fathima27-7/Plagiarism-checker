import re

class CitationChecker:
    IEEE_NUMERIC_PATTERN = r'\[(\d+(?:[,\s–\-]+\d+)*)\]'
    APA_AUTHOR_YEAR_PAREN = r'\(([A-Z][a-zA-Z\s\.\&]+(?:et\s+al\.)?),\s*([12]\d{3}[a-z]?)\)'
    APA_IN_PROSE = r'\b([A-Z][a-zA-Z]+(?:\s+et\s+al\.)?)\s+\(([12]\d{3}[a-z]?)\)'

    BIBLIOGRAPHY_HEADERS = [
        r'^\s*(?:\d+\.?\s*)?(?:references|bibliography|works\s+cited|literature\s+cited)(?:\s*\(.*?\))?\s*:?\s*$'
    ]

    @staticmethod
    def audit_citations(text):
        """
        Audits in-text citations against the document's bibliography section.
        Distinguishes automated format checking from factual existence.
        """
        if not text:
            return {
                'total_citations': 0,
                'citation_format': 'None Detected',
                'citations': [],
                'references_count': 0,
                'missing_references_count': 0,
                'uncited_references_count': 0,
                'has_bibliography': False,
                'verification_note': 'No document text available.'
            }

        body_text, bib_text, bib_entries = CitationChecker._extract_bibliography(text)

        in_text_citations = []

        # 1. IEEE numeric [1], [1, 2], [1-3]
        for m in re.finditer(CitationChecker.IEEE_NUMERIC_PATTERN, body_text):
            raw_match = m.group(0)
            inner_nums = re.findall(r'\d+', m.group(1))
            for num in inner_nums:
                in_text_citations.append({
                    'raw_text': raw_match,
                    'key': num,
                    'type': 'IEEE Numeric',
                    'author': None,
                    'year': None,
                    'position': m.start()
                })

        # 2. APA author-year in parentheses: (Smith, 2020)
        for m in re.finditer(CitationChecker.APA_AUTHOR_YEAR_PAREN, body_text):
            author_part = m.group(1).strip()
            year_part = m.group(2).strip()
            first_author = author_part.split()[0].replace(',', '').strip()
            in_text_citations.append({
                'raw_text': m.group(0),
                'key': f"{first_author}_{year_part}".lower(),
                'type': 'APA / Harvard',
                'author': author_part,
                'year': year_part,
                'position': m.start()
            })

        # 3. APA author in prose: Smith (2020)
        for m in re.finditer(CitationChecker.APA_IN_PROSE, body_text):
            author_part = m.group(1).strip()
            year_part = m.group(2).strip()
            first_author = author_part.split()[0].replace(',', '').strip()
            in_text_citations.append({
                'raw_text': m.group(0),
                'key': f"{first_author}_{year_part}".lower(),
                'type': 'APA / Harvard',
                'author': author_part,
                'year': year_part,
                'position': m.start()
            })

        ieee_count = sum(1 for c in in_text_citations if c['type'] == 'IEEE Numeric')
        apa_count = sum(1 for c in in_text_citations if c['type'] == 'APA / Harvard')

        if ieee_count > 0 and apa_count == 0:
            dominant_format = 'IEEE (Numeric)'
        elif apa_count > 0 and ieee_count == 0:
            dominant_format = 'APA / Harvard (Author-Date)'
        elif ieee_count > 0 and apa_count > 0:
            dominant_format = 'Mixed Styles'
        else:
            dominant_format = 'None Detected'

        audited_citations = []
        matched_bib_indices = set()
        missing_count = 0

        for c in in_text_citations:
            is_matched = False

            if not bib_entries:
                is_matched = False
            elif c['type'] == 'IEEE Numeric':
                target_num = c['key']
                for b_idx, b_entry in enumerate(bib_entries):
                    # Match [1] or 1. or 1 at start of entry
                    if re.match(rf'^\[?{target_num}\]?[.\s]', b_entry.strip()) or re.match(rf'^{target_num}\b', b_entry.strip()):
                        is_matched = True
                        matched_bib_indices.add(b_idx)
                        break
            else:
                author_keyword = c['author'].split()[0].lower() if c['author'] else ''
                year_keyword = c['year'] if c['year'] else ''
                for b_idx, b_entry in enumerate(bib_entries):
                    b_lower = b_entry.lower()
                    if author_keyword in b_lower and (not year_keyword or year_keyword in b_lower):
                        is_matched = True
                        matched_bib_indices.add(b_idx)
                        break

            if not is_matched and bib_entries:
                missing_count += 1

            audited_citations.append({
                'citation_text': c['raw_text'],
                'citation_type': c['type'],
                'is_in_bibliography': is_matched,
                'position_index': c['position']
            })

        uncited_references = max(0, len(bib_entries) - len(matched_bib_indices)) if bib_entries else 0

        verification_note = "Automated cross-referencing verifies bibliographic correspondence between in-text markers and the references section. It does not verify external factual existence or DOI validity."

        return {
            'total_citations': len(in_text_citations),
            'citation_format': dominant_format,
            'citations': audited_citations[:50],
            'references_count': len(bib_entries),
            'missing_references_count': missing_count,
            'uncited_references_count': uncited_references,
            'has_bibliography': len(bib_entries) > 0,
            'verification_note': verification_note
        }

    @staticmethod
    def _extract_bibliography(text):
        lines = text.split('\n')
        bib_start_index = -1

        for i, line in enumerate(lines):
            clean_line = line.strip().lower()
            if 2 < len(clean_line) < 60:
                for header_pat in CitationChecker.BIBLIOGRAPHY_HEADERS:
                    if re.match(header_pat, clean_line):
                        bib_start_index = i
                        break
                if bib_start_index != -1:
                    break

        if bib_start_index == -1:
            return text, "", []

        body_text = "\n".join(lines[:bib_start_index])
        bib_text = "\n".join(lines[bib_start_index:])

        bib_lines = lines[bib_start_index + 1:]
        entries = []
        current_entry = []

        for bline in bib_lines:
            s_line = bline.strip()
            if not s_line:
                continue

            # Detect new citation entry (starts with [1], 1., or standalone number)
            if re.match(r'^\[\d+\]', s_line) or re.match(r'^\d+\.', s_line) or re.match(r'^\d+$', s_line):
                if current_entry:
                    entries.append(" ".join(current_entry))
                current_entry = [s_line]
            else:
                if current_entry:
                    current_entry.append(s_line)
                else:
                    current_entry = [s_line]

        if current_entry:
            entries.append(" ".join(current_entry))

        return body_text, bib_text, entries
