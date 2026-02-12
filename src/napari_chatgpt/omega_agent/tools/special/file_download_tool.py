"""Tool for downloading files from URLs to local storage.

Extracts URLs from the agent's input text, downloads each file to the
current working directory, and returns the resulting local file paths
so subsequent tools can operate on the downloaded files.
"""

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.download.download_files import download_files
from napari_chatgpt.utils.strings.extract_urls import extract_urls


class FileDownloadTool(BaseOmegaTool):
    """Tool for downloading files from URLs to the local filesystem.

    Parses the input for valid URLs, downloads each file, and returns
    the local file paths. Useful as a prerequisite step before tools
    that need to operate on local files (e.g., opening images in napari).

    Attributes:
        name: Tool identifier string (set to ``'UrlDownloadTool'``).
        description: Human-readable description used by the LLM agent.
    """

    def __init__(self, **kwargs):
        """Initialize the FileDownloadTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
        """
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
        """Extract URLs from the query and download the corresponding files.

        Args:
            query: Free-text input that may contain one or more URLs.

        Returns:
            A success message listing downloaded file paths, an error if no
            valid URLs are found, or an error message if downloading fails.
        """
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
