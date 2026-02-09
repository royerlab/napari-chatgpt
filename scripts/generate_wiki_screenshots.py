#!/usr/bin/env python
from __future__ import annotations

"""Generate screenshots of napari-chatgpt (Omega) for wiki and social media.

Captures:
  - Omega settings widget panel
  - API key dialogs (new & returning user)
  - MicroPlugin code editor
  - Full napari viewer with Omega widget and sample data
  - Chat UI mockup (dark theme, requires playwright CLI)
  - Feature highlight text cards (requires Pillow)

Usage:
    python scripts/generate_wiki_screenshots.py [--output-dir DIR]
    make update-screenshots

Requires a display (real or virtual via Xvfb) and napari-chatgpt installed.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_app():
    """Return existing QApplication or create one."""
    from qtpy.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def _process_events(seconds: float = 0.5):
    """Process Qt events for *seconds* to let the UI render."""
    from qtpy.QtWidgets import QApplication

    app = QApplication.instance()
    end = time.time() + seconds
    while time.time() < end:
        app.processEvents()
        time.sleep(0.05)


def _grab_widget(widget, width, height, filepath):
    """Resize widget, process events, grab screenshot, save to file."""
    widget.resize(width, height)
    widget.show()
    _process_events(0.5)
    pixmap = widget.grab()
    pixmap.save(str(filepath))
    print(f"  Saved: {filepath.name} ({pixmap.width()}x{pixmap.height()})")
    widget.close()


# ---------------------------------------------------------------------------
# Basic widget screenshots
# ---------------------------------------------------------------------------


def generate_omega_settings(output_dir: Path):
    """Capture the OmegaQWidget settings panel."""
    import napari

    viewer = napari.Viewer(show=False)
    try:
        from napari_chatgpt._widget import OmegaQWidget

        widget = OmegaQWidget(viewer, add_code_editor=False)
        _grab_widget(widget, 340, 600, output_dir / "omega_settings_widget.png")
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

    # Use the real microplugins folder so the file list is populated
    microplugins_dir = Path.home() / "microplugins"
    if not microplugins_dir.exists():
        microplugins_dir = None  # fall back to MicroPlugin default

    viewer = napari.Viewer(show=False)
    try:
        MicroPluginMainWindow._singleton_pattern_active = False
        kwargs = {"napari_viewer": viewer}
        if microplugins_dir:
            kwargs["folder_path"] = str(microplugins_dir)
        editor = MicroPluginMainWindow(**kwargs)
        _grab_widget(editor, 900, 550, output_dir / "microplugin_editor.png")
    finally:
        MicroPluginMainWindow._singleton_pattern_active = True
        viewer.close()


# ---------------------------------------------------------------------------
# Full viewer screenshot
# ---------------------------------------------------------------------------


def generate_viewer_with_omega(output_dir: Path):
    """Capture napari viewer with Omega widget docked and sample data loaded."""
    import napari

    viewer = napari.Viewer(show=True)
    try:
        window = viewer.window._qt_window
        window.resize(1400, 900)
        _process_events(1.0)

        # Load sample data
        try:
            from napari_chatgpt._sample_data import make_sample_data

            layers = make_sample_data()
            for layer_data, meta, layer_type in layers:
                viewer.add_image(layer_data, name=meta.get("name", "Sample"))
        except Exception as e:
            print(f"  Warning: sample data failed ({e}), using random image")
            import numpy as np

            viewer.add_image(
                np.random.randint(0, 255, (512, 512), dtype=np.uint8),
                name="Sample",
            )

        _process_events(0.5)

        # Add Omega widget
        from napari_chatgpt._widget import OmegaQWidget

        widget = OmegaQWidget(viewer, add_code_editor=False)
        viewer.window.add_dock_widget(widget, area="right", name="Omega")
        _process_events(2.0)

        # Grab the full viewer window
        from qtpy.QtWidgets import QApplication

        screen = QApplication.instance().primaryScreen()
        pixmap = screen.grabWindow(window.winId())
        path = output_dir / "omega_napari_viewer.png"
        pixmap.save(str(path))
        print(f"  Saved: {path.name} ({pixmap.width()}x{pixmap.height()})")

        # Grab the widget alone at a nice size for a closeup
        widget_pixmap = widget.grab()
        path2 = output_dir / "omega_widget_closeup.png"
        widget_pixmap.save(str(path2))
        print(
            f"  Saved: {path2.name} "
            f"({widget_pixmap.width()}x{widget_pixmap.height()})"
        )
    finally:
        viewer.close()
        _process_events(0.5)


# ---------------------------------------------------------------------------
# Chat UI mockup (via Playwright)
# ---------------------------------------------------------------------------

_CHAT_MOCKUP_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0d1017; color: #e2e8f0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 14px; line-height: 1.6;
  }
  .container { max-width: 800px; margin: 0 auto; padding: 16px; }
  .header {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; margin-bottom: 16px;
    background: #161b22; border-radius: 12px;
    border: 1px solid #30363d;
  }
  .header .logo {
    width: 44px; height: 44px; border-radius: 10px;
    background: linear-gradient(135deg, #1a73e8, #00bcd4);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: bold; color: white;
  }
  .header .title { font-size: 18px; font-weight: 600; }
  .header .subtitle { font-size: 12px; color: #8b949e; }
  .messages { display: flex; flex-direction: column; gap: 12px; }
  .msg {
    padding: 12px 16px; border-radius: 12px;
    max-width: 85%; animation: msg-in 0.3s ease-out;
  }
  @keyframes msg-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .msg.client {
    background: #1a2f4d; border: 1px solid #1e4976;
    align-self: flex-end; border-bottom-right-radius: 4px;
  }
  .msg.server {
    background: #1e2130; border: 1px solid #2d3154;
    align-self: flex-start; border-bottom-left-radius: 4px;
  }
  .msg.action {
    background: #162033; border: 1px solid #1e3a5f;
    align-self: flex-start; font-size: 13px;
    border-left: 3px solid #00bcd4;
  }
  .msg .label {
    font-size: 11px; font-weight: 600; margin-bottom: 4px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .msg.client .label { color: #60a5fa; }
  .msg.server .label { color: #818cf8; }
  .msg.action .label { color: #00bcd4; }
  code {
    background: #0d1117; padding: 2px 6px; border-radius: 4px;
    font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 13px;
  }
  pre {
    background: #0d1117; padding: 12px; border-radius: 8px;
    margin: 8px 0; overflow-x: auto; border: 1px solid #21262d;
  }
  pre code { padding: 0; background: none; }
  .code-kw { color: #ff7b72; }
  .code-fn { color: #d2a8ff; }
  .code-str { color: #a5d6ff; }
  .code-cmt { color: #8b949e; }
  .code-num { color: #79c0ff; }
  .tool-details {
    margin: 8px 0; border: 1px solid #21262d; border-radius: 8px;
    overflow: hidden;
  }
  .tool-summary {
    padding: 8px 12px; background: #161b22; cursor: pointer;
    font-size: 12px; color: #8b949e;
  }
  .tool-content { padding: 8px 12px; font-size: 12px; color: #8b949e; }
  .input-area {
    margin-top: 16px; display: flex; gap: 8px;
    padding: 12px; background: #161b22; border-radius: 12px;
    border: 1px solid #30363d;
  }
  .input-area textarea {
    flex: 1; background: #0d1017; color: #e2e8f0;
    border: 1px solid #30363d; border-radius: 8px;
    padding: 10px 14px; font-size: 14px; resize: none;
    font-family: inherit; outline: none;
  }
  .input-area button {
    background: #1a73e8; color: white; border: none;
    border-radius: 8px; padding: 10px 20px; font-weight: 600;
    cursor: pointer;
  }
  .token-count {
    text-align: right; font-size: 11px; color: #484f58;
    margin-top: 4px;
  }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">&Omega;</div>
    <div>
      <div class="title">Omega</div>
      <div class="subtitle">LLM-powered agent for napari</div>
    </div>
  </div>
  <div class="messages">
    <div class="msg client">
      <div class="label">You</div>
      Segment the nuclei in this image using cellpose and show the result
      as a labels layer.
    </div>
    <div class="msg action">
      <div class="label">Tool: Image Segmentation</div>
      <div class="tool-details">
        <div class="tool-summary">Executing cellpose segmentation...</div>
      </div>
      <pre><code><span class="code-kw">from</span> cellpose.models <span class="code-kw">import</span> CellposeModel
<span class="code-cmt"># Get the current image from the viewer</span>
image = viewer.layers[<span class="code-num">0</span>].data
<span class="code-cmt"># Run cellpose segmentation</span>
model = CellposeModel(model_type=<span class="code-str">'nuclei'</span>)
masks, _, _ = model.<span class="code-fn">eval</span>(image, diameter=<span class="code-num">30</span>)
<span class="code-cmt"># Add result as labels layer</span>
viewer.<span class="code-fn">add_labels</span>(masks, name=<span class="code-str">'Nuclei Segmentation'</span>)</code></pre>
    </div>
    <div class="msg server">
      <div class="label">Omega</div>
      Done! I segmented the nuclei using <strong>Cellpose</strong> with the
      <code>nuclei</code> model. The result has been added as a labels layer
      called <strong>"Nuclei Segmentation"</strong>. I found <strong>247 nuclei</strong>
      in the image. Would you like me to measure their properties or refine
      the segmentation?
    </div>
    <div class="msg client">
      <div class="label">You</div>
      Measure the area and circularity of each nucleus and show a histogram.
    </div>
    <div class="msg action">
      <div class="label">Tool: Python REPL</div>
      <pre><code><span class="code-kw">import</span> numpy <span class="code-kw">as</span> np
<span class="code-kw">from</span> skimage.measure <span class="code-kw">import</span> regionprops_table
<span class="code-kw">import</span> matplotlib.pyplot <span class="code-kw">as</span> plt
props = <span class="code-fn">regionprops_table</span>(masks, properties=[<span class="code-str">'area'</span>, <span class="code-str">'eccentricity'</span>])
fig, axes = plt.<span class="code-fn">subplots</span>(<span class="code-num">1</span>, <span class="code-num">2</span>, figsize=(<span class="code-num">10</span>, <span class="code-num">4</span>))
axes[<span class="code-num">0</span>].<span class="code-fn">hist</span>(props[<span class="code-str">'area'</span>], bins=<span class="code-num">30</span>, color=<span class="code-str">'#1a73e8'</span>)
axes[<span class="code-num">0</span>].<span class="code-fn">set_title</span>(<span class="code-str">'Nucleus Area Distribution'</span>)
axes[<span class="code-num">1</span>].<span class="code-fn">hist</span>(<span class="code-num">1</span> - props[<span class="code-str">'eccentricity'</span>], bins=<span class="code-num">30</span>, color=<span class="code-str">'#00bcd4'</span>)
axes[<span class="code-num">1</span>].<span class="code-fn">set_title</span>(<span class="code-str">'Circularity Distribution'</span>)
plt.<span class="code-fn">tight_layout</span>(); plt.<span class="code-fn">show</span>()</code></pre>
    </div>
    <div class="msg server">
      <div class="label">Omega</div>
      Here are the measurements for the 247 nuclei:<br><br>
      <strong>Area:</strong> mean = 342 px, median = 318 px (range: 89 &ndash; 1,204 px)<br>
      <strong>Circularity:</strong> mean = 0.82 (most nuclei are fairly round)<br><br>
      The histograms are displayed. The area distribution shows a right-skewed
      pattern typical of healthy tissue. Would you like to filter out outliers
      or export the data?
    </div>
  </div>
  <div class="input-area">
    <textarea rows="1" placeholder="Ask Omega anything..."></textarea>
    <button>Send</button>
  </div>
  <div class="token-count">Session: 1,847 tokens</div>
</div>
</body>
</html>
"""


