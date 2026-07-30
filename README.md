# LabGuard — AI Submission Preflight

**CP2 · Show được thứ bấm được.** LabGuard kiểm tra repo Lab 03 trước khi nộp:
đọc yêu cầu, rà artifact và chỉ ra thiếu sót. Nó không chạy, sửa hoặc nộp bài thay học viên.

## Thành viên & phân công

| Thành viên | Phần phụ trách |
|---|---|
| _Cập nhật trước CP4_ | Product/spec |
| _Cập nhật trước CP4_ | Prototype/code |
| _Cập nhật trước CP4_ | Eval/validation/demo |

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
