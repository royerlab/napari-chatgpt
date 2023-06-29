from arbol import asection, aprint

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.download.download_files import download_files
from napari_chatgpt.utils.strings.extract_urls import extract_urls


class FileDownloadTool(AsyncBaseTool):
    name = "UrlDownloadTool"
    description = (
        "Use this tool to download file(s) by writing: download(<urls>) where <urls> is a list of valid and syntatically correct URLs. "
        "The file(s) is(are) stored in the current folder using its(their) filename as found in the URL, "
        "and thus is(are) directly accessible using its(their) filename. "
        "Use this tool to download files before any subsequent operations on these files.")

    def _run(self, query: str) -> str:
        """Use the tool."""
        try:

            with asection(f"FileDownloadTool: query= {query} "):
                # extract urls from query
                urls = extract_urls(query)

                # Download files:
                filenames = download_files(urls)

                # Filename as string:
                filenames_str = ', '.join(filenames)

                # message:
                message = f"Successfully downloaded {len(urls)} files: {filenames_str}"

                aprint(message)

                # Respond:
                return message

        except Exception as e:
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to download files from: '{query}'."
