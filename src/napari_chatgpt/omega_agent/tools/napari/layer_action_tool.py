"""Tool for creating napari layer context menu actions."""

import re
import traceback

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.strings.find_function_name import find_function_name
from napari_chatgpt.utils.strings.trailing_code import remove_trailing_code

_napari_layer_action_prompt = """
**Context**
You write simple, parameterless image processing functions that operate on
the currently selected napari layer.  These functions will be registered as
right-click context-menu actions and (optionally) keyboard shortcuts.

**Instructions:**
{instructions}

{last_generated_code}

**Viewer Information:**
{viewer_information}

**System Information:**
{system_information}

**Request:**
{input}

**Answer in markdown:**
"""

_instructions = r"""

## Preamble
Write **one** layer-action function.  The caller handles registering it into
napari menus and keybindings.

---

## Metadata Comments (REQUIRED)

At the **very top** of the code, before any imports, emit
metadata as single-line comments. Example:

```
# ACTION_TITLE: Invert Image
# ACTION_CATEGORY: filter
# ACTION_LAYER_TYPE: image
# ACTION_KEYBINDING: Ctrl+Shift+I
```

Each comment must be on **one line** (do not split across lines).

- **ACTION_TITLE** (required): short menu label.
- **ACTION_CATEGORY** (required): one of `filter`, `segment`,
  `transform`, `measure`, `visualize`, `annotate`, `project`,
  `classify`, `register`, `track`, `data`.
- **ACTION_LAYER_TYPE** (required): one of `image`, `labels`,
  `points`, `shapes`, `any`.
- **ACTION_KEYBINDING** (optional): e.g. `Ctrl+Shift+I`.
  Omit this line entirely if no keybinding was requested.

---

## Function Signature

```python
def action_name(ll: LayerList):
```

- `ll` is a `napari.components.LayerList`.
  napari injects it automatically via the type hint.
- You **must** include the `: LayerList` type hint.
- The function must take **no other parameters**.

---

## Accessing the Layer

```python
layer = ll.selection.active
if layer is None:
    return
```

Always guard against `None`.  If you need a specific layer type, check with
`isinstance(layer, Image)` (or `Labels`, `Points`, etc.) and return early
if the type does not match.

---

## Producing Results

- **New layer**: build a napari `Layer` (or use `Layer.create`) and insert it:
  ```python
  from napari.layers import Layer
  new = Layer.create(result_data, {"name": f"{layer.name} inverted"}, "image")
  ll.insert(ll.index(layer) + 1, new)
  ```
- **In-place update**: simply assign `layer.data = new_data`.
- Prefer returning data or using `Layer.create()` / `layer.data =` rather than calling `viewer.add_*()` directly.
- **Never** call `viewer.window.add_dock_widget()` or `napari.run()`.

---

## General Rules

- Emit **only code** (plus the metadata comments). No extra prose or examples.
- All imports must be **inside** the function body (except layer-type imports
  needed for isinstance checks, which may be at module level).
- Avoid side-effects (prints, file I/O, logging) unless explicitly asked.
- Keep label data integer — cast with `arr.astype(np.uint32, copy=False)`.
- The function should work on 2D and 3D data (and ideally nD) unless
  the request specifies otherwise.

"""

_code_prefix = """
import numpy as np
from napari.components import LayerList
from napari.layers import (
    Image, Labels, Points, Shapes,
    Surface, Tracks, Vectors, Layer,
)
"""

_code_lines_to_filter_out = [
    "viewer = napari.Viewer(",
    "viewer = Viewer(",
    "viewer.window.add_dock_widget(",
    "napari.run(",
    "gui_qt(",
]

# Module-level state for the Omega submenu and action counter:
_omega_submenu_registered = False
_action_counter = 0

# Regex for extracting metadata from ACTION_* comments:
_METADATA_RE = re.compile(r"^#\s*ACTION_(\w+)\s*:\s*(.+)$", re.MULTILINE)


def _parse_action_metadata(code: str) -> dict:
    """Extract ACTION_* metadata comments from generated code.

    Returns a dict with keys: title, category, layer_type, keybinding.
    Missing optional keys get default values.
    """
    meta = {}
    for match in _METADATA_RE.finditer(code):
        key = match.group(1).lower()
        value = match.group(2).strip()
        meta[key] = value

    return {
        "title": meta.get("title", "Omega Action"),
        "category": meta.get("category", "filter").lower(),
        "layer_type": meta.get("layer_type", "any").lower(),
        "keybinding": meta.get("keybinding"),
    }


def _strip_metadata_comments(code: str) -> str:
    """Remove ACTION_* metadata comment lines from code."""
    return _METADATA_RE.sub("", code)


