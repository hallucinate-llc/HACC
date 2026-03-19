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


def _complete_intake(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)


def _complete_evidence(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.2)


def test_can_advance_to_unknown_phase_false():
    manager = PhaseManager()
    assert manager._can_advance_to("bogus") is False


def test_is_phase_complete_fallback_to_class_mapping():
    manager = PhaseManager()
    _complete_intake(manager)
    manager._phase_completion_checks = {}
    assert manager.is_phase_complete(ComplaintPhase.INTAKE) is True


def test_is_phase_complete_missing_mappings_false(monkeypatch):
    manager = PhaseManager()
    manager._phase_completion_checks = {}
    monkeypatch.setattr(pm.PhaseManager, "_PHASE_COMPLETION_CHECKS", {})
    assert manager.is_phase_complete(ComplaintPhase.INTAKE) is False


def test_get_next_action_fallback_to_class_mapping():
    manager = PhaseManager()
    manager._phase_action_getters = {}
    action = manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    assert "intake_readiness_score" in action


def test_get_next_action_missing_mappings_unknown(monkeypatch):
    manager = PhaseManager()
    manager._phase_action_getters = {}
    monkeypatch.setattr(pm.PhaseManager, "_PHASE_ACTION_GETTERS", {})
    assert manager.get_next_action() == {"action": "unknown"}


def test_record_iteration_stores_metrics_and_timestamp(monkeypatch):
    manager = PhaseManager()
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2030-01-01T00:00:00+00:00")
    manager.record_iteration(0.25, {"precision": 0.9})
    assert manager.loss_history[-1] == {
        "iteration": 1,
        "loss": 0.25,
        "phase": "intake",
        "metrics": {"precision": 0.9},
        "timestamp": "2030-01-01T00:00:00+00:00",
    }


def test_has_converged_window_zero_raises():
    manager = PhaseManager()
    manager.record_iteration(1.0, {})
    assert manager.has_converged(window=0, threshold=0.1) is True


def test_from_dict_missing_keys_raises():
    data = {
        "current_phase": "intake",
        "phase_history": [],
        "phase_data": {"intake": {}},
        "iteration_count": 0,
    }
    with pytest.raises(KeyError):
        PhaseManager.from_dict(data)


def test_transitions_to_phase_zero_when_none():
    manager = PhaseManager()
    _complete_intake(manager)
    manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    assert manager.transitions_to_phase(ComplaintPhase.FORMALIZATION) == 0


def test_phase_data_coverage_full():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "a", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "b", 2)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "c", 3)
    assert manager.phase_data_coverage() == 1.0


def test_get_phase_data_returns_full_dict_reference():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "k", "v")
    data = manager.get_phase_data(ComplaintPhase.INTAKE)
    data["k"] = "changed"
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "k") == "changed"


def test_advance_to_phase_records_iteration_at_time(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    _complete_evidence(manager)
    manager.record_iteration(0.9, {})
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2040-01-01T00:00:00+00:00")
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
    assert manager.phase_history[-1]["iteration"] == 1


@pytest.mark.performance
def test_get_next_action_intake_performance():
    manager = PhaseManager()
    start = time.perf_counter()
    for _ in range(5000):
        manager.get_next_action()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.75


@pytest.mark.performance
def test_average_loss_performance():
    manager = PhaseManager()
    for i in range(5000):
        manager.record_iteration(1.0 - (i * 0.0001), {})
    start = time.perf_counter()
    value = manager.average_loss()
    elapsed = time.perf_counter() - start
    assert value > 0.0
    assert elapsed < 0.2
