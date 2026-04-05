from datetime import datetime
from pathlib import Path

from formal_logic.graphrag_obligation_analysis import analyze_title18_corpus


CORPUS_ROOT = Path("/home/barberb/HACC/evidence/paper documents/graphrag")


def test_graphrag_scan_finds_target_parties_and_documents():
    report = analyze_title18_corpus(CORPUS_ROOT, current_date=datetime(2026, 4, 5))
    assert report["metadata"]["documentsScanned"] >= 10
    assert report["metadata"]["eventsExtracted"] > 0
    assert report["parties"]["org:hacc"]["mentions"] > 0
    assert report["parties"]["org:quantum"]["mentions"] > 0
    assert report["parties"]["person:jane_cortez"]["mentions"] > 0
    assert report["metadata"]["usingIpfsDatasetsPy"] is True
    assert report["metadata"]["ipfsDatasetsPySource"]


def test_graphrag_analysis_builds_expected_obligation_links():
    report = analyze_title18_corpus(CORPUS_ROOT, current_date=datetime(2026, 4, 5))
    matrix = report["obligationMatrix"]

    hacc_to_benjamin = matrix["org:hacc"]["person:benjamin_barber"]
    quantum_to_hacc = matrix["org:quantum"]["org:hacc"]
    hud_to_hacc = matrix["org:hud"]["org:hacc"]

    assert any("relocation counseling" in item["action"] for item in hacc_to_benjamin)
    assert any("replacement housing" in item["action"] for item in hacc_to_benjamin)
    assert any("forward resident intake/application packets to HACC" == item["action"] for item in quantum_to_hacc)
    assert any("monitor and enforce Section 18 relocation compliance" == item["action"] for item in hud_to_hacc)
    assert any(
        item["modality"] == "prohibited" and "evict before relocation duties are completed" == item["action"]
        for item in hacc_to_benjamin
    )


def test_graphrag_analysis_emits_formal_logic_models():
    report = analyze_title18_corpus(CORPUS_ROOT, current_date=datetime(2026, 4, 5))
    formal_models = report["formalModels"]
    deontic_fol = formal_models["deonticFirstOrderLogic"]
    dcec = formal_models["deonticCognitiveEventCalculus"]

    assert deontic_fol["partyUniverse"]
    assert len(deontic_fol["obligationFormulas"]) == len(report["obligations"])
    assert any(item["temporalStatus"] == "overdue" for item in deontic_fol["obligationFormulas"])
    assert dcec["happens"]
    assert dcec["initiates"]
    assert dcec["holdsAt"]
