from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from .utils import analyze_resume
from database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ats_score", tags=["ATS Score"])

@router.post("/analyze")
async def get_ats_score(
    file: UploadFile = File(...),
    job_description: str = Form(None),
    mode: str = Form("resume_ats"),
    db: Session = Depends(get_db)
):
    """
    Analyze resume based on the selected mode:
    - 'resume_ats': Extract info
    - 'resume_vs_jd': Compare with Job Description
    """
    logger.info(f"Received request: mode={mode}, filename={file.filename}")
    
    if mode == "resume_vs_jd" and not job_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Job description is required for 'resume_vs_jd' mode."
        )

    try:
        result = await analyze_resume(file, job_description, mode)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during analysis."
        )    