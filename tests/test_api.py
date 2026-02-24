import os

import pytest
from fastapi import HTTPException

from app.brain import DepartmentBrain
from app.security import FixedWindowRateLimiter, require_api_key


def test_brain_readiness_has_checks() -> None:
    brain = DepartmentBrain()
    checks = brain.readiness()
    assert set(checks.keys()) == {"data_loaded", "rag_enabled", "llm_configured"}
    assert checks["data_loaded"] is True


def test_structured_query_answer() -> None:
    brain = DepartmentBrain()
    answer, route, _ = brain.answer("Where is Dr. Asha Menon cabin?")
    assert route == "structured"
    assert "cabin a-201" in answer.lower()


def test_domain_guardrail() -> None:
    brain = DepartmentBrain()
    _, route, _ = brain.answer("What is bitcoin price?")
    assert route == "guardrail_domain"


def test_abuse_guardrail() -> None:
    brain = DepartmentBrain()
    _, route, _ = brain.answer("you are stupid")
    assert route == "guardrail_abuse"


def test_department_hod_note_answer() -> None:
    brain = DepartmentBrain()
    answer, route, sources = brain.answer("who is the head of the department")
    assert route == "structured"
    assert "head of department" in answer.lower() or "hod" in answer.lower()
    assert sources


def test_multi_faculty_subject_with_branch_and_semester_filter() -> None:
    brain = DepartmentBrain()
    answer, route, _ = brain.answer("Who teaches Machine Learning for DS semester 8?")
    assert route == "structured"
    assert "dr. nitin deshmukh" in answer.lower()
    assert "semester 8" in answer.lower()


def test_multi_faculty_subject_without_filter_lists_multiple() -> None:
    brain = DepartmentBrain()
    answer, route, _ = brain.answer("Who teaches Database Systems?")
    assert route == "structured"
    assert "dr. neha sharma" in answer.lower()
    assert "prof. kavita joshi" in answer.lower()


def test_rate_limiter_blocks_after_limit() -> None:
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=60)
    assert limiter.allow("1.2.3.4") is True
    assert limiter.allow("1.2.3.4") is False


def test_api_key_auth_passes_and_fails() -> None:
    os.environ["SERVICE_API_KEY"] = "secret-key"
    try:
        require_api_key("secret-key")
        with pytest.raises(HTTPException):
            require_api_key("wrong-key")
    finally:
        os.environ.pop("SERVICE_API_KEY", None)
