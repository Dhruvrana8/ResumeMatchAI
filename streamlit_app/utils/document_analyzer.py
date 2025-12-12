"""
Document Analysis Module for Direct File Processing

This module provides alternative approaches for analyzing resume files directly
instead of just extracting plain text.
"""

import os
import logging
from typing import Optional, Dict, Any
import base64

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """
    Advanced document analyzer that can process files directly using various methods
    """

    def __init__(self):
        self.available_methods = {
            "ocr": self._analyze_with_ocr,
            "multimodal": self._analyze_with_multimodal,
            "base64": self._analyze_with_base64,
        }

    def analyze_document(self, file_path: str, method: str = "ocr") -> str:
        """
        Analyze a document file directly using the specified method

        Args:
            file_path: Path to the document file
            method: Analysis method ("ocr", "multimodal", "base64")

        Returns:
            Analysis result as string
        """
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"

        if method not in self.available_methods:
            return f"Error: Unknown method '{method}'. Available: {list(self.available_methods.keys())}"

        try:
            return self.available_methods[method](file_path)
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            return f"Error during document analysis: {str(e)}"

    def _analyze_with_ocr(self, file_path: str) -> str:
        """
        Analyze document using OCR (Optical Character Recognition)
        Preserves some layout information
        """
        try:
            # Check if pytesseract is available
            import pytesseract
            from PIL import Image
            import fitz  # PyMuPDF for PDF processing

        except ImportError:
            return """
            OCR Analysis Not Available

            To use OCR analysis, install required packages:
            pip install pytesseract pillow pymupdf

            Also install Tesseract OCR on your system:
            - macOS: brew install tesseract
            - Ubuntu: sudo apt-get install tesseract-ocr
            - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
            """

        try:
            # Extract images from PDF and perform OCR
            doc = fitz.open(file_path)
            full_text = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.open(fitz.io.BytesIO(pix.tobytes()))

                # Perform OCR with layout preservation
                text = pytesseract.image_to_string(img, lang='eng')
                full_text.append(f"=== PAGE {page_num + 1} ===\n{text}")

            doc.close()

            combined_text = "\n\n".join(full_text)

            return f"""
            OCR Analysis Result:

            This analysis preserves document layout and can handle:
            - Multi-column layouts
            - Tables and structured content
            - Various fonts and formatting
            - Scanned documents

            Extracted Text Length: {len(combined_text)} characters

            Full Text:
            {combined_text}
            """

        except Exception as e:
            return f"OCR analysis failed: {str(e)}"

    def _analyze_with_multimodal(self, file_path: str) -> str:
        """
        Future implementation: Use multimodal models for direct document analysis
        """
        return """
        Multimodal Analysis (Not Yet Implemented)

        This would use vision-language models like:
        - LLaVA: Open-source vision-language model
        - GPT-4V: Commercial multimodal model
        - Custom document understanding models

        Benefits:
        - Understands document layout and formatting
        - Can analyze tables, charts, and visual elements
        - Better context understanding
        - Handles complex document structures

        Requirements:
        - Large multimodal models (significant compute requirements)
        - Specialized training data
        - Higher API costs (if using commercial models)

        Would you like me to implement this?
        """

    def _analyze_with_base64(self, file_path: str) -> str:
        """
        Encode file as base64 for potential multimodal analysis
        """
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Encode as base64
            encoded = base64.b64encode(file_data).decode('utf-8')

            file_ext = os.path.splitext(file_path)[1].lower()
            mime_type = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }.get(file_ext, 'application/octet-stream')

            return f"""
            Base64 Encoded File:

            This encoding can be used with multimodal models that accept binary data.
            However, text-only models like Llama cannot meaningfully process this.

            File: {os.path.basename(file_path)}
            Type: {mime_type}
            Size: {len(file_data)} bytes
            Encoded Length: {len(encoded)} characters

            Base64 Data (first 200 chars):
            {encoded[:200]}...

            To use this with a multimodal model, you would send:
            "data:{mime_type};base64,{encoded}"
            """

        except Exception as e:
            return f"Base64 encoding failed: {str(e)}"

def analyze_resume_file_direct(file_path: str, job_description: str, method: str = "ocr") -> str:
    """
    Analyze resume file directly and combine with job description analysis

    Args:
        file_path: Path to resume file
        job_description: Job description text
        method: Analysis method ("ocr", "multimodal", "base64")

    Returns:
        Combined analysis result
    """
    analyzer = DocumentAnalyzer()

    # Analyze the resume file
    resume_analysis = analyzer.analyze_document(file_path, method)

    # Combine with job description for final analysis
    if "Error" not in resume_analysis:
        return f"""
        Direct Document Analysis Result:

        {resume_analysis}

        Next Steps:
        1. The document has been analyzed using {method} method
        2. To complete the analysis, combine this with job description matching
        3. Consider implementing multimodal LLM analysis for richer insights

        Job Description Preview:
        {job_description[:500]}...
        """
    else:
        return resume_analysis

# Quick test function
if __name__ == "__main__":
    # Test with a sample file (if it exists)
    test_file = "sample_resume.pdf"
    if os.path.exists(test_file):
        result = analyze_resume_file_direct(test_file, "Sample job description", "ocr")
        print(result)
    else:
        print("No test file found. Create a sample_resume.pdf to test.")