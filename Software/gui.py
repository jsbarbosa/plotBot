import os
import sys
# import fontconfig
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import pyqtgraph as pg
from time import sleep
from threading import Thread

from constants import DEFAULT_FONTSIZE, WIDTH, HEIGHT

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, \
                            QFrame, QGroupBox, QRadioButton, QTextEdit, QLineEdit, QPushButton, \
                            QFileDialog, QComboBox, QSpinBox, QSizePolicy, QSplashScreen, QProgressBar, QStyleFactory


pg.setConfigOption('background', None)

PROGRESS_BAR_VALUE = 0
FONTS_DICT = {}
FONTS = []

class MainWindow(QMainWindow):
    PREVIEW_REFRESH_TIME = 100

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlotBot")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        lay = QHBoxLayout(self.central_widget)

        self.source_frame = SourceFrame()
        self.preview_frame = PreviewFrame()
        self.progress_frame = ProgressView()

        self.update_preview_timer = QTimer()
        self.update_preview_timer.setInterval(self.PREVIEW_REFRESH_TIME)
        self.update_preview_timer.timeout.connect(self.update_preview)
        self.update_preview_timer.start()

        lay.addWidget(self.source_frame)
        lay.addWidget(self.preview_frame)
        lay.addWidget(self.progress_frame)

        self.resize(600, 400)
        self.show()

    def update_preview(self):
        if self.source_frame.is_text_mode:
            img = self.source_frame.get_image()
            self.preview_frame.update(img)


class SourceFrame(QGroupBox):
    TEXT_LABEL = 'Text'
    FILE_LABEL = 'File'

    def __init__(self):
        super().__init__("Source")

        # layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # choices
        self.choice_frame = QFrame()
        self.choice_frame.setMaximumHeight(40)
        self.choice_layout = QHBoxLayout()
        self.choice_frame.setLayout(self.choice_layout)

        self.layout.addWidget(self.choice_frame)

        # specific_choice_frame
        self.text_frame = TextFrame()
        self.file_frame = FileFrame()

        self.chosen_frame = QFrame()
        self.chosen_frame_layout = QVBoxLayout()
        self.chosen_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.chosen_frame.setLayout(self.chosen_frame_layout)
        self.chosen_frame_layout.addWidget(self.file_frame)

        self.layout.addWidget(self.chosen_frame)

        self.is_text_mode = 1

        rb = self.create_radiobutton(self.TEXT_LABEL, self.radiobutton_handler)
        rb.setChecked(True)
        self.choice_layout.addWidget(rb)

        rb = self.create_radiobutton(self.FILE_LABEL, self.radiobutton_handler)
        self.choice_layout.addWidget(rb)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.setSizePolicy(sizePolicy)

    def create_radiobutton(self, name: str, connect_func):
        rb = QRadioButton(name)
        rb.toggled.connect(connect_func)
        return rb

    def radiobutton_handler(self):
        rb = self.sender()
        if rb.isChecked():
            self.is_text_mode = rb.text() == self.TEXT_LABEL
            if self.is_text_mode:
                # remove file widget
                self.chosen_frame_layout.removeWidget(self.file_frame)
                self.file_frame.setParent(None)

                # include text widget
                self.chosen_frame_layout.addWidget(self.text_frame)

            else:
                # remove text widget
                self.chosen_frame_layout.removeWidget(self.text_frame)
                self.text_frame.setParent(None)

                # include file widget
                self.chosen_frame_layout.addWidget(self.file_frame)

    def get_image(self):
        if self.is_text_mode:
            return self.text_frame.get_image()
        else:
            return None


class TextFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.menu_frame = QFrame()
        self.menu_frame_layout = QHBoxLayout()
        self.menu_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_frame_layout.setSpacing(2)
        self.menu_frame.setLayout(self.menu_frame_layout)
        self.layout.addWidget(self.menu_frame)

        self.font_combobox = QComboBox()
        self.font_combobox.addItems(FONTS)
        self.font_combobox.setMaximumWidth(100)
        self.font_combobox.currentIndexChanged.connect(self.change_font_properties)

        self.fontsize_spinbox = QSpinBox()
        self.fontsize_spinbox.setValue(DEFAULT_FONTSIZE)
        self.fontsize_spinbox.setMinimum(8)
        self.fontsize_spinbox.setMaximum(100)
        self.fontsize_spinbox.valueChanged.connect(self.change_font_properties)

        menu_widgets = [
            (QLabel('Font:'), self.font_combobox),
            (QLabel('Size:'), self.fontsize_spinbox)
        ]

        for i, (label, widget) in enumerate(menu_widgets):
            self.menu_frame_layout.addWidget(label)
            self.menu_frame_layout.addWidget(widget)

        self.textedit = QTextEdit()
        self.layout.addWidget(self.textedit)

        self.change_font_properties()

    def change_font_properties(self, *args):
        properties = self.get_font_properties()

        font = QFont(properties['font'])
        font.setPointSize(properties['size'])
        self.textedit.setFont(font)

    def get_font_properties(self) -> dict:
        font = self.font_combobox.currentText()
        size = self.fontsize_spinbox.value()

        return {
            'font': font,
            'size': size
        }

    def get_text(self):
        return self.textedit.toPlainText()

    def get_image(self):
        properties = self.get_font_properties()
        # font_path = FONTS_DICT[properties['font']]
        # font = ImageFont.truetype(font_path, properties['size'])
        text = self.get_text()

        img = Image.new('1', (WIDTH, HEIGHT))
        d = ImageDraw.Draw(img)
        d.text((0, 0), text, fill=1)
        # d.text((0, 0), text, fill=1, font=font)

        img = np.array(img)
        return img


