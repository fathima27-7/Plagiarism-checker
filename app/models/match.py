from app.extensions import db

class PlagiarismMatch(db.Model):
    __tablename__ = 'plagiarism_matches'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False)
    source_document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True)
    source_title = db.Column(db.String(255), nullable=False)
    
    query_text = db.Column(db.Text, nullable=False)
    matched_text = db.Column(db.Text, nullable=False)
    similarity_percentage = db.Column(db.Float, default=0.0)
    
    start_char = db.Column(db.Integer, nullable=True)
    end_char = db.Column(db.Integer, nullable=True)
    sentence_index = db.Column(db.Integer, nullable=True)

    # Relationships
    analysis = db.relationship('AnalysisResult', back_populates='plagiarism_matches')
    source_document = db.relationship('Document', foreign_keys=[source_document_id])

    def to_dict(self):
        return {
            'id': self.id,
            'source_document_id': self.source_document_id,
            'source_title': self.source_title,
            'query_text': self.query_text,
            'matched_text': self.matched_text,
            'similarity_percentage': round(self.similarity_percentage, 1),
            'start_char': self.start_char,
            'end_char': self.end_char,
            'sentence_index': self.sentence_index
        }

