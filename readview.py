import logging
import os.path
from collections import namedtuple
from pathlib import Path

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QFileDialog, QShortcut, QApplication

from epubparser import EpubParser
from persistentdict import data
from utils import addCssToHtml
from webview import WebView

readingProgress = namedtuple("readingProgress", ["pageIndex", "scrollHeight"])


class ReadView(WebView):
    def __init__(self, parent: QWidget = None) -> None:
        """
        Initialize EpubWindow
        """
        super().__init__(parent)
        self._setFont()
        self.epubParser = None

        self.bindShortcutKeys()
        self.scrollHeight = None
        self.page().scrollPositionChanged.connect(self.onScrollPositionChanged)

    def _setFont(self):
        settings = QWebEngineSettings.globalSettings()
        settings.setFontFamily(QWebEngineSettings.StandardFont, "LXGW WenKai")
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 24)

    def onScrollPositionChanged(self, x) -> None:
        def setScrollHeight(height:int) -> None:
            self.scrollHeight = height

        self.page().runJavaScript("window.scrollY", setScrollHeight)

    def currentReadProgress(self) -> readingProgress:
        print(self.scrollHeight)
        return readingProgress(pageIndex=self.epubParser.current_page_index, scrollHeight=self.scrollHeight)

    def gotoReadProgress(self, rp: tuple) -> None:
        rp = readingProgress(*rp)
        self.runINL(lambda: self.loadPage(rp.pageIndex))
        self.runALF(lambda: self.page().runJavaScript(f"window.scrollTo(0,{rp.scrollHeight});"))

    def bindShortcutKeys(self) -> None:
        shortcut = lambda key, func: QShortcut(QtGui.QKeySequence(key), self).activated.connect(func)

        shortcut("A", self.loadPrePage)
        shortcut("D", self.loadNextPage)
        shortcut("left", self.loadPrePage)
        shortcut("right", self.loadNextPage)

        shortcut("home", self.scrollToTop)
        shortcut("end", self.scrollToButton)

        shortcut("O", self.oepnEpub)

        up = lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, -window.innerHeight/20);"))
        down = lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, window.innerHeight/20);"))

        shortcut("W", up)
        shortcut("S", down)
        shortcut("up", up)
        shortcut("down", down)

        shortcut(Qt.Key_PageUp,
                 lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, -window.innerHeight);")))
        shortcut(Qt.Key_PageDown,
                 lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, window.innerHeight);")))

        shortcut("Q", lambda: QApplication.quit())
        for i in range(10):
            shortcut(str(i), lambda i=i: self.runINL(lambda: self.loadPage(i)))
        shortcut("ctrl+home", lambda: self.runINL(lambda: self.loadPage(0)))
        shortcut("ctrl+end", lambda: self.runINL(lambda: self.loadPage(len(self.epubParser.pages_path) - 1)))

    def setHtmlFromFile(self, file: Path, baseUrl: QtCore.QUrl = QtCore.QUrl("")) -> None:

        with open(file, "r") as f:
            html = f.read()
        css_path = self.epubParser.css_path + ["ereader.css"]
        for css in css_path:
            with open(css, "r") as f:
                html = addCssToHtml(f.read(), html)
        self.setHtml(html, baseUrl=QtCore.QUrl.fromLocalFile(str(file.parent) + os.path.sep))

    def oepnEpub(self) -> None:
        """
        Open EPUB file
        """
        epubPath, _ = QFileDialog.getOpenFileName(self, 'Open EPUB', '', 'EPUB files (*.epub)')
        if epubPath:
            logging.info(f"Opening EPUB file: {epubPath}")
            self.loadEpub(epubPath)

    def loadEpub(self, filename: str) -> None:
        """
        Load EPUB file
        """
        self.epubParser = EpubParser(filename)
        self.setHtmlFromFile(self.epubParser.currentPagePath())
        logging.info(f"Loaded HTML file: {self.epubParser.pages_path[0]}")
        data["currentEpubPath"] = filename
        data.save()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if not self.loading:
            bias = e.angleDelta().y()
            if bias > 0:
                self.loadPrePage()
                self.scrollToButton()
            else:
                self.loadNextPage()

    def loadNextPage(self) -> None:
        self.loadPage(self.epubParser.current_page_index + 1)

    def loadPrePage(self) -> None:
        self.loadPage(self.epubParser.current_page_index - 1)

    def loadPage(self, index: int) -> None:
        if 0 <= index <= len(self.epubParser.pages_path) - 1:
            self.epubParser.current_page_index = index
            self.setHtmlFromFile(self.epubParser.currentPagePath())
            logging.info(f"Loaded HTML file: {self.epubParser.currentPagePath()}")
        else:
            logging.info("No that HTML files to load")

    def scrollToTop(self) -> None:
        self.runALF(lambda: self.page().runJavaScript("window.scrollTo(0, 0);"))
    def scrollToButton(self) -> None:
        self.runALF(lambda: self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);"))
