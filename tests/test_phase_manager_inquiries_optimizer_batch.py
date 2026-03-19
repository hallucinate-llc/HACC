import sys
import time
from datetime import datetime
from pathlib import Path

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
from mediator.inquiries import Inquiries, _normalize_question_cached

try:
    import pytest_benchmark  # noqa: F401

    _HAS_BENCHMARK = True
except ImportError:  # pragma: no cover - fixture fallback
    _HAS_BENCHMARK = False


if not _HAS_BENCHMARK:
    @pytest.fixture
    def benchmark():
        def _bench(func, *args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            _ = time.perf_counter() - start
            return result

        return _bench


class DummyState:
    def __init__(self):
        self.inquiries = []
        self.complaint = "My complaint needs context."


class DummyMediator:
    def __init__(self):
        self.state = DummyState()
        self.backend_calls = []

    def query_backend(self, prompt: str) -> str:
        self.backend_calls.append(prompt)
        return "What happened?\nWhat else should we know?"

    def build_inquiry_gap_context(self) -> dict:
        return {"priority_terms": ["support", "dependency"]}


class ExplodingMediator(DummyMediator):
    def build_inquiry_gap_context(self) -> dict:
        raise RuntimeError("synthetic failure")


def _complete_intake(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    manager.update_phase_data(
        ComplaintPhase.INTAKE,
        "intake_case_file",
        {
            "intake_sections": {
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
            },
            "candidate_claims": [
                {"claim_type": "discrimination", "confidence": 0.8, "ambiguity_flags": []}
            ],
            "canonical_facts": [{"fact": "exists"}],
            "proof_leads": ["lead"],
            "summary_snapshots": [],
            "contradiction_queue": [],
            "complainant_summary_confirmation": {"confirmed": True},
        },
    )
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", [])


def _complete_evidence(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.1)


def test_utc_now_is_iso_and_parseable():
    timestamp = _utc_now_isoformat()
    assert timestamp.endswith("+00:00")
    assert datetime.fromisoformat(timestamp)


def test_phase_manager_gap_and_contradiction_extractors():
    manager = PhaseManager()
    data = {
        "intake_gap_types": [" missing_timeline ", None, "missing_timeline"],
        "current_gaps": [{"type": "missing_support"}, {"type": None}],
        "intake_contradictions": {
            "candidates": [
                {"status": "resolved", "severity": "blocking"},
                {"status": "awaiting_testimony", "severity": "blocking"},
            ]
        },
    }

    gap_types = manager._extract_intake_gap_types(data)
    assert gap_types == ["missing_timeline", "missing_support"]

    contradictions = manager._extract_intake_contradictions(data)
    assert len(contradictions) == 2
    assert manager._is_intake_contradiction_resolved(contradictions[0])
    assert manager._is_intake_contradiction_resolved_or_escalated(contradictions[1])
    active = manager._active_intake_contradictions(contradictions)
    assert len(active) == 1

    assert manager._extract_intake_case_file({}) == {}


def test_collect_blockers_and_build_readiness():
    manager = PhaseManager()
    intake_case_file = {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": ["dates"]},
            "actors": {"status": "present"},
            "conduct": {"status": "missing", "missing_items": []},
            "harm": {"status": "missing"},
            "remedy": {"status": "present"},
            "proof_leads": {"status": "present"},
            "claim_elements": {"status": "present"},
        },
        "contradiction_queue": [
            {"status": "open", "severity": "blocking"},
            {"status": "awaiting_testimony", "severity": "blocking"},
        ],
        "candidate_claims": [
            {"claim_type": "discrimination", "confidence": 0.65},
            {"claim_type": "discrimination", "confidence": 0.55, "ambiguity_flags": ["flag"]},
        ],
        "canonical_facts": ["fact"],
        "proof_leads": ["lead"],
        "summary_snapshots": [{"text": "draft"}],
        "complainant_summary_confirmation": {"confirmed": False},
    }

    blockers_payload = manager._collect_intake_section_blockers(intake_case_file)
    assert "blocking_contradiction" in blockers_payload["blockers"]

    data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 2,
        "denoising_converged": True,
        "intake_case_file": intake_case_file,
    }
    readiness = manager._build_intake_readiness(data)
    assert readiness["intake_readiness_score"] <= 1.0
    assert readiness["intake_readiness_blockers"]
    manager.phase_data[ComplaintPhase.INTAKE] = data
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    intake_readiness = manager.get_intake_readiness()
    assert "score" in intake_readiness


