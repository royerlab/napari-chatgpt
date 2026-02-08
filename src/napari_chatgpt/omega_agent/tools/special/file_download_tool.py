from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.download.download_files import download_files
from napari_chatgpt.utils.strings.extract_urls import extract_urls


class FileDownloadTool(BaseOmegaTool):
    """
    A tool for downloading files from URLs.
    This tool can download files from valid and syntactically correct URLs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "UrlDownloadTool"
        self.description = (
            "Use this tool to download files from URLs. "
            "Provide the URLs in the input and the files will be "
            "downloaded to the current folder. "
            "The tool returns the full file paths of the downloaded files. "
            "Use this tool to download files before any subsequent "
            "operations on these files."
        )

    def run_omega_tool(self, query: str = ""):

        try:
            with asection("FileDownloadTool:"):
                with asection("Query:"):
                    aprint(query)

                # extract urls from query
                urls = extract_urls(query)

                if not urls:
                    return (
                        "Error: No valid URLs found in the input. "
                        "Please provide valid URLs to download."
                    )

                # Download files:
                file_paths = download_files(urls)

                # File paths as string:
                file_paths_str = ", ".join(file_paths)

                # message:
                message = (
                    f"Successfully downloaded "
                    f"{len(urls)} file(s): "
                    f"{file_paths_str}"
                )

                aprint(message)

                # Respond:
                return message

        except Exception as e:
            return (
                f"Error: {type(e).__name__} with message: '{e}' "
                f"occurred while trying to download files from: '{query}'."
            )
