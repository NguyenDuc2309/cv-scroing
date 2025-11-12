from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
import logging
import time

from config import config
from models.schemas import CVAnalysisResponse, CVAnalysisData, Metadata, TokenUsage
from services.extraction import extract_text
from services.llm_service import get_llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        config.validate()
    except ValueError as e:
        print(f"Warning: {str(e)}")
    yield
    # Shutdown (if needed)


# Initialize FastAPI app
app = FastAPI(
    title="CV Scoring API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure logging (simplified - only console, no file to avoid reload loop)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Only console, no file logging
)
logger = logging.getLogger(__name__)


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    description="Returns API information and status",
    response_description="API information"
)
async def root():
    """
    Root endpoint that returns basic API information.
    
    Use this endpoint to verify the API is running and get version information.
    """
    return {
        "message": "CV Scoring API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is healthy and running",
    response_description="Health status"
)
async def health():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns a simple status to indicate the API is operational.
    """
    return {"status": "healthy"}


@app.post(
    "/upload-cv",
    tags=["CV Analysis"],
    summary="Upload and analyze CV",
)
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_cv(
    request: Request,
    file: UploadFile = File(
        ...,
        description="CV file to analyze (PDF or DOCX format)"
    )
):
    # Start processing time tracking
    start_time = time.time()
    upload_time = datetime.now(timezone.utc).isoformat()
    
    try:
        # Validate file extension
        filename = file.filename or ""
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed formats: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size and read content
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {config.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # Extract text from file
        cv_text = await extract_text(file_content, filename)
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="CV text is too short or empty. Please ensure the file contains readable text."
            )
        
        # Analyze CV with LLM (uses provider from config)
        llm_service = get_llm_service()
        analysis_result = await llm_service.analyze_cv(cv_text)
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract token usage if available
        token_usage_data = analysis_result.pop("_token_usage", None)
        token_usage = None
        if token_usage_data:
            token_usage = TokenUsage(**token_usage_data)
        
        # Validate and wrap response with status, data, and metadata
        try:
            # Validate the data structure
            data = CVAnalysisData(**analysis_result)
            # Create metadata
            metadata = Metadata(
                filename=filename,
                upload_time=upload_time,
                processing_time_ms=processing_time_ms,
                token_usage=token_usage
            )
            # Wrap with status, data, and metadata
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
    # Hot reload enabled for development
    # Must use import string format (e.g., "main:app") to enable reload
    # Set reload=False in production
    uvicorn.run(
        "main:app",  # Import string format required for reload
        host="0.0.0.0", 
        port=config.PORT,  # Port from environment variable
        reload=True,  # Hot reload - tự động restart khi code thay đổi
        reload_excludes=["*.log", "*.pyc", "__pycache__", ".git", "venv", "*.log.*"],  # Exclude log files from watch
        log_level="info"
    )

