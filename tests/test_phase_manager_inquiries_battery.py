import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

COMPLAINT_GENERATOR_ROOT = Path(__file__).resolve().parents[1] / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_phases.phase_manager import ComplaintPhase, PhaseManager
from mediator import strings
from mediator.inquiries import Inquiries, _normalize_question_cached


class DummyState:
    def __init__(self):
        self.complaint = "Tenant rights violations"
        self.inquiries: List[Dict[str, Any]] = []


class DummyMediator:
    def __init__(self):
        self.state = DummyState()
        self.queries: List[str] = []

    def query_backend(self, prompt: str):
        self.queries.append(prompt)
        return """
        1. What happened during the incident?
        2. Who witnessed the conduct?
        3. What documents support the timeline?
        """

    def build_inquiry_gap_context(self) -> Dict[str, Any]:
        return {
            "priority_terms": ["timeline", "actors", "responsible"],
        }


def make_broken_mediator():
    class _Broken(DummyMediator):
        def build_inquiry_gap_context(self):
            raise RuntimeError("gap context failed")

    return _Broken()


@pytest.fixture
def manager():
    return PhaseManager()


@pytest.fixture
def mediator():
    return DummyMediator()


@pytest.fixture
def inquiries(mediator):
    return Inquiries(mediator)


class TestPhaseManagerIntakeHelpers:
    def test_extract_gap_types_and_contradictions(self, manager: PhaseManager):
        data = {
            "intake_gap_types": ["missing_timeline", "missing_timeline", "unsupported_claim"],
            "current_gaps": [
                {"type": "missing_responsible_party"},
                {"type": "missing_timeline"},
            ],
            "intake_contradictions": {
                "candidates": [
                    {"status": "open"},
                    {"status": "resolved", "current_resolution_status": "resolved"},
                ]
            },
        }
        gap_types = manager._extract_intake_gap_types(data)
        assert sorted(set(gap_types)) == sorted(gap_types)
        assert "missing_timeline" in gap_types

        contradictions = manager._extract_intake_contradictions(data)
        assert len(contradictions) == 2
        active = manager._active_intake_contradictions(contradictions)
        assert len(active) == 1
        assert manager._is_intake_contradiction_resolved(contradictions[1])
        escalated = {"status": "awaiting_complainant_record"}
        assert manager._is_intake_contradiction_resolved_or_escalated(escalated)

    def test_collect_sections_blockers_and_readiness(self, manager: PhaseManager):
        intake_case_file = {
            "intake_sections": {
                "chronology": {"status": "missing", "missing_items": ["dates"]},
                "actors": {"status": "present"},
                "conduct": {"status": "missing"},
                "claim_elements": {"status": "present"},
            },
            "candidate_claims": [
                {"claim_type": "eviction", "confidence": 0.8, "ambiguity_flags": []}
            ],
            "canonical_facts": [{"fact": "rent not paid"}],
            "proof_leads": ["lease"],
            "contradiction_queue": [
                {"severity": "blocking", "status": "open"},
                {"severity": "blocking", "status": "awaiting_testimony"},
            ],
            "summary_snapshots": ["snapshot"],
            "complainant_summary_confirmation": {"confirmed": False},
        }
        blockers = manager._collect_intake_section_blockers(intake_case_file)
        assert "blocking_contradiction" in blockers["blockers"]
        assert blockers["criteria"]["case_theory_coherent"] is False
        readiness = manager._build_intake_readiness({
            "knowledge_graph": {},
            "dependency_graph": {},
            "remaining_gaps": 1,
            "denoising_converged": True,
            "intake_case_file": intake_case_file,
        })
        assert readiness["intake_ready"] is False
        assert readiness["intake_readiness_score"] <= 1.0
        assert "missing_core_chronology" in readiness["intake_readiness_blockers"]

    def test_refresh_intake_state_and_get(self, manager: PhaseManager):
        manager.phase_data[ComplaintPhase.INTAKE] = {
            "knowledge_graph": {},
            "dependency_graph": {},
            "denoising_converged": True,
            "current_gaps": [],
            "remaining_gaps": 0,
            "intake_blockers": [],
        }
        readiness = manager.get_intake_readiness()
        assert readiness["ready"] and readiness["score"] == 1.0
        manager.update_phase_data(ComplaintPhase.INTAKE, "remaining_gaps", 5)
        assert manager.get_phase_data(ComplaintPhase.INTAKE, "remaining_gaps") == 5
        assert hasattr(manager, "phase_data")


