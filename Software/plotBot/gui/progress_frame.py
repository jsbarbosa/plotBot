from time import sleep
from threading import Thread

from .dependencies import *
from .common import get_size_policy
from .. import communication
from .. import constants as pconstants
from ..path_constructor import path_generator


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

        self.thread = None
        self.foreign_start_function = None
        self.foreign_stop_function = None

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

    def set_foreign_start_function(self, func):
        self.foreign_start_function = func

    def set_foreign_stop_function(self, func):
        self.foreign_stop_function = func

    def start_button_handler(self):
        if pconstants.IS_DRAWING:
            buttonReply = QMessageBox.question(self,
                                               'Drawing', "Do you want to stop drawing?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                pconstants.IS_DRAWING = False
                self.start_button.setText(self.START_TEXT)

        else:
            buttonReply = QMessageBox.question(self,
                                               'Drawing', "Do you want to start drawing?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                pconstants.IS_DRAWING = True
                self.start_button.setText(self.STOP_TEXT)
                self.start_thread()

    def find_device(self):
        port = communication.find_device()
        self.set_device(port)
        return port

    def connect_device(self, device: str):
        pconstants.CURRENT_DEVICE = communication.plotBotPort(device)

    def disconnect_device(self):
        if pconstants.CURRENT_DEVICE is not None:
            pconstants.CURRENT_DEVICE.close()
        pconstants.CURRENT_DEVICE = None
        self.set_device(None)

    def connect_button_handler(self):
        if pconstants.CURRENT_DEVICE is None:
            device = self.find_device()
            self.connect_device(device)

        else:
            self.disconnect_device()

    def threaded_method(self):
        image = self.foreign_start_function()
        paths = path_generator(image)
        for path in paths:
            trials = 0
            result = False
            while pconstants.IS_DRAWING and not result:
                result = pconstants.CURRENT_DEVICE.set_position(*path)
                if trials == pconstants.NUMBER_OF_PIXEL_TRIALS - 1:
                    raise(ValueError("Position X{} Y{} Z{} can not be reached".format(*path)))
                else:
                    sleep(pconstants.TRIAL_TIMEOUT)
                trials += 1

        self.foreign_stop_function()
        self.thread = None
        pconstants.IS_DRAWING = False
        self.start_button.setText(self.START_TEXT)

    def start_thread(self):
        self.thread = Thread(target=self.threaded_method,
                             daemon=True)
        self.thread.start()


class ProgressFrame(QGroupBox):
    def __init__(self):
        super().__init__('Progress')

        self.setSizePolicy(get_size_policy('Expanding', 'Expanding'))