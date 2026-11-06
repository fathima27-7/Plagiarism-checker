# PlagiScan AI – AI-Based Plagiarism Checker and Academic Content Analyzer

---

## 📌 Project Architecture Overview

**PlagiScan AI** is an academic content integrity and stylometric evaluation suite designed to assist students, educators, and researchers in auditing assignments, research drafts, and technical papers.

The application follows a **Modular Clean Architecture** separating business logic into specialized engines and packages:
1. **Document Processing Engine**: Structured text extraction from PDF, Word (DOCX), and TXT formats with SHA-256 deduplication.
2. **Plagiarism Detection Engine**: Sublinear TF-IDF vectorization and Cosine Similarity calculation with granular sentence-level sliding-window matching against local reference papers.
3. **AI Likelihood Estimation Engine**: Interpretable multi-signal statistical evaluation of Shannon entropy (Perplexity), sentence length variance (Burstiness), and transitional buzzword density. Sentences exceeding the threshold ($\ge 65\%$) are highlighted in **Yellow**.
4. **Citation & Reference Auditor**: Regex-based cross-referencing of IEEE numeric `[1]` and APA parenthetical `(Author, Year)` citations against bibliography headers.
5. **Writing Quality & Readability Analyzer**: Flesch Reading Ease, Flesch-Kincaid Grade Level, reading time, passive voice density, and smart contextual improvement suggestions.
6. **Section Analyzer**: Automatic segmentation of academic papers into standard IMRAD headers (Abstract, Introduction, Methodology, Results, Conclusion, References) with localized scoring.
7. **Reporting & Privacy**: Multi-page PDF report generation via ReportLab Platypus and a complete cascade data purge for user privacy.

---

## 📁 Complete Folder Structure & File Manifest

