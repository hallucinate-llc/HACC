import sys
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases import phase_manager as pm  # noqa: E402,F401
from complaint_phases.phase_manager import ComplaintPhase, PhaseManager
from mediator import inquiries as inquiries_module
from mediator.inquiries import Inquiries


class DummyState:
    def __init__(self, complaint="sample complaint"):
        self.complaint = complaint
        self.inquiries = []


class DummyMediator:
    def __init__(self):
        self.state = DummyState()
        self.queries = []
        self.gap_context_calls = 0

    def query_backend(self, prompt):
        self.queries.append(prompt)
        return "What is your name?\nHow did the event unfold?"

    def build_inquiry_gap_context(self):
        self.gap_context_calls += 1
        return {"priority_terms": ["name", "event"]}


class ExceptionMediator(DummyMediator):
    def build_inquiry_gap_context(self):
        raise RuntimeError("gap context failure")


def _complete_intake_data():
    data = {
        "knowledge_graph": True,
        "dependency_graph": True,
        "remaining_gaps": 0,
        "denoising_converged": True,
        "knowledge_graph_ready": True,
        "dependency_graph_ready": True,
        "contradictions_resolved": True,
        "intake_blockers": [],
        "intake_case_file": {
            "intake_sections": {
                "chronology": {"status": "complete", "missing_items": []},
                "actors": {"status": "complete", "missing_items": []},
                "conduct": {"status": "complete", "missing_items": []},
                "harm": {"status": "complete", "missing_items": []},
                "remedy": {"status": "complete", "missing_items": []},
                "proof_leads": {"status": "complete", "missing_items": []},
                "claim_elements": {"status": "complete", "missing_items": []},
            },
            "proof_leads": ["lead"],
            "candidate_claims": [
                {"claim_type": "injury", "confidence": 0.7, "ambiguity_flags": []}
            ],
            "canonical_facts": [{"claim": "fact"}],
            "summary_snapshots": [],
            "complainant_summary_confirmation": {"confirmed": True},
            "contradiction_queue": [],
        },
    }
    return data


def _build_evidence_data():
    return {
        "claim_support_packets": {
            "claimA": {
                "claim_type": "ClaimA",
                "elements": [
                    {
                        "element_id": "E1",
                        "support_status": "supported",
                        "parse_quality_flags": [],
                        "recommended_next_step": "document_support",
                    },
                    {
                        "element_id": "E2",
                        "support_status": "contradicted",
                        "recommended_next_step": "reconcile_conflict",
                        "escalation_status": "awaiting_testimony",
                        "contradiction_count": 1,
                    },
                ],
            }
        },
        "alignment_evidence_tasks": [
            {
                "claim_type": "ClaimA",
                "claim_element_id": "E2",
                "support_status": "contradicted",
                "resolution_status": "needs_manual_review",
                "temporal_rule_status": "partial",
                "action": "fill_temporal_chronology_gap",
            }
        ],
        "claim_support_recommended_actions": ["review_element"],
    }


def test_extract_intake_gap_types_filters_invalid_entries():
    manager = PhaseManager()
    data = {
        "intake_gap_types": [" missing_timeline ", None, ""],
        "current_gaps": [
            {"type": "missing_responsible_party"},
            {"type": ""},
            "not a dict",
        ],
    }
    gap_types = manager._extract_intake_gap_types(data)
    assert gap_types == ["missing_timeline", "missing_responsible_party"]


def test_extract_intake_contradictions_handles_structures():
    manager = PhaseManager()
    contract_dict = {"candidates": [{"status": "open"}, {}]}
    assert len(manager._extract_intake_contradictions({"intake_contradictions": contract_dict})) == 2
    contract_list = [{"status": "open"}, "invalid", 123]
    assert len(manager._extract_intake_contradictions({"intake_contradictions": contract_list})) == 1
    assert manager._extract_intake_contradictions({}) == []


def test_active_contradictions_excludes_resolved():
    manager = PhaseManager()
    queue = [
        {"status": "resolved"},
        {"status": "open"},
        {"current_resolution_status": "escalated"},
    ]
    active = manager._active_intake_contradictions(queue)
    assert len(active) == 2
    assert all(not manager._is_intake_contradiction_resolved(entry) for entry in active)


def test_intake_contradiction_resolution_helpers():
    manager = PhaseManager()
    resolved = {"status": "resolved"}
    escalated = {"status": "escalated"}
    assert manager._is_intake_contradiction_resolved(resolved) is True
    assert manager._is_intake_contradiction_resolved(escalated) is False
    assert manager._is_intake_contradiction_resolved_or_escalated(escalated) is True


