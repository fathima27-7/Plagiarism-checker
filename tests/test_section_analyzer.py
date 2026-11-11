import unittest
from app.section_analyzer import SectionAnalyzer

class TestSectionAnalyzer(unittest.TestCase):
    def test_section_segmentation(self):
        text = (
            "Title: Neural Network Analysis\n\n"
            "Abstract\nThis study evaluates model architectures.\n\n"
            "Introduction\nDeep learning represents a major branch of artificial intelligence.\n\n"
            "Methodology\nWe implemented a gradient descent optimization routine.\n\n"
            "Conclusion\nResults show high predictive power."
        )
        sections = SectionAnalyzer.parse_sections(text)
        sec_names = [s['section_name'] for s in sections]
        self.assertIn('Abstract', sec_names)
        self.assertIn('Introduction', sec_names)
        self.assertIn('Methodology', sec_names)
        self.assertIn('Conclusion', sec_names)

if __name__ == '__main__':
    unittest.main()

