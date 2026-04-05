import json
from pathlib import Path

from formal_logic.title18_query import build_dashboard, build_query_summary, query_obligations, render_dashboard_markdown


REPORT_PATH = Path("/home/barberb/HACC/Breach of Contract/outputs/title18_graphrag_obligations.json")


def load_report():
    return json.loads(REPORT_PATH.read_text())


def test_title18_query_can_filter_overdue_hacc_obligations():
    report = load_report()
    obligations = query_obligations(report, actor="org:hacc", temporal_status="overdue")
    summary = build_query_summary(obligations, report)
    assert obligations
    assert summary["byActor"]["org:hacc"] >= 1
    assert summary["byTemporalStatus"]["overdue"] >= 1


def test_title18_query_builds_dashboard_with_overdue_and_prohibited_sections():
    report = load_report()
    dashboard = build_dashboard(report)
    markdown = render_dashboard_markdown(dashboard)
    assert dashboard["headline"]["totalObligations"] >= 10
    assert dashboard["headline"]["overdueObligations"] >= 1
    assert dashboard["prohibited"]
    assert "# Title 18 Obligation Dashboard" in markdown