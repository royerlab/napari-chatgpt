import os
import sys
import traceback

import requests
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QLabel, \
    QVBoxLayout, QPushButton, QDialog
from arbol import aprint


def download_file_qt(url: str,
                     filename: str,
                     folder: str):
    # Check if there is already a QApplication instance running
    if not QApplication.instance():
        # If not, create a new QApplication instance
        app = QApplication(sys.argv)
    else:
        # If there is, use the existing QApplication instance
        app = QApplication.instance()

    # Create a new instance of the MainWindow class
    dialog = DownloadFileDialog(url=url,
                                filename=filename,
                                folder=folder)

    # Set the dialog box to be modal, so that it blocks interaction with the main window
    dialog.setModal(True)

    # Show the dialog box
    dialog.exec()

    # dialog.worker.wait()


class ProgressBar(QWidget):
    def __init__(self,
                 filename: str,
                 parent=None):
        super().__init__(parent)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(1000)

        self.label = QLabel(self)
        self.label.setText(f"Click to download: {filename}")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.label)

    def setProgress(self, progress):
        if self.progressBar.value() < progress:
            text = f"Downloading... {int(progress / 10)}%"
            self.label.setText(text)
            self.progressBar.setValue(progress)

            if progress % 10 == 0:
                # every 10%:
                aprint(f'progress: {progress / 10}%')


class DownloadFileDialog(QDialog):
    def __init__(self,
                 url: str = "https://people.math.sc.edu/Burkardt/data/tif/at3_1m4_01.tif",
                 filename: str = "at3_1m4_01.tif",
                 folder: str = f'{os.path.expanduser("~")}/Downloads'
                 ):
        super().__init__()

        self.url = url
        self.filename = filename
        self.folder = folder

        self.progressBar = ProgressBar(filename=filename,
                                       parent=self)

        self.button = QPushButton("Download")
        self.button.clicked.connect(self.downloadFile)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.button)

    def downloadFile(self,
                     ) -> 'DownloadWorker':
        self.progressBar.setProgress(0)
        self.button.setEnabled(False)

        # Create a worker thread
        self.worker = DownloadWorker(url=self.url,
                                     filename=self.filename,
                                     folder=self.folder,
                                     progressBar=self.progressBar)

        # Start the worker thread
        self.worker.start()

        # Connect the worker's finished signal to a slot that will update the progress bar
        self.worker.finished.connect(self.onDownloadFinished)

        return self.worker

    def onDownloadFinished(self):
        self.progressBar.setProgress(1000)
        self.close()


class DownloadWorker(QThread):
    def __init__(self,
                 url: str,
                 filename: str,
                 folder: str,
                 progressBar
                 ):

        super().__init__()

        self.url = url
        self.filename = filename
        self.folder = folder

        self.progressBar = progressBar

        self.downloaded_bytes = 0

    def run(self):

        # Filepath:
        file_path = os.path.join(self.folder, self.filename)

        try:
            # Download the file
            with open(file_path, "wb") as f:
                request = requests.get(self.url, stream=True)

                file_size = int(request.headers['Content-Length'])

                for chunk in request.iter_content(4096):
                    f.write(chunk)
                    self.downloaded_bytes += len(chunk)

                    progress = int(self.downloaded_bytes * 1000 / file_size)

                    if progress % 10 == 0:
                        # Update the progress bar every 1%:
                        def event():
                            self.progressBar.setProgress(progress)

                        QTimer.singleShot(0, event)
                        #

        except Exception as e:
            traceback.print_exc()
            os.remove(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    download_file_qt(
        url="https://people.math.sc.edu/Burkardt/data/tif/at3_1m4_01.tif",
        filename="at3_1m4_01.tif",
        folder=f'{os.path.expanduser("~")}/Downloads')

    # sys.exit(app.exec_())
