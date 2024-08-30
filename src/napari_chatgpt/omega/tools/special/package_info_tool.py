"""A tool for running python code in a REPL."""
import traceback
from typing import Any

from arbol import asection, aprint

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list
from napari_chatgpt.utils.python.relevant_libraries import \
    get_all_relevant_packages


class PythonPackageInfoTool(AsyncBaseTool):
    """A tool for querying and searching the list of installed packages."""

    name = "PackageInfoTool"
    description = (
        "Use this tool for querying and searching the list of installed package sin the system. "
        "You can provide a substring to search for a specific package or list of packages. "
        "For example, send and empty string to get the full list of installed packages. "
        "For example, send: `numpy` to get the information about the numpy package. "
    )

    def _run(self,
             *args: Any,
             **kwargs: Any
    ) -> Any:

        # Get query:
        query = self.normalise_to_string(kwargs)

        with asection(f"PythonPackageInfoTool: query= {query} "):

            try:
                # remove white spaces and other non alphanumeric characters from the query:
                query = query.strip()

                # Get list of all python packages installed
                packages = installed_package_list(filter=None)

                # If query is not empty, filter the list of packages:
                if query:
                    packages = [p for p in packages if query.lower() in p.lower()]

                # If the list of packages is too long, restrict to signal processing related packages,
                # then take the intersection of packages and get_all_relevant_packages():
                if len(packages) > 50:
                    packages = [p for p in packages if p.lower() in get_all_relevant_packages()]

                # convert the list of packages to a string:
                result = "\n".join(packages)

                aprint(result)
                return result

            except Exception as e:
                error_info = f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to get information about packages containing: '{query}'."
                traceback.print_exc()
                return error_info
