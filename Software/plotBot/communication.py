import serial
import serial.tools.list_ports as find_ports
from .common import print_exception, print_info

from . import constants

TEST_MESSAGE = "*IDN?"
TEST_ANSWER = "plotBot"


class plotBotPort(serial.Serial):
    BAUDRATE = 9600
    TIMEOUT = 0.5

    POSITION_FORMAT = "X{} Y{} Z{}"

    X_RESOLUTION = 55
    Y_RESOLUTION = 55

    def __init__(self, port: str):
        super().__init__(port=port,
                         baudrate=self.BAUDRATE,
                         timeout=self.TIMEOUT)
        # self.flush()
        self.last_x = None
        self.last_y = None
        self.last_z = None

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

    def set_position(self,
                     x: int = None,
                     y: int = None,
                     z: int = None):
        if x is None:
            x = self.last_x
            if self.last_x is None:
                raise(Exception('No starting x position has been set'))

        if y is None:
            y = self.last_y
            if self.last_y is None:
                raise(Exception('No starting z position has been set'))

        if z is None:
            z = self.last_z
            if self.last_z is None:
                raise(Exception('No starting z position has been set'))

        if x < 0 or x > self.X_RESOLUTION:
            raise(ValueError('x value should be within 0 and {}, its: {}'.format(self.X_RESOLUTION, x)))
        if y < 0 or y > self.Y_RESOLUTION:
            raise (ValueError('y value should be within 0 and {}, its: {}'.format(self.Y_RESOLUTION, y)))
        if z not in [0, 1]:
            raise(ValueError('z value should be either 0 or 1, its: {}'.format(z)))

        self.write_str(self.POSITION_FORMAT.format(x, y, z))

        if self.read_string_line() == 'OK\r\n':
            self.last_x = x
            self.last_y = y
            self.last_z = z

            return True
        else:
            return False


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

