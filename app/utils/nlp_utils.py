import re

# Comprehensive list of standard English stopwords for offline resilience
STANDARD_STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
    'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
    'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren',
    "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn',
    "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
    "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn',
    "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def split_sentences(text):
    """
    Robust sentence splitter that preserves sentence boundary punctuation
    and doesn't split on common abbreviations (e.g., et al., e.g., i.e., Dr., Prof., Fig., Vol., pp.)
    """
    if not text or not text.strip():
        return []
    
    normalized = re.sub(r'[ \t]+', ' ', text.strip())
    
    # Protect common academic abbreviations from false sentence breaks
    protected = normalized
    abbreviations = [
        (r'\bet al\.', 'et_al_PROTECTED'),
        (r'\be\.g\.', 'eg_PROTECTED'),
        (r'\bi\.e\.', 'ie_PROTECTED'),
        (r'\bFig\.', 'Fig_PROTECTED'),
        (r'\bDr\.', 'Dr_PROTECTED'),
        (r'\bProf\.', 'Prof_PROTECTED'),
        (r'\bVol\.', 'Vol_PROTECTED'),
        (r'\bNo\.', 'No_PROTECTED'),
        (r'\bpp\.', 'pp_PROTECTED'),
        (r'\bvs\.', 'vs_PROTECTED'),
    ]
    for pattern, repl in abbreviations:
        protected = re.sub(pattern, repl, protected, flags=re.IGNORECASE)

    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\(\[])', protected)
    
    sentences = []
    for s in raw_sentences:
        clean_s = s.strip()
        for pattern, repl in abbreviations:
            original = pattern.replace(r'\b', '').replace('\\', '')
            clean_s = clean_s.replace(repl, original)
        if len(clean_s) > 5:
            sentences.append(clean_s)
            
    if not sentences and normalized:
        sentences = [p.strip() for p in normalized.split('\n') if len(p.strip()) > 5]

    return sentences

def count_syllables(word):
    """Heuristic syllable counter for readability formulas."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    matches = re.findall(r'[aeiouy]{1,2}', word)
    return max(1, len(matches))