class TestPhaseManagerEvidenceFormalization:
    def test_evidence_packet_summary_and_normalization(self, manager: PhaseManager):
        data = {
            "claim_support_packets": {
                "eviction": {
                    "claim_type": "eviction",
                    "elements": [
                        {
                            "element_id": "timeline",
                            "support_status": "supported",
                            "parse_quality_flags": [],
                            "recommended_next_step": "collect_witness",
                        },
                        {
                            "element_id": "actors",
                            "support_status": "unsupported",
                            "contradiction_count": 1,
                            "escalation_status": "awaiting_testimony",
                        },
                    ],
                }
            },
            "alignment_evidence_tasks": [
                {
                    "claim_type": "eviction",
                    "claim_element_id": "actors",
                    "support_status": "unsupported",
                    "resolution_status": "awaiting_testimony",
                    "action": "fill_temporal_chronology_gap",
                    "temporal_rule_status": "partial",
                }
            ],
            "claim_support_recommended_actions": ["prioritize_timeline"],
        }
        summary = manager._build_evidence_packet_summary(data)
        assert summary["claim_support_packet_count"] == 1
        assert summary["reviewable_escalation_ratio"] >= 0
        packet_action = manager._get_next_packet_evidence_action(
            data["claim_support_packets"], data
        )
        assert packet_action is None
        assert manager._normalize_evidence_escalation_status("PROMOTED_TO_TESTIMONY") == "promoted_to_testimony"
        assert manager._resolve_evidence_escalation_status({"resolution_status": "Pending"}, "") == "pending"
        actionable = manager._get_actionable_alignment_tasks(data)
        assert actionable == []
        data_update = {
            "alignment_promotion_drift_summary": {"drift_flag": True, "promoted_count": 1},
            "alignment_task_updates": [
                {
                    "claim_type": "eviction",
                    "claim_element_id": "timeline",
                    "resolution_status": "promoted_to_document",
                    "evidence_sequence": 10,
                }
            ],
            "claim_support_recommended_actions": ["validate_document"],
        }
        action = manager._get_alignment_promotion_drift_action(data_update)
        assert action and action.get("action") == "validate_promoted_support"

    def test_evidence_and_formalization_actions(self, manager: PhaseManager):
        manager.current_phase = ComplaintPhase.INTAKE
        assert manager._get_intake_action()["action"] == "build_knowledge_graph"
        manager.phase_data[ComplaintPhase.INTAKE].update({
            "knowledge_graph": {},
            "dependency_graph": {},
            "remaining_gaps": 10,
            "current_gaps": [{"type": "missing_timeline"}],
            "denoising_converged": True,
        })
        assert manager._get_intake_action()["action"] == "address_gaps"
        manager.phase_data[ComplaintPhase.EVIDENCE] = {
            "claim_support_packets": {"test": {"elements": []}},
            "claim_support_element_count": 0,
            "claim_support_explicit_status_count": 0,
        }
        assert manager._get_evidence_action()["action"] == "build_claim_support_packets"
        manager.phase_data[ComplaintPhase.EVIDENCE].update({
            "claim_support_element_count": 1,
            "claim_support_explicit_status_count": 1,
            "claim_support_blocking_contradictions": 1,
        })
        assert manager._get_evidence_action()["action"] == "resolve_support_conflicts"
        manager.phase_data[ComplaintPhase.FORMALIZATION] = {}
        assert manager._get_formalization_action()["action"] == "build_legal_graph"
        manager.phase_data[ComplaintPhase.FORMALIZATION]["legal_graph"] = {"nodes": []}
        assert manager._get_formalization_action()["action"] == "perform_neurosymbolic_matching"
        manager.phase_data[ComplaintPhase.FORMALIZATION]["matching_complete"] = True
        assert manager._get_formalization_action()["action"] == "generate_formal_complaint"
        manager.phase_data[ComplaintPhase.FORMALIZATION]["formal_complaint"] = "done"
        assert manager._get_formalization_action()["action"] == "complete_formalization"

    def test_phase_transitions_and_statistics(self, manager: PhaseManager):
        assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is False
        manager.phase_data[ComplaintPhase.INTAKE].update({
            "knowledge_graph": {},
            "dependency_graph": {},
            "denoising_converged": True,
            "current_gaps": [],
            "remaining_gaps": 0,
            "intake_case_file": {
                "intake_sections": {
                    name: {"status": "present", "missing_items": []}
                    for name in ("chronology", "actors", "conduct", "harm", "remedy", "proof_leads", "claim_elements")
                },
                "candidate_claims": [{"claim_type": "eviction", "confidence": 0.8, "ambiguity_flags": []}],
                "canonical_facts": [{"fact": "rent not paid"}],
                "proof_leads": ["lease"],
                "summary_snapshots": [],
                "contradiction_queue": [],
                "complainant_summary_confirmation": {"confirmed": True},
            },
        })
        assert manager.advance_to_phase(ComplaintPhase.EVIDENCE) is True
        assert manager.get_current_phase() == ComplaintPhase.EVIDENCE
        assert manager.total_phase_transitions() == 1
        assert manager.transitions_to_phase(ComplaintPhase.EVIDENCE) == 1
        freq = manager.phase_transition_frequency()
        assert freq.get("evidence") == 1
        assert manager.most_visited_phase() == "evidence"
        manager.update_phase_data(ComplaintPhase.EVIDENCE, "claim_support_packets", {"claim": {"elements": []}})
        manager.record_iteration(0.2, {"metric": 1})
        manager.record_iteration(0.18, {"metric": 2})
        manager.record_iteration(0.19, {"metric": 3})
        assert manager.total_iterations() == 3
        assert manager.iterations_in_phase(ComplaintPhase.EVIDENCE) == 3
        assert manager.average_loss() == pytest.approx((0.2 + 0.18 + 0.19) / 3)
        assert manager.minimum_loss() == pytest.approx(0.18)
        assert manager.has_converged(window=3, threshold=0.05)
        assert manager.has_phase_data_key(ComplaintPhase.EVIDENCE, "claim_support_packets")
        manager.phase_history.append({"to_phase": "intake"})
        assert manager.phase_data_coverage() >= 0
        serialized = manager.to_dict()
        clone = PhaseManager.from_dict(serialized)
        assert clone.get_phase_data(ComplaintPhase.EVIDENCE, "claim_support_packets")

    def test_complete_checks_and_dispatch(self, manager: PhaseManager):
        manager.phase_data[ComplaintPhase.INTAKE].update({
            "knowledge_graph": {},
            "dependency_graph": {},
            "remaining_gaps": 0,
            "current_gaps": [],
            "denoising_converged": True,
            "intake_case_file": {
                "intake_sections": {
                    name: {"status": "present", "missing_items": []}
                    for name in ("chronology", "actors", "conduct", "harm", "remedy", "proof_leads", "claim_elements")
                },
                "candidate_claims": [{"claim_type": "eviction", "confidence": 0.8, "ambiguity_flags": []}],
                "canonical_facts": [{"fact": "rent not paid"}],
                "proof_leads": ["lease"],
                "summary_snapshots": [],
                "contradiction_queue": [],
                "complainant_summary_confirmation": {"confirmed": True},
            },
        })
        assert manager._is_intake_complete()
        manager.phase_data[ComplaintPhase.EVIDENCE].update({
            "evidence_count": 1,
            "knowledge_graph_enhanced": True,
            "evidence_gap_ratio": 0.2,
        })
        assert manager._is_evidence_complete()
        manager.phase_data[ComplaintPhase.FORMALIZATION].update({
            "legal_graph": {},
            "matching_complete": True,
            "formal_complaint": "yes",
        })
        assert manager._is_formalization_complete()
        assert manager.is_phase_complete(ComplaintPhase.FORMALIZATION)
        assert manager.get_next_action()

    def test_performance_evidence_summary(self, manager: PhaseManager):
        packets = {
            f"claim_{i}": {
                "elements": [
                    {
                        "support_status": "unsupported",
                        "element_id": f"e_{j}",
                        "recommended_next_step": "investigate",
                    }
                    for j in range(5)
                ],
            }
            for i in range(10)
        }
        data = {
            "claim_support_packets": packets,
            "alignment_evidence_tasks": [],
        }
        start = time.perf_counter()
        manager._build_evidence_packet_summary(data)
        duration = time.perf_counter() - start
        assert duration < 0.3


