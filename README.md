# LabGuard

Demo P0 kiểm tra repo Lab 03 trước khi nộp. LabGuard chỉ kiểm tra và hướng dẫn,
không chạy code, sửa code hay nộp bài thay học viên.

## Chạy local

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
npm install
npm run dev
```

Mở http://localhost:5173. API chạy tại http://localhost:8000/docs.

GitHub API không cần token cho repo public. Có thể đặt `GITHUB_TOKEN` để tăng
rate limit. Nút **Dùng repo demo chưa hoàn thiện** chạy hoàn toàn offline.

