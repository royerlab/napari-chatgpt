from napari_chatgpt.omega_agent.tools.special.functions_info_tool import (
    PythonFunctionsInfoTool,
)


def test_tools():
    tool = PythonFunctionsInfoTool()

    query = "skimage.morphology.watershed"
    result = tool.run_omega_tool(query)
    assert len(result) < 300
    assert "markers = None" in result

    query = "*skimage.morphology.watershed"
    result = tool.run_omega_tool(query)
    assert len(result) > 300
    assert "markers" in result
