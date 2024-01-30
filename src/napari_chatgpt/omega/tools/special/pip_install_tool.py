"""A tool for running python code in a REPL."""
import traceback

from arbol import asection, aprint

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.python.installed_packages import is_package_installed
from napari_chatgpt.utils.python.pip_utils import pip_install



class PipInstallTool(AsyncBaseTool):
    """A tool installing python packages with pip."""

    name = "PipInstallTool"
    description = (
        "Use this tool to pip install a list of packages. "
        "The input should be a comma separated list of package names with optional version numbers. "
        "For example, if the input is 'SimpleITK, openCV, cucim' then these three python packages will be installed.  "
        "If you want to install a specific version of a package, you can specify it by adding the version number after the package name. "
        "For example, if the input is 'SimpleITK==2.0.2, openCV==4.5.1, cucim==0.19.0' then these three python packages will be installed with the specified versions. "
        "This tool is useful for installing packages that are not installed by default in the napari environment. "
)

    def _run(self, query: str) -> str:
        """Use the tool."""

        with asection(f"PipInstallTool: query= {query} "):

            try:
                #Split the input into a list of packages:
                packages = query.split(',')

                # Clean up the package names:
                packages = [p.strip() for p in packages]

                # Remove empty strings:
                packages = [p for p in packages if p]

                # Identify that have already been installed using is_package_installed
                already_installed_packages = [p for p in packages if is_package_installed(p)]

                # Remove already installed packages from the list of packages to be installed:
                packages = [p for p in packages if p not in already_installed_packages]

                # If no packages need to be installed, return:
                if len(packages)==0:
                    message = f"No packages need to be installed, all packages are already installed: '{','.join(already_installed_packages)}'.\n"
                    aprint(message)
                    return message

                # Install the packages:
                message = pip_install(packages,
                                      skip_if_installed=True,
                                      ask_permission=False,
                                      included=False)

                if self.notebook:
                    self.notebook.add_code_cell(f"!pip install {' '.join(packages)}")

                aprint(message)
                return message

            except Exception as e:
                error_info = f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to install these packages: '{','.join(packages)}'."
                traceback.print_exc()
                return error_info
