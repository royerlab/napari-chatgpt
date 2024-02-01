import importlib
import sys
import traceback

from arbol import asection, aprint
from langchain.callbacks.manager import CallbackManager
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM
from langchain_core.prompts import PromptTemplate

from napari_chatgpt.chat_server.callbacks.callbacks_arbol_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_required_imports_prompt = f"""
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


def required_imports(code: str,
                     llm: BaseLLM = None,
                     verbose: bool = False):
    with(asection(
            f'Automatically determines missing imports for code of length: {len(code)}')):
        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing is missing!
        if len(code) == 0:
            return []

        # Instantiates LLM if needed:
        llm = llm or ChatOpenAI(model_name=get_default_openai_model_name(),
                                temperature=0)

        # Make prompt template:
        prompt_template = PromptTemplate(template=_required_imports_prompt,
                                         input_variables=["input"])

        # Instantiate chain:
        chain = LLMChain(
            prompt=prompt_template,
            llm=llm,
            verbose=verbose,
            callback_manager=CallbackManager(
                [ArbolCallbackHandler('Required imports')])
        )

        # Variable for prompt:
        variables = {'input': code}

        # call LLM:
        list_of_imports_str = chain(variables)['text']

        # Extract code:
        list_of_imports_str = extract_code_from_markdown(list_of_imports_str)

        # Parse the list:
        list_of_imports = list_of_imports_str.split('\n')

        # Filter the list of imports for bad ones:
        list_of_imports = list([i for i in list_of_imports if check_import_statement(i)])

        aprint(f'List of missing imports:\n{list_of_imports}')

    return list_of_imports


def check_import_statement(import_statement):

    with asection(f"Checking the validity of suggested import statement: '{import_statement}'"):
        try:
            # Cleanup import statement:
            import_statement = import_statement.strip()

            # remove the 'as' statement:
            if ' as ' in import_statement:
                index = import_statement.find(' as ')
                import_statement = import_statement[:index].strip()

            # Extract modules and names:
            if import_statement.startswith('import '):
                import_statement = import_statement[7:]

                # cleanup module name:
                module_name = import_statement.strip()

                names = None
            elif import_statement.startswith('from '):
                import_statement = import_statement[5:]

                # Split the import statement into module and names
                module_name, names = import_statement.split(' import ')

                # cleanup module name:
                module_name = module_name.strip()

                # Names:
                names = names.split()
            else:
                aprint(
                    f"This is not an import statement: '{import_statement}' !")
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
                            f"Name '{name}' does not exist within module '{module_name}'.")
                        return False

            return True

        except Exception:
            traceback.print_exc()
            aprint(f"Import statement: '{import_statement}' is problematic!")
            return False