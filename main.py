import logging
import sys
import os

from PyQt5.QtWidgets import QApplication

from ereader import EReader
from persistentdict import data


logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting EReader")
    app = QApplication([])
    ereader = EReader()
    if len(sys.argv) == 1:
        if epub:=data.get("currentEpubPath"):
            ereader.epub_window.loadEpub(epub)
        else:
            ereader.epub_window.oepnEpub()
    if len(sys.argv) == 2:
        ereader.epub_window.loadEpub(sys.argv[1])
    if rp:=data.get("currentReadProgress"):
        ereader.epub_window.gotoReadProgress(rp)

    app.exec_()
    data["currentReadProgress"] = tuple( ereader.epub_window.currentReadProgress())
    data.save()
    logging.shutdown()
    logging.info("Exiting EReader")
