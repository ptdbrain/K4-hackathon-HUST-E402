# LabGuard — AI Submission Preflight

**CP2 · Show được thứ bấm được.** LabGuard kiểm tra repo Lab 03 trước khi nộp:
đọc yêu cầu, rà artifact và chỉ ra thiếu sót. Nó không chạy, sửa hoặc nộp bài thay học viên.

## Thành viên & phân công

| Thành viên | Phần phụ trách |
|---|---|
| Phan Trọng Đạt — 2A202601138 | _Chưa phân công_ |
| Bùi Thu Trang — 2A202601758 | _Chưa phân công_ |
| Phạm Quốc Minh — 2A202601494 | _Chưa phân công_ |
| Nguyễn Thanh Hùng — 2A202601808 | _Chưa phân công_ |
| Phạm Danh Tuấn Dũng — 2A202601978 | _Chưa phân công_ |
| Đinh Việt Anh — 2A202601516 | _Chưa phân công_ |

## Trạng thái nộp bài

| Artifact | Trạng thái |
|---|---|
| `codebase/` | Hoàn thành cho CP2 — flow chính bấm được |
| `spec.md` | Canvas CP2 — sẽ hoàn thiện trước CP4 |
| `eval/` | Bổ sung golden set và kết quả tại CP3 |
| `validation/` | Bổ sung feedback log tại CP5 |
| `reflection/` | Mỗi thành viên bổ sung trước CP6 |
| `demo-slides.pdf` | Bổ sung trước CP6 |

## Chạy local

```bash
python -m venv .venv
.venv/bin/pip install -r codebase/backend/requirements.txt
cd codebase
npm install
npm run dev
```

Mở http://localhost:5173. API chạy tại http://localhost:8000/docs.
GitHub API không cần token cho repo public; đặt `GITHUB_TOKEN` nếu cần tăng rate limit.
