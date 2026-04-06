import json
from pathlib import Path

from formal_logic.vawa_analysis import build_case_report, write_outputs


OUTPUT_DIR = Path("/home/barberb/HACC/Breach of Contract/outputs")


def test_vawa_case_report_marks_hacc_as_primary_exposure():
    report = build_case_report()

    finding_ids = {item["finding_id"] for item in report["findings"]}
    assert "finding_hacc_primary_vawa_exposure" in finding_ids
    assert "finding_quantum_direct_vawa_theory_weak" in finding_ids
    profile_ids = {item["party_id"] for item in report["partyDeonticProfiles"]}
    assert "person:solomon_barber" in profile_ids
    assert "person:ashley_ferron" in profile_ids
    assert "org:hacc_relocation" in profile_ids
    authority_ids = {item["authority_id"] for item in report["authorities"]}
    assert "auth:boston_housing_authority_v_ya" in authority_ids
    assert "auth:mccoy_v_hano" in authority_ids
    assert "auth:24_cfr_982_555" in authority_ids

    hacc_row = next(item for item in report["actorDeonticMatrix"] if item["actor"] == "org:hacc")
    hacc_obligation_ids = {item["obligationId"] for item in hacc_row["obligated"]}
    hacc_forbidden_ids = {item["obligationId"] for item in hacc_row["forbidden"]}
    assert "obl_hacc_must_consider_causal_nexus_before_adverse_action" in hacc_obligation_ids
    assert "obl_hacc_must_not_apply_heightened_standard_to_victim_side" in hacc_forbidden_ids
    assert "obl_hacc_when_notified_of_court_order_must_comply_in_access_and_control_decisions" in hacc_obligation_ids
    assert "obl_hacc_must_not_disclose_vawa_or_location_information_to_abusive_or_restrained_actor" in hacc_forbidden_ids
    assert "obl_hacc_must_give_brief_written_reason_for_lease_or_assistance_adverse_action" in hacc_obligation_ids
    assert "obl_hacc_must_offer_hearing_path_for_adverse_action_affecting_assistance_or_occupancy" in hacc_obligation_ids

    solomon_profile = next(item for item in report["partyDeonticProfiles"] if item["party_id"] == "person:solomon_barber")
    assert "obl_solomon_if_he_secretly_induced_provider_action_theory_is_interference_not_direct_vawa" in solomon_profile["related_obligation_ids"]

    grounding = report["groundingAudit"]
    assert any(item["taskId"] == "task_pin_down_solomon_notice_to_hacc" for item in grounding["recordStrengtheningTasks"])
    assert any(item["taskId"] == "task_prove_reason_and_hearing_request_history" for item in grounding["recordStrengtheningTasks"])

    audit = report["formalModels"]["tdfol"]["proofAudit"]
    assert audit["available"] is True
    statuses = {item["label"]: item["status"] for item in audit["proofs"]}
    assert statuses["hacc_notice_packet_required"] == "proved"
    assert statuses["hacc_causal_nexus_review_required"] == "proved"
    assert statuses["hacc_court_order_compliance_required"] == "proved"
    assert statuses["hacc_brief_reason_notice_required"] == "proved"
    assert statuses["hacc_hearing_path_required"] == "proved"
    assert statuses["quantum_primary_notice_duty"] == "unknown"
    assert statuses["solomon_direct_provider_duty"] == "unknown"


def test_vawa_output_bundle_writes_expected_files():
    paths = write_outputs()

    assert paths["report_json"].exists()
    assert paths["dependency_graph"].exists()
    assert paths["flogic"].exists()
    assert paths["dcec"].exists()
    assert paths["grounding_audit_json"].exists()

    graph = json.loads(paths["dependency_graph"].read_text())
    assert graph["branch"] == "vawa_hacc_quantum_analysis"
    assert "hacc_notice_packet_breach_supported" in graph["nodes"]
    assert "quantum_conditional_owner_side_duties_preserved" in graph["nodes"]
    assert "solomon_direct_vawa_theory_not_supported" in graph["nodes"]

    grounding = json.loads(paths["grounding_audit_json"].read_text())
    assert "dependencyNodeAudit" in grounding
    assert any(item["nodeId"] == "hacc_solomon_notice_timing_unresolved" for item in grounding["dependencyNodeAudit"])

    proof_audit = json.loads(paths["tdfol_audit"].read_text())
    assert proof_audit["available"] is True
