"""Abstract base class for all Omega agent tools.

Every tool used by the Omega agent inherits from ``BaseOmegaTool``,
which bridges LiteMind's ``FunctionTool`` interface with the Omega
tool conventions (name defaulting to the class name, description
defaulting to the class docstring, and a unified ``run_omega_tool``
entry point).
"""

from abc import abstractmethod

from litemind.agent.tools.function_tool import FunctionTool


class BaseOmegaTool(FunctionTool):
    """Abstract base for all Omega tools.

    Wraps LiteMind's ``FunctionTool`` so that subclasses only need to
    implement ``run_omega_tool``. The tool name defaults to the class
    name and the description defaults to the class docstring, but both
    can be overridden via keyword arguments.
    """

    def __init__(self, **kwargs):
        """Initialise the tool.

        Args:
            **kwargs: Accepted keys include ``name`` (tool name,
                defaults to class name), ``description`` (defaults to
                class docstring), and ``notebook`` (optional Jupyter
                notebook for code recording). All other keys are
                silently ignored to allow shared ``tool_context`` dicts
                to be unpacked.
        """

        # Get Tools description:
        description = kwargs.get("description", self.__class__.__doc__)

        # Call super class constructor:
        super().__init__(func=self.run_omega_tool, description=description)

        # Set Tool's name as class:
        self.name = kwargs.get("name", self.__class__.__name__)

        # Store notebook reference (used by PipInstallTool, PythonCodeExecutionTool, etc.):
        self.notebook = kwargs.get("notebook")

    @abstractmethod
    def run_omega_tool(self, query: str = ""):
        """Execute the tool's core logic.

        This is the single entry point called by LiteMind's function-tool
        dispatch. Subclasses must implement this method.

        Args:
            query: The user request or task description provided by the
                agent.

        Returns:
            A string describing the outcome (success message, error
            message, or informational result).
        """

    def normalise_to_string(self, kwargs):
        """Normalise heterogeneous tool arguments to a single string.

        Handles dicts with an ``args`` key, singleton lists, and plain
        values, converting them all to a ``str``.

        Args:
            kwargs: Raw arguments from the LLM dispatch (may be a dict,
                list, or scalar).

        Returns:
            The normalised query string.
        """

        # extract the value for args key in kwargs:
        query = kwargs.get("args", "") if isinstance(kwargs, dict) else kwargs

        # If query is a singleton list, extract the value:
        if isinstance(query, list) and len(query) == 1:
            query = query[0]

        # convert the query to string:
        query = str(query)
        return query

    def pretty_string(self):
        """Return a concise ``name: description`` summary of the tool.

        Descriptions longer than 80 characters are truncated at the
        first sentence boundary after 80 characters.

        Returns:
            A formatted string of the form ``"ToolName: description..."``.
        """

        # Shorten description to the first period _after_ 80 characters:
        if len(self.description) > 80:
            period_pos = self.description.find(".", 80)
            if period_pos == -1:
                description = self.description[:80] + "..."
            else:
                description = self.description[: period_pos + 1] + "[...]"
        else:
            description = self.description

        return f"{self.name}: {description}"
