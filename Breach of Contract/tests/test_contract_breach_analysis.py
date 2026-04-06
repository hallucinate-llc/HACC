from formal_logic.contract_breach_analysis import build_contract_breach_report, render_contract_breach_report_markdown


def test_contract_breach_report_identifies_likely_hacc_and_quantum_theories():
    report = build_contract_breach_report()

    assert report["meta"]["reportId"] == "contract_breach_report_001"
    assert report["meta"]["likelyBreachCount"] >= 2
    finding_ids = {item["findingId"] for item in report["findings"]}
    assert "contract:hacc:relocation_commitment" in finding_ids
    assert "contract:quantum:intake_processing_commitment" in finding_ids
    assert "implied_contract:hacc:relocation_process" in finding_ids
    assert "implied_contract:quantum:application_processing_path" in finding_ids
    assert "promissory_estoppel:hacc:relocation_reliance" in finding_ids
    assert "negligence:hacc:undertaken_relocation_administration" in finding_ids
    assert report["formalAnalysis"]["frameLogic"]["status"] == "success"
    assert report["formalAnalysis"]["dcec"]["formulaCount"] >= len(report["findings"])
    assert report["formalAnalysis"]["temporalDeontic"]["formulaCount"] >= 5
    hacc_finding = next(item for item in report["findings"] if item["findingId"] == "contract:hacc:relocation_commitment")
    assert hacc_finding["formalRefs"]["frameObjectId"] == "contract_hacc_relocation_commitment"
    assert len(hacc_finding["formalRefs"]["dcecFormulaIds"]) >= 4
    assert len(hacc_finding["formalRefs"]["temporalFormulaIds"]) >= 1


def test_contract_breach_markdown_renders_heading_and_summary():
    markdown = render_contract_breach_report_markdown(build_contract_breach_report())

    assert "# Contract Breach Analysis" in markdown
    assert "Likely contract-breach findings:" in markdown
    assert "Promissory estoppel is a meaningful HACC theory" in markdown
    assert "A negligence theory against HACC is narrower" in markdown
    assert "## Formal Analysis" in markdown
    assert "Frame logic status:" in markdown
