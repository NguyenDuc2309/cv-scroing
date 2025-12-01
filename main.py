from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
import time

from config import config
from models.schemas import CVAnalysisResponse, CVAnalysisData, Metadata, TokenUsage
from services.extraction import extract_text
from services.llm_service import get_llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        config.validate()
    except ValueError as e:
        print(f"Warning: {str(e)}")
    yield


app = FastAPI(
    title="CV Scoring API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post(
    "/upload-cv",
    tags=["CV Analysis"],
    summary="Upload and analyze CV",
)
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_cv(
    request: Request,
    file: UploadFile = File(..., description="CV file to analyze (PDF or DOCX format)")
):
    start_time = time.time()
    upload_time = datetime.now(timezone.utc).isoformat()
    
    try:
        filename = file.filename or ""
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed formats: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )
        
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of 10MB"
            )
        
        cv_text = await extract_text(file_content, filename)
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="CV text is too short or empty. Please ensure the file contains readable text."
            )
        
        llm_service = get_llm_service()
        analysis_result = await llm_service.analyze_cv(cv_text)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        token_usage_data = analysis_result.pop("_token_usage", None)
        token_usage = None
        if token_usage_data:
            token_usage = TokenUsage(**token_usage_data)
        
        try:
            data = CVAnalysisData(**analysis_result)
            metadata = Metadata(
                filename=filename,
                upload_time=upload_time,
                processing_time_ms=processing_time_ms,
                token_usage=token_usage
            )
            response = CVAnalysisResponse(status="success", data=data, metadata=metadata)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid response format from LLM: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=config.PORT,
        reload=True,
        reload_excludes=["*.log", "*.pyc", "__pycache__", ".git", "venv", "*.log.*"],
        log_level="info"
    )

