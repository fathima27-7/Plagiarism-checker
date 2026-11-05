from datetime import datetime, timezone
from app.extensions import db

def get_utc_now():
    return datetime.now(timezone.utc)

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    
    # Executive percentages & metrics
    plagiarism_score = db.Column(db.Float, default=0.0)      # 0 to 100%
    ai_likelihood_score = db.Column(db.Float, default=0.0)   # 0 to 100%
    ai_risk_level = db.Column(db.String(20), default='Low')  # Low, Moderate, High
    
    # Readability metrics
    flesch_reading_ease = db.Column(db.Float, default=0.0)
    flesch_kincaid_grade = db.Column(db.Float, default=0.0)
    reading_time_minutes = db.Column(db.Float, default=0.0)
    lexical_diversity = db.Column(db.Float, default=0.0)     # Type-Token Ratio
    
    # Analysis metadata
    sentence_count = db.Column(db.Integer, default=0)
    citation_count = db.Column(db.Integer, default=0)
    uncited_sources_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='completed')   # processing, completed, failed
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    document = db.relationship('Document', back_populates='analyses')
    plagiarism_matches = db.relationship('PlagiarismMatch', back_populates='analysis', cascade='all, delete-orphan')
    ai_sentences = db.relationship('AISentenceScore', back_populates='analysis', cascade='all, delete-orphan')
    sections = db.relationship('SectionMetric', back_populates='analysis', cascade='all, delete-orphan')
    citations = db.relationship('CitationItem', back_populates='analysis', cascade='all, delete-orphan')
    suggestions = db.relationship('SmartSuggestion', back_populates='analysis', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'filename': self.document.filename if self.document else '',
            'plagiarism_score': round(self.plagiarism_score, 1),
            'ai_likelihood_score': round(self.ai_likelihood_score, 1),
            'ai_risk_level': self.ai_risk_level,
            'flesch_reading_ease': round(self.flesch_reading_ease, 1),
            'flesch_kincaid_grade': round(self.flesch_kincaid_grade, 1),
            'reading_time_minutes': round(self.reading_time_minutes, 1),
            'lexical_diversity': round(self.lexical_diversity, 2),
            'sentence_count': self.sentence_count,
            'citation_count': self.citation_count,
            'uncited_sources_count': self.uncited_sources_count,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
