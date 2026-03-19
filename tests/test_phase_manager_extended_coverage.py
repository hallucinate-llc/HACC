import sys
import time
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases.phase_manager import ComplaintPhase, PhaseManager


def _build_sample_intake_case() -> Dict[str, Any]:
    return {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": ["dates"]},
            "actors": {"status": "present"},
            "conduct": {"status": "present"},
            "harm": {"status": "missing"},
            "remedy": {"status": "present"},
            "proof_leads": {"status": "present"},
            "claim_elements": {"status": "present"},
        },
        "contradiction_queue": [
            {"status": "open", "severity": "blocking", "contradiction_count": 2},
            {"status": "needs_manual_review", "severity": "blocking"},
        ],
        "candidate_claims": [
            {"claim_type": "eviction", "confidence": 0.65, "ambiguity_flags": []}
        ],
        "canonical_facts": [{"fact": "fact"}],
        "proof_leads": [{"lead": "lead"}],
        "complainant_summary_confirmation": {"confirmed": False},
        "summary_snapshots": ["snapshot"],
    }


def test_extract_intake_gap_types_combines_sources():
    manager = PhaseManager()
    data = {
        "intake_gap_types": ["missing_timeline", "", "missing_timeline"],
        "current_gaps": [
            {"type": "missing_responsible_party"},
            {"type": "missing_timeline"},
            {"type": ""},
        ],
    }
    gap_types = manager._extract_intake_gap_types(data)
    assert gap_types == ["missing_timeline", "missing_responsible_party"]


def test_extract_intake_contradictions_supports_various_formats():
    manager = PhaseManager()
    candidates = manager._extract_intake_contradictions(
        {"intake_contradictions": {"candidates": [{"issue": "A"}, "ignore"]}}
    )
    assert candidates == [{"issue": "A"}]
    single = manager._extract_intake_contradictions({"intake_contradictions": {"unexpected": "value"}})
    assert single == [{"unexpected": "value"}]
    listed = manager._extract_intake_contradictions({
        "intake_contradictions": [{"status": "open"}, {"status": "resolved"}]
    })
    assert listed == [{"status": "open"}, {"status": "resolved"}]


def test_active_intake_contradictions_excludes_resolved():
    manager = PhaseManager()
    queue = [
        {"status": "open"},
        {"current_resolution_status": "resolved"},
        {"status": "needs_manual_review"},
    ]
    active = manager._active_intake_contradictions(queue)
    assert len(active) == 2
    assert all(item["status"] in {"open", "needs_manual_review"} for item in active)


def test_contradiction_resolution_helpers():
    manager = PhaseManager()
    resolved = {"status": "resolved"}
    escalated = {"status": "needs_manual_review"}
    assert manager._is_intake_contradiction_resolved(resolved)
    assert manager._is_intake_contradiction_resolved_or_escalated(escalated)
    assert not manager._is_intake_contradiction_resolved({"status": "open"})


def test_extract_intake_case_file_handles_missing_entries():
    manager = PhaseManager()
    assert manager._extract_intake_case_file({"intake_case_file": {"foo": "bar"}}) == {
        "foo": "bar"
    }
    assert manager._extract_intake_case_file({"intake_case_file": []}) == {}


def test_collect_intake_section_blockers_reports_blockers_and_counts():
    manager = PhaseManager()
    case_file = _build_sample_intake_case()
    result = manager._collect_intake_section_blockers(case_file)
    assert "missing_core_chronology" in result["blockers"]
    assert "complainant_summary_confirmation_required" in result["blockers"]
    assert result["candidate_claim_count"] == 1
    assert result["proof_lead_count"] == 1
    assert len(result["blocking_contradictions"]) == 1
    assert len(result["escalated_blocking_contradictions"]) == 1


