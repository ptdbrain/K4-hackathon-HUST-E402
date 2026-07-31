import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "codebase"))

from backend.main import extract_with_ai  # noqa: E402

selected, trace = extract_with_ai(
    "Repo phải có README.md, spec.md, codebase/, eval/ và validation/. "
    "Không được commit .env hoặc API key.",
    {"README.md": "Submission checklist: README.md, spec.md, codebase/, eval/, validation/. Never commit .env or API keys."},
)
if selected is None:
    raise SystemExit(f"AI smoke test chưa chạy thật: {trace['reason']}")

(ROOT / "eval/ai-trace.json").write_text(
    json.dumps(trace, ensure_ascii=False, indent=2) + "\n"
)
print(f"AI thật chọn {len(selected)} requirement; trace đã được ẩn nội dung nguồn.")
