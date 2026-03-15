import sys
from pathlib import Path
import time
import math
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


def test_utc_now_isoformat_deterministic(monkeypatch):
    fixed = pm.datetime(2024, 1, 2, 3, 4, 5, tzinfo=pm.UTC)

    class DummyDateTime:
        @classmethod
        def now(cls, tz=None):
            return fixed

    monkeypatch.setattr(pm, "datetime", DummyDateTime)
    assert pm._utc_now_isoformat() == fixed.isoformat()


def test_utc_now_isoformat_includes_utc_offset():
    value = pm._utc_now_isoformat()
    assert value.endswith("+00:00")


def test_init_defaults():
    manager = PhaseManager()
    assert manager.mediator is None
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history == []
    assert manager.iteration_count == 0
    assert manager.loss_history == []
    assert set(manager.phase_data.keys()) == {
        ComplaintPhase.INTAKE,
        ComplaintPhase.EVIDENCE,
        ComplaintPhase.FORMALIZATION,
    }
    assert all(manager.phase_data[phase] == {} for phase in manager.phase_data)


def test_get_current_phase():
    manager = PhaseManager()
    assert manager.get_current_phase() == ComplaintPhase.INTAKE


def test_advance_to_phase_success_and_history(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2020-01-01T00:00:00+00:00")

    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
    assert manager.current_phase == ComplaintPhase.EVIDENCE
    assert manager.phase_history[-1] == {
        "from_phase": "intake",
        "to_phase": "evidence",
        "timestamp": "2020-01-01T00:00:00+00:00",
        "iteration": 0,
    }


def test_advance_to_phase_allows_return_to_intake(monkeypatch):
    manager = PhaseManager()
    _complete_intake(manager)
    manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2021-01-01T00:00:00+00:00")

    assert manager.advance_to_phase(ComplaintPhase.INTAKE) is True
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history[-1]["to_phase"] == "intake"


def test_advance_to_phase_failure_when_requirements_not_met():
    manager = PhaseManager()
    assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is False
    assert manager.current_phase == ComplaintPhase.INTAKE
    assert manager.phase_history == []


def test_advance_to_phase_invalid_phase_raises():
    manager = PhaseManager()
    with pytest.raises(AttributeError):
        manager.advance_to_phase("bogus")


def test_can_advance_to_logic():
    manager = PhaseManager()
    assert manager._can_advance_to(ComplaintPhase.INTAKE) is True
    assert manager._can_advance_to(ComplaintPhase.EVIDENCE) is False
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 3)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    assert manager._can_advance_to(ComplaintPhase.EVIDENCE) is True
    assert manager._can_advance_to(ComplaintPhase.FORMALIZATION) is False
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.2)
    assert manager._can_advance_to(ComplaintPhase.FORMALIZATION) is True


def test_is_intake_complete_requirements():
    manager = PhaseManager()
    assert manager._is_intake_complete() is False
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 4)
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    assert manager._is_intake_complete() is False
    manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 3)
    assert manager._is_intake_complete() is True


def test_is_evidence_complete_requirements():
    manager = PhaseManager()
    assert manager._is_evidence_complete() is False
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 1)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.3)
    assert manager._is_evidence_complete() is False
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.29)
    assert manager._is_evidence_complete() is True


def test_is_formalization_complete_requirements():
    manager = PhaseManager()
    assert manager._is_formalization_complete() is False
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", {"nodes": []})
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", None)
    assert manager._is_formalization_complete() is False
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "text")
    assert manager._is_formalization_complete() is True


def test_is_phase_complete_routes():
    manager = PhaseManager()
    _complete_intake(manager)
    assert manager.is_phase_complete(ComplaintPhase.INTAKE) is True
    assert manager.is_phase_complete(ComplaintPhase.EVIDENCE) is False
    assert manager.is_phase_complete(ComplaintPhase.FORMALIZATION) is False


def test_is_phase_complete_unknown_phase_false():
    manager = PhaseManager()
    assert manager.is_phase_complete("bogus") is False


def test_update_and_get_phase_data():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", {"k": 1})
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "knowledge_graph") == {"k": 1}
    assert manager.get_phase_data(ComplaintPhase.INTAKE, "missing") is None
    assert manager.get_phase_data(ComplaintPhase.INTAKE) == {"knowledge_graph": {"k": 1}}


