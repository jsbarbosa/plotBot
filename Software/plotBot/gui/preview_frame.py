import numpy as np
import pyqtgraph as pg
from skimage import measure

from .dependencies import *
from .common import get_size_policy


class PreviewFrame(QGroupBox):
    def __init__(self):
        super().__init__('Preview')

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.setSizePolicy(get_size_policy('Expanding', 'Expanding'))

        # self.image_widget = pg.PlotWidget()
        self.image_widget = pg.ImageView()
        self.image_widget.ui.histogram.hide()
        self.image_widget.ui.roiBtn.hide()
        self.image_widget.ui.menuBtn.hide()
        # self.plot_lines = []

        self.layout.addWidget(self.image_widget)
        self.current_image = None

    def update(self, image: np.array):
        if image is not None:
            if self.current_image is None:
                pass
            elif not np.array_equal(image, self.current_image):
                pass
            else:
                return

            self.image_widget.setImage(image.T)
            # contours = measure.find_contours(image.T, 0.0)
            # for line in self.plot_lines:
            #     line.clear()
            #
            # for contour in contours:
            #     contour = contour.round().astype(int)
            #     mask = np.zeros(contour.shape[0], dtype=bool)
            #     mask[1:] = (np.diff(contour, axis=0) == 0).sum(axis=1) == 2
            #     contour = np.delete(contour, mask, axis=0)
            #
            #     line = self.image_widget.plot(contour[:, 0], contour[:, 1])
            #     self.plot_lines.append(line)

        self.current_image = image