def test_evidence_summary_and_alignment_helpers():
    manager = PhaseManager()
    packet_data = {
        "claim_alpha": {
            "claim_type": "Safety",
            "elements": [
                {
                    "element_id": "E1",
                    "support_status": "supported",
                    "parse_quality_flags": [],
                    "recommended_next_step": "archive",
                },
                {
                    "element_id": "E2",
                    "support_status": "contradicted",
                    "contradiction_count": 1,
                    "escalation_status": "awaiting_third_party_record",
                },
            ],
        }
    }
    data = {
        "claim_support_packets": packet_data,
        "alignment_evidence_tasks": [
            {
                "claim_type": "safety",
                "claim_element_id": "e2",
                "support_status": "unsupported",
                "resolution_status": "pending",
                "action": "fill_temporal_chronology_gap",
                "temporal_rule_status": "partial",
                "temporal_rule_blocking_reasons": ["missing_date"],
            }
        ],
        "alignment_task_update_history": [
            {
                "task_id": "task-1",
                "claim_type": "Safety",
                "claim_element_id": "E1",
                "resolution_status": "promoted_to_document",
                "evidence_sequence": 3,
            }
        ],
        "alignment_promotion_drift_summary": {
            "drift_flag": True,
            "promoted_count": 1,
            "pending_conversion_count": 1,
        },
        "claim_support_recommended_actions": ["follow up"],
    }

    summary = manager._build_evidence_packet_summary(data)
    assert summary["claim_support_packet_count"] == 1
    assert summary["proof_readiness_score"] >= 0.0
    assert manager._normalize_evidence_escalation_status(" PROMOTED_TO_DOCUMENT ") == "promoted_to_document"
    assert manager._resolve_evidence_escalation_status({"escalation_status": "open"}, "ignored") == "open"
    actionable = manager._get_actionable_alignment_tasks(data)
    assert len(actionable) == 1
    drift = manager._get_alignment_promotion_drift_action(data)
    assert drift and drift["action"] == "validate_promoted_support"
    packet_action = manager._get_next_packet_evidence_action(packet_data, data)
    assert packet_action and packet_action["action"] == "resolve_support_conflicts"


def test_phase_manager_transitions_and_stats(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    assert manager._can_advance_to(ComplaintPhase.EVIDENCE)
    # Force deterministic timestamp in history
    monkeypatch.setattr(
        "complaint_phases.phase_manager._utc_now_isoformat",
        lambda: "2025-01-01T00:00:00+00:00",
    )
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    _complete_evidence(manager)
    assert manager._can_advance_to(ComplaintPhase.FORMALIZATION)
    assert manager.advance_to_phase(ComplaintPhase.FORMALIZATION)
    assert manager.total_phase_transitions() == 2
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
    freq = manager.phase_transition_frequency()
    assert freq["evidence"] == 1
    assert manager.current_phase == ComplaintPhase.FORMALIZATION
    assert manager.most_visited_phase() == "evidence"

    manager.record_iteration(0.7, {"test": True})
    manager.record_iteration(0.65, {"test": False})
    assert manager.total_iterations() == 2
    assert manager.iterations_in_phase(ComplaintPhase.FORMALIZATION) == 2
    assert manager.average_loss() == pytest.approx(0.675)
    assert manager.minimum_loss() == 0.65
    assert manager.has_converged(window=2, threshold=0.1)

    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "knowledge_graph")
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "yes")
    assert manager._is_formalization_complete()
    assert manager.phase_data_coverage() == 1.0


