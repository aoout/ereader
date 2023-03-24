import logging
import os.path

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QFileDialog, QShortcut, QApplication

from epubparser import EpubParser
from utils import add_css_to_html
from webview import WebView


class ReadView(WebView):
    def __init__(self,parent:QWidget = None) -> None:
        """
        Initialize EpubWindow
        """
        super().__init__(parent)
        settings = QWebEngineSettings.globalSettings()
        settings.setFontFamily(QWebEngineSettings.StandardFont,"LXGW WenKai")
        settings.setFontSize(QWebEngineSettings.DefaultFontSize,24)
        self.epub_parser = None

        self.bindShortcutKeys()

    def bindShortcutKeys(self) -> None:
        shortcut = lambda key,func:QShortcut(QtGui.QKeySequence(key), self).activated.connect(func)

        shortcut("A",self.load_pre_page)
        shortcut("D",self.load_next_page)
        shortcut(Qt.Key_Left,self.load_pre_page)
        shortcut(Qt.Key_Right,self.load_next_page)

        shortcut("O",self.open_epub)


        up = lambda :self.runINL(lambda :self.page().runJavaScript("window.scrollBy(0, -window.innerHeight/20);"))
        down = lambda :self.runINL(lambda :self.page().runJavaScript("window.scrollBy(0, window.innerHeight/20);"))

        shortcut("W",up)
        shortcut("S",down)
        shortcut(Qt.Key_Up,up)
        shortcut(Qt.Key_Down,down)

        shortcut(Qt.Key_Home,lambda :self.runINL(lambda :self.page().runJavaScript("window.scrollTo(0, 0);")))
        shortcut(Qt.Key_End,lambda :self.runINL(lambda :self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")))
        shortcut(Qt.Key_PageUp,lambda :self.runINL(lambda :self.page().runJavaScript("window.scrollBy(0, -window.innerHeight);")))
        shortcut(Qt.Key_PageDown,lambda :self.runINL(lambda :self.page().runJavaScript("window.scrollBy(0, window.innerHeight);")))

        shortcut("Q",lambda :QApplication.quit())

    def setHtml(self, html: str, baseUrl: QtCore.QUrl = QtCore.QUrl("")) -> None:

        css_path = self.epub_parser.css_path + ["ereader.css"]
        for css in css_path:
            with open(css,"r") as f:
                html = add_css_to_html(f.read(),html)
        super().setHtml(html,baseUrl=QtCore.QUrl.fromLocalFile (str(self.epub_parser.tempdir) + os.path.sep ))
        print(str(self.epub_parser.tempdir))


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
        self.setHtml(self.epub_parser.get_page_content(0))
        logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[0]}")

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
        if self.epub_parser.current_page_index != len(self.epub_parser.pages_path)-1:
            self.epub_parser.current_page_index += 1
            self.setHtml(self.epub_parser.get_page_content(self.epub_parser.current_page_index))

            logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[self.epub_parser.current_page_index]}")
        else:
            logging.info("No more HTML files to load")

    def load_pre_page(self,scroll:bool = False) -> None:
        """
        Load the previous page
        """

        if self.epub_parser.current_page_index != 0:
            self.epub_parser.current_page_index -= 1
            self.setHtml(self.epub_parser.get_page_content(self.epub_parser.current_page_index))

            logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[self.epub_parser.current_page_index]}")
            if scroll:
                self.runALF(lambda :self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);"))
        else:
            logging.info("No more HTML files to load")
