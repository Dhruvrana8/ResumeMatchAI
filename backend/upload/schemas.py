from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    s3_key: str
    upload_date: datetime
    file_size: int
    
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
