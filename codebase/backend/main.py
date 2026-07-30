from __future__ import annotations

import ast
import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[1]
PACK = json.loads((ROOT / "assignment-packs/day3-chatbot-react-agent.json").read_text())
GITHUB_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+)/?$")
SECRET_RE = re.compile(r"(?:sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,}|api[_-]?key\s*=\s*[\"'][^\"']{12,})", re.I)
SEVERITY_SCORE = {"critical": 40, "high": 30, "medium": 20, "low": 10}

assignments: dict[str, list[dict[str, Any]]] = {}
analyses: dict[str, dict[str, Any]] = {}


class CodelabFile(BaseModel):
    name: str
    type: str = ""
    size: int = Field(ge=0, le=25_000_000)


class ExtractRequest(BaseModel):
    assignment_repo_url: str
    codelab_text: str = Field(default="", max_length=200_000)
    codelab_files: list[CodelabFile] = Field(default_factory=list, max_length=20)

    @field_validator("assignment_repo_url")
    @classmethod
    def public_github_url(cls, value: str) -> str:
        if not GITHUB_RE.fullmatch(value.strip()):
            raise ValueError("Cần URL GitHub public hợp lệ.")
        return value.strip()


class ConfirmRequest(BaseModel):
    requirements: list[dict[str, Any]]


class AnalysisRequest(BaseModel):
    assignment_id: str
    submission_repo_url: str

    @field_validator("submission_repo_url")
    @classmethod
    def submission_url(cls, value: str) -> str:
        if value == "demo://not-ready" or GITHUB_RE.fullmatch(value.strip()):
            return value.strip()
        raise ValueError("Cần URL GitHub public hợp lệ.")


class FeedbackRequest(BaseModel):
    requirement_id: str
    reason: str = Field(min_length=1, max_length=300)


app = FastAPI(title="LabGuard API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


def github_json(url: str) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "LabGuard"}
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        message = "Repo không tồn tại hoặc đang private." if error.code == 404 else "GitHub API tạm thời không khả dụng."
        raise HTTPException(status_code=422, detail=message) from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise HTTPException(status_code=503, detail="Không kết nối được GitHub. Hãy dùng repo demo offline.") from error


def read_repo(repo_url: str) -> tuple[dict[str, str], str]:
    if repo_url == "demo://not-ready":
        return demo_repo(), ""
    owner, repo = GITHUB_RE.fullmatch(repo_url).groups()
    metadata = github_json(f"https://api.github.com/repos/{owner}/{repo}")
    branch = urllib.parse.quote(metadata["default_branch"], safe="")
    tree = github_json(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
    files: dict[str, str] = {}
    wanted = [
        item for item in tree.get("tree", [])
        if item.get("type") == "blob"
        and item.get("size", 0) <= 300_000
        and (item["path"].endswith((".py", ".md", ".json", ".mermaid")) or item["path"] in {".env", ".gitignore"})
    ][:100]
    for item in wanted:
        blob = github_json(item["url"])
        if blob.get("encoding") == "base64":
            files[item["path"]] = base64.b64decode(blob["content"]).decode("utf-8", errors="replace")
    return files, f"https://github.com/{owner}/{repo}/blob/{metadata['default_branch']}/"


def demo_repo() -> dict[str, str]:
    return {
        ".gitignore": ".env\n__pycache__/\n",
        "config/test_cases.json": json.dumps([{"query": str(i), "type": "simple"} for i in range(5)]),
        "src/prompts.py": "MAX_ITERATIONS = 5\nAVAILABLE_TOOLS = {'weather': get_weather}\n",
        "src/tools.py": 'def get_weather(city):\n    """Get weather for a city. Input: city. Output: forecast. Errors: raises ValueError."""\n    return "sunny"\n',
        "src/app.py": '''def run_baseline(user_query):\n    return llm.generate(user_query)\n\ndef run_react_agent(user_query):\n    for _ in range(MAX_ITERATIONS):\n        thought = llm.generate(user_query)\n        observation = get_weather("Hà Nội")\n        if "Final Answer" in thought:\n            return thought\n''',
        "docs/trace_eval.md": "# Evaluation\n5 cases completed. Baseline and ReAct compared.\n",
    }


def has_python_symbol(files: dict[str, str], symbol: str) -> bool:
    for path, content in files.items():
        if not path.endswith(".py"):
            continue
        try:
            if any(isinstance(node, (ast.Name, ast.FunctionDef, ast.ClassDef)) and getattr(node, "id", getattr(node, "name", "")) == symbol for node in ast.walk(ast.parse(content))):
                return True
        except SyntaxError:
            continue
    return False


def baseline_has_no_tools(content: str) -> bool | None:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and "baseline" in node.name.lower()]
    if not functions:
        return None
    calls = [node for node in ast.walk(functions[0]) if isinstance(node, ast.Call)]
    suspicious = ("tool", "weather", "flight", "search", "lookup")
    return not any(any(word in ast.unparse(call.func).lower() for word in suspicious) for call in calls)


