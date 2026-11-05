# PlagiScan AI
**AI-Based Plagiarism Checker and Academic Content Analyzer**
*College of Computer Science & Engineering (CSE) Capstone / Mini-Project*

---

## 📌 Project Overview
**PlagiScan AI** is an academic content integrity and stylometric evaluation suite designed to assist students, educators, and researchers in auditing assignments, research drafts, and technical papers.

The system combines:
1. **Corpus-Based Plagiarism Detection**: Sublinear TF-IDF vectorization and Cosine Similarity calculation with granular sentence-level sliding window matching against the reference repository.
2. **AI-Generated Writing Likelihood Estimation**: Multi-signal stylometric evaluation evaluating token perplexity (Shannon entropy), sentence length burstiness variance, AI transitional markers, and syntax complexity. Flagged passages ($\ge 65\%$ likelihood) are highlighted in **Yellow**.
3. **Citation & Academic Structure Audit**: Validates in-text citations against the document's bibliography (supporting IEEE and APA formats) and isolates standard IMRAD sections.
4. **Readability & Style Profiling**: Computes Flesch Reading Ease, Flesch-Kincaid Grade Level, passive voice density, and provides context-aware smart improvement suggestions.
5. **Report Generation & Data Governance**: Automated compilation of printable evaluation certificates via ReportLab and full user data privacy controls (hard purge).

---

## 🚀 15 Main Features Implementation Matrix

| # | Feature | Implementation Details |
| :---: | :--- | :--- |
| **1** | **PDF, DOCX & TXT Uploads** | Multi-format extraction using PyMuPDF (`fitz`), `python-docx`, and UTF-8/Latin-1 decoders with SHA-256 deduplication. |
| **2** | **Plagiarism Detection** | Sublinear TF-IDF tokenization and Cosine Similarity cross-referenced with seed and uploaded reference corpus. |
| **3** | **AI Writing Likelihood Estimation** | Statistical ensemble evaluating vocabulary entropy (perplexity) and cadence uniformity (burstiness). |
| **4** | **Yellow Highlighting of AI Passages** | Suspected AI sentences ($\ge 65\%$ prob) are highlighted in yellow with interactive stylometric tooltips. |
| **5** | **Plagiarism Similarity Percentage** | Document-level similarity percentage computed as matching token coverage over total word count. |
| **6** | **AI Likelihood Percentage at Top** | Top hero card featuring overall statistical AI likelihood percentage with calibrated risk tier (Low, Moderate, High). |
| **7** | **Side-by-Side Document Comparison** | Dual-pane synchronized scrolling diff viewer with interactive sentence-to-sentence alignment. |
| **8** | **Citation & Reference Checker** | Audits in-text markers (`[1]`, `(Author, Year)`) against the bibliography, flagging orphan entries. |
| **9** | **Section-Wise Document Analysis** | Identifies Abstract, Intro, Methodology, Results, Conclusion, References with localized metrics. |
| **10** | **Grammar & Readability Analysis** | Computes Flesch Reading Ease, Flesch-Kincaid Grade Level, reading time, and passive voice density. |
| **11** | **Multiple Document Comparison** | Batch analysis computing an $N \times N$ symmetric pairwise similarity matrix with heatmap color-coding. |
| **12** | **Previous Analysis History** | Persistent SQLite history with full-text search, sorting by date/similarity/AI score, and pagination. |
| **13** | **Downloadable PDF Reports** | Professional evaluation certificates generated programmatically with ReportLab. |
| **14** | **Document Privacy & Deletion** | Complete cascade deletion: purges SQLite records and physically unlinks files from disk. |
| **15** | **Smart Improvement Suggestions** | Actionable recommendations for paraphrasing, diversifying syntax, fixing citations, and style. |

---

## 🛠️ Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **Backend**: Python 3.10+ / Python Flask 3.x
- **Database**: SQLite with SQLAlchemy ORM
- **Text Extraction**: PyMuPDF (`fitz`) for PDF, `python-docx` for Word, Native for TXT
- **Plagiarism & NLP**: Scikit-Learn (`TfidfVectorizer`, `cosine_similarity`), NumPy, custom regex tokenizers
- **PDF Report Generation**: ReportLab Platypus Engine
- **Data Visualization**: Chart.js (Bar charts, composition doughnut charts)

