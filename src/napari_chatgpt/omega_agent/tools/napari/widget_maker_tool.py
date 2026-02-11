"""Tool for creating napari magicgui widgets via an agentic sub-agent.

This module provides ``NapariWidgetMakerTool``, which uses a self-correcting
sub-agent loop to generate, validate, and dock ``@magicgui``-decorated
widget functions in the napari viewer.  The sub-agent is given a
``submit_widget_code`` tool that executes the generated code on the Qt
thread and provides error feedback, allowing up to 3 retry attempts.
"""

import sys
import traceback

from arbol import aprint, asection
from litemind.agent.agent import Agent
from litemind.agent.tools.function_tool import FunctionTool
from litemind.agent.tools.toolset import ToolSet
from napari import Viewer

from napari_chatgpt.omega_agent.napari_bridge import _get_viewer_info
from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.omega_agent.tools.generic_coding_instructions import (
    omega_generic_codegen_instructions,
)
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.strings.find_function_name import (
    find_magicgui_decorated_function_name,
)
from napari_chatgpt.utils.strings.trailing_code import remove_trailing_code
from napari_chatgpt.utils.system.information import system_info

_SUB_AGENT_SYSTEM_PROMPT = """
You are a specialized code generator for napari magicgui widgets.

**Workflow:**
1. Generate the widget code based on the user's request.
2. Call the `submit_widget_code` tool with your code as the `code` argument.
3. If the tool returns an error, read the error message carefully, fix your code, and call `submit_widget_code` again.
4. Repeat until the tool returns a success message or you run out of attempts.

**Rules:**
- Do NOT include these imports (they are automatically prepended):
  `from magicgui import magicgui`, `from napari.types import ...`,
  `from napari.layers import ...`, `import numpy as np`, `from typing import Union`
- Do NOT call `viewer.window.add_dock_widget()` — that is handled automatically after your code succeeds.
- Do NOT create a new `napari.Viewer()` or call `napari.run()`.
- You MUST call the `submit_widget_code` tool with your code. Do not just return code as text.

**Instructions:**
{instructions}

{last_generated_code}

**Viewer Information:**
{viewer_information}

**System Information:**
{system_information}
"""

_instructions = """

## Preamble
Write **one** napari + magicgui widget function. The caller handles docking the widget and launching napari.

---

**General Rules**
- Emit **only code** (plus minimal docstrings if helpful). No extra prose or examples.
- Write **exactly one** widget. Define helper functions *inside* the main widget if needed.
- Avoid side-effects (prints, file I/O, logging) unless explicitly asked.

---

**Labels Arrays:**
- Keep label data integer. Cast with `arr.astype(np.uint32, copy=False)` if needed.
- **Never** convert labels to float.

---

**`@magicgui` Decorator:**
- Decorate with `@magicgui(call_button='<action>')` using a concise verb phrase (e.g. `"Apply Threshold"`).
- Use `result_widget=True` **only** for small scalar/string/tuple return values.
- Float slider: `some_float={"widget_type":"FloatSlider", "min":0.0, "max":1.0}`.
- Dropdown: `choice={"choices":["first","second","third"]}`.
- Do **not** use tuples, `*args`, or `**kwargs` as parameters.
- Put layer/data parameters **first** in the signature.

---

**Return Values:**
- Return **exactly one** of:
  1. NumPy array typed as `<LayerType>Data` (`ImageData`, `LabelsData`, etc.).
  2. Concrete napari `Layer` instance (`Image`, `Labels`, `Points`, etc.).
  3. `napari.types.LayerDataTuple` (or a list of tuples).

- To update an existing layer, include `metadata["name"]` in your `LayerDataTuple`.
- Prefer returning data via return values rather than calling `viewer.add_*()` directly.
- **Never** call `viewer.window.add_dock_widget()` — docking is handled automatically.

---

**Viewer Usage:**
- If the widget needs the viewer, use the injected `viewer` for read-only tasks only.
- If the widget does not need the viewer, omit it from the signature.

---

**Type Hint Style:**
Choose **one** style consistently:

| Style | Parameter hints | Data access |
|-------|-----------------|-------------|
| *Array-oriented* | `ImageData`, `LabelsData`, etc. | Operate on the NumPy array directly. |
| *Layer-oriented* | `Image`, `Labels`, etc. | Access data via `layer.data`. |

Do **not** mix styles in one function.

"""

_code_prefix = """
from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
from napari.layers import Image, Labels, Points, Shapes, Surface, Tracks, Vectors
import numpy as np
from typing import Union
"""

_code_lines_to_filter_out = [
    "viewer = napari.Viewer(",
    "viewer = Viewer(",
    "viewer.window.add_dock_widget(",
    "napari.run(",
    "gui_qt(",
]


