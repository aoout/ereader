import logging

from PyQt5.QtWidgets import QApplication, QHBoxLayout
from qframelesswindow import FramelessWindow, StandardTitleBar

from readview import ReadView

logging.basicConfig(level=logging.INFO)


class EReader(FramelessWindow):
    def __init__(self) -> None:
        """
        Initialize EReader
        """
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        self.setWindowTitle('EReader')
        self.resize(1080, 784)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.hBoxLayout = QHBoxLayout(self)
        self.epub_window = ReadView(self)
        self.hBoxLayout.setContentsMargins(0, 40, 0, 0)
        self.hBoxLayout.addWidget(self.epub_window)
        self.setLayout(self.hBoxLayout)

        self.titleBar.raise_()

        self.show()