# PDP Integration Studio

AI hỗ trợ tích hợp năng lực PDP/INI&SED vào môn học, kế hoạch bài dạy và dự án. Ứng dụng chạy trên FastAPI/Vercel và gọi OpenAI API từ phía server.

## Biến môi trường
- `OPENAI_API_KEY`: khóa OpenAI API (bắt buộc để dùng AI thật)
- `OPENAI_MODEL`: model, mặc định `gpt-6.1-sol`
- `MOCK_AI`: đặt `false` trên production

Không commit API key vào repository.
