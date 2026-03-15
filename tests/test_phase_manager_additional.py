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


def test_is_phase_complete_invalid_phase_returns_false():
    manager = PhaseManager()
    assert manager.is_phase_complete(None) is False


def test_can_advance_to_unknown_phase_returns_false():
    manager = PhaseManager()
    assert manager._can_advance_to(None) is False


def test_get_next_action_unknown_phase_returns_unknown_action():
    manager = PhaseManager()
    manager.current_phase = None
    assert manager.get_next_action() == {"action": "unknown"}


def test_intake_action_gap_list_none_or_empty():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", None)
    assert manager.get_next_action() == {"action": "continue_denoising"}
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", [])
    assert manager.get_next_action() == {"action": "continue_denoising"}


def test_intake_action_iteration_cap():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.iteration_count = pm._DENOISING_MAX_ITERATIONS
    assert manager.get_next_action() == {"action": "complete_intake"}


def test_evidence_action_gap_ratio_threshold_edge():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", pm._EVIDENCE_GAP_RATIO_THRESHOLD)
    assert manager.get_next_action() == {"action": "complete_evidence"}


def test_formalization_action_empty_complaint_string():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "")
    assert manager.get_next_action() == {"action": "generate_formal_complaint"}


def test_update_phase_data_invalid_phase_raises():
    manager = PhaseManager()
    with pytest.raises(KeyError):
        manager.update_phase_data("not-a-phase", "key", "value")


def test_has_converged_with_sparse_loss_entries():
    manager = PhaseManager()
    manager.loss_history = [
        {"iteration": 1, "phase": "intake"},
        {"iteration": 2, "phase": "intake", "loss": 1.0},
        {"iteration": 3, "phase": "intake", "loss": 1.0},
        {"iteration": 4, "phase": "intake", "loss": 1.0},
        {"iteration": 5, "phase": "intake", "loss": 1.0},
    ]
    assert manager.has_converged(window=5, threshold=0.0001) is True


def test_phase_data_coverage_zero_phases():
    manager = PhaseManager()
    manager.phase_data = {}
    assert manager.phase_data_coverage() == 0.0


def test_transitions_to_phase_ignores_missing_keys():
    manager = PhaseManager()
    manager.phase_history = [
        {"from_phase": "intake"},
        {"to_phase": "evidence"},
        {"to_phase": "evidence"},
    ]
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 2


def test_phase_transition_frequency_includes_missing_to_phase_key():
    manager = PhaseManager()
    manager.phase_history = [{"from_phase": "intake"}, {"to_phase": "evidence"}]
    assert manager.phase_transition_frequency() == {None: 1, "evidence": 1}


def test_get_phase_data_returns_full_mapping_copy_reference():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"a": 1})
    data = manager.get_phase_data(ComplaintPhase.INTAKE)
    assert data is manager.phase_data[ComplaintPhase.INTAKE]


def test_to_dict_from_dict_multi_phase_roundtrip():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.phase_history = [
        {"from_phase": "intake", "to_phase": "evidence", "timestamp": "t1", "iteration": 1},
        {"from_phase": "evidence", "to_phase": "formalization", "timestamp": "t2", "iteration": 2},
    ]
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"k": 1})
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 2)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", {"l": 1})
    manager.iteration_count = 2
    manager.loss_history = [{"iteration": 1, "loss": 0.5, "phase": "intake", "metrics": {}, "timestamp": "t"}]

    clone = PhaseManager.from_dict(manager.to_dict())
    assert clone.current_phase == ComplaintPhase.FORMALIZATION
    assert clone.phase_history == manager.phase_history
    assert clone.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] == {"k": 1}
    assert clone.phase_data[ComplaintPhase.EVIDENCE]["evidence_count"] == 2
    assert clone.phase_data[ComplaintPhase.FORMALIZATION]["legal_graph"] == {"l": 1}
    assert clone.iteration_count == 2
    assert clone.loss_history == manager.loss_history


def test_utc_now_isoformat_tzinfo():
    value = pm._utc_now_isoformat()
    assert value.endswith("+00:00")


def test_performance_benchmark_record_iteration(benchmark):
    manager = PhaseManager()

    def _run():
        for i in range(1000):
            manager.record_iteration(1.0 - (i * 0.0001), {"i": i})

    benchmark(_run)


def test_performance_benchmark_get_next_action(benchmark):
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", [])

    def _run():
        for _ in range(5000):
            manager.get_next_action()

    benchmark(_run)
