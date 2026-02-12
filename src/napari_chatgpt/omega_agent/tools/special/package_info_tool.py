"""Tool for querying the list of installed Python packages.

Provides the Omega agent with the ability to discover which Python
packages (and their versions) are currently installed, optionally
filtering by a substring query. Useful for verifying availability
before generating code that depends on specific libraries.
"""

import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.python.installed_packages import (
    installed_package_list,
)

_MAX_PACKAGES = 200


class PythonPackageInfoTool(BaseOmegaTool):
    """Tool for searching and listing installed Python packages.

    Returns a sorted, deduplicated list of installed packages. An
    optional substring query filters results; an empty query returns
    all packages (up to ``_MAX_PACKAGES``).

    Attributes:
        name: Tool identifier string (set to ``'PackageInfoTool'``).
        description: Human-readable description used by the LLM agent.
    """

    def __init__(self, **kwargs):
        """Initialize the PythonPackageInfoTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
        """
        super().__init__(**kwargs)

        self.name = "PackageInfoTool"
        self.description = (
            "Use this tool to search the list of installed Python "
            "packages. Provide a substring to filter (e.g. 'numpy' "
            "to find numpy and its version). "
            "An empty query returns all installed packages."
        )

    def run_omega_tool(self, query: str = ""):
        """Search installed packages and return matching entries.

        Args:
            query: Substring to filter package names by. An empty string
                returns all installed packages (up to ``_MAX_PACKAGES``).

        Returns:
            A newline-separated list of matching package names and
            versions, or an error message if retrieval fails.
        """
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
