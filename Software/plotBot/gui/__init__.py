import os
import sys
from time import sleep
from threading import Thread

from . import constants
from .mainwindow import MainWindow
from .common import set_darkstyle, get_fonts
from .dependencies import QApplication, QStyleFactory, QPixmap, QSplashScreen, Qt, QProgressBar

CURRENT_FOLDER = os.path.dirname(__file__)


def run():
    global CURRENT_FOLDER

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # <- Choose the style

    set_darkstyle(app)

    splash_pic = QPixmap(os.path.join(CURRENT_FOLDER, 'splash.png')).scaledToWidth(600)

    splash = QSplashScreen(splash_pic, Qt.WindowStaysOnTopHint)
    progressbar = QProgressBar(splash)

    splash.show()

    thread = Thread(target=get_fonts)
    thread.start()

    while constants.PROGRESS_BAR_VALUE < 100:
        progressbar.setValue(constants.PROGRESS_BAR_VALUE)
        app.processEvents()
        sleep(0.1)

    sleep(0.5)

    splash.close()

    mainwindow = MainWindow()

    return sys.exit(app.exec_())