def make_finding(requirement: dict[str, Any], status: str, summary: str, detail: str, base_url: str = "") -> dict[str, Any]:
    artifact = requirement["artifacts"][0]
    actions = {
        "dynamic_react_loop": ["Parse Action từ phản hồi LLM.", "Tra tên Tool trong AVAILABLE_TOOLS.", "Đưa Observation trở lại prompt trước vòng tiếp theo."],
        "required_test_cases": ["Bổ sung đủ 5 case theo Codelab.", "Đảm bảo JSON hợp lệ rồi kiểm tra lại."],
        "max_iterations": ["Khai báo MAX_ITERATIONS.", "Dùng giới hạn này làm điều kiện dừng vòng ReAct."],
        "no_committed_secrets": ["Thu hồi key đã lộ.", "Xóa secret khỏi lịch sử Git và thêm .env vào .gitignore."],
    }.get(requirement["id"], [f"Hoàn thiện {artifact} theo Requirement Pack.", "Push commit mới rồi kiểm tra lại."])
    return {
        "requirement_id": requirement["id"],
        "requirement_title": requirement["title"],
        "status": status,
        "severity": requirement["severity"],
        "confidence": .96 if requirement["check_type"] == "deterministic" else .82,
        "summary": summary,
        "repo_evidence": [{"file": artifact, "detail": detail, "url": f"{base_url}{artifact}" if base_url else ""}],
        "impact": "Bài có thể không đạt tiêu chí trọng yếu hoặc mất điểm rubric." if status == "fail" else "",
        "recommended_action": actions,
    }


def check(requirement: dict[str, Any], files: dict[str, str], base_url: str = "") -> dict[str, Any]:
    checker = requirement["checker"]
    paths = requirement["artifacts"]
    content = "\n".join(files.get(path, "") for path in paths)

    if checker == "file_nonempty":
        passed = any(files.get(path, "").strip() for path in paths)
        return make_finding(requirement, "pass" if passed else "fail", "Artifact đã có." if passed else "Thiếu artifact bắt buộc.", f"{paths[0]} {'có nội dung' if passed else 'không tồn tại hoặc rỗng'}.", base_url)
    if checker == "json_test_cases":
        try:
            data = json.loads(files.get(paths[0], ""))
            passed = isinstance(data, list) and len(data) >= 5
        except json.JSONDecodeError:
            passed = False
        return make_finding(requirement, "pass" if passed else "fail", "Có đủ ít nhất 5 test cases." if passed else "Chưa có đủ 5 test cases hợp lệ.", "Đọc và đếm trực tiếp config/test_cases.json.", base_url)
    if checker == "max_iterations":
        passed = has_python_symbol(files, "MAX_ITERATIONS")
        return make_finding(requirement, "pass" if passed else "fail", "Đã có MAX_ITERATIONS." if passed else "Không tìm thấy MAX_ITERATIONS.", "Phân tích AST các file Python.", base_url)
    if checker == "no_secrets":
        has_env = ".env" in files
        matches = [path for path, value in files.items() if SECRET_RE.search(value)]
        passed = not has_env and not matches
        detail = "Không thấy .env hoặc chuỗi giống API key." if passed else f"Phát hiện ở: {', '.join(['.env'] if has_env else matches)}."
        return make_finding(requirement, "pass" if passed else "fail", "Không phát hiện secret bị commit." if passed else "Có nguy cơ lộ secret.", detail, base_url)
    if checker == "baseline_no_tools":
        result = baseline_has_no_tools(files.get("src/app.py", ""))
        status = "needs_review" if result is None else "pass" if result else "fail"
        return make_finding(requirement, status, "Baseline không gọi Tool." if result else "Cần xác minh bản chất Baseline.", "Phân tích lời gọi hàm trong function baseline.", base_url)
    if checker == "dynamic_react":
        lowered = content.lower()
        dynamic_markers = all(word in lowered for word in ("action", "observation", "available_tools"))
        hardcoded = bool(re.search(r"(?:weather|flight|search)\s*\(\s*[\"'][^\"']+[\"']\s*\)", lowered))
        passed = dynamic_markers and not hardcoded
        detail = "Có Action → registry → Observation động." if passed else "Không thấy đủ luồng Action → registry → Observation, hoặc Tool đang nhận tham số cố định."
        return make_finding(requirement, "pass" if passed else "fail", "ReAct loop chọn Tool động." if passed else "ReAct Agent chưa chọn Tool động.", detail, base_url)
    if checker == "tool_contract":
        markers = sum(word in content.lower() for word in ("input", "output", "error", "example", "safety"))
        status = "pass" if markers >= 4 else "needs_review"
        return make_finding(requirement, status, "Tool contract đủ dấu hiệu." if status == "pass" else "Tool contract cần xem xét.", f"Tìm thấy {markers}/5 mục contract trong src/tools.py.", base_url)
    if checker == "failed_trace":
        lowered = content.lower()
        passed = "fail" in lowered and any(word in lowered for word in ("root cause", "rca", "nguyên nhân"))
        return make_finding(requirement, "pass" if passed else "fail", "Có failed trace và RCA." if passed else "Chưa có đủ failed trace và RCA.", "Đối chiếu nội dung docs/trace_eval.md.", base_url)
    return make_finding(requirement, "needs_review", "Chưa có checker phù hợp.", "Cần người dùng kiểm tra thủ công.", base_url)


