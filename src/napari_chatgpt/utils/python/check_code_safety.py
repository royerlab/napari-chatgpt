import sys

from arbol import aprint, asection
from langchain.chains import LLMChain
from langchain.llms import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from napari_chatgpt.chat_server.callbacks.callbacks_arbol_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name
from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list

_check_code_safety_prompt = f"""
**Context:**
You are an expert Python coder with extensive cybersecurity experience and knowledge. 
You can analyse complex python code and assess its safety from an user standpoint.

**Task:**
You are given a piece of Python code. Your task is to first assess what the code does and whether it is a threat to the user's machine and files.
You then rank the piece code as follows: 
- A -> The code is super safe. It does not have any IO of any kind (no accessing or deleting files, no networking, etc... ), and is expected to use very little memory and cpu.
- B -> The code is relatively safe. It does not have any IO of any kind, but it does some complex calculations and might use a lot of memory or cpu.
- C -> The code is somewhat safe. It does read files but does nothing suspicious with them, and creates new files, It does not accesses the network. 
- D -> The code is somewhat unsafe. It reads, writes files or accesses the network in ways that might be OK, or not.
- E -> The code is unsafe. It writes or deletes files that might already exist, or accesses the network in a suspicious manner. 

**Notes:**
- Code that is deceptive or malicious should be rated as unsafe. 

**Context:**
- The code is written against Python version: {sys.version.split()[0]}.
- Here is the list of installed packages: {'{installed_packages}'}.

**Code:**

```python
{'{code}'}
```

**Response Format:**
Please return an explanation for your ranking and snippets of code that support your jusgement.
The answer must contain the rank surrounded with asterisks. 
For example you can write: 'For the reasons stated above, the code is rated *B*', or 'The code is rated *B* because...'.

**Explanation of ranking and rank itself:**
"""


def check_code_safety(code: str,
                      llm: BaseLLM = None,
                      model_name: str = None,
                      verbose: bool = False) -> str:
    with(asection(
            f'Checking safety of code of length: {len(code)}')):

        try:

            # Cleanup code:
            code = code.strip()

            # If code is empty, nothing to improve!
            if len(code) == 0:
                return 'No code is safe code,', 'A'

            aprint(f'Input code:\n{code}')

            # Instantiates LLM if needed:
            llm = llm or ChatOpenAI(model_name=model_name or get_default_openai_model_name(),
                                    temperature=0)

            # Make prompt template:
            prompt_template = PromptTemplate(template=_check_code_safety_prompt,
                                             input_variables=["code", 'installed_packages'])

            # Instantiate chain:
            chain = LLMChain(
                prompt=prompt_template,
                llm=llm,
                verbose=verbose,
                callbacks=[ArbolCallbackHandler('Check Code Safety')]
            )

            # List of installed packages:
            package_list = installed_package_list()

            # Variable for prompt:
            variables = {"code": code, 'installed_packages': ' '.join(package_list)}

            # call LLM:
            response = chain.invoke(variables)['text']

            # Cleanup:
            response = response.strip()

            # Find the upper case letter between asterisks, for example A in *A*, buy serachinhg for the four ranks: *A*, *B*, *C*, *D*, *E*:
            if '*A*' in response or '*Rank: A*' in response:
                safety_rank = 'A'
            elif '*B*' in response or '*Rank: B*' in response:
                safety_rank = 'B'
            elif '*C*' in response or '*Rank: C*' in response:
                safety_rank = 'C'
            elif '*D*' in response or '*Rank: D*' in response:
                safety_rank = 'D'
            elif '*E*' in response or '*Rank: E*' in response:
                safety_rank = 'E'
            else:
                safety_rank = 'Unknown'

            return response, safety_rank

        except Exception as e:
            import traceback
            traceback.print_exc()
            aprint(e)
            return '', 'Unknown'