class TestInquiriesFlow:
    def test_normalization_helpers_and_cache(self):
        assert _normalize_question_cached(" 1. Which actor is responsible? ") == "which actor is responsible"
        inq = Inquiries(DummyMediator())
        assert inq._normalize_question("HELLO??") == "hello"
        assert inq._priority_rank("critical") == 0
        assert inq._priority_rank("unknown") == 2
        assert Inquiries._trim_question_prefix("1) what?") == "what?"
        assert Inquiries._clean_question("  - why?   ") == "why?"

    def test_registration_and_indexing(self, inquiries: Inquiries, mediator: DummyMediator):
        mediator.state.inquiries.clear()
        inquiries.register("Why is the evidence missing?")
        assert mediator.state.inquiries
        saved_len = len(mediator.state.inquiries)
        inquiries.register("1. Why is the evidence missing?")
        assert len(mediator.state.inquiries) == saved_len
        assert mediator.state.inquiries[0]["alternative_questions"]
        inquiries.register("")
        assert len(mediator.state.inquiries) == saved_len
        index = inquiries._index_for(mediator.state.inquiries)
        pre_signature = inquiries._index_signature
        mediator.state.inquiries.append({"question": "Are witnesses available?"})
        _ = inquiries._index_for(mediator.state.inquiries)
        assert inquiries._index_signature != pre_signature

    def test_merge_explain_and_gap_context(self, mediator: DummyMediator, inquiries: Inquiries):
        mediator.state.inquiries[:] = [
            {
                "question": "What happened?",
                "priority": "high",
                "support_gap_targeted": True,
                "answer": None,
                "source": "existing",
            }
        ]
        questions = [
            {
                "question": "What happened?",
                "priority": "critical",
                "support_gap_targeted": False,
                "claim_type": "eviction",
                "element": "chronology",
            },
            "invalid",
            {"question": "", "priority": "low"},
        ]
        merged = inquiries.merge_legal_questions(questions)
        assert merged == 1
        info = inquiries.explain_inquiry(mediator.state.inquiries[0])
        assert "Selected because" in info["summary"]
        gap_context = inquiries._build_gap_context()
        assert isinstance(gap_context, dict)
        broken = Inquiries(make_broken_mediator())
        assert broken._build_gap_context() == {}

    def test_generate_answer_and_get_next(self, mediator: DummyMediator, inquiries: Inquiries):
        mediator.state.inquiries.clear()
        inquiries.generate()
        assert mediator.state.inquiries
        first = inquiries.get_next()
        assert first is not None
        inquiries.answer("sample answer")
        assert mediator.state.inquiries[0]["answer"] == "sample answer"
        assert not inquiries.is_complete()
        mediator.state.inquiries.append({"question": "Still pending?", "priority": "low"})
        assert not inquiries.is_complete()
        assert Inquiries._find_unanswered(mediator.state.inquiries)
        assert inquiries.same_question("1. Who?", "Who?")
        assert not inquiries.same_question("Who?", "What?")
        result = inquiries._extract_questions("No question here.")
        assert result == []
        block = "Will you testify?\nYes?"
        assert "Will you testify?" in inquiries._extract_questions(block)
        assert inquiries.register(None) is None
        assert inquiries.answer("ignored") is None

    def test_generate_handles_missing_template_and_backend(self, inquiries: Inquiries, mediator: DummyMediator, monkeypatch):
        mediator.state.inquiries.clear()
        monkeypatch.setitem(strings.model_prompts, "generate_questions", None)
        inquiries.generate()
        assert mediator.state.inquiries == []
        monkeypatch.setitem(strings.model_prompts, "generate_questions", strings.model_prompts.get("generate_questions", ""))
        def empty_backend(prompt: str):
            return ""
        mediator.query_backend = empty_backend
        inquiries.generate()
        assert mediator.state.inquiries == []

    def test_performance_normalization(self):
        start = time.perf_counter()
        for _ in range(1000):
            _normalize_question_cached(" What is the timeline? ")
        duration = time.perf_counter() - start
        assert duration < 0.15
