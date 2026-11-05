import re
from app.services.nlp_utils import split_sentences, count_syllables

class ReadabilityService:
    # Heuristic passive voice markers: forms of 'to be' followed by past participle (-ed, irregulars)
    PASSIVE_VOICE_PATTERN = r'\b(is|are|was|were|be|been|being)\s+([a-z]+ed|written|done|found|shown|taken|given|seen|conducted|performed|analyzed|evaluated)\b'

    @staticmethod
    def analyze(text):
        """
        Computes readability indices, lexical diversity, and stylistic metrics.
        Returns:
            dict: {
                'flesch_reading_ease': float,
                'flesch_kincaid_grade': float,
                'reading_ease_label': str,
                'reading_time_minutes': float,
                'lexical_diversity': float,
                'sentence_count': int,
                'word_count': int,
                'avg_sentence_length': float,
                'avg_syllables_per_word': float,
                'passive_voice_count': int,
                'passive_voice_percentage': float,
                'long_sentences_count': int
            }
        """
        sentences = split_sentences(text)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        
        num_sentences = max(1, len(sentences))
        num_words = max(1, len(words))

        # Syllable count
        total_syllables = sum(count_syllables(w) for w in words)
        avg_syllables = total_syllables / num_words
        avg_sent_len = num_words / num_sentences

        # 1. Flesch Reading Ease Formula
        flesch_ease = 206.835 - (1.015 * avg_sent_len) - (84.6 * avg_syllables)
        flesch_ease = max(0.0, min(100.0, flesch_ease))

        # 2. Flesch-Kincaid Grade Level
        fk_grade = (0.39 * avg_sent_len) + (11.8 * avg_syllables) - 15.59
        fk_grade = max(1.0, min(20.0, fk_grade))

        # Interpret Reading Ease
        if flesch_ease >= 70.0:
            ease_label = "Fairly Easy (High School Level)"
        elif flesch_ease >= 50.0:
            ease_label = "Standard / Moderate (Undergraduate Level)"
        elif flesch_ease >= 30.0:
            ease_label = "Difficult (College Academic Level)"
        else:
            ease_label = "Very Difficult (Advanced Graduate / Research Level)"

        # 3. Lexical Diversity (Type-Token Ratio)
        unique_words = len(set(words))
        ttr = round(unique_words / num_words, 2)

        # 4. Reading time at 200 words per minute
        reading_time = round(num_words / 200.0, 1)

        # 5. Passive Voice Detection
        passive_count = 0
        long_sentences = 0
        for s in sentences:
            if re.search(ReadabilityService.PASSIVE_VOICE_PATTERN, s, re.IGNORECASE):
                passive_count += 1
            if len(s.split()) > 35:
                long_sentences += 1

        passive_pct = round((passive_count / num_sentences) * 100, 1)

        return {
            'flesch_reading_ease': round(flesch_ease, 1),
            'flesch_kincaid_grade': round(fk_grade, 1),
            'reading_ease_label': ease_label,
            'reading_time_minutes': reading_time,
            'lexical_diversity': ttr,
            'sentence_count': num_sentences,
            'word_count': num_words,
            'avg_sentence_length': round(avg_sent_len, 1),
            'avg_syllables_per_word': round(avg_syllables, 2),
            'passive_voice_count': passive_count,
            'passive_voice_percentage': passive_pct,
            'long_sentences_count': long_sentences
        }

