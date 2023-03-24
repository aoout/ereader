import logging
import os.path
from pathlib import Path
from collections import  namedtuple

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QFileDialog, QShortcut, QApplication

from epubparser import EpubParser
from utils import add_css_to_html
from webview import WebView
from persistentdict import data

readingProgress = namedtuple("readingProgress",["pageIndex","scrollHeight"])

class ReadView(WebView):
    def __init__(self, parent: QWidget = None) -> None:
        """
        Initialize EpubWindow
        """
        super().__init__(parent)
        settings = QWebEngineSettings.globalSettings()
        settings.setFontFamily(QWebEngineSettings.StandardFont, "LXGW WenKai")
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 24)
        self.epub_parser = None

        self.bindShortcutKeys()


    def currentReadProgress(self) -> readingProgress:
        return readingProgress(pageIndex=self.epub_parser.current_page_index,scrollHeight=self.page().scrollPosition().y())

    def gotoReadProgress(self,rp:tuple) -> None:
        rp = readingProgress(*rp)
        self.runINL(lambda :self.load_page(rp.pageIndex))\
    #     scroll

    def bindShortcutKeys(self) -> None:
        shortcut = lambda key, func: QShortcut(QtGui.QKeySequence(key), self).activated.connect(func)

        shortcut("A", self.load_pre_page)
        shortcut("D", self.load_next_page)
        shortcut("left", self.load_pre_page)
        shortcut("right", self.load_next_page)

        shortcut("O", self.open_epub)

        up = lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, -window.innerHeight/20);"))
        down = lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, window.innerHeight/20);"))

        shortcut("W", up)
        shortcut("S", down)
        shortcut("up", up)
        shortcut("down", down)

        shortcut("home", lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollTo(0, 0);")))
        shortcut("end", lambda: self.runINL(
            lambda: self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")))
        shortcut(Qt.Key_PageUp,
                 lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, -window.innerHeight);")))
        shortcut(Qt.Key_PageDown,
                 lambda: self.runINL(lambda: self.page().runJavaScript("window.scrollBy(0, window.innerHeight);")))

        shortcut("Q", lambda: QApplication.quit())
        for i in range(10):
            shortcut(str(i), lambda i=i: self.runINL(lambda: self.load_page(i)))
        shortcut("ctrl+home",lambda :self.runINL(lambda :self.load_page(0)))
        shortcut("ctrl+end",lambda :self.runINL(lambda :self.load_page(len(self.epub_parser.pages_path)-1)))


    def setHtmlFromFile(self, file: Path, baseUrl: QtCore.QUrl = QtCore.QUrl("")) -> None:

        with open(file, "r") as f:
            html = f.read()
        css_path = self.epub_parser.css_path + ["ereader.css"]
        for css in css_path:
            with open(css, "r") as f:
                html = add_css_to_html(f.read(), html)
        self.setHtml(html, baseUrl=QtCore.QUrl.fromLocalFile(str(file.parent) + os.path.sep))

    def open_epub(self) -> None:
        """
        Open EPUB file
        """
        filename, _ = QFileDialog.getOpenFileName(self, 'Open EPUB', '', 'EPUB files (*.epub)')
        if filename:
            logging.info(f"Opening EPUB file: {filename}")
            self.load_epub(filename)

    def load_epub(self, filename: str) -> None:
        """
        Load EPUB file
        """
        self.epub_parser = EpubParser(filename)
        self.setHtmlFromFile(self.epub_parser.current_page_path())
        logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[0]}")
        data["currentEpubPath"] = filename
        data.save()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if not self.loading:
            bias = e.angleDelta().y()
            if bias > 0:
                self.load_pre_page(scroll=True)
            else:
                self.load_next_page()

    def load_next_page(self) -> None:
        """
        Load the next page
        """
        if self.epub_parser.current_page_index != len(self.epub_parser.pages_path) - 1:
            self.epub_parser.current_page_index += 1
            self.setHtmlFromFile(self.epub_parser.current_page_path())

            logging.info(f"Loaded HTML file: {self.epub_parser.current_page_path()}")
        else:
            logging.info("No more HTML files to load")

    def load_pre_page(self, scroll: bool = False) -> None:
        """
        Load the previous page
        """

        if self.epub_parser.current_page_index != 0:
            self.epub_parser.current_page_index -= 1
            self.setHtmlFromFile(self.epub_parser.current_page_path())

            logging.info(f"Loaded HTML file: {self.epub_parser.current_page_path()}")
            if scroll:
                self.runALF(lambda: self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);"))
        else:
            logging.info("No more HTML files to load")

    def load_page(self, index: int) -> None:
        if 0 <= index <= len(self.epub_parser.pages_path) - 1:
            self.epub_parser.current_page_index = index
            self.setHtmlFromFile(self.epub_parser.current_page_path())
            logging.info(f"Loaded HTML file: {self.epub_parser.current_page_path()}")
        else:
            logging.info("No that HTML files to load")
