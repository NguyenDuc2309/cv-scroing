def build_cv_analysis_prompt(cv_text: str) -> str:
    prompt = f"""Phân tích CV và trả về CHỈ JSON hợp lệ, KHÔNG markdown.

CV:
{cv_text}

QUY TẮC:
- Mỗi score (0-100) kèm reason cụ thể từ CV.
- Backend sẽ tính lại overall_score theo trọng số level.

CORE (6 tiêu chí):
format: Bố cục, logic, dễ đọc.
experience: Kinh nghiệm field, số năm, vai trò, impact. PHÂN BIỆT intern/trainee (~30%) vs full-time. Chỉ intern/trainee → không thể mid/senior.
skills: Hard skills theo field + mức độ.
soft_skills: Giao tiếp, teamwork, leadership.
education: Bằng cấp, chuyên ngành, GPA (quan trọng intern/fresher).
field_match: Định hướng ngành rõ ràng.

BONUS (6 tiêu chí, không có → 30-40 điểm):
portfolio, certificates, awards, scholarships, side_projects, community.

credibility_issues: Mảng vấn đề độ tin cậy (mốc thời gian tương lai, thông tin không nhất quán). Không có → [].

LEVEL: intern (<0.5 năm) | fresher (0.5-1.5 năm) | junior (1-3 năm full-time) | mid (3-5 năm) | senior (5+ năm). Chỉ intern/trainee → max fresher.

field: Từ mục tiêu nghề nghiệp hoặc suy luận từ kinh nghiệm+skills.
info.location: Địa chỉ/thành phố, để "" nếu không có.
strengths/weaknesses/suggestions: 3-5 mục, tiếng Việt, mỗi phần tử 1 câu ngắn.

YÊU CẦU: TẤT CẢ nội dung TIẾNG VIỆT (trừ level và số điểm). CHỈ JSON, không escape, không xuống dòng trong arrays.

{{
  "overall_score": <0-100>,
  "level": "<intern|fresher|junior|mid|senior>",
  "field": "<tên lĩnh vực tiếng Việt>",
  "info": {{
    "location": "<địa chỉ/thành phố hoặc '' nếu không có>"
  }},
  "core_scores": {{
    "format": {{"score": <0-100>, "reason": "<lý do cụ thể>"}},
    "experience": {{"score": <0-100>, "reason": "<lý do cụ thể, impact, level>"}},
    "skills": {{"score": <0-100>, "reason": "<lý do cụ thể, hard skills, mức độ>"}},
    "soft_skills": {{"score": <0-100>, "reason": "<lý do cụ thể về kỹ năng mềm>"}},
    "education": {{"score": <0-100>, "reason": "<lý do cụ thể, GPA/nơi học nếu có>"}},
    "field_match": {{"score": <0-100>, "reason": "<lý do CV phù hợp/không phù hợp field>"}}
  }},
  "bonus_scores": {{
    "portfolio": {{"score": <0-100>, "reason": "<lý do cụ thể, link/project>"}},
    "certificates": {{"score": <0-100>, "reason": "<lý do cụ thể về chứng chỉ>"}},
    "awards": {{"score": <0-100>, "reason": "<giải thưởng nếu có, nếu không có thì giải thích điểm trung lập>"}},
    "scholarships": {{"score": <0-100>, "reason": "<học bổng nếu có, nếu không có thì giải thích điểm trung lập>"}},
    "side_projects": {{"score": <0-100>, "reason": "<dự án cá nhân nếu có, nếu không có thì giải thích điểm trung lập>"}},
    "community": {{"score": <0-100>, "reason": "<hoạt động cộng đồng/CLB nếu có, nếu không có thì giải thích điểm trung lập>"}}
  }},
  "credibility_issues": ["<vấn đề 1 nếu có>", "<vấn đề 2 nếu có>"],
  "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>", ...],
  "weaknesses": ["<điểm yếu 1>", "<điểm yếu 2>", ...],
  "suggestions": ["<gợi ý 1>", "<gợi ý 2>", ...]
}}"""
    
    return prompt