```
plagiscan_ai/
│
├── app.py                             # Primary Flask application runner and entry point
├── config.py                          # Global configuration, threshold settings & storage paths
├── requirements.txt                   # Production Python package dependencies
├── README.md                          # Comprehensive architectural documentation & manifest
├── .env.example                       # Environment variables configuration template
├── plagiscan.db                       # SQLite relational database storage
│
├── app/                               # Core Flask Application Package
│   ├── __init__.py                    # Flask App Factory (create_app) & corpus seeder
│   ├── extensions.py                  # Shared SQLAlchemy database instance
│   │
│   ├── document_processing/           # Folder 5: Document Ingestion & Extraction Engine
│   │   ├── __init__.py                # Module initializer exporting DocumentExtractor
│   │   └── extractor.py               # PyMuPDF (fitz), python-docx, TXT decoders & SHA-256 hasher
│   │
│   ├── plagiarism_engine/             # Folder 6: Plagiarism Detection Engine
│   │   ├── __init__.py                # Module initializer exporting PlagiarismDetector
│   │   └── detector.py                # TF-IDF, Cosine Similarity, sliding window diff & matrix
│   │
│   ├── ai_engine/                     # Folder 7: AI Detection Engine
│   │   ├── __init__.py                # Module initializer exporting AIDetector
│   │   └── detector.py                # Perplexity, burstiness, stylometrics & logistic probability
│   │
│   ├── citation_checker/              # Folder 8: Citation & Reference Checker
│   │   ├── __init__.py                # Module initializer exporting CitationChecker
│   │   └── checker.py                 # IEEE & APA regex parser, bibliography section auditor
│   │
│   ├── writing_quality/               # Folder 9: Writing Quality & Readability Analyzer
│   │   ├── __init__.py                # Module initializer exporting QualityAnalyzer & Suggester
│   │   ├── readability.py             # Flesch-Kincaid, Flesch Reading Ease & passive voice rules
│   │   └── suggestions.py             # Rule-based academic writing improvement generator
│   │
│   ├── section_analyzer/              # Folder 10: Academic Section Analyzer
│   │   ├── __init__.py                # Module initializer exporting SectionAnalyzer
│   │   └── analyzer.py                # IMRAD section segmenter & section-wise score calculator
│   │
│   ├── report_generator/              # Folder 16: PDF Report Generator Module
│   │   ├── __init__.py                # Module initializer exporting PDFReportGenerator
│   │   └── generator.py               # ReportLab Platypus multi-page PDF evaluation certificate builder
│   │
│   ├── models/                        # Folder 11: SQLAlchemy Database Models
│   │   ├── __init__.py                # Exports Document, AnalysisResult, PlagiarismMatch, etc.
│   │   ├── document.py                # Document model (metadata, file hash, word count)
│   │   ├── analysis.py                # AnalysisResult model (executive percentages & scores)
│   │   ├── match.py                   # PlagiarismMatch model (snippet offsets & source titles)
│   │   ├── ai_sentence.py             # AISentenceScore model (per-sentence AI probs & yellow flags)
│   │   ├── section.py                 # SectionMetric model (per-section word counts & scores)
│   │   ├── citation.py                # CitationItem model (in-text vs bibliography match status)
│   │   └── suggestion.py              # SmartSuggestion model (categorized action items)
│   │
│   ├── utils/                         # Folder 12: Utility Functions
│   │   ├── __init__.py                # Exports sentence splitter and syllable counter
│   │   └── nlp_utils.py               # Regex sentence boundary protector, syllable counter, stopwords
│   │
│   ├── ml_models/                     # Folder 13: Machine Learning Models
│   │   ├── __init__.py                # Exports MLModelRegistry
│   │   └── model_loader.py            # Model registry, loader and serialization utilities
│   │
│   ├── routes/                        # Folder 4: API & Web Routes (Flask Blueprints)
│   │   ├── __init__.py                # Blueprint registration exports
│   │   ├── web.py                     # HTML UI views (Index, Analyze, Compare, Batch, History)
│   │   ├── api.py                     # REST endpoints (/upload, /analyze, /compare, /batch-compare)
│   │   ├── history.py                 # History query, search, sorting & privacy hard-delete
│   │   └── reports.py                 # PDF streaming endpoint (/reports/download/<id>)
│   │
│   ├── templates/                     # Folder 1: Frontend Jinja2 HTML Templates
│   │   ├── base.html                  # Global layout with navigation, brand banner & footer
│   │   ├── index.html                 # Landing page with drag-and-drop dropzone & feature cards
│   │   ├── analyze.html               # Main report dashboard with yellow AI & red plag highlights
│   │   ├── compare.html               # Dual-pane side-by-side synchronized scrolling diff viewer
│   │   ├── batch.html                 # Multiple document batch matrix & heatmap viewer
│   │   └── history.html               # Searchable, paginated history table with privacy modal
│   │
│   └── static/                        # Folder 2: CSS and JavaScript Assets
│       ├── css/
│       │   ├── main.css               # Typography, modern card elevation, and layout styles
│       │   └── highlights.css         # Yellow (AI), Red (Plag), and Peach highlight CSS classes
│       └── js/
│           ├── main.js                # Toast notifications and common UI utilities
│           ├── upload.js              # File dropzone, progress bar & scan execution
│           ├── dashboard.js           # Chart.js charts, toggleable highlight filters & sentence inspector
│           ├── diff_viewer.js         # Synchronized dual-pane scrolling and click-to-match alignment
│           ├── batch.js               # Multi-file batch matrix calculation & heatmap renderer
│           └── history.js             # History API fetch, live search, sorting & privacy purge
│
├── uploads/                           # Folder 14: Uploaded Documents Storage
│   ├── documents/                     # Permanent user-uploaded documents
│   └── temp/                          # Transient files for batch comparison
│
├── reference_documents/               # Folder 15: Reference Documents Repository
│   ├── paper1_machine_learning_ethics.txt       # Benchmark paper on AI ethics & bias mitigation
│   ├── paper2_deep_learning_nlp.txt             # Benchmark paper on Transformer self-attention
│   └── paper3_cloud_computing_security.txt      # Benchmark paper on Zero-Trust cloud architectures
│
├── generated_reports/                 # Folder 16: Generated PDF Reports Output Directory
│   └── .gitkeep                       # Directory retention marker
│
└── tests/                             # Folder 17: Comprehensive Unit & Integration Tests
    ├── __init__.py                    # Test suite package marker
    ├── test_document_processing.py    # Unit tests for PyMuPDF, python-docx & SHA-256
    ├── test_plagiarism_engine.py      # Unit tests for TF-IDF, Cosine Similarity & Diff alignment
    ├── test_ai_engine.py              # Unit tests for Perplexity, Burstiness & AI flagging
    ├── test_citation_checker.py       # Unit tests for IEEE/APA regex & bibliography validation
    ├── test_writing_quality.py        # Unit tests for Flesch-Kincaid & suggestion generator
    ├── test_section_analyzer.py       # Unit tests for IMRAD academic section segmentation
    ├── test_api_endpoints.py          # Unit tests for REST API endpoints & HTTP status codes
    └── test_e2e.py                    # End-to-end integration test (Upload -> Analyze -> PDF -> Delete)
```

---

## 📖 Detailed Explanation of Every Folder and File

