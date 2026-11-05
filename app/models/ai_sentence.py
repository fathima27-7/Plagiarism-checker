from app.extensions import db

class AISentenceScore(db.Model):
    __tablename__ = 'ai_sentence_scores'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False)
    
    sentence_index = db.Column(db.Integer, nullable=False)
    sentence_text = db.Column(db.Text, nullable=False)
    
    perplexity_score = db.Column(db.Float, default=0.0)
    burstiness_score = db.Column(db.Float, default=0.0)
    ai_probability = db.Column(db.Float, default=0.0)      # 0.0 to 1.0
    is_flagged = db.Column(db.Boolean, default=False)      # Highlighted in yellow if True
    
    start_char = db.Column(db.Integer, nullable=True)
    end_char = db.Column(db.Integer, nullable=True)

    # Relationships
    analysis = db.relationship('AnalysisResult', back_populates='ai_sentences')

    def to_dict(self):
        return {
            'id': self.id,
            'sentence_index': self.sentence_index,
            'sentence_text': self.sentence_text,
            'perplexity_score': round(self.perplexity_score, 2),
            'burstiness_score': round(self.burstiness_score, 2),
            'ai_probability': round(self.ai_probability * 100, 1),
            'is_flagged': self.is_flagged,
            'start_char': self.start_char,
            'end_char': self.end_char
        }

