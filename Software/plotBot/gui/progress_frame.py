from .dependencies import *
from .common import get_size_policy


class ProgressFrame(QGroupBox):
    def __init__(self):
        super().__init__('Progress')

        self.setSizePolicy(get_size_policy('Expanding', 'Expanding'))
