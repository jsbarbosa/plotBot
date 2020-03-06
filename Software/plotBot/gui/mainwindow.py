import numpy as np
import pyqtgraph as pg

from . import constants
from .dependencies import *
from .common import get_size_policy
from .source_frame import SourceFrame
from .preview_frame import PreviewFrame
from .progress_frame import ProgressFrame, ConnectionFrame


pg.setConfigOption('background', None)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlotBot")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        lay = QHBoxLayout(self.central_widget)

        self.source_frame = SourceFrame()
        self.view_frame = QFrame()
        self.view_frame.setSizePolicy(get_size_policy('Expanding', 'Expanding'))
        self.view_frame_layout = QVBoxLayout()
        self.view_frame.setLayout(self.view_frame_layout)

        self.preview_frame = PreviewFrame()
        self.connection_frame = ConnectionFrame()
        self.progress_frame = ProgressFrame()

        self.view_frame_layout.addWidget(self.preview_frame)
        self.view_frame_layout.addWidget(self.connection_frame)
        self.view_frame_layout.addWidget(self.progress_frame)

        self.update_preview_timer = QTimer()
        self.update_preview_timer.setInterval(constants.PREVIEW_REFRESH_TIME)
        self.update_preview_timer.timeout.connect(self.update_preview)
        self.update_preview_timer.start()

        lay.addWidget(self.source_frame)
        lay.addWidget(self.view_frame)

        self.resize(constants.DEFAULT_MAINWINDOW_WIDTH,
                    constants.DEFAULT_MAINWINDOW_HEIGHT)
        self.show()

    def update_preview(self):
        img = self.source_frame.get_image()
        self.preview_frame.update(img)
