import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status, UploadFile
import os
from dotenv import load_dotenv
from typing import Optional
import uuid
from datetime import timedelta

load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword"
}

class S3Service:
    def __init__(self):
        """Initialize S3 client."""
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
            raise ValueError("AWS credentials and bucket name must be configured in .env file")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = S3_BUCKET_NAME
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Validate file type and size.
        
        Args:
            file: The uploaded file
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type. Allowed types: PDF, DOCX"
            )
    
    async def upload_file(self, file: UploadFile, user_id: int) -> tuple[str, int]:
        """
        Upload file to S3 bucket.
        
        Args:
            file: The file to upload
            user_id: ID of the user uploading the file
            
        Returns:
            Tuple of (s3_key, file_size)
            
        Raises:
            HTTPException: If upload fails
        """
        # Validate file
        self.validate_file(file)
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Generate unique S3 key
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        s3_key = f"users/{user_id}/documents/{unique_filename}"
        
        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'original_filename': file.filename,
                    'user_id': str(user_id)
                }
            )
            
            return s3_key, file_size
            
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for accessing a file.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL string
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate presigned URL: {str(e)}"
            )
    
    def delete_file(self, s3_key: str) -> None:
        """
        Delete a file from S3.
        
        Args:
            s3_key: S3 object key
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file from S3: {str(e)}"
            )

# Singleton instance
s3_service = S3Service()
