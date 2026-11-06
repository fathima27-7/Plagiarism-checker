import os
from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    app.config.from_object(config_class)

    # Ensure required runtime directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REFERENCE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GENERATED_REPORTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CORPUS_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp
    from app.routes.history import history_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(reports_bp)

    # Initialize database tables and seed reference papers
    with app.app_context():
        import app.models as _models # Register all models
        db.create_all()
        seed_reference_corpus(app)

    return app

def seed_reference_corpus(app):
    """Indexes initial reference papers from reference_documents/ or corpus/ into SQLite."""
    from app.models.document import Document
    from app.document_processing import DocumentExtractor

    # Check primary reference_documents folder first, fallback to corpus folder
    candidate_folders = [
        app.config.get('REFERENCE_FOLDER'),
        app.config.get('CORPUS_FOLDER')
    ]

    for corpus_dir in candidate_folders:
        if not corpus_dir or not os.path.exists(corpus_dir):
            continue

        for filename in os.listdir(corpus_dir):
            if filename.endswith(('.txt', '.pdf', '.docx')):
                filepath = os.path.join(corpus_dir, filename)
                file_hash = DocumentExtractor.compute_sha256(filepath)
                
                existing = Document.query.filter_by(file_hash=file_hash).first()
                if not existing:
                    try:
                        ext = filename.rsplit('.', 1)[1].lower()
                        extracted = DocumentExtractor.extract_text(filepath, ext)
                        doc = Document(
                            filename=filename,
                            file_type=ext,
                            file_path=filepath,
                            file_hash=file_hash,
                            raw_text=extracted['clean_text'],
                            word_count=extracted['word_count'],
                            character_count=extracted['character_count'],
                            is_reference=True
                        )
                        db.session.add(doc)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(f"Failed to seed reference paper {filename}: {e}")
