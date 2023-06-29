import sys

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QSlider, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
import numpy as np
from vispy import scene
from vispy.scene import visuals

class OrthoViewWidget(QWidget):
    def __init__(self, data, parent=None):
        super(OrthoViewWidget, self).__init__(parent)

        self.data = data
        self.shape = data.shape

        # Create sliders for x, y and z
        self.x_slider = QSlider(Qt.Horizontal)
        self.y_slider = QSlider(Qt.Horizontal)
        self.z_slider = QSlider(Qt.Horizontal)
        self.x_slider.setMaximum(self.shape[0] - 1)
        self.y_slider.setMaximum(self.shape[1] - 1)
        self.z_slider.setMaximum(self.shape[2] - 1)

        # Create three vispy SceneCanvas objects for each orthoview
        self.canvas_xy = scene.SceneCanvas(keys='interactive', show=True)
        self.canvas_yz = scene.SceneCanvas(keys='interactive', show=True)
        self.canvas_zx = scene.SceneCanvas(keys='interactive', show=True)

        # Set up a viewbox for each canvas
        self.view_xy = self.canvas_xy.central_widget.add_view()
        self.view_yz = self.canvas_yz.central_widget.add_view()
        self.view_zx = self.canvas_zx.central_widget.add_view()

        # Create an image visual for each view and attach to the viewboxes
        self.image_xy = visuals.Image(self.data[0,:,:], parent=self.view_xy.scene)
        self.image_yz = visuals.Image(self.data[:,0,:], parent=self.view_yz.scene)
        self.image_zx = visuals.Image(self.data[:,:,0], parent=self.view_zx.scene)

        # Add line visuals for slice positions
        self.line_xy = visuals.Line(color='red', parent=self.view_xy.scene)
        self.line_yz = visuals.Line(color='red', parent=self.view_yz.scene)
        self.line_zx = visuals.Line(color='red', parent=self.view_zx.scene)

        # Connect slider value changed signals to the update function
        self.x_slider.valueChanged.connect(self.update_views)
        self.y_slider.valueChanged.connect(self.update_views)
        self.z_slider.valueChanged.connect(self.update_views)

        # Create a layout
        self.layout = QVBoxLayout()
        self.slider_layout = QHBoxLayout()

        # Add the canvases and sliders to the layout
        self.layout.addWidget(self.canvas_xy.native)
        self.layout.addWidget(self.canvas_yz.native)
        self.layout.addWidget(self.canvas_zx.native)

        self.slider_layout.addWidget(QLabel('X:'))
        self.slider_layout.addWidget(self.x_slider)
        self.slider_layout.addWidget(QLabel('Y:'))
        self.slider_layout.addWidget(self.y_slider)
        self.slider_layout.addWidget(QLabel('Z:'))
        self.slider_layout.addWidget(self.z_slider)

        self.layout.addLayout(self.slider_layout)

        self.setLayout(self.layout)

    def update_views(self):
        x = self.x_slider.value()
        y = self.y_slider.value()
        z = self.z_slider.value()

        # Update the image visuals with new slices
        self.image_xy.set_data(self.data[x,:,:])
        self.image_yz.set_data(self.data[:,y,:])
        self.image_zx.set_data(self.data[:,:,z])

        # Update line positions
        self.line_xy.set_data(np.array([[y, 0], [y, self.shape[2]], [z, z], [0, z]]))
        self.line_yz.set_data(np.array([[x, 0], [x, self.shape[2]], [z, z], [0, x]]))
        self.line_zx.set_data(np.array([[z, 0], [z, self.shape[1]], [y, y], [0, y]]))

        self.canvas_xy.update()
        self.canvas_yz.update()
        self.canvas_zx.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create a 3D numpy array
    data = np.random.random((100, 100, 100))

    widget = OrthoViewWidget(data)
    widget.show()

    sys.exit(app.exec_())
