# Eval

Quality bar khóa trong `spec.md`: ≥85% toàn bộ và 100% case secret critical.

- `golden-set.json`: 38 case có expected status và lớp rủi ro; 14 case `self_test_2026-07-31`.
- `run-01.json`: 23/24; false positive khi comment chứa keyword ReAct.
- `run-02.json`: 24/24 sau root-cause fix.
- `run-03.json`: 38/38 sau khi thêm 14 case từ phiên self-test.
- `run_eval.py`: chạy lại toàn bộ bộ test.
- `run_ai_smoke.py`: gọi provider đã cấu hình và chỉ lưu provider, model, hash input, requirement IDs.

Provenance: 24 case synthetic và 14 case self-test ngày 2026-07-31. 