def test_update_phase_data_invalid_phase_raises():
    manager = PhaseManager()
    with pytest.raises(KeyError):
        manager.update_phase_data("bogus", "x", 1)


def test_get_phase_data_invalid_phase_raises():
    manager = PhaseManager()
    with pytest.raises(KeyError):
        manager.get_phase_data("not-a-phase")


def test_record_iteration_and_convergence(monkeypatch):
    manager = PhaseManager()
    monkeypatch.setattr(pm, "_utc_now_isoformat", lambda: "2020-01-01T00:00:00+00:00")
    manager.record_iteration(1.0, {"a": 1})
    manager.record_iteration(1.02, {"a": 2})
    assert manager.iteration_count == 2
    assert manager.loss_history[-1]["phase"] == "intake"
    assert manager.loss_history[-1]["timestamp"] == "2020-01-01T00:00:00+00:00"
    assert manager.has_converged(window=3, threshold=0.1) is False
    manager.record_iteration(1.01, {"a": 3})
    assert manager.has_converged(window=3, threshold=0.05) is True
    assert manager.has_converged(window=3, threshold=0.005) is False


def test_has_converged_exact_threshold_is_false():
    manager = PhaseManager()
    manager.record_iteration(1.0, {})
    manager.record_iteration(1.1, {})
    manager.record_iteration(1.0, {})
    assert manager.has_converged(window=3, threshold=0.1) is False


def test_get_next_action_intake_flow():
    manager = PhaseManager()
    assert manager.get_next_action() == {"action": "build_knowledge_graph"}
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    assert manager.get_next_action() == {"action": "build_dependency_graph"}
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", ["g1"])
    assert manager.get_next_action() == {"action": "address_gaps", "gaps": ["g1"]}
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", [])
    assert manager.get_next_action() == {"action": "continue_denoising"}
    manager.update_phase_data(ComplaintPhase.INTAKE, "denoising_converged", True)
    assert manager.get_next_action() == {"action": "complete_intake"}


def test_get_next_action_intake_iteration_cutoff():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.iteration_count = 20
    assert manager.get_next_action() == {"action": "complete_intake"}


def test_get_next_action_intake_no_gaps_none():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "dependency_graph", True)
    manager.update_phase_data(ComplaintPhase.INTAKE, "current_gaps", None)
    assert manager.get_next_action() == {"action": "continue_denoising"}


def test_get_next_action_evidence_flow():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.EVIDENCE
    assert manager.get_next_action() == {"action": "gather_evidence"}
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_count", 2)
    assert manager.get_next_action() == {"action": "enhance_knowledge_graph"}
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "knowledge_graph_enhanced", True)
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.6)
    assert manager.get_next_action() == {"action": "fill_evidence_gaps", "gap_ratio": 0.6}
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "evidence_gap_ratio", 0.3)
    assert manager.get_next_action() == {"action": "complete_evidence"}


def test_get_next_action_formalization_flow():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    assert manager.get_next_action() == {"action": "build_legal_graph"}
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", True)
    assert manager.get_next_action() == {"action": "perform_neurosymbolic_matching"}
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    assert manager.get_next_action() == {"action": "generate_formal_complaint"}
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "done")
    assert manager.get_next_action() == {"action": "complete_formalization"}


def test_get_next_action_formalization_empty_string_complaint():
    manager = PhaseManager()
    manager.current_phase = ComplaintPhase.FORMALIZATION
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "legal_graph", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "matching_complete", True)
    manager.update_phase_data(ComplaintPhase.FORMALIZATION, "formal_complaint", "")
    assert manager.get_next_action() == {"action": "generate_formal_complaint"}


def test_get_next_action_unknown_phase():
    manager = PhaseManager()
    manager.current_phase = "bogus"
    assert manager.get_next_action() == {"action": "unknown"}


def test_to_dict_from_dict_roundtrip():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    manager.record_iteration(0.9, {"m": 1})
    manager.phase_history.append({
        "from_phase": "intake",
        "to_phase": "evidence",
        "timestamp": "2020-01-01T00:00:00+00:00",
        "iteration": 1,
    })
    manager.current_phase = ComplaintPhase.EVIDENCE

    data = manager.to_dict()
    clone = PhaseManager.from_dict(data)

    assert clone.current_phase == ComplaintPhase.EVIDENCE
    assert clone.phase_history == manager.phase_history
    assert clone.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] is True
    assert clone.iteration_count == manager.iteration_count
    assert clone.loss_history == manager.loss_history


