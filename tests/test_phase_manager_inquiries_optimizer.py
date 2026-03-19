"""Comprehensive tests for phase manager and inquiry workflows."""
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

from complaint_phases.phase_manager import (
    ComplaintPhase,
    PhaseManager,
    _utc_now_isoformat,
)
from mediator import strings
from mediator.inquiries import Inquiries, _normalize_question_cached

try:
    import pytest_benchmark  # noqa: F401

    _HAS_BENCHMARK = True
except Exception:  # pragma: no cover - optional
    _HAS_BENCHMARK = False


if not _HAS_BENCHMARK:
    @pytest.fixture
    def benchmark():
        def _bench(func, *args, **kwargs):
            _ = time.perf_counter()
            result = func(*args, **kwargs)
            _ = time.perf_counter() - _
            return result

        return _bench


class DummyState(SimpleNamespace):
    def __init__(self, complaint: str = "Complaint"):
        super().__init__(inquiries=[], complaint=complaint)


class DummyMediator:
    def __init__(self):
        self.state = DummyState()
        self.query_calls: List[str] = []

    def query_backend(self, prompt: str):
        self.query_calls.append(prompt)
        return "What happened?\nWho did it?"  # two simple questions

    def build_inquiry_gap_context(self):
        return {"priority_terms": ["critical", "dependency"]}


class FaultyGapMediator(DummyMediator):
    def build_inquiry_gap_context(self):
        raise RuntimeError("boom")


def _ready_case_file() -> Dict[str, Any]:
    sections = {
        name: {"status": "present", "missing_items": []}
        for name in (
            "chronology",
            "actors",
            "conduct",
            "harm",
            "remedy",
            "proof_leads",
            "claim_elements",
        )
    }
    return {
        "intake_sections": sections,
        "candidate_claims": [
            {
                "claim_type": "eligibility",
                "confidence": 0.9,
                "ambiguity_flags": [],
            }
        ],
        "proof_leads": ["lead"],
        "canonical_facts": ["fact"],
        "summary_snapshots": [],
        "contradiction_queue": [],
        "complainant_summary_confirmation": {"confirmed": True},
    }


