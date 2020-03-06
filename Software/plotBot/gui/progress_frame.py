from .dependencies import *
from .common import get_size_policy
from .. import communication
from .. import constants as pconstants


class ConnectionFrame(QGroupBox):
    CONNECT_TEXT = 'Connect'
    DISCONECT_TEXT = 'Disconnect'

    START_TEXT = 'Draw'
    STOP_TEXT = 'Pause'

    def __init__(self):
        super().__init__('Start')

        self.setSizePolicy(get_size_policy('Expanding', 'Preferred'))

        self.layout = QFormLayout()

        self.setLayout(self.layout)

        self.device_label = QLabel('')
        self.connect_button = QPushButton(self.CONNECT_TEXT)
        self.start_button = QPushButton(self.START_TEXT)

        self.connect_button.pressed.connect(self.connect_button_handler)
        self.start_button.pressed.connect(self.start_button_handler)

        self.layout.addRow(QLabel('Device:'), self.device_label)
        self.layout.addRow(QLabel(), self.connect_button)
        self.layout.addRow(QLabel(), self.start_button)

        self.set_device(None)

    def set_device(self, device: str):
        if device is None:
            self.connect_button.setText(self.CONNECT_TEXT)
            self.device_label.setText('')
            self.start_button.setText(self.START_TEXT)
            self.start_button.setEnabled(False)

        else:
            self.connect_button.setText(self.DISCONECT_TEXT)
            self.device_label.setText(device)
            self.start_button.setText(self.START_TEXT)
            self.start_button.setEnabled(True)

    def start_button_handler(self):
        if pconstants.IS_DRAWING:
            pconstants.IS_DRAWING = False
            self.start_button.setText(self.START_TEXT)
        else:
            pconstants.IS_DRAWING = True
            self.start_button.setText(self.STOP_TEXT)

    def find_device(self):
        port = communication.find_device()
        self.set_device(port)

    def disconnect_device(self):
        pconstants.CURRENT_DEVICE.close()
        pconstants.CURRENT_DEVICE = None
        self.set_device(None)

    def connect_button_handler(self):
        if pconstants.CURRENT_DEVICE is None:
            self.find_device()
        else:
            self.disconnect_device()


class ProgressFrame(QGroupBox):
    def __init__(self):
        super().__init__('Progress')

        self.setSizePolicy(get_size_policy('Expanding', 'Expanding'))