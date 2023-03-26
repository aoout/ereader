import logging
import os.path
from pathlib import Path
from typing import Callable

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QFileDialog, QShortcut, QWidget

from .epubparser import EpubParser
from .persistentdict import data
from .utils import addCssToHtml
from .webview import WebView


class ReadView(WebView):
    def __init__(self, parent: QWidget = None,settings:dict={}) -> None:
        """
        Initialize EpubWindow
        """
        super().__init__(parent)
        self.settings = settings
        self._setFont()
        self.epubParser = None

        self.bindShortcutKeys()
        self.scrollHeight = 0
        self.page().scrollPositionChanged.connect(self.onScrollPositionChanged)


    def _setFont(self) -> None:
        settings = QWebEngineSettings.globalSettings()
        fontFamily = self.settings.get("fontFamily","LXGW WenKai")
        settings.setFontFamily(QWebEngineSettings.StandardFont, fontFamily)
        fontSize = self.settings.get("fontSize",24)
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, fontSize)

    def onScrollPositionChanged(self, _) -> None:
        def setScrollHeight(height:int) -> None:
            self.scrollHeight = height

        self.page().runJavaScript("window.scrollY", setScrollHeight)

    def currentReadProgress(self) -> dict:
        return {"pageIndex":self.epubParser.currentPageIndex, "scrollHeight":self.scrollHeight}

    def gotoReadProgress(self, readProgress: dict) -> None:
        self.runINL(lambda: self.loadPage(readProgress["pageIndex"]))
        self.runALF(lambda: self.page().runJavaScript(f"window.scrollTo(0,{readProgress['scrollHeight']});"))

    def bindShortcutKeys(self) -> None:
        shortcut = lambda key, func: QShortcut(QtGui.QKeySequence(key), self).activated.connect(func)

        def shiftUp() -> None:
            self.loadPrePage()
        def shiftDown() -> None:
            self.loadNextPage()

        shortcut("A", shiftUp)
        shortcut("D", shiftDown)
        shortcut("left", shiftUp)
        shortcut("right", shiftDown)

        shortcut("home", self.scrollToTop)
        shortcut("end", self.scrollToButton)

        shortcut("O", self.openEpub)

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
        shortcut("ctrl+end", lambda: self.runINL(lambda: self.loadPage(len(self.epubParser.pagesPath) - 1)))

    def setHtmlFromFile(self, file: Path) -> None:

        with open(file, "r") as f:
            html = f.read()
        css_path = self.epubParser.css_path + [".ereader.css"]
        for css in css_path:
            with open(css, "r") as f:
                html = addCssToHtml(f.read(), html)
        self.setHtml(html, baseUrl=QtCore.QUrl.fromLocalFile(str(file.parent) + os.path.sep))

    def openEpub(self) -> None:
        """
        Open EPUB file
        """
        epubPath, _ = QFileDialog.getOpenFileName(self, 'Open EPUB', '', 'EPUB files (*.epub)')
        if epubPath:
            self.loadEpub(epubPath)

    def loadEpub(self, epubPath: str) -> None:
        """
        Load EPUB file
        """
        self.epubParser = EpubParser(epubPath)
        self.setHtmlFromFile(self.epubParser.currentPagePath())
        data["currentEpubPath"] = epubPath
        data.save()

        self.parent().tocView.load(self.epubParser.toc)

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if not self.loading:
            bias = e.angleDelta().y()
            if bias > 0:
                self.loadPrePage(scroll=self.scrollToButton)
            else:
                self.loadNextPage()

    def loadNextPage(self,scroll:Callable = None) -> None:
        self.loadPage(self.epubParser.currentPageIndex + 1,scroll)

    def loadPrePage(self,scroll:Callable = None) -> None:
        self.loadPage(self.epubParser.currentPageIndex - 1,scroll)

    def loadPage(self, index: int,scroll:Callable = None) -> None:
        if not scroll:
            scroll = self.scrollToTop

        if 0 <= index <= len(self.epubParser.pagesPath) - 1:
            self.epubParser.currentPageIndex = index
            self.setHtmlFromFile(self.epubParser.currentPagePath())
            self.runALF(scroll)

    def scrollToTop(self,func:Callable = None) -> None:
        if not func:
            func = self.runINL
        func (lambda: self.page().runJavaScript("window.scrollTo(0, 0);"))

    def scrollToButton(self,func:Callable = None) -> None:
        if not func:
            func = self.runINL
        func (lambda: self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);"))

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        self.parent().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
