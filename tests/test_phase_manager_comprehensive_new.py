import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases import phase_manager as pm
from complaint_phases.phase_manager import ComplaintPhase, PhaseManager


def test_extract_intake_gap_types_collects_normalized_entries():
    manager = PhaseManager()
    data = {
        "intake_gap_types": ["missing_timeline", " Missing_Timeline ", None, ""],
        "current_gaps": [
            {"type": "missing_responsible_party"},
            {"type": "missing_timeline"},
            "invalid",
        ],
    }
    assert manager._extract_intake_gap_types(data) == [
        "missing_timeline",
        "missing_responsible_party",
    ]


def test_extract_intake_contradictions_variants():
    manager = PhaseManager()
    assert manager._extract_intake_contradictions({"candidates": [{"status": "open"}]}) == [
        {"status": "open"},
    ]
    assert manager._extract_intake_contradictions([{"status": "resolved"}, "x"]) == [
        {"status": "resolved"},
    ]
    assert manager._extract_intake_contradictions({"status": "open"}) == [{"status": "open"}]
    assert manager._extract_intake_contradictions("bad") == []


def test_active_contradictions_filters_resolved():
    manager = PhaseManager()
    queue = [
        {"severity": "blocking", "status": "resolved"},
        {"severity": "blocking", "status": "open"},
    ]
    active = manager._active_intake_contradictions(queue)
    assert len(active) == 1
    assert active[0]["status"] == "open"


def test_contradiction_resolution_checks():
    manager = PhaseManager()
    resolved = {"current_resolution_status": "resolved"}
    escalated = {"status": "awaiting_complainant_record"}
    assert manager._is_intake_contradiction_resolved(resolved)
    assert not manager._is_intake_contradiction_resolved_or_escalated({"status": "open"})
    assert manager._is_intake_contradiction_resolved_or_escalated(escalated)


def test_extract_intake_case_file_safe():
    manager = PhaseManager()
    assert manager._extract_intake_case_file({}) == {}
    assert manager._extract_intake_case_file({"intake_case_file": {"foo": "bar"}}) == {"foo": "bar"}


def test_collect_intake_section_blockers_and_criteria():
    manager = PhaseManager()
    intake_case_file = {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": ["when"]},
            "actors": {"status": "complete"},
            "conduct": {"status": "missing"},
            "harm": {"status": "complete"},
            "proof_leads": {"status": "missing"},
        },
        "contradiction_queue": [
            {"severity": "blocking", "status": "blocking", "current_resolution_status": "open"}
        ],
        "candidate_claims": [
            {"claim_type": "housing", "confidence": 0.6},
            {"claim_type": "housing", "confidence": 0.55, "ambiguity_flags": ["flag"]},
        ],
        "canonical_facts": [{"fact": "a"}],
        "proof_leads": ["lead"],
        "complainant_summary_confirmation": {"confirmed": False},
        "summary_snapshots": ["snapshot"],
    }
    result = manager._collect_intake_section_blockers(intake_case_file)
    assert "missing_core_chronology" in result["blockers"]
    assert "missing_proof_leads" in result["blockers"]
    assert result["criteria"]["blocking_contradictions_resolved"] is False
    assert result["criteria"]["blocking_contradictions_resolved_or_escalated"] is False
    assert result["candidate_claim_count"] == 2
    assert result["criteria"]["claim_disambiguation_resolved"] is False
    assert result["canonical_fact_count"] == 1


def test_build_intake_readiness_combines_sources():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update({
        "knowledge_graph": {"nodes": []},
        "dependency_graph": {"edges": []},
        "remaining_gaps": 2,
        "denoising_converged": True,
        "intake_case_file": {
            "intake_sections": {"chronology": {"status": "complete"}},
            "candidate_claims": [{"confidence": 0.8}],
            "canonical_facts": [],
            "proof_leads": [],
            "complainant_summary_confirmation": {"confirmed": True},
        },
        "intake_contradictions": [],
    })
    readiness = manager._build_intake_readiness(manager.phase_data[ComplaintPhase.INTAKE])
    assert readiness["intake_ready"]
    assert readiness["remaining_gap_count"] == 2
    assert readiness["candidate_claim_count"] == 1


def test_refresh_phase_derived_state_and_intake_readiness():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = True
    readiness = manager.get_intake_readiness()
    assert readiness["ready"] is False
    assert "missing_dependency_graph" in readiness["blockers"]