def _ready_evidence_data() -> Dict[str, Any]:
    return {
        "alignment_evidence_tasks": [
            {
                "claim_type": "eligibility",
                "claim_element_id": "elem",
                "support_status": "unsupported",
                "resolution_status": "settled",
                "action": "fill_evidence_gaps",
                "temporal_rule_status": "partial",
                "temporal_rule_blocking_reasons": ["details needed"],
                "recommended_next_step": "collect_support",
            }
        ],
        "claim_support_packets": {
            "eligibility": {
                "claim_type": "eligibility",
                "elements": [
                    {
                        "element_id": "elem",
                        "support_status": "unsupported",
                        "parse_quality_flags": [],
                        "recommended_next_step": "collect_support",
                        "contradiction_count": 1,
                    }
                ],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 1,
        "claim_support_recommended_actions": ["collect_support"],
        "claim_support_unresolved_without_review_path_count": 1,
    }


def _complete_evidence_state() -> Dict[str, Any]:
    return {
        "alignment_evidence_tasks": [],
        "claim_support_packets": {
            "eligibility": {
                "claim_type": "eligibility",
                "elements": [
                    {
                        "element_id": "elem",
                        "support_status": "supported",
                        "parse_quality_flags": [],
                        "recommended_next_step": "collect_support",
                        "contradiction_count": 0,
                    }
                ],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
        "claim_support_recommended_actions": [],
        "claim_support_unsupported_count": 0,
    }


@pytest.fixture
def phase_manager() -> PhaseManager:
    return PhaseManager()


@pytest.fixture
def inquiries(phase_manager) -> Inquiries:
    return Inquiries(DummyMediator())


def test_utc_now_isoformat_has_offset():
    value = _utc_now_isoformat()
    assert "T" in value
    assert value.endswith("+00:00") or value.endswith("Z")


def test_phase_manager_serialization_round_trip(phase_manager):
    phase_manager.phase_history.append(
        {"from_phase": "intake", "to_phase": "evidence", "timestamp": "ts", "iteration": 1}
    )
    phase_manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    data = phase_manager.to_dict()
    restored = PhaseManager.from_dict(data)
    assert restored.current_phase == phase_manager.current_phase
    assert restored.phase_history == phase_manager.phase_history
    assert restored.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] is True


def test_extract_gap_and_contradiction_helpers(phase_manager):
    data = {
        "intake_gap_types": [" missing_timeline", "missing_timeline"],
        "current_gaps": [{"type": "missing_actor"}, "invalid"],
        "intake_contradictions": {"candidates": [{"id": 1}, "bad"]},
    }
    gap_types = phase_manager._extract_intake_gap_types(data)
    assert gap_types == ["missing_timeline", "missing_actor"]
    contradictions = phase_manager._extract_intake_contradictions(data)
    assert contradictions == [{"id": 1}]


def test_active_and_resolution_detects_blocking():
    manager = PhaseManager()
    queue = [
        {"status": "open"},
        {"status": "resolved"},
        {"current_resolution_status": "manual_review_pending", "severity": "blocking"},
    ]
    active = manager._active_intake_contradictions(queue)
    assert len(active) == 2
    assert not manager._is_intake_contradiction_resolved(active[0])
    assert manager._is_intake_contradiction_resolved_or_escalated(queue[2])


def test_section_blockers_and_readiness_integration(phase_manager):
    case_file = _ready_case_file()
    intake_state = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 0,
        "denoising_converged": True,
        "intake_case_file": case_file,
        "current_gaps": [],
    }
    readiness = phase_manager._build_intake_readiness(intake_state)
    assert readiness["intake_ready"] is True
    blockers = list(readiness.get("blockers") or readiness.get("intake_readiness_blockers") or [])
    assert all(not blocker.startswith("missing_") for blocker in blockers)
    phase_manager.phase_data[ComplaintPhase.INTAKE] = {**intake_state, **readiness}
    phase_manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    assert phase_manager.phase_data[ComplaintPhase.INTAKE].get("intake_ready") is True


def test_evidence_summary_and_next_packet_actions(phase_manager):
    data = _ready_evidence_data()
    summary = phase_manager._build_evidence_packet_summary(data)
    assert summary["claim_support_packet_count"] == 1
    assert summary["evidence_completion_ready"] is False
    packets = data["claim_support_packets"]
    action = phase_manager._get_next_packet_evidence_action(packets, data)
    assert action["action"] == "collect_support"
    assert action["support_status"] == "unsupported"


def test_alignment_tasks_and_drift_action(phase_manager):
    data = _ready_evidence_data()
    actionable = phase_manager._get_actionable_alignment_tasks(data)
    assert actionable
    data["alignment_promotion_drift_summary"] = {
        "drift_flag": True,
        "promoted_count": 1,
        "pending_conversion_count": 1,
    }
    data["alignment_task_update_history"] = [
        {
            "claim_type": "eligibility",
            "claim_element_id": "elem",
            "resolution_status": "promoted_to_document",
            "task_id": "t1",
            "evidence_sequence": 5,
        }
    ]
    drift_action = phase_manager._get_alignment_promotion_drift_action(data)
    assert drift_action and drift_action["action"] == "validate_promoted_support"
    assert drift_action.get("claim_element_id") == "elem"


def test_phase_transitions_and_completion_checks(phase_manager):
    assert phase_manager.get_current_phase() == ComplaintPhase.INTAKE
    assert not phase_manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    assert not phase_manager._can_advance_to(ComplaintPhase.FORMALIZATION)
    # satisfy intake readiness
    phase_manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    phase_manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    phase_manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    phase_manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    phase_manager.update_phase_data(ComplaintPhase.INTAKE, "intake_case_file", _ready_case_file())
    assert phase_manager._is_intake_complete()
    assert phase_manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    phase_manager.phase_data[ComplaintPhase.EVIDENCE] = _complete_evidence_state()
    assert phase_manager._is_evidence_complete()
    phase_manager.current_phase = ComplaintPhase.FORMALIZATION
    phase_manager.phase_data[ComplaintPhase.FORMALIZATION] = {
        "legal_graph": {},
        "matching_complete": True,
        "formal_complaint": "complaint",
    }
    assert phase_manager._is_formalization_complete()


def test_phase_data_updates_metrics(phase_manager):
    phase_manager.update_phase_data(ComplaintPhase.EVIDENCE, "foo", "bar")
    assert phase_manager.get_phase_data(ComplaintPhase.EVIDENCE, "foo") == "bar"
    assert phase_manager.has_phase_data_key(ComplaintPhase.EVIDENCE, "foo")
    phase_manager.update_phase_data(ComplaintPhase.EVIDENCE, "baz", 1)
    phase_manager.update_phase_data(ComplaintPhase.FORMALIZATION, "meta", True)
    assert phase_manager.phase_data_coverage() == 2 / 3


def test_iteration_tracking_and_convergence(phase_manager):
    for loss in (0.5, 0.51, 0.5, 0.49, 0.5, 0.48):
        phase_manager.record_iteration(loss, {"phase": phase_manager.current_phase.value})
    assert phase_manager.total_iterations() == 6
    assert phase_manager.iterations_in_phase(ComplaintPhase.INTAKE) == 6
    assert 0.48 <= phase_manager.minimum_loss() <= 0.5
    assert phase_manager.average_loss() > 0
    assert phase_manager.has_converged(window=5, threshold=0.05)


def test_next_actions_per_phase(phase_manager):
    action = phase_manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    phase_manager.phase_data[ComplaintPhase.INTAKE].update(
        {
            "knowledge_graph": True,
            "dependency_graph": True,
            "current_gaps": [],
            "remaining_gaps": 0,
            "denoising_converged": True,
            "intake_case_file": _ready_case_file(),
        }
    )
    phase_manager.iteration_count = 25
    action = phase_manager._get_intake_action()
    assert action["action"] == "complete_intake"
    phase_manager.current_phase = ComplaintPhase.EVIDENCE
    phase_manager.phase_data[ComplaintPhase.EVIDENCE] = {"evidence_count": 0}
    assert phase_manager.get_next_action()["action"] == "gather_evidence"
    phase_manager.phase_data[ComplaintPhase.EVIDENCE] = _complete_evidence_state()
    assert phase_manager._get_evidence_action()["action"] == "complete_evidence"
    phase_manager.current_phase = ComplaintPhase.FORMALIZATION
    action = phase_manager._get_formalization_action()
    assert action["action"] == "build_legal_graph"
    phase_manager.phase_data[ComplaintPhase.FORMALIZATION].update(
        {"legal_graph": {"nodes": []}, "matching_complete": True}
    )
    assert phase_manager._get_formalization_action()["action"] == "generate_formal_complaint"
    phase_manager.phase_data[ComplaintPhase.FORMALIZATION]["formal_complaint"] = "doc"
    assert phase_manager._get_formalization_action()["action"] == "complete_formalization"


def test_history_statistics(phase_manager):
    phase_manager.phase_history.extend(
        [
            {"to_phase": "evidence"},
            {"to_phase": "formalization"},
            {"to_phase": "evidence"},
        ]
    )
    assert phase_manager.total_phase_transitions() == 3
    assert phase_manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 2
    freq = phase_manager.phase_transition_frequency()
    assert freq["evidence"] == 2
    assert phase_manager.most_visited_phase() == "evidence"


def test_evidence_summary_performance(phase_manager, benchmark):
    data = _ready_evidence_data()
    result = benchmark(lambda: phase_manager._build_evidence_packet_summary(data))
    assert isinstance(result, dict)


def test_intake_readiness_performance(phase_manager, benchmark):
    data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 0,
        "denoising_converged": True,
        "intake_case_file": _ready_case_file(),
        "current_gaps": [],
    }
    result = benchmark(lambda: phase_manager._build_intake_readiness(data))
    assert result["intake_ready"]


def test_normalize_question_cache_and_same():
    normalized = _normalize_question_cached("  What happened???")
    assert normalized == "what happened"
    assert Inquiries(DummyMediator()).same_question("?What happened", "what happened??")


def test_inquiries_indexing_and_next_selection():
    mediator = DummyMediator()
    mediator.state.inquiries = [
        {"question": "First", "priority": "high"},
        {"question": "Second", "priority": "low", "support_gap_targeted": True},
    ]
    iq = Inquiries(mediator)
    assert iq.get_next()["question"] == "Second"
    assert iq._find_unanswered(mediator.state.inquiries) == mediator.state.inquiries[0]
    mediator.state.inquiries[0]["answer"] = "done"
    assert iq._find_unanswered(mediator.state.inquiries) == mediator.state.inquiries[1]


def test_answer_and_completion():
    mediator = DummyMediator()
    mediator.state.inquiries = [{"question": "Q", "priority": "medium"}]
    iq = Inquiries(mediator)
    iq.answer("A")
    assert mediator.state.inquiries[0]["answer"] == "A"
    assert iq.is_complete()


def test_register_and_merge_questions(monkeypatch):
    mediator = DummyMediator()
    mediator.state.inquiries = []
    iq = Inquiries(mediator)
    iq.register("First?")
    assert mediator.state.inquiries[0]["question"] == "First?"
    merged = iq.merge_legal_questions(
        [
            {"question": "FIRST?", "priority": "critical", "support_gap_targeted": True}
        ]
    )
    assert merged == 1
    assert mediator.state.inquiries[0]["priority"] == "critical"
    assert mediator.state.inquiries[0]["support_gap_targeted"]


def test_merge_legal_questions_handles_non_dicts_and_priority(monkeypatch):
    mediator = DummyMediator()
    mediator.state.inquiries = []
    iq = Inquiries(mediator)
    iq.register("A question?")
    questions = [None, {"question": "A question?", "priority": "low"}]
    merged = iq.merge_legal_questions(questions)
    assert merged == 1


def test_generate_questions_flow(monkeypatch):
    mediator = DummyMediator()
    mediator.state.inquiries = []
    iq = Inquiries(mediator)
    monkeypatch.setitem(strings.model_prompts, "generate_questions", "{complaint}\n?")
    iq.generate()
    assert mediator.state.inquiries
    assert mediator.query_calls


def test_generate_skips_on_empty_template(monkeypatch):
    mediator = DummyMediator()
    mediator.state.inquiries = []
    iq = Inquiries(mediator)
    monkeypatch.setitem(strings.model_prompts, "generate_questions", "")
    iq.generate()
    assert not mediator.state.inquiries


def test_explain_inquiry_details():
    mediator = DummyMediator()
    iq = Inquiries(mediator)
    inquiry = {
        "question": "Q",
        "priority": "high",
        "support_gap_targeted": True,
        "dependency_gap_targeted": True,
        "source": "legal_question",
        "claim_type": "eligibility",
        "element": "actor",
    }
    explanation = iq.explain_inquiry(inquiry)
    assert "targets a missing" in explanation["summary"]
    assert explanation["support_gap_targeted"]


def test_clean_and_extract_questions():
    mediator = DummyMediator()
    iq = Inquiries(mediator)
    text = "1) Who?\n2) What happened??\nNo question here"
    questions = iq._extract_questions(text)
    assert "Who" in questions[0]
    assert any("What happened" in q for q in questions)
    assert iq._trim_question_prefix("1. Question") == "Question"
    assert iq._clean_question("  1) Hello ?  ") == "Hello ?"


def test_index_cache_and_gap_context(monkeypatch):
    mediator = DummyMediator()
    iq = Inquiries(mediator)
    mediator.state.inquiries = [{"question": "Q"}]
    first_index = iq._index_for(mediator.state.inquiries)
    mediator.state.inquiries.append({"question": "New"})
    second_index = iq._index_for(mediator.state.inquiries)
    assert first_index is not second_index
    assert iq._build_gap_context() == {"priority_terms": ["critical", "dependency"]}
    faulty = Inquiries(FaultyGapMediator())
    assert faulty._build_gap_context() == {}


def test_priority_ranking_and_normalization():
    mediator = DummyMediator()
    iq = Inquiries(mediator)
    assert iq._priority_rank("critical") == 0
    assert iq._priority_rank("unknown") == 2
    assert iq._normalize_question("A?  ") == "a"
