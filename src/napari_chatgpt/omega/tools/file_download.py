from arbol import asection

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.download_files import download_files
from napari_chatgpt.utils.extract_urls import extract_urls


class FileDownloadTool(AsyncBaseTool):
    name = "UrlDownload"
    description = (
        "Use this tool to download file(s) by writing: download(<url>) where <url> is a valid syntatically corect url. "
        "The file(s) is(are) stored in the current folder using its(their) filename as found in the URL, "
        "and thus is(are) directly accessible using its(their) filename. "
        "Use this tool to download files before any subsequent operations.")

    def _run(self, query: str) -> str:
        """Use the tool."""

        with asection(f"Using FileDownloadTool with query: {query} "):

            try:
                # extract urls from query
                urls = extract_urls(query)

                # Download files:
                filenames = download_files(urls)

                # Respond:
                return f"Successfully downloaded {len(urls)} file: {', '.join(filenames)}"

            except Exception as e:
                return f"Exception: {type(e).__name__} with message: {e.args[0]}"
