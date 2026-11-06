import os
import hashlib
import re
import fitz  # PyMuPDF
from docx import Document as DocxDocument

class DocumentExtractor:
    @staticmethod
    def compute_sha256(file_path):
        """Computes SHA-256 hash to prevent duplicate document reprocessing."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def extract_text(file_path, file_extension):
        """
        Extracts raw and normalized text from PDF, DOCX, or TXT.
        Returns:
            dict: {
                'raw_text': str,
                'clean_text': str,
                'word_count': int,
                'character_count': int,
                'paragraphs': list[str]
            }
        """
        ext = file_extension.lower().lstrip('.')
        raw_text = ""

        if ext == 'pdf':
            raw_text = DocumentExtractor._extract_pdf(file_path)
        elif ext in ['docx', 'doc']:
            raw_text = DocumentExtractor._extract_docx(file_path)
        elif ext == 'txt':
            raw_text = DocumentExtractor._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: .{ext}")

        if not raw_text or not raw_text.strip():
            raise ValueError("The uploaded document contains no readable text or is an empty/scanned document.")

        clean_text, paragraphs = DocumentExtractor._normalize_text(raw_text)
        words = re.findall(r'\b\w+\b', clean_text)

        return {
            'raw_text': raw_text,
            'clean_text': clean_text,
            'word_count': len(words),
            'character_count': len(clean_text),
            'paragraphs': paragraphs
        }

    @staticmethod
    def _extract_pdf(file_path):
        doc = fitz.open(file_path)
        full_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                full_text.append(text.strip())
        doc.close()
        return "\n\n".join(full_text)

    @staticmethod
    def _extract_docx(file_path):
        doc = DocxDocument(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        return "\n\n".join(full_text)

    @staticmethod
    def _extract_txt(file_path):
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
        raise ValueError("Could not decode TXT file with standard encodings.")

    @staticmethod
    def _normalize_text(text):
        normalized = text.replace('\r\n', '\n').replace('\r', '\n')
        normalized = normalized.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
        
        raw_paras = normalized.split('\n\n')
        clean_paras = []
        for p in raw_paras:
            cleaned_p = re.sub(r'[ \t]+', ' ', p).strip()
            if cleaned_p:
                clean_paras.append(cleaned_p)

        full_clean = "\n\n".join(clean_paras)
        return full_clean, clean_paras
