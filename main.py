import logging

from PyQt5.QtWidgets import QApplication

from ereader import EReader

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting EReader")
    app = QApplication([])
    ereader = EReader()
    ereader.open_epub()
    ereader.next_page_button.show()
    app.exec_()
    logging.info("Exiting EReader")
