"""
Bridge module ensuring backwards compatibility with app.services imports.
Maps directly to the dedicated engine folders.
"""
from app.document_processing.extractor import DocumentExtractor as ExtractorService
from app.plagiarism_engine.detector import PlagiarismDetector as PlagiarismService
from app.ai_engine.detector import AIDetector as AIDetectorService
from app.citation_checker.checker import CitationChecker as CitationService
from app.section_analyzer.analyzer import SectionAnalyzer as SectionService
from app.writing_quality.readability import QualityAnalyzer as ReadabilityService
from app.writing_quality.suggestions import QualitySuggester as SuggestionService
from app.report_generator.generator import PDFReportGenerator as ReportService

__all__ = [
    'ExtractorService',
    'PlagiarismService',
    'AIDetectorService',
    'CitationService',
    'SectionService',
    'ReadabilityService',
    'SuggestionService',
    'ReportService'
]
