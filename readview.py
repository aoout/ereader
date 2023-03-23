import logging

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import QtCore

from epubparser import EpubParser
from webview import WebView
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from utils import add_css_to_html

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

    def setHtml(self, html: str, baseUrl: QtCore.QUrl = QtCore.QUrl("")) -> None:
        with open("ereader.css", "r") as f:
            css = f.read()
        html = add_css_to_html(css,html)
        for css in self.epub_parser.css_path:
            with open(css, "r") as f:
                css = f.read()
            html = add_css_to_html(css,html)
        super().setHtml(html,baseUrl)


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
                self.load_pre_page()
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

    def load_pre_page(self) -> None:
        """
        Load the previous page
        """

        if self.epub_parser.current_page_index != 0:
            self.epub_parser.current_page_index -= 1
            self.setHtml(self.epub_parser.get_page_content(self.epub_parser.current_page_index))

            logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[self.epub_parser.current_page_index]}")
            self.runALF(lambda :self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);"))
        else:
            logging.info("No more HTML files to load")