from backend.main import PACK, check, demo_repo


def test_demo_finds_hardcoded_react_as_highest_risk_candidate() -> None:
    requirement = next(item for item in PACK["requirements"] if item["id"] == "dynamic_react_loop")
    finding = check(requirement, demo_repo())
    assert finding["status"] == "fail"
    assert "chọn Tool động" in finding["summary"]


if __name__ == "__main__":
    test_demo_finds_hardcoded_react_as_highest_risk_candidate()
    print("backend self-check passed")