---

## 📂 Directory Structure

```
plagiscan_ai/
│
├── run.py                      # Application entry point
├── config.py                   # Global configuration & thresholds
├── requirements.txt            # Project dependencies
├── test_system.py              # Unit test suite
├── test_e2e_workflow.py        # End-to-end integration test
├── README.md                   # Project documentation
│
├── app/
│   ├── __init__.py             # Flask Application Factory & reference seeder
│   ├── extensions.py           # SQLAlchemy database instance
│   │
│   ├── models/                 # SQLite Database Models
│   │   ├── document.py         # Uploaded and reference document schema
│   │   ├── analysis.py         # Core analysis results & metrics
│   │   ├── match.py            # Granular plagiarism matches & offsets
│   │   ├── ai_sentence.py      # Sentence-level AI scores for yellow highlights
│   │   ├── section.py          # Section-wise breakdown scores
│   │   ├── citation.py         # In-text citation & bibliography records
│   │   └── suggestion.py       # Actionable academic suggestions
│   │
│   ├── routes/                 # Blueprint Handlers
│   │   ├── web.py              # HTML Views (Index, Analyze, Compare, Batch, History)
│   │   ├── api.py              # REST API (Upload, Analyze, Compare, Batch)
│   │   ├── history.py          # History query, search & privacy deletion
│   │   └── reports.py          # ReportLab PDF streaming
│   │
│   ├── services/               # Core Analytical Algorithms
│   │   ├── extractor_service.py    # PyMuPDF, python-docx, TXT parsers
│   │   ├── plagiarism_service.py   # TF-IDF, Cosine Similarity, Diff alignment
│   │   ├── ai_detector_service.py  # Perplexity, burstiness, stylometric scoring
│   │   ├── citation_service.py     # APA/IEEE regex auditor
│   │   ├── section_service.py      # Academic header segmenter
│   │   ├── readability_service.py  # Flesch-Kincaid & passive voice rules
│   │   ├── suggestion_service.py   # Contextual improvement advice
│   │   ├── report_service.py       # ReportLab PDF builder
│   │   └── nlp_utils.py            # Sentence segmentation & syllable counter
│   │
│   ├── templates/              # Jinja2 Templates (Bootstrap 5)
│   │   ├── base.html           # Master layout with navbar & footer
│   │   ├── index.html          # Upload dropzone & features overview
│   │   ├── analyze.html        # Main dashboard with yellow/red highlights
│   │   ├── compare.html        # Dual-pane synchronized scrolling diff
│   │   ├── batch.html          # Multi-document similarity matrix
│   │   └── history.html        # History table with search & privacy purge
│   │
│   └── static/                 # Static Assets
│       ├── css/
│       │   ├── main.css        # Typography, cards, layout
│       │   └── highlights.css  # Yellow (AI) & Red (Plagiarism) highlight styles
│       └── js/
│           ├── main.js         # Toasts & common helpers
│           ├── upload.js       # File dropzone & upload progress
│           ├── dashboard.js    # Chart.js & interactive highlighted text reader
│           ├── diff_viewer.js  # Dual synchronized scroll diff viewer
│           ├── batch.js        # Multi-document matrix generator
│           └── history.js      # History search, sort & deletion
│
├── corpus/
│   └── reference_papers/       # Seed academic reference papers
│
└── uploads/
    ├── documents/              # Stored uploaded files
    └── temp/                   # Temporary batch comparisons
```

---

## ⚡ Setup & Execution Instructions

### 1. Prerequisites
- Python 3.10+ (compatible with Python 3.11, 3.12, 3.13, and 3.14)
- Pip package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### 4. Running the Automated Tests
```bash
# Run unit test suite
python test_system.py

# Run end-to-end integration test
python test_e2e_workflow.py
```

---

## ⚖️ Academic Integrity Disclaimers
1. **Corpus Boundary**: Plagiarism detection is evaluated strictly against the accessible local reference corpus and peer documents uploaded to the system. External web checking requires commercial search API subscriptions.
2. **AI Detection Disclaimer**: AI detection is probabilistic and heuristic, measuring statistical markers such as predictability (perplexity) and sentence cadence variance (burstiness). Results represent an **estimate of likelihood**, not forensic proof of AI authorship.