def test_phase_manager_actions_and_serialization():
    manager = PhaseManager()
    assert manager.get_current_phase() == ComplaintPhase.INTAKE
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 5)
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", [{"type": "missing_timeline"}])
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", False)
    assert manager._get_intake_action()["action"] == "address_gaps"
    manager.iteration_count = 21
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", [])
    assert manager._get_intake_action()["action"] == "complete_intake"

    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 0)
    assert manager._get_evidence_action()["action"] == "gather_evidence"

    manager.current_phase = ComplaintPhase.FORMALIZATION
    assert manager._get_formalization_action()["action"] == "build_legal_graph"
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", {"nodes": []})
    assert manager._get_formalization_action()["action"] == "perform_neurosymbolic_matching"
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    assert manager._get_formalization_action()["action"] == "generate_formal_complaint"
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "done")
    assert manager._get_formalization_action()["action"] == "complete_formalization"

    mgr_dict = manager.to_dict()
    restored = PhaseManager.from_dict(mgr_dict)
    assert restored.current_phase == manager.current_phase
    assert restored.phase_history == manager.phase_history


@pytest.mark.performance
def test_phase_manager_intake_action_performance(benchmark):
    manager = PhaseManager()
    action = benchmark(manager._get_intake_action)
    assert action["action"] == "build_knowledge_graph"


def test_inquiries_registration_and_generation():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    inquiries.register("1. Missing detail?")
    inquiries.register("Missing detail?")
    assert len(mediator.state.inquiries) == 1
    assert mediator.state.inquiries[0]["alternative_questions"]
    inquiries.generate()
    assert len(mediator.state.inquiries) >= 2
    assert mediator.backend_calls


def test_inquiries_question_indexing_and_priorities():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    mediator.state.inquiries = [
        {"question": "What is this?", "priority": "low"},
        {"question": "Why missing support?", "support_gap_targeted": True, "priority": "high"},
        {"question": "Explain dependency", "dependency_gap_targeted": True, "priority": "medium"},
    ]
    next_question = inquiries.get_next()
    assert next_question["question"] == "Why missing support?"
    inquiries.answer("It is missing because...")
    assert mediator.state.inquiries[1]["answer"]
    assert not inquiries.is_complete()
    mediator.state.inquiries[1]["answer"] = "done"
    mediator.state.inquiries[0]["answer"] = "done"
    mediator.state.inquiries[2]["answer"] = "done"
    assert inquiries.is_complete()


def test_inquiries_merge_explain_gap_context():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    mediator.state.inquiries = []
    base = {"question": "What are support gaps?", "priority": "medium"}
    merged = inquiries.merge_legal_questions([base])
    assert merged == 1
    assert inquiries._state_inquiries() is mediator.state.inquiries
    explanation = inquiries.explain_inquiry(mediator.state.inquiries[0])
    assert "Selected because" in explanation["summary"]
    assert inquiries.same_question("What are support gaps?", "1. What are support gaps?")
    assert inquiries._priority_rank("Critical") == 0


def test_inquiries_normalization_and_helpers():
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    assert _normalize_question_cached("1. Trim THIS?") == "trim this"
    assert inquiries._trim_question_prefix("1. prefix? ") == "prefix?"
    assert inquiries._clean_question("  1. spaced ?") == "spaced ?"
    assert inquiries._extract_questions("Line?\nAnother line.") == ["Line?"]
    assert inquiries._normalize_question("LIST question?") == "list question"
    assert inquiries._priority_rank("unknown") == 2
    assert inquiries._find_unanswered([{"answer": "now"}, {}]) == {}
    sample_index = [{"question": "one?"}]
    index = inquiries._index_for(sample_index)
    assert "one" in index
    assert inquiries._index_key(sample_index) == (id(sample_index), len(sample_index))

    mediator.state.inquiries = []
    assert inquiries.merge_legal_questions([]) == 0
    failing = Inquiries(ExplodingMediator())
    assert failing._build_gap_context() == {}


@pytest.mark.performance
def test_inquiries_normalize_question_performance(benchmark):
    mediator = DummyMediator()
    inquiries = Inquiries(mediator)
    text = "1. Why is this urgent?"
    normalized = benchmark(inquiries._normalize_question, text)
    assert normalized == "why is this urgent"
