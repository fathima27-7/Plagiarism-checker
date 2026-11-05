from app.extensions import db

class CitationItem(db.Model):
    __tablename__ = 'citation_items'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False)
    
    citation_text = db.Column(db.String(255), nullable=False)
    citation_type = db.Column(db.String(50), default='Generic')  # APA, IEEE, Numeric, Author-Date
    is_in_bibliography = db.Column(db.Boolean, default=True)     # Matched with references list
    position_index = db.Column(db.Integer, nullable=True)

    # Relationships
    analysis = db.relationship('AnalysisResult', back_populates='citations')

    def to_dict(self):
        return {
            'id': self.id,
            'citation_text': self.citation_text,
            'citation_type': self.citation_type,
            'is_in_bibliography': self.is_in_bibliography,
            'position_index': self.position_index
        }

