# LabGuard — AI Submission Preflight

LabGuard giúp học viên đối chiếu Codelab, rubric GitHub và repo cho nhiều bài lab trước khi nộp. Prototype chỉ đọc: không chạy code không tin cậy, không sửa và không nộp bài.

## Thành viên

| Thành viên | Phần phụ trách |
|---|---|
| Phan Trọng Đạt — 2A202601138 | Product owner, spec và impact |
| Bùi Thu Trang — 2A202601758 | Evidence survey và validation |
| Phạm Quốc Minh — 2A202601494 | Golden set, quality bar và eval |
| Nguyễn Thanh Hùng — 2A202601808 | Backend, AI provider và GitHub checker |
| Phạm Danh Tuấn Dũng — 2A202601978 | Frontend, demo path và fallback |
| Đinh Việt Anh — 2A202601516 | Secret/data audit, slides và dry run |

## Chạy local

```bash
python -m venv .venv
.venv/bin/pip install -r codebase/backend/requirements.txt
cd codebase
npm install
npm run dev
```

Mở `http://localhost:5173`. API ở `http://localhost:8000/docs`.

Chọn provider/model trong `.env.example`, sau đó nạp biến môi trường trước khi chạy:

```bash
cp codebase/.env.example codebase/.env
```

`AI_PROVIDER` nhận `OPENAI`, `GOOGLE`, `OPENROUTER` hoặc `OLLAMA`; `AI_MODEL` nhận model ID tương ứng. Ba provider cloud cần API key riêng, Ollama dùng `OLLAMA_BASE_URL` và không cần key. AI tạo pack động từ Codelab cùng README/docs của repo đề bài rồi ánh xạ vào tập checker an toàn. Nếu thiếu cấu hình, bài Lab 3 mẫu dùng pack dự phòng; bài khác dừng với lỗi rõ ràng để tránh kiểm sai rubric.

## Kiểm thử và fallback

```bash
cd codebase
../.venv/bin/python -m backend.test_main
../.venv/bin/python ../eval/run_eval.py
npm run build
```

Sau khi provider đã sẵn sàng, tạo trace đã lược nội dung nguồn:

```bash
.venv/bin/python eval/run_ai_smoke.py
```

Fallback Demo: dùng nút “Dùng repo demo chưa hoàn thiện”; kịch bản khó là comment chứa từ khóa ReAct nhưng không có loop động.