def test_extract_case_file_and_collect_blockers():
    manager = PhaseManager()
    case = {
        "intake_sections": {
            "chronology": {"status": "missing", "missing_items": ["date"]},
            "actors": {"status": "missing", "missing_items": []},
        },
        "contradiction_queue": [
            {"status": "open", "severity": "blocking"},
            {"status": "resolved", "severity": "blocking"},
        ],
        "proof_leads": [],
        "candidate_claims": [{"claim_type": "injury", "confidence": 0.1, "ambiguity_flags": ["flag"]}],
        "canonical_facts": [],
        "summary_snapshots": [{"snapshot": 1}],
        "complainant_summary_confirmation": {},
    }
    blockers = manager._collect_intake_section_blockers(case)
    assert "missing_core_chronology" in blockers["blockers"]
    assert blockers["criteria"]["blocking_contradictions_resolved"] is False
    assert blockers["candidate_claim_count"] == 1


def test_build_intake_readiness_and_refresh():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update(_complete_intake_data())
    manager._refresh_phase_derived_state(ComplaintPhase.INTAKE)
    readiness = manager.get_intake_readiness()
    assert readiness["ready"] is True
    assert readiness["score"] <= 1.0
    assert readiness["blocking_contradictions"] == []


def test_build_evidence_summary_counts_ratios():
    summary = PhaseManager()._build_evidence_packet_summary(_build_evidence_data())
    assert summary["claim_support_packet_count"] == 1
    assert summary["claim_support_blocking_contradictions"] == 1
    assert 0 <= summary["proof_readiness_score"] <= 1.0
    assert "fill_temporal_chronology_gap" not in summary["claim_support_recommended_actions"]


def test_evidence_escalation_status_normalization():
    manager = PhaseManager()
    assert manager._normalize_evidence_escalation_status("  PROMOTED  ") == "promoted"
    element = {"escalation_status": "blocked"}
    assert manager._resolve_evidence_escalation_status(element, "override") == "blocked"
    assert manager._resolve_evidence_escalation_status({"resolution_status": "resolved"}, "task") == "resolved"


def test_actionable_alignment_tasks_filtering():
    manager = PhaseManager()
    data = {
        "alignment_evidence_tasks": [
            {"support_status": "unsupported", "resolution_status": "resolved"},
            {"support_status": "supported", "resolution_status": "awaiting_testimony"},
            {"support_status": "partially_supported", "resolution_status": "awaiting_testimony"},
        ]
    }
    tasks = manager._get_actionable_alignment_tasks(data)
    assert len(tasks) == 1
    assert all(task["support_status"] in {"unsupported", "partially_supported"} for task in tasks)


def test_alignment_promotion_drift_action_focuses_elements():
    manager = PhaseManager()
    data = {
        "alignment_promotion_drift_summary": {"drift_flag": True, "promoted_count": 1, "pending_conversion_count": 1},
        "alignment_task_update_history": [
            {
                "claim_type": "ClaimA",
                "claim_element_id": "E1",
                "resolution_status": "promoted_to_testimony",
                "evidence_sequence": 1,
            }
        ],
        "claim_support_recommended_actions": ["prioritize"],
    }
    action = manager._get_alignment_promotion_drift_action(data)
    assert action["action"] == "validate_promoted_support"
    assert action["claim_type"] == "ClaimA"


def test_next_packet_evidence_action_skips_reviewable_and_returns_fill():
    manager = PhaseManager()
    data = {
        "alignment_evidence_tasks": [],
        "claim_support_recommended_actions": ["retry"],
    }
    packets = {
        "claimA": {
            "claim_type": "ClaimA",
            "elements": [
                {"element_id": "E3", "support_status": "unsupported", "recommended_next_step": "fill_evidence_gaps"},
            ],
        }
    }
    action = manager._get_next_packet_evidence_action(packets, data)
    assert action["action"] == "fill_evidence_gaps"
    assert action["claim_element_id"] == "E3"


def test_phase_transitions_tracking_and_metrics():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update(_complete_intake_data())
    manager.advance_to_phase(ComplaintPhase.EVIDENCE)
    manager.advance_to_phase(ComplaintPhase.INTAKE)
    assert manager.total_phase_transitions() == 2
    assert manager.transitions_to_phase(ComplaintPhase.INTAKE) == 1
    freq = manager.phase_transition_frequency()
    assert freq["intake"] == 1
    assert manager.most_visited_phase() == "evidence"


def test_iteration_and_loss_metrics():
    manager = PhaseManager()
    manager.record_iteration(0.5, {"metric": 1})
    manager.record_iteration(0.4, {"metric": 2})
    assert manager.total_iterations() == 2
    assert manager.iterations_in_phase(ComplaintPhase.INTAKE) == 2
    assert pytest.approx(manager.average_loss(), rel=1e-3) == 0.45
    assert manager.minimum_loss() == 0.4


