import logging
from typing import Optional

import fire
from PyQt5.QtWidgets import QApplication

from .ereader import EReader
from .persistentdict import data

logging.basicConfig(level=logging.INFO)

def run(epubPath:Optional[str]=None, fontFamily:Optional[str]=None,fontSize:Optional[int]=None):
    app = QApplication([])
    settings = {}
    if fontFamily:
        settings["fontFamily"] = fontFamily
    if fontSize:
        settings["fontSize"] = fontSize
    ereader = EReader(settings)
    if epubPath:
        ereader.loadEpub(epubPath)
    else:
        if epubPath:=data.get("currentEpubPath"):
            ereader.loadEpub(epubPath)
        else:
            ereader.openEpub()
    
    if readProgress:=data.get("currentReadProgress"):
        ereader.gotoReadProgress(readProgress)

    app.exec_()
    data["currentReadProgress"] = ereader.currentReadProgress()
    data.save()
    logging.shutdown()

def main():
    fire.Fire(run)