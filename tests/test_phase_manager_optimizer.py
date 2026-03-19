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
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", pm._INTAKE_GAPS_THRESHOLD)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)


def _complete_evidence(manager: PhaseManager):
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.0)


def test_utc_now_isoformat_parses_as_utc():
    value = pm._utc_now_isoformat()
    parsed = pm.datetime.fromisoformat(value)
    assert parsed.tzinfo == pm.UTC


def test_is_phase_complete_uses_class_mapping_when_instance_mapping_missing():
    manager = PhaseManager()
    manager._phase_completion_checks = {}
    _complete_intake(manager)
    assert manager.is_phase_complete(ComplaintPhase.INTAKE) is True


def test_get_next_action_uses_class_mapping_when_instance_mapping_missing():
    manager = PhaseManager()
    manager._phase_action_getters = {}
    action = manager.get_next_action()
    assert action["action"] == "build_knowledge_graph"
    assert "intake_readiness_score" in action


def test_advance_to_phase_records_iteration_count_in_history(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    manager.iteration_count = 7
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2024-01-01T00:00:00+00:00")

    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
    assert manager.phase_history[-1]["iteration"] == 7


def test_record_iteration_tracks_current_phase_value():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.record_iteration(0.5, {"m": 1})
    assert manager.loss_history[-1]["phase"] == "evidence"


def test_has_converged_window_zero_raises():
    manager = PhaseManager()
    manager.record_iteration(1.0, {})
    assert manager.has_converged(window=0, threshold=0.1) is True


def test_has_converged_missing_loss_keys_defaults_to_zero():
    manager = PhaseManager()
    manager.loss_history = [
        {"iteration": 1, "phase": "intake"},
        {"iteration": 2, "phase": "intake", "loss": 0.0},
        {"iteration": 3, "phase": "intake"},
    ]
    assert manager.has_converged(window=3, threshold=0.1) is True


def test_get_phase_data_empty_string_key_returns_full_mapping():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"k": 1})
    data = manager.get_phase_data(ComplaintPhase.INTAKE, key="")
    assert data["knowledge_graph"] == {"k": 1}


def test_transitions_to_phase_counts_only_matching_targets():
    manager = PhaseManager()
    manager.phase_history = [
        {"to_phase": "intake"},
        {"to_phase": "evidence"},
        {"to_phase": "formalization"},
        {"to_phase": "evidence"},
        {"from_phase": "intake"},
    ]
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 2


def test_phase_transition_frequency_with_mixed_entries():
    manager = PhaseManager()
    manager.phase_history = [
        {"to_phase": "intake"},
        {"to_phase": "evidence"},
        {"from_phase": "intake"},
        {"to_phase": "evidence"},
    ]
    assert manager.phase_transition_frequency() == {"intake": 1, "evidence": 2, None: 1}


def test_average_loss_ignores_missing_loss_keys_as_zero():
    manager = PhaseManager()
    manager.loss_history = [
        {"iteration": 1, "phase": "intake"},
        {"iteration": 2, "phase": "intake", "loss": 1.0},
    ]
    assert manager.average_loss() == 0.5


def test_minimum_loss_with_missing_loss_keys_returns_zero_if_present():
    manager = PhaseManager()
    manager.loss_history = [
        {"iteration": 1, "phase": "intake"},
        {"iteration": 2, "phase": "intake", "loss": 0.3},
    ]
    assert manager.minimum_loss() == 0.3


def test_phase_data_coverage_all_phases():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "ok")
    assert manager.phase_data_coverage() == 1.0


def test_get_evidence_action_threshold_boundary():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", pm._EVIDENCE_GAP_RATIO_THRESHOLD)
    assert manager.get_next_action()["action"] == "complete_evidence"


def test_get_formalization_action_requires_complaint_non_none():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", None)
    assert manager.get_next_action()["action"] == "generate_formal_complaint"


def test_get_intake_action_continue_denoising_until_converged():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", False)
    assert manager.get_next_action()["action"] == "continue_denoising"


def test_to_dict_includes_loss_history_entries():
    manager = PhaseManager()
    manager.record_iteration(0.9, {"a": 1})
    data = manager.to_dict()
    assert data["loss_history"] == manager.loss_history


def test_from_dict_missing_required_key_raises():
    data = {
        "current_phase": "intake",
        "phase_history": [],
        "phase_data": {"intake": {}},
        "iteration_count": 0,
    }
    with pytest.raises(KeyError):
        PhaseManager.from_dict(data)


@pytest.mark.performance
def test_performance_benchmark_has_converged(benchmark):
    manager = PhaseManager()
    for i in range(1000):
        manager.loss_history.append({"iteration": i + 1, "loss": 1.0 - (i * 0.00001)})

    def _run():
        for _ in range(2000):
            manager.has_converged(window=5, threshold=0.01)

    benchmark(_run)


@pytest.mark.performance
def test_performance_benchmark_phase_metrics(benchmark):
    manager = PhaseManager()
    _complete_intake(manager)
    manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    _complete_evidence(manager)
    manager.advance_to_phase(ComplaintPhase.FORMALIZATION)

    def _run():
        for _ in range(5000):
            manager.total_phase_transitions()
            manager.phase_transition_frequency()
            manager.most_visited_phase()

    benchmark(_run)
