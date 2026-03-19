import sys
import time
from pathlib import Path
from typing import Any, Dict

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases.phase_manager import ComplaintPhase, PhaseManager


@pytest.fixture
def manager() -> PhaseManager:
    return PhaseManager()


def _build_sparse_intake_case() -> Dict[str, Any]:
    return {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": []},
            "actors": {"status": "missing", "missing_items": []},
        },
        "contradiction_queue": [
            {
                "severity": "blocking",
                "status": "open",
                "current_resolution_status": "open",
            }
        ],
        "summary_snapshots": [{"summary": "draft"}],
        "complainant_summary_confirmation": {"confirmed": False},
    }


def test_collect_intake_section_blockers_handles_missing_sections(manager: PhaseManager):
    result = manager._collect_intake_section_blockers(_build_sparse_intake_case())
    assert "blocking_contradiction" in result["blockers"]
    assert "complainant_summary_confirmation_required" in result["blockers"]
    assert result["sections"]["chronology"]["status"] == "missing"
    assert not result["criteria"]["case_theory_coherent"]


def test_build_intake_readiness_synthesizes_blockers_and_scores(manager: PhaseManager):
    data: Dict[str, Any] = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "denoising_converged": False,
        "current_gaps": [{"type": "missing_timeline"}],
        "remaining_gaps": 2,
        "intake_gap_types": ["missing_timeline"],
        "intake_contradictions": [],
        "intake_blockers": ["custom_block"],
        "intake_case_file": {
            "intake_sections": {},
            "candidate_claims": [],
            "proof_leads": [],
            "canonical_facts": [],
            "summary_snapshots": [],
            "contradiction_queue": [],
        },
    }
    readiness = manager._build_intake_readiness(data)
    assert not readiness["intake_ready"]
    assert "missing_timeline" in readiness["intake_readiness_blockers"]
    assert "denoising_not_converged" in readiness["intake_readiness_blockers"]
    assert "custom_block" in readiness["intake_readiness_blockers"]
    assert readiness["intake_readiness_score"] <= 1.0


def test_get_intake_action_progresses_through_steps(manager: PhaseManager):
    action = manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = {"nodes": []}
    action = manager.get_next_action()
    assert action["action"] == "build_dependency_graph"
    manager.phase_data[ComplaintPhase.INTAKE]["dependency_graph"] = {"edges": []}
    manager.phase_data[ComplaintPhase.INTAKE]["current_gaps"] = [{"type": "gap"}]
    manager.phase_data[ComplaintPhase.INTAKE]["remaining_gaps"] = 10
    action = manager.get_next_action()
    assert action["action"] == "address_gaps"


def test_get_intake_action_completes_when_ready(manager: PhaseManager):
    manager.iteration_count = 25
    manager.phase_data[ComplaintPhase.INTAKE].update({
        "knowledge_graph": True,
        "dependency_graph": True,
        "denoising_converged": True,
        "current_gaps": [],
        "remaining_gaps": 0,
    })
    action = manager.get_next_action()
    assert action["action"] == "complete_intake"


def test_get_evidence_action_respects_alignment_and_packets(manager: PhaseManager):
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "claim_support_packets": {
            "claim-a": {
                "claim_type": "claim-a",
                "elements": [
                    {
                        "element_id": "el-1",
                        "support_status": "unsupported",
                        "contradiction_count": 0,
                    }
                ],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
        "claim_support_recommended_actions": ["collect"],
        "alignment_evidence_tasks": [
            {
                "support_status": "unsupported",
                "claim_type": "claim-a",
                "claim_element_id": "el-1",
                "resolution_status": "pending",
                "action": "follow_up",
            }
        ],
    })
    action = manager.get_next_action()
    assert action["action"] == "follow_up"
    assert action["claim_type"] == "claim-a"


def test_get_evidence_action_handles_gap_ratio(monkeypatch, manager: PhaseManager):
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "evidence_count": 1,
        "knowledge_graph_enhanced": True,
        "evidence_gap_ratio": 0.5,
    })
    action = manager.get_next_action()
    assert action["action"] == "fill_evidence_gaps"


def test_formalization_action_sequence(manager: PhaseManager):
    manager.current_phase = ComplaintPhase.FORMALIZATION
    action = manager.get_next_action()
    assert action["action"] == "build_legal_graph"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["legal_graph"] = {"nodes": []}
    action = manager.get_next_action()
    assert action["action"] == "perform_neurosymbolic_matching"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["matching_complete"] = True
    action = manager.get_next_action()
    assert action["action"] == "generate_formal_complaint"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["formal_complaint"] = "ready"
    action = manager.get_next_action()
    assert action["action"] == "complete_formalization"


def test_advance_to_phase_respects_completion(monkeypatch, manager: PhaseManager):
    monkeypatch.setattr(manager, "is_phase_complete", lambda phase: False)
    assert not manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    monkeypatch.setattr(manager, "is_phase_complete", lambda phase: True)
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    assert manager.current_phase == ComplaintPhase.EVIDENCE


def test_phase_transition_statistics_and_totals(manager: PhaseManager):
    history = [
        {"from_phase": "intake", "to_phase": "evidence", "timestamp": "t1", "iteration": 1},
        {"from_phase": "evidence", "to_phase": "formalization", "timestamp": "t2", "iteration": 2},
        {"from_phase": "formalization", "to_phase": "evidence", "timestamp": "t3", "iteration": 3},
    ]
    manager.phase_history.extend(history)
    assert manager.total_phase_transitions() == 3
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 2
    freq = manager.phase_transition_frequency()
    assert freq["evidence"] == 2
    assert freq["formalization"] == 1
    assert manager.most_visited_phase() == "evidence"


def test_iteration_metrics_edge_cases(manager: PhaseManager):
    assert manager.average_loss() == 0.0
    assert manager.minimum_loss() == float("inf")
    assert not manager.has_converged(window=3)
    manager.record_iteration(0.5, {})
    manager.record_iteration(0.5, {})
    manager.record_iteration(0.5, {})
    assert manager.has_converged(window=3, threshold=0.0001)


def test_phase_data_keys_and_coverage(manager: PhaseManager):
    assert not manager.has_phase_data_key(ComplaintPhase.INTAKE, "missing")
    assert manager.phase_data_coverage() == 0
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "knowledge_graph")
    assert manager.phase_data_coverage() == pytest.approx(1 / 3)


def test_next_packet_action_returns_none_when_no_candidates(manager: PhaseManager):
    packets = {
        "claim-a": {"elements": [{"support_status": "supported", "element_id": "el"}]}
    }
    action = manager._get_next_packet_evidence_action(packets, {})
    assert action is None


def test_intake_action_performance(manager: PhaseManager):
    start = time.perf_counter()
    for _ in range(100):
        manager.get_next_action()
    assert time.perf_counter() - start < 1.0
