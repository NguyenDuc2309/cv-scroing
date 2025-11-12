from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ScoreWithReason(BaseModel):
    """Score with its reason"""
    score: int = Field(..., ge=0, le=100, description="Điểm số (0-100)")
    reason: str = Field(..., description="Lý do và dẫn chứng cho điểm số này (tiếng Việt)")


class ScoreBreakdown(BaseModel):
    """Individual score components with reasons"""
    format: ScoreWithReason = Field(..., description="Điểm format và lý do")
    experience: ScoreWithReason = Field(..., description="Điểm experience và lý do")
    skills: ScoreWithReason = Field(..., description="Điểm skills và lý do")
    soft_skills: ScoreWithReason = Field(..., description="Điểm soft_skills và lý do")
    education: ScoreWithReason = Field(..., description="Điểm education và lý do")
    portfolio: ScoreWithReason = Field(..., description="Điểm portfolio và lý do")
    certificates: ScoreWithReason = Field(..., description="Điểm certificates và lý do")


class CVAnalysisData(BaseModel):
    """CV analysis data"""
    overall_score: int = Field(..., ge=0, le=100, description="Điểm tổng thể CV (0-100)")
    level: str = Field(..., description="Cấp độ chuyên nghiệp: 'intern', 'junior', 'mid', hoặc 'senior'")
    field: str = Field(..., description="Lĩnh vực chuyên môn (ví dụ: 'Phát triển phần mềm', 'Marketing')")
    scores: ScoreBreakdown = Field(..., description="Chi tiết điểm số theo từng hạng mục")
    strengths: List[str] = Field(..., description="Danh sách điểm mạnh của CV (tiếng Việt)")
    weaknesses: List[str] = Field(..., description="Danh sách điểm yếu của CV (tiếng Việt)")
    suggestions: List[str] = Field(..., description="Gợi ý cải thiện CV (tiếng Việt)")


class TokenUsage(BaseModel):
    """Token usage information"""
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total tokens used")


class Metadata(BaseModel):
    """Metadata for benchmarking and tracking"""
    filename: str = Field(..., description="Original filename of uploaded CV")
    upload_time: str = Field(..., description="Upload timestamp in ISO format")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    token_usage: Optional[TokenUsage] = Field(None, description="Token usage information from LLM")


class CVAnalysisResponse(BaseModel):
    """Response model for CV analysis"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": {
                    "overall_score": 85,
                    "level": "junior",
                    "field": "Phát triển phần mềm",
                    "scores": {
                        "format": {"score": 90, "reason": "CV có cấu trúc rõ ràng, bố cục hợp lý"},
                        "experience": {"score": 80, "reason": "Kinh nghiệm phù hợp với vị trí"},
                        "skills": {"score": 85, "reason": "Kỹ năng được liệt kê đầy đủ"},
                        "soft_skills": {"score": 85, "reason": "Kỹ năng mềm được liệt kê đầy đủ"},
                        "education": {"score": 90, "reason": "Có bằng đại học chuyên ngành"},
                        "portfolio": {"score": 10, "reason": "Chưa có portfolio được đề cập"},
                        "certificates": {"score": 15, "reason": "Thiếu chứng chỉ quan trọng"}
                    },
                    "strengths": ["Phần kinh nghiệm rõ ràng", "Kỹ năng phù hợp"],
                    "weaknesses": ["Ít portfolio", "Thiếu chứng chỉ"],
                    "suggestions": ["Thêm portfolio", "Bổ sung chứng chỉ"]
                },
                "metadata": {
                    "filename": "cv_nguyen_van_a.pdf",
                    "upload_time": "2025-11-12T08:45:00Z",
                    "processing_time_ms": 2200,
                    "token_usage": {
                        "prompt_tokens": 1500,
                        "completion_tokens": 800,
                        "total_tokens": 2300
                    }
                }
            }
        }
    )
    
    status: str = Field(..., description="Status of the response")
    data: CVAnalysisData = Field(..., description="CV analysis data")
    metadata: Metadata = Field(..., description="Metadata for benchmarking and tracking")