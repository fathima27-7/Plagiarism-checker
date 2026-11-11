import os
from app.utils.vectorizer import TfidfVectorizer, cosine_similarity
import numpy as np
from app.services.nlp_utils import split_sentences
from app.models.document import Document

class PlagiarismService:
    @staticmethod
    def analyze_document(query_doc, reference_docs, similarity_threshold=0.55):
        """
        Analyzes query document against all available reference documents.
        Returns:
            dict: {
                'overall_score': float, # 0 to 100
                'matches': list[dict],  # Sentence-level matches
                'top_sources': list[dict]
            }
        """
        query_sentences = split_sentences(query_doc.raw_text)
        if not query_sentences:
            return {'overall_score': 0.0, 'matches': [], 'top_sources': []}

        if not reference_docs:
            return {'overall_score': 0.0, 'matches': [], 'top_sources': []}

        # Build corpus of reference documents and their individual sentences
        ref_data = [] # list of (doc_id, doc_title, sentence)
        all_ref_sentences = []

        for ref in reference_docs:
            if ref.id == query_doc.id:
                continue
            ref_sentences = split_sentences(ref.raw_text)
            for s in ref_sentences:
                clean_s = s.strip()
                if len(clean_s.split()) >= 4:  # Only consider sentences with at least 4 words
                    all_ref_sentences.append(clean_s)
                    ref_data.append({
                        'doc_id': ref.id,
                        'title': ref.filename,
                        'sentence': clean_s
                    })

        if not all_ref_sentences:
            return {'overall_score': 0.0, 'matches': [], 'top_sources': []}

        # Global document-level TF-IDF similarity
        all_doc_texts = [query_doc.raw_text] + [ref.raw_text for ref in reference_docs if ref.id != query_doc.id]
        doc_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
        doc_tfidf = doc_vectorizer.fit_transform(all_doc_texts)
        global_similarities = cosine_similarity(doc_tfidf[0:1], doc_tfidf[1:]).flatten()

        # Sentence-level granular matching
        # Vectorize all query sentences and all reference sentences together
        valid_query_sentences = [(idx, s) for idx, s in enumerate(query_sentences) if len(s.split()) >= 4]
        if not valid_query_sentences:
            return {'overall_score': 0.0, 'matches': [], 'top_sources': []}

        sent_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        all_sents = [s for _, s in valid_query_sentences] + all_ref_sentences
        sent_tfidf = sent_vectorizer.fit_transform(all_sents)

        num_queries = len(valid_query_sentences)
        query_tfidf = sent_tfidf[:num_queries]
        ref_tfidf = sent_tfidf[num_queries:]

        sim_matrix = cosine_similarity(query_tfidf, ref_tfidf)

        matches = []
        plagiarized_word_count = 0
        source_counts = {}

        # Search query text for character start/end offsets
        current_search_pos = 0
        full_text = query_doc.raw_text

        for q_i, (orig_idx, q_sent) in enumerate(valid_query_sentences):
            best_ref_idx = int(np.argmax(sim_matrix[q_i]))
            best_sim = float(sim_matrix[q_i, best_ref_idx])

            if best_sim >= similarity_threshold:
                ref_match = ref_data[best_ref_idx]
                
                # Locate character offset
                found_pos = full_text.find(q_sent, current_search_pos)
                if found_pos == -1:
                    found_pos = full_text.find(q_sent)
                
                start_char = found_pos if found_pos != -1 else 0
                end_char = start_char + len(q_sent)
                if found_pos != -1:
                    current_search_pos = end_char

                words_in_sent = len(q_sent.split())
                plagiarized_word_count += words_in_sent

                src_title = ref_match['title']
                source_counts[src_title] = source_counts.get(src_title, 0) + 1

                matches.append({
                    'sentence_index': orig_idx,
                    'query_text': q_sent,
                    'matched_text': ref_match['sentence'],
                    'similarity_percentage': round(best_sim * 100, 1),
                    'source_document_id': ref_match['doc_id'],
                    'source_title': src_title,
                    'start_char': start_char,
                    'end_char': end_char
                })

        total_words = max(1, query_doc.word_count)
        # Ratio of matched words to total words, smoothed with global max similarity
        max_global_sim = float(np.max(global_similarities)) * 100 if len(global_similarities) > 0 else 0.0
        word_ratio_score = min(100.0, (plagiarized_word_count / total_words) * 100)
        
        # Weighted overall score (70% fine-grained matched token coverage, 30% global doc vector alignment)
        overall_score = round(0.70 * word_ratio_score + 0.30 * min(word_ratio_score, max_global_sim), 1)
        if matches and overall_score < 5.0:
            overall_score = round(word_ratio_score, 1)

        # Ranked list of source contributions
        top_sources = [
            {'title': title, 'matches_count': count}
            for title, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            'overall_score': min(100.0, overall_score),
            'matches': matches,
            'top_sources': top_sources
        }

    @staticmethod
    def compare_two_documents(doc1_text, doc2_text):
        """
        Calculates side-by-side comparison between two documents.
        Returns:
            dict: {
                'overall_similarity': float,
                'doc1_sentences': list[dict], # with match info
                'doc2_sentences': list[dict]
            }
        """
        sents1 = split_sentences(doc1_text)
        sents2 = split_sentences(doc2_text)

        if not sents1 or not sents2:
            return {'overall_similarity': 0.0, 'doc1_sentences': [], 'doc2_sentences': []}

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        all_sents = sents1 + sents2
        tfidf = vectorizer.fit_transform(all_sents)

        tfidf1 = tfidf[:len(sents1)]
        tfidf2 = tfidf[len(sents1):]

        matrix = cosine_similarity(tfidf1, tfidf2)

        doc1_annotated = []
        doc2_annotated = []

        # Find best matches for doc1
        for i, s1 in enumerate(sents1):
            best_j = int(np.argmax(matrix[i]))
            best_score = float(matrix[i, best_j])
            is_match = best_score >= 0.50
            doc1_annotated.append({
                'index': i,
                'text': s1,
                'is_match': is_match,
                'matched_with_index': best_j if is_match else None,
                'score': round(best_score * 100, 1) if is_match else 0.0
            })

        # Find best matches for doc2
        for j, s2 in enumerate(sents2):
            best_i = int(np.argmax(matrix[:, j]))
            best_score = float(matrix[best_i, j])
            is_match = best_score >= 0.50
            doc2_annotated.append({
                'index': j,
                'text': s2,
                'is_match': is_match,
                'matched_with_index': best_i if is_match else None,
                'score': round(best_score * 100, 1) if is_match else 0.0
            })

        # Global similarity between the two documents
        doc_vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        doc_tfidf = doc_vec.fit_transform([doc1_text, doc2_text])
        global_score = float(cosine_similarity(doc_tfidf[0:1], doc_tfidf[1:2])[0][0]) * 100

        return {
            'overall_similarity': round(global_score, 1),
            'doc1_sentences': doc1_annotated,
            'doc2_sentences': doc2_annotated
        }

    @staticmethod
    def compare_multiple_documents(documents):
        """
        N-by-N pairwise similarity matrix for multiple document comparisons.
        """
        if not documents:
            return {'matrix': [], 'filenames': []}

        filenames = [d.filename for d in documents]
        texts = [d.raw_text for d in documents]

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf = vectorizer.fit_transform(texts)
        sim_matrix = cosine_similarity(tfidf, tfidf)

        # Format matrix as percentages rounded to 1 decimal place
        formatted_matrix = []
        for row in sim_matrix:
            formatted_matrix.append([round(float(val) * 100, 1) for val in row])

        return {
            'matrix': formatted_matrix,
            'filenames': filenames
        }

