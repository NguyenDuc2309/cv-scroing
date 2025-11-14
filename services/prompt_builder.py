def build_cv_analysis_prompt(cv_text: str) -> str:
    prompt = f"""Phân tích CV và đánh giá chất lượng. Trả về CHỈ JSON object hợp lệ, KHÔNG markdown hay text bổ sung.

CV:
{cv_text}

QUY TẮC CHẤM ĐIỂM:
- Tuân theo quy tắc backend đã định nghĩa, KHÔNG sáng tạo hay thay đổi rule.
- Mỗi score (0-100) phải có reason cụ thể, dẫn chứng từ CV.
- Backend sẽ tính lại overall_score theo trọng số từng level và override giá trị bạn đưa ra.

TIÊU CHÍ CHẤM ĐIỂM:

CORE (6 tiêu chí):
1. format: Bố cục, logic, dễ đọc, rõ ràng.
2. experience: Kinh nghiệm liên quan field, số năm, vai trò, impact. PHÂN BIỆT intern/trainee vs full-time: intern/trainee chỉ tính ~30% giá trị. Nếu chỉ có intern/trainee → không thể là mid/senior.
3. skills: Hard skills theo field + mức độ basic/intermediate/advanced.
4. soft_skills: Giao tiếp, teamwork, leadership, chủ động.
5. education: Bằng cấp, chuyên ngành, GPA (quan trọng cho intern/fresher).
6. field_match: CV có định hướng ngành rõ ràng (hoặc suy luận từ kinh nghiệm).

BONUS (6 tiêu chí, không có → mặc định 30-40 điểm):
7. portfolio: Link website/case study/dự án.
8. certificates: Chứng chỉ liên quan field.
9. awards: Giải thưởng học thuật, cuộc thi, ranking.
10. scholarships: Học bổng.
11. side_projects: Dự án cá nhân.
12. community: CLB, hoạt động xã hội, mentoring.

PHÁT HIỆN VẤN ĐỀ ĐỘ TIN CẬY:
- credibility_issues: Mảng các vấn đề về độ tin cậy CV.
- Mốc thời gian tương lai → "Mốc thời gian kinh nghiệm trong tương lai: [chi tiết]".
- Thông tin không nhất quán → "Thông tin không nhất quán: [chi tiết]".
- Không có vấn đề → mảng rỗng [].

LEVEL DETECTION:
- intern: < 0.5 năm hoặc không có kinh nghiệm
- fresher: 0.5-1.5 năm (có thể mix intern/trainee + full-time)
- junior: 1-3 năm FULL-TIME thực tế
- mid: 3-5 năm FULL-TIME thực tế
- senior: 5+ năm FULL-TIME thực tế, impact lớn, vai trò chính/leadership
- QUAN TRỌNG: Nếu chỉ có intern/trainee → KHÔNG THỂ là mid/senior.

THÔNG TIN KHÁC:
- field: Lấy từ mục tiêu nghề nghiệp/lĩnh vực trong CV, hoặc suy luận từ kinh nghiệm + skills. Không bịa đặt.
- info.location: Trích xuất địa chỉ/thành phố từ CV, để trống "" nếu không tìm thấy.
- strengths: 3-5 điểm mạnh nổi bật, tiếng Việt, mỗi phần tử 1 câu ngắn.
- weaknesses: 3-5 điểm cần cải thiện, liên quan field/level, tiếng Việt, mỗi phần tử 1 câu ngắn.
- suggestions: 3-5 gợi ý cải thiện CV, logic theo level/field, tiếng Việt, mỗi phần tử 1 câu ngắn.

YÊU CẦU:
- TẤT CẢ nội dung bằng TIẾNG VIỆT (trừ level và số điểm).
- Trả về CHỈ JSON object, không escape, không xuống dòng trong arrays.

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
