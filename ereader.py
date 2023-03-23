import logging

from PyQt5.QtWidgets import QApplication, QHBoxLayout
from qframelesswindow import FramelessWindow, StandardTitleBar

from readview import ReadView

logging.basicConfig(level=logging.INFO)


class EReader(FramelessWindow):
    """
    A class representing an EReader object.
    """
    def __init__(self) -> None:
        """
        Initialize EReader
        """
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        self.setWindowTitle('EReader')
        self.resize_window()
        self.set_layout()
        self.set_qss()

        self.show()

    def resize_window(self) -> None:
        self.resize(1080, 784)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def set_layout(self) -> None:
        self.hBoxLayout = QHBoxLayout(self)
        self.epub_window = ReadView(self)
        self.hBoxLayout.setContentsMargins(0, 40, 0, 0)
        self.hBoxLayout.addWidget(self.epub_window)
        self.setLayout(self.hBoxLayout)

    def set_qss(self) -> None:
        with open("ereader.qss","r") as f:
            self.setStyleSheet(f.read())