def test_build_evidence_packet_summary_calculations():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "claim_support_packets": {
            "claimA": {
                "claim_type": "Housing",
        "elements": [
            {
                "element_id": "1",
                "support_status": "supported",
                "parse_quality_flags": [],
                "recommended_next_step": "finalize",
            },
            {
                "element_id": "2",
                "support_status": "contradicted",
                "contradiction_count": 1,
            },
        ],
            }
        },
        "alignment_evidence_tasks": [
            {"claim_type": "housing", "claim_element_id": "2", "support_status": "unsupported", "resolution_status": "pending"}
        ],
    })
    summary = manager._build_evidence_packet_summary(manager.phase_data[ComplaintPhase.EVIDENCE])
    assert summary["claim_support_packet_count"] == 1
    assert summary["claim_support_blocking_contradictions"] == 1
    assert "finalize" in summary["claim_support_recommended_actions"]


def test_normalize_and_resolve_evidence_escalation_status():
    manager = PhaseManager()
    assert manager._normalize_evidence_escalation_status(" Pending ") == "pending"
    element = {"escalation_status": "", "resolution_status": "OCR"}
    assert manager._resolve_evidence_escalation_status(element, "") == "ocr"
    assert manager._resolve_evidence_escalation_status(element, "secondary") == "ocr"


def test_actionable_alignment_tasks_filters():
    manager = PhaseManager()
    data = {"alignment_evidence_tasks": [
        {"support_status": "unsupported", "resolution_status": ""},
        {"support_status": "supported", "resolution_status": ""},
    ]}
    tasks = manager._get_actionable_alignment_tasks(data)
    assert len(tasks) == 1


def test_alignment_promotion_drift_action_prioritizes_single_element():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "alignment_promotion_drift_summary": {"drift_flag": True, "promoted_count": 1, "pending_conversion_count": 0},
        "alignment_task_update_history": [
            {"claim_type": "housing", "claim_element_id": "E1", "resolution_status": "promoted_to_document", "evidence_sequence": 2},
        ],
        "claim_support_recommended_actions": ["next"],
    })
    action = manager._get_alignment_promotion_drift_action(manager.phase_data[ComplaintPhase.EVIDENCE])
    assert action is not None
    assert action["action"] == "validate_promoted_support"
    assert action["claim_element_id"] == "E1"


def test_next_packet_evidence_action_returns_fill_gaps_for_partial():
    manager = PhaseManager()
    packets = {
        "claim": {
            "claim_type": "Housing",
            "elements": [
                {"element_id": "1", "support_status": "contradicted", "recommended_next_step": "resolve"},
                {"element_id": "2", "support_status": "supported"},
            ],
        }
    }
    data = {"alignment_evidence_tasks": []}
    action = manager._get_next_packet_evidence_action(packets, data)
    assert action["action"] == "resolve"
    assert action["support_status"] == "contradicted"


def test_phase_state_and_actions_transition_metrics(monkeypatch):
    manager = PhaseManager()
    assert manager.get_current_phase() == ComplaintPhase.INTAKE
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 1)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2020-01-01T00:00:00+00:00")
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    assert manager.total_phase_transitions() == 1
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
    assert manager.phase_transition_frequency()["evidence"] == 1
    assert manager.most_visited_phase() == "evidence"


def test_iteration_metrics_and_serialization(monkeypatch):
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.record_iteration(0.5, {"metric": 1})
    manager.record_iteration(0.6, {"metric": 2})
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.record_iteration(0.4, {"metric": 3})
    assert manager.total_iterations() == 3
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 2
    assert round(manager.average_loss(), 3) == pytest.approx(0.5)
    assert manager.minimum_loss() == 0.4
    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "knowledge_graph")
    assert manager.phase_data_coverage() >= 0.5
    snapshot = manager.to_dict()
    restored = PhaseManager.from_dict(snapshot)
    assert restored.current_phase == manager.current_phase
    assert restored.loss_history == manager.loss_history


def test_get_next_action_delegates_and_unknown():
    manager = PhaseManager()
    action = manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    manager._phase_action_getters.clear()
    manager._PHASE_ACTION_GETTERS[ComplaintPhase.INTAKE] = "_get_intake_action"
    assert manager.get_next_action()["action"] == "build_knowledge_graph"