### Root Configuration & Entry Points
- **`app.py`**: The primary server entry point. Reads runtime environment variables (`HOST`, `PORT`, `FLASK_DEBUG`) and starts the local WSGI development server.
- **`config.py`**: Centralized configuration class setting SQLite database URI, upload limits (16 MB), allowed file extensions, and analytical thresholds (`PLAGIARISM_MATCH_THRESHOLD = 0.55`, `AI_FLAG_THRESHOLD = 0.65`).
- **`requirements.txt`**: Declares verified dependencies (`Flask`, `Flask-SQLAlchemy`, `PyMuPDF`, `python-docx`, `scikit-learn`, `numpy`, `scipy`, `nltk`, `reportlab`, `textstat`).
- **`.env.example`**: Documentation template for environment variables used in staging and production deployments.
- **`README.md`**: Complete architectural guide, directory manifest, and setup instructions.

### 1. Frontend Templates (`app/templates/`)
- **`base.html`**: Master layout providing the responsive Bootstrap 5 navbar, active navigation highlights, footer with academic disclaimers, and toast notification containers.
- **`index.html`**: The home page with multi-format drag-and-drop dropzone, direct text-paste option, reference corpus counter, and dynamic progress bar.
- **`analyze.html`**: The central interactive analysis report. Displays hero metric badges at the top, Chart.js section radar/bar charts, and the full document text with yellow and red marks.
- **`compare.html`**: Dual-pane side-by-side comparison screen allowing users to pick two documents and view aligned sentences.
- **`batch.html`**: Multi-document comparison interface with interactive $N \times N$ similarity matrix and color heatmap cells.
- **`history.html`**: Paginated history table with live debounced search, sorting dropdown, and a privacy confirmation modal.

### 2. CSS and JavaScript (`app/static/`)
- **`css/main.css`**: Professional slate/indigo theme typography, modern card drop shadows, metric cards, and responsive container layout.
- **`css/highlights.css`**: Specific annotation styling: `.ai-highlight` (pastel yellow with dark amber border), `.plag-highlight` (soft red with crimson border), and `.both-highlight` (peach).
- **`js/main.js`**: Reusable toast notification triggers and bootstrap tooltips.
- **`js/upload.js`**: Handles drag-and-drop events, file size formatting, simulated progress stages, and multipart API submissions.
- **`js/dashboard.js`**: Chart.js initialization, highlight toggles, and click-to-inspect sentence modal card.
- **`js/diff_viewer.js`**: Dual-pane synchronized scrolling handler with cross-pane click-to-match scrolling.
- **`js/batch.js`**: Multi-file batch selection, FormData submission, and matrix heatmap table generation.
- **`js/history.js`**: Paginated history querying, search filtering, and privacy hard-deletion requests.

### 3. Flask Backend Core (`app/`)
- **`app/__init__.py`**: Flask Application Factory (`create_app`). Binds configurations, registers Blueprints, ensures runtime directories exist, initializes SQLite tables, and automatically indexes reference papers into the database.
- **`app/extensions.py`**: Initializes the global `db = SQLAlchemy()` object without attaching it to a specific application instance, preventing circular dependencies.

### 4. API Routes (`app/routes/`)
- **`routes/web.py`**: HTML view routes serving rendered templates (`/`, `/analyze/<id>`, `/compare`, `/batch`, `/history`).
- **`routes/api.py`**: Core RESTful JSON API endpoints:
  - `POST /api/upload`: Handles file upload, text extraction, and SHA-256 hashing.
  - `POST /api/analyze`: Runs analytical engines and returns consolidated JSON.
  - `POST /api/compare`: Runs pairwise sentence alignment between two documents.
  - `POST /api/batch-compare`: Computes symmetric pairwise matrix across uploaded files.
  - `GET /api/analyses/<id>`: Fetches historical analysis JSON.
- **`routes/history.py`**:
  - `GET /api/history`: Returns paginated, searchable, sortable analysis records.
  - `DELETE /api/history/document/<id>`: Executes complete privacy purge (cascades database rows and removes physical file from disk).
- **`routes/reports.py`**:
  - `GET /reports/download/<id>`: Builds and streams the ReportLab PDF evaluation report as an attachment.

### 5. Document Processing (`app/document_processing/`)
- **`extractor.py`**: High-performance extraction engine using PyMuPDF (`fitz`) for PDF documents, `python-docx` for Word XML files, and multi-encoding fallbacks for plain text. Normalizes whitespace, quotes, and punctuation while computing SHA-256 hashes.

### 6. Plagiarism Detection Engine (`app/plagiarism_engine/`)
- **`detector.py`**: Computes sublinear TF-IDF matrices across all reference documents and target submissions. Calculates global Cosine Similarity and performs fine-grained sentence-level matching to extract character offsets `[start_char, end_char]` for UI annotation. Also computes $N \times N$ batch comparison matrices.