class _WidgetCodeSubmitTool(FunctionTool):
    """FunctionTool that the sub-agent calls to submit and execute widget code.

    Each invocation sends the code to the napari Qt thread for execution.
    If the code fails, the error is returned so the sub-agent can fix it
    and retry (up to ``max_attempts``).

    Attributes:
        last_successful_code: The code string that last succeeded, or ``None``.
        last_function_name: The name of the last successfully created widget
            function, or ``None``.
    """

    def __init__(
        self,
        to_napari_queue,
        from_napari_queue,
        code_prefix,
        max_attempts=3,
    ):
        super().__init__(
            func=self.submit_widget_code,
            description=(
                "Submit magicgui widget code for execution in napari. "
                "The code argument must contain a complete @magicgui-decorated function. "
                "Returns 'Success: ...' if the widget was created, or an error message if it failed."
            ),
        )
        self._to_napari_queue = to_napari_queue
        self._from_napari_queue = from_napari_queue
        self._code_prefix = code_prefix
        self._max_attempts = max_attempts
        self._attempt_count = 0
        self.last_successful_code = None
        self.last_function_name = None

    def submit_widget_code(self, code: str) -> str:
        """Submit widget code for execution in napari.

        Parameters
        ----------
        code : str
            The complete Python code containing a @magicgui-decorated function.

        Returns
        -------
        str
            Success message if the widget was created, or an error description.
        """
        self._attempt_count += 1

        if self._attempt_count > self._max_attempts:
            return (
                f"STOP: Maximum attempts ({self._max_attempts}) exceeded. "
                f"The widget could not be created. Do not retry."
            )

        with asection(
            f"WidgetCodeSubmitTool attempt {self._attempt_count}/{self._max_attempts}"
        ):
            aprint(f"Received code of length: {len(code)}")

            # Execute on the napari Qt thread via the queue:
            def delegated_function(v):
                return self._execute_widget_code(code, v)

            self._to_napari_queue.put(delegated_function)
            response = self._from_napari_queue.get()

            if isinstance(response, ExceptionGuard):
                error_desc = response.exception_description or str(
                    response.exception_value
                )
                error_msg = (
                    f"Error on attempt {self._attempt_count}/{self._max_attempts}: "
                    f"{response.exception_type_name}: {error_desc}\n"
                    f"Please fix the code and call submit_widget_code again."
                )
                with asection("Widget code execution failed:"):
                    aprint(error_msg)
                return error_msg

            # response is a success/error string from _execute_widget_code
            with asection("Widget code execution result:"):
                aprint(response)
            return response

    def _execute_widget_code(self, code: str, viewer: Viewer) -> str:
        """Execute widget code on the Qt thread and dock the resulting widget.

        Prepends the code prefix, filters forbidden lines, finds the
        ``@magicgui``-decorated function, dynamically imports it, and docks
        it in the viewer.  Exceptions propagate to ``ExceptionGuard``.

        Args:
            code: The raw Python code from the sub-agent.
            viewer: The active napari viewer instance.

        Returns:
            A success or error message string.
        """

        # Extract code from markdown if needed:
        code = extract_code_from_markdown(code)

        # Prepend code prefix:
        code = self._code_prefix + code

        # Add spacing:
        code = "\n\n" + code + "\n\n"

        # Filter forbidden lines (standard _prepare_code logic):
        code = filter_lines(
            code,
            [
                "from __future__",
                "napari.Viewer(",
                "= Viewer(",
                "gui_qt(",
                "viewer.window.add_dock_widget(",
            ],
        )

        # Find the magicgui-decorated function name:
        function_name = find_magicgui_decorated_function_name(code)
        if not function_name:
            return (
                f"Error on attempt {self._attempt_count}/{self._max_attempts}: "
                f"Could not find a @magicgui-decorated function in the code. "
                f"Make sure the code has a function decorated with @magicgui. "
                f"Please fix and call submit_widget_code again."
            )

        # Filter widget-specific forbidden lines:
        code = filter_lines(code, _code_lines_to_filter_out)

        # Remove trailing code after the function definition:
        code = remove_trailing_code(code)

        # Dynamically import and execute:
        loaded_module = dynamic_import(code)
        function = getattr(loaded_module, function_name)

        # Dock the widget:
        viewer.window.add_dock_widget(function, name=function_name)

        # Store the successful code and function name:
        self.last_successful_code = code
        self.last_function_name = function_name

        return f"Success: Widget '{function_name}' created and docked in the viewer."


