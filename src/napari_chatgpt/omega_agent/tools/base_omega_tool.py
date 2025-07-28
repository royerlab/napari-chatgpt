from abc import abstractmethod

from litemind.agent.tools.function_tool import FunctionTool


class BaseOmegaTool(FunctionTool):
    """
    Base class for tools in the Omega agent.
    """

    def __init__(self, **kwargs):
        """
        Initialize a BaseOmegaTool instance with optional description and name.
        
        If not provided, the description defaults to the class docstring and the name defaults to the class name.
        """

        # Get Tools description:
        description = kwargs.get("description", self.__class__.__doc__)

        # Call super class constructor:
        super().__init__(func=self.run_omega_tool, description=description)

        # Set Tool's name as class:
        self.name = kwargs.get("name", self.__class__.__name__)

    @abstractmethod
    def run_omega_tool(self, query: str = ""):
        """
        Abstract method to execute the Omega tool with the provided query.
        
        Parameters:
            query (str): The input query string for the tool.
        
        Returns:
            The result of the tool execution, as defined by the subclass implementation.
        
        Note:
            Subclasses must implement this method to define the tool's behavior.
        """
        pass

    def normalise_to_string(self, kwargs):

        # extract the value for args key in kwargs:
        """
        Convert input arguments to a normalized string representation.
        
        If the input is a dictionary, extracts the value associated with the "args" key; otherwise, uses the input directly. If the extracted value is a single-element list, unwraps it to the element. Returns the final value as a string.
        """
        query = kwargs.get("args", "") if isinstance(kwargs, dict) else kwargs

        # If query is a singleton list, extract the value:
        if isinstance(query, list) and len(query) == 1:
            query = query[0]

        # convert the query to string:
        query = str(query)
        return query

    def pretty_string(self):
        """
        Return a formatted string summarizing the tool's name and a truncated description if it exceeds 80 characters.
        
        If the description is longer than 80 characters, it is truncated at the first period after the 80th character and an ellipsis is appended.
        Returns:
            str: The formatted string representation of the tool.
        """

        # Shorten description to the first period _after_ 80 characters:
        if len(self.description) > 80:
            description = (
                self.description[: self.description.find(".", 80) + 1] + "[...]"
            )
        else:
            description = self.description

        return f"{self.name}: {description}"
