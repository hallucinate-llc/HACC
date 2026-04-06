from pathlib import Path
import sys


ROOT = Path("/home/barberb/HACC/Breach of Contract")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from formal_logic.title18_contract_eviction_bar_analysis import build_case_report


def main() -> None:
    report = build_case_report()
    assert report["metadata"]["caseId"] == "title18_contract_eviction_bar"
    obligation_ids = {item["obligation_id"] for item in report["obligations"]}
    assert "obl_hacc_no_eviction_before_relocation_complete" in obligation_ids
    proof_labels = {item["label"] for item in report["formalModels"]["tdfol"]["proofAudit"]["proofs"]}
    assert "eviction_forbidden_while_duties_incomplete" in proof_labels
    print("title18_contract_eviction_bar_analysis smoke test passed")


if __name__ == "__main__":
    main()