class NapariWidgetMakerTool(BaseNapariTool):
    """LLM-driven tool for creating ``@magicgui`` widgets in napari.

    Unlike other napari tools, this one uses an agentic sub-agent loop with
    self-correction: the sub-agent generates widget code, submits it via
    ``_WidgetCodeSubmitTool``, and retries on failure (up to 3 attempts).
    The resulting widget is automatically docked in the napari viewer.

    Attributes:
        code_prefix: Common imports prepended to generated code.
        instructions: Detailed coding instructions for the sub-agent.
    """

    def __init__(self, **kwargs):
        """Initialize the widget maker tool.

        Args:
            **kwargs: Forwarded to ``BaseNapariTool.__init__``.
        """
        super().__init__(**kwargs)

        self.name = "NapariWidgetMakerTool"
        self.description = (
            "Use this tool to make a napari widget. "
            "Input must be a plain text description of the requested function and its parameters. "
            "The input must not assume knowledge of our conversation. "
            "For instance, if the input is for a 'Gaussian filter with a sigma parameter', "
            "this tool will make a napari widget that can apply a Gaussian filter to an image. "
            "Another example: if the input is to 'add a mean parameter to the previous widget', "
            "this tool will make a new version of the previously generated widget, but with mean parameter. "
            "Important: The input must fully describe the widget every time, "
            "and in addition describe the modifications or fixes. "
            "This tool only makes widgets from function descriptions, "
            "it does not directly process or analyse images or other napari layers. "
            "Only use this tool when you need to make, modify, or fix a widget, not to answer questions! "
            "Do NOT include code in the input."
        )

        self.code_prefix = _code_prefix
        self.prompt = None  # We override run_omega_tool entirely, no sub-LLM prompt
        self.instructions = _instructions
        self.save_last_generated_code = False
        self.return_direct: bool = True

    def run_omega_tool(self, query: str = "") -> str:
        """Create a magicgui widget using a self-correcting sub-agent.

        Builds the system prompt with viewer/system context, creates a
        fresh ``_WidgetCodeSubmitTool`` and sub-agent, and runs the agent
        with the user's query.  On success, the widget code is saved to
        the notebook and snippet editor.

        Args:
            query: Plain-text description of the desired widget.

        Returns:
            A success message if the widget was created, or an error message.
        """
        with asection("NapariWidgetMakerTool (agentic):"):
            with asection("Query:"):
                aprint(query)

            # Build context strings (same as BaseNapariTool.run_omega_tool):
            if self.last_generated_code:
                last_generated_code = (
                    "**Previously Generated Code:**\n"
                    "Use this code for reference, useful if you need to modify or fix the code. "
                    "IMPORTANT: This code might not be relevant to the current request or task! "
                    "You should ignore it, unless you are explicitly asked "
                    "to fix or modify the last generated widget!\n"
                    "```python\n" + self.last_generated_code + "\n"
                    "```\n"
                )
            else:
                last_generated_code = ""

            filled_generic_instructions = omega_generic_codegen_instructions.format(
                python_version=str(sys.version.split()[0]),
                packages=", ".join(self._installed_package_list),
            )
            instructions = filled_generic_instructions + self.instructions

            viewer_information = (
                "For reference, below is information about the current state of the napari viewer: \n"
                + _get_viewer_info()
            )
            system_information = (
                "For reference, below is information about the current system: \n"
                + system_info(add_python_info=False)
            )

            # Fill the system prompt template:
            system_prompt = _SUB_AGENT_SYSTEM_PROMPT.format(
                instructions=instructions,
                last_generated_code=last_generated_code,
                viewer_information=viewer_information,
                system_information=system_information,
            )

            # Create the submit tool (fresh per invocation — counter resets):
            submit_tool = _WidgetCodeSubmitTool(
                to_napari_queue=self.to_napari_queue,
                from_napari_queue=self.from_napari_queue,
                code_prefix=self.code_prefix,
                max_attempts=3,
            )

            # Create the sub-agent:
            toolset = ToolSet([submit_tool])
            sub_agent = Agent(
                api=self.llm._api,
                model_name=self.llm.model_name,
                temperature=self.llm.temperature,
                toolset=toolset,
            )
            sub_agent.append_system_message(system_prompt)

            # Run the sub-agent with the user's query:
            try:
                sub_agent(query)
            except Exception as e:
                traceback.print_exc()
                return (
                    f"Error: {type(e).__name__} with message: '{e}' "
                    f"occurred while trying to create the requested widget."
                )

            # Check if the sub-agent succeeded:
            if submit_tool.last_successful_code is not None:
                code = submit_tool.last_successful_code
                function_name = submit_tool.last_function_name

                # Update last generated code for future reference:
                self.last_generated_code = code

                # Notify activity callback:
                self.callbacks.on_tool_activity(self, "coding", code=code)

                # Standalone code with the add_dock_widget call:
                standalone_code = (
                    f"{code}\n\n"
                    f"viewer.window.add_dock_widget({function_name}, name='{function_name}')"
                )

                # Add to notebook:
                if self.notebook:
                    self.notebook.add_code_cell(standalone_code)

                # Add to MicroPlugin snippet editor:
                from napari_chatgpt.microplugin.microplugin_window import (
                    MicroPluginMainWindow,
                )

                MicroPluginMainWindow.add_snippet(
                    filename=function_name, code=standalone_code
                )

                message = "The requested widget has been successfully created and registered to the viewer."
                with asection("Result:"):
                    aprint(message)
                return message
            else:
                message = (
                    "Could not create the requested widget after multiple attempts. "
                    "Please try rephrasing the request or simplifying the widget."
                )
                with asection("Result:"):
                    aprint(message)
                return message