### 7. AI Detection Engine (`app/ai_engine/`)
- **`detector.py`**: Evaluates sentence-level Shannon entropy (perplexity), sentence length variance (burstiness), transitional marker density, and punctuation complexity. Sentences with probability $\ge 0.65$ are marked for **Yellow Highlighting**.

### 8. Citation Checker (`app/citation_checker/`)
- **`checker.py`**: Regex-based citation parser supporting IEEE numeric (`[1]`, `[1-3]`) and APA author-year (`(Smith, 2021)`, `According to Miller (2020)`) styles. Extracts bibliography entries and cross-references them to detect unreferenced or orphan citations.

### 9. Writing Quality Analyzer (`app/writing_quality/`)
- **`readability.py`**: Computes Flesch Reading Ease, Flesch-Kincaid Grade Level, reading time, Type-Token Ratio (lexical diversity), and passive voice density.
- **`suggestions.py`**: Contextual suggestion generator offering advice on paraphrasing high-similarity spans, varying sentence rhythm for AI-flagged sections, fixing citation discrepancies, and reducing passive constructions.

### 10. Section Analyzer (`app/section_analyzer/`)
- **`analyzer.py`**: Heuristic parser identifying academic headers (Abstract, Introduction, Literature Review, Methodology, Results, Conclusion, References). Evaluates localized word counts, section-level plagiarism percentages, and section-level AI likelihood scores.

### 11. Database Models (`app/models/`)
- **`document.py`**: `Document` model tracking file metadata, path, hash, word count, and reference status.
- **`analysis.py`**: `AnalysisResult` model storing overall percentages, readability indices, and foreign keys.
- **`match.py`**: `PlagiarismMatch` model storing matched text snippets and character start/end offsets.
- **`ai_sentence.py`**: `AISentenceScore` model storing sentence-level perplexity, burstiness, and yellow highlight flags.
- **`section.py`**: `SectionMetric` model storing section names and localized scores.
- **`citation.py`**: `CitationItem` model storing detected citation markers and match statuses.
- **`suggestion.py`**: `SmartSuggestion` model storing categorized academic recommendations.

### 12. Utility Functions (`app/utils/`)
- **`nlp_utils.py`**: Abbreviation-protected sentence boundary splitter (preventing false splits on "et al.", "e.g.", "Dr.", "pp."), heuristic syllable counter, and offline stopword dictionary.

### 13. Machine Learning Models (`app/ml_models/`)
- **`model_loader.py`**: Model registry managing serialization, caching, and loading of scikit-learn models and TF-IDF vectorizers.

### 14. Uploaded Documents (`uploads/`)
- **`uploads/documents/`**: Storage for uploaded student files.
- **`uploads/temp/`**: Temporary storage for one-off batch comparisons.

### 15. Reference Documents (`reference_documents/`)
- Seed academic papers automatically indexed into SQLite on application startup:
  - `paper1_machine_learning_ethics.txt`
  - `paper2_deep_learning_nlp.txt`
  - `paper3_cloud_computing_security.txt`

### 16. Generated Reports (`generated_reports/` & `app/report_generator/`)
- **`app/report_generator/generator.py`**: Programmatically generates multi-page PDF evaluation reports using ReportLab Platypus with metadata tables, score badges, section tables, citation summaries, and annotated text appendices.
- **`generated_reports/`**: Destination directory for saved PDF reports.

### 17. Unit Tests (`tests/`)
- **`test_document_processing.py`**: Validates file extraction, paragraph splitting, and SHA-256 generation.
- **`test_plagiarism_engine.py`**: Tests TF-IDF similarity calculation and sentence-level matching.
- **`test_ai_engine.py`**: Tests perplexity, burstiness, and sentence flagging.
- **`test_citation_checker.py`**: Tests APA/IEEE citation identification and bibliography validation.
- **`test_writing_quality.py`**: Tests readability formulas and rule-based suggestions.
- **`test_section_analyzer.py`**: Tests academic section boundary segmentation.
- **`test_api_endpoints.py`**: Tests RESTful endpoints (`/`, `/compare`, `/batch`, `/api/history`).
- **`test_e2e.py`**: Tests complete user lifecycle (upload $\to$ analyze $\to$ diff $\to$ PDF report $\to$ privacy hard delete).

---

## ⚡ Execution Instructions

### Run the Application Server
```powershell
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

### Run All Unit & Integration Tests
```powershell
python -m unittest discover tests
```
