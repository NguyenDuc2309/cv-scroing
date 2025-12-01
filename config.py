import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    PORT: int = int(os.getenv("PORT", "3001"))
    
    @classmethod
    def validate(cls) -> None:
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")


config = Config()
