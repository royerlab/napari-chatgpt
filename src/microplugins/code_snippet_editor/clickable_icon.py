from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor, QImage
from PyQt5.QtWidgets import QLabel


class ClickableIcon(QLabel):
    clicked = pyqtSignal()  # Signal to emit when the label is clicked

    def __init__(
        self, icon: Union[QIcon, QPixmap, str], invert_colors: bool = False, parent=None
    ):
        """
        Create a clickable icon label.
        The icon can be: QIcon, QPixmap, or a string with the path to the image.
        For example:
        icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)

        Parameters
        ----------
        icon : QIcon, QPixmap, or str
            The icon to display
        parent : QWidget, optional
            The parent widget, by default None

        """
        super().__init__(parent)
        pixmap = icon.pixmap(32, 32)  # Convert QIcon to QPixmap
        if invert_colors:
            pixmap = self._modify_pixmap_for_dark_ui(pixmap)
        self.setPixmap(pixmap)  # Adjust size as needed
        self.setCursor(Qt.PointingHandCursor)  # Change cursor to hand pointer

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    @staticmethod
    def _modify_pixmap_for_dark_ui(pixmap):
        # Convert QPixmap to QImage
        image = pixmap.toImage()

        # Ensure image supports alpha channel:
        image = image.convertToFormat(QImage.Format_ARGB32)

        # Access image pixels to invert colors and rotate hue, preserving transparency
        for x in range(image.width()):
            for y in range(image.height()):
                # Get the current pixel's color with alpha channel
                color = QColor(image.pixel(x, y))

                # Invert colors
                color.setRed(255 - color.red())
                color.setGreen(255 - color.green())
                color.setBlue(255 - color.blue())

                # Rotate hue by 180 degrees
                if (
                    color.hue() != -1
                ):  # Check if color is not grayscale (hue is undefined for grayscale)
                    hue = (color.hue() + 180) % 360
                    color.setHsv(
                        hue, color.saturation(), color.value(), color.alpha()
                    )  # Preserve alpha

                # Set the modified color back to the image
                image.setPixel(
                    x, y, color.rgba()
                )  # Use rgba() to include the alpha channel

        # Convert QImage back to QPixmap
        modified_pixmap = QPixmap.fromImage(image)
        return modified_pixmap
