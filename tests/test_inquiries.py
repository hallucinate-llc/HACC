import sys
import time
from pathlib import Path
from typing import Dict, List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_ROOT))

from mediator import strings
from mediator.inquiries import Inquiries, _normalize_question_cached


class DummyState:
    def __init__(self):
        self.inquiries: List[Dict[str, object]] = []
        self.complaint = "apartment damage"


class DummyMediator:
    def __init__(self):
        self.state = DummyState()
        self.queries: List[str] = []

    def query_backend(self, prompt: str) -> str:
        self.queries.append(prompt)
        return "1) What happened?\n2) Who was involved?"

    def build_inquiry_gap_context(self) -> Dict[str, List[str]]:
        return {"priority_terms": ["eviction"]}


class ErrorMediator(DummyMediator):
    def build_inquiry_gap_context(self):
        raise RuntimeError("boom")


@pytest.fixture
def inquiries() -> Inquiries:
    mediator = DummyMediator()
    return Inquiries(mediator)


def test_normalize_question_cached_and_performance():
    sample = "  1. Is the hot water working?  "
    normalized = _normalize_question_cached(sample)
    assert normalized == "is the hot water working"
    start = time.perf_counter()
    for _ in range(500):
        assert _normalize_question_cached(sample) == normalized
    assert time.perf_counter() - start < 0.3


def test_register_answer_and_is_complete(inquiries: Inquiries):
    inquiries.register("What is the notice?")
    assert inquiries.get_next()["question"].startswith("What is")
    inquiries.answer("It was posted.")
    assert inquiries._find_unanswered(inquiries._state_inquiries()) is None
    assert inquiries.is_complete()


def test_generate_builds_questions_and_indexes(inquiries: Inquiries):
    mediator = inquiries.m
    mediator.state.inquiries = []
    inquiries.generate()
    assert len(mediator.state.inquiries) == 2
    assert mediator.queries
    index = inquiries._index_for(mediator.state.inquiries)
    assert index
    first_question = mediator.state.inquiries[0]
    assert first_question["question"].endswith("?")


def test_merge_legal_questions_updates_priorities_and_dependency_flags(inquiries: Inquiries):
    mediator = inquiries.m
    mediator.state.inquiries = [
        {"question": "What is the notice?", "alternative_questions": [], "answer": None, "priority": "medium"}
    ]
    questions = [
        {"question": "What is the notice?", "priority": "critical", "support_gap_targeted": True},
        {"question": "How long was the notice?", "priority": "high", "provenance": {"source": "doc"}},
        {"question": "Will eviction happen?", "priority": "low"},
    ]
    merged = inquiries.merge_legal_questions(questions)
    assert merged == 3
    updated = mediator.state.inquiries[0]
    assert updated["priority"] == "critical"
    assert updated["support_gap_targeted"]
    assert any(item["question"].startswith("Will eviction") for item in mediator.state.inquiries)


def test_explain_inquiry_with_reasons():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    inquiry = {
        "question": "Is the eviction notice valid?",
        "priority": "High",
        "support_gap_targeted": True,
        "dependency_gap_targeted": False,
        "source": "legal_question",
        "claim_type": "housing",
        "element": "notice",
    }
    explanation = inquiries.explain_inquiry(inquiry)
    assert "targets a missing claim element" in explanation["reasons"][0]
    assert explanation["priority"] == "High"


def test_merge_handles_invalid_entries_and_alternatives(inquiries: Inquiries):
    mediator = inquiries.m
    mediator.state.inquiries = []
    inquiries.register(" 1) Can we negotiate? ")
    inquiries.register("Can we negotiate?")
    assert len(mediator.state.inquiries) == 1
    assert mediator.state.inquiries[0]["alternative_questions"]


def test_index_and_state_helpers(inquiries: Inquiries):
    mediator = inquiries.m
    mediator.state.inquiries = []
    signature_before = inquiries._index_key(mediator.state.inquiries)
    assert isinstance(signature_before, tuple)
    inquiries.register("How should we respond?")
    signature_after = inquiries._index_signature
    assert signature_after[0] == id(mediator.state.inquiries)
    assert signature_after[1] == len(mediator.state.inquiries)


def test_priority_rank_default():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    assert inquiries._priority_rank("unexpected") == 2
    assert inquiries._priority_rank(None) == 2


def test_extract_questions_fallback_and_clean():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    block = "Lawyer: Q: Why did you move?\nPlaintiff: Because...\nQ: What happened?"
    questions = inquiries._extract_questions(block)
    assert "What happened?" in questions
    assert inquiries._clean_question("   1)  Is anyone hurt?  ") == "Is anyone hurt?"


def test_build_gap_context_handles_missing_builder(monkeypatch):
    mediator = ErrorMediator()
    inquiries = Inquiries(mediator)
    assert inquiries._build_gap_context() == {}
    mediator.state.inquiries = []
    definitions = inquiries._index_for(mediator.state.inquiries)
    assert definitions == {}


def test_answer_no_unanswered_safe(inquiries: Inquiries):
    inquiries.m.state.inquiries = []
    inquiries.answer("nothing")
    assert inquiries.m.state.inquiries == []

