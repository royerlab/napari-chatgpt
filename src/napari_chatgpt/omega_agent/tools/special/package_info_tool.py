"""A tool for querying the list of installed packages."""

import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.python.installed_packages import (
    installed_package_list,
)

_MAX_PACKAGES = 200


class PythonPackageInfoTool(BaseOmegaTool):
    """
    A tool for querying and searching the list of
    installed packages.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "PackageInfoTool"
        self.description = (
            "Use this tool to search the list of installed Python "
            "packages. Provide a substring to filter (e.g. 'numpy' "
            "to find numpy and its version). "
            "An empty query returns all installed packages."
        )

    def run_omega_tool(self, query: str = ""):

        with asection("PythonPackageInfoTool:"):
            with asection("Query:"):
                aprint(query)

            try:
                query = query.strip()

                # Get all installed packages (no hardcoded filter):
                packages = installed_package_list(filter=None, clean_up=False)

                # Filter by query substring if provided:
                if query:
                    q = query.lower()
                    packages = [p for p in packages if q in p.lower()]

                # Sort alphabetically for consistent output:
                packages = sorted(set(packages))

                # Truncate if too many:
                if len(packages) > _MAX_PACKAGES:
                    packages = packages[:_MAX_PACKAGES]
                    packages.append(
                        f"... ({len(packages)} shown, "
                        f"use a search term to narrow results)"
                    )

                result = "\n".join(packages)

                aprint(result)
                return result

            except Exception as e:
                error_info = (
                    f"Error: {type(e).__name__} with message: "
                    f"'{str(e)}' occurred while trying to get "
                    f"information about packages containing: "
                    f"'{query}'."
                )
                traceback.print_exc()
                return error_info