def test_data_accessors_and_phase_flags():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.EVIDENCE, "status", True)
    assert manager.get_phase_data(ComplaintPhase.EVIDENCE, "status") is True
    assert manager.has_phase_data_key(ComplaintPhase.EVIDENCE, "status")
    assert manager.phase_data_coverage() >= 0.33


def test_entry_and_next_action_routing():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = True
    manager.phase_data[ComplaintPhase.INTAKE]["dependency_graph"] = True
    manager.phase_data[ComplaintPhase.INTAKE]["remaining_gaps"] = 5
    manager.phase_data[ComplaintPhase.INTAKE]["denoising_converged"] = False
    action = manager.get_next_action()
    assert action["action"] == "address_gaps" or action["action"] == "continue_denoising"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["legal_graph"] = {"nodes": []}
    manager.phase_data[ComplaintPhase.FORMALIZATION]["matching_complete"] = True
    manager.phase_data[ComplaintPhase.FORMALIZATION]["formal_complaint"] = "text"
    manager.current_phase = ComplaintPhase.FORMALIZATION
    assert manager.get_next_action()["action"] == "complete_formalization"


def test_intake_action_stage_decisions():
    manager = PhaseManager()
    # build knowledge graph
    result = manager._get_intake_action()
    assert result["action"] == "build_knowledge_graph"
    manager.phase_data[ComplaintPhase.INTAKE]["knowledge_graph"] = True
    result = manager._get_intake_action()
    assert result["action"] == "build_dependency_graph"

def test_evidence_action_has_fallbacks():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.EVIDENCE]["claim_support_packets"] = {}
    manager.phase_data[ComplaintPhase.EVIDENCE]["evidence_count"] = 0
    assert manager._get_evidence_action()["action"] == "gather_evidence"
    manager.phase_data[ComplaintPhase.EVIDENCE]["evidence_count"] = 1
    manager.phase_data[ComplaintPhase.EVIDENCE]["knowledge_graph_enhanced"] = False
    assert manager._get_evidence_action()["action"] == "enhance_knowledge_graph"
    manager.phase_data[ComplaintPhase.EVIDENCE]["knowledge_graph_enhanced"] = True
    manager.phase_data[ComplaintPhase.EVIDENCE]["evidence_gap_ratio"] = 0.5
    assert manager._get_evidence_action()["action"] in {"fill_evidence_gaps", "complete_evidence"}


def test_formalization_action_sequence_progresses():
    manager = PhaseManager()
    assert manager._get_formalization_action()["action"] == "build_legal_graph"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["legal_graph"] = {"nodes": []}
    assert manager._get_formalization_action()["action"] == "perform_neurosymbolic_matching"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["matching_complete"] = True
    assert manager._get_formalization_action()["action"] == "generate_formal_complaint"
    manager.phase_data[ComplaintPhase.FORMALIZATION]["formal_complaint"] = "final"
    assert manager._get_formalization_action()["action"] == "complete_formalization"


def test_serialization_round_trip():
    manager = PhaseManager()
    manager.update_phase_data(ComplaintPhase.INTAKE, "test", 1)
    manager.record_iteration(0.3, {"dummy": True})
    state = manager.to_dict()
    restored = PhaseManager.from_dict(state)
    assert restored.current_phase == manager.current_phase
    assert restored.phase_history == manager.phase_history
    assert restored.loss_history == manager.loss_history


def test_evidence_summary_performance():
    manager = PhaseManager()
    data = _build_evidence_data()
    for i in range(100):
        data["claim_support_packets"][f"claim_{i}"] = {
            "claim_type": f"Claim{i}",
            "elements": [
                {
                    "element_id": f"E{i}",
                    "support_status": "unsupported",
                    "recommended_next_step": "fill_evidence_gaps",
                }
            ],
        }
    start = perf_counter()
    manager._build_evidence_packet_summary(data)
    duration = perf_counter() - start
    assert duration < 1.0


def test_intake_readiness_performance():
    manager = PhaseManager()
    manager.phase_data[ComplaintPhase.INTAKE].update(_complete_intake_data())
    start = perf_counter()
    manager.get_intake_readiness()
    duration = perf_counter() - start
    assert duration < 0.5


def test_inquiries_normalize_question_variants():
    normalized = inquiries_module._normalize_question_cached("  1) Hello, world?? ")
    assert normalized == "hello world"
    assert inquiries_module._normalize_question_cached("Hello") == inquiries_module._normalize_question_cached("hello")


def test_inquiries_initialization_and_state_access():
    mediator = DummyMediator()
    inquiry_handler = Inquiries(mediator)
    assert inquiry_handler._index is None
    assert inquiry_handler._state_inquiries() == mediator.state.inquiries
    mediator.state = None
    assert inquiry_handler._state_inquiries() is None


