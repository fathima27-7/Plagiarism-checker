import unittest
from app.ai_engine import AIDetector

class TestAIEngine(unittest.TestCase):
    def test_ai_likelihood_detection(self):
        ai_sample = (
            "In conclusion, it is important to note that machine learning plays a crucial role in modern society. "
            "Furthermore, artificial intelligence fosters a sense of technological advancement across multiple sectors. "
            "Moreover, the system seamlessly integrates various algorithms to achieve predictable outcomes. "
            "Additionally, this serves as a testament to the power of computational algorithms in everyday tasks."
        )

        result = AIDetector.analyze_document(ai_sample, ai_flag_threshold=0.50)
        self.assertGreater(result['overall_ai_score'], 50.0)
        self.assertGreaterEqual(result['flagged_sentences_count'], 1)
        self.assertIn(result['ai_risk_level'], ['Moderate', 'High'])

if __name__ == '__main__':
    unittest.main()

