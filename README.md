# LabGuard — AI Submission Preflight

LabGuard giúp học viên đối chiếu Codelab, rubric GitHub và repo cho nhiều bài lab trước khi nộp. Prototype chỉ đọc: không chạy code không tin cậy, không sửa và không nộp bài.

## Thành viên & phần có tên

| Thành viên | Phần phụ trách |
|---|---|
| Phan Trọng Đạt — 2A202601138 | Product owner, spec và impact |
| Bùi Thu Trang — 2A202601758 | Evidence survey và validation |
| Phạm Quốc Minh — 2A202601494 | Golden set, quality bar và eval |
| Nguyễn Thanh Hùng — 2A202601808 | Backend, AI provider và GitHub checker |
| Phạm Danh Tuấn Dũng — 2A202601978 | Frontend, demo path và fallback |
| Đinh Việt Anh — 2A202601516 | Secret/data audit, slides và dry run |

## Artifact

| Artifact | Trạng thái trung thực |
|---|---|
| `spec.md` | Đủ §1–§9; raw survey và validation người thật còn chờ |
| `codebase/` | Mock end-to-end; hỗ trợ OpenAI, Google AI, OpenRouter, Ollama; offline mock có nhãn |
| `eval/` | 38 cases (24 synthetic + 14 self-test); Run 01 = 95,8%, Run 03 = 100% |
| `validation/` | Có survey tổng hợp + dry run kỹ thuật; V01–V05 còn trống |
| `demo-slides.pdf` | Đang thiếu trong workspace; team phải khôi phục trước khi nộp |
| `reflection/` | Đã có bản nháp hoàn chỉnh; từng thành viên phải đọc và xác nhận |

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
set -a
source codebase/.env
set +a
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

Fallback Demo: dùng nút “Dùng repo demo chưa hoàn thiện”; kịch bản khó là comment chứa từ khóa ReAct nhưng không có loop động. Slide nguồn là `demo-slides.html`; in lại `demo-slides.pdf` sau khi điền evidence/validation.

## Việc con người bắt buộc trước CP6

1. Khóa `spec.md` đúng hạn của K4: **12:00 ngày 2 tại CP4**. Checkpoint trễ không thể lấy lại điểm đúng hạn.
2. Thu ≥20 phản hồi ngoài nhóm theo `validation/evidence-survey.md`; điền số/quote vào spec §1–§2 và slide 1–2.
3. Chốt tên ≥3 willing users; cho ≥5 người ngoài nhóm tự test, trong đó ≥2 willing users, rồi điền `validation/feedback-log.md`.
4. Áp dụng ít nhất 1 feedback thật hoặc ghi lý do giữ nguyên trong spec §9; khôi phục `demo-slides.pdf`.
5. Bổ sung ≥10 case từ chatlog thật nếu BTC cấp data pack; 14 case self-test hiện không thay thế tiêu chí này.
6. Mỗi thành viên tự hoàn thiện reflection, dry run 5 phút, mỗi người nói ≥1 phần và tự nộp cùng một link repo.
7. Trước push: kiểm tra không có API key, `.env`, dữ liệu cá nhân hoặc data pack; thu hồi ngay nếu key từng xuất hiện trong Git.
