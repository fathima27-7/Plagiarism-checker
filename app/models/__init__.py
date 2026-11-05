from app.models.document import Document
from app.models.analysis import AnalysisResult
from app.models.match import PlagiarismMatch
from app.models.ai_sentence import AISentenceScore
from app.models.section import SectionMetric
from app.models.citation import CitationItem
from app.models.suggestion import SmartSuggestion

__all__ = [
    'Document',
    'AnalysisResult',
    'PlagiarismMatch',
    'AISentenceScore',
    'SectionMetric',
    'CitationItem',
    'SmartSuggestion'
]

