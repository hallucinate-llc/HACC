import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_ROOT))

from complaint_phases import phase_manager as pm
from complaint_phases.phase_manager import ComplaintPhase, PhaseManager


def _build_complete_intake_case() -> dict:
    sections = {
        "chronology": {"status": "complete", "missing_items": []},
        "actors": {"status": "complete", "missing_items": []},
        "conduct": {"status": "complete", "missing_items": []},
        "harm": {"status": "complete", "missing_items": []},
        "remedy": {"status": "complete", "missing_items": []},
        "proof_leads": {"status": "complete", "missing_items": []},
        "claim_elements": {"status": "complete", "missing_items": []},
    }
    case_file = {
        "intake_sections": sections,
        "candidate_claims": [{"claim_type": "retaliation", "confidence": 0.9}],
        "canonical_facts": [{"fact": "confirmed"}],
        "proof_leads": [{"lead": "document"}],
        "summary_snapshots": [],
        "contradiction_queue": [],
    }
    return case_file


@pytest.fixture
def manager() -> PhaseManager:
    return PhaseManager()


def test_phase_manager_initial_state_and_utc_helper(manager: PhaseManager):
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history == []
    assert isinstance(pm._utc_now_isoformat(), str)
    assert manager.phase_data[ComplaintPhase.INTAKE] == {}


def test_extract_gap_types_and_contradictions(manager: PhaseManager):
    data = {
        "intake_gap_types": ["missing_timeline", "missing_timeline", None],
        "current_gaps": [
            {"type": "missing_responsible_party"},
            {"type": "", "notes": "ignored"},
            "not a dict",
        ],
        "intake_contradictions": {
            "candidates": [{"id": 1}, {"status": "resolved"}],
        },
    }
    gap_types = manager._extract_intake_gap_types(data)
    assert "missing_timeline" in gap_types
    assert "missing_responsible_party" in gap_types
    contradictions = manager._extract_intake_contradictions(data)
    assert isinstance(contradictions, list)
    assert any(c.get("id") == 1 for c in contradictions)
    assert manager._active_intake_contradictions([
        {"status": "open"},
        {"status": "resolved"},
    ]) == [{"status": "open"}]
    assert manager._is_intake_contradiction_resolved({"status": "resolved"})
    assert manager._is_intake_contradiction_resolved_or_escalated({"status": "escalated"})
    assert not manager._is_intake_contradiction_resolved_or_escalated({"status": "open"})


def test_collect_intake_case_blockers_creates_metrics(manager: PhaseManager):
    intake_file = _build_complete_intake_case()
    intake_file.update({
        "summary_snapshots": [{"summary": "draft"}],
        "complainant_summary_confirmation": {"confirmed": False},
        "contradiction_queue": [
            {"severity": "blocking", "status": "open", "current_resolution_status": "open"}
        ],
    })
    readiness = manager._collect_intake_section_blockers(intake_file)
    assert readiness["sections"]["chronology"]["status"] == "complete"
    assert "blocking_contradiction" in readiness["blockers"]
    assert readiness["criteria"]["case_theory_coherent"]
    assert readiness["criteria"]["minimum_proof_path_present"]


def test_build_and_refresh_intake_readiness(manager: PhaseManager):
    manager.phase_data[ComplaintPhase.INTAKE].update({
        "knowledge_graph": True,
        "dependency_graph": True,
        "denoising_converged": True,
        "current_gaps": [],
        "remaining_gaps": 0,
        "intake_case_file": _build_complete_intake_case(),
    })
    readiness = manager._build_intake_readiness(manager.phase_data[ComplaintPhase.INTAKE])
    assert readiness["intake_ready"]
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    state = manager.get_intake_readiness()
    assert state["ready"]
    assert state["score"] > 0.0


def test_evidence_packet_summary_and_resolution_helpers(manager: PhaseManager):
    packets = {
        "claim-a": {
            "claim_type": "retaliation",
            "elements": [
                {
                    "element_id": "el-1",
                    "support_status": "partially_supported",
                    "contradiction_count": 0,
                    "recommended_next_step": "review",
                },
                {
                    "element_id": "el-2",
                    "support_status": "unsupported",
                    "parse_quality_flags": [],
                },
            ],
        }
    }
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "claim_support_packets": packets,
        "alignment_evidence_tasks": [
            {"claim_type": "retaliation", "claim_element_id": "el-1", "support_status": "contradicted", "action": "follow_up", "resolution_status": "needs_manual_review"},
        ],
        "claim_support_recommended_actions": ["doc review"],
    })
    summary = manager._build_evidence_packet_summary(manager.phase_data[ComplaintPhase.EVIDENCE])
    assert summary["claim_support_packet_count"] == 1
    assert summary["reviewable_escalation_ratio"] >= 0.0
    assert manager._normalize_evidence_escalation_status(" PROMOTED_To_TESTIMONY ") == "promoted_to_testimony"
    element = {"resolution_status": "", "recommended_next_step": "next"}
    resolved = manager._resolve_evidence_escalation_status(element, "promoted_to_document")
    assert resolved == "promoted_to_document"