def test_build_intake_readiness_tracks_readiness_and_blockers():
    manager = PhaseManager()
    intake_case_file = _build_sample_intake_case()
    data = {
        "knowledge_graph": {"nodes": []},
        "dependency_graph": {"edges": []},
        "current_gaps": [{"type": "missing_timeline"}],
        "remaining_gaps": 2,
        "denoising_converged": True,
        "intake_case_file": intake_case_file,
        "contradictions_unresolved": True,
        "intake_blockers": ["external_blocker"],
    }
    readiness = manager._build_intake_readiness(data)
    assert readiness["intake_readiness_score"] <= 1.0
    assert "contradiction_unresolved" in readiness["intake_readiness_blockers"]
    assert "missing_core_chronology" in readiness["intake_readiness_blockers"]
    assert readiness["candidate_claim_count"] == 1


def test_refresh_phase_derived_state_updates_intake_and_evidence():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update(
        {"knowledge_graph": {"nodes": []}, "dependency_graph": {}, "remaining_gaps": 0}
    )
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    assert "intake_readiness_score" in manager.phase_data[ComplaintPhase.INTAKE]

    manager.phase_data[ComplaintPhase.EVIDENCE].update(
        {
            "claim_support_packets": {
                "packet": {
                    "claim_type": "eviction",
                    "elements": [{
                        "element_id": "elem",
                        "support_status": "supported",
                        "parse_quality_flags": [],
                    }]
                }
            },
            "alignment_evidence_tasks": [],
        }
    )
    manager._refresh_phase_derived_state(ComplaintPhase.EVIDENCE)
    assert "proof_readiness_score" in manager.phase_data[ComplaintPhase.EVIDENCE]


def test_get_intake_readiness_returns_computed_view():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = {}
    readiness = manager.get_intake_readiness()
    assert "score" in readiness
    assert isinstance(readiness["blockers"], list)


def test_build_evidence_packet_summary_counts_elements_and_temporal_tasks():
    manager = PhaseManager()
    data = {
        "claim_support_packets": {
            "eviction": {
                "claim_type": "Eviction",
                "elements": [
                    {
                        "element_id": "elem1",
                        "support_status": "unsupported",
                        "recommended_next_step": "collect_documents",
                        "contradiction_count": 0,
                    }
                ],
            }
        },
        "alignment_evidence_tasks": [
            {
                "claim_type": "Eviction",
                "claim_element_id": "elem1",
                "support_status": "unsupported",
                "resolution_status": "awaiting_complainant_record",
                "action": "fill_temporal_chronology_gap",
                "temporal_rule_status": "partial",
                "temporal_rule_blocking_reasons": ["lack proof"],
            }
        ],
    }
    summary = manager._build_evidence_packet_summary(data)
    assert summary["claim_support_packet_count"] == 1
    assert summary["temporal_gap_task_count"] == 1
    assert summary["claim_support_reviewable_escalation_count"] >= 1
    assert summary["proof_readiness_score"] >= 0.0


def test_normalize_and_resolve_evidence_escalation_status():
    manager = PhaseManager()
    assert manager._normalize_evidence_escalation_status(" PROMOTED ") == "promoted"
    element = {
        "escalation_status": "",
        "resolution_status": "Resolved",
        "recommended_next_step": "finalize",
    }
    assert manager._resolve_evidence_escalation_status(element) == "resolved"


def test_get_actionable_alignment_tasks_filters_nonactionable():
    manager = PhaseManager()
    data = {
        "alignment_evidence_tasks": [
            {"support_status": "supported", "resolution_status": "resolved"},
            {
                "support_status": "unsupported",
                "resolution_status": "awaiting_complainant_record",
            },
            {
                "support_status": "contradicted",
                "resolution_status": "resolved",
            },
        ]
    }
    actionable = manager._get_actionable_alignment_tasks(data)
    assert len(actionable) == 1
    assert actionable[0]["support_status"] == "contradicted"


def test_get_alignment_promotion_drift_action_focuses_single_claim():
    manager = PhaseManager()
    data = {
        "alignment_promotion_drift_summary": {
            "drift_flag": True,
            "promoted_count": 1,
            "pending_conversion_count": 0,
        },
        "alignment_task_update_history": [
            {
                "task_id": "t1",
                "claim_type": "Eviction",
                "claim_element_id": "elem1",
                "resolution_status": "promoted_to_document",
                "evidence_sequence": 1,
            }
        ],
        "claim_support_recommended_actions": ["verify_doc"],
    }
    action = manager._get_alignment_promotion_drift_action(data)
    assert action is not None
    assert action["action"] == "validate_promoted_support"
    assert action["claim_type"] == "Eviction"
    assert action["claim_element_id"] == "elem1"


