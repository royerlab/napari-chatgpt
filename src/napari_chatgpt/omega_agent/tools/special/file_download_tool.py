from arbol import asection, aprint

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.download.download_files import download_files
from napari_chatgpt.utils.strings.extract_urls import extract_urls


class FileDownloadTool(BaseOmegaTool):
    """
    A tool for downloading files from URLs.
    This tool can download files from valid and syntactically correct URLs.
    """

    def __init__(self, **kwargs):
        """
        Initialize the FileDownloadTool with a specific name and usage description.
        """
        super().__init__(**kwargs)

        self.name = "UrlDownloadTool"
        self.description = (
            "Use this tool to download file(s) by writing: download(<urls>) where <urls> is a list of valid and syntatically correct URLs. "
            "The file(s) is(are) stored in the current folder using its(their) filename as found in the URL, "
            "and thus is(are) directly accessible using its(their) filename. "
            "Use this tool to download files before any subsequent operations on these files."
        )

    def run_omega_tool(self, query: str = ""):

        """
        Downloads files from URLs found in the input query string.
        
        Extracts all valid URLs from the provided query, downloads the corresponding files, and returns a message summarizing the number and names of files downloaded. If an error occurs during extraction or download, returns an error message with details.
         
        Parameters:
            query (str): The input string potentially containing URLs to download.
        
        Returns:
            str: A message indicating the result of the download operation or an error message if the process fails.
        """
        try:
            with asection(f"FileDownloadTool:"):
                with asection(f"Query:"):
                    aprint(query)

                # extract urls from query
                urls = extract_urls(query)

                # Download files:
                filenames = download_files(urls)

                # Filename as string:
                filenames_str = ", ".join(filenames)

                # message:
                message = f"Successfully downloaded {len(urls)} files: {filenames_str}"

                aprint(message)

                # Respond:
                return message

        except Exception as e:
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to download files from: '{query}'."
