import os
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.document import Document
from app.models.analysis import AnalysisResult

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

@history_bp.route('', methods=['GET'])
def get_history():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')

    query = AnalysisResult.query.join(Document)

    if search_query:
        query = query.filter(Document.filename.ilike(f'%{search_query}%'))

    if sort_by == 'plagiarism':
        sort_col = AnalysisResult.plagiarism_score
    elif sort_by == 'ai':
        sort_col = AnalysisResult.ai_likelihood_score
    elif sort_by == 'filename':
        sort_col = Document.filename
    else:
        sort_col = AnalysisResult.created_at

    if order == 'asc':
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for a in paginated.items:
        data = a.to_dict()
        data['word_count'] = a.document.word_count if a.document else 0
        data['file_type'] = a.document.file_type if a.document else ''
        results.append(data)

    return jsonify({
        'items': results,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }), 200

@history_bp.route('/document/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """
    Privacy and deletion endpoint (Feature 14).
    Completely purges document, cascades DB records, and physically deletes the file.
    """
    doc = Document.query.get_or_404(doc_id)

    # 1. Unlink physical file from disk if present
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass # Continue even if file already removed

    # 2. Delete document record (SQLAlchemy cascades all AnalysisResults, Matches, etc.)
    db.session.delete(doc)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Document "{doc.filename}" and all associated analysis records were permanently deleted.'
    }), 200

@history_bp.route('/analysis/<int:analysis_id>', methods=['DELETE'])
def delete_single_analysis(analysis_id):
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    doc_id = analysis.document_id

    db.session.delete(analysis)
    db.session.commit()

    # If document has no other analyses and is not a reference paper, optionally clean up
    remaining = AnalysisResult.query.filter_by(document_id=doc_id).count()
    return jsonify({
        'success': True,
        'message': f'Analysis record #{analysis_id} deleted successfully.',
        'remaining_for_doc': remaining
    }), 200

