# CV Scoring API - Hướng dẫn Sử dụng

Hệ thống phân tích và chấm điểm CV tự động sử dụng AI (Gemini hoặc OpenAI).

## Tổng quan

API này cung cấp phân tích toàn diện CV bao gồm:

- Điểm số chi tiết theo từng hạng mục (format, experience, skills, education, portfolio, certificates)
- Lý do cụ thể cho từng điểm số kèm dẫn chứng
- Xác định cấp độ chuyên nghiệp (intern/junior/mid/senior)
- Nhận diện lĩnh vực chuyên môn
- Điểm mạnh và điểm yếu
- Gợi ý cải thiện CV

## API Endpoints

### POST `/upload-cv`

Upload và phân tích CV file.

**Request:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: CV file (PDF hoặc DOCX) - **required**

**Response:**

```json
{
  "status": "success",
  "data": {
    "overall_score": 85,
    "level": "junior",
    "field": "Phát triển phần mềm",
    "scores": {
      "format": {
        "score": 90,
        "reason": "CV có cấu trúc rõ ràng, bố cục hợp lý, dễ đọc. Các phần được tổ chức theo thứ tự logic."
      },
      "experience": {
        "score": 80,
        "reason": "Kinh nghiệm làm việc phù hợp với vị trí, có các dự án liên quan. Tuy nhiên thiếu số liệu cụ thể về thành tựu."
      },
      "skills": {
        "score": 85,
        "reason": "Kỹ năng được liệt kê đầy đủ và phù hợp với lĩnh vực. Bao gồm cả technical và soft skills."
      },
      "education": {
        "score": 90,
        "reason": "Có bằng đại học, chuyên ngành liên quan. GPA tốt và có các khóa học bổ sung."
      },
      "portfolio": {
        "score": 10,
        "reason": "Chưa có portfolio được đề cập hoặc link không hoạt động. Nên thêm các dự án cụ thể."
      },
      "certificates": {
        "score": 15,
        "reason": "Có một số chứng chỉ nhưng còn thiếu các chứng chỉ quan trọng như AWS, Google Cloud, etc."
      }
    },
    "strengths": [
      "Phần kinh nghiệm làm việc rõ ràng và chi tiết",
      "Kỹ năng kỹ thuật phù hợp được liệt kê đầy đủ",
      "Nền tảng giáo dục tốt với bằng đại học chuyên ngành"
    ],
    "weaknesses": [
      "Ít dự án portfolio được đề cập hoặc không có link",
      "Thiếu chứng chỉ chuyên nghiệp quan trọng",
      "Có thể mở rộng thêm về thành tựu và số liệu cụ thể"
    ],
    "suggestions": [
      "Thêm nhiều dự án portfolio kèm link GitHub hoặc demo",
      "Bao gồm các chứng chỉ liên quan (AWS, Google Cloud, etc.)",
      "Định lượng thành tựu bằng số liệu cụ thể (ví dụ: tăng 30% hiệu suất)"
    ]
  },
  "metadata": {
    "filename": "cv_nguyen_van_a.pdf",
    "upload_time": "2025-11-12T08:45:00Z",
    "processing_time_ms": 2200
  }
}
```

### GET `/health`

Kiểm tra trạng thái API.

**Response:**

```json
{
  "status": "healthy"
}
```

### GET `/`

Thông tin API.

**Response:**

```json
{
  "message": "CV Scoring API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/health"
}
```

## Ví dụ sử dụng

### Sử dụng cURL

```bash
curl -X POST "http://localhost:3001/upload-cv" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/cv.pdf"
```

### Sử dụng Python requests

```python
import requests

url = "http://localhost:3001/upload-cv"
files = {"file": open("cv.pdf", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"Overall Score: {result['data']['overall_score']}")
print(f"Level: {result['data']['level']}")
print(f"Field: {result['data']['field']}")
print(f"Processing Time: {result['metadata']['processing_time_ms']}ms")
```

### Sử dụng JavaScript (Fetch API)

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://localhost:3001/upload-cv", {
  method: "POST",
  body: formData,
});

const result = await response.json();
console.log("Overall Score:", result.data.overall_score);
console.log("Processing Time:", result.metadata.processing_time_ms, "ms");
```

## Metadata cho Benchmarking

Mỗi response bao gồm metadata để theo dõi hiệu suất:

- `filename`: Tên file CV được upload
- `upload_time`: Thời điểm upload (ISO format)
- `processing_time_ms`: Thời gian xử lý tính bằng milliseconds

Bạn có thể sử dụng `processing_time_ms` để:

- Benchmark hiệu suất của model
- Theo dõi thời gian xử lý trung bình
- Phát hiện các vấn đề về performance

## Rate Limiting

Mặc định: 10 requests/phút cho mỗi IP address.

Có thể cấu hình trong file `.env`:

```env
RATE_LIMIT_PER_MINUTE=10
```

Khi vượt quá giới hạn, API sẽ trả về:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later."
}
```

## Error Handling

### 400 Bad Request

```json
{
  "error": "Unsupported file format",
  "detail": "Only PDF and DOCX files are supported"
}
```

### 429 Too Many Requests

```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later."
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "detail": "An error occurred while processing your request"
}
```

## Cấu hình

Tất cả cấu hình được thực hiện qua file `.env`:

- `LLM_PROVIDER`: Provider AI sử dụng ("gemini" hoặc "openai")
- `GEMINI_API_KEY`: API key cho Gemini
- `OPENAI_API_KEY`: API key cho OpenAI
- `OPENAI_MODEL`: Model OpenAI sử dụng (mặc định: "gpt-4")
- `RATE_LIMIT_PER_MINUTE`: Giới hạn request/phút (mặc định: 10)
- `MAX_FILE_SIZE`: Kích thước file tối đa (mặc định: 10MB)
- `PORT`: Port cho API server (mặc định: 3001)

Xem file `INSTALL.md` để biết chi tiết về cài đặt và cấu hình.

## API Documentation

Khi server đang chạy, truy cập:

- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## Tính mở rộng

Hệ thống được thiết kế để dễ dàng mở rộng:

- Thêm các hạng mục đánh giá mới trong `ScoreBreakdown`
- Thêm metadata mới trong `Metadata` model
- Tích hợp thêm LLM providers khác
- Thêm các tính năng phân tích nâng cao

Xem `models/schemas.py` để biết cấu trúc dữ liệu chi tiết.
