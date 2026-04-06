from formal_logic.federal_civil_rights_claim_matrix import build_matrix


def test_federal_civil_rights_claim_matrix_contains_core_claims():
    matrix = build_matrix()
    claim_ids = {item["claimId"] for item in matrix["claims"]}
    assert "claim_1981_quantum" in claim_ids
    assert "claim_1983_first_amendment_retaliation" in claim_ids
    assert "claim_title_vi_race_discrimination" in claim_ids
