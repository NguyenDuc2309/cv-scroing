def build_cv_analysis_prompt(cv_text: str) -> str:
    """
    Build an optimized prompt for CV analysis using LLM,
    adding soft skills, detailed experience evaluation, skill proficiency levels,
    and optimized certificates scoring per field.
    
    Args:
        cv_text: Extracted text from CV file
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""Phân tích CV sau đây và đưa ra đánh giá toàn diện. 
Trả về CHỈ một JSON object hợp lệ, KHÔNG markdown, code block, hoặc text bổ sung.

Nội dung CV:
{cv_text}

Hướng dẫn chi tiết:

1. **overall_score (0-100)**: Trung bình có trọng số của tất cả các tiêu chí dưới.
2. **level**: Xác định cấp độ dựa trên kinh nghiệm làm việc thực tế:
   - intern: <1 năm hoặc không có kinh nghiệm
   - junior: 1-3 năm
   - mid: 3-5 năm
   - senior: >5 năm
3. **field**: Nếu CV có ghi mục tiêu nghề nghiệp hoặc lĩnh vực, lấy ra chính xác; nếu không có thì dựa trên kinh nghiệm và kỹ năng liên quan. Tuyệt đối không bịa đặt.
4. **info**: Trích xuất thông tin cơ bản từ CV:
   - name: Tên ứng viên (từ phần header hoặc thông tin cá nhân)
   - phone: Số điện thoại (nếu có)
   - email: Email (nếu có)
   - location: Địa chỉ hoặc thành phố (nếu có)
   Nếu không tìm thấy thông tin nào, để trống string rỗng "".
5. **scores** (0-100, kèm reason cụ thể):
   - format: Cấu trúc, bố cục, tiêu đề, font, khoảng cách, dễ đọc. Nêu ví dụ từ CV.
   - experience: Chỉ đánh giá kinh nghiệm liên quan đến field/role. Phân loại theo loại kinh nghiệm: full-time, part-time, internship, volunteer. Điểm đánh giá dựa trên **impact dự án/role** và cấp độ ứng viên. Nêu số năm, vai trò, dự án cụ thể. Không đánh giá kinh nghiệm không liên quan.
   - skills: Phân biệt **hard skill** và **soft skill**. Chỉ đánh giá các kỹ năng liên quan field/role, theo level ứng viên. Đánh giá **mức độ thành thạo**: basic, intermediate, advanced. Tránh lan man.
   - soft_skills: Đánh giá kỹ năng mềm nổi bật như giao tiếp, teamwork, leadership, adaptability, initiative. Tăng điểm nếu phù hợp với level ứng viên.
   - education: Đánh giá bằng cấp, chuyên ngành, GPA (nếu có). Thang điểm Việt Nam: 4 điểm: Xuất sắc 3.6-4.0, Giỏi 3.2-3.59, Khá 2.5-3.19, Trung bình 2.0-2.49, Yếu <2.0. 10 điểm: Giỏi 8.5-10, Khá giỏi 8.0-8.4, Khá 7.0-7.9, Trung bình khá 6.5-6.9. Nêu xếp loại, ý nghĩa với role.
   - portfolio: Đánh giá sự hiện diện và chất lượng portfolio/dự án hoặc link liên quan (GitHub, website, case study...). Cộng điểm nếu có, không trừ nếu không có. Nêu ví dụ cụ thể.
   - certificates: Đánh giá chứng chỉ liên quan field/role, bao gồm cả chứng chỉ nghề, chứng chỉ online (Coursera, Udemy, Google, Microsoft…). Với một số ngành (Kinh tế, Logistics, IT, kỹ thuật) chứng chỉ đặc thù là điểm cộng lớn. Nêu rõ có hay không và tác động đến scoring.
6. **strengths**: Liệt kê 3-5 điểm mạnh nổi bật, bằng tiếng Việt, mỗi dòng 1 item, tránh lặp từ.
7. **weaknesses**: Liệt kê 3-5 điểm cần cải thiện, liên quan field/level, bằng tiếng Việt, mỗi dòng 1 item, tránh lan man.
8. **suggestions**: 3-5 gợi ý cải thiện CV, logic theo level, field, strengths/weaknesses, bằng tiếng Việt, mỗi dòng 1 item.

QUAN TRỌNG:
- Mỗi score phải có score và reason cụ thể, dẫn chứng từ CV, tránh lặp từ chung chung.
- TẤT CẢ nội dung bằng TIẾNG VIỆT (trừ level và số điểm).
- Trả về CHỈ JSON object, không ký tự escape, không xuống dòng trong arrays.
- Bắt đầu trực tiếp với {{ và kết thúc bằng }}.
- Tuân thủ cấu trúc JSON:

{{
  "overall_score": <0-100>,
  "level": "<intern|junior|mid|senior>",
  "field": "<tên lĩnh vực bằng tiếng Việt>",
  "info": {{
    "name": "<tên ứng viên hoặc '' nếu không có>",
    "phone": "<số điện thoại hoặc '' nếu không có>",
    "email": "<email hoặc '' nếu không có>",
    "location": "<địa chỉ/thành phố hoặc '' nếu không có>"
  }},
  "scores": {{
    "format": {{"score": <0-100>, "reason": "<lý do cụ thể từ CV>"}},
    "experience": {{"score": <0-100>, "reason": "<lý do cụ thể từ CV, chỉ kinh nghiệm liên quan, theo impact và level>"}},
    "skills": {{"score": <0-100>, "reason": "<lý do cụ thể từ CV, hard/soft skill, mức độ thành thạo, theo level>"}},
    "soft_skills": {{"score": <0-100>, "reason": "<lý do cụ thể từ CV, kỹ năng mềm nổi bật>"}},
    "education": {{"score": <0-100>, "reason": "<lý do cụ thể, GPA/thang điểm Việt Nam>"}},
    "portfolio": {{"score": <0-100>, "reason": "<lý do cụ thể, link/project có hay không>"}},
    "certificates": {{"score": <0-100>, "reason": "<lý do cụ thể, chứng chỉ liên quan ngành, online, đặc thù>"}}
  }},
  "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>", ...],
  "weaknesses": ["<điểm yếu 1>", "<điểm yếu 2>", ...],
  "suggestions": ["<gợi ý 1>", "<gợi ý 2>", ...]
}}"""
    
    return prompt
