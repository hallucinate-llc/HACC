import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from mediator import strings
from mediator.inquiries import Inquiries, _normalize_question_cached


class SimpleMediator:
    def __init__(self):
        self.state = SimpleNamespace(inquiries=[], complaint="Complaint text")
        self.queries: List[str] = []

    def query_backend(self, prompt: str) -> str:
        self.queries.append(prompt)
        return "What happened?\nWho did it?"

    def build_inquiry_gap_context(self) -> Dict[str, Any]:
        return {"priority_terms": ["dependency", "critical"]}


class FaultyMediator(SimpleMediator):
    def build_inquiry_gap_context(self) -> Dict[str, Any]:
        raise RuntimeError("failure")


@pytest.fixture
def mediator() -> SimpleMediator:
    return SimpleMediator()


@pytest.fixture
def inquiries(mediator: SimpleMediator) -> Inquiries:
    return Inquiries(mediator)


def test_normalize_question_cached_strips_noise():
    normalized = _normalize_question_cached("1. WHAT happened??")
    assert normalized == "what happened"
    assert _normalize_question_cached("1. What happened??") == "what happened"


def test_register_and_index_avoid_duplicates(inquiries: Inquiries, mediator: SimpleMediator):
    mediator.state.inquiries.clear()
    inquiries.register("Who is responsible?")
    inquiries.register("Who is responsible?")
    assert len(mediator.state.inquiries) == 1
    assert mediator.state.inquiries[0]["alternative_questions"]
    index = inquiries._index_for(mediator.state.inquiries)
    assert index


def test_get_next_prioritizes_gaps_and_priority(inquiries: Inquiries, mediator: SimpleMediator):
    mediator.state.inquiries[:] = [
        {"question": "Why?", "priority": "low", "support_gap_targeted": False, "answer": None},
        {"question": "What?", "priority": "high", "support_gap_targeted": True},
    ]
    current = inquiries.get_next()
    assert current["question"] == "What?"
    inquiries.answer("Because")
    assert mediator.state.inquiries[1]["answer"] == "Because"


def test_generate_population_and_template(monkeypatch, inquiries: Inquiries, mediator: SimpleMediator):
    mediator.state.inquiries.clear()
    inquiries.generate()
    assert mediator.state.inquiries
    assert len(mediator.queries) == 1
    # Regenerate when template missing should be safe
    monkeypatch.setitem(strings.model_prompts, "generate_questions", None)
    previous = len(mediator.state.inquiries)
    inquiries.generate()
    assert len(mediator.state.inquiries) == previous


def test_merge_legal_questions_updates_existing(inquiries: Inquiries, mediator: SimpleMediator):
    mediator.state.inquiries[:] = [{"question": "What happened?", "priority": "medium"}]
    merged = inquiries.merge_legal_questions([
        {"question": "What happened?", "priority": "high", "support_gap_targeted": True, "claim_type": "eligibility", "element": "required", "provenance": {"source": "doc"}},
    ])
    assert merged == 1
    entry = mediator.state.inquiries[0]
    assert entry["priority"] == "high"
    assert entry["support_gap_targeted"] is True
    assert entry.get("claim_type") == "eligibility"
    assert entry.get("element") == "required"


def test_explain_inquiry_returns_reason_list(inquiries: Inquiries):
    explanation = inquiries.explain_inquiry({
        "question": "What happened?",
        "priority": "critical",
        "support_gap_targeted": True,
    })
    assert "critical" in explanation["priority"].lower()
    assert explanation["support_gap_targeted"]
    assert explanation["reasons"]


def test_state_inquiries_none_and_is_complete(monkeypatch):
    mediator = SimpleMediator()
    mediator.state = None
    inquiries = Inquiries(mediator)
    assert inquiries.get_next() is None
    assert inquiries.is_complete()


def test_build_gap_context_handles_builder_errors():
    mediator = FaultyMediator()
    inquiries = Inquiries(mediator)
    assert inquiries._build_gap_context() == {}


def test_extract_and_clean_question_variants(inquiries: Inquiries):
    text = "1. First?\nSecond question?" + "\nNo question"
    questions = inquiries._extract_questions(text)
    assert any(q.startswith("First") for q in questions)
    trimmed = Inquiries._trim_question_prefix("1. Already? ")
    assert trimmed == "Already?"
    assert Inquiries._clean_question("  2. Later?  ") == "Later?"


def test_same_question_and_priority_rank(monkeypatch, inquiries: Inquiries):
    assert inquiries.same_question("Why?", "why")
    assert not inquiries.same_question("Why?", None)
    assert inquiries._priority_rank("critical") == 0
    assert inquiries._priority_rank("unknown") == 2


def test_index_rebuilds_when_inquiries_change(inquiries: Inquiries, mediator: SimpleMediator):
    mediator.state.inquiries[:] = [
        {"question": "What?"}
    ]
    first = inquiries._index_for(mediator.state.inquiries)
    mediator.state.inquiries.append({"question": "Why?"})
    second = inquiries._index_for(mediator.state.inquiries)
    assert len(second) == 2
    assert second != first


def test_normalize_question_performance():
    start = time.perf_counter()
    for _ in range(1000):
        _normalize_question_cached("1. What happened?")
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1
