import re
from app.utils.nlp_utils import split_sentences, count_syllables, tokenize_words, count_words

class QualityAnalyzer:
    PASSIVE_VOICE_PATTERN = r'\b(is|are|was|were|be|been|being)\s+([a-z]+ed|written|done|found|shown|taken|given|seen|conducted|performed|analyzed|evaluated)\b'

    @staticmethod
    def analyze(text):
        """
        Computes readability indices, lexical diversity, and stylistic metrics.
        Uses centralized word tokenization for exact consistency.
        """
        if not text or not text.strip():
            return {
                'flesch_reading_ease': 0.0,
                'flesch_kincaid_grade': 0.0,
                'reading_ease_label': 'Insufficient Text',
                'reading_time_minutes': 0.0,
                'lexical_diversity': 0.0,
                'sentence_count': 0,
                'word_count': 0,
                'avg_sentence_length': 0.0,
                'avg_word_length': 0.0,
                'avg_syllables_per_word': 0.0,
                'passive_voice_count': 0,
                'passive_voice_percentage': 0.0,
                'long_sentences_count': 0,
                'interpretation': 'No text provided for evaluation.'
            }

        sentences = split_sentences(text)
        words = tokenize_words(text.lower())
        
        num_sentences = max(1, len(sentences))
        num_words = max(1, len(words))

        # Handle very short documents (< 10 words) safely
        if num_words < 10:
            return {
                'flesch_reading_ease': 65.0,
                'flesch_kincaid_grade': 8.0,
                'reading_ease_label': 'Short Sample',
                'reading_time_minutes': 0.1,
                'lexical_diversity': round(len(set(words)) / num_words, 2),
                'sentence_count': len(sentences),
                'word_count': len(words),
                'avg_sentence_length': round(num_words / num_sentences, 1),
                'avg_word_length': round(sum(len(w) for w in words) / num_words, 1),
                'avg_syllables_per_word': 1.5,
                'passive_voice_count': 0,
                'passive_voice_percentage': 0.0,
                'long_sentences_count': 0,
                'interpretation': 'Document contains very few words; readability formulas provide approximations only.'
            }

        total_syllables = sum(count_syllables(w) for w in words)
        avg_syllables = total_syllables / num_words
        avg_sent_len = num_words / num_sentences
        avg_word_len = sum(len(w) for w in words) / num_words

        # Standard Flesch Reading Ease Formula
        flesch_ease = 206.835 - (1.015 * avg_sent_len) - (84.6 * avg_syllables)
        flesch_ease = max(0.0, min(100.0, flesch_ease))

        # Standard Flesch-Kincaid Grade Level Formula
        fk_grade = (0.39 * avg_sent_len) + (11.8 * avg_syllables) - 15.59
        fk_grade = max(1.0, min(20.0, fk_grade))

        if flesch_ease >= 70.0:
            ease_label = "Fairly Easy (High School Level)"
            interpretation = "Clear, straightforward prose suitable for general audiences."
        elif flesch_ease >= 50.0:
            ease_label = "Standard / Moderate (Undergraduate Level)"
            interpretation = "Standard technical complexity appropriate for college coursework."
        elif flesch_ease >= 30.0:
            ease_label = "Difficult (College Academic Level)"
            interpretation = "Scholarly vocabulary and sentence complexity typical of peer-reviewed literature."
        else:
            ease_label = "Very Difficult (Advanced Graduate / Research Level)"
            interpretation = "Dense academic prose with specialized syntax and compound technical terminology."

        unique_words = len(set(words))
        ttr = round(unique_words / num_words, 2)
        reading_time = max(0.1, round(num_words / 200.0, 1))

        passive_count = 0
        long_sentences = 0
        for s in sentences:
            if re.search(QualityAnalyzer.PASSIVE_VOICE_PATTERN, s, re.IGNORECASE):
                passive_count += 1
            if count_words(s) > 35:
                long_sentences += 1

        passive_pct = round((passive_count / num_sentences) * 100, 1)

        return {
            'flesch_reading_ease': round(flesch_ease, 1),
            'flesch_kincaid_grade': round(fk_grade, 1),
            'reading_ease_label': ease_label,
            'reading_time_minutes': reading_time,
            'lexical_diversity': ttr,
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': round(avg_sent_len, 1),
            'avg_word_length': round(avg_word_len, 1),
            'avg_syllables_per_word': round(avg_syllables, 2),
            'passive_voice_count': passive_count,
            'passive_voice_percentage': passive_pct,
            'long_sentences_count': long_sentences,
            'interpretation': interpretation
        }
