import traceback
import numpy as np
import pyqtgraph as pg
from threading import Thread
from skimage import feature, transform, filters
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from . import constants
from .. import constants as pconstants
from .dependencies import *
from .common import get_size_policy, error_window


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

        self.setSizePolicy(get_size_policy('Preferred', 'Expanding'))

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
            image = self.text_frame.get_image()
        else:
            self.file_frame.set_image()
            image = self.file_frame.get_image()
        return image


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
        self.font_combobox.addItems(constants.FONTS)
        self.font_combobox.setMaximumWidth(100)
        self.font_combobox.currentIndexChanged.connect(self.change_font_properties)

        self.fontsize_spinbox = QSpinBox()
        self.fontsize_spinbox.setValue(constants.DEFAULT_FONTSIZE)
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

        text = self.get_text()

        img = Image.new('1',
                        (pconstants.WIDTH, pconstants.HEIGHT))
        d = ImageDraw.Draw(img)

        if not constants.IGNORE_FONTS:
            font_path = constants.FONTS_DICT[properties['font']]
            font = ImageFont.truetype(font_path, properties['size'])

            d.text((0, 0), text, fill=1, font=font)
        else:
            d.text((0, 0), text, fill=1)

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

        self.tabs = QTabWidget()
        self.tab1 = Properties_1_Tab()
        self.tab1.set_slot(self.set_image)

        # Add tabs
        self.tabs.addTab(self.tab1, "Properties")

        self.image_view = pg.ViewBox()
        self.image_item = pg.ImageItem()
        self.image_widget = pg.ImageView(view=self.image_view,
                                         imageItem=self.image_item)
        # self.image_widget.ui.histogram.hide()
        self.image_widget.ui.roiBtn.hide()
        self.image_widget.ui.menuBtn.hide()

        # self.image_widget.scene.sigMouseMoved.connect(self.mouseMoved)
        self.image_widget.scene.sigPrepareForPaint.connect(self.set_image_movement)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(self.lineedit)
        self.layout.addWidget(self.browse_button, alignment=Qt.AlignRight)
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.image_widget)

        self.original_image = None
        self.processed_image = None
        self.image_moved = False
        self.properties = self.tab1.get_properties()

        self.thread = None

    def browse(self):
        name, ext = QFileDialog.getOpenFileName(self,
                                                'Open image',
                                                filter=self.FILE_FILTERS,
                                                options=QFileDialog.DontUseNativeDialog)
        if name:
            self.lineedit.setText(name)

            try:
                self.original_image = np.array(Image.open(name).convert('L'))
                self.image_widget.setImage(self.original_image.T)
                self.set_image()

            except (FileNotFoundError, UnidentifiedImageError, ValueError) as e:
                expanded = traceback.format_exc()
                self.lineedit.setText('')
                self.original_image = None

                error_window(str(e), expanded)

    def set_image_movement(self):
        self.image_moved = True

    def get_image(self):
        return self.processed_image

    def get_rectangle_corners(self, rectangle):
        left = rectangle.left()
        right = rectangle.right()
        bottom = rectangle.bottom()
        top = rectangle.top()

        return np.array([left, right, bottom, top]).round().astype(int)

    def get_displayed_image(self):
        view_left, view_right, view_bottom, view_top = self.get_rectangle_corners(self.image_item.viewRect())
        bound_left, bound_right, bound_bottom, bound_top = self.get_rectangle_corners(self.image_item.boundingRect())

        left = min(bound_right, max(0, view_left))
        right = min(bound_right, max(0, view_right))
        top = min(bound_bottom, max(0, view_top))
        bottom = min(bound_bottom, max(0, view_bottom))

        return self.image_item.image.T[top:bottom, left:right]

    def get_image_to_show(self):
        image_on_display = self.get_displayed_image()
        height, width = image_on_display.shape
        image_on_display = transform.rescale(image_on_display,
                                             (pconstants.HEIGHT / height, pconstants.WIDTH / width),
                                             anti_aliasing=False)

        return image_on_display

    def __set_image__(self):
        properties = self.tab1.get_properties()
        if self.original_image is not None:
            image_on_display = self.get_image_to_show()

            if ~np.array_equal(self.processed_image, image_on_display) or self.image_moved:
                image = properties['binary_algorithm'](image_on_display)
                if properties['is_threshold']:
                    self.processed_image = image_on_display > image
                else:
                    self.processed_image = image
                self.image_moved = False
            else:
                return
        self.thread = None

    def set_image(self):
        if self.thread is None:
            self.thread = Thread(target=self.__set_image__,
                                 daemon=True)
            self.thread.start()


class Properties_1_Tab(QWidget):
    BINARY_OPTIONS = [
        'Isodata',
        'Li',
        'Mean',
        'Minimum',
        'Niblack',
        'Otsu',
        'Sauvola',
        'Triangle',
        'Yen',
        'Canny'
    ]

    def __init__(self):
        super().__init__()

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.binary_combobox = QComboBox()
        self.binary_combobox.addItems(self.BINARY_OPTIONS)

        self.binary_combobox.currentTextChanged.connect(self.binary_combobox_handler)

        self.sigma_spinbox = QDoubleSpinBox()

        self.extraspace_frame = QFrame()
        self.extraspace_frame.setSizePolicy(get_size_policy('Expanding', 'Expanding'))

        self.layout.addRow(QLabel('Binary algorithm'), self.binary_combobox)
        self.layout.addRow(QLabel('Canny sigma'), self.sigma_spinbox)

        self.layout.addRow(self.extraspace_frame, self.extraspace_frame)

        self.foreign_slot = None

        self.binary_combobox_handler()

    def binary_combobox_handler(self, *args):
        if self.binary_combobox.currentText() == 'Canny':
            self.sigma_spinbox.setEnabled(True)
        else:
            self.sigma_spinbox.setEnabled(False)
        if self.foreign_slot is not None:
            self.foreign_slot()

    def get_rescale_option(self):
        return getattr(Image, self.rescale_combobox.currentText().upper())

    def set_slot(self, slot):
        self.foreign_slot = slot
        self.sigma_spinbox.valueChanged.connect(slot)

    def canny(self, image):
        return feature.canny(image, sigma=self.sigma_spinbox.value())

    def get_properties(self):
        binary_algorithm = self.binary_combobox.currentText().lower()
        if binary_algorithm != 'canny':
            binary_algorithm = getattr(filters, 'threshold_%s' % binary_algorithm)
            is_threshold = True
        else:
            binary_algorithm = self.canny
            is_threshold = False

        return {
            'is_threshold': is_threshold,
            'binary_algorithm': binary_algorithm,
        }