def analyze(assignment_id: str, repo_url: str, analysis_id: str | None = None) -> dict[str, Any]:
    if assignment_id not in assignments:
        raise HTTPException(status_code=409, detail="Requirement Pack chưa được xác nhận.")
    files, base_url = read_repo(repo_url)
    findings = [check(requirement, files, base_url) for requirement in assignments[assignment_id]]
    failures = [item for item in findings if item["status"] == "fail"]
    highest = max(failures, key=lambda item: SEVERITY_SCORE[item["severity"]] * item["confidence"], default=None)
    summary = {status: sum(item["status"] == status for item in findings) for status in ("pass", "fail", "needs_review")}
    result = {
        "analysis_id": analysis_id or uuid.uuid4().hex[:12],
        "assignment_id": assignment_id,
        "submission_repo_url": repo_url,
        "readiness": "not_ready" if failures else "ready",
        "highest_risk": highest,
        "summary": summary,
        "findings": findings,
    }
    analyses[result["analysis_id"]] = result
    return result


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/assignments/extract")
def extract_requirements(payload: ExtractRequest) -> dict[str, Any]:
    if not payload.codelab_text.strip() and not payload.codelab_files:
        raise HTTPException(status_code=422, detail="Hãy cung cấp ảnh, PDF hoặc nội dung Codelab.")
    requirements = [dict(item, enabled=True) for item in PACK["requirements"]]
    return {
        "assignment_id": PACK["assignment"]["id"],
        "title": PACK["assignment"]["title"],
        "requirements": requirements,
        "conflicts": [item["id"] for item in requirements if item.get("source_conflict")],
        "source_summary": {"codelab_files": len(payload.codelab_files), "github_repo": payload.assignment_repo_url},
    }


@app.post("/api/assignments/{assignment_id}/confirm")
def confirm_requirements(assignment_id: str, payload: ConfirmRequest) -> dict[str, Any]:
    if assignment_id != PACK["assignment"]["id"]:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài Lab.")
    known_ids = {item["id"] for item in PACK["requirements"]}
    requirements = [item for item in payload.requirements if item.get("id") in known_ids]
    if not requirements:
        raise HTTPException(status_code=422, detail="Requirement Pack không được để trống.")
    assignments[assignment_id] = requirements
    return {"assignment_id": assignment_id, "confirmed": len(requirements)}


@app.post("/api/analysis")
def create_analysis(payload: AnalysisRequest) -> dict[str, Any]:
    return analyze(payload.assignment_id, payload.submission_repo_url)


@app.get("/api/analysis/{analysis_id}")
def get_analysis(analysis_id: str) -> dict[str, Any]:
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả.")
    return analyses[analysis_id]


@app.post("/api/analysis/{analysis_id}/feedback")
def feedback(analysis_id: str, payload: FeedbackRequest) -> dict[str, str]:
    result = get_analysis(analysis_id)
    finding = next((item for item in result["findings"] if item["requirement_id"] == payload.requirement_id), None)
    if finding is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy finding.")
    finding["status"] = "needs_review"
    finding["feedback"] = payload.reason
    return {"status": "human_review_required"}


@app.post("/api/analysis/{analysis_id}/rerun")
def rerun(analysis_id: str) -> dict[str, Any]:
    previous = get_analysis(analysis_id)
    return analyze(previous["assignment_id"], previous["submission_repo_url"], analysis_id)

