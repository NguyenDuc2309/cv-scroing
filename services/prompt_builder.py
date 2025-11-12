def build_cv_analysis_prompt(cv_text: str) -> str:
    """
    Build a structured prompt for CV analysis using LLM.
    
    Args:
        cv_text: Extracted text from CV file
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""Phân tích CV sau đây và đưa ra đánh giá toàn diện.
Trả về kết quả dưới dạng JSON object hợp lệ với cấu trúc chính xác như mô tả bên dưới.

Nội dung CV:
{cv_text}

Hãy phân tích CV này và cung cấp:

1. **Điểm tổng thể (0-100)**: Điểm trung bình có trọng số dựa trên tất cả các yếu tố bên dưới
2. **Cấp độ**: Xác định cấp độ chuyên nghiệp dựa trên kinh nghiệm làm việc:
   - "intern": Không có hoặc ít kinh nghiệm làm việc (< 1 năm)
   - "junior": 1-3 năm kinh nghiệm
   - "mid": 3-5 năm kinh nghiệm
   - "senior": 5+ năm kinh nghiệm
3. **Lĩnh vực**: Xác định lĩnh vực chuyên môn chính (ví dụ: "Phát triển phần mềm", "Marketing", "Tài chính")
4. **Chi tiết điểm số** (mỗi mục 0-100):
   - format: Cấu trúc CV, tổ chức, rõ ràng, chất lượng định dạng
   - experience: Mức độ phù hợp và chất lượng kinh nghiệm làm việc với lĩnh vực
   - skills: Mức độ phù hợp của kỹ năng với lĩnh vực đã xác định
   - education: Trình độ học vấn (có bằng đại học là điểm cộng, học vấn cao hơn điểm cao hơn)
   - portfolio: Sự hiện diện và đề cập đến portfolio/dự án (có điểm thưởng nếu có)
   - certificates: Sự hiện diện của các chứng chỉ liên quan (tiếng Anh, chứng chỉ kỹ thuật, v.v.)
5. **Lý do điểm số**: Với mỗi điểm số ở trên, phải cung cấp lý do cụ thể tại sao đưa ra điểm đó (bằng tiếng Việt)
6. **Điểm mạnh**: Liệt kê 3-5 điểm mạnh chính của CV (bằng tiếng Việt)
7. **Điểm yếu**: Liệt kê 3-5 lĩnh vực cần cải thiện (bằng tiếng Việt)
8. **Gợi ý**: Đưa ra 3-5 gợi ý hành động để cải thiện CV (bằng tiếng Việt)

QUAN TRỌNG: Trả về CHỈ một JSON object hợp lệ với định dạng chính xác này (không markdown, không code blocks, không text thêm):
{{
  "overall_score": <số 0-100>,
  "level": "<intern|junior|mid|senior>",
  "field": "<tên lĩnh vực bằng tiếng Việt>",
  "scores": {{
    "format": {{"score": <số 0-100>, "reason": "<lý do và dẫn chứng bằng tiếng Việt>"}},
    "experience": {{"score": <số 0-100>, "reason": "<lý do và dẫn chứng bằng tiếng Việt>"}},
    "skills": {{"score": <số 0-100>, "reason": "<lý do và dẫn chứng bằng tiếng Việt>"}},
    "education": {{"score": <số 0-100>, "reason": "<lý do và dẫn chứng bằng tiếng Việt>"}},
    "portfolio": {{"score": <số 0-100>, "reason": "<lý do và dẫn chứng bằng tiếng Việt>"}},
    "certificates": {{"score": <số 0-100>, "reason": "<lý do và dẫn chứng bằng tiếng Việt>"}}
  }},
  "strengths": ["<điểm mạnh 1 bằng tiếng Việt>", "<điểm mạnh 2 bằng tiếng Việt>", ...],
  "weaknesses": ["<điểm yếu 1 bằng tiếng Việt>", "<điểm yếu 2 bằng tiếng Việt>", ...],
  "suggestions": ["<gợi ý 1 bằng tiếng Việt>", "<gợi ý 2 bằng tiếng Việt>", ...]
}}

YÊU CẦU BẮT BUỘC:
- TẤT CẢ nội dung phải bằng TIẾNG VIỆT (trừ level và số điểm)
- Mỗi điểm số PHẢI có cả score và reason trong cùng một object
- Trả về CHỈ JSON object, không giải thích, không định dạng markdown
- Không sử dụng \\n hoặc ký tự escape trong response
- Mỗi string trong arrays phải là một dòng không có xuống dòng
- Bắt đầu response trực tiếp với {{ và kết thúc bằng }}
"""
    
    return prompt