class FileFrame(QFrame):
    FILE_FILTERS = "Images (*.jpg *.jpeg)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lineedit = QLineEdit()
        self.lineedit.setEnabled(False)
        self.lineedit.setMinimumWidth(300)
        self.browse_button = QPushButton('Browse')
        self.browse_button.setMaximumWidth(80)

        self.browse_button.clicked.connect(self.browse)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(self.lineedit)
        self.layout.addWidget(self.browse_button)

    def browse(self):
        name, ext = QFileDialog.getOpenFileName(self,
                                                'Open image',
                                                filter=self.FILE_FILTERS,
                                                options=QFileDialog.DontUseNativeDialog)
        if name:
            self.lineedit.setText(name)



class PreviewFrame(QGroupBox):
    def __init__(self):
        super().__init__('Preview')

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

        self.image_widget = pg.ImageView()
        self.image_widget.ui.histogram.hide()
        self.image_widget.ui.roiBtn.hide()
        self.image_widget.ui.menuBtn.hide()

        self.layout.addWidget(self.image_widget)
        self.current_image = None

    def update(self, image: np.array):
        if self.current_image is None:
            self.current_image = image
            self.image_widget.setImage(image.T)

        elif not np.array_equal(image, self.current_image):
            self.current_image = image
            self.image_widget.setImage(image.T)


class ProgressView(QGroupBox):
    def __init__(self):
        super().__init__('Progress')

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)


def get_fonts():
    global PROGRESS_BAR_VALUE, FONTS_DICT, FONTS
    # fonts = fontconfig.query(lang='en')
    # n_fonts = len(fonts)
    # for i in range(n_fonts):
    #     PROGRESS_BAR_VALUE = min(round(100 * (i + 1) / n_fonts), 99)
    #     if type(fonts[i]) is str:
    #         font = fontconfig.FcFont(fonts[i])
    #     else:
    #         font = fonts[i]
    #     if font.family and font.fontformat == 'TrueType':
    #         name = dict(font.family)['en']
    #         if name not in FONTS_DICT:
    #             FONTS_DICT[name] = font.file
    #             FONTS.append(name)

    qfonts = QFontDatabase().families()
    FONTS = qfonts
    # FONTS = sorted([font for font in FONTS if font in qfonts])
    # FONTS_DICT = dict([(font, FONTS_DICT[font]) for font in FONTS])
    PROGRESS_BAR_VALUE = 100


def darkstyle(application):
    darkpalette = QPalette()
    darkpalette.setColor(QPalette.Window, QColor(41, 44, 51))
    darkpalette.setColor(QPalette.WindowText, Qt.white)
    darkpalette.setColor(QPalette.Base, QColor(15, 15, 15))
    darkpalette.setColor(QPalette.AlternateBase, QColor(41, 44, 51))
    darkpalette.setColor(QPalette.ToolTipBase, Qt.white)
    darkpalette.setColor(QPalette.ToolTipText, Qt.white)
    darkpalette.setColor(QPalette.Text, Qt.white)
    darkpalette.setColor(QPalette.Button, QColor(41, 44, 51))
    darkpalette.setColor(QPalette.ButtonText, Qt.white)
    darkpalette.setColor(QPalette.BrightText, Qt.red)
    darkpalette.setColor(QPalette.Highlight, QColor(100, 100, 225))
    darkpalette.setColor(QPalette.HighlightedText, Qt.black)
    application.setPalette(darkpalette)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # <- Choose the style

    darkstyle(app)

    splash_pic = QPixmap('splash.png').scaledToWidth(600)

    splash = QSplashScreen(splash_pic, Qt.WindowStaysOnTopHint)
    progressbar = QProgressBar(splash)

    splash.show()

    thread = Thread(target=get_fonts)
    thread.start()

    while PROGRESS_BAR_VALUE < 100:
        progressbar.setValue(PROGRESS_BAR_VALUE)
        app.processEvents()
        sleep(0.1)

    sleep(0.5)

    splash.close()

    mainwindow = MainWindow()

    sys.exit(app.exec_())