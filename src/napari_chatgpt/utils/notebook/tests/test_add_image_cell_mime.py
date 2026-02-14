"""Test for Fix 4: add_image_cell handles unknown MIME types."""

import os
import tempfile

from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile


def test_add_image_cell_unknown_mime():
    """add_image_cell handles unknown MIME types without crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # File with extension that guess_type won't recognize
        unusual_file = os.path.join(tmpdir, "image.xyz_unk")
        # Write some bytes so the file can be read
        with open(unusual_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        notebook = JupyterNotebookFile(notebook_folder_path=tmpdir)
        # This should not crash (falls back to "png")
        notebook.add_image_cell(unusual_file, text="test image")

        # Verify a cell was added
        assert len(notebook.notebook.cells) == 1
        assert "png" in notebook.notebook.cells[0].source