def test_inquiries_index_key_and_caching_behavior():
    mediator = DummyMediator()
    inquiries = [{"question": "What?"}]
    mediator.state.inquiries = inquiries
    handler = Inquiries(mediator)
    first_index = handler._index_for(inquiries)
    inquiries.append({"question": "Why?"})
    handler._index_for(inquiries)
    assert handler._index_signature[1] == len(inquiries)
    assert "what" in handler._index


def test_get_next_prioritizes_support_and_dependency():
    mediator = DummyMediator()
    mediator.state.inquiries = [
        {"question": "low", "priority": "low", "support_gap_targeted": False, "dependency_gap_targeted": False},
        {"question": "target", "priority": "high", "support_gap_targeted": True, "dependency_gap_targeted": True},
    ]
    handler = Inquiries(mediator)
    assert handler.get_next()["question"] == "target"
    handler.answer("answered")
    assert mediator.state.inquiries[1]["answer"] == "answered"


def test_generate_registers_questions_and_handles_empty():
    mediator = DummyMediator()
    handler = Inquiries(mediator)
    handler.generate()
    assert mediator.state.inquiries
    initial_count = len(mediator.state.inquiries)
    mediator.query_backend = lambda prompt: ""
    handler.generate()
    assert len(mediator.state.inquiries) == initial_count


def test_register_ignores_empty_questions():
    mediator = DummyMediator()
    handler = Inquiries(mediator)
    handler.register("")
    assert mediator.state.inquiries == []
    handler.register("Unique?")
    assert mediator.state.inquiries[0]["question"] == "Unique?"


def test_merge_legal_questions_merges_and_tracks_priorities():
    mediator = DummyMediator()
    mediator.state.inquiries = [{"question": "Existing?", "priority": "medium"}]
    handler = Inquiries(mediator)
    merged = handler.merge_legal_questions(
        [
            {"question": "Existing?", "priority": "high", "support_gap_targeted": True, "claim_type": "ClaimX"},
            {"question": "New?", "priority": "low"},
        ]
    )
    assert merged == 2
    assert mediator.state.inquiries[0]["priority"] == "high"
    assert mediator.state.inquiries[-1]["source"] == "legal_question"


def test_explain_inquiry_returns_contextual_reasons():
    handler = Inquiries(DummyMediator())
    inquiry = {"question": "Why?", "priority": "high", "support_gap_targeted": True, "dependency_gap_targeted": False}
    explanation = handler.explain_inquiry(inquiry)
    assert "support gap" in explanation["reasons"][0]
    assert explanation["priority"] == "high"


def test_register_adds_alternative_on_duplicate():
    mediator = DummyMediator()
    mediator.state.inquiries = [{"question": "Repeat?", "alternative_questions": []}]
    handler = Inquiries(mediator)
    handler._register("Repeat?", mediator.state.inquiries, handler._build_index(mediator.state.inquiries))
    assert mediator.state.inquiries[0]["alternative_questions"]


def test_build_index_skips_invalid_questions():
    mediator = DummyMediator()
    inquiries = [{"question": ""}, {"question": "Valid?"}]
    handler = Inquiries(mediator)
    index = handler._build_index(inquiries)
    assert "valid" in index
    assert "" not in index


def test_trim_and_clean_question_strip_prefixes():
    handler = Inquiries(DummyMediator())
    assert handler._trim_question_prefix("1. Sample?") == "Sample?"
    assert handler._clean_question("   2) words??   ") == "words??"


def test_extract_questions_catches_questions_from_block():
    handler = Inquiries(DummyMediator())
    block = "Line one?\nLine two?\nNo question"
    questions = handler._extract_questions(block)
    assert len(questions) == 2


def test_is_complete_checks_unanswered_state():
    mediator = DummyMediator()
    mediator.state.inquiries = [{"question": "Q?", "answer": None}]
    handler = Inquiries(mediator)
    assert not handler.is_complete()
    mediator.state.inquiries[0]["answer"] = "Yes"
    assert handler.is_complete()


def test_same_question_relies_on_normalization():
    handler = Inquiries(DummyMediator())
    assert handler.same_question("Hello?", "hello.")
    assert not handler.same_question("Hello?", "World?")


def test_priority_rank_defaults_and_known_values():
    handler = Inquiries(DummyMediator())
    assert handler._priority_rank("critical") == 0
    assert handler._priority_rank("unknown") == 2


def test_build_gap_context_catches_exceptions():
    handler = Inquiries(ExceptionMediator())
    assert handler._build_gap_context() == {}


def test_inquiries_extract_performance():
    mediator = DummyMediator()
    handler = Inquiries(mediator)
    block = "Question? " * 1000
    start = perf_counter()
    questions = handler._extract_questions(block)
    duration = perf_counter() - start
    assert len(questions) == 1000
    assert duration < 0.5
