class QualitySuggester:
    @staticmethod
    def generate_suggestions(analysis_data):
        """
        Generates actionable academic recommendations based on analysis metrics.
        """
        suggestions = []

        plag_score = analysis_data.get('plagiarism_score', 0.0)
        ai_score = analysis_data.get('ai_likelihood_score', 0.0)
        readability = analysis_data.get('readability', {})
        citations = analysis_data.get('citations', {})
        sections = analysis_data.get('sections', [])
        matches = analysis_data.get('matches', [])

        if plag_score > 25.0:
            suggestions.append({
                'category': 'Plagiarism',
                'severity': 'high',
                'title': 'High Similarity Detected',
                'suggestion_text': f'Your document shows {plag_score}% textual similarity with the reference database. Consider paraphrasing matched passages using original phrasing and providing explicit quotation marks where direct quotations are preserved.',
                'example_text': f'{len(matches)} overlapping passage(s) flagged for revision.'
            })
        elif plag_score > 10.0:
            suggestions.append({
                'category': 'Plagiarism',
                'severity': 'warning',
                'title': 'Moderate Content Overlap',
                'suggestion_text': 'Several sentences closely mirror reference material. Review the highlighted passages in the comparison viewer and ensure all referenced ideas cite their original authors.',
                'example_text': None
            })
        else:
            suggestions.append({
                'category': 'Plagiarism',
                'severity': 'info',
                'title': 'Low Textual Overlap',
                'suggestion_text': 'Content demonstrates high lexical originality compared to available reference documents.',
                'example_text': None
            })

        if ai_score > 60.0:
            suggestions.append({
                'category': 'AI Writing',
                'severity': 'high',
                'title': 'High Predictability and Uniformity (AI Likelihood)',
                'suggestion_text': 'Multiple passages exhibit uniform sentence lengths and standard synthetic transition markers characteristic of LLMs. Vary your sentence rhythm by alternating short assertions with compound-complex sentences, and replace generic transitions with domain-specific explanations.',
                'example_text': 'Avoid overused boilerplate transitions like "In conclusion, it is important to note..." or "plays a crucial role".'
            })
        elif ai_score > 35.0:
            suggestions.append({
                'category': 'AI Writing',
                'severity': 'warning',
                'title': 'Moderate AI-Assisted Style Characteristics',
                'suggestion_text': 'Certain sections display low burstiness (uniform cadence). Introducing personal critical analysis, active case examples, or empirical observations can enhance authentic academic voice.',
                'example_text': None
            })

        missing_bib = citations.get('missing_references_count', 0)
        uncited_refs = citations.get('uncited_references_count', 0)
        has_bib = citations.get('has_bibliography', True)

        if not has_bib:
            suggestions.append({
                'category': 'Citations',
                'severity': 'high',
                'title': 'Missing References Section',
                'suggestion_text': 'No standard "References" or "Bibliography" heading was detected. Academic integrity requires an enumerated or alphabetical list of referenced literature at the end of the paper.',
                'example_text': 'Add a dedicated section titled "References" formatted according to APA or IEEE guidelines.'
            })
        else:
            if missing_bib > 0:
                suggestions.append({
                    'category': 'Citations',
                    'severity': 'warning',
                    'title': f'{missing_bib} In-Text Citation(s) Missing from Bibliography',
                    'suggestion_text': 'Found in-text citations that do not appear to match any entry in your References section. Ensure every cited author or bracketed numeral has a corresponding complete citation.',
                    'example_text': None
                })
            if uncited_refs > 0:
                suggestions.append({
                    'category': 'Citations',
                    'severity': 'info',
                    'title': f'{uncited_refs} Bibliography Entry/Entries Never Cited In-Text',
                    'suggestion_text': 'Your bibliography contains entries that are never referenced directly in the body text. Remove unconsulted works or insert the appropriate in-text citations.',
                    'example_text': None
                })

        passive_pct = readability.get('passive_voice_percentage', 0.0)
        long_sents = readability.get('long_sentences_count', 0)

        if long_sents > 3:
            suggestions.append({
                'category': 'Readability',
                'severity': 'warning',
                'title': f'{long_sents} Overly Long Sentences (>35 Words)',
                'suggestion_text': 'Overextended sentences can obscure technical arguments. Consider splitting compound sentences at coordinating conjunctions to improve readability and reader comprehension.',
                'example_text': None
            })

        if passive_pct > 28.0:
            suggestions.append({
                'category': 'Style',
                'severity': 'warning',
                'title': f'High Passive Voice Density ({passive_pct}%)',
                'suggestion_text': 'While passive voice is acceptable in methodology sections, excessive passive constructions make findings appear detached. Use active voice verbs where human agency or experimental action took place.',
                'example_text': None
            })

        sec_names = [s.get('section_name', '') for s in sections]
        standard_expected = ['Abstract', 'Introduction', 'Methodology', 'Conclusion']
        missing_sections = [req for req in standard_expected if not any(req.lower() in s.lower() for s in sec_names)]

        if missing_sections:
            suggestions.append({
                'category': 'Structure',
                'severity': 'info',
                'title': f'Recommended Sections Missing: {", ".join(missing_sections)}',
                'suggestion_text': 'Formal academic research papers typically include standard IMRAD headers (Introduction, Methods, Results, and Discussion). Adding clear structural headings improves peer readability and indexing.',
                'example_text': None
            })

        return suggestions

