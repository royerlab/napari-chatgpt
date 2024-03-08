import os
import tempfile

import requests

from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile


def test_notebook_creation():
    # Test if the notebook is created correctly
    notebook = JupyterNotebookFile()
    assert notebook.notebook is not None
    assert len(notebook.notebook.cells) == 0

    # delete the notebook file if it exists:
    notebook.delete_notebook_file()

def test_add_code_cell():
    # Test adding a code cell
    notebook = JupyterNotebookFile()
    notebook.add_code_cell("print('Hello, World!')")
    assert len(notebook.notebook.cells) == 1
    assert notebook.notebook.cells[0].cell_type == 'code'
    assert notebook.notebook.cells[0].source == "print('Hello, World!')"

    # delete the notebook file if it exists:
    notebook.delete_notebook_file()

def test_add_markdown_cell():
    # Test adding a markdown cell
    notebook = JupyterNotebookFile()
    notebook.add_markdown_cell("# Hello, World!")
    assert len(notebook.notebook.cells) == 1
    assert notebook.notebook.cells[0].cell_type == 'markdown'
    assert notebook.notebook.cells[0].source == "# Hello, World!"

    # delete the notebook file if it exists:
    notebook.delete_notebook_file()


def download_image(url, file):
    """Download an image from a URL and save it to a file object."""
    response = requests.get(url)
    file.write(response.content)
    file.flush()  # Ensure all data is written to the file


def test_add_image_cell():
    # URL of the image
    image_url = 'https://upload.wikimedia.org/wikipedia/commons/7/70/Example.png'

    # Use a temporary file
    temp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".png")

    # Download the image into the temporary file
    download_image(image_url, temp_image)

    # Close the file to ensure it is flushed and ready to be read
    temp_image.close()

    # Create an instance of JupyterNotebookFile
    notebook = JupyterNotebookFile()

    # Add the image cell with optional text
    notebook.add_image_cell(temp_image.name, "Example Image")

    # Save the notebook
    notebook_file_path = 'test_notebook.ipynb'
    notebook.write(notebook_file_path)

    # delete the notebook file:
    notebook.delete_notebook_file()


    print(f"Test completed. Notebook saved at {notebook_file_path}. Please open this notebook to verify the image cell.")



