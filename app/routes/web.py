from flask import Blueprint, render_template, abort
from app.models.document import Document
from app.models.analysis import AnalysisResult

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    recent_analyses = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).limit(5).all()
    total_analyzed = AnalysisResult.query.count()
    reference_count = Document.query.filter_by(is_reference=True).count()
    return render_template(
        'index.html',
        recent_analyses=recent_analyses,
        total_analyzed=total_analyzed,
        reference_count=reference_count
    )

@web_bp.route('/analyze/<int:analysis_id>')
def analyze_view(analysis_id):
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    doc = analysis.document
    return render_template(
        'analyze.html',
        analysis=analysis,
        document=doc,
        matches=analysis.plagiarism_matches,
        ai_sentences=analysis.ai_sentences,
        sections=analysis.sections,
        citations=analysis.citations,
        suggestions=analysis.suggestions
    )

@web_bp.route('/compare')
def compare_view():
    all_docs = Document.query.order_by(Document.filename.asc()).all()
    return render_template('compare.html', documents=all_docs)

@web_bp.route('/batch')
def batch_view():
    return render_template('batch.html')

@web_bp.route('/history')
def history_view():
    return render_template('history.html')

