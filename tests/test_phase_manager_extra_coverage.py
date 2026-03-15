import sys
from pathlib import Path
from datetime import datetime
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases import phase_manager as pm
from complaint_phases.phase_manager import PhaseManager, ComplaintPhase


def test_utc_now_isoformat_parseable_and_utc_offset():
    value = pm._utc_now_isoformat()
    parsed = datetime.fromisoformat(value)
    assert parsed.utcoffset().total_seconds() == 0


def test_is_phase_complete_fallback_map_when_instance_map_missing():
    manager = PhaseManager()
    manager._phase_completion_checks = {}
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 0)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    assert manager.is_phase_complete(ComplaintPhase.INTAKE) is True


def test_get_next_action_fallback_map_when_instance_map_missing():
    manager = PhaseManager()
    manager._phase_action_getters = {}
    action = manager.get_next_action()
    assert action == {"action": "build_knowledge_graph"}


def test_get_phase_data_empty_key_returns_full_map():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "") == {"knowledge_graph": True}


def test_is_intake_complete_missing_fields_false():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    assert manager._is_intake_complete() is False


def test_is_evidence_complete_defaults_and_thresholds():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    assert manager._is_evidence_complete() is False
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.0)
    assert manager._is_evidence_complete() is True


def test_is_formalization_complete_legal_graph_key_present_with_none():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", None)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "text")
    assert manager._is_formalization_complete() is True


def test_record_iteration_records_metrics_and_phase():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.record_iteration(0.25, {"m": 1})
    entry = manager.loss_history[-1]
    assert entry["metrics"] == {"m": 1}
    assert entry["phase"] == "evidence"


def test_has_converged_handles_missing_loss_entries():
    manager = PhaseManager()
    manager.loss_history = [
        {"loss": 0.5},
        {},
        {"loss": 0.49},
    ]
    assert manager.has_converged(window=3, threshold=0.51) is True
    assert manager.has_converged(window=3, threshold=0.01) is False


def test_can_advance_to_unknown_phase_returns_false():
    manager = PhaseManager()
    assert manager._can_advance_to("bogus") is False


def test_transitions_to_phase_ignores_missing_to_phase_entries():
    manager = PhaseManager()
    manager.phase_history.append({"from_phase": "intake"})
    manager.phase_history.append({"to_phase": "evidence"})
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
    assert manager.transitions_to_phase(ComplaintPhase.FORMALIZATION) == 0


@pytest.mark.performance
def test_benchmark_record_iteration(benchmark):
    pytest.importorskip("pytest_benchmark")
    manager = PhaseManager()

    def _run():
        manager.record_iteration(0.9, {"a": 1})

    benchmark(_run)


@pytest.mark.performance
def test_benchmark_phase_transition_frequency(benchmark):
    pytest.importorskip("pytest_benchmark")
    manager = PhaseManager()
    for i in range(2000):
        manager.phase_history.append({"to_phase": "intake" if i % 2 == 0 else "evidence"})

    result = benchmark(manager.phase_transition_frequency)
    assert result == {"intake": 1000, "evidence": 1000}
