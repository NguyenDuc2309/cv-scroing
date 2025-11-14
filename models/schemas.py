from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ScoreWithReason(BaseModel):
    """Score with its reason"""
    score: int = Field(..., ge=0, le=100, description="Điểm số (0-100)")
    reason: str = Field(..., description="Lý do và dẫn chứng cho điểm số này (tiếng Việt)")


class CoreScores(BaseModel):
    """Core criteria scores"""
    format: ScoreWithReason = Field(..., description="Bố cục, logic, dễ đọc, rõ ràng")
    experience: ScoreWithReason = Field(..., description="Kinh nghiệm liên quan field, số năm, vai trò, impact")
    skills: ScoreWithReason = Field(..., description="Hard skills theo field + mức độ basic/intermediate/advanced")
    soft_skills: ScoreWithReason = Field(..., description="Giao tiếp, teamwork, leadership, chủ động...")
    education: ScoreWithReason = Field(..., description="Bằng cấp, chuyên ngành, GPA (quan trọng cho intern/fresher)")
    field_match: ScoreWithReason = Field(..., description="CV có định hướng ngành rõ ràng (hoặc suy luận từ kinh nghiệm)")


class BonusScores(BaseModel):
    """Bonus criteria scores (không có → mặc định 30-40 điểm, không trừ overall_score)"""
    portfolio: ScoreWithReason = Field(..., description="Link website/case study/dự án")
    certificates: ScoreWithReason = Field(..., description="Chứng chỉ liên quan field – chỉ cộng điểm, không bắt buộc")
    awards: ScoreWithReason = Field(..., description="Giải thưởng học thuật, cuộc thi, ranking")
    scholarships: ScoreWithReason = Field(..., description="Học bổng")
    side_projects: ScoreWithReason = Field(..., description="Dự án cá nhân")
    community: ScoreWithReason = Field(..., description="CLB, hoạt động xã hội, mentoring")


class CVInfo(BaseModel):
    """Basic information extracted from CV"""
    name: str = Field(default="", description="Tên ứng viên (để trống nếu không tìm thấy)")
    phone: str = Field(default="", description="Số điện thoại (để trống nếu không tìm thấy)")
    email: str = Field(default="", description="Email (để trống nếu không tìm thấy)")
    location: str = Field(default="", description="Địa chỉ/Thành phố (để trống nếu không tìm thấy)")


class CVAnalysisData(BaseModel):
    """CV analysis data"""
    overall_score: int = Field(..., ge=0, le=100, description="Điểm tổng thể CV (0-100)")
    level: str = Field(..., description="Cấp độ chuyên nghiệp: 'intern', 'fresher', 'junior', 'mid', hoặc 'senior'")
    field: str = Field(..., description="Lĩnh vực chuyên môn (ví dụ: 'Phát triển phần mềm', 'Marketing')")
    info: CVInfo = Field(..., description="Thông tin cơ bản trích xuất từ CV")
    core_scores: CoreScores = Field(..., description="Core Criteria - Tiêu chí chính (0-100)")
    bonus_scores: BonusScores = Field(..., description="Bonus Criteria - Tiêu chí cộng điểm (0-100, không có → 30-40 điểm)")
    credibility_issues: List[str] = Field(default_factory=list, description="Danh sách các vấn đề về độ tin cậy CV (ví dụ: mốc thời gian tương lai, thông tin không nhất quán)")
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
    status: str = Field(..., description="Status of the response")
    data: CVAnalysisData = Field(..., description="CV analysis data")
    metadata: Metadata = Field(..., description="Metadata for benchmarking and tracking")