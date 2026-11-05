from datetime import datetime, timezone
from app.extensions import db

def get_utc_now():
    return datetime.now(timezone.utc)

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx, txt
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), nullable=True)   # SHA-256
    raw_text = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    character_count = db.Column(db.Integer, default=0)
    is_reference = db.Column(db.Boolean, default=False)   # True if belongs to reference corpus
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    analyses = db.relationship('AnalysisResult', back_populates='document', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'is_reference': self.is_reference,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
