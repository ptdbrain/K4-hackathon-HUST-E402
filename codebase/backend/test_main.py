import io
import zipfile
from unittest.mock import patch

from backend.main import PACK, analyze, assignments, check, demo_repo, extract_with_ai, read_zip_files
from backend.provider import generate_json, parse_json


def test_demo_finds_hardcoded_react_as_highest_risk_candidate() -> None:
    requirement = next(item for item in PACK["requirements"] if item["id"] == "dynamic_react_loop")
    finding = check(requirement, demo_repo())
    assert finding["status"] == "fail"
    assert "chọn Tool động" in finding["summary"]


def test_comments_do_not_count_as_dynamic_react() -> None:
    requirement = next(item for item in PACK["requirements"] if item["id"] == "dynamic_react_loop")
    finding = check(requirement, {"src/app.py": "# Action Observation AVAILABLE_TOOLS"})
    assert finding["status"] == "fail"


def test_missing_artifact_has_no_broken_github_link() -> None:
    requirement = next(item for item in PACK["requirements"] if item["id"] == "required_test_cases")
    finding = check(requirement, {}, "https://github.com/team/repo/blob/main/")
    assert finding["repo_evidence"][0]["file"] == "config/test_cases.json"
    assert finding["repo_evidence"][0]["url"] == ""


def test_archive_reader_keeps_supported_files() -> None:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("repo-main/eval/", "")
        zipped.writestr("repo-main/config/test_cases.json", "[]")
        zipped.writestr("repo-main/image.png", "ignored")
    assert read_zip_files(archive.getvalue()) == {"eval/": "", "config/test_cases.json": "[]", "image.png": "\0"}


def test_directory_artifact_counts_as_present() -> None:
    requirement = {
        "id": "required_eval",
        "title": "Có thư mục eval",
        "category": "artifact",
        "severity": "high",
        "artifacts": ["eval/"],
        "checker": "file_nonempty",
        "check_type": "deterministic",
    }
    finding = check(requirement, {"eval/": ""}, "https://github.com/team/repo/blob/main/")
    assert finding["status"] == "pass"
    assert "/tree/main/eval" in finding["repo_evidence"][0]["url"]


def test_analysis_reports_run_time() -> None:
    assignment_id = PACK["assignment"]["id"]
    assignments[assignment_id] = PACK["requirements"]
    assert analyze(assignment_id, "demo://not-ready")["checked_at"]


def test_missing_key_is_labeled_offline_mock() -> None:
    with patch.dict("os.environ", {"AI_PROVIDER": "GOOGLE", "AI_MODEL": "test-model"}, clear=True):
        selected, trace = extract_with_ai("five test cases")
    assert selected is None
    assert trace["mode"] == "offline_mock"


def test_all_ai_providers_parse_json() -> None:
    cases = {
        "OPENAI": ({"OPENAI_API_KEY": "test"}, {"choices": [{"message": {"content": '{"ok": true}'}}]}),
        "GOOGLE": ({"GOOGLE_API_KEY": "test"}, {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]}),
        "OPENROUTER": ({"OPENROUTER_API_KEY": "test"}, {"choices": [{"message": {"content": '{"ok": true}'}}]}),
        "OLLAMA": ({}, {"message": {"content": '{"ok": true}'}}),
    }
    for provider, (environment, response) in cases.items():
        with patch.dict("os.environ", {"AI_PROVIDER": provider, "AI_MODEL": "test-model", **environment}, clear=True):
            with patch("backend.provider._post_json", return_value=response):
                result, actual_provider, model = generate_json("prompt", {"type": "object"})
        assert result == {"ok": True}
        assert (actual_provider, model) == (provider, "test-model")


def test_provider_parses_fenced_json() -> None:
    assert parse_json('Kết quả:\n```json\n{"ok": true}\n```') == {"ok": True}


def test_ai_can_build_pack_for_another_lab() -> None:
    requirement = {
        "id": "required_readme",
        "title": "Có README",
        "category": "artifact",
        "severity": "high",
        "artifacts": ["README.md"],
        "checker": "file_nonempty",
        "expected": [],
        "min_count": 0,
        "symbol": "",
        "source_locations": ["README · Submission"],
        "source_conflict": False,
    }
    requirements_data = [{**requirement, "id": f"required_readme_{index}"} for index in range(3)] + [{"id": "invalid"}]
    requirements_data[0]["id"] = "Required-README-0"
    with patch("backend.main.generate_json", return_value=({"requirements": requirements_data}, "OLLAMA", "test-model")):
        requirements, trace = extract_with_ai("Nộp README", {"README.md": "Rubric"})
    assert len(requirements) == 3
    assert requirements[0]["id"] == "required_readme_0"
    assert requirements[0]["checker"] == "file_nonempty"
    assert trace["provider"] == "OLLAMA"
    assert trace["rejected_requirements"] == 1


def test_ai_makes_duplicate_ids_unique() -> None:
    requirement = {
        "id": "artifact",
        "title": "Artifact bắt buộc",
        "category": "artifact",
        "severity": "high",
        "artifacts": ["README.md"],
        "checker": "file_nonempty",
        "expected": [],
        "min_count": 0,
        "symbol": "",
        "source_locations": ["Codelab"],
        "source_conflict": False,
    }
    with patch("backend.main.generate_json", return_value=({"requirements": [requirement] * 3}, "OLLAMA", "test-model")):
        requirements, _ = extract_with_ai("Nộp README")
    assert [item["id"] for item in requirements] == ["artifact", "artifact_2", "artifact_3"]


def test_ai_rejects_invalid_checker_arguments() -> None:
    requirement = {
        "id": "invalid_symbol",
        "title": "Requirement không hợp lệ",
        "category": "implementation",
        "severity": "high",
        "artifacts": ["src/app.py"],
        "checker": "python_symbol",
        "expected": [],
        "min_count": 0,
        "symbol": "==",
        "source_locations": ["Codelab"],
        "source_conflict": False,
    }
    with patch("backend.main.generate_json", return_value=({"requirements": [requirement] * 3}, "OLLAMA", "test-model")):
        requirements, trace = extract_with_ai("Nộp code")
    assert requirements is None
    assert "symbol Python hợp lệ" in trace["reason"]


if __name__ == "__main__":
    test_demo_finds_hardcoded_react_as_highest_risk_candidate()
    test_comments_do_not_count_as_dynamic_react()
    test_missing_artifact_has_no_broken_github_link()
    test_archive_reader_keeps_supported_files()
    test_directory_artifact_counts_as_present()
    test_analysis_reports_run_time()
    test_missing_key_is_labeled_offline_mock()
    test_all_ai_providers_parse_json()
    test_provider_parses_fenced_json()
    test_ai_can_build_pack_for_another_lab()
    test_ai_makes_duplicate_ids_unique()
    test_ai_rejects_invalid_checker_arguments()
    print("backend self-check passed")
