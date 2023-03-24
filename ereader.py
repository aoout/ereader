import logging

from PyQt5.QtWidgets import QApplication, QHBoxLayout
from qframelesswindow import FramelessWindow, StandardTitleBar

from readview import ReadView

logging.basicConfig(level=logging.INFO)


class EReader(FramelessWindow):

    def __init__(self) -> None:

        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        self.setWindowTitle('EReader')
        self._resizeWindow()
        self._setLayout()
        self._setQss()

        self.show()

    def _resizeWindow(self) -> None:
        self.resize(1080, 784)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _setLayout(self) -> None:
        self.hBoxLayout = QHBoxLayout(self)
        self.epub_window = ReadView(self)
        self.hBoxLayout.setContentsMargins(0, 40, 0, 0)
        self.hBoxLayout.addWidget(self.epub_window)
        self.setLayout(self.hBoxLayout)

    def _setQss(self) -> None:
        with open("ereader.qss","r") as f:
            self.setStyleSheet(f.read())
