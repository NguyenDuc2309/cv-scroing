def build_cv_analysis_prompt(cv_text: str, level: str, field: str = "") -> str:
    field_context = f"Lĩnh vực ứng viên: {field}. " if field else ""
    
    prompt = f"""Phân tích CV và đánh giá chất lượng. Trả về CHỈ JSON object hợp lệ, KHÔNG markdown hay text bổ sung.

CV:
{cv_text}

Context: Cấp độ ứng viên: {level}. {field_context}

Đánh giá các tiêu chí (0-100, kèm reason cụ thể từ CV):

1. **format**: Cấu trúc, bố cục, dễ đọc. Nêu ví dụ cụ thể.
2. **experience**: Chỉ kinh nghiệm liên quan field. Đánh giá theo impact và level {level}. Nêu số năm, vai trò, dự án.
3. **skills**: Hard/soft skills liên quan field, theo level {level}. Mức độ thành thạo: basic/intermediate/advanced.
4. **soft_skills**: Kỹ năng mềm nổi bật (giao tiếp, teamwork, leadership, adaptability). Phù hợp với level {level}.
5. **education**: Bằng cấp, chuyên ngành, GPA. Thang VN: 4 điểm (Xuất sắc 3.6-4.0, Giỏi 3.2-3.59, Khá 2.5-3.19) hoặc 10 điểm (Giỏi 8.5-10, Khá 7.0-7.9).
6. **portfolio**: Portfolio/dự án/link (GitHub, website, case study). Cộng điểm nếu có.
7. **certificates**: Chứng chỉ liên quan field (nghề, online: Coursera, Udemy, Google, Microsoft). Đặc thù ngành (IT, Kinh tế, Logistics) là điểm cộng lớn.

8. **field**: Nếu CV có mục tiêu nghề nghiệp/lĩnh vực, lấy chính xác; nếu không thì dựa trên kinh nghiệm/kỹ năng. Không bịa đặt.

9. **info.location**: Trích xuất địa chỉ/thành phố từ CV. Nếu không tìm thấy, để trống "".

10. **overall_score**: Trung bình có trọng số của tất cả scores.

11. **strengths**: 3-5 điểm mạnh nổi bật, tiếng Việt, mỗi dòng 1 item.
12. **weaknesses**: 3-5 điểm cần cải thiện, liên quan field/level, tiếng Việt, mỗi dòng 1 item.
13. **suggestions**: 3-5 gợi ý cải thiện CV, logic theo level/field, tiếng Việt, mỗi dòng 1 item.

QUAN TRỌNG:
- Mỗi score phải có reason cụ thể, dẫn chứng từ CV.
- TẤT CẢ nội dung bằng TIẾNG VIỆT (trừ level và số điểm).
- Trả về CHỈ JSON object, không escape, không xuống dòng trong arrays.

{{
  "overall_score": <0-100>,
  "field": "<tên lĩnh vực tiếng Việt>",
  "info": {{
    "location": "<địa chỉ/thành phố hoặc '' nếu không có>"
  }},
  "scores": {{
    "format": {{"score": <0-100>, "reason": "<lý do cụ thể>"}},
    "experience": {{"score": <0-100>, "reason": "<lý do cụ thể, impact, level>"}},
    "skills": {{"score": <0-100>, "reason": "<lý do cụ thể, hard/soft, mức độ>"}},
    "soft_skills": {{"score": <0-100>, "reason": "<lý do cụ thể>"}},
    "education": {{"score": <0-100>, "reason": "<lý do cụ thể, GPA>"}},
    "portfolio": {{"score": <0-100>, "reason": "<lý do cụ thể, link/project>"}},
    "certificates": {{"score": <0-100>, "reason": "<lý do cụ thể>"}}
  }},
  "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>", ...],
  "weaknesses": ["<điểm yếu 1>", "<điểm yếu 2>", ...],
  "suggestions": ["<gợi ý 1>", "<gợi ý 2>", ...]
}}"""
    
    return prompt
