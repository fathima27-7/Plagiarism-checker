from flask import Blueprint, send_file, abort
from app.models.analysis import AnalysisResult
from app.report_generator import PDFReportGenerator

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/download/<int:analysis_id>', methods=['GET'])
def download_pdf_report(analysis_id):
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    doc = analysis.document
    if not doc:
        abort(404, description="Associated document not found.")

    matches = analysis.plagiarism_matches
    ai_sentences = analysis.ai_sentences
    sections = analysis.sections
    suggestions = analysis.suggestions

    pdf_buffer = PDFReportGenerator.generate_pdf(
        analysis=analysis,
        document=doc,
        matches=matches,
        ai_sentences=ai_sentences,
        sections=sections,
        suggestions=suggestions
    )

    clean_filename = doc.filename.rsplit('.', 1)[0]
    download_name = f"PlagiScan_Report_{clean_filename}_{analysis.id}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=download_name
    )

