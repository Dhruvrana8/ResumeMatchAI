import io
import logging
import pdfplumber
from docx import Document
from fastapi import UploadFile

logger = logging.getLogger(__name__)

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text from an uploaded file (PDF or DOCX).
    """
    filename = file.filename.lower()
    content = await file.read()
    file_stream = io.BytesIO(content)
    
    text = ""
    
    try:
        if filename.endswith(".pdf"):
            with pdfplumber.open(file_stream) as reader:
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
                
        elif filename.endswith(".docx"):
            doc = Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + "\n"
        
        elif filename.endswith(".txt"):
            text = content.decode("utf-8")
            
        else:
            raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT.")
            
    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        raise ValueError(f"Failed to extract text: {str(e)}")
    
    finally:
        await file.seek(0) # Reset file pointer if needed elsewhere, though usually consumed here
        
    return text.strip()