def test_get_next_packet_evidence_action_prefers_recommended_step():
    manager = PhaseManager()
    packets = {
        "eviction": {
            "claim_type": "Eviction",
            "elements": [
                {
                    "element_id": "elem1",
                    "support_status": "unsupported",
                    "recommended_next_step": "collect_documents",
                }
            ],
        }
    }
    data = {"claim_support_packets": packets}
    action = manager._get_next_packet_evidence_action(packets, data)
    assert action["action"] == "collect_documents"
    assert action["claim_type"] == "Eviction"


def test_get_next_action_variants_for_each_phase():
    manager = PhaseManager()
    intake_action = manager.get_next_action()
    assert intake_action["action"] == "build_knowledge_graph"

    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.phase_data[ComplaintPhase.EVIDENCE].update(
        {
            "claim_support_packets": {
                "eviction": {
                    "claim_type": "Eviction",
                    "elements": [
                        {
                            "element_id": "elem1",
                            "support_status": "unsupported",
                            "recommended_next_step": "collect_documents",
                        }
                    ],
                }
            },
            "claim_support_explicit_status_count": 1,
            "claim_support_element_count": 1,
            "claim_support_blocking_contradictions": 0,
        }
    )
    evidence_action = manager.get_next_action()
    assert evidence_action["action"] == "collect_documents"

    manager.current_phase = ComplaintPhase.FORMALIZATION
    formal_action = manager.get_next_action()
    assert formal_action["action"] == "build_legal_graph"


def test_update_phase_data_refreshes_derived_state():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"nodes": []})
    assert manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"]
    assert "intake_readiness_score" in manager.phase_data[ComplaintPhase.INTAKE]


def test_get_phase_data_with_and_without_key():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE]["foo"] = "bar"
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "foo") == "bar"
    assert isinstance(manager.get_phase_data(ComplaintPhase.INTAKE), dict)


def test_record_iteration_and_convergence_logic():
    manager = PhaseManager()
    manager.record_iteration(0.2, {"metric": 1})
    manager.record_iteration(0.25, {"metric": 2})
    manager.record_iteration(0.22, {"metric": 3})
    assert manager.iteration_count == 3
    assert len(manager.loss_history) == 3
    assert manager.has_converged(window=3, threshold=0.05)


def test_iteration_and_loss_statistics_calculated():
    manager = PhaseManager()
    manager.loss_history = [
        {"phase": "intake", "loss": 0.3},
        {"phase": "intake", "loss": 0.4},
        {"phase": "evidence", "loss": 0.2},
    ]
    manager.iteration_count = 3
    assert manager.total_iterations() == 3
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 2
    assert abs(manager.average_loss() - (0.3 + 0.4 + 0.2) / 3) < 1e-6
    assert manager.minimum_loss() == 0.2


def test_phase_history_metrics_and_serialization():
    manager = PhaseManager()
    manager.phase_history = [
        {"from_phase": "intake", "to_phase": "evidence"},
        {"from_phase": "evidence", "to_phase": "intake"},
        {"from_phase": "intake", "to_phase": "evidence"},
    ]
    assert manager.total_phase_transitions() == 3
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 2
    freq = manager.phase_transition_frequency()
    assert freq["evidence"] == 2
    assert manager.most_visited_phase() == "evidence"

    snapshot = manager.to_dict()
    restored = PhaseManager.from_dict(snapshot, mediator="mediator-marker")
    assert restored.current_phase == manager.current_phase
    assert restored.phase_history == manager.phase_history
    assert restored.mediator == "mediator-marker"


def test_phase_data_key_checks_and_coverage():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE]["foo"] = 1
    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "foo")
    assert manager.phase_data_coverage() == 1 / 3


def test_get_next_action_intake_performance():
    manager = PhaseManager()
    start = time.perf_counter()
    for _ in range(20):
        manager.get_next_action()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1
