import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'plagiscan-ai-secret-key-cse-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'plagiscan.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Storage and folder paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'documents')
    TEMP_FOLDER = os.path.join(BASE_DIR, 'uploads', 'temp')
    REFERENCE_FOLDER = os.path.join(BASE_DIR, 'reference_documents')
    GENERATED_REPORTS_FOLDER = os.path.join(BASE_DIR, 'generated_reports')
    CORPUS_FOLDER = os.path.join(BASE_DIR, 'corpus', 'reference_papers')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    # Analysis thresholds
    PLAGIARISM_MATCH_THRESHOLD = 0.55  # Sentence similarity threshold (Cosine >= 0.55)
    AI_FLAG_THRESHOLD = 0.65           # Sentence AI probability threshold
