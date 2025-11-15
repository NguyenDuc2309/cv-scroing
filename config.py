import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini") 
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    PORT: int = int(os.getenv("PORT", "3001"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required API keys are present"""
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")


config = Config()

