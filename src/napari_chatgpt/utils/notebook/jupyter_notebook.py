import os
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from mimetypes import guess_type
from os import path, makedirs
from typing import Optional, Callable

import nbformat
from PIL import Image
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

from napari_chatgpt.utils.strings.markdown import extract_markdown_blocks


class JupyterNotebookFile:

    def __init__(self, notebook_folder_path: Optional[str] = None):
        """
        Initialize a new JupyterNotebookFile instance and start a fresh notebook session.
        
        Parameters:
            notebook_folder_path (Optional[str]): Path to the folder where notebooks will be stored. If not provided, defaults to a folder named "omega_notebooks" on the user's Desktop.
        """
        self._modified = False
        self.restart(
            notebook_folder_path=notebook_folder_path,
            write_before_restart=False,
            force_restart=True,
        )

    def restart(
        self,
        notebook_folder_path: Optional[str] = None,
        write_before_restart: bool = True,
        force_restart: bool = False,
    ):

        # If the notebook has not been modified since last restart then we don't need to restart again:
        """
        Restart the notebook session, optionally saving changes and updating the storage location.
        
        If the notebook has been modified or a forced restart is requested, writes the current notebook to disk (if specified), resets the notebook to a new empty state, and updates the default file path to a timestamped filename in the specified or default folder. Creates the target folder if it does not exist.
        """
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

    def write(self, file_path: Optional[str] = None):
        """
        Write the current notebook to disk at the specified file path or the default location.
        
        Parameters:
            file_path (Optional[str]): The path where the notebook will be saved. If not provided, uses the default file path.
        """
        file_path = file_path or self.default_file_path
        # Write the notebook to disk
        with open(file_path, "w") as f:
            nbformat.write(self.notebook, f)
            self.file_path = file_path

    def add_code_cell(self, code: str, remove_quotes: bool = False):

        """
        Adds a code cell to the notebook with the provided code.
        
        Parameters:
            code (str): The code to insert into the new cell.
            remove_quotes (bool): If True, removes the first and last lines from the code before adding, typically to strip enclosing quotes.
        """
        if remove_quotes:
            # Remove the quotes from the code block
            code = "\n".join(code.split("\n")[1:-1])

        # Add a code cell
        self.notebook.cells.append(new_code_cell(code))

        # Mark as modified:
        self._modified = True

    def add_markdown_cell(self, markdown: str, detect_code_blocks: bool = True):

        """
        Add a markdown cell to the notebook, optionally extracting and adding code blocks as separate code cells.
        
        If `detect_code_blocks` is True, code blocks within the markdown are extracted and added as code cells, while other blocks are added as markdown cells. If False, the entire input is added as a single markdown cell.
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
        # Read the image and convert it to base64
        """
        Adds an image cell to the notebook by embedding an image file from disk, optionally accompanied by descriptive text.
        
        Parameters:
            image_path (str): Path to the image file to embed.
            text (str, optional): Text to display alongside the image. Defaults to an empty string.
        """
        image_type = guess_type(image_path)[0].split("/")[1]
        with open(image_path, "rb") as image_file:
            base64_string = b64encode(image_file.read()).decode()

        # Use the existing method to add the image with text
        self._add_image(base64_string, image_type, text)

    def add_image_cell_from_PIL_image(self, pil_image: Image, text: str = ""):
        # Convert PIL image to base64
        """
        Adds a PNG image cell to the notebook from a given PIL Image object, optionally including accompanying text.
        
        Parameters:
            pil_image (Image): The PIL Image to embed in the notebook.
            text (str): Optional text to display with the image.
        """
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        base64_string = b64encode(buffered.getvalue()).decode()

        # Use the existing method to add the image with text
        self._add_image(base64_string, "PNG", text)

        # Mark as modified:
        self._modified = True

    def register_snapshot_function(self, snapshot_function: Callable):
        self._snapshot_function = snapshot_function

    def take_snapshot(self, text: str = ""):

        # Call the snapshot function:
        """
        Captures an image using the registered snapshot function and adds it as an image cell to the notebook.
        
        Parameters:
            text (str): Optional text to accompany the image in the notebook cell.
        """
        pil_image = self._snapshot_function()

        # Add this image to the notebook
        self.add_image_cell_from_PIL_image(pil_image, text)

    def delete_notebook_file(self):
        # Delete the notebook file
        """
        Delete the current notebook file from disk if it exists.
        """
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
