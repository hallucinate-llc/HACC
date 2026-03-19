import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

COMPLAINT_GENERATOR_ROOT = Path(__file__).resolve().parents[1] / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases.phase_manager import (
    PhaseManager,
    ComplaintPhase,
    _utc_now_isoformat,
)


def _build_sample_intake_case_file():
    return {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": ["event"]},
            "actors": {"status": "present"},
            "conduct": {"status": "missing"},
            "harm": {"status": "present"},
            "remedy": {"status": "missing"},
            "proof_leads": {"status": "present"},
            "claim_elements": {"status": "present"},
        },
        "contradiction_queue": [
            {"severity": "blocking", "status": "open"},
            {"severity": "blocking", "status": "resolved"},
        ],
        "candidate_claims": [
            {
                "claim_type": "discrimination",
                "confidence": "0.55",
                "ambiguity_flags": [],
            }
        ],
        "canonical_facts": [{"fact": "exists"}],
        "proof_leads": ["lead"],
        "complainant_summary_confirmation": {"confirmed": False},
        "summary_snapshots": [{"snapshot": True}],
    }


def _build_ready_intake_case_file():
    return {
        "intake_sections": {
            "chronology": {"status": "present", "missing_items": []},
            "actors": {"status": "present", "missing_items": []},
            "conduct": {"status": "present", "missing_items": []},
            "harm": {"status": "present", "missing_items": []},
            "remedy": {"status": "present", "missing_items": []},
            "proof_leads": {"status": "present", "missing_items": []},
            "claim_elements": {"status": "present", "missing_items": []},
        },
        "contradiction_queue": [],
        "candidate_claims": [
            {
                "claim_type": "discrimination",
                "confidence": "0.8",
                "ambiguity_flags": [],
            }
        ],
        "canonical_facts": [{"fact": "exists"}],
        "proof_leads": ["lead"],
        "complainant_summary_confirmation": {"confirmed": True},
        "summary_snapshots": [],
    }


def _ready_intake_data():
    data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 0,
        "denoising_converged": True,
        "intake_case_file": _build_ready_intake_case_file(),
    }
    return data


