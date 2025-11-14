# Hướng dẫn Cài đặt

Hướng dẫn chi tiết để cài đặt và cấu hình hệ thống CV Scoring.

## Yêu cầu hệ thống

- Python 3.10 trở lên
- pip (Python package manager)

## Cài đặt

### 1. Clone repository và di chuyển vào thư mục dự án

```bash
cd cv-scoring
```

### 2. Tạo virtual environment (khuyến nghị)

```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` và thêm API keys của bạn:

```env
# LLM Provider Configuration
# Options: "gemini" or "openai"
LLM_PROVIDER=gemini

# Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Rate Limiting
# Number of requests allowed per minute per IP address
RATE_LIMIT_PER_MINUTE=10

# File Upload Settings
# Maximum file size in bytes (default: 10MB)
MAX_FILE_SIZE=10485760

# Server Configuration
# Port for the API server
PORT=3001
```

## Lấy API Keys

### Gemini API Key

1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Đăng nhập bằng tài khoản Google
3. Click "Create API Key"
4. Copy key vào file `.env`

### OpenAI API Key

1. Truy cập [OpenAI Platform](https://platform.openai.com/api-keys)
2. Đăng nhập hoặc tạo tài khoản
3. Vào phần API Keys
4. Tạo secret key mới
5. Copy key vào file `.env`

## Chạy ứng dụng

### Development mode (với hot reload)

```bash
python main.py
```

### Production mode

```bash
uvicorn main:app --host 0.0.0.0 --port 3001
```

Hoặc chỉnh sửa `main.py` và set `reload=False`:

```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=config.PORT,
    reload=False  # Tắt hot reload cho production
)
```

## Kiểm tra cài đặt

Sau khi chạy server, truy cập:

- **Swagger UI**: http://localhost:{PORT}/docs
- **Health check**: http://localhost:{PORT}/health

## Troubleshooting

### Lỗi import modules

Đảm bảo bạn đã activate virtual environment:

```bash
source venv/bin/activate
```

### Lỗi API key

Kiểm tra file `.env` đã được tạo và có API key đúng chưa:

```bash
cat .env
```

### Lỗi port đã được sử dụng

Thay đổi PORT trong file `.env` hoặc kill process đang dùng port đó:

```bash
# Linux/Mac
lsof -ti:3001 | xargs kill -9

# Hoặc đổi PORT trong .env
PORT=3002
```

## Dependencies chính

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `PyMuPDF`: PDF text extraction
- `python-docx`: DOCX text extraction
- `google-generativeai`: Gemini API client
- `openai`: OpenAI API client
- `pydantic`: Data validation
- `slowapi`: Rate limiting
- `python-dotenv`: Environment variables

Logic chấm điểm:

- Core/bonus criteria và cấu trúc JSON được định nghĩa trong `models/schemas.py`.
- Prompt LLM được xây dựng trong `services/prompt_builder.py`.
- `overall_score` được tính lại hoàn toàn ở backend trong `services/scoring.py` dựa trên:
  - Cấp độ ứng viên (`intern`, `fresher`, `junior`, `mid`, `senior`).
  - Bảng trọng số từng tiêu chí (core/bonus) cho mỗi level.

Xem `requirements.txt` để biết đầy đủ danh sách dependencies.
