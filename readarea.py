import logging

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog
from qfluentwidgets import ScrollArea, ExpandLayout

from epubparser import EpubParser


class ReadArea(ScrollArea):
    def __init__(self) -> None:
        """
        Initialize EpubWindow
        """
        super().__init__()

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.webview = QWebEngineView(self)
        self.expandLayout.addWidget(self.webview)

        self.webview.page().scrollPositionChanged.connect(self.on_scroll)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.webview)

        self.next_page_button = QPushButton('Next Page', self)
        self.next_page_button.setGeometry(700, 500, 80, 30)
        self.next_page_button.clicked.connect(self.load_next_page)

        self.epub_parser = None

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
        self.webview.setHtml('')
        self.webview.setHtml(self.epub_parser._get_page_content(0))
        logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[0]}")

    def on_scroll(self) -> None:
        """
        Scroll the page
        """
        logging.info("Scrolling the page")

        if self.webview.page().scrollPosition().y() >= self.webview.page().contentsSize().height() - self.webview.height():
            self.load_next_page()

    def load_next_page(self) -> None:
        """
        Load the next page
        """

        content = self.epub_parser.get_next_page_content()
        if content:
            self.webview.setHtml(content)
            logging.info(f"Loaded HTML file: {self.epub_parser.pages_path[self.epub_parser.current_page_index]}")
        else:
            logging.info("No more HTML files to load")
