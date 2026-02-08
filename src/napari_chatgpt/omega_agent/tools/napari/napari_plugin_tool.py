"""Tool for discovering and executing installed napari plugin functions."""

import inspect
import logging
import re
import traceback

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool

log = logging.getLogger(__name__)

_PLUGIN_CATALOG_PLACEHOLDER = "[PLUGIN_CATALOG]"

_napari_plugin_prompt = """
**Context**
You write Python code that uses installed napari plugins for image
processing and analysis.
The viewer instance is accessible as `viewer`.

**Available Plugins:**
[PLUGIN_CATALOG]

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

**Instructions for using napari plugins:**
- Import functions using the exact python_name shown in the catalog
  (e.g. `from my_plugin.module import my_function`).
- For function-based widgets, call directly with appropriate parameters.
- Add results to the viewer using `viewer.add_image()`,
  `viewer.add_labels()`, etc.
- Match parameter types to the signature shown in the catalog.
- For readers, use the file patterns shown to determine compatibility.
- For writers, use the extensions and layer types shown.
"""

# Keywords that trigger info mode instead of execution mode:
_INFO_KEYWORDS = re.compile(
    r"\b(list|what|available|show|which\s+plugin|discover|catalog)\b",
    re.IGNORECASE,
)


class PluginCatalog:
    """Scans npe2 plugin manifests and builds a catalog of available
    plugin contributions (widgets, readers, writers)."""

    def __init__(self):
        self.widgets: list[dict] = []
        self.readers: list[dict] = []
        self.writers: list[dict] = []
        self.error_log: list[str] = []
        self._plugin_names: set[str] = set()
        self._build_catalog()

    # ------------------------------------------------------------------
    # Catalog building
    # ------------------------------------------------------------------
    def _build_catalog(self):
        try:
            from npe2 import PluginManager
        except ImportError:
            self.error_log.append("npe2 is not installed; cannot discover plugins.")
            return

        try:
            pm = PluginManager.instance()
            pm.discover()
        except Exception as exc:
            self.error_log.append(f"Failed to get PluginManager instance: {exc}")
            return

        for manifest in pm.iter_manifests(disabled=False):
            plugin_name = manifest.name
            # Skip ourselves:
            if plugin_name == "napari-chatgpt":
                continue

            # Build command-id -> python_name lookup:
            cmd_map = {}
            for cmd in manifest.contributions.commands or []:
                pn = getattr(cmd, "python_name", None)
                if pn:
                    cmd_map[cmd.id] = pn

            has_contributions = False

            # --- Widgets ---
            for contrib in manifest.contributions.widgets or []:
                has_contributions = True
                try:
                    self._process_widget(plugin_name, contrib, cmd_map)
                except Exception as exc:
                    msg = (
                        f"Error introspecting widget "
                        f"'{contrib.display_name}' from "
                        f"'{plugin_name}': {exc}"
                    )
                    self.error_log.append(msg)
                    log.debug(msg, exc_info=True)

            # --- Readers ---
            for contrib in manifest.contributions.readers or []:
                has_contributions = True
                try:
                    self._process_reader(plugin_name, contrib, cmd_map)
                except Exception as exc:
                    msg = f"Error introspecting reader from " f"'{plugin_name}': {exc}"
                    self.error_log.append(msg)
                    log.debug(msg, exc_info=True)

            # --- Writers ---
            for contrib in manifest.contributions.writers or []:
                has_contributions = True
                try:
                    self._process_writer(plugin_name, contrib, cmd_map)
                except Exception as exc:
                    msg = f"Error introspecting writer from " f"'{plugin_name}': {exc}"
                    self.error_log.append(msg)
                    log.debug(msg, exc_info=True)

            if has_contributions:
                self._plugin_names.add(plugin_name)

    def _process_widget(self, plugin_name, contrib, cmd_map):
        display_name = contrib.display_name or ""
        autogenerate = getattr(contrib, "autogenerate", False)

        # Widget contributions reference a command; resolve
        # the python_name from the command map:
        command_id = getattr(contrib, "command", None) or ""
        python_name = cmd_map.get(command_id, command_id)

        sig_str = ""
        docstring = ""

        # Try to resolve the callable for introspection:
        if python_name and ":" in python_name:
            try:
                obj = _resolve_python_name(python_name)
                if obj is not None:
                    sig_str = str(inspect.signature(obj))
                    docstring = inspect.getdoc(obj) or ""
            except Exception:
                pass

        kind = "function" if autogenerate else "class"
        self.widgets.append(
            {
                "plugin": plugin_name,
                "display_name": display_name,
                "python_name": python_name,
                "signature": sig_str,
                "docstring": docstring,
                "kind": kind,
            }
        )

    def _process_reader(self, plugin_name, contrib, cmd_map):
        command_id = getattr(contrib, "command", None) or ""
        patterns = getattr(contrib, "filename_patterns", []) or []
        python_name = cmd_map.get(command_id, command_id)
        self.readers.append(
            {
                "plugin": plugin_name,
                "command": command_id,
                "python_name": python_name,
                "filename_patterns": patterns,
            }
        )

    def _process_writer(self, plugin_name, contrib, cmd_map):
        command_id = getattr(contrib, "command", None) or ""
        extensions = getattr(contrib, "filename_extensions", []) or []
        layer_types = getattr(contrib, "layer_types", []) or []
        python_name = cmd_map.get(command_id, command_id)
        self.writers.append(
            {
                "plugin": plugin_name,
                "command": command_id,
                "python_name": python_name,
                "filename_extensions": extensions,
                "layer_types": layer_types,
            }
        )

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------
    def format_for_prompt(self, max_items: int = 30) -> str:
        """Concise format suitable for embedding in a sub-LLM prompt."""
        if self.is_empty():
            return "(no plugins detected)"

        lines: list[str] = []
        count = 0

        for w in self.widgets:
            if count >= max_items:
                break
            sig = w["signature"] or "(…)"
            doc = _truncate(w["docstring"], 200)
            lines.append(
                f"- [{w['plugin']}] widget: "
                f"{w['python_name']}{sig}  "
                f"# {w['kind']}; {doc}"
            )
            count += 1

        for r in self.readers:
            if count >= max_items:
                break
            patterns = _truncate_list(r["filename_patterns"], 10)
            lines.append(
                f"- [{r['plugin']}] reader: "
                f"{r['python_name']}  "
                f"patterns={patterns}"
            )
            count += 1

        for wr in self.writers:
            if count >= max_items:
                break
            exts = _truncate_list(wr["filename_extensions"], 10)
            ltypes = ", ".join(wr["layer_types"])
            lines.append(
                f"- [{wr['plugin']}] writer: "
                f"{wr['python_name']}  "
                f"extensions={exts}  "
                f"layer_types={ltypes}"
            )
            count += 1

        total = self._total_items()
        if count < total:
            lines.append(f"... and {total - count} more " f"(total {total})")

        return "\n".join(lines)

    def format_for_info_query(self) -> str:
        """Detailed format returned to the main agent for info queries."""
        if self.is_empty():
            msg = "No napari plugins detected."
            if self.error_log:
                msg += "\nErrors during scanning:\n" + "\n".join(self.error_log)
            return msg

        sections: list[str] = []
        sections.append(
            f"Found {self.get_plugin_count()} plugin(s) with "
            f"{len(self.widgets)} widget(s), "
            f"{len(self.readers)} reader(s), "
            f"{len(self.writers)} writer(s).\n"
        )

        if self.widgets:
            sections.append("## Widgets")
            for w in self.widgets:
                sig = w["signature"] or "(…)"
                doc = w["docstring"] or "(no docstring)"
                sections.append(
                    f"- **{w['display_name']}** [{w['plugin']}]\n"
                    f"  import: `{w['python_name']}`\n"
                    f"  type: {w['kind']}\n"
                    f"  signature: `{sig}`\n"
                    f"  docstring: {doc}\n"
                )

        if self.readers:
            sections.append("## Readers")
            for r in self.readers:
                patterns = ", ".join(r["filename_patterns"])
                sections.append(
                    f"- [{r['plugin']}] patterns: {patterns}\n"
                    f"  import: `{r['python_name']}`\n"
                )

        if self.writers:
            sections.append("## Writers")
            for wr in self.writers:
                exts = ", ".join(wr["filename_extensions"])
                ltypes = ", ".join(wr["layer_types"])
                sections.append(
                    f"- [{wr['plugin']}] extensions: {exts}  "
                    f"layer_types: {ltypes}\n"
                    f"  import: `{wr['python_name']}`\n"
                )

        if self.error_log:
            sections.append("## Warnings")
            for err in self.error_log:
                sections.append(f"- {err}")

        return "\n".join(sections)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def is_empty(self) -> bool:
        return not (self.widgets or self.readers or self.writers)

    def get_plugin_count(self) -> int:
        return len(self._plugin_names)

    def _total_items(self) -> int:
        return len(self.widgets) + len(self.readers) + len(self.writers)


