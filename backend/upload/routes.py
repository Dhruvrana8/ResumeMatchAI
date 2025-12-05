from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Document
from auth.utils import get_current_user
from upload.schemas import DocumentUploadResponse, DocumentResponse
from upload.s3_service import s3_service

router = APIRouter(prefix="/upload", tags=["Document Upload"])

@router.post("/document", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a single resume document.
    
    - **file**: PDF or DOCX file (max 10MB)
    
    Requires authentication. File will be uploaded to S3 and metadata stored in database.
    """
    # Upload file to S3
    s3_key, file_size = await s3_service.upload_file(file, current_user.id)
    
    # Create document record in database
    new_document = Document(
        user_id=current_user.id,
        filename=file.filename,
        s3_key=s3_key,
        file_size=file_size,
        status="uploaded"
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    return DocumentUploadResponse(
        document_id=new_document.id,
        filename=new_document.filename,
        s3_key=new_document.s3_key,
        upload_date=new_document.upload_date,
        file_size=new_document.file_size
    )

@router.get("/documents", response_model=List[DocumentResponse])
async def get_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all documents uploaded by the current user.
    
    Requires authentication. Returns list of documents with metadata.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    
    # Add presigned URLs to documents
    response_documents = []
    for doc in documents:
        presigned_url = s3_service.generate_presigned_url(doc.s3_key)
        doc_response = DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            filename=doc.filename,
            s3_key=doc.s3_key,
            upload_date=doc.upload_date,
            file_size=doc.file_size,
            status=doc.status,
            presigned_url=presigned_url
        )
        response_documents.append(doc_response)
    
    return response_documents

@router.get("/document/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID.
    
    Requires authentication. Returns document metadata and presigned URL for download.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Generate presigned URL
    presigned_url = s3_service.generate_presigned_url(document.s3_key)
    
    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        filename=document.filename,
        s3_key=document.s3_key,
        upload_date=document.upload_date,
        file_size=document.file_size,
        status=document.status,
        presigned_url=presigned_url
    )

@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document.
    
    Requires authentication. Deletes document from both S3 and database.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete from S3
    s3_service.delete_file(document.s3_key)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return None
