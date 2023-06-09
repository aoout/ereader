import os.path
import re
from typing import Callable
from pathlib import Path

from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QFileDialog, QShortcut, QWidget
from termcolor import colored

from ..utils import EpubParser, data
from .webview import WebView


class ReadWidget(WebView):
    def __init__(self, parent: QWidget = None, settings: dict = {}) -> None:
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
        fontFamily = self.settings.get("fontFamily", "LXGW WenKai")
        settings.setFontFamily(QWebEngineSettings.StandardFont, fontFamily)
        fontSize = self.settings.get("fontSize", 24)
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, fontSize)

    def onScrollPositionChanged(self, _) -> None:
        def setScrollHeight(height: int) -> None:
            self.scrollHeight = height

        self.page().runJavaScript("window.scrollY", setScrollHeight)

    def currentReadProgress(self) -> dict:
        return {"pageIndex": self.epubParser.currentPageIndex, "scrollHeight": self.scrollHeight}

    def gotoReadProgress(self, readProgress: dict) -> None:
        self.runINL(lambda: self.loadPage(readProgress["pageIndex"]))
        self.runALF(lambda: self.page().runJavaScript(
            f"window.scrollTo(0,{readProgress['scrollHeight']});"))

    def ctrlHome(self) -> None:
        self.runINL(lambda: self.loadPage(0))

    def ctrlEnd(self) -> None:
        self.runINL(lambda: self.loadPage(len(self.epubParser.pagesPath) - 1))

    def bindShortcutKeys(self) -> None:
        def shortcut(key, func): return QShortcut(
            QtGui.QKeySequence(key), self).activated.connect(func)

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

        def up(): return self.runINL(lambda: self.page().runJavaScript(
            "window.scrollBy(0, -window.innerHeight/20);"))

        def down(): return self.runINL(lambda: self.page().runJavaScript(
            "window.scrollBy(0, window.innerHeight/20);"))

        shortcut("W", up)
        shortcut("S", down)
        shortcut("up", up)
        shortcut("down", down)

        shortcut(Qt.Key_PageUp,
                 lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, -window.innerHeight);")))
        shortcut(Qt.Key_PageDown,
                 lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, window.innerHeight);")))

        shortcut("Q", lambda: self.parent().closeEvent())

        shortcut("ctrl+home", self.ctrlHome)

        shortcut("ctrl+end", self.ctrlEnd)

    def searchPage(self, pagePath: str, query: str) -> None:
        with open(pagePath, "r", encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        index = 0
        while True:
            index = text.find(query, index)
            if index == -1:
                break
            start = max(0, index - 40)
            end = min(len(text), index + len(query) + 40)
            context = text[start:end]
            context = re.sub(r'\s+', '', context)
            text_lines = context.split('\n')
            for line in text_lines:
                if query in line:
                    line = line.replace(query, colored(
                        query, 'green', attrs=['bold']))
                print(line)
            print('')
            index += len(query)

    def search(self, query: str, allPages: bool = False) -> None:
        if allPages:
            for pagePath in self.epubParser.pagesPath:
                self.searchPage(pagePath, query)
        else:
            self.searchPage(self.epubParser.currentPagePath(), query)

    def setHtml(self, html: str, baseUrl: QtCore.QUrl) -> None:

        css = os.path.join(os.path.dirname(__file__), 'ereader.css')
        with open(css, "r", encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        super().setHtml(html, baseUrl)

    def openEpub(self) -> None:
        """
        Open EPUB file
        """
        epubPath, _ = QFileDialog.getOpenFileName(
            self, 'Open EPUB', '', 'EPUB files (*.epub)')
        if epubPath:
            self.loadEpub(epubPath)

    def loadEpub(self, epubPath: str) -> None:
        """
        Load EPUB file
        """
        self.epubParser = EpubParser(epubPath)
        self.setHtml(self.epubParser.currentPageHtml(), QtCore.QUrl.fromLocalFile(
            str(self.epubParser.currentPagePath())))
        data["currentEpubPath"] = str(Path(epubPath).resolve())
        data.save()

        self.parent().tocView.load(self.epubParser.toc)

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if not self.loading:
            bias = e.angleDelta().y()
            if bias > 0:
                self.loadPrePage(scroll=self.scrollToButton)
            else:
                self.loadNextPage()

    def loadNextPage(self, scroll: Callable = None) -> None:
        self.loadPage(self.epubParser.currentPageIndex + 1, scroll)

    def loadPrePage(self, scroll: Callable = None) -> None:
        self.loadPage(self.epubParser.currentPageIndex - 1, scroll)

    def loadPage(self, index: int, scroll: Callable = None) -> None:
        if not scroll:
            scroll = self.scrollToTop

        if 0 <= index <= len(self.epubParser.pagesPath) - 1:
            self.epubParser.currentPageIndex = index
            self.setHtml(self.epubParser.currentPageHtml(), QtCore.QUrl.fromLocalFile(
                (str(self.epubParser.currentPagePath()))))
            self.runALF(scroll)

    def scrollToTop(self, func: Callable = None) -> None:
        if not func:
            func = self.runINL
        func(lambda: self.page().runJavaScript("window.scrollTo(0, 0);"))

    def scrollToButton(self, func: Callable = None) -> None:
        if not func:
            func = self.runINL
        func(lambda: self.page().runJavaScript(
            "window.scrollTo(0, document.body.scrollHeight);"))

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        self.parent().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
