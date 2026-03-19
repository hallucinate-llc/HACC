import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases import phase_manager as pm  # noqa: E402
from complaint_phases.phase_manager import (
    ComplaintPhase,
    PhaseManager,
    _utc_now_isoformat,
)
from mediator.inquiries import Inquiries, _normalize_question_cached  # noqa: E402

try:
    import pytest_benchmark  # noqa: F401

    _HAS_BENCHMARK = True
except Exception:  # pragma: no cover - optional
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


class DummyState(SimpleNamespace):
    def __init__(self):
        super().__init__(inquiries=[], complaint="State complaint")


class DummyMediator:
    def __init__(self):
        self.state = DummyState()
        self.query_calls = []

    def query_backend(self, prompt):
        self.query_calls.append(prompt)
        return "What happened?" "\n" "Who was involved?"

    def build_inquiry_gap_context(self):
        return {"priority_terms": ["critical", "dependency"]}


class FaultyMediator(DummyMediator):
    def build_inquiry_gap_context(self):
        raise RuntimeError("boom")


def _ready_case_file():
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


def _ready_evidence_data():
    return {
        "alignment_evidence_tasks": [
            {
                "claim_type": "eligibility",
                "claim_element_id": "elem",
                "support_status": "unsupported",
                "resolution_status": "awaiting_testimony",
                "action": "fill_evidence_gaps",
                "temporal_rule_status": "partial",
                "temporal_rule_blocking_reasons": ["need more detail"],
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
                "claim_support_elements": [],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 1,
        "claim_support_recommended_actions": ["collect_support"],
    }


def _complete_evidence_data():
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


def test_utc_now_isoformat_has_timezone_and_delimiter():
    value = _utc_now_isoformat()
    assert "T" in value
    assert value.endswith("+00:00") or value.endswith("Z")


def test_phase_manager_init_sets_defaults():
    manager = PhaseManager()
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.loss_history == []
    assert manager.iteration_count == 0
    assert set(manager.phase_data.keys()) == {
        ComplaintPhase.INTAKE,
        ComplaintPhase.EVIDENCE,
        ComplaintPhase.FORMALIZATION,
    }


def test_extract_intake_gap_types_normalizes_and_dedups():
    manager = PhaseManager()
    data = {
        "intake_gap_types": [" missing_timeline", "missing_timeline"],
        "current_gaps": [{"type": "missing_actor"}, "bad"],
    }
    assert manager._extract_intake_gap_types(data) == ["missing_timeline", "missing_actor"]


def test_extract_intake_contradictions_handles_varied_structures():
    manager = PhaseManager()
    assert manager._extract_intake_contradictions({"intake_contradictions": {}}) == []
    block = {"intake_contradictions": {"candidates": [{"id": 1}]}}
    assert manager._extract_intake_contradictions(block) == [{"id": 1}]
    assert manager._extract_intake_contradictions({"intake_contradictions": [{"id": 2}, "bad"]}) == [{"id": 2}]


def test_active_and_resolution_contradictions_detect_status():
    manager = PhaseManager()
    queue = [
        {"status": "open"},
        {"current_resolution_status": "resolved"},
        {"status": "manual_review_pending"},
    ]
    active = manager._active_intake_contradictions(queue)
    assert len(active) == 2
    assert manager._is_intake_contradiction_resolved(active[1]) is False
    assert manager._is_intake_contradiction_resolved_or_escalated(queue[2]) is True


def test_extract_intake_case_file_and_section_blockers():
    manager = PhaseManager()
    case_file = {
        "intake_case_file": {"intake_sections": {"chronology": {"status": "missing"}}}
    }
    extracted = manager._extract_intake_case_file(case_file)
    assert "intake_sections" in extracted
    blockers = manager._collect_intake_section_blockers(
        {
            "intake_sections": {"chronology": {"status": "missing"}},
            "contradiction_queue": [{"severity": "blocking", "status": "open"}],
            "proof_leads": [],
            "summary_snapshots": [{"snap": 1}],
        }
    )
    assert "blocking_contradiction" in blockers["blockers"]
    assert blockers["criteria"]["blocking_contradictions_resolved"] is False


def test_build_intake_readiness_includes_structured_data():
    manager = PhaseManager()
    intake_data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 0,
        "denoising_converged": True,
        "intake_case_file": _ready_case_file(),
        "current_gaps": [],
    }
    readiness = manager._build_intake_readiness(intake_data)
    assert readiness["intake_ready"] is True
    assert readiness["candidate_claim_count"] == 1
    assert readiness["proof_lead_count"] == 1


def test_refresh_phase_and_get_readiness_invokes_builders():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "intake_case_file", _ready_case_file())
    readiness = manager.get_intake_readiness()
    assert readiness["ready"] is True


def test_build_evidence_packet_summary_and_resolution_helpers():
    manager = PhaseManager()
    data = _ready_evidence_data()
    summary = manager._build_evidence_packet_summary(data)
    assert summary["claim_support_packet_count"] == 1
    assert summary["claim_support_blocking_contradictions"] == 0
    assert summary["proof_readiness_score"] <= 1.0
    assert manager._normalize_evidence_escalation_status(None) == ""
    resolved = manager._resolve_evidence_escalation_status(
        {"escalation_status": "awaiting_third_party_record"}
    )
    assert resolved == "awaiting_third_party_record"


def test_alignment_task_helpers_and_drift_actions():
    manager = PhaseManager()
    data = _ready_evidence_data()
    actionable = manager._get_actionable_alignment_tasks(data)
    assert actionable == []
    data["alignment_promotion_drift_summary"] = {
        "drift_flag": True,
        "promoted_count": 1,
        "pending_conversion_count": 1,
    }
    data["alignment_task_updates"] = [
        {
            "claim_type": "eligibility",
            "claim_element_id": "elem",
            "resolution_status": "promoted_to_document",
            "task_id": "123",
            "evidence_sequence": 2,
        }
    ]
    drift_action = manager._get_alignment_promotion_drift_action(data)
    assert drift_action and drift_action["action"] == "validate_promoted_support"
    packets = data["claim_support_packets"]
    next_packet = manager._get_next_packet_evidence_action(packets, data)
    assert next_packet is None


def test_phase_transitions_and_completions():
    manager = PhaseManager()
    assert manager.get_current_phase() == ComplaintPhase.INTAKE
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is False
    manager.update_phase_data(ComplaintPhase.INTAKE, "intake_case_file", _ready_case_file())
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    assert manager._is_intake_complete() is True
    assert manager._can_advance_to(ComplaintPhase.EVIDENCE) is True
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
    assert manager.get_current_phase() == ComplaintPhase.EVIDENCE
    assert manager.phase_history[-1]["to_phase"] == "evidence"
