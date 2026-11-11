import unittest
from app.writing_quality import QualityAnalyzer, QualitySuggester

class TestWritingQuality(unittest.TestCase):
    def test_readability_metrics(self):
        text = "The experimental procedures were conducted in a sanitized environment. The samples were evaluated by the team."
        readability = QualityAnalyzer.analyze(text)
        self.assertGreater(readability['passive_voice_percentage'], 0.0)
        self.assertGreater(readability['flesch_reading_ease'], 0.0)
        self.assertGreater(readability['flesch_kincaid_grade'], 0.0)

    def test_suggestions_generator(self):
        data = {
            'plagiarism_score': 30.0,
            'ai_likelihood_score': 70.0,
            'readability': {'passive_voice_percentage': 40.0, 'long_sentences_count': 5},
            'citations': {'missing_references_count': 2, 'has_bibliography': True},
            'sections': [{'section_name': 'Introduction'}]
        }
        suggestions = QualitySuggester.generate_suggestions(data)
        self.assertGreater(len(suggestions), 0)

if __name__ == '__main__':
    unittest.main()

