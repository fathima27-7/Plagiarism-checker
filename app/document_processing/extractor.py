import os
import hashlib
import re
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from app.utils.nlp_utils import count_words

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
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_extension.lower().lstrip('.')
        raw_text = ""

        try:
            if ext == 'pdf':
                raw_text = DocumentExtractor._extract_pdf(file_path)
            elif ext in ['docx', 'doc']:
                raw_text = DocumentExtractor._extract_docx(file_path)
            elif ext == 'txt':
                raw_text = DocumentExtractor._extract_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: .{ext}. Supported formats are .pdf, .docx, and .txt.")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to read or parse .{ext} document: {str(e)}")

        if not raw_text or not raw_text.strip():
            raise ValueError(f"The uploaded .{ext} document contains no readable text or is an empty/scanned document.")

        clean_text, paragraphs = DocumentExtractor._normalize_text(raw_text)
        word_count = count_words(clean_text)

        if word_count == 0:
            raise ValueError("The uploaded document contains no valid words.")

        return {
            'raw_text': raw_text,
            'clean_text': clean_text,
            'word_count': word_count,
            'character_count': len(clean_text),
            'paragraphs': paragraphs
        }

    @staticmethod
    def _extract_pdf(file_path):
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Corrupted or invalid PDF file: {str(e)}")

        if doc.is_encrypted:
            doc.close()
            raise ValueError("The uploaded PDF is encrypted or password-protected. Please provide an unencrypted document.")

        if len(doc) == 0:
            doc.close()
            raise ValueError("The uploaded PDF has 0 pages.")

        full_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text and text.strip():
                full_text.append(text.strip())

        doc.close()

        if not full_text:
            raise ValueError("The uploaded PDF contains no extractable text. Scanned or image-only PDFs are not supported.")

        return "\n\n".join(full_text)

    @staticmethod
    def _extract_docx(file_path):
        try:
            doc = DocxDocument(file_path)
        except Exception as e:
            raise ValueError(f"Corrupted or invalid DOCX file: {str(e)}")

        full_text = []

        # Extract paragraphs (body + headings)
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text.append(text)

        # Extract tables row by row with cell deduplication
        for table in doc.tables:
            for row in table.rows:
                row_cells = []
                for cell in row.cells:
                    ctext = cell.text.strip()
                    if ctext and (not row_cells or ctext != row_cells[-1]):
                        row_cells.append(ctext)
                if row_cells:
                    full_text.append(" | ".join(row_cells))

        if not full_text:
            raise ValueError("The uploaded DOCX contains no extractable paragraphs or text.")

        return "\n\n".join(full_text)

    @staticmethod
    def _extract_txt(file_path):
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    if content and content.strip():
                        return content
                    elif content == "":
                        raise ValueError("The uploaded TXT file is completely empty.")
            except (UnicodeDecodeError, LookupError):
                continue
        raise ValueError("Could not decode TXT file with standard encodings (UTF-8, Latin-1, CP1252).")

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
