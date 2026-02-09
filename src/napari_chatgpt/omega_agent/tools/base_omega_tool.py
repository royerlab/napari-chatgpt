from abc import abstractmethod

from litemind.agent.tools.function_tool import FunctionTool


class BaseOmegaTool(FunctionTool):
    """
    Base class for tools in the Omega agent.
    """

    def __init__(self, **kwargs):
        """
        Initialize the tool with the provided keyword arguments.
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
        """
        This is an adapter function to bridge between Omega tools and Litemind's Function tools
        Parameters
        ----------
        query

        Returns
        -------

        """

    def normalise_to_string(self, kwargs):

        # extract the value for args key in kwargs:
        query = kwargs.get("args", "") if isinstance(kwargs, dict) else kwargs

        # If query is a singleton list, extract the value:
        if isinstance(query, list) and len(query) == 1:
            query = query[0]

        # convert the query to string:
        query = str(query)
        return query

    def pretty_string(self):
        """
        Return a pretty string representation of the tool agent.

        Returns
        -------
        str
            A pretty string representation of the tool agent.
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
