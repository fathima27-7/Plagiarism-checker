from app.extensions import db

class SmartSuggestion(db.Model):
    __tablename__ = 'smart_suggestions'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False)
    
    category = db.Column(db.String(50), nullable=False)    # Readability, Style, Citation, Structure
    severity = db.Column(db.String(20), default='info')     # info, warning, high
    title = db.Column(db.String(200), nullable=False)
    suggestion_text = db.Column(db.Text, nullable=False)
    example_text = db.Column(db.Text, nullable=True)

    # Relationships
    analysis = db.relationship('AnalysisResult', back_populates='suggestions')

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'severity': self.severity,
            'title': self.title,
            'suggestion_text': self.suggestion_text,
            'example_text': self.example_text
        }

