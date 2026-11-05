import re

class CitationService:
    # Regex patterns for various citation standards
    IEEE_NUMERIC_PATTERN = r'\[(\d+(?:[,\s–\-]+\d+)*)\]'
    APA_AUTHOR_YEAR_PAREN = r'\(([A-Z][a-zA-Z\s\.\&]+(?:et\s+al\.)?),\s*([12]\d{3}[a-z]?)\)'
    APA_IN_PROSE = r'\b([A-Z][a-zA-Z]+(?:\s+et\s+al\.)?)\s+\(([12]\d{3}[a-z]?)\)'

    BIBLIOGRAPHY_HEADERS = [
        r'^\s*references\s*$',
        r'^\s*bibliography\s*$',
        r'^\s*works\s+cited\s*$',
        r'^\s*literature\s+cited\s*$'
    ]

    @staticmethod
    def audit_citations(text):
        """
        Audits in-text citations against the document's bibliography section.
        Returns:
            dict: {
                'total_citations': int,
                'citation_format': str, # 'IEEE Numeric', 'APA/Author-Year', 'Mixed', or 'None'
                'citations': list[dict], # list of identified citations with match status
                'references_count': int,
                'missing_references_count': int,
                'uncited_references_count': int,
                'bibliography_entries': list[str]
            }
        """
        # 1. Locate and split References section
        body_text, bib_text, bib_entries = CitationService._extract_bibliography(text)

        # 2. Extract all in-text citations from the body text
        in_text_citations = []

        # Find IEEE/Numeric [1], [2, 3]
        for m in re.finditer(CitationService.IEEE_NUMERIC_PATTERN, body_text):
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

        # Find APA Parenthetical (Author, 2021)
        for m in re.finditer(CitationService.APA_AUTHOR_YEAR_PAREN, body_text):
            author_part = m.group(1).strip()
            year_part = m.group(2).strip()
            # Clean author key (take primary surname)
            first_author = author_part.split()[0].replace(',', '').strip()
            in_text_citations.append({
                'raw_text': m.group(0),
                'key': f"{first_author}_{year_part}".lower(),
                'type': 'APA / Harvard',
                'author': author_part,
                'year': year_part,
                'position': m.start()
            })

        # Find APA In-Prose: According to Author (2021)
        for m in re.finditer(CitationService.APA_IN_PROSE, body_text):
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

        # Determine dominant citation style
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

        # 3. Cross-reference citations with bibliography entries
        audited_citations = []
        matched_bib_indices = set()
        missing_count = 0

        for c in in_text_citations:
            is_matched = False

            if not bib_entries:
                # No bibliography found in document
                is_matched = False
            elif c['type'] == 'IEEE Numeric':
                target_num = c['key']
                for b_idx, b_entry in enumerate(bib_entries):
                    # Check if entry starts with [target_num] or target_num.
                    if re.match(rf'^\[?{target_num}\]?', b_entry.strip()):
                        is_matched = True
                        matched_bib_indices.add(b_idx)
                        break
            else: # APA
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

        uncited_references = len(bib_entries) - len(matched_bib_indices) if bib_entries else 0

        return {
            'total_citations': len(in_text_citations),
            'citation_format': dominant_format,
            'citations': audited_citations[:50],  # Return up to 50 for inspection
            'references_count': len(bib_entries),
            'missing_references_count': missing_count,
            'uncited_references_count': max(0, uncited_references),
            'has_bibliography': len(bib_entries) > 0
        }

    @staticmethod
    def _extract_bibliography(text):
        """Finds where the References/Bibliography section starts."""
        lines = text.split('\n')
        bib_start_index = -1

        for i, line in enumerate(lines):
            clean_line = line.strip().lower()
            for header_pat in CitationService.BIBLIOGRAPHY_HEADERS:
                if re.match(header_pat, clean_line):
                    bib_start_index = i
                    break
            if bib_start_index != -1:
                break

        if bib_start_index == -1:
            return text, "", []

        body_text = "\n".join(lines[:bib_start_index])
        bib_text = "\n".join(lines[bib_start_index:])

        # Parse bibliography lines into discrete entries
        bib_lines = lines[bib_start_index + 1:]
        entries = []
        current_entry = []

        for bline in bib_lines:
            s_line = bline.strip()
            if not s_line:
                if current_entry:
                    entries.append(" ".join(current_entry))
                    current_entry = []
                continue

            # If line starts with a new citation marker (e.g. [1] or Author, or hanging indent)
            if re.match(r'^\[\d+\]', s_line) or re.match(r'^\d+\.', s_line):
                if current_entry:
                    entries.append(" ".join(current_entry))
                current_entry = [s_line]
            else:
                current_entry.append(s_line)

        if current_entry:
            entries.append(" ".join(current_entry))

        return body_text, bib_text, entries