def generate_chat_ui_mockup(output_dir: Path):
    """Generate a dark-theme chat UI screenshot using Playwright."""
    playwright_cmd = shutil.which("playwright") or shutil.which("npx")
    if not playwright_cmd:
        print("  Skipped: playwright CLI not found")
        return

    with tempfile.NamedTemporaryFile(
        suffix=".html", mode="w", delete=False
    ) as f:
        f.write(_CHAT_MOCKUP_HTML)
        html_path = f.name

    try:
        outpath = str(output_dir / "omega_chat_ui.png")
        cmd = ["playwright", "screenshot", "--full-page"]
        if "npx" in str(playwright_cmd):
            cmd = ["npx"] + cmd
        cmd += [f"file://{html_path}", outpath]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  Saved: omega_chat_ui.png")
        else:
            print(f"  Warning: playwright failed: {result.stderr[:200]}")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  Skipped: {e}")
    finally:
        os.unlink(html_path)


# ---------------------------------------------------------------------------
# Feature highlight cards (Pillow)
# ---------------------------------------------------------------------------


def _draw_text_card(
    output_path: Path,
    title: str,
    bullets: list[str],
    bg_color: tuple = (13, 16, 23),
    accent_color: tuple = (26, 115, 232),
    width: int = 800,
):
    """Generate a text-card infographic with Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  Skipped: Pillow not available")
        return

    # Try to find a good font, fall back to default
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    font_paths_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]

    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    for fp in font_paths:
        if os.path.exists(fp):
            title_font = ImageFont.truetype(fp, 36)
            break
    for fp in font_paths_regular:
        if os.path.exists(fp):
            body_font = ImageFont.truetype(fp, 22)
            break

    # Calculate height
    line_height = 38
    height = 100 + 60 + len(bullets) * line_height + 60

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Accent bar at top
    draw.rectangle([(0, 0), (width, 6)], fill=accent_color)

    # Title
    y = 40
    draw.text((40, y), title, fill=(226, 232, 240), font=title_font)
    y += 70

    # Divider
    draw.rectangle([(40, y), (width - 40, y + 2)], fill=(48, 54, 61))
    y += 20

    # Bullets
    for bullet in bullets:
        draw.text(
            (50, y), f"\u2022  {bullet}", fill=(139, 148, 158), font=body_font
        )
        y += line_height

    img.save(str(output_path))
    print(f"  Saved: {output_path.name} ({width}x{height})")


def generate_feature_cards(output_dir: Path):
    """Generate feature-highlight text cards."""
    _draw_text_card(
        output_dir / "card_bug_fixes.png",
        "30+ Bug Fixes & Security Hardening",
        [
            "Qt thread safety: fixed segfault in pip install dialog",
            "Windows: fixed UnicodeEncodeError on emoji output",
            "macOS: fixed server thread hang on shutdown",
            "Shell injection prevention in pip/conda utils",
            "Infinite loop guard in web search",
            "Thread-safe viewer state with locking",
            "Execution timeout to prevent deadlocks",
        ],
        accent_color=(220, 38, 38),
    )

    _draw_text_card(
        output_dir / "card_multi_provider.png",
        "Multi-Provider LLM Support",
        [
            "OpenAI: GPT-5.2, GPT-5.1, GPT-4o, and more",
            "Anthropic: Claude Opus 4.6, Sonnet 4.5, Haiku",
            "Google: Gemini 3, Gemini 2.5 Pro/Flash",
            "Separate model selection for chat & coding",
            "Intelligent tiered model ranking",
            "Powered by the LiteMind library",
        ],
        accent_color=(26, 115, 232),
    )

    _draw_text_card(
        output_dir / "card_new_tools.png",
        "New Tools & Capabilities",
        [
            "NapariPluginTool: discover & use any napari plugin",
            "Layer Actions: create context menu items & shortcuts",
            "FileDownload: download files from URLs",
            "PipInstall: install packages with user permission",
            "Web Search: built-in DuckDuckGo & Wikipedia",
            "Sample Data: test Omega from the File menu",
        ],
        accent_color=(0, 188, 212),
    )


# ---------------------------------------------------------------------------
# Screen recording (ffmpeg + xdotool)
# ---------------------------------------------------------------------------


def _get_window_geometry_by_id(wid: int) -> tuple | None:
    """Get (x, y, width, height) for a known X11 window ID."""
    xdotool = shutil.which("xdotool")
    if not xdotool:
        return None
    try:
        geo = subprocess.run(
            ["xdotool", "getwindowgeometry", "--shell", str(wid)],
            capture_output=True, text=True, timeout=5,
        )
        if geo.returncode != 0:
            return None
        vals = {}
        for line in geo.stdout.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                vals[k] = int(v)
        return (vals.get("X", 0), vals.get("Y", 0),
                vals.get("WIDTH", 800), vals.get("HEIGHT", 600))
    except (subprocess.TimeoutExpired, ValueError, KeyError):
        return None


def record_window(
    output_path: Path,
    window_id: int,
    duration: int = 15,
    fps: int = 15,
    display: str = "",
):
    """Record a specific window to MP4 using ffmpeg x11grab.

    Args:
        output_path: Path for the output .mp4 file.
        window_id: X11 window ID (e.g. from QWidget.winId()).
        duration: Recording duration in seconds.
        fps: Frames per second.
        display: X11 display (default: from $DISPLAY env var).
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("  Skipped: ffmpeg not found")
        return False

    if not display:
        display = os.environ.get("DISPLAY", ":0")

    geo = _get_window_geometry_by_id(window_id)
    if not geo:
        print(f"  Skipped: could not get geometry for window {window_id}")
        return False

    x, y, w, h = geo
    # Ensure even dimensions (required by x264)
    w = w if w % 2 == 0 else w + 1
    h = h if h % 2 == 0 else h + 1

    print(f"  Recording window {window_id} at {x},{y} {w}x{h} "
          f"for {duration}s...")

    cmd = [
        ffmpeg, "-y",
        "-f", "x11grab",
        "-framerate", str(fps),
        "-video_size", f"{w}x{h}",
        "-i", f"{display}+{x},{y}",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=duration + 30,
    )
    if result.returncode == 0:
        print(f"  Saved: {output_path.name}")
        return True
    else:
        print(f"  Warning: ffmpeg failed: {result.stderr[-200:]}")
        return False


