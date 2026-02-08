"""Tests for FileDownloadTool."""

from unittest.mock import MagicMock, patch

from napari_chatgpt.omega_agent.tools.special.file_download_tool import (
    FileDownloadTool,
)


def test_download_with_urls(tmp_path):
    """Test URL extraction and download with mocked HTTP request."""
    tool = FileDownloadTool()

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.raise_for_status = MagicMock()
    fake_response.iter_content = MagicMock(return_value=[b"fake content"])

    with patch(
        "napari_chatgpt.utils.download.download_files.requests.get",
        return_value=fake_response,
    ):
        with patch("os.getcwd", return_value=str(tmp_path)):
            query = "Download https://example.com/image.tif"
            result = tool.run_omega_tool(query)

    assert "Successfully downloaded" in result
    assert "image.tif" in result


def test_download_empty_urls():
    """Test that empty URL query returns clear error."""
    tool = FileDownloadTool()
    result = tool.run_omega_tool("no urls here")
    assert "No valid URLs found" in result
