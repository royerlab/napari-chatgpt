#!/usr/bin/env python
"""Generate screenshots of napari-chatgpt widgets for the wiki.

Usage:
    python scripts/generate_wiki_screenshots.py [--output-dir DIR]

Outputs PNGs to the wiki images/ directory (default: ../napari-chatgpt.wiki/images/).
Requires a display (real or virtual via Xvfb).
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from qtpy.QtWidgets import QApplication


def _ensure_app():
    """Return existing QApplication or create one."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def _grab_widget(widget, width, height, filepath):
    """Resize widget, process events, grab screenshot, save to file."""
    widget.resize(width, height)
    widget.show()
    QApplication.processEvents()
    QApplication.processEvents()  # double-pump to ensure full render
    pixmap = widget.grab()
    pixmap.save(str(filepath))
    print(f"  Saved: {filepath}")
    widget.close()


def generate_omega_settings(output_dir: Path):
    """Capture the OmegaQWidget settings panel."""
    import napari

    viewer = napari.Viewer(show=False)
    try:
        from napari_chatgpt._widget import OmegaQWidget

        widget = OmegaQWidget(viewer, add_code_editor=False)
        _grab_widget(widget, 340, 520, output_dir / "omega_settings_widget.png")
    finally:
        viewer.close()


def generate_api_key_dialog_new(output_dir: Path, provider: str):
    """Capture first-time API Key dialog for a given provider."""
    from napari_chatgpt.llm.api_keys.api_key_vault import KeyVault

    with patch.object(KeyVault, "is_key_present", return_value=False):
        from napari_chatgpt.llm.api_keys.api_key_vault_dialog import APIKeyDialog

        dialog = APIKeyDialog(api_key_name=provider)
        fname = f"api_key_dialog_{provider.lower()}_new.png"
        _grab_widget(dialog, 400, 220, output_dir / fname)


def generate_api_key_dialog_returning(output_dir: Path):
    """Capture returning-user API Key dialog (OpenAI, with key present)."""
    from napari_chatgpt.llm.api_keys.api_key_vault import KeyVault

    with patch.object(KeyVault, "is_key_present", return_value=True):
        from napari_chatgpt.llm.api_keys.api_key_vault_dialog import APIKeyDialog

        dialog = APIKeyDialog(api_key_name="OpenAI")
        _grab_widget(
            dialog, 400, 250, output_dir / "api_key_dialog_openai_returning.png"
        )


def generate_microplugin_editor(output_dir: Path):
    """Capture the MicroPlugin code editor window."""
    import napari

    from napari_chatgpt.microplugin.microplugin_window import MicroPluginMainWindow

    viewer = napari.Viewer(show=False)
    try:
        # Disable singleton so we can create a fresh instance:
        MicroPluginMainWindow._singleton_pattern_active = False
        with tempfile.TemporaryDirectory() as tmpdir:
            editor = MicroPluginMainWindow(
                napari_viewer=viewer, folder_path=tmpdir
            )
            _grab_widget(editor, 900, 550, output_dir / "microplugin_editor.png")
    finally:
        MicroPluginMainWindow._singleton_pattern_active = True
        viewer.close()


def main():
    parser = argparse.ArgumentParser(description="Generate wiki screenshots")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent
        / "napari-chatgpt.wiki"
        / "images",
        help="Directory to write screenshots (default: ../napari-chatgpt.wiki/images/)",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    app = _ensure_app()

    print("Generating Omega settings widget screenshot...")
    generate_omega_settings(output_dir)

    for provider in ("OpenAI", "Anthropic", "Gemini"):
        print(f"Generating {provider} first-time API key dialog screenshot...")
        generate_api_key_dialog_new(output_dir, provider)

    print("Generating OpenAI returning-user API key dialog screenshot...")
    generate_api_key_dialog_returning(output_dir)

    print("Generating MicroPlugin editor screenshot...")
    generate_microplugin_editor(output_dir)

    print("Done! All screenshots generated.")


if __name__ == "__main__":
    main()