def generate_viewer_recording(output_dir: Path, duration: int = 20):
    """Launch napari with Omega, then record the window for a demo video."""
    import napari

    success = False
    viewer = napari.Viewer(show=True)
    try:
        window = viewer.window._qt_window
        window.resize(1400, 900)
        _process_events(1.0)

        # Load sample data
        try:
            from napari_chatgpt._sample_data import make_sample_data

            layers = make_sample_data()
            for layer_data, meta, layer_type in layers:
                viewer.add_image(
                    layer_data, name=meta.get("name", "Sample")
                )
        except Exception:
            import numpy as np

            viewer.add_image(
                np.random.randint(0, 255, (512, 512), dtype=np.uint8),
                name="Sample",
            )

        _process_events(0.5)

        # Add Omega widget
        from napari_chatgpt._widget import OmegaQWidget

        widget = OmegaQWidget(viewer, add_code_editor=False)
        viewer.window.add_dock_widget(widget, area="right", name="Omega")
        _process_events(2.0)

        # Record the napari window using its actual X11 window ID
        wid = int(window.winId())
        success = record_window(
            output_path=output_dir / "omega_demo.mp4",
            window_id=wid,
            duration=duration,
        )
    finally:
        viewer.close()
        _process_events(0.5)
    return success


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate screenshots for wiki and social media"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent
        / "napari-chatgpt.wiki"
        / "images",
        help="Directory to write screenshots "
        "(default: ../napari-chatgpt.wiki/images/)",
    )
    parser.add_argument(
        "--only",
        choices=[
            "widget",
            "viewer",
            "api-keys",
            "editor",
            "chat",
            "cards",
            "recording",
            "all",
        ],
        default="all",
        help="Generate only a specific category of screenshots",
    )
    parser.add_argument(
        "--record-duration",
        type=int,
        default=20,
        help="Duration of screen recording in seconds (default: 20)",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    which = args.only
    needs_qt = which in (
        "all", "widget", "viewer", "api-keys", "editor", "recording",
    )
    if needs_qt:
        app = _ensure_app()  # noqa: F841 - must keep reference

    if which in ("all", "widget"):
        print("\n[1/7] Omega settings widget...")
        generate_omega_settings(output_dir)

    if which in ("all", "api-keys"):
        print("\n[2/7] API key dialogs...")
        for provider in ("OpenAI", "Anthropic", "Gemini"):
            generate_api_key_dialog_new(output_dir, provider)
        generate_api_key_dialog_returning(output_dir)

    if which in ("all", "editor"):
        print("\n[3/7] MicroPlugin editor...")
        generate_microplugin_editor(output_dir)

    if which in ("all", "viewer"):
        print("\n[4/7] Full napari viewer with Omega...")
        generate_viewer_with_omega(output_dir)

    if which in ("all", "chat"):
        print("\n[5/7] Chat UI mockup...")
        generate_chat_ui_mockup(output_dir)

    if which in ("all", "cards"):
        print("\n[6/7] Feature highlight cards...")
        generate_feature_cards(output_dir)

    if which == "recording":
        print("\n[7/7] Screen recording of napari viewer...")
        generate_viewer_recording(output_dir, duration=args.record_duration)

    print(f"\nDone! Screenshots saved to {output_dir}/")


if __name__ == "__main__":
    main()
