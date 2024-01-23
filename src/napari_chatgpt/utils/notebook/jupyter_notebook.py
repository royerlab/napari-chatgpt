import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
class JupyterNotebookFile:

    def __init__(self):
        # Create a new notebook
        self.notebook = new_notebook()

    def write(self, file_path: str):
        # Write the notebook to disk
        with open(file_path, 'w') as f:
            nbformat.write(self.notebook, f)

    def add_code_cell(self, code: str):
        # Add a code cell
        self.notebook.cells.append(new_code_cell(code))

    def add_markdown_cell(self, markdown: str):
        # Add a markdown cell
        self.notebook.cells.append(new_markdown_cell(markdown))




# def start_jupyter_server(folder_path):
#     # Function to run the notebook server in a thread
#     def notebook_thread():
#         notebookapp.main(['--notebook-dir', folder_path])
#
#     # Start the Jupyter server in a separate thread
#     thread = threading.Thread(target=notebook_thread)
#     thread.start()
#     print(f"Jupyter server started at {folder_path} 😄")


