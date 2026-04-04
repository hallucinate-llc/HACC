import json
from pathlib import Path

from engine.evaluate_case import evaluate_case


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def load_fixture(name: str):
    return json.loads((FIXTURE_DIR / name).read_text())


def test_positive_constructive_denial_case():
    result = evaluate_case(load_fixture("live_in_aide_case.json"))
    assert result["outcome"]["sleepInterruption"] is True
    assert result["outcome"]["necessary"] is True
    assert result["outcome"]["reasonable"] is True
    assert result["outcome"]["dutyToGrant"] is True
    assert result["outcome"]["constructiveDenial"] is True
    assert result["outcome"]["violation"] is True
    assert result["missingEvidence"] == []
    assert result["authoritySupport"]["reasonable"]


def test_undue_burden_defeats_reasonable_but_not_constructive_denial():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "undue_burden_case"
    payload["acceptedFindings"]["undue_burden"] = True
    result = evaluate_case(payload)
    assert result["outcome"]["sleepInterruption"] is True
    assert result["outcome"]["reasonable"] is False
    assert result["outcome"]["dutyToGrant"] is False
    assert result["outcome"]["constructiveDenial"] is True
    assert result["outcome"]["violation"] is True


def test_living_room_sleeping_still_counts_as_privacy_harm():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "privacy_harm_case"
    payload["acceptedFindings"]["night_access_needed"] = False
    payload["acceptedFindings"]["works_remotely"] = False
    payload["acceptedFindings"]["privacy_loss"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["sleepInterruption"] is False
    assert result["outcome"]["workInterference"] is False
    assert result["outcome"]["privacyLoss"] is True
    assert result["outcome"]["necessary"] is True
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["violation"] is True


def test_alternative_private_sleeping_space_avoids_violation():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "alternative_private_sleeping_space"
    payload["acceptedFindings"]["aide_sleeps_in_living_room"] = False
    payload["acceptedFindings"]["night_access_needed"] = False
    payload["acceptedFindings"]["works_remotely"] = False
    payload["acceptedFindings"]["privacy_loss"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["sleepInterruption"] is False
    assert result["outcome"]["privacyLoss"] is False
    assert result["outcome"]["necessary"] is False
    assert result["outcome"]["reasonable"] is False
    assert result["outcome"]["dutyToGrant"] is False
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["violation"] is False


def test_missing_request_blocks_duty_to_grant():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "missing_request_case"
    payload["acceptedFindings"]["requested_separate_bedroom"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["dutyToGrant"] is False
    assert "requested_separate_bedroom" in result["missingEvidence"]


def test_accepted_findings_override_asserted_facts_and_report_conflicts():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "conflict_case"
    payload["acceptedFindings"]["works_remotely"] = False
    result = evaluate_case(payload)
    assert result["facts"]["resolved"]["works_remotely"] is False
    assert any(item["fact"] == "works_remotely" for item in result["facts"]["conflicts"])
