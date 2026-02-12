"""Create and manage Jupyter notebook files programmatically.

Provides ``JupyterNotebookFile``, a helper for building ``.ipynb`` files
with code cells, markdown cells, and embedded images.
"""

import os
from base64 import b64encode
from collections.abc import Callable
from datetime import datetime
from io import BytesIO
from mimetypes import guess_type
from os import makedirs, path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from PIL import Image

from napari_chatgpt.utils.strings.markdown import extract_markdown_blocks


class JupyterNotebookFile:
    """In-memory Jupyter notebook builder that writes to disk on demand.

    Notebooks are stored in a timestamped file under
    ``~/Desktop/omega_notebooks/`` by default.  The class tracks whether the
    notebook has been modified since the last save/restart so redundant I/O
    is avoided.

    Attributes:
        default_file_path: Path where the notebook will be saved if no
            explicit path is given.
        file_path: Path of the most recently saved notebook file, or ``None``.
        notebook: The in-memory ``nbformat`` notebook object.
    """

    def __init__(self, notebook_folder_path: str | None = None):
        """Initialize a new notebook.

        Args:
            notebook_folder_path: Directory for saving notebook files.
                Defaults to ``~/Desktop/omega_notebooks/``.
        """
        self._modified = False
        self.restart(
            notebook_folder_path=notebook_folder_path,
            write_before_restart=False,
            force_restart=True,
        )

    def restart(
        self,
        notebook_folder_path: str | None = None,
        write_before_restart: bool = True,
        force_restart: bool = False,
    ):
        """Reset the notebook, optionally saving the current one first.

        Args:
            notebook_folder_path: Directory for the new notebook file.
            write_before_restart: If ``True``, persist the current notebook
                before creating a new one.
            force_restart: If ``True``, restart even when no modifications
                have been made.
        """
        # If the notebook has not been modified since last restart then we don't need to restart again:
        if not force_restart and not self._modified:
            return

        if write_before_restart:
            # Write the notebook to disk before restarting
            self.write()

        # path of system's desktop folder:
        desktop_path = path.join(path.join(path.expanduser("~")), "Desktop")

        # default folder path for notebooks:
        notebook_folder_path = notebook_folder_path or path.join(
            desktop_path, "omega_notebooks"
        )

        # Create the folder if it does not exist:
        if not path.exists(notebook_folder_path):
            makedirs(notebook_folder_path, exist_ok=True)

        # Get current date and time
        now = datetime.now()

        # Format date and time
        formatted_date_time = now.strftime("%Y_%m_%d_%H_%M_%S")

        # path of default notebook file on desktop:
        self.default_file_path = path.join(
            notebook_folder_path, f"{formatted_date_time}_omega_notebook.ipynb"
        )

        # Actual file path of the notebook (last saved file path):
        self.file_path = None

        # Restart the notebook:
        self.notebook = new_notebook()

        # Mark as not modified:
        self._modified = False

    def write(self, file_path: str | None = None):
        """Write the notebook to disk.

        Args:
            file_path: Destination path. Defaults to ``self.default_file_path``.
        """
        file_path = file_path or self.default_file_path
        # Write the notebook to disk
        with open(file_path, "w", encoding="utf-8") as f:
            nbformat.write(self.notebook, f)
            self.file_path = file_path

    def add_code_cell(self, code: str, remove_quotes: bool = False):
        """Append a code cell to the notebook.

        Args:
            code: Source code for the cell.
            remove_quotes: If ``True``, strip the first and last lines
                (assumed to be markdown code-fence delimiters).
        """
        if remove_quotes:
            # Remove the quotes from the code block
            code = "\n".join(code.split("\n")[1:-1])

        # Add a code cell
        self.notebook.cells.append(new_code_cell(code))

        # Mark as modified:
        self._modified = True

    def add_markdown_cell(self, markdown: str, detect_code_blocks: bool = True):
        """Append a markdown cell, optionally extracting embedded code blocks.

        When *detect_code_blocks* is ``True``, fenced code blocks inside the
        markdown are split out into separate code cells.

        Args:
            markdown: Markdown text to add.
            detect_code_blocks: If ``True``, parse and split code fences.
        """
        if detect_code_blocks:
            # Extract code blocks from markdown:
            blocks = extract_markdown_blocks(markdown)
            if blocks:
                # Add a code cell for each code block
                for block in blocks:
                    if block.strip().startswith("```"):
                        self.add_code_cell(block, remove_quotes=True)
                    else:
                        self.add_markdown_cell(block, detect_code_blocks=False)

        else:
            # Add a plain markdown cell without detecting code blocks:
            self.notebook.cells.append(new_markdown_cell(markdown))

            # Mark as modified:
            self._modified = True

    def _add_image(self, base64_string: str, image_type: str, text: str = ""):
        # Add a markdown cell with the image and optional text
        image_html = f'<img src="data:image/{image_type};base64,{base64_string}"/>'
        markdown_content = f"{text}\n\n{image_html}" if text else image_html
        new_image_cell = new_markdown_cell(markdown_content)
        self.notebook.cells.append(new_image_cell)

        # Mark as modified:
        self._modified = True

    def add_image_cell(self, image_path: str, text: str = ""):
        """Add a markdown cell with an embedded image loaded from a file path.

        Args:
            image_path: Path to the image file on disk.
            text: Optional text to display alongside the image.
        """
        # Read the image and convert it to base64
        mime_type = guess_type(image_path)[0]
        image_type = mime_type.split("/")[1] if mime_type else "png"
        with open(image_path, "rb") as image_file:
            base64_string = b64encode(image_file.read()).decode()

        # Use the existing method to add the image with text
        self._add_image(base64_string, image_type, text)

    def add_image_cell_from_PIL_image(self, pil_image: Image, text: str = ""):
        """Add a markdown cell with an embedded image from a PIL ``Image``.

        Args:
            pil_image: A PIL ``Image`` instance.
            text: Optional text to display alongside the image.
        """
        # Convert PIL image to base64
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        base64_string = b64encode(buffered.getvalue()).decode()

        # Use the existing method to add the image with text
        self._add_image(base64_string, "PNG", text)

        # Mark as modified:
        self._modified = True

    def register_snapshot_function(self, snapshot_function: Callable):
        """Register a callable that returns a PIL ``Image`` snapshot."""
        self._snapshot_function = snapshot_function

    def take_snapshot(self, text: str = ""):
        """Take a snapshot using the registered function and embed it as a cell.

        Args:
            text: Optional descriptive text to include with the snapshot.
        """
        # Call the snapshot function:
        pil_image = self._snapshot_function()

        # Add this image to the notebook
        self.add_image_cell_from_PIL_image(pil_image, text)

    def delete_notebook_file(self):
        """Delete the saved notebook file from disk, if it exists."""
        # Delete the notebook file
        if self.file_path is not None and path.exists(self.file_path):
            os.unlink(self.file_path)
            print(f"Deleted the notebook at {self.file_path}")


# def start_jupyter_server(folder_path):
#     # Function to run the notebook server in a thread
#     def notebook_thread():
#         notebookapp.main(['--notebook-dir', folder_path])
#
#     # Start the Jupyter server in a separate thread
#     thread = threading.Thread(target=notebook_thread)
#     thread.start()
#     print(f"Jupyter server started at {folder_path} 😄")