def test_alignment_actions_and_packet_selection(manager: PhaseManager):
    data = {
        "alignment_evidence_tasks": [
            {"support_status": "unsupported", "claim_type": "retaliation", "claim_element_id": "el-1", "resolution_status": "needs_manual_review", "action": "fill_temporal_chronology_gap"},
            {"support_status": "supported", "action": "ok"},
        ],
        "alignment_task_update_history": [
            {"task_id": "t1", "resolution_status": "promoted_to_testimony", "claim_type": "retaliation", "claim_element_id": "el-1", "evidence_sequence": 1},
            {"task_id": "t1", "resolution_status": "promoted_to_document", "claim_type": "retaliation", "claim_element_id": "el-1", "evidence_sequence": 2},
        ],
        "claim_support_recommended_actions": ["follow-up"],
    }
    tasks = manager._get_actionable_alignment_tasks(data)
    assert all(task.get("support_status") != "supported" for task in tasks)
    drift_action = manager._get_alignment_promotion_drift_action(data)
    assert drift_action["action"] == "validate_promoted_support"
    packets = {
        "claim-a": {
            "claim_type": "retaliation",
            "elements": [
                {"element_id": "el-1", "support_status": "contradicted", "recommended_next_step": "resolve"}
            ],
        }
    }
    packet_action = manager._get_next_packet_evidence_action(packets, data)
    assert packet_action["action"] == "resolve"


def test_phase_transitions_actions_and_checks(manager: PhaseManager):
    manager.phase_data[ComplaintPhase.INTAKE].update({
        "knowledge_graph": True,
        "dependency_graph": True,
        "denoising_converged": True,
        "current_gaps": [],
        "remaining_gaps": 0,
        "intake_case_file": _build_complete_intake_case(),
    })
    assert manager._is_intake_complete()
    assert manager._can_advance_to(ComplaintPhase.EVIDENCE)
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    assert manager.current_phase == ComplaintPhase.EVIDENCE
    assert manager.total_phase_transitions() == 1
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
    assert manager.most_visited_phase() == "evidence"
    assert manager.phase_transition_frequency()["evidence"] == 1
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "claim_support_packets": {
            "claim-a": {
                "elements": [{"support_status": "supported", "element_id": "el"}],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
        "alignment_evidence_tasks": [],
        "claim_support_unsupported_count": 0,
    })
    assert manager._is_evidence_complete()
    manager.phase_data[ComplaintPhase.FORMALIZATION].clear()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    assert manager._get_formalization_action()["action"] == "build_legal_graph"
    assert manager.get_next_action()["action"] == "build_legal_graph"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["legal_graph"] = {"nodes": []}
    assert manager._get_formalization_action()["action"] == "perform_neurosymbolic_matching"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["matching_complete"] = True
    assert manager._get_formalization_action()["action"] == "generate_formal_complaint"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["formal_complaint"] = "draft"
    assert manager._get_formalization_action()["action"] == "complete_formalization"
    assert manager._is_formalization_complete()


def test_phase_data_management_and_serialization(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.INTAKE, "key", "value")
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "key") == "value"
    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "key")
    assert manager.phase_data_coverage() > 0.0
    snapshot = manager.to_dict()
    restored = PhaseManager.from_dict(snapshot)
    assert restored.current_phase == snapshot["current_phase"] and restored.iteration_count == snapshot["iteration_count"]
    assert restored.total_phase_transitions() == manager.total_phase_transitions()


def test_iteration_metrics_and_convergence(manager: PhaseManager):
    manager.record_iteration(1.0, {"label": "first"})
    manager.record_iteration(0.9, {"label": "second"})
    manager.record_iteration(0.91, {"label": "third"})
    manager.record_iteration(0.905, {"label": "fourth"})
    manager.record_iteration(0.902, {"label": "fifth"})
    assert manager.total_iterations() == 5
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 5
    assert pytest.approx(manager.average_loss(), rel=1e-3) == pytest.approx((1.0 + 0.9 + 0.91 + 0.905 + 0.902) / 5)
    assert manager.minimum_loss() == pytest.approx(0.9, rel=1e-3)
    assert manager.has_converged(window=5, threshold=0.05)


def test_evidence_packet_summary_performance(manager: PhaseManager):
    data = {
        "claim_support_packets": {
            "claim-a": {
                "elements": [{"support_status": "unsupported", "element_id": "el"}],
            }
        },
        "alignment_evidence_tasks": [],
    }
    start = time.perf_counter()
    for _ in range(50):
        manager._build_evidence_packet_summary(data)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5
