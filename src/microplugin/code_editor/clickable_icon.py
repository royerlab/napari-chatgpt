from typing import Union

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QIcon, QPixmap, QColor, QImage
from qtpy.QtWidgets import QLabel


class ClickableIcon(QLabel):
    clicked = Signal()  # Signal to emit when the label is clicked

    def __init__(
            self,
            icon: Union[QIcon, QPixmap, str],
            size: int = 24,
            invert_colors: bool = True,
            parent=None
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

        # Store the size for use in scaling the icon:
        self.size = size

        # Convert the icon to QIcon if it is a string:
        if isinstance(icon, str):
            icon = QIcon(icon)

        # Convert the icon to QPixmap if it is a QIcon or use it directly if it's already a QPixmap:
        if isinstance(icon, QIcon):
            # Get the pixmap from the icon, scaled isotropically:
            pixmap = icon.pixmap(self.size, self.size)
        elif isinstance(icon, QPixmap):
            pixmap = icon.scaled(self.size,
                                 self.size,
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)

        # Invert colors if requested:
        if invert_colors:
            pixmap = self._modify_pixmap_for_dark_ui(pixmap)

        # If the icon is a QPixmap, use it directly:
        self.setPixmap(pixmap)

        # Change cursor to hand pointer when hovering over the label:
        self.setCursor(Qt.PointingHandCursor)

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

                # # Rotate hue by 180 degrees
                # if (
                #         color.hue() != -1
                # ):  # Check if color is not grayscale (hue is undefined for grayscale)
                #     hue = (color.hue() + 180) % 360
                #     color.setHsv(
                #         hue, color.saturation(), color.value(), color.alpha()
                #     )  # Preserve alpha
                #
                # # Set the modified color back to the image
                # image.setPixel(
                #     x, y, color.rgba()
                # )  # Use rgba() to include the alpha channel

        # Convert QImage back to QPixmap
        modified_pixmap = QPixmap.fromImage(image)
        return modified_pixmap
