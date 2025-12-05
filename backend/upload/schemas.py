from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid

class DocumentUploadResponse(BaseModel):
    document_id: UUID = Field(default_factory=uuid.uuid4)
    filename: str
    s3_key: str
    upload_date: datetime
    file_size: int
    user_id: UUID = Field(default_factory=uuid.uuid4)
    
    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    s3_key: str
    upload_date: datetime
    file_size: int
    status: str
    presigned_url: Optional[str] = None
    
    class Config:
        from_attributes = True
