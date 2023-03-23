import logging
import sys

from PyQt5.QtWidgets import QApplication

from ereader import EReader

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting EReader")
    app = QApplication([])
    ereader = EReader()
    if len(sys.argv) == 1:
        ereader.epub_window.open_epub()
    if len(sys.argv) == 2:
        ereader.epub_window.load_epub(sys.argv[1])
    app.exec_()
    logging.shutdown()
    logging.info("Exiting EReader")
