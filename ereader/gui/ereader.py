import logging
import os
from queue import Queue

import fire
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QHBoxLayout
from qframelesswindow import FramelessWindow, StandardTitleBar

from ..utils import data
from .readwidget import ReadWidget
from .tocwidget import TocWidget

logging.basicConfig(level=logging.INFO)


class EReader(FramelessWindow):
    receivedCmd = pyqtSignal(str)

    def __init__(self, queue: Queue, settings: dict = {}) -> None:

        super().__init__()
        self.queue = queue
        self.setTitleBar(StandardTitleBar(self))

        self.setWindowTitle('EReader')
        self.settings = settings
        self._resizeWindow()
        self._setLayout()
        self._setQss()
        self.receivedCmd.connect(self.dealCmd)

        self.setMouseTracking(True)

        self.show()

    def dealCmd(self, cmd: str) -> None:
        try:
            readView = self.readView

            class Shell:
                def next(self, pageNum: int = 1) -> None:
                    readView.loadPage(
                        readView.epubParser.currentPageIndex + pageNum)

                def pre(self, pageNum: int = 1) -> None:
                    readView.loadPage(
                        readView.epubParser.currentPageIndex - pageNum)

                def home(self) -> None:
                    readView.ctrlHome()

                def end(self) -> None:
                    readView.ctrlEnd()

                def path(self) -> None:
                    print(readView.epubParser.epubPath)

                def toc(self) -> None:
                    readView.epubParser.printToc()

                def meta(self) -> None:
                    print(readView.epubParser.meta)

                def search(self, query: str, allPages: bool = False) -> None:
                    readView.search(query, allPages)

                def index(self) -> None:
                    print(readView.epubParser.currentPageIndex)

                def setFontFamily(self, family: str) -> None:
                    QWebEngineSettings.globalSettings().setFontFamily(
                        QWebEngineSettings.StandardFont, family)

                def setFontSize(self, size: int) -> None:
                    QWebEngineSettings.globalSettings().setFontSize(
                        QWebEngineSettings.DefaultFontSize, size)

                def exit(self) -> None:
                    ...

            fire.Fire(name="ereader", component=Shell, command=cmd)
        except:
            ...

    def _resizeWindow(self) -> None:
        self.resize(1080, 784)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _setLayout(self) -> None:
        self.hBoxLayout = QHBoxLayout(self)
        self.tocView = TocWidget(self)
        self.readView = ReadWidget(self, self.settings)
        self.hBoxLayout.setContentsMargins(10, 40, 10, 0)
        self.hBoxLayout.addWidget(self.tocView)
        self.hBoxLayout.addWidget(self.readView)
        self.setLayout(self.hBoxLayout)

    def _setQss(self) -> None:
        qss_path = os.path.join(os.path.dirname(__file__), 'ereader.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def openEpub(self) -> None:
        self.readView.openEpub()

    def loadEpub(self, epubPath: str) -> None:
        self.readView.loadEpub(epubPath)

    def currentReadProgress(self) -> dict:
        return self.readView.currentReadProgress()

    def gotoReadProgress(self, readProgress: dict) -> None:
        self.readView.gotoReadProgress(readProgress)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:

        if e.pos().x() < 8:
            self.tocView.show()
        elif e.pos().x() > self.tocView.pos().x() + self.tocView.size().width():
            self.tocView.hide()
        return super().mouseMoveEvent(e)

    def closeEvent(self, e: QtGui.QCloseEvent=None) -> None:
        if e:
            super().closeEvent(e)
        data["currentReadProgress"] = self.currentReadProgress()
        data.save()

        print("exit")
        exit()
