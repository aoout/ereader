import logging
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
import zipfile
import shutil
import xmltodict
from pathlib import Path
from qframelesswindow import FramelessWindow, StandardTitleBar

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
        self.webview = QWebEngineView(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.webview)
        self.titleBar.raise_()
        self.show()
        self.current_html_index = 0

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
        tempdir = Path(os.path.dirname(filename)) / 'temp'
        if tempdir.exists():
            shutil.rmtree(tempdir)
        os.makedirs(tempdir)
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(tempdir)
        opf_file = tempdir / 'content.opf'

        with open(opf_file, 'r', encoding='utf-8') as f:
            opf_content = f.read()
        opf_dict = xmltodict.parse(opf_content)
        manifest = opf_dict['package']['manifest']
        html_files = []
        for item in manifest['item']:
            if item['@media-type'] == 'application/xhtml+xml':
                html_files.append(item['@href'])
        html_files.sort()
        html_files = [tempdir / html_file for html_file in html_files]
        self.html_files = html_files
        self.webview.setHtml('')
        with open(html_files[0], 'r', encoding='utf-8') as f:
            html_content = f.read()
        self.webview.setHtml(html_content)
        logging.info(f"Loaded HTML file: {html_files[0]}")
        
        self.webview.page().scrollPositionChanged.connect(self.on_scroll)

        self.next_page_button = QPushButton('Next Page', self)
        self.next_page_button.setGeometry(700, 500, 80, 30)
        self.next_page_button.clicked.connect(self.load_next_page)
        

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
        if self.current_html_index < len(self.html_files) - 1:
            with open(self.html_files[self.current_html_index + 1], 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.webview.page().runJavaScript('document.body.innerHTML += `{}`;'.format(html_content))
            logging.info(f"Loaded HTML file: {self.html_files[self.current_html_index + 1]}")
            self.current_html_index += 1
        else:
            logging.info("No more HTML files to load")



if __name__ == '__main__':
    logging.info("Starting EReader")
    app = QApplication([])
    ereader = EReader()
    ereader.open_epub()
    ereader.next_page_button.show()
    app.exec_()
    logging.info("Exiting EReader")
