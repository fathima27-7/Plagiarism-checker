import numpy as np
from app.utils.vectorizer import TfidfVectorizer, cosine_similarity
from app.utils.nlp_utils import split_sentences, count_words

class PlagiarismDetector:
    @staticmethod
    def analyze_document(query_doc, reference_docs, similarity_threshold=0.55):
        """
        Analyzes query document against available reference corpus and peer documents,
        and detects internal within-document duplicate content.
        
        Returns:
            dict: {
                'overall_score': float,          # 0.0 to 100.0 (unclamped)
                'matches': list[dict],           # Matched passages with offsets and sources
                'top_sources': list[dict],       # Sources with match counts
                'matching_sources_count': int,   # Number of unique matching sources
                'corpus_size': int,              # Number of documents evaluated against
                'corpus_scope_note': str         # Clear explanation of corpus scope
            }
        """
        raw_text = query_doc.raw_text or ""
        total_words = count_words(raw_text)

        if not raw_text.strip() or total_words < 5:
            return {
                'overall_score': 0.0,
                'matches': [],
                'top_sources': [],
                'matching_sources_count': 0,
                'corpus_size': len(reference_docs) if reference_docs else 0,
                'corpus_scope_note': "Document contains insufficient text for plagiarism evaluation."
            }

        query_sentences = split_sentences(raw_text)
        if not query_sentences:
            return {
                'overall_score': 0.0,
                'matches': [],
                'top_sources': [],
                'matching_sources_count': 0,
                'corpus_size': len(reference_docs) if reference_docs else 0,
                'corpus_scope_note': "No valid sentences isolated."
            }

        # Filter out very short fragments (< 4 words) from matching
        valid_query_sentences = [
            (idx, s.strip()) for idx, s in enumerate(query_sentences)
            if count_words(s) >= 4
        ]

        if not valid_query_sentences:
            return {
                'overall_score': 0.0,
                'matches': [],
                'top_sources': [],
                'matching_sources_count': 0,
                'corpus_size': len(reference_docs) if reference_docs else 0,
                'corpus_scope_note': "Document contains only very short phrases below matching threshold."
            }

        # Prepare reference corpus sentences (avoiding self-comparison and duplicate reference matches)
        ref_data = []
        all_ref_sentences = []
        eligible_refs = []
        seen_ref_keys = set()

        for ref in (reference_docs or []):
            if ref.id == query_doc.id:
                continue
            # Deduplicate reference documents by filename or hash to avoid redundant comparisons
            ref_key = (ref.filename, getattr(ref, 'file_hash', None)) if getattr(ref, 'file_hash', None) else ref.filename
            if ref_key in seen_ref_keys:
                continue
            seen_ref_keys.add(ref_key)
            eligible_refs.append(ref)

        for ref in eligible_refs:
            ref_sents = split_sentences(ref.raw_text or "")
            for s in ref_sents:
                clean_s = s.strip()
                if count_words(clean_s) >= 4:
                    all_ref_sentences.append(clean_s)
                    ref_data.append({
                        'doc_id': ref.id,
                        'title': ref.filename,
                        'sentence': clean_s
                    })

        matches = []
        matched_sentence_indices = set()
        matched_word_count = 0
        source_counts = {}

        # 1. External Corpus Matching (TF-IDF & Cosine Similarity)
        if all_ref_sentences:
            try:
                vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
                all_corpus_sents = [s for _, s in valid_query_sentences] + all_ref_sentences
                sent_tfidf = vectorizer.fit_transform(all_corpus_sents)

                num_queries = len(valid_query_sentences)
                query_tfidf = sent_tfidf[:num_queries]
                ref_tfidf = sent_tfidf[num_queries:]

                sim_matrix = cosine_similarity(query_tfidf, ref_tfidf)

                current_search_pos = 0

                for q_i, (orig_idx, q_sent) in enumerate(valid_query_sentences):
                    best_ref_idx = int(np.argmax(sim_matrix[q_i]))
                    best_sim = float(sim_matrix[q_i, best_ref_idx])

                    if best_sim >= similarity_threshold:
                        ref_match = ref_data[best_ref_idx]
                        matched_sentence_indices.add(orig_idx)

                        found_pos = raw_text.find(q_sent, current_search_pos)
                        if found_pos == -1:
                            found_pos = raw_text.find(q_sent)
                        start_char = found_pos if found_pos != -1 else 0
                        end_char = start_char + len(q_sent)
                        if found_pos != -1:
                            current_search_pos = end_char

                        words_in_sent = count_words(q_sent)
                        matched_word_count += words_in_sent

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
                            'end_char': end_char,
                            'match_type': 'External Corpus Match'
                        })
            except Exception:
                pass

        # 2. Within-Document Duplicate / Repetition Detection
        # Detects duplicated paragraphs/passages repeated within the same document
        if len(valid_query_sentences) >= 2:
            seen_sentences = {}
            for q_i, (orig_idx, q_sent) in enumerate(valid_query_sentences):
                norm_q = " ".join(q_sent.lower().split())
                if len(norm_q) < 25:
                    continue

                if norm_q in seen_sentences and orig_idx not in matched_sentence_indices:
                    # Found internal duplicate
                    first_idx, first_text = seen_sentences[norm_q]
                    matched_sentence_indices.add(orig_idx)

                    found_pos = raw_text.find(q_sent)
                    start_char = found_pos if found_pos != -1 else 0
                    end_char = start_char + len(q_sent)

                    words_in_sent = count_words(q_sent)
                    matched_word_count += words_in_sent

                    dup_source = "Internal Duplicate (Within-Document Repetition)"
                    source_counts[dup_source] = source_counts.get(dup_source, 0) + 1

                    matches.append({
                        'sentence_index': orig_idx,
                        'query_text': q_sent,
                        'matched_text': first_text,
                        'similarity_percentage': 100.0,
                        'source_document_id': query_doc.id,
                        'source_title': dup_source,
                        'start_char': start_char,
                        'end_char': end_char,
                        'match_type': 'Internal Duplicate'
                    })
                elif norm_q not in seen_sentences:
                    seen_sentences[norm_q] = (orig_idx, q_sent)

        # 3. Overall Similarity Calculation (Unclamped)
        # Ratio of matched words to total words
        overall_score = round(min(100.0, (matched_word_count / max(1, total_words)) * 100), 1)

        top_sources = [
            {'title': title, 'matches_count': count}
            for title, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        corpus_count = len(eligible_refs)
        if corpus_count == 0:
            scope_note = "Evaluation limited to within-document repetition checks. No external reference documents were available in the local repository."
        else:
            scope_note = f"Evaluated against {corpus_count} reference and peer document(s) in the local corpus. External web indexing is not enabled; zero matches in the local corpus does not guarantee absence of external plagiarism."

        return {
            'overall_score': overall_score,
            'matches': matches,
            'top_sources': top_sources,
            'matching_sources_count': len(top_sources),
            'corpus_size': corpus_count,
            'corpus_scope_note': scope_note
        }

    @staticmethod
    def compare_two_documents(doc1_text, doc2_text):
        """Calculates side-by-side comparison between two documents."""
        sents1 = split_sentences(doc1_text or "")
        sents2 = split_sentences(doc2_text or "")

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
        """N-by-N pairwise similarity matrix for multiple document comparisons."""
        if not documents:
            return {'matrix': [], 'filenames': []}

        filenames = [d.filename for d in documents]
        texts = [d.raw_text for d in documents]

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf = vectorizer.fit_transform(texts)
        sim_matrix = cosine_similarity(tfidf, tfidf)

        formatted_matrix = []
        for row in sim_matrix:
            formatted_matrix.append([round(float(val) * 100, 1) for val in row])

        return {
            'matrix': formatted_matrix,
            'filenames': filenames
        }
