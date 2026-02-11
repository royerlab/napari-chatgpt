"""Clickable icon widget with hover highlighting for dark UI themes."""

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor, QIcon, QImage, QPainter, QPixmap
from qtpy.QtWidgets import QLabel


class ClickableIcon(QLabel):
    """A QLabel that displays an icon and emits a signal when clicked.

    Supports QIcon, QPixmap, or file path strings as icon sources. Optionally
    inverts colors for dark UI themes and shows a highlight overlay on hover.

    Attributes:
        clicked: Signal emitted when the icon is left-clicked.
    """

    clicked = Signal()  # Signal to emit when the label is clicked

    def __init__(
        self,
        icon: QIcon | QPixmap | str,
        size: int = 24,
        invert_colors: bool = True,
        parent=None,
    ):
        """Create a clickable icon label.

        Args:
            icon: The icon to display. Can be a QIcon, QPixmap, or file path
                string. Example: ``QApplication.style().standardIcon(QStyle.SP_FileIcon)``
            size: Icon size in pixels (width and height).
            invert_colors: If True, invert pixel colors for dark UI compatibility.
            parent: Parent widget.
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
            pixmap = icon.scaled(
                self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

        # Invert colors if requested:
        if invert_colors:
            pixmap = self._modify_pixmap_for_dark_ui(pixmap)

        # If the icon is a QPixmap, use it directly:
        self.setPixmap(pixmap)

        # Change cursor to hand pointer when hovering over the label:
        self.setCursor(Qt.PointingHandCursor)

        # Highlight color when hovering over the label:
        self.highlight_color = QColor(200, 200, 200, 50)  # Semi-transparent gray color

        # Flag to indicate if the mouse is hovering over the label:
        self.is_hovered = False

    def mousePressEvent(self, event):
        """Emit ``clicked`` signal on left mouse button press."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def enterEvent(self, event):
        """Set hover state to True and trigger repaint."""
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        """Clear hover state and trigger repaint."""
        self.is_hovered = False
        self.update()

    def paintEvent(self, event):
        """Paint the icon with a semi-transparent highlight overlay when hovered."""
        super().paintEvent(event)

        if self.is_hovered:
            painter = QPainter(self)
            painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
            painter.fillRect(self.rect(), self.highlight_color)
            painter.end()

    @staticmethod
    def _modify_pixmap_for_dark_ui(pixmap):
        """Invert the RGB colors of a pixmap for dark UI visibility.

        Args:
            pixmap: The source QPixmap to modify.

        Returns:
            A new QPixmap with inverted colors, preserving alpha transparency.
        """
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