class NapariPluginTool(BaseNapariTool):
    """Tool that discovers and executes installed napari plugin functions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "NapariPluginTool"

        # Build the catalog once at init:
        with asection("Building napari plugin catalog"):
            self.catalog = PluginCatalog()

        if self.catalog.is_empty():
            self.description = (
                "Use this tool to check for installed napari plugins. "
                "Currently no third-party plugins are detected."
            )
            self.prompt = None
        else:
            n_plugins = self.catalog.get_plugin_count()
            n_w = len(self.catalog.widgets)
            n_r = len(self.catalog.readers)
            n_wr = len(self.catalog.writers)
            self.description = (
                "Use this tool to work with installed napari plugins "
                "or to get information about available plugins. "
                f"Currently {n_plugins} plugin(s) available with "
                f"{n_w} widget(s), {n_r} reader(s), "
                f"and {n_wr} writer(s). "
                "Input can be: (1) a request like 'list available "
                "plugins' to get catalog info, or (2) a description "
                "of what to do, e.g. 'denoise this image using "
                "plugin X'."
            )
            # Bake the catalog into the prompt template.
            # Escape { and } so format_map() in the LLM
            # layer doesn't treat them as template variables:
            catalog_text = self.catalog.format_for_prompt()
            catalog_text = catalog_text.replace("{", "{{").replace("}", "}}")
            self.prompt = _napari_plugin_prompt.replace(
                _PLUGIN_CATALOG_PLACEHOLDER, catalog_text
            )

        self.instructions = _instructions
        self.save_last_generated_code = False

    # ------------------------------------------------------------------
    # Dual-mode dispatch
    # ------------------------------------------------------------------
    def run_omega_tool(self, query: str = "") -> str:
        # Info mode: return catalog directly, no sub-LLM or Qt round-trip:
        if _INFO_KEYWORDS.search(query):
            with asection("NapariPluginTool: info mode"):
                aprint(f"Query: {query}")
                return self.catalog.format_for_info_query()

        # Execution mode: delegate to BaseNapariTool (sub-LLM + Qt):
        if self.prompt is None:
            return (
                "No napari plugins are currently detected. "
                "Install plugins with pip and restart napari."
            )

        return super().run_omega_tool(query)

    # ------------------------------------------------------------------
    # Code execution (runs on Qt thread via napari bridge)
    # ------------------------------------------------------------------
    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:
        try:
            with asection("NapariPluginTool:"):
                with asection("Request:"):
                    aprint(request)
                aprint(f"Resulting in code of length: {len(code)}")

                # Prepare code:
                code = super()._prepare_code(code)

                captured_output = self._execute_code(code, viewer=viewer)

                if len(captured_output) > 0:
                    message = (
                        f"Plugin tool completed task successfully: "
                        f"{captured_output}"
                    )
                else:
                    message = "Plugin tool completed task successfully"

                with asection("Message:"):
                    aprint(message)

                return message

        except ImportError as e:
            traceback.print_exc()
            return (
                f"Error: ImportError '{e}'. "
                f"The plugin may not be installed correctly. "
                f"Try: pip install <plugin-package-name>"
            )
        except TypeError as e:
            traceback.print_exc()
            return (
                f"Error: TypeError '{e}'. "
                f"Check that the function arguments match the "
                f"signature shown in the plugin catalog."
            )
        except Exception as e:
            traceback.print_exc()
            return (
                f"Error: {type(e).__name__} with message: '{e}' "
                f"occurred while fulfilling request."
            )


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _resolve_python_name(python_name: str):
    """Import and return the object pointed to by a dotted python name
    like 'package.module:callable'."""
    if not python_name:
        return None
    # npe2 uses 'module.path:attribute' format:
    if ":" in python_name:
        module_path, attr_name = python_name.rsplit(":", 1)
    else:
        # Fallback: last component is the attribute:
        parts = python_name.rsplit(".", 1)
        if len(parts) < 2:
            return None
        module_path, attr_name = parts

    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, attr_name, None)


def _truncate_list(items: list, max_show: int) -> str:
    """Join list items, showing at most max_show with a count of omitted."""
    if not items:
        return ""
    if len(items) <= max_show:
        return ", ".join(items)
    shown = ", ".join(items[:max_show])
    return f"{shown}, ... ({len(items)} total)"


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