class NapariLayerActionTool(BaseNapariTool):
    """
    A tool for creating napari layer actions (context menu and keybindings)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "NapariLayerActionTool"
        self.description = (
            "Use this tool to create a layer action — a one-click operation "
            "that appears in the napari layer list right-click context menu "
            "and the Layers menu bar. "
            "Layer actions operate on the currently selected layer without "
            "additional parameters. "
            "Examples: 'invert the image', 'normalize to 0-1', "
            "'binarize with Otsu threshold', 'compute edge map', "
            "'auto-contrast stretch'. "
            "Optionally, a keyboard shortcut can be bound to the action. "
            "Input must be a plain text description of the desired action. "
            "The input must not assume knowledge of our conversation. "
            "Do NOT use this tool for operations that need user-adjustable "
            "parameters — use the widget maker tool instead. "
            "Do NOT include code in the input."
        )

        self.code_prefix = _code_prefix
        self.prompt = _napari_layer_action_prompt
        self.instructions = _instructions
        self.save_last_generated_code = False
        self.return_direct = True

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        global _action_counter

        try:
            with asection("NapariLayerActionTool:"):
                with asection("Query:"):
                    aprint(query)
                aprint(f"Resulting in code of length: {len(code)}")

                # Prepare code:
                code = super()._prepare_code(code)

                # Parse metadata before stripping:
                metadata = _parse_action_metadata(code)
                title = metadata["title"]
                category = metadata["category"]
                layer_type = metadata["layer_type"]
                keybinding = metadata["keybinding"]

                with asection("Parsed metadata:"):
                    aprint(f"Title: {title}")
                    aprint(f"Category: {category}")
                    aprint(f"Layer type: {layer_type}")
                    aprint(f"Keybinding: {keybinding}")

                # Strip metadata comments from the code:
                clean_code = _strip_metadata_comments(code)

                # Remove any viewer forbidden code:
                clean_code = filter_lines(
                    clean_code, _code_lines_to_filter_out
                )

                # Remove trailing code:
                clean_code = remove_trailing_code(clean_code)

                # Find the function name:
                function_name = find_function_name(clean_code)

                if not function_name:
                    return "Could not find a function in the generated code."

                aprint(f"Function name: {function_name}")

                # Load the code as a module:
                loaded_module = dynamic_import(clean_code)

                # Get the function:
                function = getattr(loaded_module, function_name)

                # Register with napari's app-model:
                _action_counter += 1
                action_id = (
                    f"napari-chatgpt.action."
                    f"{function_name}_{_action_counter}"
                )

                self._register_action(
                    action_id=action_id,
                    title=title,
                    category=category,
                    layer_type=layer_type,
                    keybinding=keybinding,
                    callback=function,
                )

                # Call the activity callback:
                self.callbacks.on_tool_activity(self, "coding", code=code)

                # Build standalone code for notebook/snippets:
                standalone_code = (
                    f"{code}\n\n"
                    f"# Registration code:\n"
                    f"# This action was registered as '{title}' "
                    f"in the layer list context menu.\n"
                )
                if keybinding:
                    standalone_code += f"# Keybinding: {keybinding}\n"

                # Add to notebook:
                if self.notebook:
                    self.notebook.add_code_cell(standalone_code)

                # Add to code snippet editor:
                from napari_chatgpt.microplugin.microplugin_window import (
                    MicroPluginMainWindow,
                )

                MicroPluginMainWindow.add_snippet(
                    filename=function_name, code=standalone_code
                )

                # Build success message:
                message = (
                    f"The layer action '{title}' has been successfully "
                    f"created and registered. It is now available in the "
                    f"layer list right-click context menu under 'Omega' "
                    f"and in the Layers > "
                    f"{category.title()} menu."
                )
                if keybinding:
                    message += f" Keyboard shortcut: {keybinding}."

                with asection("Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return (
                f"Error: {type(e).__name__} with message: '{e}' "
                f"occurred while trying to create the layer action."
            )

    @staticmethod
    def _register_action(
        action_id: str,
        title: str,
        category: str,
        layer_type: str,
        keybinding: str | None,
        callback,
    ):
        """Register a function as a napari app-model Action."""
        from app_model.types import Action, SubmenuItem
        from napari._app_model._app import get_app_model
        from napari._app_model.constants import MenuId
        from napari._app_model.context import (
            LayerListSelectionContextKeys as LLSCK,
        )

        global _omega_submenu_registered

        app = get_app_model()

        # Category -> MenuId mapping:
        category_menu_map = {
            "filter": MenuId.LAYERS_FILTER,
            "segment": MenuId.LAYERS_SEGMENT,
            "transform": MenuId.LAYERS_TRANSFORM,
            "measure": MenuId.LAYERS_MEASURE,
            "visualize": MenuId.LAYERS_VISUALIZE,
            "annotate": MenuId.LAYERS_ANNOTATE,
            "project": MenuId.LAYERS_PROJECT,
            "classify": MenuId.LAYERS_CLASSIFY,
            "register": MenuId.LAYERS_REGISTER,
            "track": MenuId.LAYERS_TRACK,
            "data": MenuId.LAYERS_DATA,
        }

        # Layer type -> enablement expression:
        enablement_map = {
            "image": LLSCK.active_layer_type == "image",
            "labels": LLSCK.active_layer_type == "labels",
            "points": LLSCK.active_layer_type == "points",
            "shapes": LLSCK.active_layer_type == "shapes",
            "any": LLSCK.num_selected_layers >= 1,
        }

        # Register the Omega submenu in the context menu (once):
        omega_submenu_id = "napari-chatgpt/omega_actions"
        if not _omega_submenu_registered:
            app.menus.append_menu_items(
                [
                    (
                        MenuId.LAYERLIST_CONTEXT,
                        SubmenuItem(
                            submenu=omega_submenu_id,
                            title="Omega",
                            group="6_omega",
                        ),
                    )
                ]
            )
            _omega_submenu_registered = True

        # Build menu rules:
        menus = [{"id": omega_submenu_id}]
        category_menu = category_menu_map.get(category)
        if category_menu:
            menus.append({"id": category_menu})

        # Build enablement:
        enablement = enablement_map.get(layer_type, enablement_map["any"])

        # Build keybindings:
        keybindings = []
        if keybinding:
            keybindings.append({"primary": keybinding})

        # Create and register the action:
        action = Action(
            id=action_id,
            title=title,
            callback=callback,
            enablement=enablement,
            menus=menus,
            keybindings=keybindings or None,
        )

        app.register_actions([action])

        menu_ids = [m["id"] for m in menus]
        aprint(
            f"Registered action '{title}' "
            f"(id={action_id}) in menus: {menu_ids}"
        )
