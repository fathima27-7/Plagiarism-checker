import unittest
from app.citation_checker import CitationChecker

class TestCitationChecker(unittest.TestCase):
    def test_citation_auditing(self):
        academic_text = (
            "Attention mechanisms have revolutionized natural language processing (Vaswani et al., 2017). "
            "Another approach was proposed in [1].\n\n"
            "References\n"
            "[1] A. Vaswani et al., Attention is all you need, NeurIPS, 2017.\n"
            "[2] J. Devlin et al., BERT representations, NAACL, 2018."
        )

        audit = CitationChecker.audit_citations(academic_text)
        self.assertGreaterEqual(audit['total_citations'], 2)
        self.assertEqual(audit['references_count'], 2)
        self.assertTrue(audit['has_bibliography'])

if __name__ == '__main__':
    unittest.main()
