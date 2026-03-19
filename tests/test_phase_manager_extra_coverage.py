import sys
from pathlib import Path
import time

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

import complaint_phases.phase_manager as pm
from complaint_phases.phase_manager import ComplaintPhase, PhaseManager


try:
    import pytest_benchmark  # noqa: F401
    _HAS_BENCHMARK = True
except Exception:
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


def _complete_intake(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "intake_case_file", _ready_intake_case_file())


def _complete_evidence(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.1)


def _sample_intake_case_file():
    return {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": ["date"]},
            "actors": {"status": "present", "missing_items": []},
            "conduct": {"status": "present"},
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
            {"claim_type": "Breach", "confidence": 0.7, "ambiguity_flags": []},
            {"claim_type": "Negligence", "confidence": 0.65, "ambiguity_flags": ["similar"]},
        ],
        "canonical_facts": [{"fact": "f1"}],
        "proof_leads": [{"lead": "evidence"}],
        "complainant_summary_confirmation": {"confirmed": False},
        "summary_snapshots": [{"snapshot": "hey"}],
    }


def _ready_intake_case_file():
    return {
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
        "candidate_claims": [{"claim_type": "breach", "confidence": 0.8, "ambiguity_flags": []}],
        "canonical_facts": [{"fact": "f1"}],
        "proof_leads": [{"lead": "evidence"}],
        "summary_snapshots": [],
        "contradiction_queue": [],
        "complainant_summary_confirmation": {"confirmed": True},
    }


def _sample_evidence_data():
    return {
        "claim_support_packets": {
            "claim_a": {
                "claim_type": "Breach",
                "elements": [
                    {
                        "element_id": "E1",
                        "support_status": "supported",
                        "parse_quality_flags": [],
                    },
                    {
                        "element_id": "E2",
                        "support_status": "unsupported",
                        "contradiction_count": 1,
                        "escalation_status": "awaiting_testimony",
                        "recommended_next_step": "fill_evidence_gaps",
                    },
                ],
            }
        },
        "alignment_evidence_tasks": [
            {
                "claim_type": "Breach",
                "claim_element_id": "E2",
                "support_status": "unsupported",
                "action": "fill_temporal_chronology_gap",
                "resolution_status": "awaiting_testimony",
                "temporal_rule_status": "partial",
                "temporal_rule_blocking_reasons": ["missing_document"],
            }
        ],
        "alignment_promotion_drift_summary": {
            "drift_flag": True,
            "promoted_count": 1,
            "pending_conversion_count": 1,
        },
        "alignment_task_update_history": [
            {
                "task_id": "task-1",
                "claim_type": "Breach",
                "claim_element_id": "E2",
                "resolution_status": "promoted_to_testimony",
                "evidence_sequence": 2,
            }
        ],
        "claim_support_recommended_actions": ["validate_support"],
    }


@pytest.fixture
def manager():
    return PhaseManager()


def test_init_sets_defaults():
    manager = PhaseManager()
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history == []


def test_utc_now_isoformat_contains_timestamp():
    value = pm._utc_now_isoformat()
    assert "T" in value and value.endswith("+00:00")


def test_extract_intake_gap_types_combines_inputs(manager):
    data = {
        "intake_gap_types": ["missing_timeline", "missing_responsible_party"],
        "current_gaps": [
            {"type": "missing_timeline"},
            {"type": "missing_impact_remedy"},
            "invalid"
        ],
    }
    gaps = manager._extract_intake_gap_types(data)
    assert "missing_timeline" in gaps
    assert "missing_responsible_party" in gaps
    assert "missing_impact_remedy" in gaps
    assert len(gaps) == 3


def test_extract_intake_contradictions_accepts_dict_or_list(manager):
    data = {"intake_contradictions": {"candidates": [
        {"status": "open"},
        "not-a-dict"
    ]}}
    contradictions = manager._extract_intake_contradictions(data)
    assert len(contradictions) == 1
    assert contradictions[0]["status"] == "open"
    data = {"intake_contradictions": ["x", {"status": "closed"}]}
    contradictions = manager._extract_intake_contradictions(data)
    assert contradictions == [{"status": "closed"}]


