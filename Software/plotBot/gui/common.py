from . import constants
from .dependencies import *
from .. import constants as pconstants


def get_size_policy(horizontal: str, vertical: str) -> QSizePolicy:
    size_policy = QSizePolicy(getattr(QSizePolicy, horizontal),
                              getattr(QSizePolicy, vertical))
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)

    return size_policy


def get_fonts():
    if not constants.IGNORE_FONTS:
        if pconstants.SYSTEM == pconstants.WINDOWS:
            raise(NotImplementedError('Windows fonts to develop'))

        else:
            import fontconfig

            fonts = fontconfig.query(lang='en')
            n_fonts = len(fonts)
            for i in range(n_fonts):
                constants.PROGRESS_BAR_VALUE = min(round(100 * (i + 1) / n_fonts), 99)
                if type(fonts[i]) is str:
                    font = fontconfig.FcFont(fonts[i])
                else:
                    font = fonts[i]
                if font.family and font.fontformat == 'TrueType':
                    name = dict(font.family)['en']
                    if name not in constants.FONTS_DICT:
                        constants.FONTS_DICT[name] = font.file
                        constants.FONTS.append(name)

            qfonts = QFontDatabase().families()
            constants.FONTS = sorted([font for font in constants.FONTS if font in qfonts])
            constants.FONTS_DICT = dict([(font, constants.FONTS_DICT[font]) for font in constants.FONTS])

    constants.PROGRESS_BAR_VALUE = 100


def set_darkstyle(application):
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


def error_window(exception_str: str, traceback_str: str) -> int:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText("An error has ocurred")
    msg.setInformativeText(exception_str)
    msg.setWindowTitle("Error")
    msg.setDetailedText(traceback_str)
    msg.setStandardButtons(QMessageBox.Ok)

    return msg.exec_()

