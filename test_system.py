import os
import unittest
from app import create_app
from app.extensions import db
from app.models.document import Document
from app.models.analysis import AnalysisResult
from app.services.extractor_service import ExtractorService
from app.services.plagiarism_service import PlagiarismService
from app.services.ai_detector_service import AIDetectorService
from app.services.citation_service import CitationService
from app.services.readability_service import ReadabilityService
from app.services.section_service import SectionService
from app.services.suggestion_service import SuggestionService
from app.services.report_service import ReportService

class TestPlagiScanSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_01_reference_seeding(self):
        """Verify that seed reference corpus papers are in SQLite."""
        with self.app.app_context():
            refs = Document.query.filter_by(is_reference=True).all()
            print(f"[TEST 1] Indexed Reference Papers: {len(refs)}")
            self.assertGreaterEqual(len(refs), 3)

    def test_02_plagiarism_engine(self):
        """Verify TF-IDF and Cosine similarity detection."""
        with self.app.app_context():
            ref_docs = Document.query.filter_by(is_reference=True).all()
            
            # Query containing exact copied sentence from paper 1
            query_doc = Document(
                id=9999,
                filename="test_query.txt",
                raw_text="The widespread deployment of machine learning algorithms in critical societal domains has necessitated rigorous examination of algorithmic bias and unfairness. Machine learning models trained on historical data frequently perpetuate and amplify systemic inequities.",
                word_count=32
            )

            result = PlagiarismService.analyze_document(query_doc, ref_docs)
            print(f"[TEST 2] Plagiarism Score: {result['overall_score']}%, Matches: {len(result['matches'])}")
            self.assertGreater(result['overall_score'], 50.0)
            self.assertGreater(len(result['matches']), 0)

    def test_03_ai_detection_engine(self):
        """Verify AI Likelihood estimation, perplexity, burstiness, and flagging."""
        # Simulated repetitive LLM style text
        ai_sample = (
            "In conclusion, it is important to note that machine learning plays a crucial role in modern society. "
            "Furthermore, artificial intelligence fosters a sense of technological advancement across multiple sectors. "
            "Moreover, the system seamlessly integrates various algorithms to achieve predictable outcomes. "
            "Additionally, this serves as a testament to the power of computational algorithms in everyday tasks."
        )

        result = AIDetectorService.analyze_document(ai_sample, ai_flag_threshold=0.50)
        print(f"[TEST 3] AI Likelihood Score: {result['overall_ai_score']}%, Risk: {result['ai_risk_level']}, Flagged: {result['flagged_sentences_count']}")
        self.assertGreater(result['overall_ai_score'], 50.0)
        self.assertGreaterEqual(result['flagged_sentences_count'], 1)

    def test_04_citation_checker(self):
        """Verify citation auditing against references section."""
        academic_text = (
            "Attention mechanisms have revolutionized natural language processing (Vaswani et al., 2017). "
            "Deep contextual embeddings were later introduced by Devlin et al. (2018). "
            "Another approach was proposed in [1].\n\n"
            "References\n"
            "[1] A. Vaswani et al., Attention is all you need, NeurIPS, 2017.\n"
            "[2] J. Devlin et al., BERT representations, NAACL, 2018."
        )

        audit = CitationService.audit_citations(academic_text)
        print(f"[TEST 4] Citations: {audit['total_citations']}, References: {audit['references_count']}, Format: {audit['citation_format']}")
        self.assertGreaterEqual(audit['total_citations'], 2)
        self.assertEqual(audit['references_count'], 2)

    def test_05_readability_metrics(self):
        """Verify Flesch-Kincaid grade level and passive voice calculations."""
        text = "The experimental procedures were conducted in a sanitized environment. The samples were evaluated by the team."
        readability = ReadabilityService.analyze(text)
        print(f"[TEST 5] Reading Ease: {readability['flesch_reading_ease']}, Grade: {readability['flesch_kincaid_grade']}, Passive: {readability['passive_voice_percentage']}%")
        self.assertGreater(readability['passive_voice_percentage'], 0.0)

    def test_06_pdf_report_generation(self):
        """Verify ReportLab PDF generation."""
        with self.app.app_context():
            doc = Document(filename="sample_test.pdf", word_count=500, file_type="pdf")
            analysis = AnalysisResult(
                id=1,
                plagiarism_score=14.5,
                ai_likelihood_score=38.0,
                ai_risk_level="Moderate",
                flesch_reading_ease=52.4,
                flesch_kincaid_grade=13.2,
                reading_time_minutes=2.5,
                lexical_diversity=0.64,
                sentence_count=22,
                citation_count=5,
                uncited_sources_count=0
            )
            buffer = ReportService.generate_pdf(analysis, doc)
            pdf_bytes = buffer.getvalue()
            print(f"[TEST 6] Generated PDF size: {len(pdf_bytes)} bytes")
            self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_07_api_endpoints(self):
        """Test Flask client endpoints."""
        # Test web index
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        # Test compare view
        res = self.client.get('/compare')
        self.assertEqual(res.status_code, 200)

        # Test batch view
        res = self.client.get('/batch')
        self.assertEqual(res.status_code, 200)

        # Test history API
        res = self.client.get('/api/history')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn('items', json_data)
        print(f"[TEST 7] API History endpoint verified. Total historical items: {json_data['total']}")

if __name__ == '__main__':
    unittest.main()
