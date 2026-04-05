import json
from pathlib import Path

from formal_logic.reasoning_exports import (
    build_dcec_export,
    build_flogic_export,
    build_manifest,
    build_prolog_export,
)


REPORT_PATH = Path("/home/barberb/HACC/Breach of Contract/outputs/title18_graphrag_obligations.json")


def load_report():
    return json.loads(REPORT_PATH.read_text())


def test_reasoning_exports_include_core_parties_and_obligations():
    report = load_report()
    prolog = build_prolog_export(report)
    assert "party(org_hacc)." in prolog
    assert "party(org_quantum)." in prolog
    assert "overdue_obligation(O)" in prolog
    assert "obl_person_benjamin_barber_hacc_relocation_counseling" in prolog


def test_reasoning_exports_include_dcec_and_flogic_views():
    report = load_report()
    dcec = build_dcec_export(report)
    flogic = build_flogic_export(report)
    manifest = build_manifest(report)

    assert "Happens(" in dcec
    assert "Initiates(" in dcec
    assert "HoldsAt(" in dcec
    assert ":obligation[" in flogic
    assert "title18_obligations_dcec.pl" in manifest["exports"]