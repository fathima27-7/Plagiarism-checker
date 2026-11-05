from app.extensions import db

class SectionMetric(db.Model):
    __tablename__ = 'section_metrics'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False)
    
    section_name = db.Column(db.String(100), nullable=False)
    word_count = db.Column(db.Integer, default=0)
    plagiarism_score = db.Column(db.Float, default=0.0)
    ai_score = db.Column(db.Float, default=0.0)
    content_snippet = db.Column(db.Text, nullable=True)

    # Relationships
    analysis = db.relationship('AnalysisResult', back_populates='sections')

    def to_dict(self):
        return {
            'id': self.id,
            'section_name': self.section_name,
            'word_count': self.word_count,
            'plagiarism_score': round(self.plagiarism_score, 1),
            'ai_score': round(self.ai_score, 1),
            'content_snippet': self.content_snippet[:200] if self.content_snippet else ''
        }

