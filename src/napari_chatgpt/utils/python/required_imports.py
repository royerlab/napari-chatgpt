import importlib
import sys
import traceback

from arbol import asection, aprint

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_required_imports_prompt = \
f"""
**Context:**
You are an expert Python coder with extensive knowledge of all python libraries, and their different versions.

**Task:**
You competently list all and only necessary import statements required to run without error the following python ({sys.version.split()[0]}) code:

**CODE:**

```python
{'{input}'}
```

**Important Notes:**
Please include all imports already in the code and add any import statements that are missing but are required for the code to run correctly.
Note: No need to add import statements for the napari viewer, and for the variable 'viewer'.
If no additional import statements are required to run this code, just return an empty string.
Answer should be in markdown format with one import statement per line without explanations before or after.
Make sure we have the right answer.

**ANSWER in markdown:**
"""


def required_imports(code: str, llm: LLM = None, verbose: bool = False):
    """
    Determine and return a list of validated import statements required to run the given Python code snippet without errors.
    
    Parameters:
        code (str): The Python code snippet to analyze.
    
    Returns:
        list of str: Import statements necessary for the code to execute, validated for correctness.
    """
    with asection(
        f"Automatically determines missing imports for code of length: {len(code)}"
    ):
        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing is missing!
        if len(code) == 0:
            return []

        # Instantiates LLM if needed:
        llm = llm or get_llm()

        variables = {"input": code}

        # call LLM:
        result = llm.generate(
            _required_imports_prompt, variables=variables, temperature=0.0
        )

        # Extract text from messages:
        response_text = "\n".join([m.to_plain_text() for m in result])

        # Extract code:
        list_of_imports_str = extract_code_from_markdown(response_text)

        # Parse the list:
        list_of_imports = list_of_imports_str.split("\n")

        # Filter the list of imports for bad ones:
        list_of_imports = list(
            [i for i in list_of_imports if check_import_statement(i)]
        )

        aprint(f"List of missing imports:\n{list_of_imports}")

    return list_of_imports


def check_import_statement(import_statement):
    """
    Validate whether a given Python import statement is syntactically correct and references existing modules and names.
    
    Parameters:
        import_statement (str): The import statement to validate.
    
    Returns:
        bool: True if the import statement is valid and all referenced modules and names exist; False otherwise.
    """
    with asection(
        f"Checking the validity of suggested import statement: '{import_statement}'"
    ):
        try:
            # Cleanup import statement:
            import_statement = import_statement.strip()

            # remove the 'as' statement:
            if " as " in import_statement:
                index = import_statement.find(" as ")
                import_statement = import_statement[:index].strip()

            # Extract modules and names:
            if import_statement.startswith("import "):
                import_statement = import_statement[7:]

                # cleanup module name:
                module_name = import_statement.strip()

                names = None
            elif import_statement.startswith("from "):
                import_statement = import_statement[5:]

                # Split the import statement into module and names
                module_name, names = import_statement.split(" import ")

                # cleanup module name:
                module_name = module_name.strip()

                # Names:
                names = names.split()
            else:
                aprint(f"This is not an import statement: '{import_statement}' !")
                return False

            # cleanup module name and names:
            module_name = module_name.strip()
            names = [n.strip() for n in names] if names else None

            # Check module's existence:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                aprint(f"Module '{module_name}' does not exist.")
                return False

            aprint(f"Module '{module_name}' exists.")

            # Do we need to check whether the names exist?
            if names:
                # Loading module from spec:
                module = importlib.util.module_from_spec(spec)

                # Loading from spec:
                spec.loader.exec_module(module)

                # Checking if each name exists:
                for name in names:
                    if hasattr(module, name):
                        aprint(f"Name '{name}' exists within module '{module_name}'.")
                    else:
                        aprint(
                            f"Name '{name}' does not exist within module '{module_name}'."
                        )
                        return False

            return True

        except Exception:
            traceback.print_exc()
            aprint(f"Import statement: '{import_statement}' is problematic!")
            return False
