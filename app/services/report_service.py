from app.report_generator.generator import PDFReportGenerator

class ReportService:
    """
    Unified Report Service that delegates directly to PDFReportGenerator.
    Ensures a single source of truth across all application routes.
    """
    @staticmethod
    def generate_pdf(analysis, document, matches=None, ai_sentences=None, sections=None, suggestions=None):
        return PDFReportGenerator.generate_pdf(
            analysis=analysis,
            document=document,
            matches=matches,
            ai_sentences=ai_sentences,
            sections=sections,
            suggestions=suggestions
        )
