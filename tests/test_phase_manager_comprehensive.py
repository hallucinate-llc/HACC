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


def test_init_maps_and_defaults():
    manager = PhaseManager()
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history == []
    assert manager.iteration_count == 0
    assert manager.loss_history == []
    assert set(manager.phase_data.keys()) == {
        ComplaintPhase.INTAKE,
        ComplaintPhase.EVIDENCE,
        ComplaintPhase.FORMALIZATION,
    }
    assert set(manager._phase_action_getters.keys()) == {
        ComplaintPhase.INTAKE,
        ComplaintPhase.EVIDENCE,
        ComplaintPhase.FORMALIZATION,
    }
    assert set(manager._phase_completion_checks.keys()) == {
        ComplaintPhase.INTAKE,
        ComplaintPhase.EVIDENCE,
        ComplaintPhase.FORMALIZATION,
    }
    assert manager._phase_action_getters[ComplaintPhase.INTAKE].__name__ == "_get_intake_action"
    assert manager._phase_completion_checks[ComplaintPhase.INTAKE].__name__ == "_is_intake_complete"


def test_get_current_phase_after_transition(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2024-01-01T00:00:00+00:00")
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
    assert manager.get_current_phase() == ComplaintPhase.EVIDENCE


def test_advance_to_phase_records_iteration_count(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    manager.iteration_count = 7
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2024-01-02T00:00:00+00:00")
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
    assert manager.phase_history[-1]["iteration"] == 7


def test_is_phase_complete_fallback_when_instance_entry_none():
    manager = PhaseManager()
    manager._phase_completion_checks = {ComplaintPhase.INTAKE: None}
    _complete_intake(manager)
    assert manager.is_phase_complete(ComplaintPhase.INTAKE) is True


def test_get_next_action_fallback_when_instance_entry_none():
    manager = PhaseManager()
    manager._phase_action_getters = {ComplaintPhase.INTAKE: None}
    action = manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    assert "intake_readiness_score" in action


def test_get_phase_data_falsey_key_returns_full_map():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"a": 1})
    data = manager.get_phase_data(ComplaintPhase.INTAKE, 0)
    assert data["knowledge_graph"] == {"a": 1}


def test_record_iteration_increments_and_tracks_phase(monkeypatch):
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2024-01-03T00:00:00+00:00")
    manager.record_iteration(0.9, {"k": 2})
    assert manager.iteration_count == 1
    entry = manager.loss_history[-1]
    assert entry["phase"] == "evidence"
    assert entry["timestamp"] == "2024-01-03T00:00:00+00:00"


def test_has_converged_window_larger_than_history():
    manager = PhaseManager()
    manager.record_iteration(1.0, {})
    manager.record_iteration(0.99, {})
    assert manager.has_converged(window=3, threshold=0.5) is False


def test_has_converged_window_zero_raises():
    manager = PhaseManager()
    manager.record_iteration(1.0, {})
    assert manager.has_converged(window=0, threshold=0.1) is True


def test_average_and_minimum_loss_with_missing_loss_values():
    manager = PhaseManager()
    manager.loss_history = [{"iteration": 1}, {"iteration": 2, "loss": 0.5}, {"iteration": 3}]
    assert manager.average_loss() == pytest.approx(0.5 / 3, rel=0.0, abs=1e-12)
    assert manager.minimum_loss() == 0.5


def test_minimum_loss_all_missing_returns_inf():
    manager = PhaseManager()
    manager.loss_history = [{"iteration": 1}, {"iteration": 2}]
    assert manager.minimum_loss() == float("inf")


def test_most_visited_phase_tie_breaks_by_insertion_order():
    manager = PhaseManager()
    manager.phase_history = [
        {"to_phase": "evidence"},
        {"to_phase": "formalization"},
    ]
    assert manager.most_visited_phase() == "evidence"


def test_transitions_to_phase_with_non_string_entries():
    manager = PhaseManager()
    manager.phase_history = [
        {"to_phase": None},
        {"to_phase": "evidence"},
        {"to_phase": 1},
    ]
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1


def test_from_dict_missing_keys_raises_key_error():
    data = {
        "current_phase": "intake",
        "phase_history": [],
        "iteration_count": 0,
        "loss_history": [],
    }
    with pytest.raises(KeyError):
        PhaseManager.from_dict(data)


def test_phase_data_coverage_full():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", True)
    assert manager.phase_data_coverage() == 1.0


@pytest.mark.performance
def test_benchmark_iterations_in_phase(benchmark):
    manager = PhaseManager()
    manager.loss_history = [
        {"phase": "intake", "loss": 1.0},
        {"phase": "evidence", "loss": 0.9},
    ] * 1000
    result = benchmark(manager.iterations_in_phase, ComplaintPhase.INTAKE)
    assert result == 1000


@pytest.mark.performance
def test_benchmark_phase_data_coverage(benchmark):
    manager = PhaseManager()
    manager.phase_data = {
        ComplaintPhase.INTAKE: {"a": 1},
        ComplaintPhase.EVIDENCE: {},
        ComplaintPhase.FORMALIZATION: {"b": 2},
    }
    result = benchmark(manager.phase_data_coverage)
    assert result == 2 / 3