def _complete_evidence_data():
    return {
        "claim_support_packets": {
            "claim1": {
                "claim_type": "discrimination",
                "elements": [
                    {
                        "element_id": "element1",
                        "support_status": "supported",
                        "parse_quality_flags": [],
                    }
                ],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
        "alignment_evidence_tasks": [],
        "claim_support_recommended_actions": ["document"],
    }


def _ready_evidence_data():
    return {
        "claim_support_packets": {
            "claim1": {
                "claim_type": "discrimination",
                "elements": [
                    {
                        "element_id": "element1",
                        "support_status": "unsupported",
                        "recommended_next_step": "collect_more",
                    }
                ],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
        "alignment_evidence_tasks": [],
        "claim_support_recommended_actions": ["document"],
    }


def test_utc_now_isoformat_produces_parseable_timestamp():
    result = _utc_now_isoformat()
    parsed = datetime.fromisoformat(result)
    assert parsed.tzinfo is not None


def test_phase_manager_initializes_with_default_phase_and_data():
    manager = PhaseManager()
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history == []
    assert all(isinstance(data, dict) for data in manager.phase_data.values())


def test_extract_intake_gap_types_merges_explicit_and_current():
    manager = PhaseManager()
    data = {
        "intake_gap_types": [" missing_timeline ", None, ""],
        "current_gaps": [{"type": " missing_responsible_party "}, {"type": "missing_timeline"}],
    }
    gap_types = manager._extract_intake_gap_types(data)
    assert "missing_timeline" in gap_types
    assert "missing_responsible_party" in gap_types
    assert gap_types.count("missing_timeline") == 1


def test_extract_intake_contradictions_handles_dict_and_list():
    manager = PhaseManager()
    dict_input = {"candidates": [{"status": "open"}]}
    assert manager._extract_intake_contradictions({"intake_contradictions": dict_input}) == [{"status": "open"}]
    list_input = [{"status": "resolved"}, "bad"]
    assert manager._extract_intake_contradictions({"intake_contradictions": list_input}) == [{"status": "resolved"}]


@pytest.mark.parametrize("status,expected", [("resolved", True), ("escalated", False)])
def test_intake_contradiction_resolution_status_checks(status, expected):
    manager = PhaseManager()
    contradiction = {"current_resolution_status": status}
    assert manager._is_intake_contradiction_resolved(contradiction) is expected
    assert manager._is_intake_contradiction_resolved_or_escalated(contradiction) is True


def test_active_intake_contradictions_filters_out_resolved_and_non_dicts():
    manager = PhaseManager()
    queue = [
        {"status": "resolved"},
        {"status": "open"},
        "invalid",
    ]
    active = manager._active_intake_contradictions(queue)
    assert all(item.get("status") == "open" for item in active)


def test_extract_intake_case_file_returns_empty_for_invalid():
    manager = PhaseManager()
    assert manager._extract_intake_case_file({"intake_case_file": "bad"}) == {}
    payload = {"intake_case_file": {"any": 1}}
    assert manager._extract_intake_case_file(payload) == {"any": 1}


def test_collect_intake_section_blockers_derives_expected_fields():
    manager = PhaseManager()
    intake_case_file = _build_sample_intake_case_file()
    result = manager._collect_intake_section_blockers(intake_case_file)
    assert "blockers" in result
    assert "missing_core_chronology" in result["blockers"]
    assert result["criteria"]["blocking_contradictions_resolved"] is False


def test_build_intake_readiness_marks_ready_with_no_blockers():
    manager = PhaseManager()
    data = _ready_intake_data()
    readiness = manager._build_intake_readiness(data)
    assert readiness["intake_ready"] is True
    assert readiness["intake_readiness_score"] >= 0.0


def test_refresh_phase_derived_state_adds_intake_metrics():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update(_ready_intake_data())
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    assert "intake_readiness_score" in manager.phase_data[ComplaintPhase.INTAKE]
    readiness = manager.get_intake_readiness()
    assert readiness["ready"] is True


def test_build_evidence_packet_summary_counts_elements_and_temporal():
    manager = PhaseManager()
    data = {
        "claim_support_packets": {
            "claimA": {
                "claim_type": "ClaimA",
                "elements": [
                    {
                        "element_id": "E1",
                        "support_status": "supported",
                        "parse_quality_flags": [],
                    },
                    {
                        "element_id": "E2",
                        "support_status": "contradicted",
                        "contradiction_count": 1,
                        "recommended_next_step": "resolve",
                    },
                ],
            }
        },
        "alignment_evidence_tasks": [
            {
                "claim_type": "claima",
                "claim_element_id": "e2",
                "resolution_status": "promoted_to_testimony",
                "action": "fill_temporal_chronology_gap",
                "temporal_rule_status": "partial",
                "temporal_rule_blocking_reasons": ["missing"],
            }
        ],
    }
    summary = manager._build_evidence_packet_summary(data)
    assert summary["claim_support_element_count"] == 2
    assert summary["claim_support_blocking_contradictions"] >= 1
    assert summary["temporal_gap_task_count"] == 1


def test_normalize_and_resolve_evidence_escalation_status_prioritizes_fields():
    manager = PhaseManager()
    element = {
        "escalation_status": "manual_review_pending",
        "resolution_status": "resolved",
    }
    assert manager._normalize_evidence_escalation_status(" MANUAL_REVIEW_PENDING ") == "manual_review_pending"
    assert manager._resolve_evidence_escalation_status(element, "promo") == "manual_review_pending"


def test_get_actionable_alignment_tasks_filters_by_resolution_status():
    manager = PhaseManager()
    data = {
        "alignment_evidence_tasks": [
            {"support_status": "unsupported", "resolution_status": "pending"},
            {"support_status": "supported", "resolution_status": "awaiting_complainant_record"},
        ]
    }
    actionable = manager._get_actionable_alignment_tasks(data)
    assert len(actionable) == 1


def test_get_alignment_promotion_drift_action_picks_promoted_targets():
    manager = PhaseManager()
    data = {
        "alignment_promotion_drift_summary": {"drift_flag": True, "promoted_count": 1, "pending_conversion_count": 0},
        "alignment_task_updates": [
            {
                "claim_type": "ClaimA",
                "claim_element_id": "E1",
                "resolution_status": "promoted_to_document",
                "evidence_sequence": 1,
            }
        ],
        "claim_support_recommended_actions": ["validate"],
    }
    action = manager._get_alignment_promotion_drift_action(data)
    assert action is not None
    assert action["action"] == "validate_promoted_support"


def test_get_next_packet_evidence_action_returns_gap_resolution():
    manager = PhaseManager()
    data = _ready_evidence_data()
    packets = data["claim_support_packets"].copy()
    action = manager._get_next_packet_evidence_action(packets, data)
    assert action["action"] == "collect_more"
    assert action["support_status"] == "unsupported"


def test_phase_transitions_record_history_and_stats():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update(_ready_intake_data())
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    manager.phase_data[ComplaintPhase.EVIDENCE].update(_complete_evidence_data())
    assert manager.advance_to_phase(ComplaintPhase.FORMALIZATION)
    manager.phase_data[ComplaintPhase.FORMALIZATION].update({"legal_graph": True, "matching_complete": True, "formal_complaint": {}})
    assert manager.total_phase_transitions() == 2
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
    assert manager.most_visited_phase() in {ComplaintPhase.EVIDENCE.value, ComplaintPhase.FORMALIZATION.value}
    assert manager.phase_transition_frequency()[ComplaintPhase.EVIDENCE.value] == 1


def test_iteration_recording_average_and_minimum_loss():
    manager = PhaseManager()
    values = (0.5, 0.49, 0.49, 0.49, 0.49)
    for value in values:
        manager.record_iteration(value, {"metric": "test"})
    assert manager.total_iterations() == 5
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 5
    values = (0.5, 0.49, 0.49, 0.49, 0.49)
    assert manager.average_loss() == pytest.approx(sum(values) / len(values))
    assert manager.minimum_loss() == pytest.approx(min(values))
    assert manager.has_converged(window=5, threshold=0.05)


def test_phase_manager_actions_reflect_phase_data_transitions():
    manager = PhaseManager()
    assert manager.get_next_action()["action"] == "build_knowledge_graph"
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = True
    manager.phase_data[ComplaintPhase.INTAKE]["dependency_graph"] = True
    manager.phase_data[ComplaintPhase.INTAKE]["remaining_gaps"] = 0
    manager.phase_data[ComplaintPhase.INTAKE]["denoising_converged"] = True
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    action = manager.get_next_action()
    assert action["action"] in {"address_gaps", "complete_intake", "continue_denoising"}
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.phase_data[ComplaintPhase.EVIDENCE].update(_ready_evidence_data())
    evidence_action = manager.get_next_action()
    assert "action" in evidence_action
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.phase_data[ComplaintPhase.FORMALIZATION].update({"legal_graph": True})
    assert manager.get_next_action()["action"] == "perform_neurosymbolic_matching"


def test_phase_data_helpers_serialization_and_coverage():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "test_key", "value")
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "test_key") == "value"
    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "test_key")
    assert manager.phase_data_coverage() >= 0
    snapshot = manager.to_dict()
    restored = PhaseManager.from_dict(snapshot)
    assert restored.current_phase == manager.current_phase
    assert restored.iteration_count == manager.iteration_count


@pytest.mark.performance
def test_phase_manager_get_next_action_remains_performant():
    manager = PhaseManager()
    start = time.perf_counter()
    for _ in range(200):
        manager.get_next_action()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5
