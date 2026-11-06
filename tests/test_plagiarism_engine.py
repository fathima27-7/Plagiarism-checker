import unittest
from app import create_app
from app.models.document import Document
from app.plagiarism_engine import PlagiarismDetector

class TestPlagiarismEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()

    def test_plagiarism_detection_and_matching(self):
        with self.app.app_context():
            ref_docs = Document.query.filter_by(is_reference=True).all()
            
            # Query copied sentence from paper 1
            query_doc = Document(
                id=9999,
                filename="test_query.txt",
                raw_text="The widespread deployment of machine learning algorithms in critical societal domains has necessitated rigorous examination of algorithmic bias and unfairness. Machine learning models trained on historical data frequently perpetuate and amplify systemic inequities.",
                word_count=32
            )

            result = PlagiarismDetector.analyze_document(query_doc, ref_docs)
            self.assertGreater(result['overall_score'], 50.0)
            self.assertGreater(len(result['matches']), 0)
            self.assertIn('top_sources', result)

    def test_compare_two_documents(self):
        doc1 = "Attention mechanisms have revolutionized natural language processing and computer vision."
        doc2 = "Attention mechanisms have revolutionized natural language processing in computational linguistics."
        diff = PlagiarismDetector.compare_two_documents(doc1, doc2)
        self.assertGreater(diff['overall_similarity'], 40.0)
        self.assertEqual(len(diff['doc1_sentences']), 1)

if __name__ == '__main__':
    unittest.main()
