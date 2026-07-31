import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "codebase"))

from backend.main import PACK, check  # noqa: E402


def main() -> None:
    cases = json.loads((ROOT / "eval/golden-set.json").read_text())
    requirements = {item["id"]: item for item in PACK["requirements"]}
    results = []
    for case in cases:
        secret_fixture = "api_" + "key = \"" + "x" * 20 + "\""
        files = {path: content.replace("__SECRET__", secret_fixture) for path, content in case["files"].items()}
        actual = check(requirements[case["requirement_id"]], files)["status"]
        results.append({
            "id": case["id"],
            "expected": case["expected_status"],
            "actual": actual,
            "pass": actual == case["expected_status"],
        })
    passed = sum(item["pass"] for item in results)
    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "cases": len(results),
        "passed": passed,
        "pass_rate": round(100 * passed / len(results), 1),
        "results": results,
    }
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "eval/latest-results.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"{passed}/{len(results)} ({output['pass_rate']}%) -> {target}")


if __name__ == "__main__":
    main()
