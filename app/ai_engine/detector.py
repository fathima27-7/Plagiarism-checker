import math
import re
import numpy as np
from app.utils.nlp_utils import split_sentences

class AIDetector:
    # Stylometric transition markers frequent in machine-generated academic prose
    AI_TRANSITIONAL_MARKERS = [
        r'\bin conclusion\b',
        r'\bit is important to note\b',
        r'\bit is worth noting\b',
        r'\bplays a crucial role\b',
        r'\bplays a pivotal role\b',
        r'\ba testament to\b',
        r'\bdelves into\b',
        r'\bfosters a sense of\b',
        r'\brich tapestry\b',
        r'\bnavigating the\b',
        r'\bseamlessly integrates?\b',
        r'\bfurthermore,?\b',
        r'\bmoreover,?\b',
        r'\bconsequently,?\b',
        r'\badditionally,?\b',
        r'\bnot only.*but also\b',
        r'\bin summary,?\b',
        r'\bin modern times\b',
        r'\bvital aspect\b',
        r'\bcornerstone of\b'
    ]

    @staticmethod
    def analyze_document(text, ai_flag_threshold=0.65):
        """
        Estimates the likelihood of AI-generated content based on
        perplexity heuristics, burstiness variance, and stylometric markers.
        """
        sentences = split_sentences(text)
        if not sentences:
            return {
                'overall_ai_score': 0.0,
                'ai_risk_level': 'Low',
                'avg_perplexity': 0.0,
                'overall_burstiness': 0.0,
                'flagged_sentences_count': 0,
                'sentence_analyses': []
            }

        sentence_lengths = [len(s.split()) for s in sentences]
        mean_len = np.mean(sentence_lengths) if sentence_lengths else 1.0
        std_len = np.std(sentence_lengths) if sentence_lengths else 0.0
        
        overall_burstiness = float(std_len / mean_len) if mean_len > 0 else 0.0

        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        total_vocab_tokens = max(1, len(words))

        sentence_analyses = []
        flagged_count = 0
        weighted_ai_probs = []
        total_analyzed_words = 0

        current_search_pos = 0

        for idx, sentence in enumerate(sentences):
            sent_words = re.findall(r'\b[a-zA-Z]{2,}\b', sentence.lower())
            word_count = len(sent_words)

            if word_count < 4:
                prob = 0.15
                perp = 50.0
                burst = 0.5
            else:
                word_probs = [word_freq.get(w, 1) / total_vocab_tokens for w in sent_words]
                log_probs = [math.log2(p) for p in word_probs if p > 0]
                entropy = - (sum(log_probs) / len(log_probs)) if log_probs else 5.0
                perplexity = math.pow(2, min(entropy, 12.0))

                perp_score = 1.0 / (1.0 + math.exp((perplexity - 30.0) / 8.0))

                prev_len = sentence_lengths[idx - 1] if idx > 0 else mean_len
                next_len = sentence_lengths[idx + 1] if idx < len(sentences) - 1 else mean_len
                local_diff = (abs(word_count - prev_len) + abs(word_count - next_len)) / 2.0
                local_burstiness = local_diff / max(1.0, mean_len)

                burst_score = 1.0 / (1.0 + math.exp((local_burstiness - 0.30) * 10.0))

                marker_hits = 0
                for pattern in AIDetector.AI_TRANSITIONAL_MARKERS:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        marker_hits += 1
                marker_score = min(1.0, marker_hits * 0.35)

                punctuation_count = len(re.findall(r'[:;\-\—\?\"\(\)]', sentence))
                human_syntactic_bonus = min(0.35, punctuation_count * 0.12)

                raw_prob = (0.42 * perp_score) + (0.33 * burst_score) + (0.25 * marker_score) - human_syntactic_bonus
                prob = float(np.clip(raw_prob, 0.05, 0.96))
                perp = float(perplexity)
                burst = float(local_burstiness)

            is_flagged = bool(prob >= ai_flag_threshold)
            if is_flagged:
                flagged_count += 1

            found_pos = text.find(sentence, current_search_pos)
            if found_pos == -1:
                found_pos = text.find(sentence)
            start_char = found_pos if found_pos != -1 else 0
            end_char = start_char + len(sentence)
            if found_pos != -1:
                current_search_pos = end_char

            sentence_analyses.append({
                'sentence_index': idx,
                'sentence_text': sentence,
                'perplexity_score': round(perp, 1),
                'burstiness_score': round(burst, 2),
                'ai_probability': round(prob, 3),
                'is_flagged': is_flagged,
                'start_char': start_char,
                'end_char': end_char
            })

            weighted_ai_probs.append(prob * max(1, word_count))
            total_analyzed_words += max(1, word_count)

        if total_analyzed_words > 0:
            avg_prob = sum(weighted_ai_probs) / total_analyzed_words
        else:
            avg_prob = 0.0

        if overall_burstiness > 0.55:
            avg_prob *= 0.82
        elif overall_burstiness < 0.25:
            avg_prob = min(0.98, avg_prob * 1.15)

        overall_ai_score = round(float(avg_prob * 100), 1)

        if overall_ai_score >= 65.0:
            risk_level = 'High'
        elif overall_ai_score >= 35.0:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'

        avg_perp = float(np.mean([s['perplexity_score'] for s in sentence_analyses])) if sentence_analyses else 0.0

        return {
            'overall_ai_score': overall_ai_score,
            'ai_risk_level': risk_level,
            'avg_perplexity': round(avg_perp, 1),
            'overall_burstiness': round(overall_burstiness, 2),
            'flagged_sentences_count': flagged_count,
            'sentence_analyses': sentence_analyses
        }