def test_active_contradictions_and_resolution_checks(manager):
    queue = [
        {"status": "open", "severity": "blocking"},
        {"status": "resolved"},
        {"status": "escalated"},
    ]
    active = manager._active_intake_contradictions(queue)
    assert len(active) == 2
    assert manager._is_intake_contradiction_resolved(queue[1]) is True
    assert manager._is_intake_contradiction_resolved_or_escalated(queue[2]) is True


def test_phase_completion_and_advancement_logic(manager):
    assert manager._can_advance_to(ComplaintPhase.INTAKE)
    assert not manager._can_advance_to(ComplaintPhase.EVIDENCE)
    _complete_intake(manager)
    assert manager._is_intake_complete()
    assert manager._can_advance_to(ComplaintPhase.EVIDENCE)
    assert not manager._is_evidence_complete()
    _complete_evidence(manager)
    assert manager._is_evidence_complete()
    assert manager._can_advance_to(ComplaintPhase.FORMALIZATION)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", {"nodes": []})
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "ok")
    assert manager._is_formalization_complete()
    assert manager.is_phase_complete(ComplaintPhase.EVIDENCE)
    assert not manager.is_phase_complete("bogus")


def test_update_and_get_phase_data(manager):
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "counter", 3)
    assert manager.get_phase_data(ComplaintPhase.EVIDENCE, "counter") == 3
    assert manager.get_phase_data(ComplaintPhase.EVIDENCE)["counter"] == 3


def test_phase_data_access_invalid_phase_raises():
    manager = PhaseManager()
    with pytest.raises(KeyError):
        manager.update_phase_data("bogus", "k", 1)
    with pytest.raises(KeyError):
        manager.get_phase_data("bogus")


def test_collect_intake_section_blockers_and_criteria(manager):
    intake_case = _sample_intake_case_file()
    readiness = manager._collect_intake_section_blockers(intake_case)
    assert readiness["sections"]["chronology"]["status"] == "missing"
    assert "missing_core_chronology" in readiness["blockers"]
    assert readiness["criteria"]["blocking_contradictions_resolved"] is False
    assert readiness["criteria"]["claim_disambiguation_resolved"] is False


def test_build_intake_readiness_includes_structured_blocks(manager):
    data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 2,
        "denoising_converged": True,
        "intake_gap_types": ["missing_timeline"],
        "intake_case_file": _sample_intake_case_file(),
        "intake_blockers": ["custom_blocker"],
    }
    readiness = manager._build_intake_readiness(data)
    assert readiness["intake_readiness_score"] <= 1.0
    assert "missing_timeline" in readiness["intake_readiness_blockers"]
    assert "custom_blocker" in readiness["intake_readiness_blockers"]
    assert readiness["intake_contradiction_count"] > 0


def test_refresh_phase_derived_state_populates_metrics(manager):
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = True
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    assert "intake_readiness_score" in manager.phase_data[ComplaintPhase.INTAKE]


def test_get_intake_readiness_copy(manager):
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "intake_case_file", _ready_intake_case_file())
    readiness = manager.get_intake_readiness()
    assert readiness["score"] == 1.0
    assert readiness["blockers"] == []


def test_build_evidence_packet_summary_counts_and_ratios(manager):
    data = _sample_evidence_data()
    summary = manager._build_evidence_packet_summary(data)
    assert summary["claim_support_packet_count"] == 1
    assert summary["reviewable_escalation_ratio"] >= 0.0
    assert summary["claim_support_blocking_contradictions"] == 0
    assert summary["proof_readiness_score"] <= 1.0


def test_evidence_escalation_resolution_helpers(manager):
    assert manager._normalize_evidence_escalation_status(" PROMOTED_to_Testimony ") == "promoted_to_testimony"
    element = {"escalation_status": "", "resolution_status": "partial"}
    resolved = manager._resolve_evidence_escalation_status(element, "promoted")
    assert resolved == "partial"


def test_actionable_alignment_tasks_filters(manager):
    data = {
        "alignment_evidence_tasks": [
            {"support_status": "unsupported", "resolution_status": ""},
            {"support_status": "contradicted", "resolution_status": "awaiting_testimony"},
            {"support_status": "supported", "resolution_status": ""},
        ]
    }
    result = manager._get_actionable_alignment_tasks(data)
    assert len(result) == 2