def test_get_intake_action_flow_through_gaps_and_completion():
    manager = PhaseManager()
    data = manager.phase_data[ComplaintPhase.INTAKE]
    data["intake_case_file"] = {"intake_sections": {}}
    assert manager._get_intake_action()["action"] == "build_knowledge_graph"
    data["knowledge_graph"] = True
    assert manager._get_intake_action()["action"] == "build_dependency_graph"
    data["dependency_graph"] = True
    data["current_gaps"] = [{"issue": 1}]
    data["remaining_gaps"] = 5
    assert manager._get_intake_action()["action"] == "address_gaps"
    data["remaining_gaps"] = 0
    data["denoising_converged"] = True
    manager.iteration_count = 999
    assert manager._get_intake_action()["action"] == "complete_intake"


def test_get_evidence_action_branches_with_packets():
    manager = PhaseManager()
    data = manager.phase_data[ComplaintPhase.EVIDENCE]
    data.update({
        "claim_support_packets": {
            "claim": {
                "claim_type": "housing",
                "elements": [{"element_id": "1", "support_status": "unsupported"}],
            }
        },
        "claim_support_explicit_status_count": 1,
        "claim_support_element_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
    })
    assert manager._get_evidence_action()["action"] == "fill_evidence_gaps"
    data["claim_support_blocking_contradictions"] = 1
    assert manager._get_evidence_action()["action"] == "resolve_support_conflicts"
    data["claim_support_blocking_contradictions"] = 0
    data["alignment_evidence_tasks"] = [
        {"action": "fill_evidence_gaps", "support_status": "unsupported", "priority": "high"}
    ]
    assert manager._get_evidence_action()["action"] == "fill_evidence_gaps"


def test_get_formalization_action_sequence():
    manager = PhaseManager()
    data = manager.phase_data[ComplaintPhase.FORMALIZATION]
    assert manager._get_formalization_action()["action"] == "build_legal_graph"
    data["legal_graph"] = True
    assert manager._get_formalization_action()["action"] == "perform_neurosymbolic_matching"
    data["matching_complete"] = True
    assert manager._get_formalization_action()["action"] == "generate_formal_complaint"
    data["formal_complaint"] = "done"
    assert manager._get_formalization_action()["action"] == "complete_formalization"


def test_phase_completion_checks_for_each_phase():
    manager = PhaseManager()
    assert not manager._is_intake_complete()
    manager.phase_data[ComplaintPhase.INTAKE].update({
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 0,
        "denoising_converged": True,
    })
    assert manager._is_intake_complete()
    assert not manager._is_evidence_complete()
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "claim_support_packets": {
            "c": {"elements": [{"element_id": "1", "support_status": "supported"}]}
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
    })
    assert manager._is_evidence_complete()
    assert not manager._is_formalization_complete()
    manager.phase_data[ComplaintPhase.FORMALIZATION].update({
        "legal_graph": {"nodes": []},
        "matching_complete": True,
        "formal_complaint": {},
    })
    assert manager._is_formalization_complete()


def test_actionable_alignment_tasks_filters_reviewable_statuses():
    manager = PhaseManager()
    data = {"alignment_evidence_tasks": [
        {"support_status": "unsupported", "resolution_status": "awaiting_complainant_record"},
        {"support_status": "unsupported", "resolution_status": "manual_review_pending"},
        {"support_status": "contradicted", "resolution_status": ""},
    ]}
    tasks = manager._get_actionable_alignment_tasks(data)
    assert len(tasks) == 1


def test_alignment_promotion_drift_action_requires_flags():
    manager = PhaseManager()
    data = {"alignment_promotion_drift_summary": {"drift_flag": False}, "alignment_task_updates": []}
    assert manager._get_alignment_promotion_drift_action(data) is None


def test_next_packet_evidence_action_none_when_no_candidates():
    manager = PhaseManager()
    packets = {"claim": {"claim_type": "Housing", "elements": [{"element_id": "1", "support_status": "supported"}]}}
    assert manager._get_next_packet_evidence_action(packets, {"alignment_evidence_tasks": []}) is None


def test_transition_metrics_empty_history():
    manager = PhaseManager()
    assert manager.total_phase_transitions() == 0
    assert manager.phase_transition_frequency() == {}
    assert manager.most_visited_phase() == "none"


def test_convergence_requires_window_entries():
    manager = PhaseManager()
    manager.record_iteration(0.1, {})
    assert not manager.has_converged(window=2, threshold=0.001)


def test_phase_data_access_error_handling():
    manager = PhaseManager()
    with pytest.raises(KeyError):
        manager.update_phase_data("bogus", "key", "value")
    with pytest.raises(KeyError):
        manager.get_phase_data("bogus")


def test_phase_data_coverage_zero_when_empty():
    manager = PhaseManager()
    assert manager.phase_data_coverage() == 0.0
