from queue import Queue
from typing import Callable

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication,QWidget
from PyQt5 import QtGui


class WebView(QWebEngineView):
    """
    A class representing a web view.
    """

    def __init__(self,parent:QWidget = None) -> None:
        """
        Initializes a new instance of the WebView class.
        """
        super().__init__(parent)
        self._loadFinishedQueue = Queue()
        self.loadFinished.connect(self._on_loadFinished)
        self.loadStarted.connect(self._on_loadStarted)
        self.loading = False

    def runALF(self,func:Callable)->None:
        """
        Runs a function after the web view has finished loading.

        Args:
        func (Callable): The function to run.
        """
        self._loadFinishedQueue.put(func)

    def _on_loadStarted(self) -> None:
        self.loading = True

    def _on_loadFinished(self)->None:
        """
        A function to be called when the web view has finished loading.
        """
        self.loading = False
        while not self._loadFinishedQueue.empty():
            self._loadFinishedQueue.get()()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        print(3333)