def test_to_dict_serializes_phase_data_keys_as_strings():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    data = manager.to_dict()
    assert "intake" in data["phase_data"]
    assert ComplaintPhase.INTAKE not in data["phase_data"]


def test_from_dict_invalid_phase_raises():
    data = {
        "current_phase": "bogus",
        "phase_history": [],
        "phase_data": {"intake": {}},
        "iteration_count": 0,
        "loss_history": [],
    }
    with pytest.raises(ValueError):
        PhaseManager.from_dict(data)


def test_from_dict_invalid_phase_data_raises():
    data = {
        "current_phase": "intake",
        "phase_history": [],
        "phase_data": {"bogus": {}},
        "iteration_count": 0,
        "loss_history": [],
    }
    with pytest.raises(ValueError):
        PhaseManager.from_dict(data)


def test_from_dict_preserves_mediator():
    mediator = object()
    manager = PhaseManager()
    data = manager.to_dict()
    clone = PhaseManager.from_dict(data, mediator=mediator)
    assert clone.mediator is mediator


def test_phase_transition_metrics():
    manager = PhaseManager()
    _complete_intake(manager)
    manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    _complete_evidence(manager)
    manager.advance_to_phase(ComplaintPhase.FORMALIZATION)

    assert manager.total_phase_transitions() == 2
    assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
    assert manager.transitions_to_phase(ComplaintPhase.FORMALIZATION) == 1
    assert manager.phase_transition_frequency() == {"evidence": 1, "formalization": 1}
    assert manager.most_visited_phase() in {"evidence", "formalization"}


def test_phase_transition_metrics_empty_history():
    manager = PhaseManager()
    assert manager.total_phase_transitions() == 0
    assert manager.most_visited_phase() == "none"
    assert manager.phase_transition_frequency() == {}


def test_phase_transition_frequency_counts_missing_phase_keys():
    manager = PhaseManager()
    manager.phase_history.append({"from_phase": "intake", "timestamp": "t"})
    assert manager.phase_transition_frequency() == {None: 1}


def test_iteration_metrics_and_losses():
    manager = PhaseManager()
    assert manager.total_iterations() == 0
    assert manager.average_loss() == 0.0
    assert manager.minimum_loss() == float("inf")
    manager.record_iteration(1.0, {})
    manager.record_iteration(0.5, {})
    assert manager.total_iterations() == 2
    assert math.isclose(manager.average_loss(), 0.75, rel_tol=0.0, abs_tol=1e-9)
    assert manager.minimum_loss() == 0.5
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 2
    manager.current_phase = ComplaintPhase.EVIDENCE
    manager.record_iteration(0.4, {})
    assert manager.iterations_in_phase(ComplaintPhase.EVIDENCE) == 1


def test_iterations_in_phase_no_history():
    manager = PhaseManager()
    assert manager.iterations_in_phase(ComplaintPhase.EVIDENCE) == 0


def test_phase_data_coverage_and_keys():
    manager = PhaseManager()
    assert manager.phase_data_coverage() == 0.0
    manager.update_phase_data(ComplaintPhase.INTAKE, "knowledge_graph", True)
    assert manager.has_phase_data_key(ComplaintPhase.INTAKE, "knowledge_graph") is True
    assert manager.has_phase_data_key(ComplaintPhase.EVIDENCE, "knowledge_graph") is False
    assert manager.phase_data_coverage() == 1 / 3


def test_phase_data_coverage_no_phases():
    manager = PhaseManager()
    manager.phase_data = {}
    assert manager.phase_data_coverage() == 0.0


def test_has_phase_data_key_missing_phase():
    manager = PhaseManager()
    assert manager.has_phase_data_key("bogus", "x") is False


@pytest.mark.performance
def test_record_iteration_performance():
    manager = PhaseManager()
    start = time.perf_counter()
    for i in range(2000):
        manager.record_iteration(1.0 - (i * 0.0001), {"i": i})
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0


@pytest.mark.performance
def test_phase_transition_frequency_performance():
    manager = PhaseManager()
    for i in range(2000):
        manager.phase_history.append({"to_phase": "intake" if i % 2 == 0 else "evidence"})
    start = time.perf_counter()
    freq = manager.phase_transition_frequency()
    elapsed = time.perf_counter() - start
    assert freq == {"intake": 1000, "evidence": 1000}
    assert elapsed < 0.5
