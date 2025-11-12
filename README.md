# CV Scoring API

Hệ thống backend sử dụng FastAPI và LLM (Google Gemini hoặc OpenAI) để tự động đánh giá chất lượng CV. Mục tiêu chính là cung cấp báo cáo chấm điểm chi tiết, nhận diện cấp độ ứng viên, xác định lĩnh vực chuyên môn và đề xuất cải thiện – tất cả bằng tiếng Việt.

## Giá trị cốt lõi

- **Phân tích tự động**: Trích xuất nội dung từ PDF/DOCX và gửi tới LLM để chấm điểm.
- **Điểm số rõ ràng**: Mỗi tiêu chí đều có điểm (0-100) kèm lý do chi tiết bằng tiếng Việt.
- **Hiểu ứng viên**: Xác định level (intern/junior/mid/senior) và lĩnh vực chuyên môn từ kinh nghiệm thực tế.
- **Insight hành động**: Liệt kê điểm mạnh, điểm yếu và gợi ý cải thiện cụ thể cho ứng viên.
- **Theo dõi hiệu suất**: Metadata đi kèm giúp đo thời gian xử lý, token sử dụng và truy vết file.

## Kiến trúc tổng quan

- **FastAPI backend**: Một dịch vụ duy nhất xử lý upload, trích xuất, gọi LLM và trả JSON chuẩn hóa.
- **LLM service layer**: Tầng trung gian cho phép chọn Gemini hoặc OpenAI chỉ bằng biến môi trường.
- **Text extraction service**: Sử dụng PyMuPDF và python-docx để đọc file PDF/DOCX ổn định.
- **Prompt builder**: Định nghĩa format JSON đầu ra và yêu cầu LLM trả lời hoàn toàn bằng tiếng Việt.
- **Schema chuẩn hóa**: Pydantic đảm bảo response có cấu trúc `status`, `data`, `metadata`, dễ consume cho frontend.
- **Rate limiting**: SlowAPI tránh lạm dụng endpoint upload công khai.
- **Logging & metadata**: Ghi nhận filename, upload time, processing_time_ms và token_usage cho mục đích benchmark.

## Luồng xử lý

1. Người dùng upload CV (PDF hoặc DOCX) qua endpoint công khai.
2. FastAPI kiểm tra định dạng, dung lượng và trích xuất text.
3. Prompt được dựng bằng tiếng Việt, yêu cầu chấm điểm chi tiết + lý do.
4. LLM (Gemini/OpenAI) trả về JSON đúng cấu trúc quy định.
5. API chuẩn hóa response, bổ sung metadata và trả về cho frontend.

## Các tiêu chí chấm điểm

- `format`: Bố cục, cấu trúc, mức độ dễ đọc của CV.
- `experience`: Kinh nghiệm liên quan trực tiếp đến lĩnh vực ứng viên.
- `skills`: Hard skills quan trọng, đánh giá theo mức độ thành thạo.
- `soft_skills`: Kỹ năng mềm được thể hiện trong CV.
- `education`: Bằng cấp, chuyên ngành, GPA (nếu có).
- `portfolio`: Dự án, sản phẩm, liên kết chứng minh năng lực.
- `certificates`: Chứng chỉ chuyên môn và ngoại ngữ.

Mỗi tiêu chí bao gồm `{ "score": 0-100, "reason": "lí do bằng tiếng Việt" }`.

## Thông tin trích xuất bổ sung

- `info.name`, `info.phone`, `info.email`, `info.location`: lấy từ CV, nếu không tìm thấy thì để chuỗi rỗng.
- Các trường dữ liệu khác (`strengths`, `weaknesses`, `suggestions`) luôn trả về danh sách string tiếng Việt.

## Tích hợp LLM

- Cấu hình `LLM_PROVIDER` để chuyển nhanh giữa `gemini` và `openai`.
- Tracking `token_usage` (prompt, completion, total) để quản lý chi phí.
- Hỗ trợ lazy initialization để tránh lỗi khi thiếu API key.

## Hạn chế & lưu ý

- Kết quả phụ thuộc chất lượng CV và model LLM hiện tại.
- Không lưu trữ file CV, toàn bộ xử lý nằm trong request.
- Nên triển khai HTTPS và cơ chế auth nếu dùng trong môi trường production.

## Deployment nhanh

- **Docker Compose**: `docker compose up -d --build` để build và chạy images.

Chi tiết cài đặt, requirements và thiết lập môi trường nằm trong `INSTALL.md`.

## Tài liệu API

- Swagger UI: `http://localhost:{PORT}/docs`

Các endpoint được mô tả trực tiếp trong tài liệu tự sinh từ FastAPI.

## Liên hệ & đóng góp

- Hãy mở issue nếu phát hiện bug, ý tưởng mới hoặc cần hỗ trợ.
- Pull request được hoan nghênh cho các tính năng như caching, auth, UI upload mẫu, v.v.
