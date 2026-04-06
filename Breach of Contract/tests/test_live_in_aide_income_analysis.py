import json

from formal_logic.live_in_aide_income_analysis import build_case_report, write_outputs


def test_live_in_aide_income_report_tracks_overbreadth_and_classification_gap():
    report = build_case_report()

    finding_ids = {item["finding_id"] for item in report["findings"]}
    assert "finding_live_in_aide_exclusion_rule_clear" in finding_ids
    assert "finding_feb_25_request_looks_overbroad_if_live_in_aide_status_applies" in finding_ids
    assert "finding_classification_gap_prevents_final_liability_conclusion" in finding_ids

    authority_ids = {item["authority_id"] for item in report["authorities"]}
    assert "auth:pih_2013_04" in authority_ids
    assert "auth:hacc_adminplan_2025" in authority_ids

    hacc_row = next(item for item in report["actorDeonticMatrix"] if item["actor"] == "org:hacc")
    obligated = {item["obligationId"] for item in hacc_row["obligated"]}
    forbidden = {item["obligationId"] for item in hacc_row["forbidden"]}
    permitted = {item["obligationId"] for item in hacc_row["permitted"]}
    assert "obl_hacc_must_treat_true_live_in_aide_income_as_excluded" in obligated
    assert "obl_hacc_must_tailor_requests_to_role_and_issue" in obligated
    assert "obl_hacc_must_not_demand_stale_or_unrelated_business_records_if_live_in_aide_income_is_excluded" in forbidden
    assert "obl_hacc_may_request_targeted_live_in_aide_screening_materials" in permitted

    grounding = report["groundingAudit"]
    task_ids = {item["taskId"] for item in grounding["recordStrengtheningTasks"]}
    assert "task_pin_down_hacc_classification_of_benjamin" in task_ids
    assert "task_identify_reason_for_nerd_party_request" in task_ids

    audit = report["formalModels"]["tdfol"]["proofAudit"]
    assert audit["available"] is True
    statuses = {item["label"]: item["status"] for item in audit["proofs"]}
    assert statuses["exclude_true_live_in_aide_income"] == "proved"
    assert statuses["stale_unrelated_records_forbidden_if_excluded_income"] == "proved"
    assert statuses["nerd_party_request_was_required"] == "unknown"
    assert statuses["hacc_reclassified_benjamin_before_request"] == "unknown"


def test_live_in_aide_income_output_bundle_writes_expected_files():
    paths = write_outputs()

    assert paths["report_json"].exists()
    assert paths["dependency_graph"].exists()
    assert paths["flogic"].exists()
    assert paths["dcec"].exists()
    assert paths["tdfol_audit"].exists()

    graph = json.loads(paths["dependency_graph"].read_text())
    assert graph["branch"] == "live_in_aide_income_review"
    assert "hacc_overbreadth_theory_supported_conditionally" in graph["nodes"]
    assert "classification_gap_limits_final_fault_conclusion" in graph["nodes"]

    audit = json.loads(paths["tdfol_audit"].read_text())
    assert audit["available"] is True
