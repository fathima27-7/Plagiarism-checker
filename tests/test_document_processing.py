import unittest
import tempfile
import os
from app.document_processing import DocumentExtractor

class TestDocumentProcessing(unittest.TestCase):
    def test_txt_extraction_and_hash(self):
        sample_content = "This is a sample research paragraph.\n\nIt contains structured academic concepts."
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(sample_content)
            temp_path = f.name

        try:
            extracted = DocumentExtractor.extract_text(temp_path, 'txt')
            file_hash = DocumentExtractor.compute_sha256(temp_path)

            self.assertEqual(extracted['word_count'], 11)
            self.assertEqual(len(extracted['paragraphs']), 2)
            self.assertEqual(len(file_hash), 64)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()

