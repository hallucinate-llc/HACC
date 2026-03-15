import sys
from pathlib import Path
import time
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases import phase_manager as pm
from complaint_phases.phase_manager import PhaseManager, ComplaintPhase


def test_extract_intake_gap_types_dedupes_and_normalizes():
    manager = PhaseManager()
    data = {
        "intake_gap_types": [" missing_timeline ", "missing_timeline", None, ""],
        "current_gaps": [
            {"type": "missing_responsible_party"},
            {"type": " "},
            {"type": None},
            "not-a-dict",
            {"type": "missing_impact_remedy"},
        ],
    }
    assert manager._extract_intake_gap_types(data) == [
        "missing_timeline",
        "missing_responsible_party",
        "missing_impact_remedy",
    ]


def test_extract_intake_contradictions_handles_dict_and_list():
    manager = PhaseManager()
    data = {
        "intake_contradictions": {
            "candidates": [{"id": 1}, "bad", {"id": 2}],
        }
    }
    assert manager._extract_intake_contradictions(data) == [{"id": 1}, {"id": 2}]

    data = {"intake_contradictions": {"detail": "x"}}
    assert manager._extract_intake_contradictions(data) == [{"detail": "x"}]

    data = {"intake_contradictions": {}}
    assert manager._extract_intake_contradictions(data) == []

    data = {"intake_contradictions": [{"id": 3}, "bad"]}
    assert manager._extract_intake_contradictions(data) == [{"id": 3}]

    data = {"intake_contradictions": "not-a-collection"}
    assert manager._extract_intake_contradictions(data) == []


def test_build_intake_readiness_all_ready():
    manager = PhaseManager()
    data = {
        "knowledge_graph": {"nodes": []},
        "dependency_graph": {"edges": []},
        "remaining_gaps": 3,
        "denoising_converged": True,
    }
    readiness = manager._build_intake_readiness(data)
    assert readiness["intake_ready"] is True
    assert readiness["intake_readiness_blockers"] == []
    assert readiness["intake_readiness_score"] == 1.0
    assert readiness["intake_contradiction_count"] == 0
    assert readiness["intake_contradictions"] == []


def test_build_intake_readiness_with_gaps_and_contradictions():
    manager = PhaseManager()
    data = {
        "remaining_gaps": 5,
        "denoising_converged": False,
        "intake_gap_types": ["missing_timeline", "missing_responsible_party", "unsupported_claim"],
        "contradictions_unresolved": True,
        "intake_contradictions": [{"summary": "conflict"}],
        "intake_blockers": ["custom_blocker", "custom_blocker"],
    }
    readiness = manager._build_intake_readiness(data)
    assert readiness["intake_ready"] is False
    assert readiness["intake_contradiction_count"] == 1
    assert readiness["intake_contradictions"] == [{"summary": "conflict"}]
    assert readiness["intake_readiness_criteria"]["timeline_captured"] is False
    assert readiness["intake_readiness_criteria"]["responsible_party_identified"] is False
    assert readiness["intake_readiness_criteria"]["proof_leads_present"] is False
    assert readiness["intake_readiness_criteria"]["contradictions_resolved"] is False
    assert readiness["intake_readiness_blockers"] == [
        "missing_knowledge_graph",
        "missing_dependency_graph",
        "unresolved_gaps",
        "denoising_not_converged",
        "missing_timeline",
        "missing_actor",
        "missing_proof_leads",
        "contradiction_unresolved",
        "custom_blocker",
    ]


def test_refresh_phase_derived_state_updates_intake_data():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    assert "intake_readiness_score" in manager.phase_data[ComplaintPhase.INTAKE]
    assert manager.phase_data[ComplaintPhase.INTAKE]["intake_readiness_score"] < 1.0


def test_get_intake_readiness_returns_copies():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    readiness = manager.get_intake_readiness()
    readiness["blockers"].append("mutate")
    readiness["criteria"]["x"] = False
    readiness["contradictions"].append({"id": 9})
    fresh = manager.get_intake_readiness()
    assert "mutate" not in fresh["blockers"]
    assert "x" not in fresh["criteria"]
    assert {"id": 9} not in fresh["contradictions"]


def test_get_intake_action_with_semantic_blockers():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "intake_gap_types", ["missing_timeline"])
    action = manager._get_intake_action()
    assert action["action"] == "address_gaps"
    assert "intake_readiness_score" in action
    assert "intake_blockers" in action


def test_get_intake_action_remaining_gaps_threshold():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", pm._INTAKE_GAPS_THRESHOLD + 1)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    action = manager._get_intake_action()
    assert action["action"] == "address_gaps"


def test_get_evidence_action_threshold_edge():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", pm._EVIDENCE_GAP_RATIO_THRESHOLD)
    assert manager._get_evidence_action() == {"action": "complete_evidence"}


def test_get_formalization_action_with_empty_legal_graph():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", {})
    assert manager._get_formalization_action() == {"action": "build_legal_graph"}
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", {"nodes": []})
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "text")
    assert manager._get_formalization_action() == {"action": "complete_formalization"}


def test_can_advance_to_unknown_phase_returns_false():
    manager = PhaseManager()
    assert manager._can_advance_to("not-a-phase") is False


def test_from_dict_missing_keys_raises():
    data = {
        "current_phase": "intake",
        "phase_history": [],
        "phase_data": {"intake": {}},
        "iteration_count": 0,
    }
    with pytest.raises(KeyError):
        PhaseManager.from_dict(data)


def test_to_dict_roundtrip_with_contradictions():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "intake_contradictions", {"detail": "x"})
    data = manager.to_dict()
    clone = PhaseManager.from_dict(data)
    assert clone.phase_data[ComplaintPhase.INTAKE]["intake_contradictions"] == {"detail": "x"}


@pytest.mark.performance
def test_build_intake_readiness_performance():
    manager = PhaseManager()
    data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 2,
        "denoising_converged": True,
        "intake_gap_types": ["missing_timeline"] * 1000 + ["unsupported_claim"] * 1000,
        "current_gaps": [{"type": "missing_responsible_party"}] * 1000,
        "intake_blockers": ["custom"] * 1000,
        "intake_contradictions": {"candidates": [{"id": i} for i in range(500)]},
    }
    start = time.perf_counter()
    readiness = manager._build_intake_readiness(data)
    elapsed = time.perf_counter() - start
    assert readiness["intake_contradiction_count"] == 500
    assert elapsed < 0.5


@pytest.mark.performance
def test_extract_intake_gap_types_performance():
    manager = PhaseManager()
    data = {
        "intake_gap_types": [f"gap_{i}" for i in range(1000)],
        "current_gaps": [{"type": f"gap_{i}"} for i in range(1000, 2000)],
    }
    start = time.perf_counter()
    gap_types = manager._extract_intake_gap_types(data)
    elapsed = time.perf_counter() - start
    assert len(gap_types) == 2000
    assert elapsed < 0.3
