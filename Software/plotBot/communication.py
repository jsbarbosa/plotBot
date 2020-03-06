import serial
from time import sleep
import serial.tools.list_ports as find_ports
from . import constants
from .common import print_exception, print_info

TEST_MESSAGE = "*IDN?"
TEST_ANSWER = "plotBot"


class plotBotPort(serial.Serial):
    BAUDRATE = 9600
    TIMEOUT = 0.5

    def __init__(self, port: str):
        super().__init__(port=port,
                         baudrate=self.BAUDRATE,
                         timeout=self.TIMEOUT)
        self.flush()

    def write_str(self, data: str):
        print_info('plotBotPort.write_str', data.encode())
        self.write(data.encode())

    def read_string_line(self) -> str:
        line = self.readline()
        print_info('plotBotPort.read_string_line', line)
        try:
            return line.decode()
        except UnicodeDecodeError:
            return ''


def test_device(device: str):
    global TEST_MESSAGE, TEST_ANSWER
    try:
        port = plotBotPort(port=device)
        port.write_str(TEST_MESSAGE)
        answer = port.read_string_line()
        port.close()

    except serial.SerialException as e:
        answer = ''
        print_exception(e)

    is_device = False
    if TEST_ANSWER in answer:
        is_device = True

    return is_device


def find_device():
    ports_objects = list(find_ports.comports())
    for i in range(len(ports_objects)):
        port = ports_objects[i]
        if test_device(port.device):
            constants.CURRENT_DEVICE = plotBotPort(port.device)
            return port.device