def test_alignment_promotion_drift_action_detects_focus(manager):
    data = _sample_evidence_data()
    action = manager._get_alignment_promotion_drift_action(data)
    assert action is not None
    assert action["action"] == "validate_promoted_support"
    assert action["promoted_count"] == 1


def test_alignment_drift_returns_none_when_empty(manager):
    assert manager._get_alignment_promotion_drift_action({}) is None


def test_next_packet_evidence_action_skips_reviewable(manager):
    packets = {
        "claim": {
            "claim_type": "Breach",
            "elements": [
                {"element_id": "E3", "support_status": "unsupported", "recommended_next_step": "guide"},
            ],
        }
    }
    data = {"alignment_evidence_tasks": [], "claim_support_recommended_actions": []}
    action = manager._get_next_packet_evidence_action(packets, data)
    assert action["support_status"] == "unsupported"


def test_phase_transitions_and_statistics(manager):
    _complete_intake(manager)
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    _complete_evidence(manager)
    assert manager.advance_to_phase(ComplaintPhase.FORMALIZATION)
    manager.advance_to_phase(ComplaintPhase.INTAKE)
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    assert manager.total_phase_transitions() == 4
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 2
    freq = manager.phase_transition_frequency()
    assert freq.get("intake") == 1
    assert manager.most_visited_phase() == "evidence"


def test_iteration_statistics_and_convergence(manager):
    manager.record_iteration(1.0, {})
    manager.record_iteration(0.8, {})
    manager.record_iteration(0.9, {})
    assert manager.total_iterations() == 3
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 3
    assert pytest.approx(manager.average_loss(), rel=1e-6) == (1.0 + 0.8 + 0.9) / 3
    assert manager.minimum_loss() == 0.8
    assert manager.has_converged(window=3, threshold=0.5)


def test_get_next_action_for_each_phase(manager):
    # intake default
    action = manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    _complete_intake(manager)
    manager.iteration_count = pm._DENOISING_MAX_ITERATIONS + 1
    action = manager.get_next_action()
    assert action["action"] in {"complete_intake", "continue_denoising"}
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.phase_data[ComplaintPhase.EVIDENCE].update({
        "claim_support_packets": {
            "claim": {
                "claim_type": "Breach",
                "elements": [
                    {"element_id": "E4", "support_status": "unsupported", "recommended_next_step": "fill"}
                ],
            }
        },
        "claim_support_element_count": 1,
        "claim_support_explicit_status_count": 1,
        "claim_support_blocking_contradictions": 0,
        "claim_support_unresolved_without_review_path_count": 0,
        "claim_support_recommended_actions": ["act"],
    })
    evidence_action = manager.get_next_action()
    assert evidence_action["action"] == "fill"
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.phase_data[ComplaintPhase.FORMALIZATION].update({
        "legal_graph": {"nodes": []},
        "matching_complete": True,
        "formal_complaint": "text",
    })
    formal_action = manager.get_next_action()
    assert formal_action["action"] == "complete_formalization"


def test_to_dict_from_dict_roundtrip(manager):
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"id": "g"})
    manager.record_iteration(0.5, {"k": 1})
    snapshot = manager.to_dict()
    restored = PhaseManager.from_dict(snapshot)
    assert restored.current_phase == manager.current_phase
    assert restored.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"]["id"] == "g"


def test_phase_data_key_presence_and_coverage(manager):
    assert not manager.has_phase_data_key(ComplaintPhase.INTAKE, "missing")
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "foo", "bar")
    assert manager.has_phase_data_key(ComplaintPhase.EVIDENCE, "foo")
    assert pytest.approx(manager.phase_data_coverage(), rel=1e-6) == 1 / 3


def test_phase_manager_performance_benchmarks(manager, benchmark):
    intake_data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "intake_gap_types": ["missing_timeline"],
        "denoising_converged": True,
        "remaining_gaps": 1,
        "intake_case_file": _sample_intake_case_file(),
    }
    benchmark(manager._build_intake_readiness, intake_data)
    evidence_data = _sample_evidence_data()
    benchmark(manager._build_evidence_packet_summary, evidence_data)
