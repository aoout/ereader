import logging

from PyQt5.QtWidgets import QApplication

from ereader import EReader

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting EReader")
    app = QApplication([])
    ereader = EReader()
    ereader.epub_window.open_epub()
    logging.info("Exiting EReader")
    logging.shutdown()
    app.exec_()
