import math
import re
import numpy as np
from app.utils.nlp_utils import STANDARD_STOPWORDS

try:
    from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
    
    # Test if they can actually instantiate and run without DLL load failures
    _test_vec = SklearnTfidfVectorizer()
    _test_vec.fit_transform(["test sentence"])
    _USE_SKLEARN = True
except (ImportError, Exception):
    _USE_SKLEARN = False

class PureTfidfVectorizer:
    """
    High-performance, pure-Python/NumPy TF-IDF Vectorizer with identical API to scikit-learn.
    Immune to Windows Application Control DLL / C-extension restrictions.
    """
    def __init__(self, ngram_range=(1, 2), stop_words='english', min_df=1):
        self.ngram_range = ngram_range
        self.stop_words = STANDARD_STOPWORDS if stop_words == 'english' else (set(stop_words) if stop_words else set())
        self.min_df = min_df
        self.vocabulary_ = {}
        self.idf_ = np.array([])
        self.feature_names_ = []

    def _tokenize(self, text):
        raw_words = re.findall(r'\b[a-zA-Z0-9_\-\']+\b', text.lower())
        tokens = [w for w in raw_words if w not in self.stop_words and len(w) > 1]
        
        ngrams = list(tokens)
        if self.ngram_range[1] >= 2 and len(tokens) >= 2:
            for i in range(len(tokens) - 1):
                ngrams.append(f"{tokens[i]} {tokens[i+1]}")
        return ngrams

    def fit_transform(self, raw_documents):
        n_samples = len(raw_documents)
        doc_tokens_list = [self._tokenize(doc) for doc in raw_documents]

        # Compute document frequency for each term
        df = {}
        for tokens in doc_tokens_list:
            seen_in_doc = set(tokens)
            for t in seen_in_doc:
                df[t] = df.get(t, 0) + 1

        # Filter by min_df and build vocabulary
        sorted_terms = sorted([t for t, count in df.items() if count >= self.min_df])
        self.vocabulary_ = {term: idx for idx, term in enumerate(sorted_terms)}
        self.feature_names_ = sorted_terms
        vocab_size = len(sorted_terms)

        if vocab_size == 0:
            return np.zeros((n_samples, 1), dtype=np.float32)

        # Smooth IDF formulation matching scikit-learn
        # idf = ln((1 + N) / (1 + df)) + 1
        self.idf_ = np.array([
            math.log((1.0 + n_samples) / (1.0 + df[term])) + 1.0
            for term in sorted_terms
        ], dtype=np.float32)

        return self._transform_tokens(doc_tokens_list, n_samples, vocab_size)

    def transform(self, raw_documents):
        n_samples = len(raw_documents)
        vocab_size = len(self.vocabulary_)
        if vocab_size == 0:
            return np.zeros((n_samples, 1), dtype=np.float32)

        doc_tokens_list = [self._tokenize(doc) for doc in raw_documents]
        return self._transform_tokens(doc_tokens_list, n_samples, vocab_size)

    def _transform_tokens(self, doc_tokens_list, n_samples, vocab_size):
        matrix = np.zeros((n_samples, vocab_size), dtype=np.float32)

        for i, tokens in enumerate(doc_tokens_list):
            if not tokens:
                continue
            tf_counts = {}
            for t in tokens:
                if t in self.vocabulary_:
                    tf_counts[t] = tf_counts.get(t, 0) + 1

            for term, count in tf_counts.items():
                col = self.vocabulary_[term]
                # Sublinear TF: 1 + log(count)
                tf = 1.0 + math.log(count)
                matrix[i, col] = tf * self.idf_[col]

            # L2 normalization across each sample vector
            norm = np.linalg.norm(matrix[i])
            if norm > 0:
                matrix[i] = matrix[i] / norm

        return matrix

def pure_cosine_similarity(X, Y=None):
    """
    Computes cosine similarity between two 2D numpy arrays.
    """
    if Y is None:
        Y = X

    if X.size == 0 or Y.size == 0:
        return np.zeros((X.shape[0], Y.shape[0]), dtype=np.float32)

    # Compute dot product
    sim = np.dot(X, Y.T)

    # Normalize if not already L2-normalized
    norm_x = np.linalg.norm(X, axis=1, keepdims=True)
    norm_y = np.linalg.norm(Y, axis=1, keepdims=True)
    denom = np.dot(norm_x, norm_y.T)
    denom[denom == 0] = 1.0

    return np.clip(sim / denom, 0.0, 1.0)

if _USE_SKLEARN:
    TfidfVectorizer = SklearnTfidfVectorizer
    cosine_similarity = sklearn_cosine_similarity
else:
    TfidfVectorizer = PureTfidfVectorizer
    cosine_similarity = pure_cosine_similarity

