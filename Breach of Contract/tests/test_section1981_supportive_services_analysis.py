from formal_logic.section1981_supportive_services_analysis import write_outputs


def test_section1981_supportive_services_outputs_exist(tmp_path=None):
    outputs = write_outputs()
    assert outputs["report_json"].exists()
    assert outputs["knowledge_graph"].exists()
    assert outputs["dependency_graph"].exists()
